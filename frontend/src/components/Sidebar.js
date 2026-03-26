/**
 * Main Sidebar - Shows quick actions, saved tools, enterprise features, and navigation
 */
import React, { useState, useEffect } from 'react';
import { Activity, Wrench, Plus, Play, Trash2, ChevronDown, ChevronRight, Clock, FileText, Shield, Users } from 'lucide-react';
import { SIDEBAR_ACTIONS } from '../lib/constants';
import { API } from '../lib/api';
import axios from 'axios';
import { toast } from 'sonner';

export const Sidebar = ({ 
  erpStatus, 
  onSetInput, 
  onAnalytics, 
  onToolRun, 
  onCreateTool,
  user,
  isAuthenticated,
  onShowApprovals,
  onShowAuditLog,
  isManager
}) => {
  const [tools, setTools] = useState([]);
  const [isToolsExpanded, setIsToolsExpanded] = useState(true);
  const [isEnterpriseExpanded, setIsEnterpriseExpanded] = useState(true);
  const [loadingTool, setLoadingTool] = useState(null);

  const focusInput = () => {
    document.querySelector('[data-testid="chat-input"]')?.focus();
  };

  // Load saved tools on mount
  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const response = await axios.get(`${API}/tools`);
      if (response.data.status === 'success') {
        setTools(response.data.tools || []);
      }
    } catch (error) {
      console.error('Failed to load tools:', error);
    }
  };

  const handleRunTool = async (toolName) => {
    setLoadingTool(toolName);
    try {
      const response = await axios.get(`${API}/tools/run/${toolName}`);
      if (response.data.status === 'success') {
        onToolRun(response.data);
        toast.success(`Tool "${toolName}" executed`);
      } else {
        toast.error(response.data.message || 'Failed to run tool');
      }
    } catch (error) {
      toast.error('Failed to run tool');
    } finally {
      setLoadingTool(null);
    }
  };

  const handleDeleteTool = async (toolName, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete tool "${toolName}"?`)) return;
    
    try {
      const response = await axios.delete(`${API}/tools/${toolName}`);
      if (response.data.status === 'success') {
        setTools(tools.filter(t => t.tool_name !== toolName));
        toast.success('Tool deleted');
      }
    } catch (error) {
      toast.error('Failed to delete tool');
    }
  };

  // Expose loadTools to parent for refresh after creating tool
  useEffect(() => {
    window.refreshTools = loadTools;
    return () => delete window.refreshTools;
  }, []);

  // Role badge colors
  const roleBadgeColors = {
    admin: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    manager: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    operator: 'bg-green-500/20 text-green-300 border-green-500/30',
    viewer: 'bg-slate-500/20 text-slate-300 border-slate-500/30',
  };

  return (
    <aside className="hidden md:flex flex-col border-r border-border bg-muted/10 w-64">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'Manrope, sans-serif' }}>
          Agent<span className="text-primary">ERP</span>
        </h1>
        <p className="text-sm text-muted-foreground mt-1">Enterprise AI Agent</p>
        {isAuthenticated && user && (
          <div className="mt-2 flex items-center gap-2">
            <span className={`px-2 py-0.5 text-[10px] font-medium rounded border ${roleBadgeColors[user?.role] || roleBadgeColors.viewer}`}>
              {user?.role?.toUpperCase()}
            </span>
            <span className="text-xs text-muted-foreground truncate">{user?.name}</span>
          </div>
        )}
      </div>
      
      <div className="flex-1 p-4 space-y-2 overflow-y-auto">
        {/* Analytics Button */}
        <button
          onClick={onAnalytics}
          className="w-full flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors cursor-pointer"
          data-testid="sidebar-analytics-btn"
        >
          <Activity className="w-4 h-4" />
          <span>Analytics Dashboard</span>
        </button>
        
        <button
          onClick={() => {
            onSetInput('Show me the dashboard statistics');
            focusInput();
          }}
          className="w-full flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-md bg-muted border border-border hover:bg-primary hover:text-primary-foreground transition-colors cursor-pointer"
          data-testid="sidebar-dashboard-btn"
        >
          <Activity className="w-4 h-4" />
          <span>Quick Stats</span>
        </button>

        {/* Enterprise Features Section */}
        {isAuthenticated && (
          <div className="pt-4">
            <button
              onClick={() => setIsEnterpriseExpanded(!isEnterpriseExpanded)}
              className="w-full flex items-center justify-between px-3 py-2 text-xs text-muted-foreground font-semibold hover:text-foreground transition-colors"
            >
              <div className="flex items-center gap-2">
                <Shield className="w-3.5 h-3.5" />
                <span>Enterprise</span>
              </div>
              {isEnterpriseExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </button>
            
            {isEnterpriseExpanded && (
              <div className="mt-1 space-y-1">
                {isManager && (
                  <button
                    onClick={onShowApprovals}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:bg-amber-500/10 hover:text-amber-300 rounded-md cursor-pointer transition-colors"
                    data-testid="sidebar-approvals-btn"
                  >
                    <Clock className="w-3.5 h-3.5" />
                    <span>Approval Workflow</span>
                  </button>
                )}
                
                <button
                  onClick={onShowAuditLog}
                  className="w-full flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:bg-violet-500/10 hover:text-violet-300 rounded-md cursor-pointer transition-colors"
                  data-testid="sidebar-audit-btn"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Activity Log</span>
                </button>
                
                {user?.role === 'admin' && (
                  <button
                    onClick={() => {
                      onSetInput('List all users in the system');
                      focusInput();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:bg-purple-500/10 hover:text-purple-300 rounded-md cursor-pointer transition-colors"
                    data-testid="sidebar-users-btn"
                  >
                    <Users className="w-3.5 h-3.5" />
                    <span>User Management</span>
                  </button>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* Saved Tools Section */}
        <div className="pt-4">
          <button
            onClick={() => setIsToolsExpanded(!isToolsExpanded)}
            className="w-full flex items-center justify-between px-3 py-2 text-xs text-muted-foreground font-semibold hover:text-foreground transition-colors"
          >
            <div className="flex items-center gap-2">
              <Wrench className="w-3.5 h-3.5" />
              <span>Saved Tools</span>
              {tools.length > 0 && (
                <span className="px-1.5 py-0.5 text-[10px] bg-primary/10 text-primary rounded-full">
                  {tools.length}
                </span>
              )}
            </div>
            {isToolsExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          </button>
          
          {isToolsExpanded && (
            <div className="mt-1 space-y-1">
              {tools.map((tool) => (
                <div
                  key={tool.tool_name}
                  className="group flex items-center justify-between px-3 py-2 text-xs rounded-md hover:bg-muted cursor-pointer transition-colors"
                  onClick={() => handleRunTool(tool.tool_name)}
                  data-testid={`tool-${tool.tool_name}`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {loadingTool === tool.tool_name ? (
                      <div className="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <Play className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary" />
                    )}
                    <span className="truncate" title={tool.description}>
                      {tool.tool_name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteTool(tool.tool_name, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 hover:text-destructive rounded transition-all"
                    title="Delete tool"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))}
              
              {/* Create Tool Button */}
              <button
                onClick={onCreateTool}
                className="w-full flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:text-foreground hover:bg-muted rounded-md transition-colors border border-dashed border-border mt-2"
                data-testid="create-tool-btn-sidebar"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Create Tool</span>
              </button>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="px-3 py-2 text-xs text-muted-foreground font-semibold mt-4">
          Quick Actions
        </div>
        
        <div className="space-y-1 text-xs">
          {SIDEBAR_ACTIONS.quickActions.map((action, idx) => (
            <button
              key={idx}
              onClick={() => {
                onSetInput(action.prompt);
                focusInput();
              }}
              className="w-full text-left px-3 py-2 text-muted-foreground hover:bg-muted hover:text-foreground rounded-md cursor-pointer transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>

        {/* Analytics Quick Actions */}
        <div className="px-3 py-2 text-xs text-muted-foreground font-semibold mt-4">
          Analytics
        </div>
        
        <div className="space-y-1 text-xs">
          {SIDEBAR_ACTIONS.analytics.map((action, idx) => (
            <button
              key={idx}
              onClick={() => {
                onSetInput(action.prompt);
                focusInput();
              }}
              className="w-full text-left px-3 py-2 text-muted-foreground hover:bg-muted hover:text-foreground rounded-md cursor-pointer transition-colors"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>
      
      {/* Status */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-full bg-muted border border-border">
          <div className={`w-2 h-2 rounded-full status-dot-pulse bg-green-500`} />
          <span>
            Live ERP
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
