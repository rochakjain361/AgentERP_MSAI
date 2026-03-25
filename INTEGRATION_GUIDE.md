/**
 * INTEGRATION GUIDE - How to Add RBAC Components to DashboardView
 * 
 * This file shows the exact code needed to integrate the new components
 * into your existing DashboardView.js
 */

// ============== STEP 1: ADD IMPORTS ==============
// Add these lines to the top of DashboardView.js:

import RoleSwitcher from './RoleSwitcher';
import SalesOrderList from './SalesOrderList';
import AuditLogPanel from './AuditLogPanel';
import { useAuth } from '../contexts/AuthContext';


// ============== STEP 2: GET USER DATA ==============
// Inside the DashboardView component, add this hook:

const DashboardView = () => {
  const { user, login, logout } = useAuth();

  const handleRoleSwitch = async (email, password) => {
    const result = await login(email, password);
    if (!result.success) {
      alert(`Failed to switch role: ${result.error}`);
    }
  };

  const handleLogout = () => {
    logout();
    // Navigate to login screen if needed
  };

  // ... rest of component


// ============== STEP 3: ADD TO JSX ==============
// Add to your JSX return statement:

return (
  <div>
    {/* Header with Role Switcher */}
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400">Management & Approvals</p>
      </div>
      
      {/* Role Switcher in Top Right */}
      {user && (
        <RoleSwitcher 
          currentUser={user}
          onRoleSwitch={handleRoleSwitch}
          onLogout={handleLogout}
        />
      )}
    </div>

    {/* Main Content Grid */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Left Column: Approvals (for managers) */}
      <div>
        <SalesOrderList user={user} />
      </div>

      {/* Right Column: Audit Logs (for all) */}
      <div>
        <AuditLogPanel user={user} />
      </div>
    </div>

    {/* Additional KPI cards below */}
    <div className="mt-6">
      {/* Your existing KPI cards here */}
    </div>
  </div>
);


// ============== ALTERNATIVE: FULL EXAMPLE ==============
// Here's a complete simplified DashboardView with RBAC:

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import RoleSwitcher from './RoleSwitcher';
import SalesOrderList from './SalesOrderList';
import AuditLogPanel from './AuditLogPanel';

const DashboardViewWithRBAC = () => {
  const { user, login, logout } = useAuth();

  const handleRoleSwitch = async (email, password) => {
    const result = await login(email, password);
    if (!result.success) {
      alert(`Failed to switch role: ${result.error}`);
    }
  };

  if (!user) {
    return <div>Please log in first</div>;
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-white">AgentERP Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Role: <span className="text-white font-semibold capitalize">{user.role}</span>
            {user.company && ` • Company: ${user.company}`}
          </p>
        </div>
        <RoleSwitcher 
          currentUser={user}
          onRoleSwitch={handleRoleSwitch}
          onLogout={logout}
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Orders / Approvals Panel */}
        <SalesOrderList user={user} />

        {/* Audit Log Panel */}
        <AuditLogPanel user={user} />
      </div>

      {/* Additional Info */}
      <div className="mt-6 p-4 bg-slate-800 border border-slate-700 rounded-lg">
        <h3 className="text-white font-semibold mb-2">📋 Your Permissions</h3>
        <ul className="text-sm text-slate-400 space-y-1">
          {user.role === 'admin' && (
            <>
              <li>✓ Full system access</li>
              <li>✓ Manage all users</li>
              <li>✓ View all companies</li>
            </>
          )}
          {user.role === 'manager' && (
            <>
              <li>✓ Review & approve orders > ₹50K</li>
              <li>✓ View company data</li>
              <li>✓ See audit logs</li>
            </>
          )}
          {user.role === 'operator' && (
            <>
              <li>✓ Create orders</li>
              <li>✓ View own data</li>
              <li>✓ See own audit logs</li>
            </>
          )}
          {user.role === 'viewer' && (
            <>
              <li>✓ View-only access</li>
              <li>✓ See all orders</li>
              <li>✓ See audit logs</li>
            </>
          )}
        </ul>
      </div>
    </div>
  );
};

export default DashboardViewWithRBAC;


// ============== CONDITIONAL RENDERING ==============
// If you want to show different content based on role:

{user?.role === 'manager' && (
  <SalesOrderList user={user} />
)}

{user?.role !== 'viewer' && (
  <CreateOrderButton />
)}

{(user?.role === 'admin' || user?.role === 'manager') && (
  <AuditLogPanel user={user} />
)}


// ============== API USAGE EXAMPLES ==============
// If you need to call APIs directly in your component:

// Get pending approvals
const getApprovals = async () => {
  try {
    const result = await approvalsApi.getPending();
    console.log('Pending approvals:', result.data);
  } catch (error) {
    console.error('Failed to get approvals:', error);
  }
};

// Get audit logs
const getAuditLogs = async () => {
  try {
    const result = await auditApi.getLogs(50, 0, { action: 'create_order' });
    console.log('Audit logs:', result.data);
  } catch (error) {
    console.error('Failed to get logs:', error);
  }
};

// Approve an order
const approveOrder = async (approvalId) => {
  try {
    const result = await approvalsApi.approve(
      approvalId, 
      'Order approved - meets all criteria'
    );
    console.log('Approval successful:', result.data);
  } catch (error) {
    console.error('Failed to approve:', error);
  }
};


// ============== STYLING NOTES ==============
/*
All components use Tailwind CSS with these color schemes:

RoleSwitcher: 
  - Admin: Purple gradient (from-red-500 to-pink-500)
  - Manager: Blue gradient (from-blue-500 to-cyan-500)
  - Operator: Green gradient (from-green-500 to-emerald-500)
  - Viewer: Gray gradient (from-gray-500 to-slate-500)

SalesOrderList:
  - Background: bg-slate-800
  - Borders: border-slate-700
  - Highlights: blue-500, green-500, yellow-500

AuditLogPanel:
  - Background: bg-slate-800
  - Text: text-slate-400 (muted), text-white (prominent)
  - Filters: text-xs font-medium

All use dark theme (slate-900 background, slate-800 panels)
*/
