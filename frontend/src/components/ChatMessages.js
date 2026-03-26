/**
 * Chat Messages Component
 */
import React, { useRef, useEffect } from 'react';
import { ERPWidget } from './ERPWidgets';

export const ChatMessages = ({ messages, isLoading }) => {
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
              'Show me all customers',
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
            <div 
              className={`rounded-2xl px-4 py-2 ${
                msg.role === 'user' 
                  ? 'bg-primary text-primary-foreground ml-auto'
                  : 'bg-muted'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
            </div>
            {msg.type === 'widget' && msg.widget_data && (
              <ERPWidget data={msg.widget_data} />
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
