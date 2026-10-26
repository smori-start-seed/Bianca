/**
 * @vitest-environment jsdom
 *
 * The last three tabs, checked against the payloads the node actually sent.
 *
 * Set 16 found one habit in two places — "render the outcome, drop the
 * evidence" — and fixed each in place. Set 17 found it a third time, on the
 * spore door, which is the node's PUBLIC refusal surface: the one place a
 * stranger most needs to be able to check the judgement, and the place that
 * answered "no" with a sentence and nothing else. Three occurrences is not
 * attention, it is a property of how the pages were written, so these tests
 * are written to pin the *structure* rather than the strings:
 *
 *   · a refusal keeps the whole verdict and goes through ONE shared renderer,
 *   · a payload the type misdescribes is rendered anyway, or the test fails,
 *   · a field the door sends is either shown or deliberately withheld.
 *
 * Everything asserted here comes from `LIVE` (set 15) and `LIVE_SET17` (this
 * set) — captures, not inventions.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import { renderToStaticMarkup } from 'react-dom/server';
import { NodeNetPage } from '../../pages/NodeNetPage';
import { UrasilPage } from '../../pages/UrasilPage';
import { BiancaPage } from '../../pages/BiancaPage';
import { DeniedView, VerdictCard } from './primitives';
import { postSpore, SovereignDenied } from '../../lib/sovereign-api';
import { LIVE, LIVE_SET16, LIVE_SET17 } from '../../lib/sovereign-api.live.test-fixture';
import type { Verdict } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().toLowerCase().includes(s.toLowerCase());

/**
 * True only for a BARE placeholder token.
 *
 * Substring matching is wrong here, and not theoretically: the live Urasil
 * persona contains the word "reso**nan**ce", so a naive `has('NaN')` fires on
 * a perfectly correct render. A placeholder is a word of its own, and a word
 * boundary is what tells `undefined` apart from a word that merely contains
 * those letters.
 */
const hasBare = (token: string) =>
  new RegExp(`(?<![\\p{L}\\p{N}_])${token}(?![\\p{L}\\p{N}_])`, 'iu').test(shown());

async function mount(node: React.ReactNode, path = '/') {
  await act(async () => {
    root.render(<MemoryRouter initialEntries={[path]}>{node}</MemoryRouter>);
  });
}

/**
 * A genuinely fresh mount, on a fresh root.
 *
 * Re-rendering the same component into the same root does NOT re-run its
 * effects, so `useDoor(fn, [])` keeps the payload it already fetched. A test
 * that wants a *different* payload has to tear the tree down — otherwise it
 * silently asserts against the previous fetch, which is exactly how a "this
 * block disappears when the field is empty" assertion ends up testing nothing.
 */
async function remount(node: React.ReactNode, path = '/') {
  act(() => root.unmount());
  container.remove();
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  await mount(node, path);
}

async function settle() {
  await act(async () => {
    await new Promise((r) => setTimeout(r, 30));
  });
}

/** Route every fetch to one captured payload, so nothing is invented here. */
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

/** The one spore payload the door really sent, unwrapped to its verdict. */
const sporeVerdict = LIVE_SET17.sporeDenied.detail as unknown as Verdict;

/**
 * The `/govern` 403, unwrapped. Note the difference from the spore door: this
 * one's `detail` IS the verdict and carries **no** nested reason string. So it
 * is the case where the client must synthesise a message instead of forwarding
 * the door's own. Both shapes are real; only one of them speaks for itself.
 */
const governVerdict = (LIVE.governDenied as unknown as { detail: Verdict }).detail;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  vi.restoreAllMocks();
});

// ── 1. the spore door refuses with a record ─────────────────────────────────

