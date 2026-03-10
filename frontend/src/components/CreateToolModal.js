/**
 * CreateToolModal - Modal for creating custom query tools
 */
import React, { useState } from 'react';
import { X, Wrench, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { API } from '../lib/api';
import axios from 'axios';

const DOCTYPES = [
  { value: 'Sales Order', label: 'Sales Order', icon: '📋' },
  { value: 'Sales Invoice', label: 'Sales Invoice', icon: '💰' },
  { value: 'Purchase Order', label: 'Purchase Order', icon: '📦' },
  { value: 'Purchase Invoice', label: 'Purchase Invoice', icon: '🧾' },
  { value: 'Customer', label: 'Customer', icon: '👥' },
  { value: 'Supplier', label: 'Supplier', icon: '🏭' },
  { value: 'Item', label: 'Item', icon: '📦' },
  { value: 'Company', label: 'Company', icon: '🏢' },
  { value: 'Employee', label: 'Employee', icon: '👤' },
  { value: 'Lead', label: 'Lead', icon: '🎯' },
  { value: 'Opportunity', label: 'Opportunity', icon: '💡' },
];

const PROMPT_SUGGESTIONS = [
  'Show all orders created today',
  'Show pending/draft orders',
  'Show high value orders (>50,000)',
  'Show completed orders this week',
  'Show all active records',
  'Show unpaid invoices',
  'Show orders from last 30 days',
];

export const CreateToolModal = ({ isOpen, onClose, onToolCreated }) => {
  const [toolName, setToolName] = useState('');
  const [doctype, setDoctype] = useState('Sales Order');
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCreate = async () => {
    if (!toolName.trim()) {
      toast.error('Please enter a tool name');
      return;
    }
    if (!prompt.trim()) {
      toast.error('Please enter a query description');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/tools`, {
        tool_name: toolName,
        doctype: doctype,
        prompt: prompt
      });

      if (response.data.status === 'success') {
        toast.success(`Tool "${toolName}" created successfully!`);
        onToolCreated(response.data.tool);
        handleClose();
      } else {
        toast.error(response.data.message || 'Failed to create tool');
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Failed to create tool');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    setToolName('');
    setDoctype('Sales Order');
    setPrompt('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleClose}
    >
      <div 
        className="bg-background border border-border rounded-xl shadow-2xl w-full max-w-lg"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Wrench className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold" style={{ fontFamily: 'Manrope, sans-serif' }}>
              Create Custom Tool
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="p-1 hover:bg-muted rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 space-y-4">
          {/* Tool Name */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Tool Name</label>
            <input
              type="text"
              value={toolName}
              onChange={(e) => setToolName(e.target.value)}
              placeholder="e.g., Today's Orders"
              className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              data-testid="tool-name-input"
            />
          </div>

          {/* DocType */}
          <div>
            <label className="block text-sm font-medium mb-1.5">DocType</label>
            <select
              value={doctype}
              onChange={(e) => setDoctype(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
              data-testid="doctype-select"
            >
              {DOCTYPES.map((dt) => (
                <option key={dt.value} value={dt.value}>
                  {dt.icon} {dt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Prompt/Query */}
          <div>
            <label className="block text-sm font-medium mb-1.5">Query Description</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what data you want to query..."
              rows={3}
              className="w-full px-3 py-2 rounded-lg border border-border bg-background focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"
              data-testid="prompt-input"
            />
            <div className="mt-2 flex flex-wrap gap-1.5">
              {PROMPT_SUGGESTIONS.slice(0, 4).map((suggestion, idx) => (
                <button
                  key={idx}
                  onClick={() => setPrompt(suggestion)}
                  className="text-xs px-2 py-1 bg-muted rounded-md hover:bg-muted/80 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-2 p-4 border-t border-border bg-muted/30">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCreate}
            disabled={isLoading || !toolName.trim() || !prompt.trim()}
            className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            data-testid="create-tool-btn"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Wrench className="w-4 h-4" />
                Create Tool
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CreateToolModal;
