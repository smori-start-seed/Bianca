import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Plus, Search, Cpu, Loader2 } from 'lucide-react';
import { ConversationList } from './ConversationList';
import { useAppStore } from '../../lib/store';

export function Sidebar() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const sidebarOpen = useAppStore((s) => s.sidebarOpen);
  const createConversation = useAppStore((s) => s.createConversation);
  const selectedModel = useAppStore((s) => s.selectedModel);
  const serverInfo = useAppStore((s) => s.serverInfo);
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen);
  const modelLoading = useAppStore((s) => s.modelLoading);
  const deepResearch = useAppStore((s) => s.deepResearch);

  const messages = useAppStore((s) => s.messages);
  const handleNewChat = () => {
    // Don't create a new chat if the current one is empty
    if (messages.length === 0) {
      navigate('/jarvis');
      return;
    }
    createConversation(selectedModel);
    // The new thread belongs to the platform chat, which is the first option
    // of the Jarvis tab — so the rail is on screen for it.
    navigate('/jarvis');
  };

  return (
    <>
      <aside
        className={`
          flex flex-col h-full shrink-0 transition-all duration-200 ease-in-out overflow-hidden
          fixed md:relative z-30
          ${sidebarOpen ? 'w-[260px]' : 'w-0'}
        `}
        style={{
          background: 'var(--color-sidebar)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRight: sidebarOpen ? '1px solid var(--color-border)' : 'none',
        }}
      >
        <div className="flex flex-col h-full w-[260px]">
          {/*
            The header holds only what belongs to the conversation itself.
            The rail toggle and the theme toggle moved to the top bar in set 15
            — both are global, and a control that disappears with the rail it
            lives in is a control the reader has to go looking for.
          */}
          <div className="flex items-center justify-between px-3 pt-3 pb-2">
            <span
              className="text-[11px] uppercase tracking-wider"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Unterhaltung
            </span>
            <button
              onClick={handleNewChat}
              className="p-2 rounded-lg transition-colors cursor-pointer"
              style={{ color: 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--color-bg-tertiary)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              title="New chat"
            >
              <Plus size={18} />
            </button>
          </div>

          {/* Model badge */}
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="mx-3 mb-2 flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-colors cursor-pointer"
            style={{
              background: 'var(--color-bg-secondary)',
              color: 'var(--color-text-secondary)',
              border: '1px solid var(--color-border)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--color-bg-tertiary)')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--color-bg-secondary)')}
          >
            {modelLoading ? (
              <Loader2 size={14} className="animate-spin" style={{ color: 'var(--color-accent)' }} />
            ) : (
              <Cpu size={14} />
            )}
            <div className="flex-1 min-w-0">
              <span
                className="truncate block text-left"
                style={{ color: deepResearch ? 'var(--color-accent)' : 'var(--color-text)' }}
              >
                {deepResearch
                  ? 'Deep Research'
                  : selectedModel || serverInfo?.model || 'Select model'}
              </span>
              {modelLoading && (
                <span className="text-[10px] block text-left" style={{ color: 'var(--color-accent)' }}>
                  Loading model...
                </span>
              )}
            </div>
            {!modelLoading && (
              <kbd
                className="text-[10px] px-1.5 py-0.5 rounded font-mono"
                style={{ background: 'var(--color-bg-tertiary)', color: 'var(--color-text-tertiary)' }}
              >
                ⌘K
              </kbd>
            )}
          </button>

          {/* Search */}
          <div className="px-3 mb-2">
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm"
              style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
            >
              <Search size={14} style={{ color: 'var(--color-text-tertiary)' }} />
              <input
                type="text"
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 bg-transparent outline-none text-sm"
                style={{ color: 'var(--color-text)' }}
              />
            </div>
          </div>

          {/* Conversation list */}
          <div className="flex-1 overflow-y-auto px-2">
            <ConversationList searchQuery={searchQuery} />
          </div>
        </div>
      </aside>
    </>
  );
}
