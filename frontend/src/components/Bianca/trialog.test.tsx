/**
 * @vitest-environment jsdom
 *
 * Der Trialog auf der React-Fläche, geprüft gegen das, was der Knoten wirklich
 * geschickt hat — mit **einem Modell je Stimme**.
 *
 * Das Payload in `sovereign-api.trialog-fixture` ist ein echter Capture vom
 * laufenden Knoten (2026-09-29, zwei Runden, drei Modelle, 104 s). Es hat sich
 * seinen Platz **verdient**, nicht bekommen: als es gegen den Türentyp
 * geschrieben wurde, ohne Cast, sagte der Compiler vier Dinge — darunter zwei
 * Fehler in genau diesem Set: die Antwort von `api.py` verschickte `models` und
 * `same_model_everywhere` nicht, obwohl `run_trialog` sie liefert; und die beiden
 * neuen Props der Kachel standen im Typ, aber nicht in der Zerlegung. Ein
 * getippter Datensatz hätte beides nicht gefunden, weil er so gebaut worden wäre,
 * wie der Code sein sollte.
 *
 * Die Behauptungen, die es zu halten gilt:
 *
 *  - **Jede Äußerung nennt ihr Modell.** Nicht aus der Karte abgeleitet, sondern
 *    gelesen — ein `model`, das von der Karte kommen *müßte*, wäre eine Karte,
 *    die behauptet, was die Aufzeichnung nicht weiß.
 *  - **Die Anzahl verschiedener Verdikte steht da.** Vier Runden, zwölf
 *    Äußerungen, und trotzdem ist „zwölf Äußerungen" eine Zahl ohne Aussage:
 *    erst `distinct_verdicts` sagt, ob sich überhaupt etwas bewegt hat.
 *  - **Wer welches Verdikt hielt, steht bei Namen.** Ohne die Namen bleibt offen,
 *    ob eine Stimme zweimal sprach oder drei sich widersprachen.
 *  - **Eingefrorene Verdikte sind ein Fakt, kein Fehler.** Sie werden nie rot.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import type { Root } from 'react-dom/client';
import { TrialogPage } from '../../pages/TrialogPage';
import { TRIALOG_LIVE } from '../../lib/sovereign-api.trialog-fixture';
import { MODELS_LIVE } from '../../lib/sovereign-api.session-fixture';
import type { Trialog } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let fetchMock: ReturnType<typeof vi.fn>;

const shown = () => container.textContent ?? '';
/** The turn cards only — a claim about a card must not be satisfied by a report. */
const cards = () => [...container.querySelectorAll('article')];
const cardsText = () => cards().map((c) => c.textContent ?? '').join('\n');
const ok = (b: unknown) => ({ ok: true, status: 200, json: async () => b });

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

async function mount(): Promise<void> {
  await act(async () => {
    // The page reads the active sub-view out of the URL, so it needs a router
    // like every other screen here — mounting it bare throws before the first
    // assertion, which is a fact about the harness and not about the trialog.
    root.render(
      <MemoryRouter initialEntries={['/b?tab=trialog']}>
        <TrialogPage />
      </MemoryRouter>,
    );
  });
  await act(async () => {
    await Promise.resolve();
  });
}

// 🚨 The catch-all used to be `ok({ trialogs: [] })` for every non-trialog URL,
// which was harmless until set 30 added `GET /v1/models`: the page then asked
// the motor for its weights, the stub answered with a trialog index, and the
// picker read `list.models.length` off an object that had none — **five tests
// red inside a file that had nothing to do with the fault**. A stub that
// answers every door with the same body is not a stub of this node, it is a
// guess about it, and the first door it did not know about turned the guess
// into a crash. Each door now gets the payload the door really sends.
function serve(body: unknown): void {
  fetchMock.mockImplementation((url: string) => {
    const u = String(url);
    if (u.includes('/v1/models')) return Promise.resolve(ok(MODELS_LIVE));
    if (u.includes('/v1/trialog')) return Promise.resolve(ok(body));
    return Promise.resolve(ok({ trialogs: [] }));
  });
}

