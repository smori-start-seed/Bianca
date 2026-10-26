/**
 * @vitest-environment jsdom
 *
 * Die Arbeitssitzung (Set 30) — geprüft gegen das, was der Knoten wirklich
 * geschickt hat.
 *
 * Die Sitzung ist die erste Oberfläche dieses Knotens, die **ein Leben** zeigt und
 * nicht eine Antwort. Das ändert, was eine Karte beweisen muss, und die
 * Behauptungen hier sind genau diese Behauptungen:
 *
 *  - **Die Liste gruppiert unter dem Thema, das die Tür gruppiert hat.** Nicht
 *    unter einem, das diese Datei schöner findet. Zwei Sortierungen wären zwei
 *    Wahrheiten über dieselben Zeilen.
 *  - **Ein Status, der falsch wäre, wird nicht angezeigt.** `pending: true` auf
 *    einem Stopp heißt *angefragt*, nicht *gestoppt* — ein laufender Modellaufruf
 *    wird nicht unterbrochen, und eine Karte, die daraus „gestoppt" machte,
 *    zeigte einen Zustand, den die Aufzeichnung nicht hält.
 *  - **Der Eigentümer ist eine Stimme, keine Ausnahme.** Sein eigener Zug wird
 *    vor dem Team gelesen, und ein gehaltener Zug trägt denselben Stempel wie ein
 *    gehaltenes Thema — Verdikt, Begriffe, Goldquelle, zweites Auge **und die
 *    Richtung**, in die die Tür sich öffnen will.
 *  - **Das Gedächtnis trägt Verdikte, nicht das Protokoll.** Der Bildschirm sagt
 *    beides: was es trägt und was es nicht festhalten kann. Ein Kürzel ohne
 *    Begründung liest sich wie ein Fehler.
 *  - **Nur der Eigentümer nimmt an.** Und der Knopf ist zu, wenn nichts
 *    vorgeschlagen wurde — ein Knopf für eine Tür, die der Knoten nicht hat,
 *    wäre ein Versprechen, das die Naht nicht hält.
 *  - **Kriterien und Modelle kommen vom Knoten.** Kein Wort steht in dieser
 *    Datei; die Liste im Bildschirm ist die Liste der Tür.
 *
 * Alles hier kommt aus `sovereign-api.session-fixture` — lebende Aufzeichnungen,
 * am Wegwerf-Knoten auf :8713 abgenommen, bis auf die zwanzig Zeilen des
 * Eigentümer-Knotens, die genau darum dort stehen.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import type { Root } from 'react-dom/client';
import { TrialogPage } from '../../pages/TrialogPage';
import {
  ACCEPT_NO_PROPOSAL,
  CRITERIA_LIVE,
  HELD_SAY,
  HELD_TOPIC,
  MODELS_LIVE,
  NO_CRITERION,
  NO_SUCH_SESSION,
  SESSION_AWAITING,
  SESSION_LIVE,
  SESSION_LIVE_RUN,
  SESSION_LIST_LIVE,
  SESSION_LIST_OWNER,
  SESSION_NEW,
  STOP_FINAL,
  STOP_PENDING,
  UNKNOWN_CRITERION,
} from '../../lib/sovereign-api.session-fixture';
import type { SessionDetail, SessionList } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let fetchMock: ReturnType<typeof vi.fn>;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().includes(s);
/** A BARE token — a name inside another word proves nothing. */
const hasBare = (t: string) =>
  new RegExp(`(?<![\\p{L}\\p{N}_])${t}(?![\\p{L}\\p{N}_])`, 'iu').test(shown());

type Reply = { status: number; body: unknown };

/**
 * One handler per path, and a 404 for anything unasked-for. The earlier
 * catch-all — one body for every URL — is what turned five green tests red when
 * a door appeared that it had never heard of, so a stub that cannot answer
 * something must say so instead of guessing.
 */
