/**
 * Approval Panel Component - Manages approval workflow
 */
import React, { useState, useEffect } from 'react';
import { 
  CheckCircle, XCircle, Clock, AlertTriangle, 
  ChevronRight, User, DollarSign, FileText, X
} from 'lucide-react';
import { approvalsApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const statusColors = {
  pending: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  approved: 'bg-green-500/20 text-green-300 border-green-500/30',
  rejected: 'bg-red-500/20 text-red-300 border-red-500/30'
};

const ApprovalCard = ({ approval, onApprove, onReject, canDecide }) => {
  const [notes, setNotes] = useState('');
  const [showActions, setShowActions] = useState(false);
  const [processing, setProcessing] = useState(false);

  const status = approval?.status || 'pending';
  const createdAt = approval?.created_at ? new Date(approval.created_at).toLocaleString() : 'N/A';
  const value = approval?.resource_data?.grand_total || approval?.order_value || 0;
  const actionType = approval?.action_type || 'approval_request';
  const actionLabel = String(actionType).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  const requesterEmail = approval?.requester_email || 'Unknown requester';
  const resourceType = approval?.resource_type || approval?.doctype || 'Approval Request';
  const displayReason = approval?.reason || approval?.notes || 'Approval review required';

  const handleApprove = async () => {
    setProcessing(true);
    await onApprove(approval.id, notes);
    setProcessing(false);
    setShowActions(false);
  };

  const handleReject = async () => {
    setProcessing(true);
    await onReject(approval.id, notes);
    setProcessing(false);
    setShowActions(false);
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 text-xs font-medium rounded border ${statusColors[status] || statusColors.pending}`}>
            {String(status).toUpperCase()}
          </span>
          <span className="text-xs text-slate-500">
            {createdAt}
          </span>
        </div>
        {value > 0 && (
          <span className="text-sm font-medium text-green-400">
            ₹{value.toLocaleString()}
          </span>
        )}
      </div>

      <div className="mb-3">
        <h4 className="text-white font-medium text-sm mb-1">
          {actionLabel}
        </h4>
        <p className="text-slate-400 text-xs">{displayReason}</p>
      </div>

      <div className="flex items-center gap-4 text-xs text-slate-500 mb-3">
        <div className="flex items-center gap-1">
          <User className="w-3 h-3" />
          {requesterEmail}
        </div>
        <div className="flex items-center gap-1">
          <FileText className="w-3 h-3" />
          {resourceType}
        </div>
      </div>

      {approval.ai_analysis && (
        <div className="mb-3 p-2 bg-blue-500/10 border border-blue-500/20 rounded text-xs text-blue-300">
          <span className="font-medium">AI Analysis:</span> {approval.ai_analysis}
        </div>
      )}

      {canDecide && status === 'pending' && (
        <div className="mt-3 pt-3 border-t border-slate-700">
          {!showActions ? (
            <button
              onClick={() => setShowActions(true)}
              className="w-full py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded-lg transition-colors"
            >
              Review & Decide
            </button>
          ) : (
            <div className="space-y-3">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add notes (optional)"
                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleApprove}
                  disabled={processing}
                  className="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve
                </button>
                <button
                  onClick={handleReject}
                  disabled={processing}
                  className="flex-1 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  Reject
                </button>
                <button
                  onClick={() => setShowActions(false)}
                  className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {status !== 'pending' && approval.reviewer_email && (
        <div className="mt-3 pt-3 border-t border-slate-700 text-xs text-slate-500">
          <span className={status === 'approved' ? 'text-green-400' : 'text-red-400'}>
            {status === 'approved' ? 'Approved' : 'Rejected'}
          </span>
          {' '}by {approval.reviewer_email}
          {approval.review_notes && (
            <span className="block mt-1 text-slate-400">"{approval.review_notes}"</span>
          )}
        </div>
      )}
    </div>
  );
};

const ApprovalPanel = ({ isOpen, onClose }) => {
  const { isManager, user } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [myRequests, setMyRequests] = useState([]);
  const [activeTab, setActiveTab] = useState('pending');
  const [loading, setLoading] = useState(true);

  const fetchApprovals = async () => {
    setLoading(true);
    try {
      if (isManager) {
        const response = await approvalsApi.getPending();
        if (response.data.status === 'success') {
          setApprovals(response.data.approvals || []);
        }
      }
      
      const myResponse = await approvalsApi.getMyRequests();
      if (myResponse.data.status === 'success') {
        setMyRequests(myResponse.data.approvals || []);
      }
    } catch (err) {
      console.error('Failed to fetch approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchApprovals();
    }
  }, [isOpen, isManager]);

  const handleApprove = async (id, notes) => {
    try {
      const response = await approvalsApi.approve(id, notes);
      if (response.data.status === 'success') {
        toast.success('Request approved');
        fetchApprovals();
      }
    } catch (err) {
      toast.error('Failed to approve request');
    }
  };

  const handleReject = async (id, notes) => {
    try {
      const response = await approvalsApi.reject(id, notes);
      if (response.data.status === 'success') {
        toast.success('Request rejected');
        fetchApprovals();
      }
    } catch (err) {
      toast.error('Failed to reject request');
    }
  };

  if (!isOpen) return null;

  const displayedApprovals = activeTab === 'pending' ? approvals : myRequests;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-2xl mx-4 max-h-[80vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Approval Workflow</h2>
              <p className="text-xs text-slate-400">
                {isManager ? 'Review and manage approval requests' : 'View your approval requests'}
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

        {/* Tabs */}
        <div className="flex border-b border-slate-700">
          {isManager && (
            <button
              onClick={() => setActiveTab('pending')}
              className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === 'pending'
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Pending Approvals ({approvals.length})
            </button>
          )}
          <button
            onClick={() => setActiveTab('my-requests')}
            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
              activeTab === 'my-requests'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            My Requests ({myRequests.length})
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-32 bg-slate-800 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : displayedApprovals.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
              <p className="text-slate-400">
                {activeTab === 'pending' 
                  ? 'No pending approvals' 
                  : 'You have no approval requests'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {displayedApprovals.map(approval => (
                <ApprovalCard
                  key={approval.id}
                  approval={approval}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  canDecide={isManager && activeTab === 'pending'}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ApprovalPanel;
