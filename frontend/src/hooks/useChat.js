/**
 * Custom hook for managing chat sessions and messages
 */
import { useState, useCallback } from 'react';
import { chatApi } from '../lib/api';
import { toast } from 'sonner';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [smartSuggestions, setSmartSuggestions] = useState([]);

  const loadChatSessions = useCallback(async () => {
    try {
      const response = await chatApi.getSessions();
      setChatSessions(response.data || []);
      
      if (!response.data || response.data.length === 0) {
        await createNewChat();
      } else {
        setCurrentSessionId(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
      await createNewChat();
    }
  }, []);

  const createNewChat = useCallback(async () => {
    try {
      const response = await chatApi.createSession();
      const newSession = response.data.session;
      setChatSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(newSession.id);
      setMessages([]);
      setSmartSuggestions([]);
    } catch (error) {
      console.error('Failed to create new chat:', error);
    }
  }, []);

  const loadSessionMessages = useCallback(async (sessionId) => {
    try {
      const response = await chatApi.getMessages(sessionId);
      setMessages(response.data || []);
    } catch (error) {
      console.error('Failed to load session messages:', error);
      setMessages([]);
    }
  }, []);

  const deleteChat = useCallback(async (sessionId, e) => {
    if (e) e.stopPropagation();
    try {
      await chatApi.deleteSession(sessionId);
      setChatSessions(prev => prev.filter(s => s.id !== sessionId));
      
      if (sessionId === currentSessionId) {
        await createNewChat();
      }
      
      toast.success('Chat deleted');
    } catch (error) {
      console.error('Failed to delete chat:', error);
      toast.error('Failed to delete chat');
    }
  }, [currentSessionId, createNewChat]);

  const saveChatMessage = useCallback(async (message) => {
    if (!currentSessionId) return;
    
    try {
      await chatApi.saveMessage({
        ...message,
        session_id: currentSessionId
      });
      
      const response = await chatApi.getSessions();
      setChatSessions(response.data || []);
    } catch (error) {
      console.error('Failed to save message:', error);
    }
  }, [currentSessionId]);

  const generateSmartSuggestions = useCallback((lastAction) => {
    const suggestions = [];
    
    if (lastAction?.includes('sales order') || lastAction?.includes('order')) {
      suggestions.push({
        text: 'Create an invoice for this order',
        prompt: 'Create an invoice',
        icon: '📄'
      });
      suggestions.push({
        text: 'Check order status',
        prompt: 'What is the status of recent orders?',
        icon: '📊'
      });
    }
    
    if (lastAction?.includes('customer')) {
      suggestions.push({
        text: 'View all orders for this customer',
        prompt: 'Show me all orders for this customer',
        icon: '📋'
      });
      suggestions.push({
        text: 'Create a new order',
        prompt: 'Create a sales order',
        icon: '➕'
      });
    }
    
    suggestions.push({
      text: 'Show dashboard overview',
      prompt: 'Show me the dashboard statistics',
      icon: '📊'
    });
    
    return suggestions.slice(0, 3);
  }, []);

  const sendMessage = useCallback(async (input, conversationHistory) => {
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      type: 'text',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    saveChatMessage(userMessage);
    setIsLoading(true);

    try {
      const history = conversationHistory.slice(-6).map(msg => ({
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content
      }));

      const response = await chatApi.sendChat(input, history);

      let aiMessage = {
        role: 'assistant',
        content: response.data.message,
        type: 'text',
        timestamp: new Date().toISOString()
      };

      if (response.data.status === 'success' && response.data.data) {
        const data = response.data.data;
        
        if (data.type === 'comprehensive_analytics' || 
            data.type === 'sales_orders_list' || 
            data.type === 'invoices_list' || 
            data.type === 'customers_list' || 
            data.type === 'dashboard') {
          aiMessage = { ...aiMessage, type: 'widget', widget_data: data };
        } else if (data.name && (data.name.startsWith('SO-') || data.name.startsWith('SAL-ORD'))) {
          aiMessage = { ...aiMessage, type: 'widget', widget_data: { type: 'sales_order', ...data } };
        } else if (data.customer_name || data.customer_type) {
          aiMessage = { ...aiMessage, type: 'widget', widget_data: { type: 'customer', ...data } };
        }
      }

      setMessages(prev => [...prev, aiMessage]);
      saveChatMessage(aiMessage);
      
      const suggestions = generateSmartSuggestions(aiMessage.content);
      setSmartSuggestions(suggestions);
      
      if (response.data.status === 'success') {
        toast.success('Action completed successfully');
      } else {
        toast.error('Action failed');
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        type: 'text',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Something went wrong');
    } finally {
      setIsLoading(false);
    }
  }, [saveChatMessage, generateSmartSuggestions]);

  return {
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
  };
};

export default useChat;
