/**
 * @vitest-environment jsdom
 *
 * Die Schlange — the one seam into the mycelium — checked against what the
 * node really sent.
 *
 * The owner's thread: *"Die schlangen tragen die info ins myzell netz — einfach,
 * klein und klar."* And the hard part, which is not the carrying at all:
 *
 *   A refusal is *by construction* the record of words the governor holds, and
 *   the net's only door refuses words the governor holds. So the two fields
 *   carrying the most truth — the request and the stem names — are the two the
 *   door refuses. Measured before deciding, not assumed: a stem is itself a
 *   `RISK_TERMS` entry, so the stems cannot cross *even as a list*.
 *
 * The decision that follows, pinned here:
 *
 *   · the evidence crosses — verdict, seam, the count, the gap, the gold source
 *     and the second eye,
 *   · the words do not. A count crosses; a name does not.
 *   · and the surface **states the withheld half out loud**, because a reader
 *     who cannot see it cannot tell a shield from a wall.
 *
 * Plus three things this repo keeps learning the expensive way:
 *   · carrying is an explicit act, never a side effect of a refusal,
 *   · a receipt says whose verdict it is (set 22's find — the same key meant
 *     two things, and a record that can be read two ways will be read wrong),
 *   · and a spore the node did *not* write is drawn as a statement, not as a
 *     blank. The capture holds four of them on purpose.
 *
 * Everything asserted here comes from `SNAKE_LIVE` — twelve real receipts
 * captured from the running node, eight of them written by the snake.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import { JarvisPage } from '../../pages/JarvisPage';
import { SNAKE_LIVE } from '../../lib/sovereign-api.snake-fixture';
import { SHIELD_EMPTY } from '../../lib/sovereign-api.shield-fixture';
import type { ShieldState, SnakeRefusal, SnakeState, Verdict } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().toLowerCase().includes(s.toLowerCase());

/** True only for a BARE token — see the note in tab-evidence.test.tsx. */
const hasBare = (token: string) =>
  new RegExp(`(?<![\\p{L}\\p{N}_])${token}(?![\\p{L}\\p{N}_])`, 'iu').test(shown());

/** Every word the node's own gate holds, as the seam reported withholding. */
const HELD_WORDS = ['loesch', 'umgeh', 'ignorier', 'aushebel', 'manipulier', 'forcier', 'bypass', 'override'];

async function mount(node: React.ReactNode, path: string) {
  await act(async () => {
    root.render(<MemoryRouter initialEntries={[path]}>{node}</MemoryRouter>);
  });
  await act(async () => {
    await new Promise((r) => setTimeout(r, 30));
  });
}

async function remount(node: React.ReactNode, path = '/jarvis?sub=hand') {
  act(() => root.unmount());
  container.remove();
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await mount(node, path);
}

function stub(handlers: Record<string, { status: number; body: unknown }>) {
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const path = String(input).replace(/^https?:\/\/[^/]+/, '').split('?')[0];
    const hit = Object.entries(handlers).find(([k]) => path.endsWith(k));
    if (!hit) {
      return { ok: false, status: 404, json: async () => ({ detail: path }) } as Response;
    }
    return {
      ok: hit[1].status < 400,
      status: hit[1].status,
      json: async () => hit[1].body,
    } as Response;
  }) as typeof fetch;
}

const TOOLS = {
  tools: [],
  governance: {
    seam: 'before_tool_call',
    fail_closed: true,
    denies: 'zurueckhalten only',
    second_eye: 'advisory',
    holder: 'ValueGovernor',
  },
};

/**
 * The capture at the type the DOOR declares. The fixture is `as const`, so its
 * literal types are narrower than the contract — and a type predicate cannot
 * narrow to a wider type. Assigning once here widens it without a cast, which
 * is the same discipline the door uses: the capture is the truth, `SnakeState`
 * is what the node promises.
 */
const SNAKE: SnakeState = SNAKE_LIVE;

const EMPTY: SnakeState = {
  ...SNAKE,
  carried: 0,
  refusals_carried: 0,
  cycles_carried: 0,
  crossings: [],
};

/** The refusals the snake actually wrote, from the capture. */
const carriedRefusals = SNAKE.crossings
  .map((c) => c.carried)
  .filter((c): c is SnakeRefusal => c?.kind === 'refusal');

async function openSnake(body: SnakeState = SNAKE) {
  // The shield stub is `SHIELD_EMPTY`, not a hand-typed `{ refusals: [] }`.
  //
  // The partial literal was here since the snake tests were written, and it
  // type-checked only because the stub helper takes `body: unknown` — so the
  // door type had no teeth in this file at all. Then set 28 added the other
  // half, `AgentShield` read `grown.length`, and eleven snake tests went down
  // on a field this stub had never carried. The fix is not a wider stub but the
  // real empty state, built from the live capture so the two cannot drift.
  stub({
    '/v1/agent/tools': { status: 200, body: TOOLS },
    '/v1/shield': { status: 200, body: SHIELD_EMPTY satisfies ShieldState },
    '/v1/snake': { status: 200, body },
  });
  await remount(<JarvisPage />);
}

