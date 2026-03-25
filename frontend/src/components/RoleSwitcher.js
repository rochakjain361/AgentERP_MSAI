/**
 * Role Switcher Component - Switch between demo user roles
 */
import React, { useState } from 'react';
import { Shield, LogOut, User, CheckCircle } from 'lucide-react';

const RoleSwitcher = ({ currentUser, onRoleSwitch, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);

  const demoUsers = [
    { email: 'admin@agenterp.com', password: 'admin123', name: 'Admin', role: 'admin' },
    { email: 'manager@agenterp.com', password: 'manager123', name: 'Manager', role: 'manager' },
    { email: 'operator@agenterp.com', password: 'operator123', name: 'Operator', role: 'operator' },
    { email: 'viewer@agenterp.com', password: 'viewer123', name: 'Viewer', role: 'viewer' },
  ];

  const roleColors = {
    admin: 'from-red-500 to-pink-500',
    manager: 'from-blue-500 to-cyan-500',
    operator: 'from-green-500 to-emerald-500',
    viewer: 'from-gray-500 to-slate-500',
  };

  const roleDescriptions = {
    admin: 'Full control, manage users',
    manager: 'Approve orders, manage approvals',
    operator: 'Create orders, view data',
    viewer: 'Read-only access',
  };

  if (!currentUser) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r ${roleColors[currentUser.role]} text-white text-sm font-medium hover:opacity-90 transition-all`}
      >
        <Shield className="w-4 h-4" />
        <span className="capitalize">{currentUser.role}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
          <div className="p-4 border-b border-slate-700">
            <div className="text-xs text-slate-400 font-semibold">DEMO USER</div>
            <div className="mt-1 flex items-center gap-2">
              <User className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-white font-medium">{currentUser.name}</span>
            </div>
            <div className="text-xs text-slate-500 mt-1">{currentUser.email}</div>
            <div className="text-xs text-slate-400 mt-1">{roleDescriptions[currentUser.role]}</div>
          </div>

          <div className="p-3 space-y-2 max-h-64 overflow-y-auto">
            <div className="text-xs text-slate-400 font-semibold px-1">SWITCH ROLE</div>
            {demoUsers.map((user) => (
              <button
                key={user.email}
                onClick={() => {
                  onRoleSwitch(user.email, user.password);
                  setIsOpen(false);
                }}
                className={`w-full flex items-start gap-3 p-2 rounded-lg transition-colors ${
                  currentUser.email === user.email
                    ? 'bg-slate-700 border border-slate-600'
                    : 'bg-slate-700/50 hover:bg-slate-700 border border-slate-700'
                }`}
              >
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${roleColors[user.role]} flex items-center justify-center flex-shrink-0 mt-1`}>
                  {currentUser.email === user.email ? (
                    <CheckCircle className="w-4 h-4 text-white" />
                  ) : (
                    <Shield className="w-3 h-3 text-white/70" />
                  )}
                </div>
                <div className="text-left flex-1 min-w-0">
                  <div className="text-sm font-medium text-white">{user.name}</div>
                  <div className="text-xs text-slate-400 capitalize">{user.role}</div>
                </div>
              </button>
            ))}
          </div>

          <div className="p-3 border-t border-slate-700">
            <button
              onClick={() => {
                onLogout();
                setIsOpen(false);
              }}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 hover:bg-red-500/20 transition-colors text-sm font-medium"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleSwitcher;
