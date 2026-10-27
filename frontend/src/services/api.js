import axios from 'axios';

/**
 * Normalizes API base URL:
 * - Defaults to '/api' for local development (handled by Vite proxy)
 * - Strips trailing slashes
 * - Ensures it ends with '/api' without duplicating '/api/api'
 */
function getApiBaseUrl() {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
  if (!envUrl) {
    return '/api';
  }
  const clean = envUrl.replace(/\/+$/, '');
  if (clean.endsWith('/api')) {
    return clean;
  }
  return `${clean}/api`;
}

const BASE_URL = getApiBaseUrl();

const API = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 60s timeout to allow Render free tier cold-start
});

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
          const { data } = await axios.post(`${BASE_URL}/accounts/token/refresh/`, { refresh });
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

/**
 * Extract a human-readable error message from an Axios error.
 *
 * Handles:
 *  - Network / no-response errors (backend down, CORS blocked, cold-start timeout)
 *  - Django REST Framework field validation errors  { field: ["msg", ...] }
 *  - DRF non-field errors                          { non_field_errors: ["msg"] }
 *  - DRF detail errors                             { detail: "msg" }
 *  - Plain string bodies
 *  - HTML responses (Django debug page, Vercel 404)
 *  - Array of messages
 *  - HTTP 400 / 401 / 403 / 404 / 409 / 429 / 500
 *
 * Never renders a raw JavaScript object, never exposes tracebacks or secrets.
 */
export function getErrorMessage(err) {
  // Network error — no response received at all
  if (!err.response) {
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
      return 'Request timed out — server may be spinning up on free tier. Please retry in 30 seconds.';
    }
    return 'Network error — please check your connection or wait 30-60s for server cold start.';
  }

  const status = err.response.status;
  const data = err.response.data;

  // 5xx — never leak server internals
  if (status >= 500) {
    return 'Server error — please try again later.';
  }

  // 429 Too Many Requests
  if (status === 429) {
    return 'Too many requests — please wait a moment and try again.';
  }

  // No body
  if (data === null || data === undefined) {
    return `Request failed (HTTP ${status}).`;
  }

  // HTML response (Django debug page, Vercel 404, nginx error page)
  if (typeof data === 'string') {
    if (data.trim().startsWith('<')) {
      return `Request failed (HTTP ${status}). The server returned an unexpected response.`;
    }
    return data;
  }

  // DRF validation object: { field: ["msg", ...], non_field_errors: [...], detail: "..." }
  if (typeof data === 'object' && !Array.isArray(data)) {
    const messages = [];

    // Prioritise top-level detail
    if (data.detail) {
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    }

    for (const [field, value] of Object.entries(data)) {
      const label = field === 'non_field_errors' ? '' : `${field}: `;
      if (Array.isArray(value)) {
        messages.push(`${label}${value.join(' ')}`);
      } else if (typeof value === 'string') {
        messages.push(`${label}${value}`);
      } else if (typeof value === 'object' && value !== null) {
        // Nested validation objects (rare but possible)
        messages.push(`${label}${JSON.stringify(value)}`);
      }
    }

    if (messages.length > 0) return messages.join(' | ');
  }

  // Array of messages
  if (Array.isArray(data)) {
    return data.map((m) => (typeof m === 'string' ? m : JSON.stringify(m))).join(' ');
  }

  return `Request failed (HTTP ${status}).`;
}

// ── Auth ──────────────────────────────────────────────────────────────────
export const register = (data) => API.post('/accounts/register/', data);
export const login = (data) => API.post('/accounts/login/', data);

// ── Profiles ──────────────────────────────────────────────────────────────
export const getJobSeekerProfile = () => API.get('/accounts/profile/job-seeker/');
export const updateJobSeekerProfile = (data) => API.patch('/accounts/profile/job-seeker/', data);
export const getRecruiterProfile = () => API.get('/accounts/profile/recruiter/');
export const updateRecruiterProfile = (data) => API.patch('/accounts/profile/recruiter/', data);

// ── Jobs ──────────────────────────────────────────────────────────────────
export const getJobs = () => API.get('/jobs/');
export const getJob = (id) => API.get(`/jobs/${id}/`);
export const createJob = (data) => API.post('/jobs/', data);
export const updateJob = (id, data) => API.patch(`/jobs/${id}/`, data);
export const deleteJob = (id) => API.delete(`/jobs/${id}/`);
export const getRecruiterJobs = () => API.get('/jobs/recruiter/');

// ── Resumes ───────────────────────────────────────────────────────────────
export const uploadResume = (formData) =>
  API.post('/resumes/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
export const getMyResumes = () => API.get('/resumes/my-resumes/');

// ── Applications ──────────────────────────────────────────────────────────
export const applyToJob = (data) => API.post('/resumes/apply/', data);
export const getMyApplications = () => API.get('/resumes/applications/');
export const getApplicants = (jobId) => API.get(`/resumes/applicants/${jobId}/`);
export const updateApplicationStatus = (id, status) =>
  API.patch(`/resumes/application/${id}/status/`, { status });
export const getMatchAnalysis = (applicationId) =>
  API.get(`/resumes/match-analysis/${applicationId}/`);
export const getRecommendedJobs = () => API.get('/resumes/recommended-jobs/');

// ── Dashboards ────────────────────────────────────────────────────────────
export const getAdminDashboard = () => API.get('/accounts/dashboard/admin/');
export const getRecruiterDashboard = () => API.get('/accounts/dashboard/recruiter/');
export const getJobSeekerDashboard = () => API.get('/accounts/dashboard/job-seeker/');
export const getAdminUsers = () => API.get('/accounts/admin/users/');

export default API;
