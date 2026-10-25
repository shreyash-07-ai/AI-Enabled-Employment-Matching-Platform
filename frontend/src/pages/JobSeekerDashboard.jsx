import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getJobSeekerDashboard, getRecommendedJobs } from '../services/api';
import StatCard from '../components/StatCard';
import ScoreBadge from '../components/ScoreBadge';
import { FiBriefcase, FiCheckCircle, FiAlertCircle, FiTrendingUp } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function JobSeekerDashboard() {
  const [data, setData] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getJobSeekerDashboard().catch(() => ({ data: {} })),
      getRecommendedJobs().catch(() => ({ data: { jobs: [] } })),
    ]).then(([dashRes, recRes]) => {
      setData(dashRes.data);
      setRecommended(recRes.data?.jobs || []);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const chartData = (data?.match_scores || []).map((s) => ({
    name: s.job_posting__title?.slice(0, 15) || 'Job',
    score: Number(s.match_score_pct) || 0,
  }));

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-1">Job Seeker Dashboard</h1>
      <p className="text-slate-500 text-sm mb-8">Your career overview at a glance</p>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={<FiBriefcase />} value={data?.total_applications || 0} label="Applications" color="text-indigo-400" />
        <StatCard icon={<FiCheckCircle />} value={data?.status_counts?.SHORTLISTED || 0} label="Shortlisted" color="text-green-400" />
        <StatCard icon={<FiAlertCircle />} value={data?.status_counts?.REJECTED || 0} label="Rejected" color="text-red-400" />
        <StatCard icon={<FiTrendingUp />} value={`${data?.resume_completion || 0}%`} label="Resume Score" color="text-violet-400" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Match Scores Chart */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">📊 Match Score History</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 10 }}
                  labelStyle={{ color: '#f1f5f9' }}
                />
                <Bar dataKey="score" fill="#818cf8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-600 text-sm">Apply to jobs to see match scores</p>
          )}
        </div>

        {/* My Skills */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🛠️ My Skills</h3>
          <div className="flex flex-wrap gap-2">
            {(data?.my_skills || []).length > 0 ? (
              data.my_skills.map((skill) => (
                <span key={skill} className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-300 text-xs font-medium border border-indigo-500/20">
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-slate-600 text-sm">Upload a resume to auto-extract skills</p>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Jobs */}
      <div className="glass-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-slate-300">🎯 Recommended Jobs</h3>
          <Link to="/jobs" className="text-xs text-indigo-400 hover:text-indigo-300">View all →</Link>
        </div>
        {recommended.length > 0 ? (
          <div className="space-y-3">
            {recommended.slice(0, 5).map((job) => (
              <div key={job.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/30">
                <div>
                  <div className="text-sm font-medium text-slate-200">{job.title}</div>
                  <div className="text-xs text-slate-500">{job.recruiter_name} • {job.location || 'Remote'}</div>
                </div>
                <ScoreBadge score={job.match_score_pct} />
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-600 text-sm">No jobs available yet</p>
        )}
      </div>

      {/* Notifications */}
      {(data?.notifications || []).length > 0 && (
        <div className="glass-card mt-6">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🔔 Notifications</h3>
          <div className="space-y-2">
            {data.notifications.map((n, i) => (
              <div key={i} className="flex items-center gap-3 p-2">
                <span className={`w-2 h-2 rounded-full ${n.status === 'SHORTLISTED' ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-sm text-slate-300">
                  {n.status === 'SHORTLISTED' ? '✅ Shortlisted' : '❌ Rejected'} for{' '}
                  <span className="font-medium">{n.job_posting__title}</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
