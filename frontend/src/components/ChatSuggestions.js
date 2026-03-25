/**
 * Chat Suggestions Component - Light theme with dark text
 */
import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowRight, FileText, Plus, Clock, BarChart3, Building2, Zap } from 'lucide-react';
import { insightsApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const iconMap = {
  '📋': FileText,
  '➕': Plus,
  '⏳': Clock,
  '📊': BarChart3,
  '🏢': Building2,
};

const priorityStyles = {
  high: {
    card: 'bg-white border-red-200 hover:border-red-400 hover:shadow-md',
    icon: 'from-red-500 to-orange-500',
  },
  medium: {
    card: 'bg-white border-amber-200 hover:border-amber-400 hover:shadow-md',
    icon: 'from-amber-500 to-yellow-500',
  },
  low: {
    card: 'bg-white border-gray-200 hover:border-blue-400 hover:shadow-md',
    icon: 'from-blue-500 to-cyan-500',
  },
};

const SuggestionCard = ({ suggestion, onClick }) => {
  const Icon = iconMap[suggestion.icon] || Zap;
  const styles = priorityStyles[suggestion.priority] || priorityStyles.low;
  
  return (
    <button
      onClick={() => onClick(suggestion.prompt)}
      className={`group flex items-start gap-3 p-4 rounded-xl border-2 transition-all duration-200 ${styles.card}`}
      data-testid={`suggestion-${suggestion.type}`}
    >
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${styles.icon} flex items-center justify-center shadow-md flex-shrink-0`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      
      <div className="flex-1 text-left min-w-0">
        <p className="text-sm font-semibold text-gray-900 leading-tight mb-1">
          {suggestion.text}
        </p>
        <p className="text-xs text-gray-500">
          Click to ask
        </p>
      </div>
      
      <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 self-center">
        <ArrowRight className="w-3 h-3 text-gray-600" />
      </div>
    </button>
  );
};

const ChatSuggestions = ({ onSuggestionClick, className = "" }) => {
  const { isAuthenticated, user } = useAuth();
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        const response = await insightsApi.getSuggestions();
        if (response.data.status === 'success') {
          setSuggestions(response.data.suggestions || []);
        }
      } catch (err) {
        console.error('Failed to fetch suggestions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
    const interval = setInterval(fetchSuggestions, 3 * 60 * 1000);
    return () => clearInterval(interval);
  }, [isAuthenticated, user?.id]);

  if (!isAuthenticated || loading || suggestions.length === 0) {
    return null;
  }

  return (
    <div className={`${className}`}>
      <div className="flex items-center justify-center gap-3 mb-5">
        <div className="h-px flex-1 bg-gray-200" />
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100 border border-gray-200">
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          <span className="text-xs font-medium text-gray-700">Suggested for you</span>
          {user?.company && (
            <>
              <span className="text-gray-400">•</span>
              <span className="text-xs text-gray-500">{user.company}</span>
            </>
          )}
        </div>
        <div className="h-px flex-1 bg-gray-200" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {suggestions.map((suggestion) => (
          <SuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            onClick={onSuggestionClick}
          />
        ))}
      </div>
    </div>
  );
};

export default ChatSuggestions;
