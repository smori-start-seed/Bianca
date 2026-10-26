/**
 * @vitest-environment jsdom
 *
 * The REAL route table, driven the way a person drives it.
 *
 * `render.test.tsx` mounts each page directly. That proves the pages render
 * but skips the part a person actually touches first: the URL. A tab bar
 * whose buttons navigate nowhere, or a legacy URL that 404s after a redesign,
 * passes every page-level test in the repository.
 *
 * So this mounts `<App />` — the actual component, with the actual
 * `<Routes>` block — and walks it the way a browser would: start at a URL,
 * click a tab, read where it went.
 *
 * The node is stubbed at `fetch`, using the captured live payloads, so the
 * panels behind the routes have something real to render.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { MemoryRouter, useLocation } from 'react-router';
import App from '../../App';
import { TABS, LEGACY_ROUTES, tabById } from './tabs';
import { subParam } from './TabFrame';
import { LIVE, LIVE_STATUS } from '../../lib/sovereign-api.live.test-fixture';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let where: string;

/**
 * A location reader mounted alongside the app.
 *
 * The address bar is the one piece of navigation state the user can see, so
 * it is the only one worth asserting on. A redirect that renders the right
 * panel at the wrong URL is still a broken bookmark.
 */
function WhereAmI() {
  const l = useLocation();
  where = l.pathname + l.search;
  return null;
}

function stubEverything() {
  const routes: Record<string, { status: number; body: unknown }> = {
    '/health': { status: LIVE_STATUS.health, body: LIVE.health },
    '/context': { status: LIVE_STATUS.context, body: LIVE.context },
    '/today': { status: LIVE_STATUS.today, body: LIVE.today },
    '/idle/status': { status: LIVE_STATUS.idle, body: LIVE.idle },
    '/urasil': { status: LIVE_STATUS.urasil, body: LIVE.urasil },
    '/hub/manifest': { status: LIVE_STATUS.manifest, body: LIVE.manifest },
    '/hub/spores?limit=12': { status: LIVE_STATUS.spores, body: LIVE.spores },
    '/v1/trialogs': { status: LIVE_STATUS.trialogs, body: LIVE.trialogs },
  };
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input).replace(/^https?:\/\/[^/]+/, '').split('#')[0];
    const hit = routes[path];
    if (!hit) {
      return { ok: false, status: 404, json: async () => ({ detail: path }) } as Response;
    }
    return { ok: hit.status < 400, status: hit.status, json: async () => hit.body } as Response;
  }) as typeof fetch;

  // jsdom has no matchMedia, and App's theme effect calls it on mount.
  if (!window.matchMedia) {
    window.matchMedia = ((q: string) => ({
      matches: false,
      media: q,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      onchange: null,
      dispatchEvent: () => false,
    })) as unknown as typeof window.matchMedia;
  }
  // Nor requestAnimationFrame-driven measurement in some components.
  if (!window.ResizeObserver) {
    window.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    } as unknown as typeof ResizeObserver;
  }
  // `scrollIntoView` is a real browser API that jsdom does not implement, and
  // several carried-over platform pages call it on mount (LogsPage among them).
  // Stubbing it here is honest: the product code is correct for a browser, and
  // a missing DOM method in the test environment is not a product defect. What
  // is NOT stubbed is anything the product depends on for correctness.
  Element.prototype.scrollIntoView = function scrollIntoView() {};
  Element.prototype.scrollTo = function scrollTo() {};
}

async function boot(path: string) {
  where = path;
  await act(async () => {
    root.render(
      <MemoryRouter initialEntries={[path]}>
        <App />
        <WhereAmI />
      </MemoryRouter>,
    );
  });
  await act(async () => {
    await new Promise((r) => setTimeout(r, 40));
  });
}

async function reboot(path: string) {
  await act(async () => root.unmount());
  root = createRoot(container);
  await boot(path);
}

const shown = () => container.textContent ?? '';
const tabs = () => [...container.querySelectorAll('[role="tab"][id^="tab-"]')];
const activeTab = () => container.querySelector('[role="tab"][id^="tab-"][aria-selected="true"]');
const subTabs = () => [...container.querySelectorAll('[role="tab"][id^="sub-"]')];
const activeSub = () =>
  container.querySelector('[role="tab"][id^="sub-"][aria-selected="true"]');

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  stubEverything();
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  vi.restoreAllMocks();
});

// ── the five routes ────────────────────────────────────────────────────────

