"""
Celery tasks for asynchronous resume processing and matching.
"""
import logging
from celery import shared_task

log = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_resume_upload(self, resume_id: int):
    """
    Parse an uploaded resume file, extract text and skills,
    and store results back on the UploadedResume record.
    """
    from .models import UploadedResume
    from .matching_engine import extract_text_from_file, extract_skills_from_text

    try:
        resume = UploadedResume.objects.get(id=resume_id)
        file_path = resume.file.path

        # Extract raw text
        raw_text = extract_text_from_file(file_path)
        if not raw_text.strip():
            log.warning(f"No text extracted from resume {resume_id}")
            return

        resume.parsed_text = raw_text

        # Extract skills
        skills = extract_skills_from_text(raw_text)
        resume.extracted_skills = ", ".join(skills)

        # Simple education extraction (look for degree keywords)
        edu_keywords = ['bachelor', 'master', 'phd', 'b.e', 'b.tech', 'm.tech',
                        'mba', 'b.sc', 'm.sc', 'bca', 'mca', 'diploma']
        lines = raw_text.split('\n')
        edu_lines = [l.strip() for l in lines if any(kw in l.lower() for kw in edu_keywords)]
        resume.extracted_education = "; ".join(edu_lines[:5])

        # Simple experience extraction
        import re
        exp_pattern = re.compile(r'(\d+)\s*(?:\+\s*)?(?:years?|yrs?)', re.IGNORECASE)
        exp_matches = exp_pattern.findall(raw_text)
        if exp_matches:
            resume.extracted_experience = f"{max(int(x) for x in exp_matches)} years"

        resume.save()
        log.info(f"Resume {resume_id} processed: {len(skills)} skills extracted")

    except UploadedResume.DoesNotExist:
        log.error(f"Resume {resume_id} not found")
    except Exception as exc:
        log.error(f"Resume processing error: {exc}")
        self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def compute_application_match(self, application_id: int):
    """
    Compute the match score between an application's resume and job posting.
    Updates the JobApplication record with the score and missing skills.
    """
    from .models import JobApplication
    from .matching_engine import compute_match

    try:
        application = JobApplication.objects.select_related(
            'job_posting', 'resume'
        ).get(id=application_id)

        resume_text = ""
        if application.resume and application.resume.parsed_text:
            resume_text = application.resume.parsed_text
        elif application.job_seeker:
            # Fallback: use latest resume
            latest = application.job_seeker.resumes.order_by('-uploaded_at').first()
            if latest and latest.parsed_text:
                resume_text = latest.parsed_text

        if not resume_text:
            log.warning(f"No resume text for application {application_id}")
            return

        jd_text = application.job_posting.description

        result = compute_match(resume_text, jd_text)

        application.match_score_pct = result["match_score_pct"]
        application.missing_skills = ", ".join(result["missing_skills"])
        application.save()

        log.info(f"Application {application_id} scored: {result['match_score_pct']}%")

    except JobApplication.DoesNotExist:
        log.error(f"Application {application_id} not found")
    except Exception as exc:
        log.error(f"Match computation error: {exc}")
        self.retry(exc=exc, countdown=30)


@shared_task
def rank_all_applicants_for_job(job_id: int):
    """
    Re-compute match scores for ALL applicants of a given job posting.
    """
    from .models import JobApplication
    
    applications = JobApplication.objects.filter(job_posting_id=job_id)
    for app in applications:
        compute_application_match.delay(app.id)
