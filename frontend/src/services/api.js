import axios from 'axios';

const API = axios.create({ baseURL: '/api' });

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401
API.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const { data } = await axios.post('/api/accounts/token/refresh/', { refresh });
          localStorage.setItem('access_token', data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return API(original);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(err);
  }
);

// ── Auth ────────────────────────────────────────────────────
export const register = (data) => API.post('/accounts/register/', data);
export const login = (data) => API.post('/accounts/login/', data);

// ── Profiles ────────────────────────────────────────────────
export const getJobSeekerProfile = () => API.get('/accounts/profile/job-seeker/');
export const updateJobSeekerProfile = (data) => API.patch('/accounts/profile/job-seeker/', data);
export const getRecruiterProfile = () => API.get('/accounts/profile/recruiter/');
export const updateRecruiterProfile = (data) => API.patch('/accounts/profile/recruiter/', data);

// ── Jobs ────────────────────────────────────────────────────
export const getJobs = () => API.get('/jobs/');
export const getJob = (id) => API.get(`/jobs/${id}/`);
export const createJob = (data) => API.post('/jobs/', data);
export const updateJob = (id, data) => API.patch(`/jobs/${id}/`, data);
export const deleteJob = (id) => API.delete(`/jobs/${id}/`);
export const getRecruiterJobs = () => API.get('/jobs/recruiter/');

// ── Resumes ─────────────────────────────────────────────────
export const uploadResume = (formData) =>
  API.post('/resumes/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const getMyResumes = () => API.get('/resumes/my-resumes/');

// ── Applications ────────────────────────────────────────────
export const applyToJob = (data) => API.post('/resumes/apply/', data);
export const getMyApplications = () => API.get('/resumes/applications/');
export const getApplicants = (jobId) => API.get(`/resumes/applicants/${jobId}/`);
export const updateApplicationStatus = (id, status) =>
  API.patch(`/resumes/application/${id}/status/`, { status });
export const getMatchAnalysis = (applicationId) =>
  API.get(`/resumes/match-analysis/${applicationId}/`);
export const getRecommendedJobs = () => API.get('/resumes/recommended-jobs/');

// ── Dashboards ──────────────────────────────────────────────
export const getAdminDashboard = () => API.get('/accounts/dashboard/admin/');
export const getRecruiterDashboard = () => API.get('/accounts/dashboard/recruiter/');
export const getJobSeekerDashboard = () => API.get('/accounts/dashboard/job-seeker/');
export const getAdminUsers = () => API.get('/accounts/admin/users/');

export default API;
