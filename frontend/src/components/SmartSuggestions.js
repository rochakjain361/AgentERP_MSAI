/**
 * Smart Suggestions Component
 */
import React from 'react';

export const SmartSuggestions = ({ suggestions, onSelect }) => {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {suggestions.map((suggestion, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(suggestion.prompt)}
          className="flex items-center gap-2 px-3 py-1.5 text-xs bg-muted/50 border border-border rounded-full hover:bg-muted transition-colors"
          data-testid={`smart-suggestion-${idx}`}
        >
          <span>{suggestion.icon}</span>
          <span>{suggestion.text}</span>
        </button>
      ))}
    </div>
  );
};

export default SmartSuggestions;
