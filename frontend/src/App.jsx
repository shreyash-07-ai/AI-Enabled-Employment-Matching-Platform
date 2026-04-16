import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import DashboardLayout from './components/DashboardLayout';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import JobSeekerDashboard from './pages/JobSeekerDashboard';
import RecruiterDashboard from './pages/RecruiterDashboard';
import AdminDashboard from './pages/AdminDashboard';
import BrowseJobsPage from './pages/BrowseJobsPage';
import MyApplicationsPage from './pages/MyApplicationsPage';
import UploadResumePage from './pages/UploadResumePage';
import PostJobPage from './pages/PostJobPage';
import MyJobsPage from './pages/MyJobsPage';
import ProfilePage from './pages/ProfilePage';

function DashboardRouter() {
  const { user } = useAuth();
  if (user?.role === 'ADMIN') return <AdminDashboard />;
  if (user?.role === 'RECRUITER') return <RecruiterDashboard />;
  return <JobSeekerDashboard />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected routes (wrapped in DashboardLayout with Sidebar) */}
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<DashboardRouter />} />
            <Route path="/jobs" element={<BrowseJobsPage />} />
            <Route path="/my-applications" element={<MyApplicationsPage />} />
            <Route path="/upload-resume" element={<UploadResumePage />} />
            <Route path="/post-job" element={<PostJobPage />} />
            <Route path="/my-jobs" element={<MyJobsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            {/* Admin routes */}
            <Route path="/admin/users" element={<AdminDashboard />} />
            <Route path="/admin/jobs" element={<BrowseJobsPage />} />
            <Route path="/admin/analytics" element={<AdminDashboard />} />
            <Route path="/admin/settings" element={<ProfilePage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
