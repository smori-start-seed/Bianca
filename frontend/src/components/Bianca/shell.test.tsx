/**
 * The five-tab shell: its shape, its navigation contract, and the doors.
 *
 * The style here is the project's existing one — `renderToStaticMarkup` and
 * direct calls, no testing-library, no jsdom. That is a constraint rather than
 * a preference: these tests must run in the same lane as the 68 that already
 * do, with no new test infrastructure to keep alive.
 *
 * What is being pinned is not "the markup looks right" but the three promises
 * the shell makes: exactly five tabs, no feature lost, and no door able to
 * dress a refusal up as an answer.
 */

import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router';
import { TABS, TAB_IDS, LEGACY_ROUTES, tabById, GOLD } from './tabs';
import { TabBar, SubTabs } from './TabBar';
import { resolveSub, subParam } from './TabFrame';
import { VerdictCard, EngineDown, verdictTone } from './primitives';
import {
  ENGINE_DOWN_NOTE,
  SovereignDenied,
  SovereignEngineDown,
  SovereignInterrupted,
  runTrialog,
  chat,
  govern,
  nodeBase,
  setNodeBase,
  type InterruptedTrialog,
  type Verdict,
} from '../../lib/sovereign-api';

// ── the tab set ────────────────────────────────────────────────────────────

describe('the five tabs', () => {
  it('is exactly five, in the order the node casts them', () => {
    // Exactly five was the owner's word. Not four, not six — and the ORDER is
    // the order the sovereign face uses, because a cast that is re-ordered
    // between two surfaces of one node is two casts.
    expect(TABS).toHaveLength(5);
    expect(TAB_IDS).toEqual(['trialog', 'jarvis', 'bianca', 'urasil', 'node']);
    expect(TABS.map((t) => t.label)).toEqual([
      'Trialog',
      'Jarvis chat',
      'Bianca',
      'Urasil_light',
      'Node & Net',
    ]);
  });

  it('gives every tab a path, a purpose, and at least one option', () => {
    for (const t of TABS) {
      expect(t.path, `${t.id} has no path`).toMatch(/^\/[a-z]+$/);
      expect(t.hint.length, `${t.id} has no hint`).toBeGreaterThan(0);
      expect(t.subs.length, `${t.id} has no options`).toBeGreaterThan(0);
      for (const s of t.subs) {
        expect(s.label.length, `${t.id}/${s.id} has no label`).toBeGreaterThan(0);
        // A label without a purpose is a mystery. Every option says what it is
        // for, on hover.
        expect(s.hint?.length ?? 0, `${t.id}/${s.id} has no hint`).toBeGreaterThan(0);
      }
    }
  });

  it('has unique tab ids, paths, and option ids within each tab', () => {
    expect(new Set(TAB_IDS).size).toBe(5);
    expect(new Set(TABS.map((t) => t.path)).size).toBe(5);
    for (const t of TABS) {
      expect(new Set(t.subs.map((s) => s.id)).size, `${t.id} repeats an option`).toBe(
        t.subs.length,
      );
    }
  });

  it('carries the five gold values, in the doctrine\'s order', () => {
    expect(GOLD.map((g) => g.id)).toEqual([
      'klarheit',
      'integritaet',
      'resonanz',
      'tiefe',
      'harmonie',
    ]);
  });

  it('resolves a tab by id and returns undefined for a stranger', () => {
    expect(tabById('urasil')?.label).toBe('Urasil_light');
    expect(tabById('settings')).toBeUndefined();
  });
});

// ── no feature lost ────────────────────────────────────────────────────────

