import { useEffect, useState } from 'react';
import { getRecruiterDashboard, getRecruiterJobs, getApplicants, updateApplicationStatus } from '../services/api';
import StatCard from '../components/StatCard';
import ScoreBadge from '../components/ScoreBadge';
import { FiBriefcase, FiUsers, FiTrendingUp, FiCheckCircle } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const PIE_COLORS = ['#818cf8', '#4ade80', '#f87171', '#facc15'];

export default function RecruiterDashboard() {
  const [data, setData] = useState(null);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicants, setApplicants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getRecruiterDashboard()
      .then((res) => { setData(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const loadApplicants = async (jobId) => {
    setSelectedJob(jobId);
    try {
      const res = await getApplicants(jobId);
      setApplicants(res.data);
    } catch { setApplicants([]); }
  };

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await updateApplicationStatus(appId, newStatus);
      setApplicants((prev) =>
        prev.map((a) => (a.id === appId ? { ...a, status: newStatus } : a))
      );
    } catch {}
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const appsPerJob = (data?.applications_per_job || []).map((j) => ({
    name: j.title?.slice(0, 18) || 'Job',
    count: j.app_count || 0,
  }));

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-1">Recruiter Dashboard</h1>
      <p className="text-slate-500 text-sm mb-8">Manage your hiring pipeline</p>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={<FiBriefcase />} value={data?.total_jobs || 0} label="Jobs Posted" color="text-indigo-400" />
        <StatCard icon={<FiCheckCircle />} value={data?.active_jobs || 0} label="Active Jobs" color="text-green-400" />
        <StatCard icon={<FiUsers />} value={data?.total_applications || 0} label="Total Applicants" color="text-violet-400" />
        <StatCard icon={<FiTrendingUp />} value={data?.top_skills?.length || 0} label="Skills Tracked" color="text-amber-400" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Applications per Job Chart */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">📊 Applications per Job</h3>
          {appsPerJob.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={appsPerJob}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 10 }} />
                <Bar dataKey="count" fill="#a78bfa" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-600 text-sm">Post jobs to see analytics</p>
          )}
        </div>

        {/* Top Skills Demand */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🔥 Top Skills in Demand</h3>
          <div className="flex flex-wrap gap-2">
            {(data?.top_skills || []).map((s) => (
              <span key={s.skill} className="px-3 py-1.5 rounded-full bg-violet-500/10 text-violet-300 text-xs font-medium border border-violet-500/20">
                {s.skill} ({s.count})
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Top Candidates Table */}
      <div className="glass-card mb-8">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">🏆 Top Matching Candidates</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-slate-700/50">
                <th className="pb-3 font-medium">Candidate</th>
                <th className="pb-3 font-medium">Job</th>
                <th className="pb-3 font-medium">Score</th>
                <th className="pb-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {(data?.top_candidates || []).map((c, i) => (
                <tr key={i} className="border-b border-slate-800/50">
                  <td className="py-3 text-slate-200">{c.job_seeker__user__username}</td>
                  <td className="py-3 text-slate-400">{c.job_posting__title}</td>
                  <td className="py-3"><ScoreBadge score={Number(c.match_score_pct)} /></td>
                  <td className="py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                      c.status === 'SHORTLISTED' ? 'bg-green-500/10 text-green-400' :
                      c.status === 'REJECTED' ? 'bg-red-500/10 text-red-400' :
                      c.status === 'HIRED' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-slate-500/10 text-slate-400'
                    }`}>
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
              {(!data?.top_candidates || data.top_candidates.length === 0) && (
                <tr><td colSpan={4} className="py-4 text-slate-600 text-center">No applicants yet</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Job selector + Applicant list */}
      <div className="glass-card">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">📋 View Applicants by Job</h3>
        <div className="flex flex-wrap gap-2 mb-4">
          {(data?.applications_per_job || []).map((j) => (
            <button
              key={j.id}
              onClick={() => loadApplicants(j.id)}
              className={`px-4 py-2 rounded-lg text-xs font-medium transition ${
                selectedJob === j.id
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                  : 'bg-slate-800/50 text-slate-500 border border-slate-700/50 hover:text-slate-300'
              }`}
            >
              {j.title} ({j.app_count})
            </button>
          ))}
        </div>

        {selectedJob && (
          <div className="space-y-3">
            {applicants.map((a) => (
              <div key={a.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/30">
                <div>
                  <div className="text-sm font-medium text-slate-200">{a.job_seeker_name}</div>
                  <div className="text-xs text-slate-500">
                    Missing: {a.missing_skills?.slice(0, 50) || 'None'}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <ScoreBadge score={Number(a.match_score_pct)} />
                  <select
                    value={a.status}
                    onChange={(e) => handleStatusChange(a.id, e.target.value)}
                    className="bg-slate-800 text-xs text-slate-300 border border-slate-700 rounded-lg px-2 py-1.5 outline-none"
                  >
                    <option value="APPLIED">Applied</option>
                    <option value="SHORTLISTED">Shortlist</option>
                    <option value="REJECTED">Reject</option>
                    <option value="HIRED">Hire</option>
                  </select>
                </div>
              </div>
            ))}
            {applicants.length === 0 && (
              <p className="text-slate-600 text-sm text-center py-4">No applicants for this job</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
