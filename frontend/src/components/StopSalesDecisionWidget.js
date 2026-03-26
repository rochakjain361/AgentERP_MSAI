/**
 * StopSalesDecisionWidget - Multi-step AI decision workflow for Stop Future Sales
 * 
 * This widget is rendered in chat when a user initiates "Stop Future Sales" action.
 * It shows consequence awareness, annualized revenue at risk, and decision options.
 */
import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Ban, 
  Users, 
  CheckCircle,
  Loader2,
  TrendingDown,
  Calendar
} from 'lucide-react';
import { aiAnalysisApi } from '../lib/api';
import { toast } from 'sonner';

// Confirmation Modal
const ConfirmationModal = ({ action, customer, details, onConfirm, onCancel, loading }) => (
  <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
          action === 'stop_sales' ? 'bg-red-100' : 'bg-blue-100'
        }`}>
          {action === 'stop_sales' ? (
            <Ban className="w-5 h-5 text-red-600" />
          ) : (
            <Users className="w-5 h-5 text-blue-600" />
          )}
        </div>
        <h3 className="text-lg font-semibold text-gray-900">
          {action === 'stop_sales' ? 'Confirm: Stop Future Sales' : 'Confirm: Schedule Review'}
        </h3>
      </div>
      
      <p className="text-gray-700 mb-2">
        {action === 'stop_sales' ? (
          <>Are you sure you want to <span className="font-semibold text-red-600">block all future sales</span> for <span className="font-semibold">{customer}</span>?</>
        ) : (
          <>Schedule a <span className="font-semibold text-blue-600">Senior Management Review</span> for <span className="font-semibold">{customer}</span>?</>
        )}
      </p>
      
      <div className="text-sm text-gray-500 mb-4 p-3 bg-gray-50 rounded-lg">
        {action === 'stop_sales' ? (
          <>
            <p className="mb-1"><strong>Impact:</strong> Customer will be unable to place new orders</p>
            <p><strong>Revenue at Risk:</strong> <span className="text-red-600 font-semibold">{details.annualizedRisk}</span></p>
          </>
        ) : (
          <>
            <p className="mb-1"><strong>Action:</strong> Senior management will be notified</p>
            <p><strong>Review will cover:</strong> Payment history, risk assessment, relationship value</p>
          </>
        )}
      </div>
      
      <div className="flex gap-3">
        <button
          onClick={onCancel}
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={loading}
          className={`flex-1 px-4 py-2 text-white rounded-lg font-medium flex items-center justify-center gap-2 ${
            action === 'stop_sales' 
              ? 'bg-red-600 hover:bg-red-700' 
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            'Confirm'
          )}
        </button>
      </div>
    </div>
  </div>
);

const StopSalesDecisionWidget = ({ data, onActionComplete }) => {
  const [selectedAction, setSelectedAction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [completedAction, setCompletedAction] = useState(null);
  
  const { customer, amount_due, order_id, annualized_risk } = data;
  
  const formattedAnnualizedRisk = `₹${annualized_risk?.toLocaleString() || (amount_due * 15).toLocaleString()}`;
  
  const handleActionClick = (action) => {
    setSelectedAction(action);
  };
  
  const handleConfirm = async () => {
    setLoading(true);
    
    try {
      // Call backend to execute the action
      const response = await aiAnalysisApi.executeAction(
        selectedAction,
        customer,
        order_id
      );
      
      if (response.data.status === 'success') {
        setCompleted(true);
        setCompletedAction(selectedAction);
        
        // Notify parent to add confirmation message
        if (onActionComplete) {
          onActionComplete({
            action: selectedAction,
            customer,
            amount_due,
            annualized_risk: annualized_risk || amount_due * 15,
            result: response.data.result
          });
        }
        
        toast.success(response.data.result?.message || 'Action completed successfully');
      } else {
        toast.error(response.data.message || 'Action failed');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to execute action');
    } finally {
      setLoading(false);
      setSelectedAction(null);
    }
  };
  
  // Show completed state
  if (completed) {
    return (
      <div className="bg-white border border-green-200 rounded-xl p-4 mt-3 shadow-sm" data-testid="stop-sales-completed">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="font-medium text-gray-900">
              {completedAction === 'stop_sales' 
                ? 'Future sales blocked' 
                : 'Senior management review scheduled'}
            </p>
            <p className="text-sm text-gray-500">Action logged to audit trail for {customer}</p>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="bg-white border border-red-200 rounded-xl overflow-hidden mt-3 shadow-sm" data-testid="stop-sales-decision-widget">
      {/* Header */}
      <div className="bg-red-50 px-4 py-3 border-b border-red-200">
        <div className="flex items-center gap-2 text-red-700">
          <AlertTriangle className="w-5 h-5" />
          <span className="font-semibold">High-Impact Action Required</span>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-4">
        {/* Warning Message */}
        <div className="mb-4">
          <p className="text-gray-800 mb-3">
            You are about to take a <strong>major action</strong> that could significantly impact your business relationship with <strong className="text-red-600">{customer}</strong>.
          </p>
          
          {/* Annualized Risk Card */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <div className="text-xs text-red-600 uppercase tracking-wide font-medium">Estimated Annualized Revenue at Risk</div>
                <div className="text-2xl font-bold text-red-700">{formattedAnnualizedRisk}</div>
                <div className="text-xs text-gray-500">Based on current outstanding: ₹{amount_due?.toLocaleString()}</div>
              </div>
            </div>
          </div>
          
          <p className="text-gray-600 text-sm">
            Stopping future sales reduces immediate risk but may impact future revenue from this customer. 
            Consider the long-term relationship value before proceeding.
          </p>
        </div>
        
        {/* Decision Options */}
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-700">Choose your next step:</p>
          
          {/* Option 1: Proceed to Stop */}
          <button
            onClick={() => handleActionClick('stop_sales')}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border-2 border-red-200 bg-red-50 hover:bg-red-100 hover:border-red-300 transition-all text-left"
            data-testid="proceed-stop-sales-btn"
          >
            <div className="w-10 h-10 rounded-full bg-red-200 flex items-center justify-center flex-shrink-0">
              <Ban className="w-5 h-5 text-red-700" />
            </div>
            <div className="flex-1">
              <div className="font-medium text-red-700">Proceed to Stop Future Sales</div>
              <div className="text-xs text-red-600">Block all new orders for this customer immediately</div>
            </div>
          </button>
          
          {/* Option 2: Schedule Review */}
          <button
            onClick={() => handleActionClick('schedule_management_review')}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg border-2 border-blue-200 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 transition-all text-left"
            data-testid="schedule-review-btn"
          >
            <div className="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center flex-shrink-0">
              <Calendar className="w-5 h-5 text-blue-700" />
            </div>
            <div className="flex-1">
              <div className="font-medium text-blue-700">Schedule Senior Management Review</div>
              <div className="text-xs text-blue-600">Escalate decision to management for collective review</div>
            </div>
          </button>
        </div>
      </div>
      
      {/* Confirmation Modal */}
      {selectedAction && (
        <ConfirmationModal
          action={selectedAction}
          customer={customer}
          details={{ annualizedRisk: formattedAnnualizedRisk }}
          onConfirm={handleConfirm}
          onCancel={() => setSelectedAction(null)}
          loading={loading}
        />
      )}
    </div>
  );
};

export default StopSalesDecisionWidget;