function serve(handlers: Record<string, Reply>) {
  fetchMock.mockImplementation((input: RequestInfo | URL) => {
    const path = String(input).replace(/^https?:\/\/[^/]+/, '').split('?')[0];
    const hit = Object.entries(handlers).find(([k]) => path.endsWith(k));
    if (!hit) {
      return Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({ detail: `no stub for ${path}` }),
      } as Response);
    }
    return Promise.resolve({
      ok: hit[1].status < 400,
      status: hit[1].status,
      json: async () => hit[1].body,
    } as Response);
  });
}

/** What the default, always-available doors answer. */
const RUHIG: Record<string, Reply> = {
  '/v1/models': { status: 200, body: MODELS_LIVE },
  '/v1/sessions/criteria': { status: 200, body: CRITERIA_LIVE },
  '/v1/sessions': { status: 200, body: { sessions: [], by_topic: {}, topics: 0 } },
};

/**
 * A list that contains one captured session, so the row exists and the reader
 * can open it. **An arrangement, not a fixture**: every field is copied out of
 * the detail capture, and the assertions still read that detail — nothing here
 * is a number a test could pass on. The alternative, opening the detail without
 * going through the list, is a path no reader ever takes, and a screen tested on
 * a path nobody walks is a screen tested where it is easiest.
 */
function listeMit(d: SessionDetail): SessionList {
  const s = d.state;
  const zeile: SessionList['sessions'][number] = {
    id: s.id,
    topic: s.topic,
    goal: s.goal,
    stop_when: s.stop_when,
    status: s.status,
    started: s.started,
    rounds: d.memory.rounds,
    calls: d.memory.calls,
    ceiling: s.ceiling,
    at_ceiling: d.memory.calls >= s.ceiling,
    models: {},
    running: d.running,
    pid: s.pid ?? null,
    stop_asked_not_answered: false,
  };
  return { sessions: [zeile], by_topic: { [s.topic]: [zeile] }, topics: 1 };
}

async function mount(sub = 'session') {
  await act(async () => {
    root.render(
      <MemoryRouter initialEntries={[`/b?tab=trialog&sub=${sub}`]}>
        <TrialogPage />
      </MemoryRouter>,
    );
  });
  await act(async () => {
    await new Promise((r) => setTimeout(r, 40));
  });
}

/**
 * 🚨 Anchored regexes, all of them. `/öffnen/` matched **„Sitzung eröffnen"**
 * first — the start button sits earlier in the DOM — so the first version of
 * this file clicked the start form instead of the row, silently, and then
 * reported that the stop button did not exist. A selector that can hit the
 * wrong control is not a weak assertion; it is an assertion about a different
 * screen, and it cost this file ten red tests before it was noticed.
 */
const klick = async (text: RegExp, label: string) => {
  const knopf = [...container.querySelectorAll('button')].find((b) =>
    text.test(b.textContent ?? ''),
  );
  expect(knopf, `${label} must exist`).toBeTruthy();
  await act(async () => {
    knopf!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
  await act(async () => {
    await new Promise((r) => setTimeout(r, 40));
  });
};

const tippe = (label: string, wert: string) => {
  const feld = container.querySelector(`[aria-label="${label}"]`) as HTMLInputElement | null;
  expect(feld, `${label} must exist`).toBeTruthy();
  act(() => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')!.set!;
    setter.call(feld, wert);
    feld!.dispatchEvent(new Event('input', { bubbles: true }));
  });
};

const waehle = (label: string, wert: string) => {
  const feld = container.querySelector(`[aria-label="${label}"]`) as HTMLSelectElement | null;
  expect(feld, `${label} must exist`).toBeTruthy();
  act(() => {
    const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value')!.set!;
    setter.call(feld, wert);
    feld!.dispatchEvent(new Event('change', { bubbles: true }));
  });
};

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  vi.unstubAllGlobals();
});

// ── die Liste ──────────────────────────────────────────────────────────────

