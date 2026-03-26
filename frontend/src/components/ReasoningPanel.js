/**
 * ReasoningPanel - Displays AI reasoning summary and suggested actions
 * 
 * Shows:
 * - Situation summary
 * - Metrics checked
 * - Severity classification
 * - Suggested actions with checkboxes
 * - Expected impact
 */
import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Play,
  Shield,
  DollarSign,
  BarChart3,
  AlertCircle,
  Info
} from 'lucide-react';

const severityConfig = {
  critical: {
    color: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: AlertTriangle,
    badge: 'bg-red-100 text-red-700'
  },
  high: {
    color: 'text-orange-600',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    icon: AlertCircle,
    badge: 'bg-orange-100 text-orange-700'
  },
  medium: {
    color: 'text-amber-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    icon: Clock,
    badge: 'bg-amber-100 text-amber-700'
  },
  low: {
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: Info,
    badge: 'bg-blue-100 text-blue-700'
  }
};

const ReasoningPanel = ({ 
  situation, 
  onExecute, 
  isExecuting = false,
  userRole = 'viewer'
}) => {
  const [selectedActions, setSelectedActions] = useState([]);
  const [showMetrics, setShowMetrics] = useState(false);
  const [showImpact, setShowImpact] = useState(false);

  if (!situation) return null;

  const config = severityConfig[situation.severity] || severityConfig.low;
  const SeverityIcon = config.icon;
  const canExecute = userRole !== 'viewer';

  const toggleAction = (actionId) => {
    setSelectedActions(prev => 
      prev.includes(actionId) 
        ? prev.filter(id => id !== actionId)
        : [...prev, actionId]
    );
  };

  const selectAllActions = () => {
    const allIds = situation.suggested_actions.map(a => a.id);
    setSelectedActions(allIds);
  };

  const handleExecute = () => {
    if (selectedActions.length > 0 && onExecute) {
      onExecute(situation.id, situation.type, selectedActions, situation.context_data);
    }
  };

  return (
    <div className={`rounded-xl border-2 ${config.border} ${config.bg} overflow-hidden`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${config.badge}`}>
              <SeverityIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{situation.situation}</h3>
              <p className={`text-sm ${config.color} font-medium mt-1`}>
                {situation.status_reason}
              </p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${config.badge}`}>
            {situation.severity}
          </span>
        </div>
      </div>

      {/* Metrics Section */}
      <div className="border-b border-gray-200">
        <button 
          onClick={() => setShowMetrics(!showMetrics)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/50 transition-colors"
        >
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <BarChart3 className="w-4 h-4" />
            Metrics Checked ({situation.metrics_checked?.length || 0})
          </div>
          {showMetrics ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {showMetrics && (
          <div className="px-4 pb-4 grid grid-cols-2 gap-3">
            {situation.metrics_checked?.map((metric, idx) => (
              <div key={idx} className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="text-xs text-gray-500">{metric.name}</div>
                <div className="text-sm font-semibold text-gray-900">{metric.value}</div>
                <div className="text-xs text-gray-400 mt-1">Threshold: {metric.threshold}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suggested Actions */}
      <div className="p-4 bg-white">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
            <Play className="w-4 h-4" />
            Suggested Actions
          </h4>
          {canExecute && (
            <button 
              onClick={selectAllActions}
              className="text-xs text-blue-600 hover:underline"
            >
              Select All
            </button>
          )}
        </div>
        
        <div className="space-y-2">
          {situation.suggested_actions?.map((action) => (
            <label 
              key={action.id}
              className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${
                selectedActions.includes(action.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              } ${!canExecute ? 'opacity-60 cursor-not-allowed' : ''}`}
            >
              <input
                type="checkbox"
                checked={selectedActions.includes(action.id)}
                onChange={() => canExecute && toggleAction(action.id)}
                disabled={!canExecute}
                className="mt-0.5 w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">{action.label}</span>
                  {action.requires_approval && (
                    <span className="px-1.5 py-0.5 bg-amber-100 text-amber-700 text-[10px] font-medium rounded flex items-center gap-1">
                      <Shield className="w-3 h-3" />
                      Approval
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{action.description}</p>
              </div>
            </label>
          ))}
        </div>

        {/* Approval Notice */}
        {situation.approval_needed && (
          <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-amber-700">
              <Shield className="w-4 h-4" />
              <span className="font-medium">Manager approval required</span>
            </div>
            <p className="text-xs text-amber-600 mt-1">{situation.approval_reason}</p>
          </div>
        )}
      </div>

      {/* Expected Impact */}
      <div className="border-t border-gray-200">
        <button 
          onClick={() => setShowImpact(!showImpact)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-white/50 transition-colors"
        >
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
            <TrendingUp className="w-4 h-4 text-green-600" />
            Expected Impact
          </div>
          {showImpact ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
        
        {showImpact && situation.expected_impact && (
          <div className="px-4 pb-4 grid grid-cols-2 gap-3">
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <DollarSign className="w-3 h-3" />
                Financial Risk
              </div>
              <div className="text-sm font-semibold text-gray-900">
                ₹{(situation.expected_impact.financial_risk || 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                Time Saved
              </div>
              <div className="text-sm font-semibold text-gray-900">
                {situation.expected_impact.time_saved_hours || 0} hours
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="text-xs text-gray-500">Recovery Probability</div>
              <div className="text-sm font-semibold text-green-600">
                {situation.expected_impact.recovery_probability || 'N/A'}
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <div className="text-xs text-gray-500">Risk Reduction</div>
              <div className="text-sm font-semibold text-blue-600">
                {situation.expected_impact.risk_reduction || 'N/A'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Execute Button */}
      {canExecute && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <button
            onClick={handleExecute}
            disabled={selectedActions.length === 0 || isExecuting}
            className={`w-full py-3 px-4 rounded-lg font-medium flex items-center justify-center gap-2 transition-all ${
              selectedActions.length > 0 && !isExecuting
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isExecuting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Execute {selectedActions.length} Action{selectedActions.length !== 1 ? 's' : ''}
              </>
            )}
          </button>
        </div>
      )}

      {!canExecute && (
        <div className="p-4 bg-gray-50 border-t border-gray-200 text-center">
          <p className="text-sm text-gray-500">
            <Shield className="w-4 h-4 inline mr-1" />
            View-only access. Contact a manager to execute actions.
          </p>
        </div>
      )}
    </div>
  );
};

export default ReasoningPanel;
