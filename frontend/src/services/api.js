import axios from 'axios';

// API Base URL through API Gateway
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor: automatically attach JWT Authorization header
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: automatically handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Avoid redirect loop when login attempt fails
      if (!error.config?.url?.includes('/auth/login')) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

/**
 * Format any API or network error into a clean, human-readable string
 */
export const formatApiError = (error, defaultMsg = 'An unexpected error occurred.') => {
  if (!error) return defaultMsg;
  if (error.code === 'ERR_NETWORK') {
    return 'Unable to reach API Gateway. Please verify backend services and API Gateway (port 8000) are running.';
  }
  if (error.response) {
    const { status, data } = error.response;
    if (status === 403) return 'Access denied. You do not have permission to perform this action.';
    if (status === 404) return data?.detail || 'Requested resource was not found.';
    if (status === 409) return data?.detail || 'A conflict occurred with existing records.';
    if (status === 503) return 'Service temporarily unavailable. Please try again shortly.';
    if (data?.detail) {
      if (typeof data.detail === 'string') return data.detail;
      if (Array.isArray(data.detail)) return data.detail.map((d) => d.msg || d).join(', ');
      return JSON.stringify(data.detail);
    }
    if (data?.message) return data.message;
  }
  return error.message || defaultMsg;
};

export default api;
