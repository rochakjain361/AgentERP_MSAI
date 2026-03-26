/**
 * Chat Messages Component
 */
import React, { useRef, useEffect } from 'react';
import { ERPWidget } from './ERPWidgets';
import StopSalesDecisionWidget from './StopSalesDecisionWidget';
import { CheckCircle } from 'lucide-react';

// Action Confirmation Widget - shows after action completes
const ActionConfirmationWidget = ({ data }) => {
  const { action, customer, annualized_risk, result } = data;
  
  return (
    <div className="bg-white border border-green-200 rounded-xl p-4 mt-3 shadow-sm" data-testid="action-confirmation-widget">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
          <CheckCircle className="w-5 h-5 text-green-600" />
        </div>
        <div className="flex-1">
          <p className="font-medium text-gray-900">
            {action === 'stop_sales' 
              ? `Future sales blocked for ${customer}` 
              : `Senior management review scheduled for ${customer}`}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {result?.message || 'Action completed successfully'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            This action has been logged to the audit trail.
            {action === 'stop_sales' && ` Annualized revenue impact: ₹${annualized_risk?.toLocaleString()}`}
          </p>
        </div>
      </div>
    </div>
  );
};

export const ChatMessages = ({ messages, isLoading, onStopSalesActionComplete }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.length === 0 && (
        <div className="text-center py-12" data-testid="welcome-message">
          <h2 className="text-2xl font-semibold mb-2" style={{ fontFamily: 'Manrope, sans-serif' }}>
            Welcome to AgentERP
          </h2>
          <p className="text-muted-foreground">
            Your AI-powered ERP assistant. Ask me anything about your business data!
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {[
              'Show me the dashboard',
              'List recent sales orders',
              'Check customer Grant Plastics Ltd.',
              'Create a new sales order'
            ].map((suggestion, idx) => (
              <span
                key={idx}
                className="px-3 py-1 text-sm bg-muted rounded-full text-muted-foreground"
              >
                "{suggestion}"
              </span>
            ))}
          </div>
        </div>
      )}
      
      {messages.map((msg, idx) => (
        <div 
          key={idx} 
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          data-testid={`chat-message-${idx}`}
        >
          <div className={`max-w-[85%] ${msg.role === 'user' ? 'order-2' : ''}`}>
            {/* Regular text content */}
            {msg.content && (
              <div 
                className={`rounded-2xl px-4 py-2 ${
                  msg.role === 'user' 
                    ? 'bg-primary text-primary-foreground ml-auto'
                    : 'bg-muted'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              </div>
            )}
            
            {/* Standard ERP Widget */}
            {msg.type === 'widget' && msg.widget_data && (
              <ERPWidget data={msg.widget_data} />
            )}
            
            {/* Stop Sales Decision Widget - Multi-step AI workflow */}
            {msg.type === 'stop_sales_decision' && msg.decision_data && (
              <StopSalesDecisionWidget 
                data={msg.decision_data}
                onActionComplete={onStopSalesActionComplete}
              />
            )}
            
            {/* Action Confirmation Widget */}
            {msg.type === 'action_confirmation' && msg.confirmation_data && (
              <ActionConfirmationWidget data={msg.confirmation_data} />
            )}
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-muted rounded-2xl px-4 py-2">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-foreground/30 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatMessages;
