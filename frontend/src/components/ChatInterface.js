/**
 * ChatInterface - Main chat interface component
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
 */
import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { Menu, Command, ExternalLink, Download, Trash2, History } from 'lucide-react';

// Import components
import { Sidebar } from './Sidebar';
import { ChatSidebar } from './ChatSidebar';
import { CommandPalette } from './CommandPalette';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { SmartSuggestions } from './SmartSuggestions';
import { CreateToolModal } from './CreateToolModal';
import { ToolResultsView } from './ToolResultsView';

// Import hooks
import { useChat } from '../hooks/useChat';
import { useHealth } from '../hooks/useHealth';

// Import constants and API
import { ERP_BASE_URL } from '../lib/constants';
import { API } from '../lib/api';
import axios from 'axios';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [showChatHistory, setShowChatHistory] = useState(false);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showCreateToolModal, setShowCreateToolModal] = useState(false);
  const [toolResult, setToolResult] = useState(null);
  const [isToolLoading, setIsToolLoading] = useState(false);
  
  // Custom hooks
  const { erpStatus, checkHealth } = useHealth();
  const {
    messages,
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
    loadChatSessions();
  }, []);

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
    setToolResult(null); // Clear tool results when switching to analytics
    setInput('Show me comprehensive analytics and insights');
    setTimeout(() => {
      document.querySelector('[data-testid="send-message-btn"]')?.click();
    }, 100);
  }, []);

  // Handle tool run from sidebar
  const handleToolRun = useCallback((result) => {
    setToolResult(result);
  }, []);

  // Handle tool created
  const handleToolCreated = useCallback((tool) => {
    // Refresh tools in sidebar
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
    setToolResult(null); // Clear tool results when switching sessions
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
            
            <button 
              onClick={() => setShowChatHistory(prev => !prev)}
              className="hidden md:flex items-center gap-2 p-2 hover:bg-muted rounded-lg text-sm"
              data-testid="toggle-history-btn"
            >
              <History className="w-4 h-4" />
              <span>Chat History</span>
            </button>
            
            <button 
              onClick={createNewChat}
              className="hidden md:flex items-center gap-2 p-2 hover:bg-muted rounded-lg text-sm text-primary"
              data-testid="new-chat-btn"
            >
              <span className="text-lg">+</span>
              <span>New Chat</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
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
            
            <button
              onClick={exportChat}
              className="p-2 hover:bg-muted rounded-lg"
              title="Export chat"
            >
              <Download className="w-4 h-4" />
            </button>
            
            <button
              onClick={clearChat}
              className="p-2 hover:bg-muted rounded-lg text-destructive"
              title="Clear chat"
            >
              <Trash2 className="w-4 h-4" />
            </button>
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
        ) : (
          <ChatMessages messages={messages} isLoading={isLoading} />
        )}

        {/* Input Area */}
        <div className="p-4 border-t border-border bg-background">
          <ChatInput
            value={input}
            onChange={setInput}
            onSend={() => {
              setToolResult(null);
              handleSendMessage();
            }}
            isLoading={isLoading}
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
    </div>
  );
};

export default ChatInterface;
