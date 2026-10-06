import React, { useState, useEffect } from 'react';
import inventoryService from '../services/inventoryService';
import productService from '../services/productService';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';
import { formatDate, getStatusBadgeClass } from '../utils/helpers';
import {
  Boxes,
  ArrowDownRight,
  ArrowUpRight,
  Sliders,
  History,
  AlertTriangle,
  RefreshCw,
  Search,
  X,
  AlertCircle,
} from 'lucide-react';

export const Inventory = () => {
  const { isStaff } = useAuth();
  const [inventoryList, setInventoryList] = useState([]);
  const [lowStockList, setLowStockList] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('all'); // 'all' | 'low-stock' | 'history'
  const [searchTerm, setSearchTerm] = useState('');

  // Transaction history modal
  const [selectedProductHistory, setSelectedProductHistory] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loadingTransactions, setLoadingTransactions] = useState(false);

  // Stock action modal (stock-in, stock-out, adjust)
  const [modalMode, setModalMode] = useState(null); // 'IN' | 'OUT' | 'ADJUST'
  const [targetItem, setTargetItem] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchInventoryData = async () => {
    try {
      setRefreshing(true);
      const [inv, low, prods] = await Promise.all([
        inventoryService.getAllInventory().catch(() => []),
        inventoryService.getLowStock().catch(() => []),
        productService.getProducts().catch(() => []),
      ]);
      setInventoryList(inv || []);
      setLowStockList(low || []);
      setProducts(prods || []);
    } catch (err) {
      console.error('Failed to load inventory data', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchInventoryData();
  }, []);

  const openActionModal = (item, mode) => {
    setTargetItem(item);
    setModalMode(mode);
    setQuantity(mode === 'ADJUST' ? (item.quantity ?? item.stock ?? 0) : 1);
    setReason(
      mode === 'IN'
        ? 'Restock from supplier'
        : mode === 'OUT'
        ? 'Shipment dispatched'
        : 'Physical audit correction'
    );
    setError('');
  };

  const closeActionModal = () => {
    setModalMode(null);
    setTargetItem(null);
    setError('');
  };

  const handleActionSubmit = async (e) => {
    e.preventDefault();
    if (!targetItem) return;

    setSubmitting(true);
    setError('');

    try {
      const pId = targetItem.product_id || targetItem.id;
      if (modalMode === 'IN') {
        await inventoryService.stockIn({
          product_id: pId,
          quantity: parseInt(quantity),
          reason,
        });
      } else if (modalMode === 'OUT') {
        await inventoryService.stockOut({
          product_id: pId,
          quantity: parseInt(quantity),
          reason,
        });
      } else if (modalMode === 'ADJUST') {
        await inventoryService.adjustStock({
          product_id: pId,
          new_quantity: parseInt(quantity),
          reason,
        });
      }
      closeActionModal();
      await fetchInventoryData();
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Failed to process stock movement.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSubmitting(false);
    }
  };

  const viewHistory = async (item) => {
    const pId = item.product_id || item.id;
    setSelectedProductHistory(item);
    setLoadingTransactions(true);
    try {
      const logs = await inventoryService.getTransactions(pId);
      setTransactions(logs || []);
    } catch (err) {
      console.error('Failed to get transactions', err);
      setTransactions([]);
    } finally {
      setLoadingTransactions(false);
    }
  };

  const getProductName = (productId) => {
    const match = products.find((p) => p.id === productId);
    return match ? match.name : `Product #${productId}`;
  };

  const getProductSku = (productId) => {
    const match = products.find((p) => p.id === productId);
    return match ? match.sku : '—';
  };

  const displayList = activeTab === 'low-stock' ? lowStockList : inventoryList;

  const filteredDisplayList = displayList.filter((item) => {
    const pName = (item.product_name || getProductName(item.product_id)).toLowerCase();
    const pSku = (item.sku || getProductSku(item.product_id)).toLowerCase();
    const term = searchTerm.toLowerCase();
    return pName.includes(term) || pSku.includes(term);
  });

  if (loading) {
    return <Loading message="Loading warehouse stock levels..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Inventory Management</h1>
          <p className="page-subtitle">
            Track real-time stock balances, execute movements, and audit log entries
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={fetchInventoryData}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="tab-bar">
        <button
          className={`tab-btn ${activeTab === 'all' ? 'tab-btn-active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          <Boxes size={16} /> All Stock ({inventoryList.length})
        </button>
        <button
          className={`tab-btn ${
            activeTab === 'low-stock' ? 'tab-btn-active' : ''
          }`}
          onClick={() => setActiveTab('low-stock')}
        >
          <AlertTriangle size={16} className="text-warning" /> Low Stock Alerts (
          {lowStockList.length})
        </button>
      </div>

      {/* Filter Bar */}
      <div className="filter-bar">
        <div className="search-input-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="form-input search-input"
            placeholder="Search by product name or SKU..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Inventory Table */}
      <div className="card table-responsive">
        {filteredDisplayList.length === 0 ? (
          <div className="empty-state">
            <Boxes size={40} className="empty-state-icon" />
            <h3>No Inventory Records Found</h3>
            <p>Stock will automatically track as products are added or received.</p>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>SKU</th>
                <th>Current Stock</th>
                <th>Reorder Level</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Stock Operations</th>
              </tr>
            </thead>
            <tbody>
              {filteredDisplayList.map((item) => {
                const pId = item.product_id || item.id;
                const qty = item.quantity ?? item.stock ?? 0;
                const threshold = item.reorder_level || item.low_stock_threshold || 5;
                const isLow = qty <= threshold;
                const isOut = qty <= 0;
                const status = isOut
                  ? 'OUT_OF_STOCK'
                  : isLow
                  ? 'LOW_STOCK'
                  : 'IN_STOCK';

                return (
                  <tr key={item.id || pId}>
                    <td>
                      <strong>{item.product_name || getProductName(pId)}</strong>
                    </td>
                    <td>
                      <code className="text-mono">
                        {item.sku || getProductSku(pId)}
                      </code>
                    </td>
                    <td>
                      <span className="font-bold text-lg">{qty}</span>
                    </td>
                    <td>{threshold}</td>
                    <td>
                      <span className={`badge ${getStatusBadgeClass(status)}`}>
                        {status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="text-muted text-sm">
                      {formatDate(item.updated_at)}
                    </td>
                    <td>
                      <div className="action-buttons-row">
                        {isStaff && (
                          <>
                            <button
                              className="btn btn-sm btn-outline-success"
                              onClick={() => openActionModal(item, 'IN')}
                              title="Stock In"
                            >
                              <ArrowDownRight size={14} /> In
                            </button>
                            <button
                              className="btn btn-sm btn-outline-warning"
                              onClick={() => openActionModal(item, 'OUT')}
                              disabled={isOut}
                              title="Stock Out"
                            >
                              <ArrowUpRight size={14} /> Out
                            </button>
                            <button
                              className="btn btn-sm btn-outline-primary"
                              onClick={() => openActionModal(item, 'ADJUST')}
                              title="Adjust Stock"
                            >
                              <Sliders size={14} /> Adjust
                            </button>
                          </>
                        )}
                        <button
                          className="btn-icon-sm"
                          onClick={() => viewHistory(item)}
                          title="Audit Trail"
                        >
                          <History size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Movement Modal */}
      {modalMode && targetItem && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {modalMode === 'IN'
                  ? 'Stock In (Receive Inventory)'
                  : modalMode === 'OUT'
                  ? 'Stock Out (Disburse Inventory)'
                  : 'Inventory Stock Adjustment'}
              </h2>
              <button className="btn-icon" onClick={closeActionModal}>
                <X size={18} />
              </button>
            </div>

            {error && (
              <div className="alert alert-error">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleActionSubmit}>
              <div className="modal-body">
                <p className="mb-3">
                  Product:{' '}
                  <strong>
                    {targetItem.product_name ||
                      getProductName(targetItem.product_id || targetItem.id)}
                  </strong>
                </p>

                <div className="form-group">
                  <label className="form-label">
                    {modalMode === 'ADJUST'
                      ? 'New Exact Stock Level'
                      : 'Quantity to Transfer'}
                  </label>
                  <input
                    type="number"
                    min={modalMode === 'ADJUST' ? '0' : '1'}
                    className="form-input"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Audit Reason / Reference *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. PO-8899 or Warehouse count variance"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeActionModal}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={`btn ${
                    modalMode === 'IN'
                      ? 'btn-success'
                      : modalMode === 'OUT'
                      ? 'btn-warning'
                      : 'btn-primary'
                  }`}
                  disabled={submitting}
                >
                  {submitting
                    ? 'Submitting...'
                    : `Confirm ${
                        modalMode === 'IN'
                          ? 'Stock In'
                          : modalMode === 'OUT'
                          ? 'Stock Out'
                          : 'Adjustment'
                      }`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transaction History Modal */}
      {selectedProductHistory && (
        <div className="modal-backdrop">
          <div className="modal-content modal-lg">
            <div className="modal-header">
              <h2 className="modal-title">
                Stock Audit Trail:{' '}
                {selectedProductHistory.product_name ||
                  getProductName(
                    selectedProductHistory.product_id || selectedProductHistory.id
                  )}
              </h2>
              <button
                className="btn-icon"
                onClick={() => setSelectedProductHistory(null)}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              {loadingTransactions ? (
                <Loading message="Fetching transaction history..." />
              ) : transactions.length === 0 ? (
                <div className="empty-state">
                  <History size={32} className="empty-state-icon" />
                  <p>No historical stock movements found for this product.</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Type</th>
                        <th>Qty</th>
                        <th>Previous</th>
                        <th>New Bal</th>
                        <th>Reason</th>
                        <th>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {transactions.map((tx) => (
                        <tr key={tx.id}>
                          <td>
                            <span
                              className={`badge ${
                                tx.movement_type === 'IN' || tx.type === 'IN'
                                  ? 'badge-success'
                                  : tx.movement_type === 'OUT' || tx.type === 'OUT'
                                  ? 'badge-warning'
                                  : 'badge-info'
                              }`}
                            >
                              {tx.movement_type || tx.type}
                            </span>
                          </td>
                          <td className="font-semibold">{tx.quantity}</td>
                          <td className="text-muted">{tx.previous_quantity ?? '—'}</td>
                          <td className="font-bold">{tx.new_quantity ?? '—'}</td>
                          <td>{tx.reason || '—'}</td>
                          <td className="text-muted text-sm">
                            {formatDate(tx.created_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setSelectedProductHistory(null)}
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

export default Inventory;
