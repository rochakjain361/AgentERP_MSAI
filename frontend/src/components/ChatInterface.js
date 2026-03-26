/**
 * ChatInterface - Main chat interface component (Enterprise Edition)
 * 
 * This is the refactored version that imports from smaller components:
 * - Sidebar: Main navigation sidebar with saved tools
 * - ChatSidebar: Chat history sidebar
 * - CommandPalette: ⌘K command palette
 * - ChatMessages: Message display
 * - ChatInput: Message input
 * - SmartSuggestions: Context-aware suggestions
 * - ERPWidgets: ERP data display components
 * - CreateToolModal: Modal for creating custom tools
 * - ToolResultsView: Display query results from tools
 * - LoginModal: User authentication
 * - ChatSuggestions: Proactive insights as chat suggestions
 * - ApprovalPanel: Approval workflow management
 * - AuditLog: Activity trail viewer
 * - BusinessImpact: Time/cost savings metrics
 */
import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Menu, Command, ExternalLink, Download, Trash2, History, User, LogOut, Shield, Clock, Activity, Building2, Sparkles, Brain } from 'lucide-react';

// Import components
import { Sidebar } from './Sidebar';
import { ChatSidebar } from './ChatSidebar';
import { CommandPalette } from './CommandPalette';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { SmartSuggestions } from './SmartSuggestions';
import { CreateToolModal } from './CreateToolModal';
import { ToolResultsView } from './ToolResultsView';
import LoginModal from './LoginModal';
import ChatSuggestions from './ChatSuggestions';
import ApprovalPanel from './ApprovalPanel';
import AuditLog from './AuditLog';
import BusinessImpact from './BusinessImpact';
import TodaysPriorities from './TodaysPriorities';
import ManagerIntelligence from './ManagerIntelligence';

// Import hooks and context
import { useChat } from '../hooks/useChat';
import { useHealth } from '../hooks/useHealth';
import { useAuth } from '../contexts/AuthContext';

// Import constants and API
import { ERP_BASE_URL } from '../lib/constants';
import { API } from '../lib/api';
import axios from 'axios';

