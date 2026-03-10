import React from 'react';
import { TrendingUp, Users, FileText, AlertCircle } from 'lucide-react';
import { ERP_BASE_URL } from '../lib/constants';

const KPICard = ({ title, value, subtitle, icon: Icon, color, link }) => (
  <a
    href={link}
    target="_blank"
    rel="noopener noreferrer"
    className="bg-card text-card-foreground rounded-xl border border-border p-4 hover:shadow-lg transition-all hover:border-primary/30 block"
    data-testid={`kpi-${title.toLowerCase().replace(/\s+/g, '-')}`}
  >
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">{title}</p>
        <p className={`text-2xl font-bold mt-1 ${color || 'text-foreground'}`}>{value}</p>
        {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
      </div>
      <div className={`p-2 rounded-lg ${color ? `bg-${color.replace('text-', '')}/10` : 'bg-primary/10'}`}>
        <Icon className={`w-5 h-5 ${color || 'text-primary'}`} />
      </div>
    </div>
  </a>
);

const DataTable = ({ title, columns, data, emptyMessage, linkPrefix }) => (
  <div className="bg-card text-card-foreground rounded-xl border border-border overflow-hidden" data-testid={`table-${title.toLowerCase().replace(/\s+/g, '-')}`}>
    <div className="px-4 py-3 border-b border-border bg-muted/30">
      <h3 className="font-semibold text-sm" style={{ fontFamily: 'Manrope, sans-serif' }}>{title}</h3>
    </div>
    <div className="overflow-x-auto">
      {data && data.length > 0 ? (
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/20">
              {columns.map((col, idx) => (
                <th key={idx} className={`px-4 py-2 text-xs font-semibold text-muted-foreground text-left ${col.align || ''}`}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIdx) => (
              <tr key={rowIdx} className="border-b border-border/50 hover:bg-muted/20 transition-colors">
                {columns.map((col, colIdx) => (
                  <td key={colIdx} className={`px-4 py-3 text-sm ${col.align || ''}`}>
                    {col.render ? col.render(row, rowIdx) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="px-4 py-8 text-center text-sm text-muted-foreground">
          {emptyMessage || 'No data available'}
        </div>
      )}
    </div>
  </div>
);

const StatusBadge = ({ status }) => {
  const colors = {
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
    'Partly Paid': 'bg-amber-100 text-amber-800'
  };
  
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  );
};

export const DashboardView = ({ data }) => {
  const summary = data.summary || {};
  const topCustomers = data.top_customers || [];
  const recentOrders = data.recent_orders || [];
  const recentInvoices = data.recent_invoices || [];
  const salesByStatus = data.sales_by_status || {};
  const topItems = data.top_items || [];
  const outstandingReceivables = data.outstanding_receivables || 0;

  const formatCurrency = (value) => {
    if (!value && value !== 0) return '₹0.00';
    return `₹${parseFloat(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Order table columns
  const orderColumns = [
    {
      header: 'Order',
      key: 'name',
      render: (row) => (
        <a
          href={`${ERP_BASE_URL}/app/sales-order/${row.name}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline font-mono text-xs"
        >
          {row.name}
        </a>
      )
    },
    { header: 'Customer', key: 'customer' },
    { header: 'Date', key: 'transaction_date' },
    {
      header: 'Amount',
      key: 'grand_total',
      align: 'text-right',
      render: (row) => <span className="font-medium">{formatCurrency(row.grand_total)}</span>
    },
    {
      header: 'Status',
      key: 'status',
      render: (row) => <StatusBadge status={row.status} />
    }
  ];

  // Invoice table columns
  const invoiceColumns = [
    {
      header: 'Invoice',
      key: 'name',
      render: (row) => (
        <a
          href={`${ERP_BASE_URL}/app/sales-invoice/${row.name}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline font-mono text-xs"
        >
          {row.name}
        </a>
      )
    },
    { header: 'Customer', key: 'customer' },
    { header: 'Date', key: 'posting_date' },
    {
      header: 'Total',
      key: 'grand_total',
      align: 'text-right',
      render: (row) => <span className="font-medium">{formatCurrency(row.grand_total)}</span>
    },
    {
      header: 'Outstanding',
      key: 'outstanding_amount',
      align: 'text-right',
      render: (row) => (
        <span className={parseFloat(row.outstanding_amount || 0) > 0 ? 'text-amber-600 font-medium' : 'text-green-600'}>
          {formatCurrency(row.outstanding_amount)}
        </span>
      )
    },
    {
      header: 'Status',
      key: 'status',
      render: (row) => <StatusBadge status={row.status} />
    }
  ];

  // Top customers table columns
  const customerColumns = [
    {
      header: '#',
      key: 'rank',
      render: (row, idx) => <span className="text-muted-foreground">{idx + 1}</span>
    },
    {
      header: 'Customer',
      key: 'customer',
      render: (row) => (
        <a
          href={`${ERP_BASE_URL}/app/customer/${row.customer}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline"
        >
          {row.customer}
        </a>
      )
    },
    {
      header: 'Orders',
      key: 'order_count',
      align: 'text-center',
      render: (row) => <span className="font-medium">{row.order_count}</span>
    },
    {
      header: 'Total Revenue',
      key: 'total_value',
      align: 'text-right',
      render: (row) => <span className="font-semibold text-green-600">{formatCurrency(row.total_value)}</span>
    }
  ];

  // Items table columns
  const itemColumns = [
    {
      header: 'Item Code',
      key: 'name',
      render: (row) => (
        <a
          href={`${ERP_BASE_URL}/app/item/${row.name}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary hover:underline font-mono text-xs"
        >
          {row.name}
        </a>
      )
    },
    { header: 'Item Name', key: 'item_name' },
    { header: 'Group', key: 'item_group' },
    { header: 'UOM', key: 'stock_uom' }
  ];

  return (
    <div className="space-y-6 w-full max-w-4xl" data-testid="dashboard-view">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard
          title="Total Sales"
          value={formatCurrency(summary.total_sales_value)}
          subtitle={`${summary.total_orders || 0} orders`}
          icon={TrendingUp}
          color="text-green-600"
          link={`${ERP_BASE_URL}/app/sales-order`}
        />
        <KPICard
          title="Customers"
          value={summary.total_customers || 0}
          subtitle="Active customers"
          icon={Users}
          color="text-blue-600"
          link={`${ERP_BASE_URL}/app/customer`}
        />
        <KPICard
          title="Invoiced"
          value={formatCurrency(summary.total_invoiced)}
          subtitle={`${summary.total_invoices || 0} invoices`}
          icon={FileText}
          color="text-purple-600"
          link={`${ERP_BASE_URL}/app/sales-invoice`}
        />
        <KPICard
          title="Outstanding"
          value={formatCurrency(outstandingReceivables)}
          subtitle="Accounts receivable"
          icon={AlertCircle}
          color={outstandingReceivables > 0 ? "text-amber-600" : "text-green-600"}
          link={`${ERP_BASE_URL}/app/accounts-receivable`}
        />
      </div>

      {/* Sales by Status */}
      {Object.keys(salesByStatus).length > 0 && (
        <div className="bg-card text-card-foreground rounded-xl border border-border p-4" data-testid="sales-by-status">
          <h3 className="font-semibold text-sm mb-3" style={{ fontFamily: 'Manrope, sans-serif' }}>Sales Orders by Status</h3>
          <div className="flex flex-wrap gap-3">
            {Object.entries(salesByStatus).map(([status, data]) => (
              <div key={status} className="flex items-center gap-2 px-3 py-2 bg-muted/50 rounded-lg">
                <StatusBadge status={status} />
                <span className="text-sm font-medium">{data.count}</span>
                <span className="text-xs text-muted-foreground">({formatCurrency(data.value)})</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Customers */}
        <DataTable
          title="Top Customers by Revenue"
          columns={customerColumns}
          data={topCustomers}
          emptyMessage="No customer data available"
        />

        {/* Items */}
        <DataTable
          title="Items Catalog"
          columns={itemColumns}
          data={topItems}
          emptyMessage="No items found"
        />
      </div>

      {/* Recent Orders */}
      <DataTable
        title="Recent Sales Orders"
        columns={orderColumns}
        data={recentOrders}
        emptyMessage="No recent orders"
      />

      {/* Recent Invoices */}
      <DataTable
        title="Recent Invoices"
        columns={invoiceColumns}
        data={recentInvoices}
        emptyMessage="No recent invoices"
      />

      {/* Quick Links */}
      <div className="bg-muted/30 rounded-xl border border-border p-4">
        <h3 className="font-semibold text-sm mb-3" style={{ fontFamily: 'Manrope, sans-serif' }}>Quick Links to ERPNext</h3>
        <div className="flex flex-wrap gap-2">
          {[
            { label: 'Sales Analytics', url: `${ERP_BASE_URL}/app/query-report/Sales Analytics` },
            { label: 'Accounts Receivable', url: `${ERP_BASE_URL}/app/query-report/Accounts Receivable` },
            { label: 'Stock Balance', url: `${ERP_BASE_URL}/app/query-report/Stock Balance` },
            { label: 'General Ledger', url: `${ERP_BASE_URL}/app/query-report/General Ledger` },
            { label: 'Customer Statement', url: `${ERP_BASE_URL}/app/query-report/Customer Statement` },
          ].map((link, idx) => (
            <a
              key={idx}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1.5 bg-background border border-border rounded-md hover:bg-muted hover:border-primary/30 transition-colors"
            >
              {link.label} →
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DashboardView;
