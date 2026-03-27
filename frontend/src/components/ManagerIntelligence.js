/**
 * ManagerIntelligence - Business Health Dashboard for strategic decision-making
 * 
 * Uses Azure AI Foundry Agent to analyze real ERP data and provide:
 * - Monthly business health score
 * - Strategic risks and opportunities
 * - Revenue and payment health metrics
 * - Operational efficiency insights
 * - Actionable recommendations for long-term health
 */
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Brain, 
  RefreshCw, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  Lightbulb,
  CheckCircle2,
  XCircle,
  Clock,
  Building2,
  BarChart3,
  Zap
} from 'lucide-react';
import { intelligenceApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const severityColors = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  medium: 'bg-amber-100 text-amber-700 border-amber-200',
  low: 'bg-blue-100 text-blue-700 border-blue-200',
  info: 'bg-gray-100 text-gray-700 border-gray-200'
};

const HealthScoreGauge = ({ score }) => {
  const getColor = () => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };
  
  const getLabel = () => {
    if (score >= 80) return 'Healthy';
    if (score >= 60) return 'Needs Attention';
    return 'Critical';
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white rounded-xl border border-gray-200">
      <div className="text-sm text-gray-500 mb-2">Monthly Business Resilience Index</div>
      <div className={`text-5xl font-bold ${getColor()}`}>{score}</div>
      <div className={`text-sm font-medium ${getColor()} mt-1`}>{getLabel()}</div>
      <div className="w-full h-2 bg-gray-200 rounded-full mt-4">
        <div 
          className={`h-full rounded-full transition-all duration-500 ${
            score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-amber-500' : 'bg-red-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
};

const FindingCard = ({ finding }) => (
  <div className={`p-4 rounded-lg border ${severityColors[finding.severity] || severityColors.info}`}>
    <div className="flex items-start gap-3">
      <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-medium">{finding.finding}</p>
        <p className="text-sm opacity-80 mt-1">Impact: {finding.impact}</p>
      </div>
    </div>
  </div>
);

const RiskCard = ({ risk }) => (
  <div className="p-4 bg-red-50 rounded-lg border border-red-200">
    <div className="flex items-start gap-3">
      <Shield className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-medium text-red-900">{risk.risk}</p>
        <p className="text-sm text-red-700 mt-1">Probability: {risk.probability}</p>
        <p className="text-sm text-red-600 mt-2">
          <span className="font-medium">Mitigation:</span> {risk.mitigation}
        </p>
      </div>
    </div>
  </div>
);

const OpportunityCard = ({ opportunity }) => (
  <div className="p-4 bg-green-50 rounded-lg border border-green-200">
    <div className="flex items-start gap-3">
      <Lightbulb className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-medium text-green-900">{opportunity.opportunity}</p>
        <p className="text-sm text-green-700 mt-1">Potential: {opportunity.potential_value}</p>
        <p className="text-sm text-green-600 mt-2">
          <span className="font-medium">Action:</span> {opportunity.action}
        </p>
      </div>
    </div>
  </div>
);

const RecommendationCard = ({ recommendation, index }) => (
  <div className="flex items-start gap-4 p-4 bg-white rounded-lg border border-gray-200">
    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
      index === 0 ? 'bg-blue-600' : index === 1 ? 'bg-blue-500' : 'bg-blue-400'
    }`}>
      {recommendation.priority || index + 1}
    </div>
    <div className="flex-1">
      <p className="font-medium text-gray-900">{recommendation.action}</p>
      <p className="text-sm text-gray-600 mt-1">Expected: {recommendation.expected_outcome}</p>
    </div>
  </div>
);

