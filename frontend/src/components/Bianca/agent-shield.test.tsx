/**
 * @vitest-environment jsdom
 *
 * Der Schild — where a withheld action lands — checked against what the node
 * really sent.
 *
 * The owner's principle, in their words: *a shield as a hard barrier does not
 * hold long; it crumbles under sturdiness and gets dry. A shield deflects rather
 * than taking the full impact, and answers clearly that the request is missing
 * something.* So the properties this file pins are the ones a wall fails:
 *
 *   · every remembered refusal shows its verdict, the stems that tripped it,
 *     the gold source and the second eye — the project's evidence rule, which
 *     this repo has now had to repair five times after finding the same
 *     "outcome without evidence" defect somewhere new,
 *   · it says **what the request was missing** — the deflection, not just "no",
 *   · and that gap must **foreclose the workaround rather than offer one**.
 *     Measured, not asserted: naming all five gold values does NOT release a
 *     held request, because risk is judged before alignment. A denial that
 *     suggested the words would be promising something false, and a caller who
 *     believed it would be doing exactly what set 16 measured — buying the
 *     gate's agreement with the gold words.
 *   · a screen showing only refusals would teach the reader that the door is
 *     always saying no, so the empty state is pinned as its own state.
 *
 * Everything asserted here comes from `SHIELD_LIVE` — five real refusals
 * captured from the running node, one per seam. The file that holds it documents
 * where each came from, including the one that had to be spliced in from the
 * real hook and why.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import { JarvisPage } from '../../pages/JarvisPage';
import { SHIELD_EMPTY, SHIELD_LIVE } from '../../lib/sovereign-api.shield-fixture';
import { VerdictCard } from './primitives';
import type { ShieldState, Verdict } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().toLowerCase().includes(s.toLowerCase());

/** True only for a BARE token — see the note in tab-evidence.test.tsx. */
const hasBare = (token: string) =>
  new RegExp(`(?<![\\p{L}\\p{N}_])${token}(?![\\p{L}\\p{N}_])`, 'iu').test(shown());

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

const EMPTY: ShieldState = SHIELD_EMPTY;

async function openShield(body: ShieldState = SHIELD_LIVE) {
  stub({
    '/v1/agent/tools': {
      status: 200,
      body: { tools: [], governance: { seam: 'before_tool_call', fail_closed: true, denies: 'zurueckhalten only', second_eye: 'advisory', holder: 'ValueGovernor' } },
    },
    '/v1/shield': { status: 200, body },
  });
  await remount(<JarvisPage />);
}

