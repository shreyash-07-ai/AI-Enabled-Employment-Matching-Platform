import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  FiHome, FiBriefcase, FiFileText, FiUsers, FiBarChart2,
  FiUpload, FiSearch, FiLogOut, FiUser, FiSettings
} from 'react-icons/fi';

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const seekerLinks = [
    { to: '/dashboard', icon: <FiHome />, label: 'Dashboard' },
    { to: '/jobs', icon: <FiSearch />, label: 'Browse Jobs' },
    { to: '/my-applications', icon: <FiBriefcase />, label: 'My Applications' },
    { to: '/upload-resume', icon: <FiUpload />, label: 'Upload Resume' },
    { to: '/profile', icon: <FiUser />, label: 'My Profile' },
  ];

  const recruiterLinks = [
    { to: '/dashboard', icon: <FiHome />, label: 'Dashboard' },
    { to: '/my-jobs', icon: <FiBriefcase />, label: 'My Job Posts' },
    { to: '/post-job', icon: <FiFileText />, label: 'Post a Job' },
    { to: '/profile', icon: <FiUser />, label: 'Company Profile' },
  ];

  const adminLinks = [
    { to: '/dashboard', icon: <FiHome />, label: 'Dashboard' },
    { to: '/admin/users', icon: <FiUsers />, label: 'Manage Users' },
    { to: '/admin/jobs', icon: <FiBriefcase />, label: 'All Jobs' },
    { to: '/admin/analytics', icon: <FiBarChart2 />, label: 'Analytics' },
    { to: '/admin/settings', icon: <FiSettings />, label: 'Settings' },
  ];

  const links =
    user?.role === 'ADMIN' ? adminLinks :
    user?.role === 'RECRUITER' ? recruiterLinks :
    seekerLinks;

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="mb-8 px-2">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
            AI
          </div>
          <div>
            <div className="text-sm font-bold text-slate-100">MatchAI</div>
            <div className="text-[10px] text-slate-500">Employment Platform</div>
          </div>
        </div>
      </div>

      {/* Role badge */}
      <div className="mb-6 px-2">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-indigo-400">
          {user?.role?.replace('_', ' ')}
        </span>
      </div>

      {/* Nav links */}
      <nav className="flex flex-col gap-1">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <span className="text-lg">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>

      {/* User & Logout */}
      <div className="mt-auto pt-8 border-t border-slate-700/50 mt-12">
        <div className="px-4 mb-3">
          <div className="text-sm font-medium text-slate-200">{user?.username}</div>
          <div className="text-[11px] text-slate-500">{user?.role?.replace('_', ' ')}</div>
        </div>
        <button
          onClick={handleLogout}
          className="sidebar-link w-full text-red-400 hover:text-red-300 hover:bg-red-500/10"
        >
          <FiLogOut className="text-lg" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