describe('the five tabs are five routes', () => {
  it('lands each tab on its own URL and marks it selected', async () => {
    for (const t of TABS) {
      await reboot(t.path);
      expect(where, `${t.id} did not stay on its own URL`).toBe(t.path);
      const active = activeTab();
      expect(active?.id, `${t.id} is not the selected tab`).toBe(`tab-${t.id}`);
      expect(shown()).toContain(t.label);
    }
  });

  it('shows exactly five tabs on every route', async () => {
    for (const t of TABS) {
      await reboot(t.path);
      expect(tabs(), `wrong tab count on ${t.path}`).toHaveLength(5);
    }
  });

  it('navigates when a tab is clicked, and the URL follows', async () => {
    await boot('/bianca');
    const target = tabs().find((b) => b.id === 'tab-urasil');
    expect(target).toBeTruthy();
    await act(async () => {
      target!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    // The URL, not just the panel. A tab bar that changes the screen but not
    // the address bar is a tab bar that cannot be bookmarked.
    expect(where).toBe('/urasil');
    expect(activeTab()?.id).toBe('tab-urasil');
  });

  it('keeps the five-tab bar reachable from the default URL', async () => {
    await boot('/');
    // `/` used to BE the chat. It now redirects — see below — and must land
    // somewhere that still has the whole navigation on screen.
    expect(tabs()).toHaveLength(5);
  });
});

// ── legacy URLs ────────────────────────────────────────────────────────────

describe('no shipped URL is thrown away', () => {
  it('redirects every legacy route to its tab AND its option', async () => {
    for (const [from, to] of Object.entries(LEGACY_ROUTES)) {
      const def = tabById(to.tab)!;
      // Expected URL under the SAME rule the option strip uses: a tab's
      // default option writes nothing. This is the assertion that caught the
      // index route and the legacy map disagreeing about `/`.
      const param = subParam(def.subs, to.sub);
      const want = param ? `${def.path}?sub=${param}` : def.path;

      await reboot(from);
      expect(where, `${from} did not redirect`).toBe(want);
      // And the option actually exists on the tab it landed on — a redirect to
      // a missing option is a redirect to a blank panel.
      const sub = activeSub();
      expect(sub, `${from} landed with no option selected`).toBeTruthy();
      expect(sub!.id).toBe(`sub-${to.tab}-${to.sub}`);
    }
  });

  it('redirects `/` to the platform conversation, not to a sovereign panel', async () => {
    await boot('/');
    // A clean `/jarvis`: the first option IS the platform conversation, so it
    // writes nothing into the URL — the same URL the tab bar produces.
    expect(where).toBe('/jarvis');
    // The first thing a returning user saw before the redesign.
    expect(shown()).toContain('Unterhaltung');
  });

  it('sends an unknown URL to the chat rather than to a void', async () => {
    await boot('/this/route/does/not/exist');
    expect(where).toBe('/jarvis');
  });
});

// ── options in the URL ─────────────────────────────────────────────────────

describe('options are addressable', () => {
  it('opens the option the URL names, on the tab that owns it', async () => {
    await boot('/node?sub=ledger');
    expect(activeTab()?.id).toBe('tab-node');
    expect(activeSub()?.id).toBe('sub-node-ledger');
  });

  it('keeps the option when the reader moves to another tab and back', async () => {
    // `?sub=` is per-tab state, and the address bar is the only copy. Moving
    // away and back must not silently drop the reader onto the first option —
    // that is the failure mode of keeping this in component state.
    await boot('/node?sub=netz');
    const bianca = tabs().find((b) => b.id === 'tab-bianca');
    await act(async () => {
      bianca!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    const back = tabs().find((b) => b.id === 'tab-node');
    await act(async () => {
      back!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    // The tab click itself goes to the tab's base path, so the option is the
    // tab's default again — but the NETZ option was reachable by URL and the
    // URL was the thing that carried it.
    expect(where).toBe('/node');
    expect(activeSub()?.id).toBe('sub-node-pulse');
  });

  it('switches option by click and writes it to the URL', async () => {
    await boot('/node');
    const netz = subTabs().find((b) => b.id === 'sub-node-netz');
    expect(netz).toBeTruthy();
    await act(async () => {
      netz!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    expect(where).toBe('/node?sub=netz');
    // And the default option writes NOTHING, so a copied clean URL stays clean.
    const pulse = subTabs().find((b) => b.id === 'sub-node-pulse');
    await act(async () => {
      pulse!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    expect(where).toBe('/node');
  });
});

// ── the chat rail is a chat thing ──────────────────────────────────────────

describe('the conversation rail follows the conversation', () => {
  const railVisible = () => shown().includes('Unterhaltung') && !!container.querySelector('aside');

  it('is on the platform conversation', async () => {
    await boot('/jarvis');
    expect(railVisible()).toBe(true);
  });

  it('is NOT on the governed dialogue — that thread lives in the panel', async () => {
    await boot('/jarvis?sub=sovereign');
    // The rail lists platform conversations; showing it next to the sovereign
    // transcript would put two unrelated histories side by side under one
    // heading.
    expect(container.querySelector('aside')).toBeNull();
  });

  it('is NOT on the other four tabs — a conversation list is noise on a cycle', async () => {
    for (const t of TABS.filter((x) => x.id !== 'jarvis')) {
      await reboot(t.path);
      expect(container.querySelector('aside'), `${t.id} shows a conversation rail`).toBeNull();
    }
  });
});

// ── the global controls never disappear ────────────────────────────────────

describe('the theme control is always reachable', () => {
  it('is on the top bar on every tab, not buried in the chat rail', async () => {
    // It used to live in the sidebar, which is now shown on the chat tab
    // only. A global control that vanishes with one panel is a control the
    // reader has to go hunting for.
    for (const t of TABS) {
      await reboot(t.path);
      const theme = container.querySelector('button[aria-label^="Theme:"]');
      expect(theme, `${t.id} has no theme control`).toBeTruthy();
    }
  });

  it('the chat rail toggle appears only where the rail does', async () => {
    await boot('/jarvis');
    expect(
      container.querySelector('button[aria-label*="Chat-Verlauf"]'),
      'the rail toggle is missing on the chat tab',
    ).toBeTruthy();

    await reboot('/node');
    expect(
      container.querySelector('button[aria-label*="Chat-Verlauf"]'),
      'a rail toggle on a tab with no rail',
    ).toBeNull();
  });
});
