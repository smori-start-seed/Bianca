/**
 * Trialog — drei Stimmen, eine Frage.
 *
 * The card this screen is built around: a trialog is not three answers, it is
 * three JUDGED utterances. So every card carries its verdict and the second
 * eye, and an off-limit utterance is shown in full with its stamp —
 * recorded, not censored. Deleting it would make the governor look effective
 * by making it invisible.
 */

import { useCallback, useEffect, useState } from 'react';
import { TabFrame, useSub } from '../components/Bianca/TabFrame';
import { useDoor, useElapsed } from '../components/Bianca/useDoor';
import {
  DeniedView,
  Empty,
  EngineDown,
  OraclePill,
  Pending,
  Pill,
  Skeleton,
  Tile,
  VerdictCard,
  VerdictPill,
  verdictTone,
} from '../components/Bianca/primitives';
import {
  listModels,
  listTrialogs,
  readTrialog,
  runTrialog,
  SovereignDenied,
  SovereignEngineDown,
  SovereignInterrupted,
} from '../lib/sovereign-api';
import type {
  InterruptedTrialog,
  ModelList,
  Trialog as TrialogResult,
  TrialogIndexEntry,
  TrialogTurn,
  Verdict,
} from '../lib/sovereign-api';
import { VoiceModels } from '../components/Bianca/VoiceModels';
import { SessionView } from './TrialogPage.session';
import { tabById } from '../components/Bianca/tabs';
import type { TabId } from '../components/Bianca/tabs';

const DEF = tabById('trialog')!;
const VOICES = ['Jarvis', 'Bianca', 'Urasil_light'] as const;

export function TrialogPage({ tab = 'trialog' }: { tab?: TabId }) {
  const def = tabById(tab) ?? DEF;
  const [sub, setSub] = useSub(tab, def.subs);

  return (
    <TabFrame
      tab={tab}
      subs={def.subs}
      active={sub}
      onSelect={setSub}
      title="Trialog"
      lede="Jarvis, Bianca und Urasil_light beraten dieselbe Frage. Jede Äußerung wird einzeln bewertet — und eine unzulässige wird gestempelt und behalten, nicht gelöscht."
      aside={<Pill tone="gold">drei Stimmen</Pill>}
    >
      {sub === 'run' && <RunView />}
      {sub === 'session' && <SessionView />}
      {sub === 'archive' && <ArchiveView />}
    </TabFrame>
  );
}

// ── one utterance, shown whole ─────────────────────────────────────────────

function TurnCard({ t }: { t: TrialogTurn }) {
  const denied = t.verdict === 'zurueckhalten';
  return (
    <article
      className="rounded-lg border p-3"
      style={{
        borderColor: denied ? 'color-mix(in srgb, var(--s-deny) 45%, transparent)' : 'var(--s-line)',
        background: denied
          ? 'color-mix(in srgb, var(--s-deny) 7%, transparent)'
          : 'var(--s-surface-2)',
      }}
    >
      <header className="flex items-center gap-2 flex-wrap mb-1.5">
        <span className="text-[13px] font-semibold" style={{ color: 'var(--s-ink)' }}>
          {t.voice}
        </span>
        <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          Runde {t.round}
        </span>
        {/* Set 29: which weights wrote THIS sentence. Three voices can be three
            models or one model in three masks, and the card is where a reader
            looks to tell those apart — so the name goes next to the voice, not
            into a report nobody opens. */}
        <span className="text-[11px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
          {t.model}
        </span>
        <span className="ml-auto flex items-center gap-1.5">
          <VerdictPill verdict={t.verdict} />
          <OraclePill oracle={t.oracle} />
        </span>
      </header>
      <p className="text-[13px] leading-relaxed whitespace-pre-wrap" style={{ color: 'var(--s-ink)' }}>
        {t.text}
      </p>
      {denied && (
        <div
          className="mt-2 pt-2 border-t text-[11px]"
          style={{ borderColor: 'color-mix(in srgb, var(--s-deny) 25%, transparent)', color: 'var(--s-deny)' }}
        >
          zurueckhalten — Begriffe: {t.risk_hits.join(', ') || '—'} · recorded, not censored
        </div>
      )}
    </article>
  );
}