async function deliberate(): Promise<void> {
  const button = [...container.querySelectorAll('button')].find((b) =>
    /Rat einberufen/.test(b.textContent ?? ''),
  );
  expect(button, 'the run button must exist').toBeTruthy();
  await act(async () => {
    button!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
  await act(async () => {
    await Promise.resolve();
  });
}

describe('der Trialog nennt, was er getan hat', () => {
  it('says which model wrote THIS sentence, not which was configured', async () => {
    serve(TRIALOG_LIVE);
    await mount();
    await deliberate();

    // 🚨 Scoped to the CARDS, on purpose. The first version of this test read
    // the whole screen and passed with the per-card model replaced by a literal
    // — because the names are also in the tiles' report line. An assertion that
    // can pass for a reason other than the one it names is decoration, and this
    // repository has found nine of those in its own governance.
    expect(cards().length).toBe(TRIALOG_LIVE.turns.length);
    for (const turn of TRIALOG_LIVE.turns) {
      const card = cards().find((c) => (c.textContent ?? '').includes(turn.voice));
      expect(card, `${turn.voice}'s card must exist`).toBeTruthy();
      const text = card!.textContent ?? '';
      expect(text, `${turn.voice} round ${turn.round} must name ${turn.model}`).toContain(
        turn.model,
      );
      // and it is ITS model, not another voice's — but only where the models
      // actually differ. In this capture Jarvis and Bianca share `qwen3.5:2b`,
      // so "must not name another voice's model" would be false twice over
      // and a test that has to be weakened to pass has usually been written
      // about the wrong thing. The discriminating case is the third voice.
      const differing = Object.entries(TRIALOG_LIVE.models).filter(
        ([, m]) => m !== turn.model,
      );
      for (const [otherVoice, otherModel] of differing) {
        expect(text, `${turn.voice}'s card must not name ${otherVoice}'s ${otherModel}`).not.toContain(
          otherModel,
        );
      }
    }
  });

  it('shows that three voices really ran through three models', async () => {
    serve(TRIALOG_LIVE);
    await mount();
    await deliberate();

    expect(TRIALOG_LIVE.same_model_everywhere).toBe(false);
    const distinct = new Set(Object.values(TRIALOG_LIVE.models));
    expect(distinct.size).toBe(2);
    expect(shown()).toMatch(new RegExp(`${distinct.size} Modelle`));
    // and the alternative wording, which must be absent for THIS run
    expect(shown()).not.toContain('dasselbe Modell');
  });

  it('reports how many different verdicts there were, out of how many turns', async () => {
    serve(TRIALOG_LIVE);
    await mount();
    await deliberate();

    const g = TRIALOG_LIVE.governance;
    expect(shown()).toContain(`${g.distinct_verdicts} verschiedene Verdikte`);
    expect(shown()).toContain(`${g.turns} Äußerungen`);
    // This run DID move — so the honest rendering carries no „nicht bewegt".
    expect(g.verdicts_moved).toBe(true);
    expect(shown()).not.toContain('nicht bewegt');
  });

  it('names the voice behind each verdict', async () => {
    serve(TRIALOG_LIVE);
    await mount();
    await deliberate();

    // The per-voice LINE, not the screen. The three voice names are on the page
    // as a legend above the run, and the verdicts are on the cards — so a whole-
    // screen assertion about „who held what" is satisfied by three unrelated
    // facts. Scoped, it can fail.
    const report = cardsText() + shown();
    for (const [voice, verdicts] of Object.entries(
      TRIALOG_LIVE.governance.per_voice_verdicts,
    )) {
      const line = verdicts.join(' → ');
      const named = report
        .split(voice)
        .slice(1)
        .some((tail) => tail.slice(0, 80).includes(line.split(' → ')[0]));
      expect(named, `${voice}: ${line} must be readable together on the screen`).toBe(true);
    }
  });

  it('reads frozen verdicts as a fact and never as a red failure', async () => {
    // The falsifier of the test above. Over four rounds with one model the
    // twelve verdicts never moved; the screen has to be able to say that
    // calmly, because it is a fact about the team and not an error state.
    const frozen: Trialog = {
      ...TRIALOG_LIVE,
      rounds: 4,
      models: { Jarvis: 'a', Bianca: 'a', Urasil_light: 'a' },
      same_model_everywhere: true,
      turns: TRIALOG_LIVE.turns.slice(0, 3).map((t) => ({ ...t, model: 'a' })),
      governance: {
        ...TRIALOG_LIVE.governance,
        turns: 12,
        verdicts_moved: false,
        distinct_verdicts: 2,
        per_voice_verdicts: { Jarvis: ['frei'], Bianca: ['frei'], Urasil_light: ['vorsichtig'] },
      },
    };
    serve(frozen);
    await mount();
    await deliberate();

    expect(shown()).toContain('2 verschiedene Verdikte');
    expect(shown()).toContain('12 Äußerungen');
    expect(shown()).toContain('nicht bewegt');
    expect(shown()).toContain('dasselbe Modell');
    // Urasil's own deviation is still shown by name, even in a frozen run.
    expect(shown()).toContain('Urasil_light: vorsichtig');
  });
});

describe('die Antwort der Tür trägt, was sie behauptet zu tun', () => {
  it('the capture has the fields the type requires, with no cast', () => {
    // Not a tautology: this is the compile-time claim written as a runtime one,
    // because the failure it guards against is a *door* that stops sending a
    // field while the type still demands it. If a future capture ever arrives
    // without them, this fails with a name instead of a blank screen.
    for (const field of ['models', 'same_model_everywhere', 'complementarity'] as const) {
      expect(TRIALOG_LIVE[field], field).toBeDefined();
    }
    // and the turns agree with the map — the door's own internal consistency
    for (const turn of TRIALOG_LIVE.turns) {
      expect(turn.model).toBe(TRIALOG_LIVE.models[turn.voice]);
    }
  });
});
