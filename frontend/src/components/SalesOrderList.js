/**
 * Sales Order List Component - Shows and manages sales orders with approval status
 */
import React, { useState, useEffect } from 'react';
import { CheckCircle, Clock, AlertCircle, ArrowRight, XCircle } from 'lucide-react';
import { approvalsApi } from '../lib/api';

const SalesOrderList = ({ user }) => {
  const [approvals, setPendingApprovals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedApproval, setSelectedApproval] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [user?.role]);

  const fetchApprovals = async () => {
    try {
      if (user?.role === 'manager' || user?.role === 'admin') {
        const result = await approvalsApi.getPending();
        setPendingApprovals(result.data?.approvals || []);
      }
    } catch (error) {
      console.error('Failed to fetch approvals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (approvalId) => {
    setProcessingId(approvalId);
    try {
      await approvalsApi.approve(approvalId, 'Approved - Order meets requirements');
      setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
      setSelectedApproval(null);
    } catch (error) {
      alert('Failed to approve: ' + error.message);
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (approvalId) => {
    setProcessingId(approvalId);
    try {
      await approvalsApi.reject(approvalId, 'Rejected - Customer credit limit exceeded');
      setPendingApprovals(prev => prev.filter(a => a.id !== approvalId));
      setSelectedApproval(null);
    } catch (error) {
      alert('Failed to reject: ' + error.message);
    } finally {
      setProcessingId(null);
    }
  };

  if (!user || (user.role !== 'manager' && user.role !== 'admin')) {
    return null;
  }

  const pendingCount = approvals.filter(a => a.status === 'pending').length;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700 bg-gradient-to-r from-blue-500/10 to-cyan-500/10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
            <AlertCircle className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="text-white font-semibold">Sales Orders</h3>
            <p className="text-xs text-slate-400">{pendingCount} pending approvals</p>
          </div>
        </div>
        <div className="bg-blue-500/20 border border-blue-500/30 px-3 py-1 rounded-full">
          <span className="text-sm font-semibold text-blue-300">{pendingCount} pending</span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin">
              <Clock className="w-6 h-6 text-slate-500" />
            </div>
            <p className="text-slate-400 text-sm mt-2">Loading orders...</p>
          </div>
        ) : approvals.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="w-8 h-8 text-green-500/50 mx-auto mb-2" />
            <p className="text-slate-400 text-sm">No pending orders</p>
          </div>
        ) : (
          <div className="space-y-2">
            {approvals.map((approval) => (
              <div
                key={approval.id}
                onClick={() => setSelectedApproval(approval)}
                className={`p-3 rounded-lg border transition-all cursor-pointer ${
                  selectedApproval?.id === approval.id
                    ? 'bg-slate-700 border-blue-500/50'
                    : 'bg-slate-700/50 border-slate-600 hover:border-slate-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-white">
                        {approval.resource_data?.customer || 'Unknown Customer'}
                      </span>
                      <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                        Pending
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 mb-2">
                      Order Value: <span className="text-white font-semibold">₹{approval.resource_data?.grand_total?.toLocaleString()}</span>
                    </div>
                    <div className="text-xs text-slate-500">
                      {approval.reason}
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-400 flex-shrink-0 ml-2" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail View */}
      {selectedApproval && (
        <div className="border-t border-slate-700 bg-slate-700/30 p-4 space-y-4">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-slate-400 text-xs">From</div>
              <div className="text-white font-medium mt-1">{selectedApproval.requester_email}</div>
            </div>
            <div>
              <div className="text-slate-400 text-xs">Created</div>
              <div className="text-white font-medium mt-1">
                {new Date(selectedApproval.requested_at).toLocaleDateString()}
              </div>
            </div>
          </div>

          <div>
            <div className="text-slate-400 text-xs mb-1">Order Details</div>
            <div className="bg-slate-800 rounded p-2 text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Order ID:</span>
                <span className="text-white">{selectedApproval.order_id?.substring(0, 8)}...</span>
              </div>
              {selectedApproval.resource_data?.items?.map((item, idx) => (
                <div key={idx} className="flex justify-between">
                  <span className="text-slate-400">{item.item_name}:</span>
                  <span className="text-white">₹{(item.qty * item.rate).toLocaleString()}</span>
                </div>
              ))}
              <div className="border-t border-slate-700 pt-1 mt-1 flex justify-between font-semibold">
                <span className="text-slate-300">Total:</span>
                <span className="text-blue-400">₹{selectedApproval.resource_data?.grand_total?.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => handleApprove(selectedApproval.id)}
              disabled={processingId === selectedApproval.id}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-green-500/20 border border-green-500/30 hover:bg-green-500/30 text-green-400 font-medium disabled:opacity-50"
            >
              <CheckCircle className="w-4 h-4" />
              Approve
            </button>
            <button
              onClick={() => handleReject(selectedApproval.id)}
              disabled={processingId === selectedApproval.id}
              className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-red-500/20 border border-red-500/30 hover:bg-red-500/30 text-red-400 font-medium disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" />
              Reject
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesOrderList;