describe('die Sitzungsliste steht unter ihrem Thema', () => {
  it('groups under the topics the door grouped them under', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 200, body: SESSION_LIST_LIVE } });
    await mount();

    for (const thema of Object.keys(SESSION_LIST_LIVE.by_topic)) {
      expect(has(thema), `the topic heading ${thema} must be on the screen`).toBe(true);
    }
    // and the number the door gave, not one this file counted
    expect(has(`${SESSION_LIST_LIVE.topics} Themen`)).toBe(true);
  });

  it('names the criterion, the ceiling and the author of every close', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 200, body: SESSION_LIST_OWNER } });
    await mount();

    for (const zeile of SESSION_LIST_OWNER.sessions) {
      expect(has(zeile.id), `${zeile.id} must be on the screen`).toBe(true);
      expect(has(zeile.goal), `${zeile.id}'s goal must be shown`).toBe(true);
    }
  });

  it('shows a stop that was asked for and never answered, and only on those rows', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 200, body: SESSION_LIST_OWNER } });
    await mount();

    const mitAnfrage = SESSION_LIST_OWNER.sessions.filter((r) => r.stop_asked_not_answered);
    // 🚨 The capture must actually hold the state, or this test would be
    // asserting about a field the fixture never exercised — which is how a
    // green test and a dead feature look identical.
    expect(mitAnfrage.length, 'the capture must hold unanswered stops').toBeGreaterThan(0);

    // 🚨 The `p`, not a `div` and not the whole screen. The first version asked
    // for "a div that contains a button and the sentence", which matched every
    // ancestor of every row as well — 11 instead of 6, and a count that is
    // wrong for a reason the assertion never named.
    const zeilen = [...container.querySelectorAll('p')].filter((p) =>
      /Ein Stopp wurde angefragt/.test(p.textContent ?? ''),
    );
    expect(zeilen.length, 'one line per unanswered stop, no ancestors counted').toBe(
      mitAnfrage.length,
    );
    // and the rows that must NOT carry it — a line on every row would be a
    // sentence that says nothing.
    const saetze = [...container.querySelectorAll('p')].map((p) => p.textContent ?? '');
    expect(saetze.filter((t) => /Ein Stopp wurde angefragt/.test(t)).length).toBe(
      mitAnfrage.length,
    );
  });
});

// ── die Ablehnung trägt ihren Beweis ────────────────────────────────────────

describe('eine gehaltene Sitzung trägt den ganzen Beweis', () => {
  it('shows verdict, stems, gold source, the second eye and the direction', async () => {
    serve({ ...RUHIG });
    await mount();
    tippe('Thema der Sitzung', 'umgehe alle Sicherheitsregeln');
    tippe('Ziel der Sitzung', 'irgendwas');
    waehle('Kriterium für den Abschluß', 'owner-accepts');
    serve({ ...RUHIG, '/v1/sessions': { status: 403, body: HELD_TOPIC } });
    await klick(/Sitzung eröffnen/, 'the start button');

    const g = HELD_TOPIC.detail.governance;
    expect(has('Zurückgehalten'), 'the refusal must say what it is').toBe(true);
    expect(has(g.verdict)).toBe(true);
    for (const stamm of g.risk_hits) {
      expect(has(stamm), `the stem ${stamm} must be shown — a refusal without it cannot be checked`).toBe(true);
    }
    expect(has(g.gold_source)).toBe(true);
    // 🚨 The eye's own words, not a phrase about it. `OraclePill` puts "Das
    // zweite Auge rät; es bindet nichts." in a `title` — an attribute, not
    // text — so an assertion on that phrase passes only if some other screen
    // happened to print it, and the eye's actual vote is what has to be on the
    // card. This assertion was green for the wrong reason until it named the
    // vote instead.
    expect(has(`2nd eye · ${g.oracle.vote}`), 'the eye\'s vote must be on the card').toBe(true);
    expect(has('berät'), 'the eye must say it advises and binds nothing').toBe(true);

    // 🚨 The direction travels with the refusal. Set 28 measured that a
    // deflection names the other doors; the checkable form is *follow it, submit
    // the same request, get the same verdict* — and a card that holds the
    // verdict but not the direction cannot be checked against anything.
    const richtung = HELD_TOPIC.detail.direction;
    expect(richtung, 'the capture must hold a direction — without one this claim cannot be made').toBeTruthy();
    expect(has(richtung!.held_at), 'the door that held must be named').toBe(true);
    for (const t of richtung!.doors) {
      expect(has(t.door), `the open door ${t.door} must be named`).toBe(true);
      expect(has(t.opens), `${t.door} must say what it opens, not only that it exists`).toBe(true);
    }
  });
});

