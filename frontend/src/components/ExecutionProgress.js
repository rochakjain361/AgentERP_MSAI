/**
 * ExecutionProgress - Shows step-by-step workflow execution status
 * 
 * Displays:
 * - Each step with status (pending/running/success/failed)
 * - Verification results
 * - Business impact summary
 * - Recovery suggestions for failures
 */
import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Loader2,
  AlertTriangle,
  ChevronRight,
  TrendingUp,
  Shield,
  RotateCcw
} from 'lucide-react';

const stepStatusConfig = {
  pending: {
    icon: Clock,
    color: 'text-gray-400',
    bg: 'bg-gray-100',
    label: 'Pending'
  },
  running: {
    icon: Loader2,
    color: 'text-blue-500',
    bg: 'bg-blue-100',
    label: 'Running',
    animate: true
  },
  success: {
    icon: CheckCircle2,
    color: 'text-green-600',
    bg: 'bg-green-100',
    label: 'Completed'
  },
  failed: {
    icon: XCircle,
    color: 'text-red-600',
    bg: 'bg-red-100',
    label: 'Failed'
  },
  needs_approval: {
    icon: Shield,
    color: 'text-amber-600',
    bg: 'bg-amber-100',
    label: 'Awaiting Approval'
  },
  skipped: {
    icon: ChevronRight,
    color: 'text-gray-400',
    bg: 'bg-gray-100',
    label: 'Skipped'
  }
};

const workflowStatusConfig = {
  completed: {
    color: 'text-green-600',
    bg: 'bg-green-50',
    border: 'border-green-200',
    label: 'Workflow Completed'
  },
  partial: {
    color: 'text-amber-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    label: 'Partially Completed'
  },
  failed: {
    color: 'text-red-600',
    bg: 'bg-red-50',
    border: 'border-red-200',
    label: 'Workflow Failed'
  },
  awaiting_approval: {
    color: 'text-amber-600',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    label: 'Awaiting Approval'
  },
  running: {
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    label: 'In Progress'
  }
};

const ExecutionProgress = ({ 
  workflowResult, 
  onRetry,
  onClose 
}) => {
  if (!workflowResult) return null;

  const { workflow_status, steps, summary, business_impact, recovery_suggestions } = workflowResult;
  const statusConfig = workflowStatusConfig[workflow_status] || workflowStatusConfig.running;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden shadow-lg">
      {/* Header */}
      <div className={`p-4 ${statusConfig.bg} ${statusConfig.border} border-b`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`font-semibold ${statusConfig.color}`}>
              {statusConfig.label}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {summary?.completed || 0} of {summary?.total_steps || 0} steps completed
            </p>
          </div>
          {workflow_status === 'completed' && (
            <CheckCircle2 className="w-8 h-8 text-green-500" />
          )}
        </div>
      </div>

      {/* Steps */}
      <div className="p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Execution Steps</h4>
        <div className="space-y-3">
          {steps?.map((step, idx) => {
            const config = stepStatusConfig[step.status] || stepStatusConfig.pending;
            const StepIcon = config.icon;
            
            return (
              <div 
                key={idx}
                className={`flex items-start gap-3 p-3 rounded-lg ${config.bg} border border-gray-200`}
              >
                <div className={`mt-0.5 ${config.color}`}>
                  <StepIcon className={`w-5 h-5 ${config.animate ? 'animate-spin' : ''}`} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">{step.name}</span>
                    <span className={`text-xs ${config.color}`}>{config.label}</span>
                  </div>
                  
                  {/* Verification result */}
                  {step.verification && (
                    <p className={`text-xs mt-1 ${step.verification.verified ? 'text-green-600' : 'text-red-600'}`}>
                      ✓ {step.verification.message}
                    </p>
                  )}
                  
                  {/* Error message */}
                  {step.error && (
                    <p className="text-xs text-red-600 mt-1">
                      Error: {step.error}
                    </p>
                  )}

                  {/* Approval pending */}
                  {step.status === 'needs_approval' && step.result?.approval_id && (
                    <p className="text-xs text-amber-600 mt-1">
                      Approval ID: {step.result.approval_id.slice(0, 8)}...
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Business Impact */}
      {business_impact && (
        <div className="px-4 pb-4">
          <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-medium text-green-800 flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4" />
              Business Impact
            </h4>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-600">Completion Rate</div>
                <div className="text-lg font-bold text-green-700">{business_impact.completion_rate}</div>
              </div>
              <div>
                <div className="text-xs text-gray-600">Time Saved</div>
                <div className="text-lg font-bold text-green-700">{business_impact.time_saved_minutes} mins</div>
              </div>
              <div>
                <div className="text-xs text-gray-600">Intervention Status</div>
                <div className="text-sm font-semibold text-gray-800">{business_impact.intervention_status}</div>
              </div>
              <div>
                <div className="text-xs text-gray-600">Amount at Risk</div>
                <div className="text-sm font-semibold text-gray-800">₹{(business_impact.amount_at_risk || 0).toLocaleString()}</div>
              </div>
            </div>
            <p className="text-xs text-green-600 mt-3 pt-3 border-t border-green-200">
              {business_impact.summary}
            </p>
          </div>
        </div>
      )}

      {/* Recovery Suggestions */}
      {recovery_suggestions && recovery_suggestions.length > 0 && (
        <div className="px-4 pb-4">
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <h4 className="text-sm font-medium text-red-800 flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4" />
              Recovery Suggestions
            </h4>
            <ul className="space-y-2">
              {recovery_suggestions.map((suggestion, idx) => (
                <li key={idx} className="text-sm text-red-700">
                  <span className="font-medium">{suggestion.failed_step}:</span> {suggestion.suggestion}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="p-4 bg-gray-50 border-t border-gray-200 flex gap-3">
        {onRetry && (summary?.failed > 0) && (
          <button
            onClick={onRetry}
            className="flex-1 py-2 px-4 bg-amber-500 text-white rounded-lg font-medium flex items-center justify-center gap-2 hover:bg-amber-600 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Retry Failed Steps
          </button>
        )}
        <button
          onClick={onClose}
          className="flex-1 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  );
};

export default ExecutionProgress;
