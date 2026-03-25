/**
 * Application constants
 */

// ERPNext base URL for direct links
export const ERP_BASE_URL = 'https://india-next.m.frappe.cloud';

// Quick action commands
export const QUICK_ACTIONS = [
  { icon: '📊', text: 'Dashboard Statistics', action: 'Show me the dashboard statistics' },
  { icon: '➕', text: 'Create New Order', action: 'Create a sales order for Grant Plastics Ltd for 2 units of SKU001' },
  { icon: '📋', text: 'List Sales Orders', action: 'List all recent sales orders' },
  { icon: '👥', text: 'View Customers', action: 'Show me all customers in the system' },
  { icon: '💰', text: 'Show Invoices', action: 'Show me all invoices' },
  { icon: '📈', text: 'Sales Report', action: 'Show me sales analytics for the last month' },
];

// ERPNext direct links
export const ERP_LINKS = [
  { icon: '🏠', text: 'ERP Home', path: '/app/home' },
  { icon: '📋', text: 'Sales Orders', path: '/app/sales-order' },
  { icon: '👥', text: 'Customers', path: '/app/customer' },
  { icon: '💰', text: 'Invoices', path: '/app/sales-invoice' },
  { icon: '📦', text: 'Items', path: '/app/item' },
  { icon: '📊', text: 'Reports', path: '/app/report' },
];

// Sidebar quick actions
export const SIDEBAR_ACTIONS = {
  quickActions: [
    { label: '+ New Order', prompt: 'Create a sales order for Grant Plastics Ltd for 2 units of SKU001' },
    { label: 'Sales Orders', prompt: 'List all recent sales orders' },
    { label: 'Customers', prompt: 'Show me all customers in the system' },
    { label: 'Invoices', prompt: 'Show me all invoices' },
  ],
  analytics: [
    { label: 'Sales Report', prompt: 'Show me sales analytics for the last month' },
    { label: 'Top Customers', prompt: 'Which customers have the most orders?' },
    { label: 'Overdue Payments', prompt: 'Show me all overdue invoices' },
  ],
};

// Status badge colors
export const STATUS_COLORS = {
  'Draft': 'bg-yellow-100 text-yellow-800',
  'To Deliver and Bill': 'bg-blue-100 text-blue-800',
  'To Bill': 'bg-purple-100 text-purple-800',
  'To Deliver': 'bg-cyan-100 text-cyan-800',
  'Completed': 'bg-green-100 text-green-800',
  'Cancelled': 'bg-red-100 text-red-800',
  'Closed': 'bg-gray-100 text-gray-800',
  'Paid': 'bg-green-100 text-green-800',
  'Unpaid': 'bg-red-100 text-red-800',
  'Overdue': 'bg-orange-100 text-orange-800',
  'Partly Paid': 'bg-amber-100 text-amber-800',
};
