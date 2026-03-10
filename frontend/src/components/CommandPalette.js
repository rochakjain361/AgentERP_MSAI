/**
 * Command Palette Component
 */
import React from 'react';
import { ERP_BASE_URL, QUICK_ACTIONS } from '../lib/constants';

const ERP_LINKS = [
  { icon: '🏠', text: 'ERP Home', url: `${ERP_BASE_URL}/app/home` },
  { icon: '📋', text: 'Sales Orders', url: `${ERP_BASE_URL}/app/sales-order` },
  { icon: '👥', text: 'Customers', url: `${ERP_BASE_URL}/app/customer` },
  { icon: '💰', text: 'Invoices', url: `${ERP_BASE_URL}/app/sales-invoice` },
  { icon: '📦', text: 'Items', url: `${ERP_BASE_URL}/app/item` },
];

export const CommandPalette = ({ isOpen, onClose, onAction }) => {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-start justify-center pt-32 z-50" 
      onClick={onClose}
    >
      <div 
        className="bg-background border border-border rounded-xl shadow-2xl w-full max-w-2xl" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-border">
          <input
            type="text"
            placeholder="Type a command or search..."
            className="w-full bg-transparent border-0 focus:ring-0 text-base outline-none"
            autoFocus
          />
        </div>
        <div className="max-h-96 overflow-y-auto">
          <div className="p-2">
            <div className="px-3 py-2 text-xs text-muted-foreground font-semibold">
              Quick Actions
            </div>
            {QUICK_ACTIONS.map((cmd, idx) => (
              <button
                key={idx}
                onClick={() => onAction(cmd.action)}
                className="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted rounded-md transition-colors text-left"
              >
                <span className="text-xl">{cmd.icon}</span>
                <span className="text-sm">{cmd.text}</span>
              </button>
            ))}
            
            <div className="px-3 py-2 text-xs text-muted-foreground font-semibold mt-4">
              ERPNext Links
            </div>
            {ERP_LINKS.map((link, idx) => (
              <a
                key={idx}
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted rounded-md transition-colors"
                onClick={onClose}
              >
                <span className="text-xl">{link.icon}</span>
                <span className="text-sm">{link.text}</span>
                <span className="ml-auto text-xs text-muted-foreground">→</span>
              </a>
            ))}
          </div>
        </div>
        <div className="p-3 border-t border-border bg-muted/30 text-xs text-muted-foreground text-center">
          Press <kbd className="px-2 py-1 bg-background border border-border rounded">ESC</kbd> to close
        </div>
      </div>
    </div>
  );
};

export default CommandPalette;
