import api from './api';

export const userService = {
  /**
   * GET /users/me
   * Retrieve the authenticated user's profile details
   */
  async getProfile() {
    const response = await api.get('/users/me');
    return response.data;
  },

  /**
   * PUT /users/me
   * Update current user's profile attributes (name, phone, address)
   */
  async updateProfile(profileData) {
    const response = await api.put('/users/me', profileData);
    return response.data;
  },

  /**
   * GET /users
   * List system users (Admin access)
   */
  async getUsers(params = {}) {
    const response = await api.get('/users', { params });
    return Array.isArray(response.data) ? response.data : [];
  },

  /**
   * GET /users/{id}
   * Get specific user by ID
   */
  async getUserById(id) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  /**
   * PUT /users/{id}/role
   * Update a user's RBAC role
   */
  async updateUserRole(id, role) {
    const response = await api.put(`/users/${id}/role`, { role });
    return response.data;
  },
};

export default userService;
