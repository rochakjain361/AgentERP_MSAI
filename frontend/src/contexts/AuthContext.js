/**
 * Authentication Context - Manages user authentication state
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../lib/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('agenterp_token');
      const savedUser = localStorage.getItem('agenterp_user');
      
      if (token && savedUser) {
        try {
          // Verify token is still valid
          const response = await authApi.verify();
          if (response.data.valid) {
            setUser(response.data.user);
          } else {
            // Token invalid, clear storage
            localStorage.removeItem('agenterp_token');
            localStorage.removeItem('agenterp_user');
          }
        } catch (err) {
          // Token expired or invalid
          localStorage.removeItem('agenterp_token');
          localStorage.removeItem('agenterp_user');
        }
      }
      setLoading(false);
    };

    checkAuth();

    // Listen for logout events
    const handleLogout = () => {
      setUser(null);
      localStorage.removeItem('agenterp_token');
      localStorage.removeItem('agenterp_user');
    };
    window.addEventListener('auth:logout', handleLogout);
    return () => window.removeEventListener('auth:logout', handleLogout);
  }, []);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const response = await authApi.login(email, password);
      if (response.data.status === 'success') {
        const { access_token, user: userData } = response.data;
        localStorage.setItem('agenterp_token', access_token);
        localStorage.setItem('agenterp_user', JSON.stringify(userData));
        setUser(userData);
        return { success: true };
      }
      return { success: false, error: response.data.message };
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      return { success: false, error: message };
    }
  }, []);

  const register = useCallback(async (email, password, name, role = 'operator', company = null) => {
    setError(null);
    try {
      const response = await authApi.register(email, password, name, role, company);
      if (response.data.status === 'success') {
        const { access_token, user: userData } = response.data;
        localStorage.setItem('agenterp_token', access_token);
        localStorage.setItem('agenterp_user', JSON.stringify(userData));
        setUser(userData);
        return { success: true };
      }
      return { success: false, error: response.data.message };
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      return { success: false, error: message };
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('agenterp_token');
    localStorage.removeItem('agenterp_user');
  }, []);

  const isManager = user?.role === 'manager' || user?.role === 'admin';
  const isAdmin = user?.role === 'admin';
  const canCreate = user?.role !== 'viewer';
  const canApprove = isManager;

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isManager,
    isAdmin,
    canCreate,
    canApprove,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
