/**
 * AIRiskWidget - Chat-embeddable Revenue Risk Radar component
 * 
 * Displays risk analysis results inline within the chat flow.
 * RBAC: Only visible to Admin and Manager roles.
 */
import React, { useState } from 'react';
import { 
  AlertTriangle, 
  AlertCircle,
  CheckCircle,
  Loader2,
  ArrowRight,
  Ban,
  Users,
  Send,
  FileText,
  Zap
} from 'lucide-react';
import { aiAnalysisApi } from '../lib/api';
import { toast } from 'sonner';

const riskConfig = {
  critical: {
    color: 'bg-red-500',
    bgLight: 'bg-red-50',
    border: 'border-red-300',
    text: 'text-red-700',
    icon: AlertTriangle,
    label: 'CRITICAL'
  },
  medium: {
    color: 'bg-amber-500',
    bgLight: 'bg-amber-50',
    border: 'border-amber-300',
    text: 'text-amber-700',
    icon: AlertCircle,
    label: 'MEDIUM'
  },
  low: {
    color: 'bg-green-500',
    bgLight: 'bg-green-50',
    border: 'border-green-300',
    text: 'text-green-700',
    icon: CheckCircle,
    label: 'LOW'
  }
};

const actionIcons = {
  stop_sales: Ban,
  escalate_management: Users,
  send_critical_reminder: Send,
  send_reminder: Send,
  escalate_tracking: FileText,
  view_order: FileText,
  continue_workflow: ArrowRight
};

