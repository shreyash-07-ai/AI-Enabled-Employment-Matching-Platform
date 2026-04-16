import { useEffect, useState } from 'react';
import { getAdminDashboard, getAdminUsers } from '../services/api';
import StatCard from '../components/StatCard';
import { FiUsers, FiBriefcase, FiFileText, FiTrendingUp } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend } from 'recharts';

const PIE_COLORS = ['#818cf8', '#4ade80', '#f87171', '#facc15'];

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getAdminDashboard().catch(() => ({ data: {} })),
      getAdminUsers().catch(() => ({ data: [] })),
    ]).then(([dashRes, usersRes]) => {
      setData(dashRes.data);
      setUsers(usersRes.data || []);
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

  const statusData = Object.entries(data?.application_status_counts || {}).map(([k, v]) => ({
    name: k, value: v,
  }));

  const skillsChart = (data?.top_skills || []).slice(0, 10).map((s) => ({
    name: s.skill,
    count: s.count,
  }));

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold mb-1">Admin Dashboard</h1>
      <p className="text-slate-500 text-sm mb-8">Platform overview and management</p>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard icon={<FiUsers />} value={data?.total_users || 0} label="Job Seekers" color="text-indigo-400" />
        <StatCard icon={<FiUsers />} value={data?.total_recruiters || 0} label="Recruiters" color="text-violet-400" />
        <StatCard icon={<FiBriefcase />} value={data?.active_jobs || 0} label="Active Jobs" color="text-green-400" />
        <StatCard icon={<FiFileText />} value={data?.total_applications || 0} label="Applications" color="text-amber-400" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Top Skills Chart */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">🔥 Most Demanded Skills</h3>
          {skillsChart.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={skillsChart} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} width={90} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 10 }} />
                <Bar dataKey="count" fill="#818cf8" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-600 text-sm">No data yet</p>
          )}
        </div>

        {/* Application Status Pie */}
        <div className="glass-card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">📊 Application Status</h3>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={statusData} cx="50%" cy="50%" innerRadius={50} outerRadius={90} dataKey="value" nameKey="name" label>
                  {statusData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 10 }} />
                <Legend wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-slate-600 text-sm">No applications yet</p>
          )}
        </div>
      </div>

      {/* Platform Stats */}
      <div className="grid lg:grid-cols-3 gap-4 mb-8">
        <div className="stat-card">
          <div className="stat-label">Avg Match Score</div>
          <div className="stat-value text-indigo-400">{data?.average_match_score || 0}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Recent Registrations (30d)</div>
          <div className="stat-value text-green-400">{data?.recent_registrations || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Matching Engine</div>
          <div className="stat-value text-violet-400 !text-lg">TF-IDF + BM25 + SBERT</div>
        </div>
      </div>

      {/* Users Table */}
      <div className="glass-card">
        <h3 className="text-sm font-semibold text-slate-300 mb-4">👥 All Users</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-slate-700/50">
                <th className="pb-3 font-medium">Username</th>
                <th className="pb-3 font-medium">Email</th>
                <th className="pb-3 font-medium">Role</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-slate-800/50">
                  <td className="py-3 text-slate-200 font-medium">{u.username}</td>
                  <td className="py-3 text-slate-400">{u.email}</td>
                  <td className="py-3">
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                      u.role === 'ADMIN' ? 'bg-violet-500/10 text-violet-400' :
                      u.role === 'RECRUITER' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-green-500/10 text-green-400'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="py-3">
                    <span className={`w-2 h-2 rounded-full inline-block ${u.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                  </td>
                  <td className="py-3 text-slate-500 text-xs">{new Date(u.date_joined).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
