import { useEffect, useState } from 'react';
import { getJobs, applyToJob } from '../services/api';
import { useAuth } from '../context/AuthContext';
import ScoreBadge from '../components/ScoreBadge';
import { FiMapPin, FiBriefcase, FiSearch } from 'react-icons/fi';

export default function BrowseJobsPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(null);

  useEffect(() => {
    getJobs()
      .then((res) => { setJobs(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleApply = async (jobId) => {
    setApplying(jobId);
    try {
      await applyToJob({ job_posting: jobId });
      alert('Application submitted! Check your dashboard for match score.');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to apply');
    } finally {
      setApplying(null);
    }
  };

  const filtered = jobs.filter((j) =>
    j.title.toLowerCase().includes(search.toLowerCase()) ||
    j.required_skills?.toLowerCase().includes(search.toLowerCase()) ||
    j.location?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-1">Browse Jobs</h1>
      <p className="text-slate-500 text-sm mb-6">Find your next opportunity</p>

      {/* Search */}
      <div className="relative mb-8 max-w-xl">
        <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          className="input-field !pl-11"
          placeholder="Search by title, skill, or location..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Job Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((job) => (
          <div key={job.id} className="glass-card">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="text-base font-bold text-slate-100">{job.title}</h3>
                <div className="text-xs text-slate-500 mt-1">{job.recruiter_name}</div>
              </div>
              {job.match_score_pct && <ScoreBadge score={job.match_score_pct} />}
            </div>
            <p className="text-sm text-slate-400 mb-3 line-clamp-2">{job.description}</p>
            <div className="flex flex-wrap gap-2 mb-3">
              {job.required_skills?.split(',').slice(0, 5).map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[11px] border border-slate-700/50">
                  {s.trim()}
                </span>
              ))}
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-xs text-slate-500">
                {job.location && <span className="flex items-center gap-1"><FiMapPin />{job.location}</span>}
                {job.salary_range && <span>{job.salary_range}</span>}
                {job.experience_requirement > 0 && <span>{job.experience_requirement}+ yrs</span>}
              </div>
              {user?.role === 'JOB_SEEKER' && (
                <button
                  onClick={() => handleApply(job.id)}
                  disabled={applying === job.id}
                  className="btn-primary !py-2 !px-5 !text-xs"
                >
                  {applying === job.id ? 'Applying...' : 'Apply'}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      {filtered.length === 0 && (
        <p className="text-center text-slate-600 py-12">No jobs found</p>
      )}
    </div>
  );
}
