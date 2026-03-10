/**
 * API client configuration and utilities
 */
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
export const apiClient = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API functions
export const chatApi = {
  getSessions: () => apiClient.get('/chat/sessions'),
  createSession: () => apiClient.post('/chat/sessions'),
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),
  getMessages: (sessionId) => apiClient.get(`/chat/messages/${sessionId}`),
  saveMessage: (message) => apiClient.post('/chat/messages', message),
  sendChat: (message, conversationHistory) => 
    apiClient.post('/chat', { message, conversation_history: conversationHistory }),
};

// Health API
export const healthApi = {
  check: () => apiClient.get('/health'),
};

export default apiClient;
