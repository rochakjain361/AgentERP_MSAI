/**
 * ToolResultsView - Display query results from custom tools
 */
import React from 'react';
import { ExternalLink, RefreshCw, Trash2, Clock, Database } from 'lucide-react';
import { ERP_BASE_URL } from '../lib/constants';

export const ToolResultsView = ({ toolResult, onRefresh, onDelete, isLoading }) => {
  if (!toolResult) return null;

  const { tool_name, doctype, description, data, count, fields } = toolResult;

  // Get display columns from fields or default
  const columns = fields && fields.length > 0 ? fields : Object.keys(data[0] || {});

  const formatValue = (value, column) => {
    if (value === null || value === undefined) return '-';
    
    // Format numbers
    if (typeof value === 'number') {
      if (column.includes('total') || column.includes('amount') || column.includes('rate')) {
        return `₹${value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
      }
      return value.toLocaleString();
    }
    
    return String(value);
  };

  const getColumnLabel = (column) => {
    return column
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusColor = (status) => {
    const colors = {
      'Draft': 'bg-yellow-100 text-yellow-800',
      'Pending': 'bg-yellow-100 text-yellow-800',
      'To Deliver and Bill': 'bg-blue-100 text-blue-800',
      'To Bill': 'bg-purple-100 text-purple-800',
      'Completed': 'bg-green-100 text-green-800',
      'Paid': 'bg-green-100 text-green-800',
      'Cancelled': 'bg-red-100 text-red-800',
      'Unpaid': 'bg-red-100 text-red-800',
      'Overdue': 'bg-orange-100 text-orange-800',
      'Active': 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-4 w-full max-w-5xl" data-testid="tool-results-view">
      {/* Header */}
      <div className="bg-card border border-border rounded-xl p-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-semibold" style={{ fontFamily: 'Manrope, sans-serif' }}>
                {tool_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </h3>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{description}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                DocType: {doctype}
              </span>
              <span>{count} results</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-2 hover:bg-muted rounded-lg transition-colors"
              title="Refresh results"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onDelete}
              className="p-2 hover:bg-destructive/10 hover:text-destructive rounded-lg transition-colors"
              title="Delete tool"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <a
              href={`${ERP_BASE_URL}/app/${doctype.toLowerCase().replace(/ /g, '-')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 px-3 py-1.5 text-xs border border-border rounded-md hover:bg-muted transition-colors"
            >
              View in ERP <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>

      {/* Results Table */}
      <div className="bg-card border border-border rounded-xl overflow-hidden">
        {data && data.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {columns.map((col, idx) => (
                    <th 
                      key={idx} 
                      className="px-4 py-3 text-xs font-semibold text-muted-foreground text-left"
                    >
                      {getColumnLabel(col)}
                    </th>
                  ))}
                  <th className="px-4 py-3 text-xs font-semibold text-muted-foreground text-center w-20">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.map((row, rowIdx) => (
                  <tr 
                    key={rowIdx} 
                    className="border-b border-border/50 hover:bg-muted/20 transition-colors"
                  >
                    {columns.map((col, colIdx) => (
                      <td key={colIdx} className="px-4 py-3 text-sm">
                        {col === 'name' ? (
                          <a
                            href={`${ERP_BASE_URL}/app/${doctype.toLowerCase().replace(/ /g, '-')}/${row[col]}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline font-mono text-xs"
                          >
                            {row[col]}
                          </a>
                        ) : col === 'status' ? (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(row[col])}`}>
                            {row[col]}
                          </span>
                        ) : col === 'customer' || col === 'supplier' ? (
                          <a
                            href={`${ERP_BASE_URL}/app/${col}/${row[col]}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:text-primary transition-colors"
                          >
                            {row[col]}
                          </a>
                        ) : (
                          <span className={col.includes('total') || col.includes('amount') ? 'font-medium' : ''}>
                            {formatValue(row[col], col)}
                          </span>
                        )}
                      </td>
                    ))}
                    <td className="px-4 py-3 text-center">
                      <a
                        href={`${ERP_BASE_URL}/app/${doctype.toLowerCase().replace(/ /g, '-')}/${row.name}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        Open →
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No results found</p>
            <p className="text-xs mt-1">Try adjusting your query filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ToolResultsView;
