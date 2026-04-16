import { useEffect, useState } from 'react';
import { getRecruiterJobs, deleteJob } from '../services/api';
import { Link } from 'react-router-dom';
import { FiEdit, FiTrash2, FiUsers, FiPlus } from 'react-icons/fi';

export default function MyJobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRecruiterJobs()
      .then((res) => { setJobs(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleDelete = async (id) => {
    if (!confirm('Delete this job posting?')) return;
    try {
      await deleteJob(id);
      setJobs(jobs.filter((j) => j.id !== id));
    } catch {
      alert('Failed to delete');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">My Job Postings</h1>
          <p className="text-slate-500 text-sm">Manage your recruitment pipeline</p>
        </div>
        <Link to="/post-job" className="btn-primary flex items-center gap-2 !text-sm">
          <FiPlus /> New Job
        </Link>
      </div>

      <div className="space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="glass-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100">{job.title}</h3>
                <div className="text-xs text-slate-500 mt-1">
                  {job.location || 'Remote'} • {job.salary_range || 'Not specified'} •{' '}
                  <span className={job.status === 'ACTIVE' ? 'text-green-400' : 'text-slate-500'}>{job.status}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link to={`/applicants/${job.id}`} className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition">
                  <FiUsers />
                </Link>
                <button onClick={() => handleDelete(job.id)} className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition">
                  <FiTrash2 />
                </button>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5 mt-3">
              {job.required_skills?.split(',').slice(0, 6).map((s) => (
                <span key={s} className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[11px]">{s.trim()}</span>
              ))}
            </div>
          </div>
        ))}
        {jobs.length === 0 && (
          <div className="text-center py-16">
            <p className="text-slate-600 mb-4">You haven't posted any jobs yet</p>
            <Link to="/post-job" className="btn-primary">Post Your First Job</Link>
          </div>
        )}
      </div>
    </div>
  );
}