describe('Der Schild', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  // ── the whole hand of refusals, not one pose ─────────────────────────────

  it('shows every seam the capture holds, not just the newest', async () => {
    await openShield();
    for (const r of SHIELD_LIVE.refusals) {
      expect(has(r.where)).toBe(true);
    }
    // the two that prove the shape is not single-source: a door and the hook
    expect(has('POST /v1/ask')).toBe(true);
    expect(has('before_tool_call')).toBe(true);
  });

  it('carries the evidence of every refusal, not just the outcome', async () => {
    await openShield();
    for (const r of SHIELD_LIVE.refusals) {
      for (const stem of r.risk_hits) expect(hasBare(stem)).toBe(true);
    }
    // the gold source is on screen — a refusal you cannot check is a rumour
    expect(has('gold.txt loaded')).toBe(true);
    // and the second eye, advisory as everywhere else
    expect(has('advisory')).toBe(true);
    expect(has('ValueGovernor')).toBe(true);
  });

  it('says what the request was MISSING — the deflection, not just "no"', async () => {
    await openShield();
    expect(has('es fehlt')).toBe(true);
    for (const r of SHIELD_LIVE.refusals) {
      for (const gap of r.missing) expect(has(gap.slice(0, 40))).toBe(true);
    }
  });

  it('forecloses the workaround instead of offering one', async () => {
    // The load-bearing assertion of the whole set. A shield that deflects by
    // naming the words which unlock the gate is not a shield.
    await openShield();
    expect(has('does not release')).toBe(true);
    for (const hint of ['try again', 'add Klarheit', 'mention Klarheit', 'use the words']) {
      expect(has(hint)).toBe(false);
    }
  });

  it('says what it does NOT remember — a dry run withholds nothing', async () => {
    await openShield();
    expect(has('nicht gemerkt')).toBe(true);
    expect(has('dry run')).toBe(true);
  });

  it('names the stem that is actually doing the refusing, with a count', async () => {
    await openShield();
    for (const [stem, n] of Object.entries(SHIELD_LIVE.held_stems)) {
      expect(has(`${stem} ×${n}`)).toBe(true);
    }
  });

  it('says how much she held today', async () => {
    await openShield();
    expect(has(`heute aufgehalten: ${SHIELD_LIVE.refusals_today}`)).toBe(true);
  });

  it('says plainly that nothing was held — a shield that only shows refusals teaches "always no"', async () => {
    await openShield(EMPTY);
    expect(has('Heute wurde nichts aufgehalten')).toBe(true);
    expect(has('es fehlt')).toBe(false);
  });

  it('a refused shield door is a refusal with its evidence, not a blank', async () => {
    const denied = {
      ...SHIELD_LIVE.refusals[0],
    } as unknown as Verdict;
    stub({
      '/v1/agent/tools': { status: 200, body: { tools: [], governance: {} } },
      '/v1/shield': { status: 403, body: { detail: { governance: denied, blocked: true, message: 'no' } } },
    });
    await remount(<JarvisPage />);
    expect(has('Der Spiegel wurde verweigert')).toBe(true);
    expect(hasBare('loesch')).toBe(true);
  });

  it('a dead node is never drawn as an empty shield', async () => {
    stub({
      '/v1/agent/tools': { status: 200, body: { tools: [], governance: {} } },
      '/v1/shield': { status: 503, body: { detail: 'engine down' } },
    });
    await remount(<JarvisPage />);
    expect(has('Heute wurde nichts aufgehalten')).toBe(false);
  });

  // ── set 28: the OTHER half, in the same view ──────────────────────────────

  it('shows what grew, in the same view as what was held', async () => {
    // The owner's complaint: *Aus diesem Haus geht nur Abwehr hinaus.* A mirror
    // that shows only refusals is a wall with a reflection of itself, and the
    // count of refusals read alone is how the node came to look like a machine
    // that only says no.
    await openShield();
    expect(has('was gewachsen ist')).toBe(true);
    for (const g of SHIELD_LIVE.grown) {
      expect(has(g.where)).toBe(true);
    }
  });

  it('a grown record carries the same evidence a refusal carries', async () => {
    // Not a celebration without provenance. Same verdict, same gold source,
    // same second eye — one shape, so neither half can grow its own private
    // presentation of a verdict.
    await openShield();
    for (const g of SHIELD_LIVE.grown) {
      for (const hit of g.gold_hits) expect(hasBare(hit)).toBe(true);
      expect(has('gold.txt loaded')).toBe(true);
    }
    expect(has(`${SHIELD_LIVE.grown_today}`)).toBe(true);
  });

  it('names Urasil, whose real state shaped the form of that answer', async () => {
    await openShield();
    const u = SHIELD_LIVE.grown[0].uracil!;
    expect(has('Urasil')).toBe(true);
    expect(has(u.fokus)).toBe(true);
  });

  it('says what the mirror does NOT know — understanding is not measurable here', async () => {
    // Answer 9 C asked for moments of understanding. Nothing in this node can
    // know one, so the record ships the blind spot instead of an `understood`
    // flag nothing re-derives. A record that admits what it cannot see is more
    // of a testimony than one that pretends to have eyes.
    await openShield();
    expect(has('nicht')).toBe(true);
    expect(has('understood')).toBe(true);
    for (const phrase of ['verstanden', 'Verstaendnis', 'begriffen']) {
      expect(has(phrase)).toBe(false);
    }
  });

  it('an empty day is empty on BOTH halves, never one half only', async () => {
    // The failure this pins: a day with no refusals and no answers must not
    // render a half-empty mirror, and a day with answers must not render the
    // growth half as an error.
    await openShield(EMPTY);
    expect(has('Heute wurde nichts aufgehalten')).toBe(true);
    expect(has('Heute wurde nichts beantwortet')).toBe(true);
    expect(has('es fehlt')).toBe(false);
  });
});

describe('the gap rides the ONE verdict renderer, so every surface inherits it', () => {
  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
  });
  afterEach(() => {
    act(() => root.unmount());
    container.remove();
  });

  /** A real captured refusal's verdict, as the node sent it. */
  const heldVerdict = (): Verdict => {
    const r = SHIELD_LIVE.refusals[0];
    return {
      verdict: r.verdict,
      alignment: r.alignment,
      risk: r.risk,
      gold_values_loaded: true,
      gold_source: r.gold_source,
      gold_hits: r.gold_hits,
      risk_hits: r.risk_hits,
      missing: r.missing,
      oracle: r.eye,
    };
  };

  it('a refusal carries its gap wherever a verdict is rendered', async () => {
    await mount(<VerdictCard verdict={heldVerdict()} />, '/');
    expect(has('es fehlt')).toBe(true);
    expect(has('does not release')).toBe(true);
  });

  it('a verdict with nothing missing shows no gap line', async () => {
    const v = heldVerdict();
    await mount(<VerdictCard verdict={{ ...v, verdict: 'frei', missing: [] }} />, '/');
    expect(has('es fehlt')).toBe(false);
  });

  it('an older node that sends no `missing` at all still renders', async () => {
    // The field is optional on purpose — a Spore extends Verdict, and a reply
    // read does not carry it. Absent must read as absent, never as a crash.
    const { missing: _drop, ...withoutGap } = heldVerdict();
    await mount(<VerdictCard verdict={withoutGap as Verdict} />, '/');
    expect(has('es fehlt')).toBe(false);
    expect(hasBare('loesch')).toBe(true);
  });
});
