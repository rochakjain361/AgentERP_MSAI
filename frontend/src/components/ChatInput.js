/**
 * Chat Input Component with role-based restrictions
 */
import React, { useRef, useEffect } from 'react';
import { Send, Loader2, AlertTriangle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export const ChatInput = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading, 
  placeholder = "Ask anything about your ERP...",
  disabled = false
}) => {
  const inputRef = useRef(null);
  const { user, isAuthenticated } = useAuth();
  
  // Check if user is a viewer (Level 3)
  const isViewer = user?.role === 'viewer';

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Show different placeholder based on auth state and role
  const getPlaceholder = () => {
    if (!isAuthenticated) {
      return "Sign in to start chatting...";
    }
    if (isViewer) {
      return "View-only mode: You can view data but cannot create/edit...";
    }
    return placeholder;
  };

  return (
    <div className="space-y-2">
      {/* Viewer warning */}
      {isAuthenticated && isViewer && (
        <div className="flex items-center gap-2 px-3 py-2 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>
            <strong>Level 3 (Viewer):</strong> You can view data and run queries, but cannot create, edit, or delete records.
          </span>
        </div>
      )}
      
      <div className="flex gap-3 items-end">
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={getPlaceholder()}
          disabled={isLoading || disabled || !isAuthenticated}
          className={`flex-1 px-4 py-3 rounded-xl bg-muted border border-border focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all ${
            isViewer ? 'border-amber-500/30' : ''
          } ${!isAuthenticated ? 'opacity-50' : ''}`}
          data-testid="chat-input"
        />
        <button
          onClick={onSend}
          disabled={!value.trim() || isLoading || disabled || !isAuthenticated}
          className="p-3 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center"
          data-testid="send-message-btn"
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