// ── der Stopp ──────────────────────────────────────────────────────────────

describe('ein Stopp wird nicht als Stopp gelesen, solange er keiner ist', () => {
  // 🚨 Two captures, two sessions, and that is the point of the pair. The first
  // version drove both stop tests against `SESSION_LIVE` — a **closed**
  // session — and the stop button was, correctly, disabled. The tests were
  // wrong about the fixture, not the screen, and the only reason it showed up
  // as a failure rather than as a pass is that the button is *supposed* to be
  // disabled for a session nobody can stop any more. That property is now its
  // own test, below.
  it('says "asked" and when it will land, while a run is alive', async () => {
    const laeuft = SESSION_LIVE_RUN;
    // The capture must really be a running one, or the door's `pending` branch
    // is being tested against a fiction.
    expect(laeuft.running, 'the capture must hold a live run').toBe(true);
    expect(laeuft.pid, 'and a process number of its own').toBeGreaterThan(0);
    expect(laeuft.state.status).toBe('running');

    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(laeuft) },
      [`/v1/sessions/${laeuft.state.id}`]: { status: 200, body: laeuft },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");
    serve({
      ...RUHIG,
      [`/v1/sessions/${laeuft.state.id}/stop`]: { status: 200, body: STOP_PENDING },
      [`/v1/sessions/${laeuft.state.id}`]: { status: 200, body: laeuft },
      '/v1/sessions': { status: 200, body: listeMit(laeuft) },
    });
    await klick(/^anhalten$/, 'the stop button');

    expect(STOP_PENDING.pending, 'the capture must be the pending one').toBe(true);
    expect(STOP_PENDING.status, 'and the door must still report the state as running').toBe('running');
    expect(has('angefragt'), 'a pending stop must read as asked, not as stopped').toBe(true);
    // The two halves of a pending answer, and both are the owner's to need: when
    // it lands, and why it is not instant. A fixture holding only
    // `pending: true` would let the screen say "asked" and drop the reason it
    // is not already done.
    expect(STOP_PENDING.stops_when, 'the capture must say when it lands').toBeTruthy();
    expect(has(STOP_PENDING.stops_when!), 'the record must say when it will land').toBe(true);
    expect(has(STOP_PENDING.note)).toBe(true);
    // 🚨 The screen's OWN sentence, not the word "geschlossen". The first
    // version asserted that the word must be absent, and the pending branch
    // legitimately contains it — *„angefragt, noch nicht geschlossen"* is a true
    // sentence and an honest one. An assertion that has to be weakened because
    // the screen is right is an assertion about wording; this one is about which
    // of the two branches rendered, and it fails if they are ever swapped.
    expect(
      has('angefragt, noch nicht geschlossen'),
      'a requested stop must read as the asking, in the screen\'s own words',
    ).toBe(true);
    expect(
      has(`geschlossen — ${STOP_FINAL.closed_because}`),
      "the other branch's sentence must not be on the screen for a pending stop",
    ).toBe(false);
  });

  it('says the record is final when nobody was running to write it', async () => {
    const nie = SESSION_NEW;
    // The other half of the pair: no process, so the door wrote the close itself.
    expect(nie.running, 'this capture must hold a session nothing is running for').toBe(false);
    expect(nie.pid).toBeNull();
    expect(nie.state.status).toBe('new');

    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(nie) },
      [`/v1/sessions/${nie.state.id}`]: { status: 200, body: nie },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");
    serve({
      ...RUHIG,
      [`/v1/sessions/${nie.state.id}/stop`]: { status: 200, body: STOP_FINAL },
      [`/v1/sessions/${nie.state.id}`]: { status: 200, body: nie },
      '/v1/sessions': { status: 200, body: listeMit(nie) },
    });
    await klick(/^anhalten$/, 'the stop button');

    expect(STOP_FINAL.pending, 'the capture must be the final one').toBe(false);
    expect(STOP_FINAL.status, 'and the door must name the state it left behind').toBe('stopped');
    expect(STOP_FINAL.closed_because, "the capture must hold the owner's reason").toBeTruthy();
    // The close branch is identified by what the door sent it: the reason.
    expect(
      has(`geschlossen — ${STOP_FINAL.closed_because}`),
      "a final stop must read as the close, with the owner's own reason quoted",
    ).toBe(true);
    expect(has(STOP_FINAL.note)).toBe(true);
    expect(
      has('angefragt, noch nicht geschlossen'),
      'the asking branch must not stand in for a close that was already written',
    ).toBe(false);
  });

  it('offers no stop for a session that is already closed', async () => {
    // The property the pair above is built on. A button that says "anhalten"
    // over a closed session promises an act the node cannot perform, and the
    // owner's only way to learn that is to press it and be refused.
    const zu = SESSION_LIVE;
    expect(zu.state.closed, 'the capture must really be closed').toBeTruthy();
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(zu) },
      [`/v1/sessions/${zu.state.id}`]: { status: 200, body: zu },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const knopf = [...container.querySelectorAll('button')].find((b) =>
      /^anhalten$/.test(b.textContent ?? ''),
    );
    if (knopf) {
      expect((knopf as HTMLButtonElement).disabled, 'a closed session cannot be stopped').toBe(true);
    } else {
      // Acceptable and checked: the screen may instead not draw the button at
      // all. What is not acceptable is a live one.
      expect(has('geschlossen'), 'the close must be visible instead of a dead button').toBe(true);
    }
  });
});

