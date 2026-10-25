import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { register as registerAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [searchParams] = useSearchParams();
  const defaultRole = searchParams.get('role') || 'JOB_SEEKER';

  const [form, setForm] = useState({
    username: '', email: '', password: '', confirmPassword: '', role: defaultRole,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await registerAPI({
        username: form.username,
        email: form.email,
        password: form.password,
        role: form.role,
      });
      navigate('/login');
    } catch (err) {
      const data = err.response?.data;
      const msg = data
        ? Object.values(data).flat().join(' ')
        : 'Registration failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gradient-bg min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      <div className="blob w-96 h-96 bg-purple-600 -top-20 right-0" />
      <div className="blob w-80 h-80 bg-indigo-600 bottom-10 -left-10" style={{ animationDelay: '2s' }} />

      <div className="glass-card w-full max-w-md relative z-10 animate-fade-in">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold">
            AI
          </div>
          <div>
            <div className="text-lg font-bold text-slate-100">MatchAI</div>
            <div className="text-[11px] text-slate-500">Create your account</div>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Role selector */}
          <div className="flex gap-2">
            {['JOB_SEEKER', 'RECRUITER'].map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => setForm({ ...form, role })}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  form.role === role
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    : 'bg-slate-800/50 text-slate-500 border border-slate-700/50 hover:text-slate-300'
                }`}
              >
                {role === 'JOB_SEEKER' ? '🎯 Job Seeker' : '🏢 Recruiter'}
              </button>
            ))}
          </div>

          <div>
            <label className="text-xs text-slate-400 mb-1 block">Username</label>
            <input
              type="text" className="input-field" placeholder="Choose a username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Email</label>
            <input
              type="email" className="input-field" placeholder="your@email.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Password</label>
            <input
              type="password" className="input-field" placeholder="Create a strong password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Confirm Password</label>
            <input
              type="password" className="input-field" placeholder="Repeat password"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
              required
            />
          </div>

          <button type="submit" className="btn-primary w-full mt-2" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