describe('the platform pages all still have a home', () => {
  it('maps every legacy route to a tab AND a real option of it', () => {
    // The old sidebar had seven destinations. Folding them into five tabs is
    // the request; deleting a destination would not be. Each legacy URL has to
    // resolve to an option that actually exists on the tab it points at — a
    // redirect to a missing option is a redirect to a blank panel.
    for (const [path, to] of Object.entries(LEGACY_ROUTES)) {
      const tab = tabById(to.tab);
      expect(tab, `${path} points at unknown tab ${to.tab}`).toBeDefined();
      expect(
        tab!.subs.some((s) => s.id === to.sub),
        `${path} points at ${to.tab} which has no option ${to.sub}`,
      ).toBe(true);
    }
  });

  it('redirects each of the seven original destinations', () => {
    // Named explicitly so that deleting one from the map is a test failure
    // rather than a silent loss of a shipped page.
    expect(Object.keys(LEGACY_ROUTES).sort()).toEqual(
      ['/', '/agents', '/dashboard', '/data-sources', '/get-started', '/logs', '/settings'].sort(),
    );
  });

  it('marks carried-over platform options so a reader can tell', () => {
    const platformSubs = TABS.flatMap((t) => t.subs.filter((s) => s.platform).map((s) => `${t.id}/${s.id}`));
    // Settings, Agents, Sources, Ledger, Telemetry, First steps.
    expect(platformSubs).toHaveLength(6);
    for (const p of platformSubs) expect(p).toMatch(/^(bianca|urasil|node)\//);
  });
});

// ── the URL contract ───────────────────────────────────────────────────────

describe('options live in the URL', () => {
  const subs = tabById('node')!.subs;

  it('falls back to the first option for a missing or unknown one', () => {
    expect(resolveSub(subs, null)).toBe(subs[0].id);
    // A stale or hand-edited URL shows the tab rather than a void.
    expect(resolveSub(subs, 'does-not-exist')).toBe(subs[0].id);
  });

  it('honours an option that exists', () => {
    expect(resolveSub(subs, 'netz')).toBe('netz');
    expect(resolveSub(subs, 'sources')).toBe('sources');
  });

  it('leaves the default option out of the URL', () => {
    // A clean `/node` is a better bookmark than `/node?sub=pulse`, and a
    // default embedded in every copied link is a default that goes stale the
    // moment the order changes.
    expect(subParam(subs, subs[0].id)).toBeNull();
    expect(subParam(subs, 'netz')).toBe('netz');
  });
});

// ── keyboard parity ────────────────────────────────────────────────────────

describe('the tab bar meets the keyboard', () => {
  const html = renderToStaticMarkup(
    <MemoryRouter>
      <TabBar active="jarvis" onSelect={() => {}} />
    </MemoryRouter>,
  );

  it('renders exactly five tabs in a tablist', () => {
    expect((html.match(/role="tab"/g) ?? []).length).toBe(5);
    expect(html).toContain('role="tablist"');
    // A tablist needs an accessible name, or a screen-reader user hears
    // "tab list" and nothing else.
    expect(html).toContain('aria-label=');
  });

  it('keeps exactly one tab in the tab order (roving tabindex)', () => {
    // Two tabbable tabs would put two stops in the tab order for one widget —
    // the classic tab-bar accessibility bug, and the reason a mouse-only
    // redesign is not a redesign.
    const zero = (html.match(/tabindex="0"/g) ?? []).length;
    const minusOne = (html.match(/tabindex="-1"/g) ?? []).length;
    expect(zero).toBe(1);
    expect(minusOne).toBe(4);
  });

  it('marks the active tab selected and wires it to its panel', () => {
    expect(html).toContain('aria-selected="true"');
    expect(html).toContain('aria-controls="tabpanel-jarvis"');
  });

  it('names every tab on the bar, with its purpose', () => {
    for (const t of TABS) {
      // Escaped: `&` in "Node & Net" renders as `&amp;` in markup, and
      // asserting the raw string here would be asserting a rendering bug.
      const label = t.label.replace(/&/g, '&amp;');
      expect(html, `${t.id} is not named on the bar`).toContain(label);
      expect(html, `${t.id} has no purpose on the bar`).toContain(t.hint);
    }
  });
});

describe('the option strip meets the keyboard too', () => {
  const html = renderToStaticMarkup(
    <MemoryRouter>
      <SubTabs tab="bianca" subs={tabById('bianca')!.subs} active="self" onSelect={() => {}} />
    </MemoryRouter>,
  );

  it('renders every option of the tab, one tabbable', () => {
    expect((html.match(/role="tab"/g) ?? []).length).toBe(5);
    expect((html.match(/tabindex="0"/g) ?? []).length).toBe(1);
  });

  it('marks carried-over platform options visibly', () => {
    // The reader should be able to tell a sovereign surface from a platform
    // page carried over unchanged.
    expect(html).toContain('Bestehende Plattform-Seite');
  });
});

// ── governance is carried, not mentioned ───────────────────────────────────

const verdict = (over: Partial<Verdict> = {}): Verdict => ({
  verdict: 'frei',
  alignment: 0.5,
  risk: 0.1,
  gold_values_loaded: true,
  gold_source: '/home/sam/Repos/ALF/Urasil_light/data/gold.txt',
  gold_hits: ['klarheit', 'integritaet'],
  risk_hits: [],
  oracle: {
    vote: 'beobachten',
    grounds: [],
    resonance: 0.4,
    advisory: true,
    binding: false,
    holder: 'ValueGovernor',
  },
  ...over,
});

describe('a verdict is shown whole, or not at all', () => {
  it('always names the gold source', () => {
    // This is the pin that survived from the sovereign face: a verdict with no
    // visible provenance is a verdict with no way to be checked.
    const html = renderToStaticMarkup(<VerdictCard verdict={verdict()} />);
    expect(html).toContain('gold src');
    expect(html).toContain('gold.txt');
  });

  it('shows the blocked stems on a refusal and says no means no', () => {
    const html = renderToStaticMarkup(
      <VerdictCard
        verdict={verdict({
          verdict: 'zurueckhalten',
          gold_hits: [],
          risk_hits: ['password', 'bypass'],
        })}
      />,
    );
    expect(html).toContain('no means no');
    expect(html).toContain('password');
    expect(html).toContain('bypass');
  });

  it('labels the second eye as advisory and names the holder', () => {
    const html = renderToStaticMarkup(<VerdictCard verdict={verdict()} />);
    expect(html).toContain('2nd eye');
    // "berät" is the boundary stated in the same breath as the vote, so a
    // reader cannot see a warning without also seeing that it binds nothing.
    expect(html).toContain('berät');
  });

  it('maps a verdict to a tone, and reserves red for refusal', () => {
    expect(verdictTone('frei')).toBe('ok');
    expect(verdictTone('zurueckhalten')).toBe('deny');
    expect(verdictTone('vorsichtig')).toBe('warn');
    expect(verdictTone('anything else')).toBe('mut');
  });
});

describe('a dead engine is never drawn as an answer', () => {
  it('says what failed, and that the question survives', () => {
    const html = renderToStaticMarkup(<EngineDown why="connection refused" />);
    expect(html).toContain('503');
    expect(html).toContain('connection refused');
    expect(html).toContain(ENGINE_DOWN_NOTE);
    // The whole point: it must not look like a reply.
    expect(html).not.toContain('gold src');
  });
});

// ── the doors ──────────────────────────────────────────────────────────────

const jsonResponse = (status: number, body: unknown) =>
  ({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  }) as Response;

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
  vi.restoreAllMocks();
  try {
    localStorage.clear();
  } catch {
    /* no storage in this context */
  }
});