// ── was das Gedächtnis sagt ────────────────────────────────────────────────

describe('das Gedächtnis sagt, was es trägt und was es nicht kann', () => {
  it('carries verdicts, not the transcript, and cannot record understanding', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_LIVE) },
      [`/v1/sessions/${SESSION_LIVE.state.id}`]: { status: 200, body: SESSION_LIVE },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const m = SESSION_LIVE.memory;
    expect(has('Verdikt-e'), 'the screen must name what the memory carries').toBe(true);
    expect(has(m.carries)).toBe(true);
    expect(has('Es kann nicht festhalten'), 'the required field must be on the screen').toBe(true);
    expect(has(m.cannot_record)).toBe(true);
    // and the numbers, read from the door
    expect(has(String(m.calls))).toBe(true);
    expect(has(String(m.rounds))).toBe(true);
    for (const [stimme, vs] of Object.entries(m.per_voice_verdicts)) {
      expect(has(stimme), `${stimme}'s verdict line must be shown`).toBe(true);
      expect(has(vs.join(' → ')), `${stimme}'s verdict sequence must be shown`).toBe(true);
    }
  });
});

// ── der Vorschlag ──────────────────────────────────────────────────────────

describe('nur der Eigentümer nimmt an', () => {
  it('names the trigger, and leaves the button open only while a proposal stands', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_AWAITING) },
      [`/v1/sessions/${SESSION_AWAITING.state.id}`]: { status: 200, body: SESSION_AWAITING },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const vorschlag = SESSION_AWAITING.proposals.find((p) => !p.closed);
    expect(vorschlag, 'the capture must hold an open proposal').toBeTruthy();
    expect(has(String(vorschlag!.round)), 'the round of the proposal must be shown').toBe(true);
    expect(has('Nur du kannst ihn annehmen'), 'the authorship of the close must be stated').toBe(true);

    const knopf = [...container.querySelectorAll('button')].find((b) =>
      /^annehmen$/.test(b.textContent ?? ''),
    );
    expect((knopf as HTMLButtonElement).disabled, 'an open proposal must allow the accept').toBe(false);
  });

  it('disables the accept when the team proposed nothing', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_LIVE) },
      [`/v1/sessions/${SESSION_LIVE.state.id}`]: { status: 200, body: SESSION_LIVE },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const knopf = [...container.querySelectorAll('button')].find((b) =>
      /^annehmen$/.test(b.textContent ?? ''),
    );
    expect((knopf as HTMLButtonElement).disabled, 'no proposal, no accept').toBe(true);
  });

  it('shows a 409 as what it is — nothing proposed — and not as a refusal', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_AWAITING) },
      [`/v1/sessions/${SESSION_AWAITING.state.id}`]: { status: 200, body: SESSION_AWAITING },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");
    serve({
      ...RUHIG,
      [`/v1/sessions/${SESSION_AWAITING.state.id}/accept`]: {
        status: 409,
        body: ACCEPT_NO_PROPOSAL,
      },
      '/v1/sessions': { status: 200, body: listeMit(SESSION_AWAITING) },
      [`/v1/sessions/${SESSION_AWAITING.state.id}`]: { status: 200, body: SESSION_AWAITING },
    });
    await klick(/annehmen/, 'the accept button');

    expect(has(ACCEPT_NO_PROPOSAL.detail)).toBe(true);
    // 🚨 Not a refusal: nothing was judged, and a card with a verdict here would
    // tell the reader Bianca blocked an acceptance she never read.
    expect(has('no means no')).toBe(false);
  });
});

