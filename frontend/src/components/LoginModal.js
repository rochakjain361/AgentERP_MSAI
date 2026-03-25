/**
 * Login Modal Component with Company Selection
 */
import React, { useState } from 'react';
import { X, LogIn, UserPlus, Eye, EyeOff, Shield, AlertCircle, Building2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LoginModal = ({ isOpen, onClose }) => {
  const { login, register, error } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'operator',
    company: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setFormError('');

    let result;
    if (isRegister) {
      result = await register(formData.email, formData.password, formData.name, formData.role, formData.company || null);
    } else {
      result = await login(formData.email, formData.password);
    }

    setLoading(false);
    
    if (result.success) {
      onClose();
    } else {
      setFormError(result.error);
    }
  };

  const quickLogin = async (email, password) => {
    setLoading(true);
    setFormError('');
    const result = await login(email, password);
    setLoading(false);
    if (result.success) {
      onClose();
    } else {
      setFormError(result.error);
    }
  };

  // Demo users with company associations
  const demoUsers = [
    { 
      email: 'admin@agenterp.com', 
      password: 'admin123', 
      label: 'Admin', 
      sublabel: 'Full System Access',
      color: 'purple'
    },
    { 
      email: 'manager@agenterp.com', 
      password: 'manager123', 
      label: 'Manager', 
      sublabel: 'Approvals & Reviews',
      color: 'blue'
    },
    { 
      email: 'operator@agenterp.com', 
      password: 'operator123', 
      label: 'Operator', 
      sublabel: 'Create Orders',
      color: 'green'
    },
    { 
      email: 'viewer@agenterp.com', 
      password: 'viewer123', 
      label: 'Viewer', 
      sublabel: 'Read-Only Access',
      color: 'slate'
    },
  ];

  const colorStyles = {
    purple: {
      bg: 'from-purple-500/20 to-violet-500/20',
      border: 'border-purple-500/30 hover:border-purple-500/50',
      icon: 'from-purple-500 to-violet-500',
      text: 'text-purple-200'
    },
    blue: {
      bg: 'from-blue-500/20 to-cyan-500/20',
      border: 'border-blue-500/30 hover:border-blue-500/50',
      icon: 'from-blue-500 to-cyan-500',
      text: 'text-blue-200'
    },
    green: {
      bg: 'from-emerald-500/20 to-green-500/20',
      border: 'border-emerald-500/30 hover:border-emerald-500/50',
      icon: 'from-emerald-500 to-green-500',
      text: 'text-emerald-200'
    },
    slate: {
      bg: 'from-slate-500/20 to-slate-600/20',
      border: 'border-slate-500/30 hover:border-slate-500/50',
      icon: 'from-slate-400 to-slate-500',
      text: 'text-slate-200'
    },
  };

  const roleIcons = {
    Admin: Shield,
    Manager: UserPlus,
    Operator: UserPlus,
    Viewer: Eye,
  };

  const roleDescriptions = {
    viewer: 'Level 3: View-only access',
    operator: 'Level 2: Create & View',
    manager: 'Level 2: Create, View + Approve',
    admin: 'Level 1: Full Control'
  };

  // Sample companies from ERPNext for demo
  const sampleCompanies = [
    "TechCorp Solutions",
    "InnovateTech Pvt Ltd",
    "Global Industries Ltd",
    "IIM Bangalore",
    "ACME Corp Ltd."
  ];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-md mx-4 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700 sticky top-0 bg-slate-900">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">
                {isRegister ? 'Create Account' : 'Welcome Back'}
              </h2>
              <p className="text-xs text-slate-400">
                {isRegister ? 'Join AgentERP Enterprise' : 'Sign in to your company'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Quick Login Section */}
        {!isRegister && (
          <div className="p-4 border-b border-slate-700 bg-slate-800/30">
            <p className="text-xs text-slate-400 mb-3 font-medium">Quick login as demo user:</p>
            <div className="grid grid-cols-2 gap-3">
              {demoUsers.map((user) => {
                const styles = colorStyles[user.color];
                const IconComponent = roleIcons[user.label] || Shield;
                return (
                  <button
                    key={user.email}
                    onClick={() => quickLogin(user.email, user.password)}
                    disabled={loading}
                    className={`group relative p-3 rounded-xl bg-gradient-to-br ${styles.bg} border ${styles.border} transition-all duration-200 hover:scale-[1.02] disabled:opacity-50`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${styles.icon} flex items-center justify-center shadow-lg flex-shrink-0`}>
                        <IconComponent className="w-4 h-4 text-white" />
                      </div>
                      <div className="text-left min-w-0">
                        <div className={`font-semibold text-sm ${styles.text}`}>{user.label}</div>
                        <div className="text-[11px] text-slate-400 truncate">{user.sublabel}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
            <div className="mt-3 flex items-center justify-center gap-2 text-[11px] text-slate-500">
              <Building2 className="w-3 h-3" />
              <span>Each user sees only their company's data</span>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {formError && (
            <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              <AlertCircle className="w-4 h-4 shrink-0" />
              {formError}
            </div>
          )}

          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your name"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-10"
                placeholder="Enter your password"
                required
                minLength={6}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {isRegister && (
            <>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Role (Access Level)
                </label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="viewer">Viewer</option>
                  <option value="operator">Operator</option>
                  <option value="manager">Manager</option>
                </select>
                <p className="mt-1 text-xs text-slate-400">
                  {roleDescriptions[formData.role]}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  <Building2 className="w-4 h-4 inline mr-1" />
                  Company / Customer
                </label>
                <select
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                  className="w-full px-3 py-2.5 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Companies (Admin only)</option>
                  {sampleCompanies.map((company) => (
                    <option key={company} value={company}>{company}</option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-slate-400">
                  You will only see data for this company
                </p>
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                {isRegister ? <UserPlus className="w-4 h-4" /> : <LogIn className="w-4 h-4" />}
                {isRegister ? 'Create Account' : 'Sign In'}
              </>
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700 text-center">
          <button
            onClick={() => {
              setIsRegister(!isRegister);
              setFormError('');
            }}
            className="text-sm text-blue-400 hover:text-blue-300"
          >
            {isRegister ? 'Already have an account? Sign in' : "Don't have an account? Register"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
