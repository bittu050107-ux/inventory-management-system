import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import productService from '../services/productService';
import inventoryService from '../services/inventoryService';
import orderService from '../services/orderService';
import userService from '../services/userService';
import { formatCurrency, formatDate, getStatusBadgeClass } from '../utils/helpers';
import Loading from '../components/Loading';
import {
  Package,
  Boxes,
  AlertTriangle,
  ShoppingCart,
  ArrowUpRight,
  Plus,
  RefreshCw,
  Server,
  Activity,
} from 'lucide-react';

export const Dashboard = () => {
  const { user, isStaff, isAdmin } = useAuth();
  const [stats, setStats] = useState({
    totalProducts: 0,
    lowStockCount: 0,
    totalStockUnits: 0,
    totalOrders: 0,
    totalUsers: 0,
  });
  const [lowStockItems, setLowStockItems] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      setRefreshing(true);
      const ordersPromise = (user?.role === 'ADMIN' || user?.role === 'MANAGER')
        ? orderService.getOrders()
        : orderService.getMyOrders();

      const [productsRes, lowStockRes, ordersRes, usersRes] = await Promise.allSettled([
        productService.getProducts(),
        inventoryService.getLowStock(),
        ordersPromise,
        isAdmin ? userService.getUsers() : Promise.resolve([]),
      ]);

      const products = productsRes.status === 'fulfilled' ? (productsRes.value || []) : [];
      const lowStock = lowStockRes.status === 'fulfilled' ? (lowStockRes.value || []) : [];
      const orders = ordersRes.status === 'fulfilled' ? (ordersRes.value || []) : [];
      const users = usersRes.status === 'fulfilled' ? (usersRes.value || []) : [];

      const totalStock = products.reduce(
        (sum, p) => sum + (Number(p.stock_quantity ?? p.stock ?? 0)),
        0
      );

      setStats({
        totalProducts: products.length,
        lowStockCount: lowStock.length,
        totalStockUnits: totalStock,
        totalOrders: orders.length,
        totalUsers: users.length,
      });

      setLowStockItems(lowStock.slice(0, 5));
      setRecentOrders(orders.slice(0, 5));
    } catch (err) {
      console.error('Error fetching dashboard stats', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <Loading message="Loading dashboard metrics..." />;
  }

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Operational Dashboard</h1>
          <p className="page-subtitle">
            Welcome back, <strong>{user?.email || 'User'}</strong> • Role:{' '}
            <span className="text-accent font-semibold">{user?.role}</span>
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={fetchDashboardData}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} /> Refresh
          </button>
          {isStaff && (
            <Link to="/products" className="btn btn-primary">
              <Plus size={16} /> Add Product
            </Link>
          )}
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon-wrapper stat-primary">
            <Package size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Products</span>
            <span className="stat-value">{stats.totalProducts}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-info">
            <Boxes size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Stock Units</span>
            <span className="stat-value">{stats.totalStockUnits.toLocaleString()}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-warning">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Low Stock Alerts</span>
            <span className="stat-value text-warning">{stats.lowStockCount}</span>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon-wrapper stat-purple">
            <ShoppingCart size={24} />
          </div>
          <div className="stat-content">
            <span className="stat-label">Total Orders</span>
            <span className="stat-value">{stats.totalOrders}</span>
          </div>
        </div>

        {isAdmin && (
          <div className="stat-card">
            <div className="stat-icon-wrapper" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#c084fc' }}>
              <Activity size={24} />
            </div>
            <div className="stat-content">
              <span className="stat-label">System Users</span>
              <span className="stat-value">{stats.totalUsers}</span>
            </div>
          </div>
        )}
      </div>

      {/* Microservices Architecture Status */}
      <div className="card microservices-card">
        <div className="card-header">
          <div className="card-title-group">
            <Server size={18} className="text-accent" />
            <h2 className="card-title">Microservice Ecosystem Health</h2>
          </div>
          <span className="badge badge-success">Gateway Connected</span>
        </div>
        <div className="microservices-grid">
          <div className="service-status-chip">
            <span className="status-dot online"></span>
            <div>
              <strong>API Gateway</strong>
              <small>Port 8000</small>
            </div>
          </div>
          <div className="service-status-chip">
            <span className="status-dot online"></span>
            <div>
              <strong>Auth Service</strong>
              <small>Port 8001</small>
            </div>
          </div>
          <div className="service-status-chip">
            <span className="status-dot online"></span>
            <div>
              <strong>Product Service</strong>
              <small>Port 8003</small>
            </div>
          </div>
          <div className="service-status-chip">
            <span className="status-dot online"></span>
            <div>
              <strong>Inventory Service</strong>
              <small>Port 8004</small>
            </div>
          </div>
          <div className="service-status-chip">
            <span className="status-dot online"></span>
            <div>
              <strong>Order Service</strong>
              <small>Port 8005</small>
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout for Low Stock & Recent Orders */}
      <div className="dashboard-split-grid">
        {/* Low Stock Alerts */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <AlertTriangle size={18} className="text-warning" />
              <h2 className="card-title">Low Stock Warnings</h2>
            </div>
            <Link to="/inventory" className="card-link">
              View All <ArrowUpRight size={14} />
            </Link>
          </div>
          <div className="card-body">
            {lowStockItems.length === 0 ? (
              <div className="empty-state">
                <Boxes size={32} className="empty-state-icon" />
                <p>All stock levels are optimal.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Quantity</th>
                      <th>Threshold</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowStockItems.map((item) => (
                      <tr key={item.id || item.product_id}>
                        <td>
                          <strong>{item.product_name || `Product #${item.product_id}`}</strong>
                        </td>
                        <td>
                          <span className="text-danger font-bold">
                            {item.quantity ?? item.stock}
                          </span>
                        </td>
                        <td>{item.reorder_level || item.low_stock_threshold || 5}</td>
                        <td>
                          <Link
                            to="/inventory"
                            className="btn btn-sm btn-outline-primary"
                          >
                            Restock
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Recent Orders */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <Activity size={18} className="text-primary" />
              <h2 className="card-title">Recent Orders</h2>
            </div>
            <Link to="/orders" className="card-link">
              View All <ArrowUpRight size={14} />
            </Link>
          </div>
          <div className="card-body">
            {recentOrders.length === 0 ? (
              <div className="empty-state">
                <ShoppingCart size={32} className="empty-state-icon" />
                <p>No recent orders found.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentOrders.map((order) => (
                      <tr key={order.id}>
                        <td>
                          <code className="text-mono">#{order.id?.slice(0, 8)}</code>
                        </td>
                        <td className="font-semibold">
                          {formatCurrency(order.total_amount)}
                        </td>
                        <td>
                          <span className={`badge ${getStatusBadgeClass(order.status)}`}>
                            {order.status}
                          </span>
                        </td>
                        <td className="text-muted text-sm">
                          {formatDate(order.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