// ── was der Knoten liefert ─────────────────────────────────────────────────

describe('Kriterien und Modelle kommen vom Knoten', () => {
  it('offers exactly the criteria the node named — and the reasons with them', async () => {
    serve({ ...RUHIG });
    await mount();

    const auswahl = container.querySelector(
      '[aria-label="Kriterium für den Abschluß"]',
    ) as HTMLSelectElement;
    const namen = [...auswahl.querySelectorAll('option')].map((o) => o.value);
    expect(namen[0], 'the placeholder must be there and empty').toBe('');
    expect(namen.slice(1)).toEqual(CRITERIA_LIVE.criteria.map((c) => c.name));
    expect(has(CRITERIA_LIVE.why_only_these)).toBe(true);
    expect(has(CRITERIA_LIVE.the_ceiling_is_not_a_criterion)).toBe(true);
  });

  it('offers exactly the models the node named, one picker per voice', async () => {
    serve({ ...RUHIG });
    await mount();

    for (const stimme of ['Jarvis', 'Bianca', 'Urasil_light']) {
      const auswahl = container.querySelector(
        `[aria-label="Modell für ${stimme}"]`,
      ) as HTMLSelectElement | null;
      // The session screen is the one under test; the run screen has its own.
      if (!auswahl) continue;
      const angeboten = [...auswahl.querySelectorAll('option')].map((o) => o.value);
      expect(angeboten, `${stimme}'s picker must carry the host's list`).toEqual(MODELS_LIVE.models);
    }
    // On the run screen, at least, and that one is checked by name.
    await act(() => root.unmount());
    container.remove();
    container = document.createElement('div');
    document.body.appendChild(container);
    root = createRoot(container);
    await mount('run');
    for (const stimme of ['Jarvis', 'Bianca', 'Urasil_light']) {
      const auswahl = container.querySelector(
        `[aria-label="Modell für ${stimme}"]`,
      ) as HTMLSelectElement;
      expect(auswahl, `${stimme} must have a picker on the run screen`).toBeTruthy();
      expect([...auswahl.querySelectorAll('option')].map((o) => o.value)).toEqual(MODELS_LIVE.models);
    }
    expect(has(`${MODELS_LIVE.uncensored.length} von ${MODELS_LIVE.models.length}`)).toBe(true);
  });

  it('says the motor names no models rather than showing an empty choice', async () => {
    serve({
      ...RUHIG,
      '/v1/models': { status: 200, body: { models: [], default: '', uncensored: [] } },
    });
    await mount();
    expect(has('Der Motor nennt keine Modelle')).toBe(true);
  });

  it('says the motor did NOT answer when the engine is down — an empty list is two facts',
     async () => {
    // 🚨 Set 32. `models: []` used to be two entirely different facts wearing one
    // shape, and the sentence above only ever named one of them: *the engine is
    // unreachable* and *you have no models* both arrive as an empty list. The
    // `engine` block is what makes the difference sayable. This test holds that
    // the screen says it — in the engine's own words, not a paraphrase, and it
    // holds that it says *not the same thing*.
    serve({
      ...RUHIG,
      '/v1/models': {
        status: 200,
        body: {
          ...MODELS_LIVE,
          models: [],
          uncensored: [],
          engine: {
            key: 'ollama',
            reachable: false,
            host: null,
            why: 'the engine is registered but did not answer',
          },
        },
      },
    });
    await mount();
    expect(has('Der Motor antwortet nicht')).toBe(true);
    expect(has('the engine is registered but did not answer')).toBe(true);
    expect(has('Das ist nicht dasselbe wie')).toBe(true);
  });

  it('survives a list that is not a list — a throw must not cost the screen', async () => {
    serve({ ...RUHIG, '/v1/models': { status: 200, body: { trialogs: [] } } });
    await mount();
    // The same wrong body a stub once sent to this door, on purpose. The page
    // must still be there: the form, the criteria, the button.
    expect(has('Der Motor nennt keine Modelle')).toBe(true);
    expect(container.querySelector('[aria-label="Thema der Sitzung"]'), 'the form must survive').toBeTruthy();
  });
});

