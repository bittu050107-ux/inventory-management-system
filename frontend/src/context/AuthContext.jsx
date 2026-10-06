import React, { createContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  // Synchronize and verify session
  const checkAuth = useCallback(async () => {
    const savedToken = localStorage.getItem('token');
    if (!savedToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const data = await authService.getMe();
      // data might be { user_id, role, email }
      const currentUser = {
        ...user,
        user_id: data.user_id,
        role: data.role,
        email: data.email || (user ? user.email : ''),
      };
      setUser(currentUser);
      localStorage.setItem('user', JSON.stringify(currentUser));
    } catch {
      // If token expired or invalid
      logout();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    const accessToken = data.access_token;
    const role = data.role;
    const userData = { email, role, user_id: data.user_id || 'me' };

    localStorage.setItem('token', accessToken);
    localStorage.setItem('user', JSON.stringify(userData));

    setToken(accessToken);
    setUser(userData);
    return userData;
  };

  const register = async (userData) => {
    const data = await authService.register(userData);
    return data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  const hasRole = (roles) => {
    if (!user || !user.role) return false;
    if (Array.isArray(roles)) {
      return roles.includes(user.role.toUpperCase());
    }
    return user.role.toUpperCase() === roles.toUpperCase();
  };

  const value = {
    token,
    user,
    setUser,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    register,
    logout,
    hasRole,
    isAdmin: user?.role?.toUpperCase() === 'ADMIN',
    isManager: ['ADMIN', 'MANAGER'].includes(user?.role?.toUpperCase()),
    isStaff: ['ADMIN', 'MANAGER', 'STAFF'].includes(user?.role?.toUpperCase()),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
