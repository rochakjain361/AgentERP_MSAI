/**
 * API client configuration and utilities
 * Enterprise Edition with Authentication
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

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('agenterp_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('agenterp_token');
      localStorage.removeItem('agenterp_user');
      // Don't redirect if already on login or it's a verify request
      if (!window.location.hash.includes('login')) {
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }
    return Promise.reject(error);
  }
);

// Auth API functions
export const authApi = {
  login: (email, password) => 
    apiClient.post('/auth/login', { email, password }),
  register: (email, password, name, role = 'operator', company = null) => 
    apiClient.post('/auth/register', { email, password, name, role, company }),
  getMe: () => apiClient.get('/auth/me'),
  verify: () => apiClient.get('/auth/verify'),
  listUsers: () => apiClient.get('/auth/users'),
  updateRole: (userId, role) => apiClient.put(`/auth/users/${userId}/role`, null, { params: { role } }),
  seedUsers: () => apiClient.post('/auth/seed'),
};

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

// Insights API functions
export const insightsApi = {
  getInsights: () => apiClient.get('/insights'),
  getSuggestions: () => apiClient.get('/insights/suggestions'),
  getPublicInsights: () => apiClient.get('/insights/public'),
  getBusinessImpact: () => apiClient.get('/insights/impact'),
};

// Approval API functions
export const approvalsApi = {
  getPending: () => apiClient.get('/approvals'),
  getMyRequests: () => apiClient.get('/approvals/my-requests'),
  getDetail: (id) => apiClient.get(`/approvals/${id}`),
  approve: (id, notes) => apiClient.post(`/approvals/${id}/approve`, null, { params: { notes } }),
  reject: (id, notes) => apiClient.post(`/approvals/${id}/reject`, null, { params: { notes } }),
  decide: (id, decision, notes) => apiClient.post(`/approvals/${id}/decide`, { decision, notes }),
};

// Audit API functions
export const auditApi = {
  getLogs: (params = {}) => apiClient.get('/audit', { params }),
  getRecent: (limit = 10) => apiClient.get('/audit/recent', { params: { limit } }),
  getSummary: (userId) => apiClient.get(`/audit/summary/${userId}`),
  getStats: () => apiClient.get('/audit/stats'),
};

// Health API
export const healthApi = {
  check: () => apiClient.get('/health'),
};

// Tools API
export const toolsApi = {
  getAll: () => apiClient.get('/tools'),
  create: (tool) => apiClient.post('/tools', tool),
  run: (toolName) => apiClient.get(`/tools/run/${toolName}`),
  delete: (toolName) => apiClient.delete(`/tools/${toolName}`),
};

// Entity API
export const entityApi = {
  query: (doctype, filters = [], fields = [], limit = 20) =>
    apiClient.post('/entity', { action: 'query', doctype, filters, fields, limit }),
  create: (doctype, data) =>
    apiClient.post('/entity', { action: 'create', doctype, data }),
  read: (doctype, name) =>
    apiClient.post('/entity', { action: 'read', doctype, name }),
  update: (doctype, name, data) =>
    apiClient.post('/entity', { action: 'update', doctype, name, data }),
  delete: (doctype, name) =>
    apiClient.post('/entity', { action: 'delete', doctype, name }),
};

// Reasoning API - Proactive Analysis & Workflow Execution
export const reasoningApi = {
  // Get today's priorities (all situations requiring attention)
  getPriorities: () => apiClient.get('/reasoning/priorities'),
  
  // Get payment delay analysis (hero scenario)
  getPaymentDelays: () => apiClient.get('/reasoning/payment-delays'),
  
  // Execute a sequence of actions
  executeSequence: (situationId, situationType, selectedActions, contextData) =>
    apiClient.post('/reasoning/execute', {
      situation_id: situationId,
      situation_type: situationType,
      selected_actions: selectedActions,
      context_data: contextData
    }),
  
  // Get workflow execution status
  getWorkflowStatus: (workflowId) => apiClient.get(`/reasoning/workflow/${workflowId}`),
};

// Intelligence API - AI-powered Manager Dashboard
export const intelligenceApi = {
  // Get comprehensive AI-powered intelligence dashboard
  getDashboard: () => apiClient.get('/intelligence/dashboard'),
  
  // Analyze a specific situation with AI
  analyzeSituation: (situationType, contextData) =>
    apiClient.post('/intelligence/analyze', {
      situation_type: situationType,
      context_data: contextData
    }),
  
  // Check AI health
  healthCheck: () => apiClient.get('/intelligence/health-check'),
};

export default apiClient;
