/**
 * Proactive Insights Component - Shows AI-generated suggestions
 */
import React, { useState, useEffect } from 'react';
import { 
  Lightbulb, AlertTriangle, TrendingUp, Clock, DollarSign, 
  Users, ShoppingCart, FileText, ChevronRight, X, Sparkles,
  CheckCircle, XCircle
} from 'lucide-react';
import { insightsApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const priorityColors = {
  high: 'from-red-500/20 to-orange-500/20 border-red-500/30',
  medium: 'from-yellow-500/20 to-amber-500/20 border-yellow-500/30',
  low: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30'
};

const priorityBadge = {
  high: 'bg-red-500/20 text-red-300 border-red-500/30',
  medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  low: 'bg-blue-500/20 text-blue-300 border-blue-500/30'
};

const typeIcons = {
  pending_approval: CheckCircle,
  high_value_orders: DollarSign,
  delayed_orders: Clock,
  low_inventory: ShoppingCart,
  overdue_invoices: FileText,
  new_opportunities: Users
};

const InsightCard = ({ insight, onAction }) => {
  const Icon = typeIcons[insight.type] || Lightbulb;
  
  return (
    <div className={`bg-gradient-to-br ${priorityColors[insight.priority]} border rounded-lg p-4 hover:scale-[1.02] transition-transform`}>
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center shrink-0">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-white font-medium text-sm truncate">{insight.title}</h4>
            <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded border ${priorityBadge[insight.priority]}`}>
              {insight.priority.toUpperCase()}
            </span>
          </div>
          <p className="text-slate-400 text-xs mb-2">{insight.context}</p>
          <p className="text-slate-500 text-xs mb-3">{insight.reason}</p>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {insight.affected_count > 0 && (
                <span className="text-xs text-slate-400">
                  {insight.affected_count} item{insight.affected_count !== 1 ? 's' : ''}
                </span>
              )}
              {insight.potential_value > 0 && (
                <span className="text-xs text-green-400">
                  ₹{insight.potential_value.toLocaleString()}
                </span>
              )}
            </div>
            <button
              onClick={() => onAction(insight)}
              className="flex items-center gap-1 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-xs font-medium rounded-lg transition-colors"
            >
              {insight.action_label}
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const ProactiveInsights = ({ onActionClick, isExpanded = false, onToggle }) => {
  const { isAuthenticated, user } = useAuth();
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsights = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        const response = await insightsApi.getInsights();
        if (response.data.status === 'success') {
          setInsights(response.data.insights || []);
        }
      } catch (err) {
        console.error('Failed to fetch insights:', err);
        setError('Failed to load insights');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
    // Refresh insights every 5 minutes
    const interval = setInterval(fetchInsights, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  if (!isAuthenticated) return null;

  if (loading) {
    return (
      <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 animate-pulse">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-5 h-5 bg-slate-700 rounded" />
          <div className="w-32 h-4 bg-slate-700 rounded" />
        </div>
        <div className="space-y-2">
          <div className="w-full h-20 bg-slate-700 rounded" />
          <div className="w-full h-20 bg-slate-700 rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/30 text-red-400 text-sm">
        {error}
      </div>
    );
  }

  if (insights.length === 0) {
    return (
      <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/30">
        <div className="flex items-center gap-2 text-green-400">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm font-medium">All caught up!</span>
        </div>
        <p className="text-xs text-green-300/70 mt-1">
          No urgent items require your attention
        </p>
      </div>
    );
  }

  const displayedInsights = isExpanded ? insights : insights.slice(0, 2);

  return (
    <div className="bg-slate-800/30 rounded-lg border border-slate-700">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
            <Sparkles className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-sm font-medium text-white">Proactive Insights</span>
          <span className="px-1.5 py-0.5 text-[10px] bg-amber-500/20 text-amber-300 rounded-full border border-amber-500/30">
            {insights.length}
          </span>
        </div>
        {insights.length > 2 && (
          <button
            onClick={onToggle}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            {isExpanded ? 'Show less' : `+${insights.length - 2} more`}
          </button>
        )}
      </div>

      {/* Insights List */}
      <div className="p-3 space-y-2">
        {displayedInsights.map((insight) => (
          <InsightCard 
            key={insight.id} 
            insight={insight} 
            onAction={onActionClick}
          />
        ))}
      </div>
    </div>
  );
};

export default ProactiveInsights;
