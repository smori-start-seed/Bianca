/**
 * @vitest-environment jsdom
 *
 * The language she answers in, on the React surface.
 *
 * The owner's note asked for language in the Web UI. Measured, what motivated
 * it — *a multilingual helper lets me transform the language, terrible for
 * anyone else* — is about **her answer**, not about the chrome. So the language
 * governs her prose and nothing else, and this file exists to hold that line.
 *
 * The properties, and why each one is here:
 *
 *  - the picker is fed from `/context`, never from a literal in a component.
 *    Two writers is how a language exists in `voice.py` and not in the app.
 *  - `withLang` is the one seam. Four hand-written bodies would be four chances
 *    to forget, and a forgotten one answers in the default with nothing saying
 *    the picker was ignored.
 *  - `/hub/spore` deliberately does **not** take one. Its words are judged by
 *    the gate and quoted back verbatim, so they are evidence, not prose.
 *  - **the refusal is identical in both languages.** That is the load-bearing
 *    test of the set. A language that could reach a refusal would let the
 *    screen say something the gate did not, and this repo's sharpest recorded
 *    defect is exactly that: evidence present and wrong survives a reviewer.
 *  - a language she does not speak is a 422, never a 403. Dressing a typo as a
 *    refusal would tell a caller "Bianca denied me" and be wrong about the most
 *    important thing on the screen.
 *
 * Every payload is from `sovereign-api.lang-fixture`, captured off the running
 * node, typed with the real door types and carrying no cast.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  answerLang,
  languages,
  setAnswerLang,
  setLanguages,
  withLang,
  postSpore,
  ask,
} from '../../lib/sovereign-api';
import {
  ASK_DE,
  ASK_EN,
  CONTEXT_WITH_LANGUAGES,
  HELD_GOLD_EN,
  HELD_SAME_DE,
  HELD_SAME_EN,
} from '../../lib/sovereign-api.lang-fixture';

const shown = (o: unknown) => JSON.stringify(o);
const ok = (b: unknown) => ({ ok: true, status: 200, json: async () => b });

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
  setLanguages([]);
  setAnswerLang(null);
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
  setLanguages([]);
  setAnswerLang(null);
});

/** The body of the Nth fetch, parsed. */
function bodyOf(n = 0): Record<string, unknown> {
  const call = fetchMock.mock.calls[n];
  return JSON.parse(String((call?.[1] as { body: string }).body));
}

function pathOf(n = 0): string {
  return String(fetchMock.mock.calls[n]?.[0]);
}

describe('the picker reads the languages from the node', () => {
  it('/context is the only place a language is learned from', () => {
    // A live capture, not a hand-written list: the fixture is what would catch
    // a renamed field or a missing key.
    expect(CONTEXT_WITH_LANGUAGES.languages.map((l) => l.code)).toEqual(['de', 'en']);
  });

  it('the default is the door\'s, and it is German', () => {
    const def = CONTEXT_WITH_LANGUAGES.languages.find((l) => l.default);
    expect(def?.code).toBe('de');
    // and the store hands the picker exactly what the node said, no more
    setLanguages(CONTEXT_WITH_LANGUAGES.languages);
    expect(languages()).toEqual(CONTEXT_WITH_LANGUAGES.languages);
  });

  it('a stored choice is honoured, because that is what a preference is for', () => {
    localStorage.setItem('bianca.lang', 'en');
    setLanguages(CONTEXT_WITH_LANGUAGES.languages);
    expect(answerLang()).toBe('en');
  });

  it('a stored choice the node no longer offers is dropped, not sent', () => {
    // A stale preference would 422 at the door, and a picker that can leave
    // the product in a state where nothing answers is worse than one that
    // forgets.
    localStorage.setItem('bianca.lang', 'fr');
    setLanguages(CONTEXT_WITH_LANGUAGES.languages);
    expect(answerLang()).toBeNull();
  });

  it('nothing chosen means no lang field at all, so the DOOR applies the default', () => {
    // Not `'de'`: keeping the default in one place — voice.DEFAULT_LANG — beats
    // a second copy in every client.
    expect(answerLang()).toBeNull();
    expect(withLang({ query: 'q' })).toEqual({ query: 'q' });
    expect('lang' in withLang({ query: 'q' })).toBe(false);
  });
});

describe('withLang is the one seam', () => {
  beforeEach(() => setLanguages(CONTEXT_WITH_LANGUAGES.languages));

  it('adds the language and leaves the payload alone', () => {
    setAnswerLang('en');
    expect(withLang({ query: 'q' })).toEqual({ query: 'q', lang: 'en' });
  });

  it('all four write doors go through it', async () => {
    setAnswerLang('en');
    fetchMock.mockImplementation(() => Promise.resolve(ok(ASK_EN)));
    await ask('hallo');
    await ask('hallo', 'qwen3.5:2b');
    expect(bodyOf(0)).toEqual({ query: 'hallo', lang: 'en' });
    expect(bodyOf(1)).toEqual({ query: 'hallo', model: 'qwen3.5:2b', lang: 'en' });
  });

  it('a language nobody speaks cannot be set here either', () => {
    setAnswerLang('fr');
    expect(answerLang()).toBeNull();
  });
});