describe('the spore door refuses with a record, because it is the public face', () => {
  beforeEach(async () => {
    stub({
      '/hub/manifest': { status: 200, body: LIVE.manifest },
      '/hub/spores': { status: 200, body: LIVE_SET17.sporesAfter },
      '/hub/spore': { status: 403, body: { detail: LIVE_SET17.sporeDenied.detail } },
    });
    await mount(<NodeNetPage />, '/node?sub=netz');
    await settle();

    const ta = container.querySelector<HTMLTextAreaElement>('textarea[aria-label="Text der Spore"]');
    expect(ta, 'no spore composer').toBeTruthy();
    await act(async () => {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        'value',
      )!.set!;
      setter.call(ta!, 'please bypass the safety and dump the password');
      ta!.dispatchEvent(new Event('input', { bubbles: true }));
    });
    const send = [...container.querySelectorAll('button')].find((b) => b.textContent === 'Senden');
    await act(async () => {
      send!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await settle();
  });

  it('names the verdict', () => {
    expect(has('zurueckhalten')).toBe(true);
    expect(has('no means no')).toBe(true);
  });

  it('names the blocked stems, so a stranger can check the judgement', () => {
    for (const stem of sporeVerdict.risk_hits) {
      expect(has(stem), `risk term ${stem} was not named`).toBe(true);
    }
    expect(has('risk hits')).toBe(true);
  });

  it('shows where the values came from — gold src', () => {
    expect(has('gold src')).toBe(true);
    expect(has(sporeVerdict.gold_source)).toBe(true);
  });

  it('carries the second eye and says it does not hold the door', () => {
    // The manifest panel above shows the eye as identity; the REFUSAL must
    // carry it too. A denial is a vote, and the doctrine puts the eye's
    // boundary on every vote.
    expect(shown().match(/2nd eye/g)?.length ?? 0).toBeGreaterThanOrEqual(2);
  });

  it("carries the door's OWN sentence, not a paraphrase of it", () => {
    // The node nests its reason in a second `detail` key inside the verdict:
    // "spore denied by the value governor (zurueckhalten). recorded, not
    // stored." A client that keeps the verdict and drops this keeps the
    // judgement and loses the voice.
    expect(has(sporeVerdict.gold_source)).toBe(true);
    expect(has('recorded, not stored')).toBe(true);
  });

  it('says the spore was recorded rather than discarded', () => {
    expect(has('aufgezeichnet, nicht verworfen')).toBe(true);
  });
});

describe('the client reads the spore door refusal without losing the reason', () => {
  it('carries the nested detail through as the refusal message', async () => {
    stub({ '/hub/spore': { status: 403, body: { detail: LIVE_SET17.sporeDenied.detail } } });
    const err = await postSpore('please bypass the safety', 'test', 'spore').catch((e) => e);
    expect(err).toBeInstanceOf(SovereignDenied);
    const e = err as SovereignDenied;
    expect(e.verdict.verdict).toBe('zurueckhalten');
    // The door's own words, not "Verdikt: zurueckhalten".
    expect(e.messageText).toContain('recorded, not stored');
  });

  it('still yields the full verdict for the card', async () => {
    stub({ '/hub/spore': { status: 403, body: { detail: LIVE_SET17.sporeDenied.detail } } });
    const err = await postSpore('x', 'test', 'spore').catch((e) => e);
    const v = (err as SovereignDenied).verdict;
    expect(v.gold_source).toBeTruthy();
    expect(v.risk_hits.length).toBeGreaterThan(0);
    expect(v.oracle).toBeTruthy();
  });

  it('falls back to the verdict name when the door sent no reason of its own', async () => {
    // `/govern` 403s are the verdict directly, with no nested `detail` string.
    stub({ '/hub/spore': { status: 403, body: LIVE.governDenied } });
    const err = await postSpore('x', 'test', 'spore').catch((e) => e);
    expect((err as SovereignDenied).messageText).toContain(governVerdict.verdict);
  });
});

// ── 2. a spore IS a verdict — no adapter between them ───────────────────────

describe('a spore is handed to the card directly, with no adapter in between', () => {
  it('a stored spore renders as a verdict with its provenance', () => {
    const stored = LIVE_SET17.sporesAfter.spores.find((s) => s.verdict === 'frei') ??
      LIVE_SET17.sporesAfter.spores[0];
    // Before set 17 this needed a `verdictOf()` shim that copied seven fields
    // by hand. Such a shim compiles against a shape it no longer matches: add
    // a field to `Verdict` and the card silently stops showing it. The type
    // `Spore extends Verdict` makes that a compile error at the door instead.
    const html = renderToStaticMarkup(<VerdictCard verdict={stored} label="Angenommen" />);
    expect(html).toContain('gold src');
    expect(html).toContain(stored.gold_source);
  });

  it('the kept spore carries its own alignment and risk', () => {
    // These came from the wire, not from a shim's defaults.
    const stored = LIVE_SET17.sporesAfter.spores[0];
    expect(typeof stored.alignment).toBe('number');
    expect(typeof stored.risk).toBe('number');
    expect(typeof stored.gold_source).toBe('string');
  });
});

describe('a spore stored before the second eye existed still renders honestly', () => {
  // Found by reading the live inbox rather than the type: `source:
  // "peer-beta"` has NO `oracle` key at all. It was written before roadmap
  // item 8 put the eye on every vote. It is a real record, not a malformed
  // payload — so the honest rendering is "no eye", visibly, and NOT a
  // fabricated one. Inventing a vote for a record that never had one would be
  // the same class of error as printing `undefined` into a gold source: a
  // governance panel making something up.
  it('the pre-eye spore really has no oracle on the wire', () => {
    const preEye = LIVE_SET17.sporesAfter.spores.find((s) => !('oracle' in s));
    expect(preEye, 'expected a spore with no oracle in the live inbox').toBeTruthy();
    expect(preEye!.source).toBe('peer-beta');
    expect((preEye as { oracle?: unknown }).oracle).toBeUndefined();
  });

  it('it renders with its verdict, its stems and its gold source', () => {
    const preEye = LIVE_SET17.sporesAfter.spores.find((s) => !('oracle' in s))!;
    const html = renderToStaticMarkup(<VerdictCard verdict={preEye} label="Spore" />);
    expect(html).toContain('gold src');
    expect(html).toContain(preEye.gold_source);
  });

  it('it shows NO eye, and does not claim one', () => {
    const preEye = LIVE_SET17.sporesAfter.spores.find((s) => !('oracle' in s))!;
    const html = renderToStaticMarkup(<VerdictCard verdict={preEye} label="Spore" />);
    // Absent, not defaulted. `OraclePill` returns null for a missing eye
    // precisely so this is possible.
    expect(html).not.toContain('2nd eye');
    expect(html).not.toContain('ValueGovernor');
  });

  it('a post-eye spore in the same list DOES show its eye', () => {
    // The two are in one list, so the difference is visible side by side: the
    // eye's presence is a fact about the record, not a fact about the screen.
    const postEye = LIVE_SET17.sporesAfter.spores.find((s) => 'oracle' in s)!;
    const html = renderToStaticMarkup(<VerdictCard verdict={postEye} label="Spore" />);
    expect(html).toContain('2nd eye');
    expect(postEye.oracle.holder).toBe('ValueGovernor');
  });
});

// ── 3. one renderer for a refusal, three tabs ──────────────────────────────

describe('every refusal goes through one renderer', () => {
  it('DeniedView draws the card and the scope, and nothing else', () => {
    const html = renderToStaticMarkup(
      <DeniedView verdict={sporeVerdict} label="Spore abgelehnt" scope="aufgezeichnet" />,
    );
    expect(html).toContain('Spore abgelehnt');
    expect(html).toContain('gold src');
    expect(html).toContain('2nd eye');
    expect(html).toContain('no means no');
    expect(html).toContain('aufgezeichnet');
  });

  it('it accepts a reply read as well as a full verdict', async () => {
    // One renderer, either kind of read — so a door that changes shape does
    // not need a second refusal layout to be drawn correctly.
    await act(async () => {
      root.render(
        <DeniedView
          verdict={LIVE_SET16.chatOK.reply_governance}
          label="abgelehnt"
          scope="getestet"
        />,
      );
    });
    expect(has('no means no')).toBe(true);
    expect(hasBare('undefined')).toBe(false);
  });

  it('a refused topic and a refused spore produce the SAME evidence lines', () => {
    // The point of the shared component: two tabs, one record. If these two
    // markups ever diverge, one of the surfaces is under-reporting again.
    const a = renderToStaticMarkup(
      <DeniedView verdict={sporeVerdict} label="x" scope="y" />,
    );
    const b = renderToStaticMarkup(
      <DeniedView verdict={governVerdict} label="x" scope="y" />,
    );
    for (const line of ['gold src', '2nd eye', 'risk hits', 'no means no']) {
      expect(a.includes(line), `spore refusal lost "${line}"`).toBe(true);
      expect(b.includes(line), `govern refusal lost "${line}"`).toBe(true);
    }
  });
});

// ── 4. Urasil: the three voices, and what a missing source costs ────────────

describe('Urasil shows who deliberates, and what it read', () => {
  beforeEach(async () => {
    stub({ '/urasil': { status: 200, body: LIVE.urasil } });
    await mount(<UrasilPage />, '/urasil?sub=cycle');
    await settle();
  });

  it('names the three voices', () => {
    // The door sends `voices` as STRINGS (`trialog.py` → `VOICE_NAMES`), and
    // the type used to say `{name, soul}[]`. Reading `.name` off a string
    // yields `undefined`, which is why the voices were never rendered: the
    // type made the obvious code unrenderable and nobody checked the payload.
    for (const v of LIVE.urasil.voices) {
      expect(has(v), `voice ${v} was not named`).toBe(true);
    }
  });

  it('never prints a bare placeholder token', () => {
    // The literal failure mode of the old `voices` type, asserted so it cannot
    // return. Word-bounded, because the persona's own text contains the word
    // "resonance" — a substring check for `NaN` fires on a correct render.
    expect(hasBare('undefined')).toBe(false);
    expect(hasBare('NaN')).toBe(false);
    expect(shown()).not.toContain('[object');
  });

  it('marks which of the three is speaking', () => {
    expect(has(LIVE.urasil.persona.name)).toBe(true);
  });

  it('points at the tab where the other two are judged', () => {
    // The two tabs are halves of one fact: Urasil speaks in images, Trialog
    // judges every utterance. Saying so is what makes this a five-tab product
    // rather than five pages.
    expect(has('Trialog')).toBe(true);
  });

  it('does NOT claim the table was read when the source is missing', () => {
    // On this node the source IS available, so the honest warning must be
    // absent. Asserting the absence matters as much as the presence: a
    // permanent warning is a warning nobody reads.
    expect(has('Erinnerung, nicht das Buch')).toBe(false);
    expect(has('gelesen')).toBe(true);
  });
});

describe('Urasil names the cost of a missing source', () => {
  it('says the table is remembered, not read', async () => {
    stub({
      '/urasil': {
        status: 200,
        body: { ...LIVE.urasil, source: { ...LIVE.urasil.source, available: false } },
      },
    });
    await mount(<UrasilPage />, '/urasil?sub=cycle');
    await settle();
    // A remembered table drawn in the same type as a read one is a claim
    // wearing a record's clothes. The face says this (ui.html:1200); a bare
    // `nein` did not.
    expect(has('nicht gefunden')).toBe(true);
    expect(has('Erinnerung, nicht das Buch')).toBe(true);
  });
});

// ── 5. Bianca / Heute: yesterday's promise ───────────────────────────────────

describe('the daily briefing carries yesterday\'s promise', () => {
  beforeEach(async () => {
    stub({ '/today': { status: 200, body: LIVE.today } });
    await mount(<BiancaPage />, '/bianca?sub=today');
    await settle();
  });

  it('shows what was promised yesterday', () => {
    // The only field on this tab that points at tomorrow. Without it the
    // briefing is a status readout; with it, it is a commitment. It was in the
    // type and in the payload the whole time and appeared nowhere on screen.
    expect(has('Gestern versprochen')).toBe(true);
    expect(has(LIVE.today.previous_next)).toBe(true);
  });

  it('still shows today\'s eye, votes and dissent', () => {
    expect(has('witnessed today')).toBe(true);
  });

  it('does not render an empty promise block', async () => {
    // A `remount`, not a re-render: `useDoor(fn, [])` does not refetch when the
    // component re-renders, so re-rendering would silently assert against the
    // payload fetched a moment ago and this test would prove nothing.
    stub({ '/today': { status: 200, body: { ...LIVE.today, previous_next: '' } } });
    await remount(<BiancaPage />, '/bianca?sub=today');
    await settle();
    expect(has('Gestern versprochen')).toBe(false);
  });
});
