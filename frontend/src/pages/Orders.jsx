import React, { useState, useEffect } from 'react';
import orderService from '../services/orderService';
import productService from '../services/productService';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';
import { formatCurrency, formatDate, getStatusBadgeClass } from '../utils/helpers';
import { formatApiError } from '../services/api';
import {
  ShoppingCart,
  Plus,
  Eye,
  X,
  AlertCircle,
  CheckCircle,
  Truck,
  RotateCcw,
  Filter,
  Trash2,
} from 'lucide-react';

export const Orders = () => {
  const { user, isManager, isAdmin } = useAuth();
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Create Order Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [orderItems, setOrderItems] = useState([
    { product_id: '', quantity: 1, unit_price: 0 },
  ]);
  const [createError, setCreateError] = useState('');
  const [creating, setCreating] = useState(false);

  // View Order Details Modal
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [statusUpdating, setStatusUpdating] = useState(false);

  const fetchOrdersAndProducts = async () => {
    try {
      setLoading(true);
      const ordersPromise = (isManager || isAdmin)
        ? orderService.getOrders()
        : orderService.getMyOrders();

      const [ordList, prodList] = await Promise.all([
        ordersPromise.catch(() => []),
        productService.getProducts().catch(() => []),
      ]);
      setOrders(ordList || []);
      setProducts(prodList || []);
    } catch (err) {
      console.error('Failed to load orders', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrdersAndProducts();
  }, [user]);

  const handleDeleteOrder = async (orderId) => {
    if (window.confirm(`Permanently delete order #${orderId}? This cannot be undone.`)) {
      try {
        await orderService.deleteOrder(orderId);
        await fetchOrdersAndProducts();
      } catch (err) {
        alert(formatApiError(err, 'Failed to delete order.'));
      }
    }
  };

  // Handle Create Order
  const handleAddItemRow = () => {
    setOrderItems([
      ...orderItems,
      { product_id: '', quantity: 1, unit_price: 0 },
    ]);
  };

  const handleRemoveItemRow = (index) => {
    if (orderItems.length > 1) {
      setOrderItems(orderItems.filter((_, idx) => idx !== index));
    }
  };

  const handleItemChange = (index, field, value) => {
    const updated = [...orderItems];
    if (field === 'product_id') {
      const selected = products.find((p) => String(p.id) === String(value));
      updated[index] = {
        ...updated[index],
        product_id: value,
        unit_price: selected ? selected.price : 0,
      };
    } else {
      updated[index] = { ...updated[index], [field]: value };
    }
    setOrderItems(updated);
  };

  const calculateOrderTotal = () => {
    return orderItems.reduce((sum, item) => {
      return sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0);
    }, 0);
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    const validItems = orderItems.filter(
      (item) => item.product_id && Number(item.quantity) > 0
    );

    if (validItems.length === 0) {
      setCreateError('Please select at least one product with quantity > 0.');
      return;
    }

    setCreating(true);
    setCreateError('');

    try {
      const payload = {
        items: validItems.map((i) => ({
          product_id: parseInt(i.product_id),
          quantity: parseInt(i.quantity),
          unit_price: parseFloat(i.unit_price),
        })),
      };

      await orderService.createOrder(payload);
      setShowCreateModal(false);
      setOrderItems([{ product_id: '', quantity: 1, unit_price: 0 }]);
      await fetchOrdersAndProducts();
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Failed to create order.';
      setCreateError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setCreating(false);
    }
  };

  // Status Change (Admin/Manager)
  const handleStatusChange = async (orderId, newStatus) => {
    try {
      setStatusUpdating(true);
      await orderService.updateOrderStatus(orderId, newStatus);
      if (selectedOrder && selectedOrder.id === orderId) {
        setSelectedOrder({ ...selectedOrder, status: newStatus });
      }
      await fetchOrdersAndProducts();
    } catch (err) {
      alert(err.response?.data?.detail || 'Status transition failed.');
    } finally {
      setStatusUpdating(false);
    }
  };

  // Cancel Order
  const handleCancelOrder = async (orderId) => {
    if (
      window.confirm(
        'Cancel this order? Stock reserved for this order will be released back to inventory.'
      )
    ) {
      try {
        await orderService.cancelOrder(orderId);
        if (selectedOrder && selectedOrder.id === orderId) {
          setSelectedOrder({ ...selectedOrder, status: 'CANCELLED' });
        }
        await fetchOrdersAndProducts();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to cancel order.');
      }
    }
  };

  const filteredOrders = orders.filter((o) => {
    if (statusFilter === 'ALL') return true;
    return o.status === statusFilter;
  });

  if (loading) {
    return <Loading message="Loading orders and fulfillments..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Orders & Fulfillments</h1>
          <p className="page-subtitle">
            Manage customer purchases, status state machine, and inventory allocation
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-primary"
            onClick={() => {
              setOrderItems([
                {
                  product_id: products[0]?.id || '',
                  quantity: 1,
                  unit_price: products[0]?.price || 0,
                },
              ]);
              setCreateError('');
              setShowCreateModal(true);
            }}
          >
            <Plus size={16} /> Place New Order
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-bar">
        <div className="filter-select-box">
          <Filter size={16} className="select-icon" />
          <select
            className="form-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">All Statuses ({orders.length})</option>
            <option value="PENDING">Pending</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="SHIPPED">Shipped</option>
            <option value="DELIVERED">Delivered</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="card table-responsive">
        {filteredOrders.length === 0 ? (
          <div className="empty-state">
            <ShoppingCart size={40} className="empty-state-icon" />
            <h3>No Orders Found</h3>
            <p>Place an order to see it flow through the fulfillment lifecycle.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Order Ref</th>
                <th>Items Count</th>
                <th>Total Value</th>
                <th>Status</th>
                <th>Placed Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredOrders.map((ord) => (
                <tr key={ord.id}>
                  <td>
                    <code className="text-mono">#{ord.id?.slice(0, 8)}</code>
                  </td>
                  <td>{ord.items?.length || ord.total_items || 1} items</td>
                  <td className="font-bold">{formatCurrency(ord.total_amount)}</td>
                  <td>
                    <span className={`badge ${getStatusBadgeClass(ord.status)}`}>
                      {ord.status}
                    </span>
                  </td>
                  <td className="text-muted text-sm">
                    {formatDate(ord.created_at)}
                  </td>
                  <td>
                    <div className="action-buttons-row">
                      <button
                        className="btn-icon-sm"
                        onClick={() => setSelectedOrder(ord)}
                        title="View Order Details"
                      >
                        <Eye size={15} />
                      </button>
                      {ord.status !== 'CANCELLED' &&
                        ord.status !== 'DELIVERED' && (
                          <button
                            className="btn-icon-sm btn-danger-ghost"
                            onClick={() => handleCancelOrder(ord.id)}
                            title="Cancel Order"
                          >
                            <RotateCcw size={15} />
                          </button>
                        )}
                      {isAdmin && (
                        <button
                          className="btn-icon-sm btn-danger-ghost"
                          onClick={() => handleDeleteOrder(ord.id)}
                          title="Delete Order (Admin)"
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Place Order Modal */}
      {showCreateModal && (
        <div className="modal-backdrop">
          <div className="modal-content modal-lg">
            <div className="modal-header">
              <h2 className="modal-title">Place Customer Order</h2>
              <button
                className="btn-icon"
                onClick={() => setShowCreateModal(false)}
              >
                <X size={18} />
              </button>
            </div>

            {createError && (
              <div className="alert alert-error">
                <AlertCircle size={16} />
                <span>{createError}</span>
              </div>
            )}

            <form onSubmit={handleCreateOrder}>
              <div className="modal-body">
                <p className="text-sm text-muted mb-3">
                  Adding products automatically checks stock and reserves items.
                </p>

                <div className="order-items-builder">
                  {orderItems.map((item, idx) => (
                    <div key={idx} className="order-item-row">
                      <div className="form-group flex-2">
                        <label className="form-label text-xs">Product</label>
                        <select
                          className="form-select"
                          value={item.product_id}
                          onChange={(e) =>
                            handleItemChange(idx, 'product_id', e.target.value)
                          }
                          required
                        >
                          <option value="">Select Product</option>
                          {products.map((p) => (
                            <option key={p.id} value={p.id}>
                              {p.name} ({p.sku}) — {formatCurrency(p.price)} [Stock:{' '}
                              {p.stock_quantity ?? p.stock ?? 0}]
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="form-group flex-1">
                        <label className="form-label text-xs">Quantity</label>
                        <input
                          type="number"
                          min="1"
                          className="form-input"
                          value={item.quantity}
                          onChange={(e) =>
                            handleItemChange(idx, 'quantity', e.target.value)
                          }
                          required
                        />
                      </div>

                      <div className="form-group flex-1">
                        <label className="form-label text-xs">Unit Price</label>
                        <input
                          type="number"
                          step="0.01"
                          className="form-input"
                          value={item.unit_price}
                          readOnly
                        />
                      </div>

                      <div className="form-group flex-1">
                        <label className="form-label text-xs">Subtotal</label>
                        <div className="form-input-readonly">
                          {formatCurrency(item.quantity * item.unit_price)}
                        </div>
                      </div>

                      {orderItems.length > 1 && (
                        <button
                          type="button"
                          className="btn-icon-sm btn-danger-ghost self-center mt-3"
                          onClick={() => handleRemoveItemRow(idx)}
                        >
                          <X size={16} />
                        </button>
                      )}
                    </div>
                  ))}

                  <button
                    type="button"
                    className="btn btn-sm btn-secondary mt-2"
                    onClick={handleAddItemRow}
                  >
                    <Plus size={14} /> Add Another Item
                  </button>
                </div>

                <div className="order-summary-box mt-4">
                  <span className="order-summary-label">Estimated Total:</span>
                  <span className="order-summary-total">
                    {formatCurrency(calculateOrderTotal())}
                  </span>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={creating}
                >
                  {creating ? 'Submitting Order...' : 'Confirm Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Order Details & Status Transition Modal */}
      {selectedOrder && (
        <div className="modal-backdrop">
          <div className="modal-content modal-lg">
            <div className="modal-header">
              <div>
                <h2 className="modal-title">
                  Order Details #{selectedOrder.id?.slice(0, 8)}
                </h2>
                <span
                  className={`badge ${getStatusBadgeClass(
                    selectedOrder.status
                  )} mt-1`}
                >
                  {selectedOrder.status}
                </span>
              </div>
              <button
                className="btn-icon"
                onClick={() => setSelectedOrder(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="order-details-meta">
                <div>
                  <span className="meta-label">Customer ID / User</span>
                  <span className="meta-value">
                    {selectedOrder.user_id || 'System User'}
                  </span>
                </div>
                <div>
                  <span className="meta-label">Date Placed</span>
                  <span className="meta-value">
                    {formatDate(selectedOrder.created_at)}
                  </span>
                </div>
                <div>
                  <span className="meta-label">Total Amount</span>
                  <span className="meta-value font-bold text-accent">
                    {formatCurrency(selectedOrder.total_amount)}
                  </span>
                </div>
              </div>

              <h4 className="mt-4 mb-2 text-sm font-semibold">Ordered Items</h4>
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Quantity</th>
                      <th>Unit Price</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(selectedOrder.items || []).map((item, i) => (
                      <tr key={item.id || i}>
                        <td>
                          <strong>
                            {item.product_name || `Product #${item.product_id}`}
                          </strong>
                        </td>
                        <td>{item.quantity}</td>
                        <td>{formatCurrency(item.unit_price)}</td>
                        <td>
                          {formatCurrency(item.quantity * item.unit_price)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Status transition controls for Manager/Admin */}
              {(isManager || isAdmin) && selectedOrder.status !== 'CANCELLED' && (
                <div className="status-lifecycle-box mt-4">
                  <h4 className="text-sm font-semibold mb-2">
                    Update Order Status (State Machine)
                  </h4>
                  <div className="flex gap-2 flex-wrap">
                    {selectedOrder.status === 'PENDING' && (
                      <button
                        className="btn btn-sm btn-primary"
                        onClick={() =>
                          handleStatusChange(selectedOrder.id, 'CONFIRMED')
                        }
                        disabled={statusUpdating}
                      >
                        Confirm Order
                      </button>
                    )}
                    {selectedOrder.status === 'CONFIRMED' && (
                      <button
                        className="btn btn-sm btn-info"
                        onClick={() =>
                          handleStatusChange(selectedOrder.id, 'SHIPPED')
                        }
                        disabled={statusUpdating}
                      >
                        <Truck size={14} /> Mark as Shipped
                      </button>
                    )}
                    {selectedOrder.status === 'SHIPPED' && (
                      <button
                        className="btn btn-sm btn-success"
                        onClick={() =>
                          handleStatusChange(selectedOrder.id, 'DELIVERED')
                        }
                        disabled={statusUpdating}
                      >
                        <CheckCircle size={14} /> Mark as Delivered
                      </button>
                    )}
                    {selectedOrder.status !== 'DELIVERED' && (
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleCancelOrder(selectedOrder.id)}
                        disabled={statusUpdating}
                      >
                        <RotateCcw size={14} /> Cancel & Restore Stock
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setSelectedOrder(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Orders;