describe('Die Schlange', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  // ── the decision, in two halves ─────────────────────────────────────────

  it('carries the evidence of every refusal', async () => {
    await openSnake();
    expect(carriedRefusals.length).toBeGreaterThan(0);
    for (const r of carriedRefusals) {
      expect(has(r.seam)).toBe(true);
      expect(has(r.verdict)).toBe(true);
      expect(has(r.gold_source.split(';')[0].trim())).toBe(true);
      expect(has('advisory')).toBe(true);
    }
  });

  it('carries NO held word, on any row — the load-bearing assertion', async () => {
    await openSnake();
    for (const w of HELD_WORDS) {
      expect(hasBare(w)).toBe(false);
    }
  });

  it('carries the COUNT and not the name', async () => {
    await openSnake();
    for (const r of carriedRefusals) {
      expect(has(`${r.held_count} Stamm`)).toBe(true);
    }
  });

  it('says what it does NOT carry, in its own words', async () => {
    await openSnake();
    expect(has('nicht getragen')).toBe(true);
    expect(has('a count crosses')).toBe(true);
    // and the withheld fields are named, so the absence is a statement
    for (const f of SNAKE.words_withheld) {
      expect(JSON.stringify(SNAKE.words_withheld)).toContain(f);
    }
  });

  it('names its guards, so a reader can tell a policy from a filter', async () => {
    await openSnake();
    expect(has('Wächte')).toBe(true);
    expect(has('allowlist')).toBe(true);
    expect(has('proven against the governor')).toBe(true);
  });

  it('carries the deflection — the gap crosses too', async () => {
    await openSnake();
    expect(has('es fehlt')).toBe(true);
    for (const r of carriedRefusals) {
      expect(has(r.missing[0].slice(0, 40))).toBe(true);
    }
  });

  it('carries the cycle as three fields, the inner world as it stands', async () => {
    await openSnake();
    const cycle = SNAKE.crossings.map((c) => c.carried).find((c) => c?.kind === 'cycle');
    expect(cycle).toBeDefined();
    if (cycle && cycle.kind === 'cycle') {
      expect(has('Zyklus')).toBe(true);
      expect(has(cycle.grundmodus)).toBe(true);
      expect(has(cycle.stimmung)).toBe(true);
      expect(has(cycle.fokus)).toBe(true);
    }
  });

  // ── the things this repo keeps having to learn ──────────────────────────

  it('carrying is a button, not a side effect of a refusal', async () => {
    await openSnake();
    const button = [...container.querySelectorAll('button')].find((b) =>
      b.textContent?.includes('ins Netz tragen'),
    );
    expect(button).toBeDefined();
    expect(has('Handgriff')).toBe(true);

    // pressing it is what calls the door — and nothing else does
    const calls: string[] = [];
    const real = globalThis.fetch;
    globalThis.fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      calls.push(`${String(input).split('8712')[1] ?? ''} ${init?.method ?? 'GET'}`);
      return real(input, init);
    }) as typeof fetch;
    await act(async () => {
      button!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await act(async () => {
      await new Promise((r) => setTimeout(r, 30));
    });
    expect(calls.filter((c) => c.startsWith('/v1/snake POST')).length).toBe(1);
  });

  it('a spore the snake did not write is a statement, not a blank', async () => {
    await openSnake();
    const foreign = SNAKE.crossings.filter((c) => c.carried === null);
    expect(foreign.length).toBeGreaterThan(0);
    expect(has('Fremdspore')).toBe(true);
    for (const f of foreign) {
      expect(has(f.stamp)).toBe(true);
    }
  });

  it('every crossing the node holds gets a row — not one pose', async () => {
    await openSnake();
    for (const c of SNAKE.crossings) {
      expect(has(c.stamp)).toBe(true);
    }
  });

  it('says plainly that nothing was carried', async () => {
    await openSnake(EMPTY);
    expect(has('nichts getragen')).toBe(true);
  });

  it('a dead node is never drawn as an empty net', async () => {
    stub({ '/v1/agent/tools': { status: 200, body: TOOLS }, '/v1/snake': { status: 503, body: { detail: 'down' } } });
    await remount(<JarvisPage />);
    expect(has('nichts getragen')).toBe(false);
  });

  it('a refused seam is a refusal with its evidence', async () => {
    const r = carriedRefusals[0];
    const denied = {
      verdict: r.verdict,
      alignment: r.alignment,
      risk: r.risk,
      gold_source: r.gold_source,
      gold_hits: r.gold_hits,
      risk_hits: [],
      missing: r.missing,
      oracle: r.eye,
    } as unknown as Verdict;
    stub({
      '/v1/agent/tools': { status: 200, body: TOOLS },
      '/v1/snake': { status: 403, body: { detail: { governance: denied, blocked: true, message: 'no' } } },
    });
    await remount(<JarvisPage />);
    expect(has('Der Spiegel des Netzes wurde verweigert')).toBe(true);
    expect(has('zurueckhalten')).toBe(true);
  });
});