/** The verdict tiles, shared by a finished and an interrupted deliberation. */
// The two `models` props are destructured, not merely declared in the type.
// They were in the annotation and not in the binding for one commit, and the
// type checker is the only thing that noticed: the body then read a name that
// was in scope nowhere, and the model line would have compiled to a crash at
// render time instead of at build time.
function Tiles({ g, eyeWarned, voices, rounds, models, sameModelEverywhere }: {
  g: TrialogResult['governance'];
  eyeWarned: number;
  voices: string[];
  rounds: number;
  models?: Record<string, string>;
  sameModelEverywhere?: boolean;
}) {
  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <Tile label="stimmen" value={voices.length} hint={`Runden ${rounds}`} />
        <Tile label="äußerungen" value={g.turns} hint="jede gelesen" />
        <Tile
          label="off-limit"
          value={g.off_limit}
          hint="gestempelt & behalten"
          tone={g.off_limit > 0 ? 'deny' : 'ok'}
        />
        <Tile label="gold-aligned" value={g.gold_aligned} tone="ok" />
        <Tile
          label="eye-warned"
          value={eyeWarned}
          hint="beratend, bindet nichts"
          tone={eyeWarned > 0 ? 'warn' : 'mut'}
        />
      </div>
      {/*
        Set 29. `distinct_verdicts` and the per-voice line are the measurement
        this door was extended for: over four rounds the twelve verdicts never
        once moved, and a page that only showed "12 äußerungen" cannot show that.
        Frozen is a **fact about the team**, not an error state — so it is
        rendered as a fact, with the count, and never as a red failure.
      */}
      <div
        className="rounded-lg border px-3 py-2 text-[12px] mt-2"
        style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
      >
        <span style={{ color: 'var(--s-ink)' }}>
          {g.distinct_verdicts} verschiedene Verdikte in {g.turns} Äußerungen
          {g.verdicts_moved ? '' : ' — die Stimmen haben sich nicht bewegt'}
        </span>
        <span style={{ color: 'var(--s-mut-2)' }}>
          {' · '}
          {Object.entries(g.per_voice_verdicts ?? {})
            .map(([voice, vs]) => `${voice}: ${vs.join(' → ') || '—'}`)
            .join('  ·  ')}
        </span>
        {models && Object.keys(models).length > 0 && (
          <div className="mt-1 text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
            {sameModelEverywhere
              ? 'alle drei Stimmen durch dasselbe Modell'
              : `${new Set(Object.values(models)).size} Modelle, eine je Stimme`}
            {' · '}
            {Object.entries(models)
              .map(([voice, m]) => `${voice} → ${m}`)
              .join('  ·  ')}
          </div>
        )}
      </div>
    </>
  );
}

// ── Rat ────────────────────────────────────────────────────────────────────

type RunState =
  | { kind: 'idle' }
  | { kind: 'pending' }
  | { kind: 'done'; r: TrialogResult }
  | { kind: 'interrupted'; partial: InterruptedTrialog }
  // The WHOLE verdict, not just its name. A refusal that keeps only
  // `verdict.verdict` leaves the reader with "no" and no way to check it —
  // no risk terms, no gold source, and no second eye on a vote that the
  // doctrine says must carry the eye's boundary. See DeniedView.
  | { kind: 'denied'; verdict: Verdict }
  | { kind: 'down'; why: string }
  | { kind: 'error'; message: string };