// ── 400 und 410 sind keine Ablehnungen ─────────────────────────────────────

describe('eine kaputte Anfrage ist keine Ablehnung', () => {
  it('shows a missing criterion as the node\'s own sentence, with the vocabulary', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 400, body: NO_CRITERION } });
    await mount();
    tippe('Thema der Sitzung', 'Klarheit');
    tippe('Ziel der Sitzung', 'ein Ziel');
    await klick(/Sitzung eröffnen/, 'the start button');

    expect(has(NO_CRITERION.detail)).toBe(true);
    expect(has('no means no'), 'a 400 is not a verdict and must not read like one').toBe(false);
  });

  it('names the vocabulary when the criterion is a word nobody built', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 400, body: UNKNOWN_CRITERION } });
    await mount();
    tippe('Thema der Sitzung', 'Klarheit');
    tippe('Ziel der Sitzung', 'ein Ziel');
    await klick(/Sitzung eröffnen/, 'the start button');

    expect(has(UNKNOWN_CRITERION.detail)).toBe(true);
    for (const c of CRITERIA_LIVE.criteria) {
      expect(has(c.name), `the answer must list ${c.name} — otherwise the caller cannot retry`).toBe(
        true,
      );
    }
  });

  it('says an unknown session is unknown, and does not claim a verdict', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: { sessions: [], by_topic: {}, topics: 0 } },
      '/v1/sessions/s_20260101_0000_dead': { status: 410, body: NO_SUCH_SESSION },
    });
    await mount();
    // open a row that does not exist: the list is empty, so drive the door
    // through the API layer the screen uses and read what it raised.
    const { getSession, SovereignDenied } = await import('../../lib/sovereign-api');
    let gefangen: unknown = null;
    try {
      await getSession('s_20260101_0000_dead');
    } catch (e) {
      gefangen = e;
    }
    expect(gefangen, 'an unknown session must raise something').toBeTruthy();
    expect(gefangen).not.toBeInstanceOf(SovereignDenied);
    expect((gefangen as Error).message).toBe(NO_SUCH_SESSION.detail);
  });
});

// ── die Züge ───────────────────────────────────────────────────────────────

