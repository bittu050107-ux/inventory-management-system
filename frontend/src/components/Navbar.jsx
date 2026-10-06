import React from 'react';
import { useNavigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import { getRoleBadgeClass } from '../utils/helpers';
import { LogOut, User, Bell, Menu, Shield } from 'lucide-react';

export const Navbar = ({ toggleSidebar }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar">
      <div className="navbar-left">
        <button className="btn-icon mobile-menu-btn" onClick={toggleSidebar} aria-label="Toggle menu">
          <Menu size={20} />
        </button>
        <div className="navbar-brand">
          <div className="brand-logo-icon">📦</div>
          <span className="brand-title">InventoryHub</span>
          <span className="badge badge-subtle">Microservices</span>
        </div>
      </div>

      <div className="navbar-right">
        <div className="status-indicator">
          <span className="status-dot online"></span>
          <span className="status-text">Gateway Online</span>
        </div>

        {user && (
          <div className="user-profile-menu">
            <div
              className="flex items-center gap-2 cursor-pointer"
              style={{ cursor: 'pointer' }}
              onClick={() => navigate('/profile')}
              title="View & Edit Profile"
            >
              <div className="user-avatar">
                <User size={18} />
              </div>
              <div className="user-info">
                <span className="user-email">{user.email || 'User'}</span>
                <span className={`badge ${getRoleBadgeClass(user.role)}`}>
                  <Shield size={10} style={{ marginRight: '3px' }} />
                  {user.role || 'USER'}
                </span>
              </div>
            </div>
            <button className="btn-icon logout-btn" onClick={handleLogout} title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