// Compact Risk Card for chat display
const RiskCard = ({ order, onExecuteAction, executingAction }) => {
  const config = riskConfig[order.risk_level] || riskConfig.low;
  const RiskIcon = config.icon;
  
  return (
    <div className={`rounded-lg border ${config.border} ${config.bgLight} overflow-hidden mb-3`}>
      {/* Compact Header */}
      <div className={`px-3 py-2 ${config.color} flex items-center justify-between`}>
        <div className="flex items-center gap-2 text-white text-sm">
          <RiskIcon className="w-4 h-4" />
          <span className="font-semibold">{config.label}</span>
        </div>
        <span className="text-white/90 text-xs font-medium truncate max-w-[150px]">
          {order.customer}
        </span>
      </div>
      
      {/* Metrics Row */}
      <div className="px-3 py-2 bg-white border-b border-gray-100 flex gap-4">
        <div>
          <div className="text-[10px] text-gray-500 uppercase">Outstanding</div>
          <div className={`text-base font-bold ${config.text}`}>
            ₹{order.amount_due?.toLocaleString() || 0}
          </div>
        </div>
        <div>
          <div className="text-[10px] text-gray-500 uppercase">Overdue</div>
          <div className={`text-base font-bold ${config.text}`}>
            {order.days_overdue || 0} days
          </div>
        </div>
      </div>
      
      {/* Reasoning */}
      <div className="px-3 py-2 bg-white text-xs text-gray-600 border-b border-gray-100">
        {order.reasoning}
      </div>
      
      {/* Actions - Compact */}
      <div className="px-3 py-2 bg-white flex flex-wrap gap-2">
        {order.suggested_actions?.slice(0, 2).map((action) => {
          const ActionIcon = actionIcons[action.id] || ArrowRight;
          const isExecuting = executingAction === `${order.id}-${action.id}`;
          
          return (
            <button
              key={action.id}
              onClick={() => onExecuteAction(order, action)}
              disabled={isExecuting}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-medium transition-all ${
                action.severity === 'critical' || action.severity === 'high'
                  ? 'bg-red-100 text-red-700 hover:bg-red-200'
                  : action.severity === 'medium'
                  ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } ${isExecuting ? 'opacity-50 cursor-not-allowed' : ''}`}
              data-testid={`action-${action.id}-${order.customer}`}
            >
              {isExecuting ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <ActionIcon className="w-3 h-3" />
              )}
              {action.label}
              {action.is_automatic && (
                <span className="px-1 py-0.5 bg-red-200 text-red-800 text-[8px] font-bold rounded ml-1">
                  AUTO
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// Main Widget for displaying analysis results in chat
export const AIRiskResultsWidget = ({ data }) => {
  const [executingAction, setExecutingAction] = useState(null);
  
  const handleExecuteAction = async (order, action) => {
    // Special handling for "Stop Future Sales" - trigger multi-step workflow
    if (action.id === 'stop_sales') {
      // Dispatch custom event to trigger the AI decision workflow in chat
      const event = new CustomEvent('ai:stop-sales-decision', {
        detail: {
          customer: order.customer,
          amount_due: order.amount_due,
          days_overdue: order.days_overdue,
          order_id: order.id,
          risk_level: order.risk_level,
          reasoning: order.reasoning,
          annualized_risk: order.amount_due * 15
        }
      });
      window.dispatchEvent(event);
      return; // Don't execute directly - let the workflow handle it
    }
    
    // For other actions, proceed with confirmation
    if (action.requires_confirmation && !action.is_automatic) {
      const confirmed = window.confirm(
        `${action.label} for ${order.customer}?\n\n${action.description}`
      );
      if (!confirmed) return;
    }
    
    const actionKey = `${order.id}-${action.id}`;
    setExecutingAction(actionKey);
    
    try {
      const response = await aiAnalysisApi.executeAction(
        action.id,
        order.customer,
        order.id
      );
      
      if (response.data.status === 'success') {
        toast.success(response.data.result.message);
      } else {
        toast.error(response.data.message || 'Action failed');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to execute action');
    } finally {
      setExecutingAction(null);
    }
  };
  
  if (!data || !data.orders) return null;
  
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mt-3 shadow-sm" data-testid="ai-risk-results-widget">
      {/* Summary Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
            <Zap className="w-4 h-4 text-amber-600" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 text-sm">AI Risk Analysis</h4>
            <p className="text-xs text-gray-500">{data.summary?.total_analyzed || 0} orders analyzed</p>
          </div>
        </div>
        
        {/* Summary Stats */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span className="font-medium">{data.summary?.critical_count || 0}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-amber-500" />
            <span className="font-medium">{data.summary?.medium_count || 0}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="font-medium">{data.summary?.low_count || 0}</span>
          </div>
        </div>
      </div>
      
      {/* Auto-actions notification */}
      {data.auto_actions?.length > 0 && (
        <div className="mb-4 p-2 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center gap-2 text-red-700 text-xs">
            <Zap className="w-3 h-3" />
            <span className="font-medium">
              {data.auto_actions.length} critical reminder(s) automatically triggered
            </span>
          </div>
        </div>
      )}
      
      {/* Amount at risk */}
      {data.summary?.total_amount_at_risk > 0 && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-500 uppercase">Total Amount at Risk</div>
          <div className="text-xl font-bold text-red-600">
            ₹{data.summary.total_amount_at_risk?.toLocaleString()}
          </div>
        </div>
      )}
      
      {/* Risk Cards */}
      <div className="space-y-2">
        {data.orders?.slice(0, 5).map((order) => (
          <RiskCard
            key={order.id}
            order={order}
            onExecuteAction={handleExecuteAction}
            executingAction={executingAction}
          />
        ))}
      </div>
      
      {data.orders?.length === 0 && (
        <div className="text-center py-6">
          <CheckCircle className="w-10 h-10 text-green-500 mx-auto mb-2" />
          <h4 className="font-medium text-gray-900">All Clear</h4>
          <p className="text-xs text-gray-500">No significant payment risks detected</p>
        </div>
      )}
      
      {data.orders?.length > 5 && (
        <div className="text-center text-xs text-gray-500 mt-3">
          Showing top 5 of {data.orders.length} orders
        </div>
      )}
    </div>
  );
};

// Loading state widget
export const AIRiskLoadingWidget = () => (
  <div className="bg-white border border-gray-200 rounded-xl p-6 mt-3 shadow-sm flex flex-col items-center" data-testid="ai-risk-loading">
    <Loader2 className="w-8 h-8 text-amber-500 animate-spin mb-3" />
    <p className="text-sm text-gray-600">Scanning customer exposure and payment risk signals...</p>
  </div>
);

// Error state widget
export const AIRiskErrorWidget = ({ error, onRetry }) => (
  <div className="bg-white border border-red-200 rounded-xl p-6 mt-3 shadow-sm flex flex-col items-center" data-testid="ai-risk-error">
    <AlertTriangle className="w-8 h-8 text-red-500 mb-3" />
    <p className="text-sm text-red-600 font-medium mb-3">{error}</p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800"
      >
        Retry Analysis
      </button>
    )}
  </div>
);

export default AIRiskResultsWidget;
