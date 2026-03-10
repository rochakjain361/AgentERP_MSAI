/**
 * Chat Input Component
 */
import React, { useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export const ChatInput = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading, 
  placeholder = "Ask anything about your ERP..." 
}) => {
  const inputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="flex gap-3 items-end">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isLoading}
        className="flex-1 px-4 py-3 rounded-xl bg-muted border border-border focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
        data-testid="chat-input"
      />
      <button
        onClick={onSend}
        disabled={!value.trim() || isLoading}
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
  );
};

export default ChatInput;
