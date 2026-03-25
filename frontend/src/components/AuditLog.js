/**
 * Audit Log Component - Activity trail viewer
 */
import React, { useState, useEffect } from 'react';
import { 
  Activity, User, Clock, FileText, CheckCircle, XCircle,
  AlertTriangle, ChevronDown, ChevronUp, Filter, X
} from 'lucide-react';
import { auditApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const actionColors = {
  user_login: 'text-blue-400 bg-blue-500/20',
  user_register: 'text-green-400 bg-green-500/20',
  create_order: 'text-emerald-400 bg-emerald-500/20',
  update_order: 'text-amber-400 bg-amber-500/20',
  delete_order: 'text-red-400 bg-red-500/20',
  create_customer: 'text-cyan-400 bg-cyan-500/20',
  query_data: 'text-purple-400 bg-purple-500/20',
  request_approval: 'text-yellow-400 bg-yellow-500/20',
  approve_request: 'text-green-400 bg-green-500/20',
  reject_request: 'text-red-400 bg-red-500/20',
  create_tool: 'text-indigo-400 bg-indigo-500/20',
  run_tool: 'text-violet-400 bg-violet-500/20',
  ai_chat: 'text-pink-400 bg-pink-500/20',
};

const resultIcons = {
  success: <CheckCircle className="w-3.5 h-3.5 text-green-400" />,
  failure: <XCircle className="w-3.5 h-3.5 text-red-400" />,
  pending: <Clock className="w-3.5 h-3.5 text-yellow-400" />,
};

const AuditLogEntry = ({ log, isExpanded, onToggle }) => {
  const colorClass = actionColors[log.action] || 'text-slate-400 bg-slate-500/20';
  
  return (
    <div className="border-b border-slate-700/50 last:border-0">
      <div 
        className="flex items-center gap-3 p-3 hover:bg-slate-800/50 cursor-pointer transition-colors"
        onClick={onToggle}
      >
        <div className={`w-8 h-8 rounded-lg ${colorClass} flex items-center justify-center shrink-0`}>
          <Activity className="w-4 h-4" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-white text-sm font-medium">
              {log.action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
            {resultIcons[log.result]}
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span>{log.user_email}</span>
            <span>•</span>
            <span>{log.resource_type}</span>
            <span>•</span>
            <span>{new Date(log.timestamp).toLocaleString()}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 text-xs rounded ${
            log.result === 'success' ? 'bg-green-500/20 text-green-300' :
            log.result === 'failure' ? 'bg-red-500/20 text-red-300' :
            'bg-yellow-500/20 text-yellow-300'
          }`}>
            {log.result}
          </span>
          {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
        </div>
      </div>

      {isExpanded && (
        <div className="px-3 pb-3 pl-14 space-y-2">
          {log.result_message && (
            <div className="text-xs text-slate-400">
              <span className="font-medium text-slate-300">Message:</span> {log.result_message}
            </div>
          )}
          {log.ai_reasoning && (
            <div className="text-xs p-2 bg-blue-500/10 border border-blue-500/20 rounded">
              <span className="font-medium text-blue-300">AI Reasoning:</span> {log.ai_reasoning}
            </div>
          )}
          {log.input_params && Object.keys(log.input_params).length > 0 && (
            <div className="text-xs text-slate-400">
              <span className="font-medium text-slate-300">Parameters:</span>
              <pre className="mt-1 p-2 bg-slate-800 rounded text-slate-300 overflow-x-auto">
                {JSON.stringify(log.input_params, null, 2)}
              </pre>
            </div>
          )}
          {log.approval_required && (
            <div className="flex items-center gap-1 text-xs text-yellow-400">
              <AlertTriangle className="w-3 h-3" />
              Approval Required {log.approval_id && `(ID: ${log.approval_id.slice(0, 8)}...)`}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AuditLog = ({ isOpen, onClose }) => {
  const { isManager, user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);
  const [filter, setFilter] = useState('all');
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (isOpen) {
      fetchLogs();
    }
  }, [isOpen, filter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = { limit: 50 };
      if (filter !== 'all') {
        params.action = filter;
      }
      const response = await auditApi.getLogs(params);
      if (response.data.status === 'success') {
        setLogs(response.data.logs || []);
        setTotal(response.data.total || 0);
      }
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const actionTypes = [
    { value: 'all', label: 'All Actions' },
    { value: 'create_order', label: 'Orders Created' },
    { value: 'create_customer', label: 'Customers Created' },
    { value: 'approve_request', label: 'Approvals' },
    { value: 'reject_request', label: 'Rejections' },
    { value: 'ai_chat', label: 'AI Chats' },
    { value: 'run_tool', label: 'Tools Run' },
  ];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-3xl mx-4 max-h-[80vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Activity Log</h2>
              <p className="text-xs text-slate-400">
                {total} total actions • Who did what, when, and why
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Filter */}
        <div className="p-3 border-b border-slate-700 bg-slate-800/50">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {actionTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Logs */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-4 space-y-3">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="h-16 bg-slate-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">No activity logs yet</p>
            </div>
          ) : (
            logs.map(log => (
              <AuditLogEntry
                key={log.id}
                log={log}
                isExpanded={expandedId === log.id}
                onToggle={() => setExpandedId(expandedId === log.id ? null : log.id)}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditLog;
