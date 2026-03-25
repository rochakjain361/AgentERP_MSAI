/**
 * Audit Log Panel - Display system audit trail
 */
import React, { useState, useEffect } from 'react';
import { FileText, Clock, User, CheckCircle, AlertCircle } from 'lucide-react';
import { auditApi } from '../lib/api';

const AuditLogPanel = ({ user }) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, [filter, user]);

  const fetchLogs = async () => {
    try {
      const filters = {};
      if (filter !== 'all') {
        filters.action = filter;
      }
      const result = await auditApi.getLogs(10, 0, filters);
      setLogs(result.data?.logs || []);
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const actionIcons = {
    user_login: User,
    create_order: CheckCircle,
    approve_request: CheckCircle,
    reject_request: AlertCircle,
    query_data: FileText,
    create_customer: CheckCircle,
  };

  const actionColors = {
    user_login: 'text-blue-400',
    create_order: 'text-green-400',
    approve_request: 'text-green-400',
    reject_request: 'text-red-400',
    query_data: 'text-slate-400',
    create_customer: 'text-green-400',
  };

  const resultColors = {
    success: 'bg-green-500/10 text-green-400 border-green-500/30',
    pending: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    failure: 'bg-red-500/10 text-red-400 border-red-500/30',
  };

  const filters = [
    { value: 'all', label: 'All Actions' },
    { value: 'user_login', label: 'Logins' },
    { value: 'create_order', label: 'Orders Created' },
    { value: 'approve_request', label: 'Approvals' },
    { value: 'reject_request', label: 'Rejections' },
  ];

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-gradient-to-r from-purple-500/10 to-pink-500/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
            <FileText className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold">Audit Log</h3>
            <p className="text-xs text-slate-400">System activity and transactions</p>
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex overflow-x-auto border-b border-slate-700 px-4">
        {filters.map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`px-3 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              filter === f.value
                ? 'border-purple-500 text-purple-400'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        {loading ? (
          <div className="text-center py-8">
            <Clock className="w-6 h-6 text-slate-500 animate-spin mx-auto mb-2" />
            <p className="text-slate-400 text-sm">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-8 h-8 text-slate-500/30 mx-auto mb-2" />
            <p className="text-slate-400 text-sm">No logs found</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {logs.map((log) => {
              const ActionIcon = actionIcons[log.action] || FileText;
              const resultClass = resultColors[log.result] || resultColors.success;

              return (
                <div
                  key={log.id}
                  className="flex items-start gap-3 p-3 rounded-lg bg-slate-700/50 border border-slate-600 hover:border-slate-500 transition-colors"
                >
                  <div className={`w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0 ${actionColors[log.action] || 'text-slate-400'}`}>
                    <ActionIcon className="w-4 h-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-medium text-white capitalize">
                          {log.action.replace(/_/g, ' ')}
                        </div>
                        <div className="text-xs text-slate-400 mt-0.5">
                          {log.user_email} • {log.user_role}
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium border ${resultClass}`}>
                        {log.result}
                      </div>
                    </div>

                    <div className="text-xs text-slate-500 mt-2">
                      {log.resource_type}
                      {log.resource_id && ` • ${log.resource_id.substring(0, 8)}...`}
                    </div>

                    {log.result_message && (
                      <div className="text-xs text-slate-400 mt-1 italic">
                        {log.result_message}
                      </div>
                    )}

                    <div className="text-xs text-slate-500 mt-2 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(log.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditLogPanel;
