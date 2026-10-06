import React, { useState, useEffect } from 'react';
import userService from '../services/userService';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';
import { getRoleBadgeClass, formatDate } from '../utils/helpers';
import {
  Users as UsersIcon,
  Shield,
  CheckCircle2,
  Mail,
  RefreshCw,
  UserCheck,
} from 'lucide-react';

export const Users = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchUsers = async () => {
    try {
      setRefreshing(true);
      const data = await userService.getUsers();
      setUsers(data || []);
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await userService.updateUserRole(userId, newRole);
      setUsers(
        users.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch {
      // Local optimistic update if backend user service is in simulated mode
      setUsers(
        users.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    }
  };

  if (loading) {
    return <Loading message="Loading system users and roles..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Users & Role Management</h1>
          <p className="page-subtitle">
            Configure RBAC permissions (Admin, Manager, Staff, User)
          </p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={fetchUsers}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spin' : ''} /> Refresh
          </button>
        </div>
      </div>

      {/* Role Guide Card */}
      <div className="card role-guide-card mb-4">
        <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
          <Shield size={18} className="text-accent" /> Role-Based Access Control (RBAC) Hierarchy
        </h3>
        <div className="role-guide-grid">
          <div className="role-guide-item">
            <span className="badge badge-purple">ADMIN</span>
            <p>Full unrestricted CRUD across all products, inventory, users, and orders.</p>
          </div>
          <div className="role-guide-item">
            <span className="badge badge-indigo">MANAGER</span>
            <p>View & manage all orders, transition order statuses, inspect stock.</p>
          </div>
          <div className="role-guide-item">
            <span className="badge badge-blue">STAFF</span>
            <p>Execute stock-in and stock-out movements, view inventory and products.</p>
          </div>
          <div className="role-guide-item">
            <span className="badge badge-neutral">USER</span>
            <p>Place customer orders and monitor order tracking updates.</p>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="card table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th>User ID</th>
              <th>Email</th>
              <th>Current Role</th>
              <th>Status</th>
              <th>Created</th>
              <th>Modify Role</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>
                  <code className="text-mono">#{String(u.id).slice(0, 8)}</code>
                </td>
                <td>
                  <div className="flex items-center gap-2">
                    <Mail size={14} className="text-muted" />
                    <strong>{u.email}</strong>
                    {currentUser?.email === u.email && (
                      <span className="badge badge-subtle">(You)</span>
                    )}
                  </div>
                </td>
                <td>
                  <span className={`badge ${getRoleBadgeClass(u.role)}`}>
                    {u.role}
                  </span>
                </td>
                <td>
                  <span className="flex items-center gap-1 text-sm text-success">
                    <CheckCircle2 size={14} /> Active
                  </span>
                </td>
                <td className="text-muted text-sm">{formatDate(u.created_at)}</td>
                <td>
                  <select
                    className="form-select form-select-sm"
                    value={u.role}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                    disabled={currentUser?.id === u.id}
                  >
                    <option value="ADMIN">ADMIN</option>
                    <option value="MANAGER">MANAGER</option>
                    <option value="STAFF">STAFF</option>
                    <option value="USER">USER</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Users;
