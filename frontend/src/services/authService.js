import api from './api';

export const authService = {
  /**
   * POST /auth/login
   * Authenticate with email/password and receive JWT token + role
   */
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  /**
   * POST /auth/register
   * Create a new user account
   */
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  /**
   * GET /auth/me
   * Retrieve current authenticated user's id and role
   */
  async getMe() {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * GET /auth/admin-test
   * Verify admin role privileges
   */
  async adminTest() {
    const response = await api.get('/auth/admin-test');
    return response.data;
  },
};

export default authService;