// Role badge colors
const roleBadgeColors = {
  admin: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  manager: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  operator: 'bg-green-500/20 text-green-300 border-green-500/30',
  viewer: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
};

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [showChatHistory, setShowChatHistory] = useState(false);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showCreateToolModal, setShowCreateToolModal] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showApprovalPanel, setShowApprovalPanel] = useState(false);
  const [showAuditLog, setShowAuditLog] = useState(false);
  const [showPriorities, setShowPriorities] = useState(false);
  const [showIntelligence, setShowIntelligence] = useState(false);
  const [toolResult, setToolResult] = useState(null);
  const [isToolLoading, setIsToolLoading] = useState(false);
  
  // Auth context
  const { user, isAuthenticated, logout, isManager, canCreate } = useAuth();
  
  // Custom hooks
  const { erpStatus, checkHealth } = useHealth();
  const {
    messages,
    setMessages,
    chatSessions,
    currentSessionId,
    setCurrentSessionId,
    isLoading,
    smartSuggestions,
    setSmartSuggestions,
    loadChatSessions,
    createNewChat,
    loadSessionMessages,
    deleteChat,
    sendMessage,
  } = useChat();

  // Initialize on mount
  useEffect(() => {
    checkHealth();
  }, []);

  // Reload chat sessions when user changes (login/logout)
  useEffect(() => {
    loadChatSessions();
  }, [isAuthenticated, user?.id]);

  // Load session messages when session changes
  useEffect(() => {
    if (currentSessionId) {
      loadSessionMessages(currentSessionId);
    }
  }, [currentSessionId]);

  // Handle keyboard shortcut for command palette
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(prev => !prev);
      }
      if (e.key === 'Escape') {
        setShowCommandPalette(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Handle Stop Sales Decision workflow - listen for custom event from AIRiskWidget
  useEffect(() => {
    const handleStopSalesDecision = (event) => {
      const { customer, amount_due, days_overdue, order_id, risk_level, reasoning, annualized_risk } = event.detail;
      
      // Add AI message explaining the high-impact action
      const aiDecisionMessage = {
        role: 'assistant',
        content: `I see you're considering stopping future sales for **${customer}**. This is a significant decision that could impact your business relationship.\n\nLet me help you understand the implications and choose the best course of action.`,
        type: 'stop_sales_decision',
        decision_data: {
          customer,
          amount_due,
          days_overdue,
          order_id,
          risk_level,
          reasoning,
          annualized_risk
        },
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiDecisionMessage]);
    };

    window.addEventListener('ai:stop-sales-decision', handleStopSalesDecision);
    return () => window.removeEventListener('ai:stop-sales-decision', handleStopSalesDecision);
  }, [setMessages]);

  // Handle Stop Sales action completion - add confirmation message to chat
  const handleStopSalesActionComplete = useCallback((actionResult) => {
    const { action, customer, amount_due, annualized_risk, result } = actionResult;
    
    // Add AI confirmation message
    const confirmationMessage = {
      role: 'assistant',
      content: action === 'stop_sales'
        ? `I've blocked future sales for **${customer}**. The sales team has been notified and this action has been logged to the audit trail.\n\n**Revenue Impact:** Estimated annualized revenue at risk is ₹${annualized_risk?.toLocaleString()}.\n\nYou may want to schedule a follow-up review in 30 days to reassess the customer relationship.`
        : `I've scheduled a Senior Management Review for **${customer}**. The management team will receive a notification with the complete payment history and risk assessment.\n\nExpect a decision within 2-3 business days.`,
      type: 'action_confirmation',
      confirmation_data: {
        action,
        customer,
        amount_due,
        annualized_risk,
        result
      },
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, confirmationMessage]);
  }, [setMessages]);

  // Handle send message
  const handleSendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;
    
    const currentInput = input;
    setInput('');
    
    // Build conversation history
    const history = messages.slice(-6).map(msg => ({
      role: msg.role === 'user' ? 'user' : 'assistant',
      content: msg.content
    }));
    
    await sendMessage(currentInput, history);
  }, [input, isLoading, messages, sendMessage]);

  // Handle command palette action
  const handleCommandAction = useCallback((action) => {
    setShowCommandPalette(false);
    setInput(action);
    setTimeout(() => {
      document.querySelector('[data-testid="send-message-btn"]')?.click();
    }, 100);
  }, []);

  // Handle analytics button
  const handleAnalytics = useCallback(() => {
    setToolResult(null);
    setInput('Show me comprehensive analytics and insights');
    setTimeout(() => {
      document.querySelector('[data-testid="send-message-btn"]')?.click();
    }, 100);
  }, []);

  // Handle insight/suggestion action from ChatSuggestions
  const handleSuggestionClick = useCallback((prompt) => {
    setInput(prompt);
    setTimeout(() => {
      document.querySelector('[data-testid="send-message-btn"]')?.click();
    }, 100);
  }, []);

  // Handle insight action from old ProactiveInsights (kept for compatibility)
  const handleInsightAction = useCallback((insight) => {
    if (insight.action_type === 'view_approvals') {
      setShowApprovalPanel(true);
    } else if (insight.action_type === 'view_high_value_orders') {
      setInput('Show me high value orders in draft status');
      setTimeout(() => {
        document.querySelector('[data-testid="send-message-btn"]')?.click();
      }, 100);
    } else if (insight.action_type === 'view_draft_orders') {
      setInput('Show me all draft orders');
      setTimeout(() => {
        document.querySelector('[data-testid="send-message-btn"]')?.click();
      }, 100);
    } else if (insight.action_type === 'view_overdue_invoices') {
      setInput('Show me overdue invoices');
      setTimeout(() => {
        document.querySelector('[data-testid="send-message-btn"]')?.click();
      }, 100);
    } else if (insight.action_type === 'view_inactive_customers') {
      setInput('Show me customers without recent orders');
      setTimeout(() => {
        document.querySelector('[data-testid="send-message-btn"]')?.click();
      }, 100);
    }
  }, []);

  // Handle tool run from sidebar
  const handleToolRun = useCallback((result) => {
    setToolResult(result);
  }, []);

  // Handle tool created
  const handleToolCreated = useCallback((tool) => {
    if (window.refreshTools) {
      window.refreshTools();
    }
  }, []);

  // Refresh tool results
  const handleRefreshTool = useCallback(async () => {
    if (!toolResult?.tool_name) return;
    setIsToolLoading(true);
    try {
      const response = await axios.get(`${API}/tools/run/${toolResult.tool_name}`);
      if (response.data.status === 'success') {
        setToolResult(response.data);
        toast.success('Results refreshed');
      }
    } catch (error) {
      toast.error('Failed to refresh');
    } finally {
      setIsToolLoading(false);
    }
  }, [toolResult]);

  // Delete tool from results view
  const handleDeleteToolFromResults = useCallback(async () => {
    if (!toolResult?.tool_name) return;
    if (!window.confirm(`Delete tool "${toolResult.tool_name}"?`)) return;
    
    try {
      const response = await axios.delete(`${API}/tools/${toolResult.tool_name}`);
      if (response.data.status === 'success') {
        setToolResult(null);
        if (window.refreshTools) {
          window.refreshTools();
        }
        toast.success('Tool deleted');
      }
    } catch (error) {
      toast.error('Failed to delete tool');
    }
  }, [toolResult]);

  // Handle session selection
  const handleSelectSession = useCallback((sessionId) => {
    setToolResult(null);
    setCurrentSessionId(sessionId);
    setShowChatHistory(false);
  }, [setCurrentSessionId]);

  // Export chat
  const exportChat = useCallback(() => {
    if (messages.length === 0) {
      toast.info('No messages to export');
      return;
    }
    
    const chatText = messages.map(msg => 
      `[${msg.role.toUpperCase()}]: ${msg.content}`
    ).join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agenterp-chat-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Chat exported!');
  }, [messages]);

  // Clear chat
  const clearChat = useCallback(async () => {
    if (currentSessionId) {
      await deleteChat(currentSessionId);
    }
  }, [currentSessionId, deleteChat]);

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Main Sidebar */}
      <Sidebar 
        erpStatus={erpStatus}
        onSetInput={setInput}
        onAnalytics={handleAnalytics}
        onToolRun={handleToolRun}
        onCreateTool={() => setShowCreateToolModal(true)}
        user={user}
        isAuthenticated={isAuthenticated}
        onShowApprovals={() => setShowApprovalPanel(true)}
        onShowAuditLog={() => setShowAuditLog(true)}
        isManager={isManager}
      />

      {/* Chat History Sidebar */}
      <ChatSidebar
        isOpen={showChatHistory}
        sessions={chatSessions}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onDeleteSession={deleteChat}
        onCreateNew={() => {
          setToolResult(null);
          createNewChat();
        }}
      />

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-border bg-background/50 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setShowChatHistory(prev => !prev)}
              className="md:hidden p-2 hover:bg-muted rounded-lg"
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            {/* AI Intelligence Dashboard - Managers Only */}
            {isAuthenticated && isManager && (
              <button
                onClick={() => setShowIntelligence(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                data-testid="intelligence-btn"
              >
                <Brain className="w-3.5 h-3.5" />
                <span>AI Intelligence</span>
              </button>
            )}

            {/* AI Priorities Button */}
            {isAuthenticated && (
              <button
                onClick={() => setShowPriorities(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg bg-gray-900 text-white hover:bg-gray-800 transition-colors"
                data-testid="priorities-btn"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Priorities</span>
              </button>
            )}

            {/* Enterprise Features Buttons */}
            {isAuthenticated && isManager && (
              <button
                onClick={() => setShowApprovalPanel(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors"
                data-testid="approvals-btn"
              >
                <Clock className="w-3.5 h-3.5" />
                <span>Approvals</span>
              </button>
            )}
            
            {isAuthenticated && (
              <button
                onClick={() => setShowAuditLog(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors"
                data-testid="audit-log-btn"
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Activity</span>
              </button>
            )}

            <button
              onClick={() => setShowCommandPalette(true)}
              className="flex items-center gap-2 px-3 py-1.5 text-xs bg-muted border border-border rounded-md hover:bg-muted/80 transition-colors"
              data-testid="command-palette-btn"
            >
              <Command className="w-3 h-3" />
              <span>Command</span>
              <kbd className="px-1 py-0.5 text-[10px] bg-background border border-border rounded">⌘K</kbd>
            </button>
            
            <a
              href={ERP_BASE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 text-xs border border-border rounded-md hover:bg-muted transition-colors"
            >
              <span>Open ERPNext</span>
              <ExternalLink className="w-3 h-3" />
            </a>

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2 ml-2 pl-2 border-l border-border">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <div className="hidden md:block">
                    <div className="text-xs font-medium text-foreground">{user?.name}</div>
                    <div className="flex items-center gap-1">
                      <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded border ${roleBadgeColors[user?.role] || roleBadgeColors.viewer}`}>
                        {user?.role?.toUpperCase()}
                      </span>
                      {user?.company && (
                        <span className="px-1.5 py-0.5 text-[10px] font-medium rounded border bg-slate-700/50 text-slate-300 border-slate-600 flex items-center gap-0.5">
                          <Building2 className="w-2.5 h-2.5" />
                          {user.company.length > 15 ? user.company.slice(0, 15) + '...' : user.company}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={logout}
                  className="p-1.5 hover:bg-muted rounded-lg text-muted-foreground hover:text-foreground"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowLoginModal(true)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                data-testid="login-btn"
              >
                <Shield className="w-3 h-3" />
                <span>Sign In</span>
              </button>
            )}
          </div>
        </header>

        {/* Messages or Tool Results */}
        {toolResult ? (
          <div className="flex-1 overflow-y-auto p-6">
            <ToolResultsView 
              toolResult={toolResult}
              onRefresh={handleRefreshTool}
              onDelete={handleDeleteToolFromResults}
              isLoading={isToolLoading}
            />
          </div>
        ) : messages.length === 0 ? (
          /* Show ChatSuggestions when chat is empty */
          <div className="flex-1 flex flex-col items-center justify-center p-6 overflow-y-auto bg-white">
            <div className="max-w-2xl w-full text-center mb-10">
              {/* Logo/Icon */}
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              
              <h2 className="text-3xl font-bold text-gray-900 mb-3 tracking-tight">
                Welcome to AgentERP
              </h2>
              <p className="text-gray-600 text-lg">
                {isAuthenticated 
                  ? (
                    <>
                      Your AI assistant for ERP operations
                      {user?.company && (
                        <span className="block mt-1 text-base">
                          Connected to <span className="text-blue-600 font-medium">{user.company}</span>
                        </span>
                      )}
                    </>
                  )
                  : 'Sign in to access your company\'s ERP data'}
              </p>
            </div>
            {isAuthenticated && (
              <ChatSuggestions 
                onSuggestionClick={handleSuggestionClick}
                className="max-w-2xl w-full"
              />
            )}
          </div>
        ) : (
          <ChatMessages 
            messages={messages} 
            isLoading={isLoading}
            onStopSalesActionComplete={handleStopSalesActionComplete}
          />
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-border bg-background">
          {/* Business Impact (compact) */}
          {isAuthenticated && (
            <div className="mb-3">
              <BusinessImpact compact />
            </div>
          )}
          
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={() => {
              setToolResult(null);
              handleSendMessage();
            }}
            isLoading={isLoading}
            disabled={!canCreate && input.toLowerCase().includes('create')}
          />
          
          <SmartSuggestions
            suggestions={smartSuggestions}
            onSelect={(prompt) => {
              setInput(prompt);
              setSmartSuggestions([]);
            }}
          />
        </div>
      </main>

      {/* Command Palette */}
      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        onAction={handleCommandAction}
      />

      {/* Create Tool Modal */}
      <CreateToolModal
        isOpen={showCreateToolModal}
        onClose={() => setShowCreateToolModal(false)}
        onToolCreated={handleToolCreated}
      />

      {/* Login Modal */}
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
      />

      {/* Approval Panel */}
      <ApprovalPanel
        isOpen={showApprovalPanel}
        onClose={() => setShowApprovalPanel(false)}
      />

      {/* Audit Log */}
      <AuditLog
        isOpen={showAuditLog}
        onClose={() => setShowAuditLog(false)}
      />

      {/* Today's Priorities - AI Reasoning Panel */}
      {showPriorities && (
        <TodaysPriorities onClose={() => setShowPriorities(false)} />
      )}

      {/* Manager Intelligence Dashboard - AI-powered */}
      {showIntelligence && (
        <ManagerIntelligence onClose={() => setShowIntelligence(false)} />
      )}
    </div>
  );
};

export default ChatInterface;