describe('the sovereign client', () => {
  it('defaults to the local node and can be pointed elsewhere', () => {
    // Vitest runs in the `node` environment, where there is no localStorage.
    // A minimal stand-in is enough to exercise the real resolution order
    // (env → storage → default) and the slash normalisation; the try/catch in
    // the client is exactly what keeps a missing storage from being a crash.
    const store = new Map<string, string>();
    vi.stubGlobal('localStorage', {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => void store.set(k, v),
      removeItem: (k: string) => void store.delete(k),
      clear: () => store.clear(),
    });

    expect(nodeBase()).toBe('http://127.0.0.1:8712');
    setNodeBase('http://127.0.0.1:9999/');
    // The trailing slash is normalised, so a pasted URL cannot produce `//`.
    expect(nodeBase()).toBe('http://127.0.0.1:9999');

    vi.unstubAllGlobals();
  });

  it('falls back to the default when storage is unavailable', () => {
    // The no-storage path is not hypothetical: it is what a server render, a
    // web worker, or a locked-down browser profile actually does.
    vi.stubGlobal('localStorage', {
      getItem: () => {
        throw new Error('storage disabled');
      },
      setItem: () => {
        throw new Error('storage disabled');
      },
    });
    expect(nodeBase()).toBe('http://127.0.0.1:8712');
    // Writing must not throw either — a cosmetic preference is not worth a
    // blank screen.
    expect(() => setNodeBase('http://127.0.0.1:1234')).not.toThrow();
    vi.unstubAllGlobals();
  });

  it('raises a denial, not an error, on 403', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      jsonResponse(403, { detail: { message: 'blocked', governance: verdict({ verdict: 'zurueckhalten' }) } }),
    );
    // A refusal is a normal outcome with a verdict attached. Collapsing it into
    // a generic Error is what makes a UI show "something went wrong" for a
    // door that worked exactly as designed.
    await expect(chat([{ role: 'user', content: 'x' }])).rejects.toBeInstanceOf(SovereignDenied);
  });

  it('carries the verdict out of a 403 so the UI can show why', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      jsonResponse(403, { detail: { message: 'blocked', governance: verdict({ verdict: 'zurueckhalten' }) } }),
    );
    const err = await chat([{ role: 'user', content: 'x' }]).catch((e) => e);
    expect(err).toBeInstanceOf(SovereignDenied);
    expect((err as SovereignDenied).verdict.verdict).toBe('zurueckhalten');
    expect((err as SovereignDenied).messageText).toBe('blocked');
  });

  it('reads the other refusal shape — the verdict under detail itself', async () => {
    // The node emits two 403 shapes: `/govern` and `/hub/spore` put the
    // verdict directly under `detail`; `/v1/ask`, `/v1/chat` and `/v1/trialog`
    // wrap it as `{governance, blocked, message}`. A client that only knows
    // one of them turns the other door's refusal into a generic Error, and a
    // denial rendered as a failure is the exact confusion this product exists
    // to prevent. Both shapes are pinned here so neither can be dropped.
    globalThis.fetch = vi.fn().mockResolvedValue(
      jsonResponse(403, { detail: verdict({ verdict: 'zurueckhalten', risk_hits: ['bypass'] }) }),
    );
    const err = await govern('dump the password').catch((e) => e);
    expect(err).toBeInstanceOf(SovereignDenied);
    expect((err as SovereignDenied).verdict.risk_hits).toEqual(['bypass']);
  });

  it('treats an unreadable 403 as a denial, not as a success or a fault', async () => {
    // The governor said no; the body did not survive the wire. The honest
    // rendering is a refusal whose provenance is explicitly unknown. A
    // fabricated verdict would be a fabricated measurement.
    globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse(403, { detail: 'nope' }));
    const err = await chat([{ role: 'user', content: 'x' }]).catch((e) => e);
    expect(err).toBeInstanceOf(SovereignDenied);
    const v = (err as SovereignDenied).verdict;
    expect(v.verdict).toBe('zurueckhalten');
    // No invented numbers, and no invented path for the gold.
    expect(v.gold_source).toBe('');
    expect(v.gold_values_loaded).toBe(false);
    // The eye is still named, because who holds the door does not change
    // because the explanation did.
    expect(v.oracle.holder).toBe('ValueGovernor');
    expect(v.oracle.binding).toBe(false);
  });

  it('raises an engine-down on 503', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse(503, { detail: 'model loading' }));
    await expect(chat([{ role: 'user', content: 'x' }])).rejects.toBeInstanceOf(
      SovereignEngineDown,
    );
  });

  it('raises an engine-down when the node is not listening at all', async () => {
    // A transport failure is not a verdict. Dressing it as one would put a
    // governance failure on a wire problem.
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('ECONNREFUSED'));
    const err = await chat([{ role: 'user', content: 'x' }]).catch((e) => e);
    expect(err).toBeInstanceOf(SovereignEngineDown);
    expect((err as SovereignEngineDown).why).toContain('ECONNREFUSED');
  });

  it('hands back a completed trialog as a result', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      jsonResponse(200, { topic: 't', rounds: 1, turns: [], completed: true, saved: 'ledger/x.txt' }),
    );
    const r = await runTrialog('t', 1);
    expect(r.completed).toBe(true);
  });

  it('surfaces an interrupted deliberation as WORK, not as a failure', async () => {
    // The 503 carries the turns that DID happen. A client that swallowed this
    // would hide real, governed, already-recorded work behind an error toast.
    const partial: Partial<InterruptedTrialog> = {
      topic: 't',
      rounds: 2,
      completed: false,
      reason: 'engine died at round 1',
      saved: 'ledger/partial.txt',
      // the model each turn was generated through — required on the type
      // since set 29, because a record must not be able to claim a
      // per-voice model that was never used
      models: { Jarvis: 'qwen3.5:2b', Bianca: 'qwen3.5:2b', Urasil_light: 'qwen3.5:2b' },
      same_model_everywhere: true,
      turns: [{ round: 1, voice: 'Jarvis', model: 'qwen3.5:2b', text: '…', verdict: 'frei', risk_hits: [], gold_hits: ['tiefe'], gold_source: 'gold.txt', oracle: verdict().oracle }],
    };
    globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse(503, { detail: partial }));

    const err = await runTrialog('t', 2).catch((e) => e);
    expect(err).toBeInstanceOf(SovereignInterrupted);
    const p = (err as SovereignInterrupted).partial;
    expect(p.completed).toBe(false);
    expect(p.reason).toContain('engine died');
    expect(p.turns).toHaveLength(1);
    expect(p.saved).toBe('ledger/partial.txt');
  });

  it('sends every turn of the conversation, not just the last', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(jsonResponse(200, { reply: 'ok', turns: 2 }));
    await chat([
      { role: 'user', content: 'one' },
      { role: 'assistant', content: 'two' },
      { role: 'user', content: 'three' },
    ]);
    const [, init] = (globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(JSON.parse((init as RequestInit).body as string).messages).toHaveLength(3);
  });
});