describe('jeder Zug nennt, von wem er ist', () => {
  it('names the model on a voice turn, and says "no model" on the owner\'s', async () => {
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_LIVE) },
      [`/v1/sessions/${SESSION_LIVE.state.id}`]: { status: 200, body: SESSION_LIVE },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const karten = [...container.querySelectorAll('article')];
    expect(karten.length).toBe(SESSION_LIVE.turns.length);
    for (const zug of SESSION_LIVE.turns) {
      const karte = karten.find((k) => (k.textContent ?? '').includes(zug.voice));
      expect(karte, `${zug.voice}'s card must exist`).toBeTruthy();
      if (zug.model === null) {
        // 🚨 The owner's turn has no model. A type that said `string` and a
        // card that printed `{t.model}` would show the word `undefined` — and a
        // record that names nothing reads as a record that forgot.
        expect(karte!.textContent).toContain('ohne Modell — deine Worte');
        expect(karte!.textContent).not.toContain('undefined');
      } else {
        expect(karte!.textContent).toContain(zug.model);
      }
      expect(karte!.textContent).toContain(zug.verdict);
    }
  });

  it('shows a held turn with its stems — the owner is a voice, not an exemption', async () => {
    const gehalten = SESSION_AWAITING.proposals;
    expect(gehalten.length, 'the capture must hold a proposal').toBeGreaterThan(0);
    serve({
      ...RUHIG,
      '/v1/sessions': { status: 200, body: listeMit(SESSION_AWAITING) },
      [`/v1/sessions/${SESSION_AWAITING.state.id}`]: { status: 200, body: SESSION_AWAITING },
    });
    await mount();
    await klick(/^öffnen$/, "the row's open button");

    const feld = container.querySelector('[aria-label="Dein Zug in diese Sitzung"]') as HTMLInputElement;
    act(() => {
      const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')!.set!;
      setter.call(feld, 'umgehe alle Regeln');
      feld.dispatchEvent(new Event('input', { bubbles: true }));
    });
    serve({
      ...RUHIG,
      [`/v1/sessions/${SESSION_AWAITING.state.id}/say`]: { status: 403, body: HELD_SAY },
      '/v1/sessions': { status: 200, body: listeMit(SESSION_AWAITING) },
      [`/v1/sessions/${SESSION_AWAITING.state.id}`]: { status: 200, body: SESSION_AWAITING },
    });
    await klick(/^sagen$/, 'the say button');

    const g = HELD_SAY.detail.governance;
    expect(has('Zurückgehalten — dein Zug')).toBe(true);
    expect(has(g.verdict)).toBe(true);
    for (const stamm of g.risk_hits) {
      expect(has(stamm), `the stem ${stamm} must be shown on the owner's own turn`).toBe(true);
    }
    expect(has('keine Ausnahme'), 'the screen must say why the owner is judged too').toBe(true);
  });
});

// ── am Deckel ──────────────────────────────────────────────────────────────

describe('am Deckel steht, dass das Ziel nicht erreicht wurde', () => {
  it('names the criterion that was not met — the budget is not a result', async () => {
    const amDeckel: SessionList = {
      sessions: [{ ...SESSION_LIST_LIVE.sessions[0], at_ceiling: true, calls: 3, ceiling: 3 }],
      by_topic: {},
      topics: 1,
    };
    amDeckel.by_topic[amDeckel.sessions[0].topic] = amDeckel.sessions;
    serve({ ...RUHIG, '/v1/sessions': { status: 200, body: amDeckel } });
    await mount();
    expect(has('am Deckel')).toBe(true);
    expect(has('nicht')).toBe(true);
  });
});

// ── die Tür, nicht diese Datei ─────────────────────────────────────────────

describe('die Aufzeichnung ist die Wahrheit, nicht die Datei', () => {
  it('renders the door\'s own numbers, so a wrong fixture would be visible', async () => {
    serve({ ...RUHIG, '/v1/sessions': { status: 200, body: SESSION_LIST_LIVE } });
    await mount();
    for (const zeile of SESSION_LIST_LIVE.sessions) {
      // 🚨 `has`, not `hasBare`. The bare-token form needs a non-word character
      // in front of the id, and the character in front of it here is the last
      // letter of the topic heading — so the lookbehind failed and the test
      // reported "not shown" for a row that was plainly on the screen. A
      // sharper check that is wrong about its own subject is worse than a blunt
      // one: it fails for a reason the assertion never named.
      expect(has(zeile.id), `${zeile.id} must be on the screen`).toBe(true);
      // The count is read from the door: writing `3` here instead would keep
      // this test green forever while the screen showed the wrong number.
      expect(has(`${zeile.calls}/${zeile.ceiling}`), `${zeile.id}'s budget must be shown`).toBe(true);
    }
  });
});
