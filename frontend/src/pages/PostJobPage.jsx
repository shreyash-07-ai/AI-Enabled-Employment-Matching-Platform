import { useState } from 'react';
import { createJob } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function PostJobPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '', description: '', required_skills: '',
    education_requirement: '', experience_requirement: '0',
    salary_range: '', location: '',
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createJob(form);
      navigate('/my-jobs');
    } catch (err) {
      alert('Failed to create job: ' + JSON.stringify(err.response?.data || 'Error'));
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <div className="animate-fade-in max-w-2xl">
      <h1 className="text-2xl font-bold mb-1">Post a New Job</h1>
      <p className="text-slate-500 text-sm mb-8">Create a job posting and find matching candidates</p>

      <form onSubmit={handleSubmit} className="glass-card space-y-5">
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Job Title *</label>
          <input className="input-field" placeholder="e.g. Senior Python Developer" value={form.title} onChange={updateField('title')} required />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Job Description *</label>
          <textarea className="input-field min-h-[120px]" placeholder="Describe the role, responsibilities, and ideal candidate..." value={form.description} onChange={updateField('description')} required />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Required Skills * (comma-separated)</label>
          <input className="input-field" placeholder="e.g. Python, Django, PostgreSQL, REST APIs, Docker" value={form.required_skills} onChange={updateField('required_skills')} required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Education</label>
            <input className="input-field" placeholder="e.g. Bachelor's in CS" value={form.education_requirement} onChange={updateField('education_requirement')} />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Min Experience (years)</label>
            <input type="number" className="input-field" value={form.experience_requirement} onChange={updateField('experience_requirement')} min="0" step="0.5" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Salary Range</label>
            <input className="input-field" placeholder="e.g. ₹8-12 LPA" value={form.salary_range} onChange={updateField('salary_range')} />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Location</label>
            <input className="input-field" placeholder="e.g. Pune, Remote" value={form.location} onChange={updateField('location')} />
          </div>
        </div>
        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Creating...' : 'Publish Job Posting'}
        </button>
      </form>
    </div>
  );
}