const ManagerIntelligence = ({ onClose }) => {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchIntelligence = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await intelligenceApi.getDashboard();
      if (response.data.status === 'success') {
        setData(response.data);
      } else {
        setError(response.data.message || 'Failed to load business health dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load business health dashboard');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIntelligence();
  }, [fetchIntelligence]);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 flex flex-col items-center gap-4 max-w-md">
          <div className="w-16 h-16 relative">
            <Brain className="w-16 h-16 text-blue-600" />
            <div className="absolute inset-0 animate-ping">
              <Brain className="w-16 h-16 text-blue-400 opacity-50" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">Analyzing Monthly Business Health Report</h3>
          <p className="text-gray-600 text-center">
            Leveraging Azure AI to provide strategic insights and actionable recommendations for your business.
          </p>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span>Collecting trend, risk, and resilience indicators</span>
          </div>
        </div>
      </div>
    );
  }

  const analysis = data?.ai_analysis || {};
  const summary = data?.data_summary?.summary || {};

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-50 rounded-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <Brain className="w-6 h-6 text-blue-600" />
              Business Health Intelligence Dashboard
            </h2>
            <p className="text-sm text-gray-500 mt-1 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-500" />
              Long-horizon guidance powered by {data?.using_agent ? 'Azure AI Foundry Agent' : 'Azure OpenAI GPT-4o'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {data?.company && (
              <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm flex items-center gap-1">
                <Building2 className="w-4 h-4" />
                {data.company}
              </span>
            )}
            <button
              onClick={fetchIntelligence}
              disabled={loading}
              className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
              title="Refresh Analysis"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800"
            >
              Close
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {error ? (
            <div className="flex flex-col items-center justify-center h-64">
              <XCircle className="w-12 h-12 text-red-500 mb-4" />
              <p className="text-red-600 font-medium">{error}</p>
              <button
                onClick={fetchIntelligence}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-6">
              {/* Left Column - Health & Summary */}
              <div className="space-y-6">
                {/* Health Score */}
                <HealthScoreGauge score={analysis.health_score || 70} />
                
                {/* Data Summary */}
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" />
                    Data Analyzed
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{summary.total_orders || 0}</div>
                      <div className="text-xs text-gray-500">Orders</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{summary.total_invoices || 0}</div>
                      <div className="text-xs text-gray-500">Invoices</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-gray-900">₹{((summary.total_order_value || 0) / 1000).toFixed(0)}K</div>
                      <div className="text-xs text-gray-500">Order Value</div>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-lg font-bold text-amber-600">₹{((summary.total_outstanding || 0) / 1000).toFixed(0)}K</div>
                      <div className="text-xs text-gray-500">Outstanding</div>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                    <span>{data?.metrics?.data_points_analyzed || 0} data points</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Just now
                    </span>
                  </div>
                </div>
              </div>

              {/* Middle Column - Executive Summary & Findings */}
              <div className="space-y-6">
                {/* Executive Summary */}
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Target className="w-4 h-4" />
                    Executive Summary
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {analysis.executive_summary || 'Analysis in progress...'}
                  </p>
                </div>

                {/* Key Findings */}
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Key Findings
                  </h3>
                  <div className="space-y-3">
                    {(analysis.key_findings || []).length > 0 ? (
                      analysis.key_findings.map((finding, idx) => (
                        <FindingCard key={idx} finding={finding} />
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No critical findings</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column - Recommendations, Risks, Opportunities */}
              <div className="space-y-6">
                {/* Recommendations */}
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600" />
                    Strategic Moves (P2 Horizon)
                  </h3>
                  <div className="space-y-3">
                    {(analysis.recommendations || []).length > 0 ? (
                      analysis.recommendations.slice(0, 4).map((rec, idx) => (
                        <RecommendationCard key={idx} recommendation={rec} index={idx} />
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No recommendations yet</p>
                    )}
                  </div>
                </div>

                {/* Risks & Opportunities */}
                <div className="grid grid-cols-1 gap-4">
                  {(analysis.risks || []).length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <TrendingDown className="w-4 h-4 text-red-600" />
                        Risks
                      </h3>
                      <div className="space-y-3">
                        {analysis.risks.slice(0, 2).map((risk, idx) => (
                          <RiskCard key={idx} risk={risk} />
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {(analysis.opportunities || []).length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-200 p-4">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-green-600" />
                        Opportunities
                      </h3>
                      <div className="space-y-3">
                        {analysis.opportunities.slice(0, 2).map((opp, idx) => (
                          <OpportunityCard key={idx} opportunity={opp} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-white px-6 py-3 border-t border-gray-200 text-center text-xs text-gray-500">
          Monthly Business Health Report generated at {data?.generated_at ? new Date(data.generated_at).toLocaleString() : 'N/A'} • 
          {data?.metrics?.analysis_depth === 'comprehensive' ? ' Long-term trajectory review' : ' Snapshot review'}
        </div>
      </div>
    </div>
  );
};

export default ManagerIntelligence;
