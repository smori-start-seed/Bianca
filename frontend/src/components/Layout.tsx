import { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router';
import { Monitor, Moon, PanelLeft, PanelLeftClose, Sun } from 'lucide-react';
import { ApprovalBell } from './ApprovalBell';
import { Sidebar } from './Sidebar/Sidebar';
import { SystemPulse } from './SystemPulse';
import { TabBar } from './Bianca/TabBar';
import { TABS, tabById } from './Bianca/tabs';
import type { TabId } from './Bianca/tabs';
import { useAppStore } from '../lib/store';
import { checkHealth } from '../lib/api';

export function Layout() {
  const sidebarOpen = useAppStore((s) => s.sidebarOpen);
  const toggleSidebar = useAppStore((s) => s.toggleSidebar);
  const settings = useAppStore((s) => s.settings);
  const updateSettings = useAppStore((s) => s.updateSettings);
  const [apiReachable, setApiReachable] = useState<boolean | null>(null);

  const ThemeIcon =
    settings.theme === 'light' ? Sun : settings.theme === 'dark' ? Moon : Monitor;
  const nextTheme =
    settings.theme === 'light' ? 'dark' : settings.theme === 'dark' ? 'system' : 'light';

  useEffect(() => {
    const check = () => checkHealth().then(setApiReachable);
    check();
    const interval = setInterval(check, 30000);
    const onFocus = () => check();
    window.addEventListener('focus', onFocus);
    return () => {
      clearInterval(interval);
      window.removeEventListener('focus', onFocus);
    };
  }, []);

  const navigate = useNavigate();
  const location = useLocation();

  // The active tab is DERIVED from the URL, never held in state. A tab bar
  // that remembers its own selection disagrees with the address bar the
  // moment a deep link, a refresh, or the back button is used — and an
  // enterprise tool that lies about where you are is not one.
  const activeTab: TabId =
    TABS.find((t) => location.pathname === t.path || location.pathname.startsWith(`${t.path}/`))
      ?.id ?? 'jarvis';
  const onTab = (id: TabId) => navigate(tabById(id)?.path ?? '/jarvis');

  // The conversation rail belongs to the platform chat specifically — not to
  // the governed dialogue, which keeps its own transcript in the panel, and
  // not to the other three tabs, which are not conversations at all.
  const showRail = activeTab === 'jarvis' && new URLSearchParams(location.search).get('sub') !== 'sovereign';

  return (
    <div className="flex flex-col h-full w-full overflow-hidden relative" style={{ paddingTop: '3px' }}>
      <div className="hud-backdrop" aria-hidden="true" />
      <SystemPulse apiReachable={apiReachable} />
      <ApprovalBell />

      {/* Health check banner */}
      {apiReachable === false && (
        <div
          className="flex items-center gap-3 px-4 py-2 text-sm shrink-0"
          style={{
            background: 'color-mix(in srgb, var(--color-error) 8%, transparent)',
            borderBottom: '1px solid color-mix(in srgb, var(--color-error) 15%, transparent)',
            color: 'var(--color-text)',
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full shrink-0"
            style={{ background: 'var(--color-error)' }}
          />
          <span>Cannot reach the Bianca node</span>
          <button
            onClick={() => navigate('/bianca?sub=settings')}
            className="text-sm underline cursor-pointer ml-auto shrink-0"
            style={{ color: 'var(--color-accent)' }}
          >
            Change URL
          </button>
        </div>
      )}

      <div className="flex flex-1 min-h-0 relative z-10">
        {/*
          The sidebar is the CHAT's rail — conversations, model, new thread.
          It is shown only on the Jarvis tab, because a list of past
          conversations is noise on a page about the cycle or the network, and
          four fifths of this product are not chat. The two global controls that
          used to live down there (rail toggle, theme) moved up into the top
          bar, so hiding the rail never hides the way back.
        */}
        {showRail && <Sidebar />}
        {showRail && sidebarOpen && (
          <div
            className="fixed inset-0 z-20 bg-black/40 md:hidden"
            onClick={() => useAppStore.getState().setSidebarOpen(false)}
          />
        )}
        <main className="flex-1 flex flex-col min-w-0 h-full relative overflow-hidden" style={{ background: 'transparent' }}>
          {/*
            The five tabs live at the top of the content area, above whatever
            the tab renders, rather than in the sidebar. A tab bar that shares
            a column with the conversation list forces a choice: either the
            navigation moves when the sidebar collapses, or the conversation
            list loses its home. Horizontal tabs and a vertical list are two
            different axes and belong on two different axes.
          */}
          <div
            className="shrink-0 border-b"
            style={{
              borderColor: 'var(--s-line)',
              background: 'color-mix(in srgb, var(--s-bg) 72%, transparent)',
              backdropFilter: 'blur(14px)',
              WebkitBackdropFilter: 'blur(14px)',
            }}
          >
            <div className="flex items-center gap-3 px-3">
              {showRail && (
                <button
                  onClick={toggleSidebar}
                  aria-label={sidebarOpen ? 'Chat-Verlauf ausblenden' : 'Chat-Verlauf einblenden'}
                  title={sidebarOpen ? 'Chat-Verlauf ausblenden' : 'Chat-Verlauf einblenden'}
                  className="p-1.5 rounded-lg transition-colors cursor-pointer shrink-0"
                  style={{ color: 'var(--color-text-secondary)' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--color-bg-tertiary)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  {sidebarOpen ? <PanelLeftClose size={16} /> : <PanelLeft size={16} />}
                </button>
              )}
              <div className="shrink-0 flex items-center gap-2 pr-2">
                <span
                  className="font-semibold text-[13px] tracking-tight"
                  style={{ color: 'var(--s-gold)' }}
                >
                  Bianca
                </span>
                <span
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  title={apiReachable === false ? 'Backend nicht erreichbar' : 'Backend erreichbar'}
                  style={{
                    background:
                      apiReachable === null
                        ? 'var(--s-mut-2)'
                        : apiReachable
                          ? 'var(--s-ok)'
                          : 'var(--s-deny)',
                  }}
                  aria-hidden
                />
              </div>
              <div className="min-w-0 flex-1">
                <TabBar active={activeTab} onSelect={onTab} />
              </div>
              <button
                onClick={() => updateSettings({ theme: nextTheme })}
                title={`Theme: ${settings.theme} (click for ${nextTheme})`}
                aria-label={`Theme: ${settings.theme}`}
                className="p-1.5 rounded-lg transition-colors cursor-pointer shrink-0"
                style={{ color: 'var(--color-text-secondary)' }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--color-bg-tertiary)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                <ThemeIcon size={16} />
              </button>
            </div>
          </div>

          <div className="flex-1 flex flex-col min-w-0 min-h-0 relative z-[2]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
