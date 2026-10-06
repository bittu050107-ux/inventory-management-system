import api from './api';

export const inventoryService = {
  /**
   * GET /inventory
   * List all current stock levels
   */
  async getAllInventory(params = {}) {
    const response = await api.get('/inventory', { params });
    return response.data;
  },

  /**
   * GET /inventory/low-stock
   * Query products with stock <= threshold
   */
  async getLowStock(params = {}) {
    const response = await api.get('/inventory/low-stock', { params });
    return response.data;
  },

  /**
   * GET /inventory/{product_id}
   * Fetch specific product inventory record
   */
  async getProductInventory(productId) {
    const response = await api.get(`/inventory/${productId}`);
    return response.data;
  },

  /**
   * POST /inventory/stock-in
   * Increment stock and record audit log
   */
  async stockIn(data) {
    const response = await api.post('/inventory/stock-in', data);
    return response.data;
  },

  /**
   * POST /inventory/stock-out
   * Decrement stock and record audit log
   */
  async stockOut(data) {
    const response = await api.post('/inventory/stock-out', data);
    return response.data;
  },

  /**
   * POST /inventory/adjust
   * Correct stock level with audit reason
   */
  async adjustStock(data) {
    const response = await api.post('/inventory/adjust', data);
    return response.data;
  },

  /**
   * GET /inventory/{product_id}/transactions
   * Audit movement transaction history
   */
  async getTransactions(productId) {
    const response = await api.get(`/inventory/${productId}/transactions`);
    return response.data;
  },
};

export default inventoryService;
