/**
 * ERP Widgets - Components for displaying ERP data
 */
import React, { useState } from 'react';
import { ExternalLink, Zap, Loader2 } from 'lucide-react';
import { ERP_BASE_URL, STATUS_COLORS } from '../lib/constants';
import { DashboardView } from './DashboardView';
import { AIRiskResultsWidget, AIRiskLoadingWidget, AIRiskErrorWidget } from './AIRiskWidget';
import { aiAnalysisApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

// Status Badge Component
export const StatusBadge = ({ status }) => {
  const colorClass = STATUS_COLORS[status] || 'bg-gray-100 text-gray-800';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
      {status}
    </span>
  );
};

// Sales Order Widget
const SalesOrderWidget = ({ data }) => (
  <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <h4 className="font-semibold flex items-center gap-2">
        <span className="text-green-500">✓</span>
        Sales Order Created
      </h4>
      <a 
        href={`${ERP_BASE_URL}/app/sales-order/${data.name}`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1 text-xs text-primary hover:underline"
      >
        View in ERP <ExternalLink className="w-3 h-3" />
      </a>
    </div>
    <div className="grid grid-cols-2 gap-3 text-sm">
      <div>
        <span className="text-muted-foreground">Order ID:</span>
        <span className="ml-2 font-mono">{data.name}</span>
      </div>
      <div>
        <span className="text-muted-foreground">Customer:</span>
        <a 
          href={`${ERP_BASE_URL}/app/customer/${data.customer}`}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 text-primary hover:underline"
        >
          {data.customer}
        </a>
      </div>
      <div>
        <span className="text-muted-foreground">Date:</span>
        <span className="ml-2">{data.transaction_date}</span>
      </div>
      <div>
        <span className="text-muted-foreground">Status:</span>
        <StatusBadge status={data.status} />
      </div>
      {data.grand_total && (
        <div>
          <span className="text-muted-foreground">Total:</span>
          <span className="ml-2 font-semibold">₹{parseFloat(data.grand_total).toLocaleString()}</span>
        </div>
      )}
    </div>
    {data.items && data.items.length > 0 && (
      <div className="mt-3 pt-3 border-t border-border">
        <span className="text-sm text-muted-foreground">Items:</span>
        <div className="mt-2 space-y-1">
          {data.items.map((item, idx) => (
            <div key={idx} className="flex justify-between text-sm">
              <a 
                href={`${ERP_BASE_URL}/app/item/${item.item_code}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                {item.item_code}
              </a>
              <span>Qty: {item.qty}</span>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

// Customer Widget
const CustomerWidget = ({ data }) => (
  <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <h4 className="font-semibold flex items-center gap-2">
        <span className="text-blue-500">👤</span>
        Customer Details
      </h4>
      <a 
        href={`${ERP_BASE_URL}/app/customer/${data.name}`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1 text-xs text-primary hover:underline"
      >
        View in ERP <ExternalLink className="w-3 h-3" />
      </a>
    </div>
    <div className="grid grid-cols-2 gap-3 text-sm">
      <div>
        <span className="text-muted-foreground">Name:</span>
        <span className="ml-2 font-medium">{data.customer_name || data.name}</span>
      </div>
      <div>
        <span className="text-muted-foreground">Type:</span>
        <span className="ml-2">{data.customer_type}</span>
      </div>
      <div>
        <span className="text-muted-foreground">Territory:</span>
        <span className="ml-2">{data.territory || 'Not Set'}</span>
      </div>
    </div>
  </div>
);

// Sales Orders List Widget with AI Analysis capability
const SalesOrdersListWidget = ({ orders, showAnalysisButton = true }) => {
  const { user, isManager } = useAuth();
  const [analysisState, setAnalysisState] = useState({ loading: false, data: null, error: null });
  
  const canRunAnalysis = user && isManager && showAnalysisButton;
  
  const handleRunAnalysis = async () => {
    setAnalysisState({ loading: true, data: null, error: null });
    try {
      const response = await aiAnalysisApi.analyzeOrders();
      if (response.data.status === 'success') {
        setAnalysisState({ loading: false, data: response.data, error: null });
      } else {
        setAnalysisState({ loading: false, data: null, error: response.data.message || 'Analysis failed' });
      }
    } catch (err) {
      const errorMsg = err.response?.status === 403 
        ? 'Access denied. AI Analysis requires Admin or Manager role.'
        : (err.response?.data?.detail || 'Failed to run analysis');
      setAnalysisState({ loading: false, data: null, error: errorMsg });
    }
  };
  
  return (
    <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold">Recent Sales Orders</h4>
        <div className="flex items-center gap-2">
          {/* AI Analysis Button - Only for Admin/Manager */}
          {canRunAnalysis && !analysisState.data && (
            <button
              onClick={handleRunAnalysis}
              disabled={analysisState.loading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 text-white text-xs font-medium rounded-lg hover:bg-amber-600 transition-colors disabled:opacity-50"
              data-testid="run-ai-analysis-btn"
            >
              {analysisState.loading ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Zap className="w-3 h-3" />
              )}
              Run AI Analysis
            </button>
          )}
          <a 
            href={`${ERP_BASE_URL}/app/sales-order`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-primary hover:underline"
          >
            View All <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 font-medium text-muted-foreground">Order</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Customer</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Date</th>
              <th className="text-right py-2 font-medium text-muted-foreground">Amount</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, idx) => (
              <tr key={idx} className="border-b border-border/50">
                <td className="py-2">
                  <a 
                    href={`${ERP_BASE_URL}/app/sales-order/${order.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-mono text-xs"
                  >
                    {order.name}
                  </a>
                </td>
                <td className="py-2">
                  <a 
                    href={`${ERP_BASE_URL}/app/customer/${order.customer}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:text-primary"
                  >
                    {order.customer}
                  </a>
                </td>
                <td className="py-2 text-muted-foreground">{order.transaction_date}</td>
                <td className="py-2 text-right font-medium">₹{parseFloat(order.grand_total || 0).toLocaleString()}</td>
                <td className="py-2"><StatusBadge status={order.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* AI Analysis Results - Inline in chat */}
      {analysisState.loading && <AIRiskLoadingWidget />}
      {analysisState.error && (
        <AIRiskErrorWidget 
          error={analysisState.error} 
          onRetry={handleRunAnalysis} 
        />
      )}
      {analysisState.data && <AIRiskResultsWidget data={analysisState.data} />}
    </div>
  );
};

// Invoices List Widget with AI Analysis capability
const InvoicesListWidget = ({ invoices, showAnalysisButton = true }) => {
  const { user, isManager } = useAuth();
  const [analysisState, setAnalysisState] = useState({ loading: false, data: null, error: null });
  
  const canRunAnalysis = user && isManager && showAnalysisButton;
  
  const handleRunAnalysis = async () => {
    setAnalysisState({ loading: true, data: null, error: null });
    try {
      const response = await aiAnalysisApi.analyzeOrders();
      if (response.data.status === 'success') {
        setAnalysisState({ loading: false, data: response.data, error: null });
      } else {
        setAnalysisState({ loading: false, data: null, error: response.data.message || 'Analysis failed' });
      }
    } catch (err) {
      const errorMsg = err.response?.status === 403 
        ? 'Access denied. AI Analysis requires Admin or Manager role.'
        : (err.response?.data?.detail || 'Failed to run analysis');
      setAnalysisState({ loading: false, data: null, error: errorMsg });
    }
  };
  
  return (
    <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold">Recent Invoices</h4>
        <div className="flex items-center gap-2">
          {/* AI Analysis Button - Only for Admin/Manager */}
          {canRunAnalysis && !analysisState.data && (
            <button
              onClick={handleRunAnalysis}
              disabled={analysisState.loading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-500 text-white text-xs font-medium rounded-lg hover:bg-amber-600 transition-colors disabled:opacity-50"
              data-testid="run-ai-analysis-invoices-btn"
            >
              {analysisState.loading ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Zap className="w-3 h-3" />
              )}
              Run AI Analysis
            </button>
          )}
          <a 
            href={`${ERP_BASE_URL}/app/sales-invoice`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-primary hover:underline"
          >
            View All <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2 font-medium text-muted-foreground">Invoice</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Customer</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Date</th>
              <th className="text-right py-2 font-medium text-muted-foreground">Amount</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice, idx) => (
              <tr key={idx} className="border-b border-border/50">
                <td className="py-2">
                  <a 
                    href={`${ERP_BASE_URL}/app/sales-invoice/${invoice.name}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline font-mono text-xs"
                  >
                    {invoice.name}
                  </a>
                </td>
                <td className="py-2">{invoice.customer}</td>
                <td className="py-2 text-muted-foreground">{invoice.posting_date}</td>
                <td className="py-2 text-right font-medium">₹{parseFloat(invoice.grand_total || 0).toLocaleString()}</td>
                <td className="py-2"><StatusBadge status={invoice.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* AI Analysis Results - Inline */}
      {analysisState.loading && <AIRiskLoadingWidget />}
      {analysisState.error && (
        <AIRiskErrorWidget 
          error={analysisState.error} 
          onRetry={handleRunAnalysis} 
        />
      )}
      {analysisState.data && <AIRiskResultsWidget data={analysisState.data} />}
    </div>
  );
};

// Customers List Widget
const CustomersListWidget = ({ customers }) => (
  <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <h4 className="font-semibold">Customers</h4>
      <a 
        href={`${ERP_BASE_URL}/app/customer`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1 text-xs text-primary hover:underline"
      >
        View All <ExternalLink className="w-3 h-3" />
      </a>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left py-2 font-medium text-muted-foreground">Name</th>
            <th className="text-left py-2 font-medium text-muted-foreground">Type</th>
            <th className="text-left py-2 font-medium text-muted-foreground">Territory</th>
          </tr>
        </thead>
        <tbody>
          {customers.map((customer, idx) => (
            <tr key={idx} className="border-b border-border/50">
              <td className="py-2">
                <a 
                  href={`${ERP_BASE_URL}/app/customer/${customer.name}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {customer.customer_name || customer.name}
                </a>
              </td>
              <td className="py-2 text-muted-foreground">{customer.customer_type}</td>
              <td className="py-2 text-muted-foreground">{customer.territory || 'Not Set'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// Dashboard Widget
const DashboardWidget = ({ data }) => (
  <div className="bg-card border border-border rounded-xl p-4 mt-3 shadow-sm">
    <div className="flex items-center justify-between mb-3">
      <h4 className="font-semibold">ERP Dashboard</h4>
      <a 
        href={`${ERP_BASE_URL}/app/home`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1 text-xs text-primary hover:underline"
      >
        Open ERP <ExternalLink className="w-3 h-3" />
      </a>
    </div>
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="p-3 rounded-lg bg-blue-50">
        <div className="text-2xl font-bold text-blue-600">{data.total_customers || 0}</div>
        <div className="text-xs text-muted-foreground">Customers</div>
      </div>
      <div className="p-3 rounded-lg bg-green-50">
        <div className="text-2xl font-bold text-green-600">{data.total_sales_orders || 0}</div>
        <div className="text-xs text-muted-foreground">Sales Orders</div>
      </div>
      <div className="p-3 rounded-lg bg-purple-50">
        <div className="text-2xl font-bold text-purple-600">{data.total_invoices || 0}</div>
        <div className="text-xs text-muted-foreground">Invoices</div>
      </div>
      <div className="p-3 rounded-lg bg-amber-50">
        <div className="text-2xl font-bold text-amber-600">{data.total_items || 0}</div>
        <div className="text-xs text-muted-foreground">Items</div>
      </div>
    </div>
  </div>
);

// Main ERPWidget Component
export const ERPWidget = ({ data }) => {
  if (!data) return null;

  // Comprehensive Analytics Dashboard
  if (data.type === 'comprehensive_analytics') {
    return <DashboardView data={data} />;
  }

  if (data.type === 'sales_order') {
    return <SalesOrderWidget data={data} />;
  }

  if (data.type === 'customer') {
    return <CustomerWidget data={data} />;
  }

  if (data.type === 'sales_orders_list' && data.orders) {
    return <SalesOrdersListWidget orders={data.orders} />;
  }

  if (data.type === 'invoices_list' && data.invoices) {
    return <InvoicesListWidget invoices={data.invoices} />;
  }

  if (data.type === 'customers_list' && data.customers) {
    return <CustomersListWidget customers={data.customers} />;
  }

  if (data.type === 'dashboard') {
    return <DashboardWidget data={data} />;
  }

  return null;
};

export default ERPWidget;
