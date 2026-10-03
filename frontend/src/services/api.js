import axios from 'axios';

const rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
let cleanBaseUrl = rawBaseUrl.replace(/\/+$/, '');
if (cleanBaseUrl.endsWith('/api')) {
  cleanBaseUrl = cleanBaseUrl.slice(0, -4).replace(/\/+$/, '');
}
const API_BASE_URL = cleanBaseUrl;

const api = axios.create({
  baseURL: API_BASE_URL || undefined,
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh and centralized error normalization
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes('/api/accounts/login/') &&
      !originalRequest.url?.includes('/api/accounts/register/') &&
      !originalRequest.url?.includes('/api/accounts/refresh/')
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_BASE_URL}/api/accounts/refresh/`, {
            refresh: refreshToken,
          });
          const newAccess = res.data.access;
          localStorage.setItem('access_token', newAccess);
          if (res.data.refresh) {
            localStorage.setItem('refresh_token', res.data.refresh);
          }
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return api(originalRequest);
        } catch (refreshErr) {
          // Token refresh failed; clear auth
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.dispatchEvent(new Event('auth-logout'));
        }
      }
    }

    // Centralized error normalization (Phase 4D)
    if (!error.response) {
      error.userMessage = 'Unable to connect to the server. Please check your connection and try again.';
    } else {
      const status = error.response.status;
      if (status >= 500 && (!error.response.data || typeof error.response.data !== 'object' || !error.response.data.detail)) {
        error.response.data = { detail: 'Something went wrong. Please try again later.' };
      } else if (status === 403 && (!error.response.data || !error.response.data.detail)) {
        error.response.data = { detail: 'You do not have permission to perform this action.' };
      } else if (status === 404 && (!error.response.data || !error.response.data.detail)) {
        error.response.data = { detail: 'The requested resource was not found.' };
      }
    }

    return Promise.reject(error);
  }
);

/**
 * Extracts a user-facing, sanitized error message from an API error response.
 * Preserves specific validation errors and rate limiting messages while sanitizing 500s and network errors.
 */
export const extractErrorMessage = (error, defaultMsg = 'Something went wrong. Please try again later.') => {
  if (!error) return defaultMsg;
  if (!error.response) {
    return 'Unable to connect to the server. Please check your connection and try again.';
  }
  const status = error.response.status;
  const data = error.response.data;

  if (status === 429) {
    return data?.detail || 'Too many requests. Please wait a while before trying again.';
  }
  if (status === 401) {
    return data?.detail || 'Invalid username or password.';
  }
  if (status === 403) {
    return data?.detail || 'You do not have permission to perform this action.';
  }
  if (status === 404) {
    return data?.detail || 'The requested resource was not found.';
  }
  if (status >= 500) {
    return data?.detail || 'Something went wrong. Please try again later.';
  }

  // 400 Validation errors
  if (data) {
    if (typeof data === 'string') return data;
    if (data.detail && typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) return data.detail.join(' ');
    if (data.non_field_errors) {
      return Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors;
    }
    for (const key of Object.keys(data)) {
      const val = data[key];
      if (Array.isArray(val) && val.length > 0) return `${val[0]}`;
      if (typeof val === 'string') return val;
    }
  }

  return defaultMsg;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/api/health/');
  return response.data;
};

// Accounts
export const registerUser = async (userData) => {
  const response = await api.post('/api/accounts/register/', userData);
  return response.data;
};

export const loginUser = async (credentials) => {
  const response = await api.post('/api/accounts/login/', credentials);
  return response.data;
};

export const fetchCurrentUser = async () => {
  const response = await api.get('/api/accounts/me/');
  return response.data;
};

export const requestPasswordReset = async (email) => {
  const response = await api.post('/api/accounts/password-reset/', { email });
  return response.data;
};

export const confirmPasswordReset = async ({ uid, token, new_password, confirm_password }) => {
  const response = await api.post('/api/accounts/password-reset-confirm/', {
    uid,
    token,
    new_password,
    confirm_password,
  });
  return response.data;
};

export const updateProfile = async (profileData) => {
  const response = await api.patch('/api/accounts/me/', profileData);
  return response.data;
};

export const changePassword = async ({ current_password, new_password, confirm_password }) => {
  const response = await api.post('/api/accounts/change-password/', {
    current_password,
    new_password,
    confirm_password,
  });
  return response.data;
};

export const deleteAccount = async () => {
  const response = await api.delete('/api/accounts/me/');
  return response.data;
};



// Resumes
export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/resumes/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const fetchResumes = async () => {
  const response = await api.get('/api/resumes/');
  return response.data;
};

export const deleteResume = async (id) => {
  const response = await api.delete(`/api/resumes/${id}/`);
  return response.data;
};

// Jobs
export const createJob = async (jobData) => {
  const response = await api.post('/api/jobs/', jobData);
  return response.data;
};

export const fetchJobs = async () => {
  const response = await api.get('/api/jobs/');
  return response.data;
};

// Analysis
export const startAnalysis = async (payload) => {
  const response = await api.post('/api/analysis/start/', payload);
  return response.data;
};

export const fetchAnalyses = async () => {
  const response = await api.get('/api/analysis/');
  return response.data;
};

export const fetchAnalysisDetail = async (id) => {
  const response = await api.get(`/api/analysis/${id}/`);
  return response.data;
};

export default api;
