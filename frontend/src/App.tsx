import { useEffect, useState, useCallback, useRef } from 'react';
import { Routes, Route, Navigate } from 'react-router';
import { Layout } from './components/Layout';
import { JarvisPage } from './pages/JarvisPage';
import { TrialogPage } from './pages/TrialogPage';
import { BiancaPage } from './pages/BiancaPage';
import { UrasilPage } from './pages/UrasilPage';
import { NodeNetPage } from './pages/NodeNetPage';
import { CommandPalette } from './components/CommandPalette';
import { SetupScreen } from './components/SetupScreen';
import { Toaster } from './components/ui/sonner';
import { useAppStore } from './lib/store';
import { fetchModels, fetchServerInfo, fetchSavings, submitSavings, isTauri } from './lib/api';
import { OptInModal } from './components/OptInModal';
import { UpdateChecker } from './components/Desktop/UpdateChecker';
import { track, hashId } from './lib/analytics';
import { LEGACY_ROUTES, tabById } from './components/Bianca/tabs';
import { subParam } from './components/Bianca/TabFrame';

export default function App() {
  const [setupDone, setSetupDone] = useState(!isTauri());
  const handleSetupReady = useCallback(() => {
    setSetupDone(true);
    // Only fire once per install — guard against setup screen re-appearing
    // on reinstalls or dev reloads.
    if (!localStorage.getItem('oj-setup-completed')) {
      localStorage.setItem('oj-setup-completed', '1');
      track('setup_completed', { preset: 'default' });
    }
  }, []);
  const prevModelRef = useRef<string>('');
  const setModels = useAppStore((s) => s.setModels);
  const setModelsLoading = useAppStore((s) => s.setModelsLoading);
  const selectedModel = useAppStore((s) => s.selectedModel);
  const setServerInfo = useAppStore((s) => s.setServerInfo);
  const setSavings = useAppStore((s) => s.setSavings);
  const settings = useAppStore((s) => s.settings);
  const commandPaletteOpen = useAppStore((s) => s.commandPaletteOpen);
  const setCommandPaletteOpen = useAppStore((s) => s.setCommandPaletteOpen);
  const optInEnabled = useAppStore((s) => s.optInEnabled);
  const optInDisplayName = useAppStore((s) => s.optInDisplayName);
  const optInEmail = useAppStore((s) => s.optInEmail);
  const optInAnonId = useAppStore((s) => s.optInAnonId);
  const optInModalSeen = useAppStore((s) => s.optInModalSeen);
  const optInModalOpen = useAppStore((s) => s.optInModalOpen);
  const setOptInModalOpen = useAppStore((s) => s.setOptInModalOpen);
  const markOptInModalSeen = useAppStore((s) => s.markOptInModalSeen);
  const savings = useAppStore((s) => s.savings);

  // Apply the theme class to <html>.
  //
  // 'system' is RESOLVED here to an explicit `dark`/`light` class on purpose.
  // The stylesheet used to carry a second, duplicated copy of the dark
  // palette behind `prefers-color-scheme`; that is how two palettes of the
  // same brand end up disagreeing. One palette, written once, and this hook
  // is the single place that decides which half applies — including when the
  // OS flips while the app is open.
  useEffect(() => {
    const root = document.documentElement;
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const apply = () => {
      const resolved =
        settings.theme === 'dark' || settings.theme === 'light'
          ? settings.theme
          : media.matches
            ? 'dark'
            : 'light';
      root.classList.remove('dark', 'light');
      root.classList.add(resolved);
    };
    apply();
    // Only meaningful while following the system, but harmless otherwise.
    media.addEventListener('change', apply);
    return () => media.removeEventListener('change', apply);
  }, [settings.theme]);

  // Sync overlay conversations into the main app
  const importOverlay = useAppStore((s) => s.importOverlayConversation);
  useEffect(() => {
    if (!isTauri()) return;
    importOverlay();
    const interval = setInterval(importOverlay, 5000);
    return () => clearInterval(interval);
  }, [importOverlay]);

  // Fetch models on mount
  useEffect(() => {
    fetchModels()
      .then((m) => {
        setModels(m);
      })
      .catch(() => setModels([]))
      .finally(() => setModelsLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Fetch server info
  useEffect(() => {
    fetchServerInfo().then(setServerInfo).catch(() => {});
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Poll savings and optionally share to Supabase
  useEffect(() => {
    const refresh = () =>
      fetchSavings()
        .then((data) => {
          setSavings(data);
          if (optInEnabled && optInDisplayName && data) {
            const claudeEntry = data.per_provider.find(
              (p) => p.provider === 'claude-fable-5',
            );
            const dollarSavings = claudeEntry ? claudeEntry.total_cost : 0;
            const energySaved = data.per_provider.reduce(
              (sum, p) => sum + (p.energy_wh || 0),
              0,
            );
            const flopsSaved = data.per_provider.reduce(
              (sum, p) => sum + (p.flops || 0),
              0,
            );
            submitSavings({
              anon_id: optInAnonId,
              display_name: optInDisplayName,
              email: optInEmail,
              total_calls: data.total_calls,
              total_tokens: data.total_tokens,
              dollar_savings: dollarSavings,
              energy_wh_saved: energySaved,
              flops_saved: flopsSaved,
              token_counting_version: data.token_counting_version ?? 1,
            });
          }
        })
        .catch(() => {});
    refresh();
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  }, [optInEnabled, optInDisplayName, optInAnonId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Show opt-in modal on first visit
  useEffect(() => {
    if (!optInModalSeen) {
      setOptInModalOpen(true);
      markOptInModalSeen();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Fire model_changed when the user switches models. First mount is
  // not a "change" — only emit when both prev and current are real and
  // differ.
  useEffect(() => {
    const prev = prevModelRef.current;
    const curr = selectedModel || '';
    prevModelRef.current = curr;
    if (!prev || !curr || prev === curr) return;
    void (async () => {
      const [fromHash, toHash] = await Promise.all([
        hashId(prev),
        hashId(curr),
      ]);
      track('model_changed', {
        from_model_hash: fromHash,
        to_model_hash: toHash,
      });
    })();
  }, [selectedModel]);

  // app_opened — one-shot per app launch, fires after analytics has had
  // a chance to initialize. platform + version are super-properties
  // registered in analytics.ts initAnalytics, so no per-call props needed.
  useEffect(() => {
    const t = setTimeout(() => {
      track('app_opened', {});
    }, 500);
    return () => clearTimeout(t);
  }, []);

  const toggleSystemPanel = useAppStore((s) => s.toggleSystemPanel);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(!commandPaletteOpen);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'i') {
        e.preventDefault();
        toggleSystemPanel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [commandPaletteOpen, setCommandPaletteOpen, toggleSystemPanel]);


  if (!setupDone) {
    return <SetupScreen onReady={handleSetupReady} />;
  }

  return (
    <>
      <UpdateChecker />
      <Routes>
        <Route element={<Layout />}>
          {/*
            Five tabs. The same five the sovereign face carries, in the same
            order, from the same single writer (`components/Bianca/tabs.ts`) —
            two surfaces of one node must not be able to disagree about what
            the node's cast is.
          */}
          <Route index element={<Navigate to="/jarvis" replace />} />
          <Route path="trialog" element={<TrialogPage />} />
          <Route path="jarvis" element={<JarvisPage />} />
          <Route path="bianca" element={<BiancaPage />} />
          <Route path="urasil" element={<UrasilPage />} />
          <Route path="node" element={<NodeNetPage />} />

          {/*
            The old seven-route sidebar is folded into five tabs, but those
            URLs are already bookmarked, deep-linked from the desktop shell,
            and excluded from the PWA navigation fallback. They redirect rather
            than 404: deleting working software to make a tab bar prettier is
            not a trade this project makes. The map lives in tabs.ts beside the
            tab definitions it points into, so a tab can never be renamed
            without its old URL following.
          */}
          {Object.entries(LEGACY_ROUTES).map(([path, to]) => {
            // `to.tab` is a tab ID, not a URL. Navigating to the ID would be a
            // RELATIVE navigation — it happens to resolve correctly from `/`,
            // and resolves wrongly from anywhere nested. The path comes from
            // the same writer the tab bar uses, so a tab can never be renamed
            // without its old URL following it.
            const def = tabById(to.tab);
            const toPath = def?.path ?? '/jarvis';
            // The same rule the option strip uses: a tab's default option
            // writes nothing into the URL. Without this, `/` would land on
            // `/jarvis?sub=platform` while `/jarvis` — the URL the tab bar
            // itself produces — is the same screen with a cleaner address.
            // One rule, so a redirected URL and a clicked URL agree.
            const param = def ? subParam(def.subs, to.sub) : to.sub;
            return (
              <Route
                key={path}
                path={path}
                element={
                  <Navigate to={param ? `${toPath}?sub=${param}` : toPath} replace />
                }
              />
            );
          })}

          <Route path="*" element={<Navigate to="/jarvis" replace />} />
        </Route>
      </Routes>
      <Toaster position="bottom-right" />
      {commandPaletteOpen && <CommandPalette />}
      {optInModalOpen && (
        <OptInModal onClose={() => setOptInModalOpen(false)} />
      )}
    </>
  );
}
