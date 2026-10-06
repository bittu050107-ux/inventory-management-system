import api from './api';

export const orderService = {
  /**
   * GET /orders
   * Retrieve all orders (Admin / Manager)
   */
  async getOrders(params = {}) {
    const response = await api.get('/orders', { params });
    // In order service, response is { orders: [...], total: ... } or list
    if (response.data && Array.isArray(response.data.orders)) {
      return response.data.orders;
    }
    return Array.isArray(response.data) ? response.data : [];
  },

  /**
   * GET /orders/my
   * Retrieve orders placed by the currently logged-in user
   */
  async getMyOrders(params = {}) {
    const response = await api.get('/orders/my', { params });
    if (response.data && Array.isArray(response.data.orders)) {
      return response.data.orders;
    }
    return Array.isArray(response.data) ? response.data : [];
  },

  /**
   * GET /orders/{id}
   * Fetch single order details with itemized list
   */
  async getOrderById(orderId) {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  /**
   * POST /orders
   * Create a new customer order (reserves inventory stock)
   */
  async createOrder(orderData) {
    const response = await api.post('/orders', orderData);
    return response.data;
  },

  /**
   * PUT /orders/{id}/status
   * Advance order status through fulfillment lifecycle
   */
  async updateOrderStatus(orderId, status) {
    const response = await api.put(`/orders/${orderId}/status`, { status });
    return response.data;
  },

  /**
   * POST /orders/{id}/cancel
   * Cancel order and restore reserved stock to inventory
   */
  async cancelOrder(orderId) {
    const response = await api.post(`/orders/${orderId}/cancel`);
    return response.data;
  },

  /**
   * DELETE /orders/{id}
   * Hard delete order (Admin only)
   */
  async deleteOrder(orderId) {
    const response = await api.delete(`/orders/${orderId}`);
    return response.data;
  },
};

export default orderService;