function RunView() {
  const [topic, setTopic] = useState('Wie sollte ein einzelner Knoten über Vertrauen im Myzel denken?');
  const [rounds, setRounds] = useState(1);
  const [state, setState] = useState<RunState>({ kind: 'idle' });
  const elapsed = useElapsed(state.kind === 'pending');
  // The host's own list. One fetch, and a failure leaves the pickers saying so
  // rather than showing an empty dropdown that looks like a choice.
  const [models, setModels] = useState<ModelList | null>(null);
  const [picked, setPicked] = useState<Record<string, string>>({});

  useEffect(() => {
    let cancelled = false;
    listModels()
      .then((m) => {
        if (!cancelled) setModels(m);
      })
      .catch(() => {
        /* the picker renders its own words; a refused list is not an error here */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const run = useCallback(async () => {
    if (!topic.trim()) return;
    setState({ kind: 'pending' });
    try {
      // An empty map means one model for all three — the behaviour this door had
      // before the field existed, so a reader who never touches a picker gets
      // exactly what they always got.
      const per = Object.fromEntries(VOICES.filter((v) => picked[v]).map((v) => [v, picked[v]]));
      setState({
        kind: 'done',
        r: await runTrialog(topic.trim(), rounds, undefined, Object.keys(per).length ? per : undefined),
      });
    } catch (e) {
      if (e instanceof SovereignInterrupted) setState({ kind: 'interrupted', partial: e.partial });
      else if (e instanceof SovereignDenied) setState({ kind: 'denied', verdict: e.verdict });
      else if (e instanceof SovereignEngineDown) setState({ kind: 'down', why: e.why });
      else setState({ kind: 'error', message: (e as Error).message });
    }
  }, [topic, rounds, picked]);

  const result = state.kind === 'done' ? state.r : state.kind === 'interrupted' ? state.partial : null;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-3 gap-2">
        {VOICES.map((v) => (
          <div
            key={v}
            className="rounded-lg border px-2 py-1.5 text-center"
            style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
          >
            <div className="text-[12px] font-medium" style={{ color: 'var(--s-ink)' }}>
              {v}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2 flex-wrap items-end">
        <div className="flex-1 min-w-[16rem]">
          <label className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Thema
          </label>
          <textarea
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            rows={2}
            aria-label="Thema der Beratung"
            className="w-full rounded-lg border px-3 py-2 text-[13px] outline-none resize-y"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          />
        </div>
        <div>
          <label className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Runden
          </label>
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((n) => (
              <button
                key={n}
                onClick={() => setRounds(n)}
                className="w-8 h-8 rounded-lg text-[13px] cursor-pointer"
                style={{
                  border: `1px solid ${rounds === n ? 'var(--s-gold)' : 'var(--s-line)'}`,
                  background: rounds === n ? 'color-mix(in srgb, var(--s-gold) 14%, transparent)' : 'transparent',
                  color: rounds === n ? 'var(--s-gold)' : 'var(--s-mut)',
                }}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
        <button
          onClick={run}
          disabled={state.kind === 'pending'}
          className="px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer disabled:opacity-50"
          style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
        >
          Rat einberufen
        </button>
      </div>

      {/* Set 30. The pickers sit under the form, not above it: the question comes
          first, and the weights are a detail of how it is answered. */}
      <VoiceModels
        list={models}
        picked={picked}
        onPick={(voice, model) => setPicked((old) => ({ ...old, [voice]: model }))}
      />

      {state.kind === 'pending' && <Pending label="drei Stimmen, eine Frage" seconds={elapsed} />}
      {state.kind === 'down' && <EngineDown why={state.why} />}
      {state.kind === 'error' && <EngineDown why={state.message} />}
      {state.kind === 'denied' && (
        // `scope` says the one thing the card cannot: the door refuses the
        // TOPIC before spending engine time, so a reader looking at zero turns
        // can tell "the deliberation never began" from "it produced nothing".
        <DeniedView
          verdict={state.verdict}
          label="Thema abgelehnt"
          scope="das Thema selbst wurde abgelehnt, bevor eine einzige Stimme sprach. Für eine abgelehnte Frage wird keine Motorzeit verbraucht."
        />
      )}

      {state.kind === 'interrupted' && (
        <div
          className="rounded-lg border p-3 text-[12px]"
          style={{
            borderColor: 'color-mix(in srgb, var(--s-warn) 45%, transparent)',
            background: 'color-mix(in srgb, var(--s-warn) 8%, transparent)',
            color: 'var(--s-warn)',
          }}
        >
          <strong>unterbrochen</strong> — {state.partial.reason}. Die bisherigen Äußerungen sind
          bewertet und gesichert als <span className="font-mono">{state.partial.saved}</span>.
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <Tiles
            g={result.governance}
            eyeWarned={result.eye_warned}
            voices={result.voices}
            rounds={result.rounds}
            models={result.models}
            sameModelEverywhere={result.same_model_everywhere}
          />
          {result.turns.length === 0 ? (
            <Empty title="Keine Stimme hat gesprochen">
              Die Beratung wurde unterbrochen, bevor eine Äußerung fertig war. Das ist ein
              Ereignis und steht im Ledger.
            </Empty>
          ) : (
            result.turns.map((t, i) => <TurnCard key={i} t={t} />)
          )}
          <div className="text-[11px]" style={{ color: 'var(--s-mut)' }}>
            {result.summary} · gesichert als <span className="font-mono">{result.saved}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Protokoll ──────────────────────────────────────────────────────────────

function ArchiveView() {
  const door = useDoor<{ trialogs: TrialogIndexEntry[] }>(() => listTrialogs(), []);
  const [open, setOpen] = useState<{ name: string; text: string } | null>(null);
  const [opening, setOpening] = useState<string | null>(null);

  const openOne = useCallback(async (name: string) => {
    setOpening(name);
    try {
      const r = await readTrialog(name);
      setOpen({ name, text: r.trialog });
    } catch {
      setOpen({ name, text: '(dieses Protokoll ist nicht mehr lesbar)' });
    } finally {
      setOpening(null);
    }
  }, []);

  if (door.kind === 'loading') return <Skeleton rows={4} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'error') return <EngineDown why={door.message} />;
  if (door.kind === 'denied' || door.kind === 'interrupted') return null;

  const items = door.data.trialogs ?? [];
  if (items.length === 0) {
    return (
      <Empty title="Noch kein Protokoll">
        Sobald drei Stimmen zu einer Frage gesprochen haben, steht die Beratung hier — und im
        Ledger, unabhängig davon, ob sie vollständig war.
      </Empty>
    );
  }

  return (
    <div className="space-y-2">
      {items.map((t) => (
        <div
          key={t.name}
          className="rounded-lg border p-3"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
        >
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-[12px]" style={{ color: 'var(--s-ink)' }}>
              {t.name}
            </span>
            <Pill tone="mut">{t.lines} Zeilen</Pill>
            <Pill tone="mut">{t.voices.length} Stimmen</Pill>
            <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
              {t.saved}
            </span>
            <button
              onClick={() => void openOne(t.name)}
              className="ml-auto px-2.5 py-1 rounded-full text-[11px] cursor-pointer"
              style={{ border: '1px solid var(--s-line)', color: 'var(--s-mut)' }}
            >
              {opening === t.name ? 'liest…' : 'lesen'}
            </button>
          </div>
          <p className="text-[12px] mt-1.5 line-clamp-2" style={{ color: 'var(--s-mut)' }}>
            <span style={{ color: 'var(--s-gold)' }}>{t.opening_voice}:</span> {t.opening}
          </p>
        </div>
      ))}

      {open && (
        <section
          className="rounded-lg border p-3"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface)' }}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="font-mono text-[12px]" style={{ color: 'var(--s-ink)' }}>
              {open.name}
            </span>
            <button
              onClick={() => setOpen(null)}
              className="ml-auto px-2 py-0.5 rounded-full text-[11px] cursor-pointer"
              style={{ border: '1px solid var(--s-line)', color: 'var(--s-mut)' }}
            >
              schließen
            </button>
          </div>
          <pre
            className="text-[12px] leading-relaxed whitespace-pre-wrap font-mono"
            style={{ color: 'var(--s-ink-2)' }}
          >
            {open.text}
          </pre>
        </section>
      )}
    </div>
  );
}