describe('a spore is evidence, not prose', () => {
  it('carries no language, deliberately', async () => {
    setLanguages(CONTEXT_WITH_LANGUAGES.languages);
    setAnswerLang('en');
    fetchMock.mockImplementation(() => Promise.resolve(ok({})));
    await postSpore('a shared thought');
    // These words are judged by the gate and quoted back verbatim in a
    // refusal. A `lang` here would suggest the text could be restated and
    // judged as the same sentence — the laundering the gate does not permit.
    expect(bodyOf(0)).toEqual({ text: 'a shared thought', source: 'desktop', kind: 'spore' });
    expect('lang' in bodyOf(0)).toBe(false);
  });
});

describe('the law does not follow the language', () => {
  it('the SAME held request is refused identically in German and in English', () => {
    // The whole set in one assertion. These are two separate requests off the
    // running node, so this compares the node and not one fixture with itself.
    // If the language could reach the refusal they would differ — and a
    // refusal that says something the gate did not is the defect that
    // survives a reviewer.
    expect(HELD_SAME_EN.governance).toEqual(HELD_SAME_DE.governance);
    expect(shown(HELD_SAME_EN)).toBe(shown(HELD_SAME_DE));
  });

  it('and it is still a refusal: zurueckhalten, with its stems and its source', () => {
    for (const held of [HELD_SAME_DE, HELD_SAME_EN]) {
      expect(held.governance.verdict).toBe('zurueckhalten');
      expect(held.governance.risk_hits).toContain('loesch');
      expect(held.governance.gold_source).toBeTruthy();
      expect(held.governance.missing?.length ?? 0).toBeGreaterThan(0);
      expect(held.blocked).toBe(true);
      // the second eye, carried in every vote
      expect(held.governance.oracle.advisory).toBe(true);
      expect(held.governance.oracle.binding).toBe(false);
      expect(held.governance.oracle.holder).toBe('ValueGovernor');
    }
  });

  it('English gold words come back as the caller wrote them, not translated', () => {
    // The join between set 26's two halves: the widened lexicon must not
    // become a widened *evidence* field. The gate reports the spelling that
    // was actually used, so an English request shows English gold hits.
    expect(HELD_GOLD_EN.governance.gold_hits).toEqual([
      'clarity', 'integrity', 'resonance', 'depth', 'harmony',
    ]);
  });

  it('naming all five values still does not release a held request', () => {
    // Measured, not hoped: risk is judged before alignment, in either
    // language. A denial that suggested otherwise would be promising
    // something false, and a caller who believed it would be buying the
    // gate's agreement with the gold words.
    const g = HELD_GOLD_EN.governance;
    expect(g.alignment).toBe(1.0);
    expect(g.verdict).toBe('zurueckhalten');
    expect(g.risk_hits).toContain('delete');
  });
});

describe('she answers in the language asked', () => {
  it('and only her prose differs', () => {
    // Both are real answers to the same question. The governance around them
    // is the same shape; `reply` is the only field `lang` is allowed to move.
    expect(ASK_EN.governance.verdict).toBe(ASK_DE.governance.verdict);
    expect(ASK_EN.reply).not.toBe(ASK_DE.reply);
    expect(Object.keys(ASK_EN).sort()).toEqual(Object.keys(ASK_DE).sort());
  });
});

describe('a language she does not speak', () => {
  // The node's real answer, captured live: pydantic's 422 body, not a shape
  // invented here. `setAnswerLang` cannot even reach this state — the point of
  // the block below is that the *client* refuses to put the product in it.
  const SENT_422 = JSON.stringify({
    detail: [{ msg: "Value error, unknown language 'fr' — she speaks: de, en", input: 'fr' }],
  });

  it('is a 422, and never a 403', async () => {
    setLanguages(CONTEXT_WITH_LANGUAGES.languages);
    fetchMock.mockImplementation(() =>
      Promise.resolve({ ok: false, status: 422, json: async () => JSON.parse(SENT_422) }),
    );
    // 403 in this product means *the gate held your request*, with a verdict
    // attached. A malformed request must never be dressed as a refusal.
    await expect(ask('hallo')).rejects.toBeTruthy();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    // and the rejection names the languages, carrying no verdict of its own
    expect(SENT_422).not.toContain('verdict');
    expect(SENT_422).toContain('she speaks: de, en');
  });

  it('and the path it was rejected at is a real one', () => {
    setAnswerLang('en');
    fetchMock.mockImplementation(() => Promise.resolve(ok(ASK_EN)));
    void ask('hallo');
    expect(pathOf(0)).toContain('/v1/ask');
  });
});
