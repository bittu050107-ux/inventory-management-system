import React from 'react';
import { NavLink } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import {
  LayoutDashboard,
  Package,
  Tags,
  Truck,
  Boxes,
  ShoppingCart,
  Users as UsersIcon,
  ShieldCheck,
} from 'lucide-react';

export const Sidebar = ({ isOpen, closeSidebar }) => {
  const { user, isAdmin, isStaff } = useAuth();

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/products', label: 'Products', icon: Package },
    { to: '/categories', label: 'Categories', icon: Tags },
    { to: '/suppliers', label: 'Suppliers', icon: Truck },
    { to: '/inventory', label: 'Inventory', icon: Boxes },
    { to: '/orders', label: 'Orders', icon: ShoppingCart },
    { to: '/profile', label: 'My Profile', icon: ShieldCheck },
  ];

  if (isAdmin) {
    navItems.push({ to: '/users', label: 'Users & Roles', icon: UsersIcon });
  }

  return (
    <>
      {isOpen && <div className="sidebar-backdrop" onClick={closeSidebar}></div>}
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-section-title">Navigation</div>
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
                }
                onClick={closeSidebar}
              >
                <Icon size={18} className="sidebar-link-icon" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-service-card">
            <div className="sidebar-service-header">
              <ShieldCheck size={14} className="text-accent" />
              <span>Gateway :8000</span>
            </div>
            <div className="service-pills">
              <span title="Auth :8001">Auth</span>
              <span title="Product :8003">Prod</span>
              <span title="Inventory :8004">Inv</span>
              <span title="Order :8005">Ord</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
