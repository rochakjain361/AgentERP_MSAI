/**
 * Chat Sidebar - Shows chat history
 */
import React from 'react';
import { XCircle } from 'lucide-react';

export const ChatSidebar = ({ 
  isOpen, 
  sessions, 
  currentSessionId, 
  onSelectSession, 
  onDeleteSession,
  onCreateNew 
}) => {
  return (
    <aside className={`${isOpen ? 'flex' : 'hidden'} md:flex flex-col border-r border-border bg-muted/10 w-64 transition-all`}>
      <div className="p-4 border-b border-border">
        <button
          onClick={onCreateNew}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          data-testid="new-chat-btn"
        >
          <span className="text-lg">+</span>
          <span>New Chat</span>
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-2">
        <div className="text-xs text-muted-foreground px-3 py-2 font-semibold">Recent Chats</div>
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`w-full text-left px-3 py-2 rounded-md mb-1 group hover:bg-muted transition-colors cursor-pointer ${
              session.id === currentSessionId ? 'bg-muted border border-primary/50' : ''
            }`}
            data-testid={`chat-session-${session.id}`}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onSelectSession(session.id);
              }
            }}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className={`text-sm truncate ${session.id === currentSessionId ? 'font-medium' : ''}`}>
                  {session.title}
                </div>
                <div className="text-xs text-muted-foreground">
                  {session.message_count} messages
                </div>
              </div>
              <button
                onClick={(e) => onDeleteSession(session.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 hover:text-destructive rounded transition-all"
                title="Delete chat"
              >
                <XCircle className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default ChatSidebar;
