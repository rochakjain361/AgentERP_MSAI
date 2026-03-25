/**
 * Business Impact Component - Shows time/cost savings metrics
 */
import React, { useState, useEffect } from 'react';
import { TrendingUp, Clock, DollarSign, Zap, BarChart3 } from 'lucide-react';
import { insightsApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const MetricCard = ({ icon: Icon, label, value, subtext, color }) => (
  <div className={`bg-gradient-to-br ${color} border rounded-lg p-3`}>
    <div className="flex items-center gap-2 mb-1">
      <Icon className="w-4 h-4 text-white/80" />
      <span className="text-xs text-white/70">{label}</span>
    </div>
    <div className="text-xl font-bold text-white">{value}</div>
    {subtext && <div className="text-xs text-white/60 mt-0.5">{subtext}</div>}
  </div>
);

const BusinessImpact = ({ compact = false }) => {
  const { isAuthenticated } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        const response = await insightsApi.getBusinessImpact();
        if (response.data.status === 'success') {
          setMetrics(response.data);
        }
      } catch (err) {
        console.error('Failed to fetch business impact:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, [isAuthenticated]);

  if (!isAuthenticated || loading) {
    return null;
  }

  if (!metrics) return null;

  const { metrics: m, summary: s } = metrics;

  if (compact) {
    return (
      <div className="flex items-center justify-center gap-6 py-2 px-4 rounded-lg bg-gray-50 border border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
            <TrendingUp className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="text-sm font-medium text-emerald-700">{s.headline}</span>
        </div>
        <div className="h-4 w-px bg-gray-300" />
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Clock className="w-3.5 h-3.5" />
          <span>{s.time_saved}</span>
        </div>
        <div className="h-4 w-px bg-gray-300" />
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <DollarSign className="w-3.5 h-3.5" />
          <span>{s.cost_saved}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/30 rounded-lg border border-slate-700">
      {/* Header */}
      <div className="flex items-center gap-2 p-3 border-b border-slate-700">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center">
          <BarChart3 className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="text-sm font-medium text-white">Business Impact</span>
      </div>

      {/* Metrics Grid */}
      <div className="p-3 grid grid-cols-2 gap-2">
        <MetricCard
          icon={Zap}
          label="Efficiency"
          value={s.headline}
          subtext={`${m.agent_time_per_action_mins} min vs ${m.manual_time_per_action_mins} min`}
          color="from-blue-500/20 to-cyan-500/20 border-blue-500/30"
        />
        <MetricCard
          icon={Clock}
          label="Time Saved"
          value={s.time_saved}
          subtext={`${m.time_saved_today_mins} mins today`}
          color="from-purple-500/20 to-violet-500/20 border-purple-500/30"
        />
        <MetricCard
          icon={DollarSign}
          label="Cost Savings"
          value={s.cost_saved}
          subtext={`@₹${m.cost_per_hour_inr}/hour`}
          color="from-emerald-500/20 to-green-500/20 border-emerald-500/30"
        />
        <MetricCard
          icon={TrendingUp}
          label="Actions"
          value={m.total_actions_month}
          subtext={`${m.total_actions_today} today`}
          color="from-amber-500/20 to-orange-500/20 border-amber-500/30"
        />
      </div>

      {/* Projection Note */}
      <div className="px-3 pb-3">
        <div className="text-xs text-slate-500 bg-slate-800/50 rounded p-2">
          <span className="text-slate-400">Projection:</span> Based on {m.estimated_monthly_actions} monthly actions
        </div>
      </div>
    </div>
  );
};

export default BusinessImpact;
