/**
 * TodaysPriorities - Dashboard showing all situations requiring attention
 * 
 * Main entry point for proactive AI analysis:
 * - Summary of critical/high/medium items
 * - List of situations with reasoning
 * - Quick actions
 */
import React, { useState, useEffect, useCallback } from 'react';
import { 
  AlertTriangle, 
  RefreshCw, 
  ChevronRight,
  Building2,
  Clock,
  TrendingDown,
  Sparkles
} from 'lucide-react';
import { reasoningApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import ReasoningPanel from './ReasoningPanel';
import ExecutionProgress from './ExecutionProgress';

const TodaysPriorities = ({ onClose }) => {
  const { user } = useAuth();
  const [priorities, setPriorities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedSituation, setSelectedSituation] = useState(null);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);

  const fetchPriorities = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await reasoningApi.getPriorities();
      if (response.data.status === 'success') {
        setPriorities(response.data);
        // Auto-select first critical situation
        if (response.data.situations?.length > 0) {
          const critical = response.data.situations.find(s => s.severity === 'critical');
          setSelectedSituation(critical || response.data.situations[0]);
        }
      }
    } catch (err) {
      setError('Failed to fetch priorities');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPriorities();
  }, [fetchPriorities]);

  const handleExecute = async (situationId, situationType, selectedActions, contextData) => {
    setExecuting(true);
    setExecutionResult(null);
    try {
      const response = await reasoningApi.executeSequence(
        situationId,
        situationType,
        selectedActions,
        contextData
      );
      setExecutionResult(response.data);
    } catch (err) {
      console.error('Execution error:', err);
      setExecutionResult({
        workflow_status: 'failed',
        steps: [],
        summary: { total_steps: 0, completed: 0, failed: 1 },
        recovery_suggestions: [{ failed_step: 'Execution', suggestion: err.message }]
      });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600">Analyzing ERP data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-100 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-amber-500" />
              Today's Priorities
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              AI-powered analysis of situations requiring your attention
            </p>
          </div>
          <div className="flex items-center gap-3">
            {user?.company && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm flex items-center gap-1">
                <Building2 className="w-4 h-4" />
                {user.company}
              </span>
            )}
            <button
              onClick={fetchPriorities}
              disabled={loading}
              className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg text-gray-700 font-medium"
            >
              Close
            </button>
          </div>
        </div>

        {/* Summary Bar */}
        {priorities?.summary && (
          <div className="bg-white px-6 py-3 border-b border-gray-200 flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-sm font-medium text-gray-700">
                {priorities.summary.critical} Critical
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-orange-500" />
              <span className="text-sm font-medium text-gray-700">
                {priorities.summary.high} High
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                {priorities.summary.total_situations - priorities.summary.critical - priorities.summary.high} Other
              </span>
            </div>
            {priorities.summary.requires_immediate_attention && (
              <div className="ml-auto px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium flex items-center gap-1">
                <AlertTriangle className="w-4 h-4" />
                Immediate attention required
              </div>
            )}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Situations List */}
          <div className="w-1/3 border-r border-gray-200 bg-white overflow-y-auto">
            {error ? (
              <div className="p-4 text-center text-red-600">{error}</div>
            ) : priorities?.situations?.length === 0 ? (
              <div className="p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                  <TrendingDown className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">All Clear!</h3>
                <p className="text-sm text-gray-500 mt-1">No situations requiring attention</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {priorities?.situations?.map((situation) => (
                  <button
                    key={situation.id}
                    onClick={() => {
                      setSelectedSituation(situation);
                      setExecutionResult(null);
                    }}
                    className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                      selectedSituation?.id === situation.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${
                            situation.severity === 'critical' ? 'bg-red-500' :
                            situation.severity === 'high' ? 'bg-orange-500' :
                            situation.severity === 'medium' ? 'bg-amber-500' : 'bg-gray-400'
                          }`} />
                          <span className="text-sm font-medium text-gray-900 truncate">
                            {situation.customer || 'Unknown'}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                          {situation.situation}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            situation.severity === 'critical' ? 'bg-red-100 text-red-700' :
                            situation.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                            situation.severity === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'
                          }`}>
                            {situation.severity}
                          </span>
                          <span className="text-xs text-gray-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {situation.suggested_actions?.length || 0} actions
                          </span>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Detail Panel */}
          <div className="flex-1 overflow-y-auto p-6">
            {executionResult ? (
              <ExecutionProgress
                workflowResult={executionResult}
                onClose={() => setExecutionResult(null)}
                onRetry={() => {
                  if (selectedSituation) {
                    // Could implement retry logic here
                    setExecutionResult(null);
                  }
                }}
              />
            ) : selectedSituation ? (
              <ReasoningPanel
                situation={selectedSituation}
                onExecute={handleExecute}
                isExecuting={executing}
                userRole={user?.role || 'viewer'}
              />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-500">
                Select a situation to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TodaysPriorities;
