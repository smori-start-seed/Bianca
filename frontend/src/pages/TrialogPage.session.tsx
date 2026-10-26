/**
 * The working session — set 30.
 *
 * Kept in its own file, and the reason is a defect this set found rather than a
 * taste: the first version grew inside `TrialogPage.tsx`, where the props were
 * declared in a type annotation and **not** in the destructuring for one commit.
 * The type checker accepted it, the model line compiled to a name that was in
 * scope nowhere, and the failure would have appeared at render time on the
 * reviewer's screen instead of at build time on mine. A separate file with the
 * props in the *binding* is the repair; the discipline it enforces is that a
 * screen which shows a session is a screen about sessions, and can be read on
 * its own.
 *
 * What this screen is built around, in the order the owner asked for it:
 *
 *  1. A session is a **process, not a request**. It is started, it runs, and it
 *     ends on a criterion or on the owner's word. The screen says which of those
 *     is true *right now* — `pending` on a stop is the field that matters, since
 *     a live run closes at its next voice boundary and a model call in flight is
 *     not interrupted.
 *  2. The **goal** and the **criterion** are named, because a run without them is
 *     three conversations in turn. The criterion vocabulary comes from the node
 *     (`GET /v1/sessions/criteria`), never from a list in this file: a third word
 *     offered here would be a promise the seam keeps.
 *  3. A refusal shows its **evidence** — verdict, stems, gold source, the second
 *     eye — on every door, including the owner's own turn. The owner is a voice,
 *     not an exemption, and a held turn is held with the same stamp as a held
 *     topic.
 *  4. The **memory carries verdicts, not the transcript.** The prompt grows
 *     quadratically with the round number (measured: 1 · 3.99 · 8.97 · 15.94
 *     characters per call for rounds 1–4, R² = 1.0000 against n²), so at forty
 *     rounds a voice would re-read ~100,000 characters of its own prose. The
 *     card says that in words, because a reader looking at a short memory should
 *     know it is short *by design* and not by omission.
 *  5. A stop that was asked for and **never answered** is shown. It is the one
 *     state where the record holds a request no run acted on, and a status alone
 *     would read as a session that simply never began.
 */

import { useCallback, useEffect, useState } from 'react';
import {
  DeniedView,
  Empty,
  EngineDown,
  OraclePill,
  Pending,
  Pill,
  Skeleton,
  Tile,
  VerdictPill,
  verdictTone,
} from '../components/Bianca/primitives';
import { useDoor, useElapsed } from '../components/Bianca/useDoor';
import { VoiceModels, VOICES } from '../components/Bianca/VoiceModels';
import {
  acceptSession,
  getSession,
  listModels,
  listSessionCriteria,
  listSessions,
  sayToSession,
  SovereignDenied,
  SovereignEngineDown,
  startSession,
  stopSession,
} from '../lib/sovereign-api';
import type {
  ModelList,
  SessionCriteria,
  SessionDetail,
  SessionList,
  SessionStopResult,
  ShieldDirection,
  Verdict,
} from '../lib/sovereign-api';

type StartState =
  | { kind: 'idle' }
  | { kind: 'pending' }
  | { kind: 'done'; id: string }
  // A held topic carries the WHOLE verdict. A refusal that keeps only its name
  // leaves the reader with "nein" and no way to check it.
  | { kind: 'denied'; verdict: Verdict; where: string; direction?: ShieldDirection }
  | { kind: 'error'; message: string };

// ── the list: sessions under their topic ───────────────────────────────────

/**
 * One row. `stop_asked_not_answered` is rendered as its own line and not folded
 * into the status, because it is a different kind of fact: the status says what
 * the session is, and this says what was asked of it and did not happen.
 */
function SessionRowCard({
  row,
  onOpen,
  open,
}: {
  row: SessionList['sessions'][number];
  onOpen: (id: string) => void;
  open: boolean;
}) {
  const tone = verdictTone(row.status === 'complete' ? 'frei' : row.status);
  return (
    <div
      className="rounded-lg border px-3 py-2"
      style={{
        borderColor: open ? 'var(--s-gold)' : 'var(--s-line)',
        background: 'var(--s-surface-2)',
      }}
    >
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-[12px] font-mono" style={{ color: 'var(--s-ink)' }}>
          {row.id}
        </span>
        <Pill tone={tone}>{row.status}</Pill>
        {row.running && <Pill tone="warn">läuft</Pill>}
        <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          {row.calls}/{row.ceiling} Aufrufe · {row.rounds} Runden
        </span>
        <button
          onClick={() => onOpen(row.id)}
          className="ml-auto px-2.5 py-1 rounded-full text-[11px] cursor-pointer"
          style={{ border: '1px solid var(--s-line)', color: 'var(--s-mut)' }}
        >
          öffnen
        </button>
      </div>
      <p className="text-[12px] mt-1" style={{ color: 'var(--s-mut)' }}>
        {row.goal}
      </p>
      <p className="text-[11px] mt-0.5" style={{ color: 'var(--s-mut-2)' }}>
        endet bei <span className="font-mono">{row.stop_when}</span>
        {row.at_ceiling && (
          <>
            {' · '}
            <span style={{ color: 'var(--s-warn)' }}>
              am Deckel — das Ziel wurde <em>nicht</em> erreicht
            </span>
          </>
        )}
      </p>
      {row.stop_asked_not_answered && (
        <p className="text-[11px] mt-1" style={{ color: 'var(--s-warn)' }}>
          Ein Stopp wurde angefragt und nie beantwortet: die Anfrage steht in der Aufzeichnung,
          kein Lauf hat sie gelesen. Das ist kein Stillstand, das ist eine offene Frage an die
          Aufzeichnung.
        </p>
      )}
    </div>
  );
}

function SessionListView({
  onOpen,
  openId,
  reloadNonce,
}: {
  onOpen: (id: string) => void;
  openId: string | null;
  reloadNonce: number;
}) {
  const door = useDoor<SessionList>(() => listSessions(), [reloadNonce]);

  if (door.kind === 'loading') return <Skeleton rows={3} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'error') return <EngineDown why={door.message} />;
  if (door.kind === 'denied' || door.kind === 'interrupted') return null;

  const { by_topic: byTopic, topics } = door.data;
  const eintraege = Object.entries(byTopic ?? {});
  if (eintraege.length === 0) {
    return (
      <Empty title="Noch keine Sitzung">
        Eine Arbeitssitzung braucht ein Ziel und ein Ende. Beides steht im Formular darüber — und
        ohne eines von beidem wäre es ein Lauf, der aus keinem Grund aufhört.
      </Empty>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
        {topics} {topics === 1 ? 'Thema' : 'Themen'} · {door.data.sessions.length} Sitzungen
      </p>
      {eintraege.map(([thema, zeilen]) => (
        <section key={thema} className="space-y-1.5">
          <h4 className="text-[11px] uppercase tracking-wider" style={{ color: 'var(--s-mut)' }}>
            {thema}
          </h4>
          {zeilen.map((r) => (
            <SessionRowCard key={r.id} row={r} onOpen={onOpen} open={r.id === openId} />
          ))}
        </section>
      ))}
    </div>
  );
}

// ── the detail: one session, whole ─────────────────────────────────────────

function MemoryTiles({ d }: { d: SessionDetail }) {
  const m = d.memory;
  return (
    <div className="space-y-2">
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        <Tile label="aufrufe" value={m.calls} hint={`von ${d.state.ceiling}`} />
        <Tile label="runden" value={m.rounds} />
        <Tile label="verdikt-arten" value={m.distinct_verdicts} tone={m.distinct_verdicts > 1 ? 'ok' : 'mut'} />
        <Tile label="owner-züge" value={m.owner_turns} hint={`${m.held_owner_turns} gehalten`} />
        <Tile label="eye-warned" value={m.eye_warned} hint="beratend" tone={m.eye_warned > 0 ? 'warn' : 'mut'} />
      </div>
      <div
        className="rounded-lg border px-3 py-2 text-[12px]"
        style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
      >
        <div style={{ color: 'var(--s-ink)' }}>
          {m.verdicts_moved
            ? `${m.distinct_verdicts} verschiedene Verdikte — die Stimmen haben sich bewegt`
            : 'die Stimmen haben über alle Runden dasselbe Verdikt gehalten'}
        </div>
        <div className="text-[11px] mt-1" style={{ color: 'var(--s-mut-2)' }}>
          {Object.entries(m.per_voice_verdicts ?? {})
            .map(([voice, vs]) => `${voice}: ${vs.join(' → ') || '—'}`)
            .join('  ·  ')}
        </div>
        {/* The memory is short on purpose, and the reason is a measurement. A
            reader looking at three verdicts instead of thirty turns should know
            the omission is a decision, not a truncation. */}
        <div className="text-[11px] mt-1.5" style={{ color: 'var(--s-mut-2)' }}>
          Das Gedächtnis trägt <strong style={{ color: 'var(--s-ink)' }}>Verdikt-e</strong>, nicht
          das Protokoll — {m.carries}.
        </div>
        <div className="text-[11px] mt-1" style={{ color: 'var(--s-warn)' }}>
          Es kann nicht festhalten: {m.cannot_record}.
        </div>
      </div>
    </div>
  );
}

/** One line of the record. NOT `TurnCard`: a session turn may have no model. */
function SessionTurnCard({ t }: { t: SessionDetail['turns'][number] }) {
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
        {/* 🚨 The owner's turn has no model, and saying so is better than
            printing `undefined`. The field is `string | null` for exactly this
            reason — a hand-written type said `string` and the face rendered
            "undefined" on its first run. */}
        {t.model ? (
          <span className="text-[11px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            {t.model}
          </span>
        ) : (
          <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
            ohne Modell — deine Worte
          </span>
        )}
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
      {t.note && (
        <div className="mt-2 pt-2 border-t text-[11px]" style={{ borderColor: 'var(--s-line)', color: 'var(--s-mut)' }}>
          {t.note}
        </div>
      )}
      {t.stopped && (
        <div className="mt-2 pt-2 border-t text-[11px]" style={{ borderColor: 'var(--s-line)', color: 'var(--s-warn)' }}>
          der Motor brach in diesem Zug ab: {t.stopped}
        </div>
      )}
    </article>
  );
}

function SessionDetailView({
  id,
  onChanged,
}: {
  id: string;
  onChanged: () => void;
}) {
  const door = useDoor<SessionDetail>(() => getSession(id), [id]);
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState<'' | 'say' | 'accept' | 'stop'>('');
  // The say door's own answer is **not** kept in state. It writes the turn into
  // the record and `neu()` reads it back out, so a copy of it here would be the
  // third place the owner's turn lives — and the one that could disagree with
  // the two that matter. The first version kept it and rendered nothing.
  const [stopAntwort, setStopAntwort] = useState<SessionStopResult | null>(null);
  const [fehler, setFehler] = useState('');
  // 🚨 The verdict a refusal came with, whole. Held here and rendered through
  // `DeniedView` rather than as a string, so the stems, the gold source and the
  // second eye are on the screen with the "no".
  const [gehalten, setGehalten] = useState<{
    verdict: Verdict;
    where: string;
    direction?: ShieldDirection;
  } | null>(null);

  const neu = useCallback(() => {
    door.reload();
    onChanged();
  }, [door, onChanged]);

  const say = useCallback(async () => {
    const text = note.trim();
    if (!text) return;
    setBusy('say');
    setFehler('');
    try {
      await sayToSession(id, text);
      setNote('');
      neu();
    } catch (e) {
      if (e instanceof SovereignDenied)
        setGehalten({ verdict: e.verdict, where: 'dein Zug', direction: e.direction });
      else if (e instanceof SovereignEngineDown) setFehler(e.why);
      else setFehler((e as Error).message);
    } finally {
      setBusy('');
    }
  }, [id, note, neu]);

  const accept = useCallback(async () => {
    setBusy('accept');
    setFehler('');
    try {
      await acceptSession(id);
      neu();
    } catch (e) {
      setFehler((e as Error).message);
    } finally {
      setBusy('');
    }
  }, [id, neu]);

  const stop = useCallback(async () => {
    setBusy('stop');
    setFehler('');
    try {
      setStopAntwort(await stopSession(id, 'das reicht mir für heute'));
      neu();
    } catch (e) {
      setFehler((e as Error).message);
    } finally {
      setBusy('');
    }
  }, [id, neu]);

  if (door.kind === 'loading') return <Skeleton rows={4} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'error') return <EngineDown why={door.message} />;
  if (door.kind === 'denied') {
    return (
      <DeniedView
        verdict={door.verdict}
        label="Sitzung nicht lesbar"
        scope="das Tor hat etwas gehalten, das diese Tür lesen sollte — der Grund steht links."
        direction={door.direction}
      />
    );
  }
  if (door.kind === 'interrupted') return null;

  const d = door.data;
  const s = d.state;
  const geschlossen = !!s.closed && !['new', 'running'].includes(s.status);
  const offen = d.proposals.find((p) => !p.closed);

  return (
    <div className="space-y-3">
      <div
        className="rounded-lg border px-3 py-2"
        style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
      >
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-[13px] font-mono" style={{ color: 'var(--s-ink)' }}>
            {s.id}
          </span>
          <Pill tone={verdictTone(s.status === 'complete' ? 'frei' : s.status)}>{s.status}</Pill>
          {d.running ? <Pill tone="warn">läuft</Pill> : null}
          {d.inbox > 0 && <Pill tone="mut">{d.inbox} im Eingang</Pill>}
        </div>
        <p className="text-[12px] mt-1.5" style={{ color: 'var(--s-ink)' }}>
          <strong>Ziel:</strong> {s.goal}
        </p>
        <p className="text-[11px] mt-0.5" style={{ color: 'var(--s-mut-2)' }}>
          endet bei <span className="font-mono">{s.stop_when}</span> · Deckel {s.ceiling} Aufrufe ·{' '}
          {d.memory.calls} bezahlt
          {d.memory.calls >= s.ceiling && (
            <span style={{ color: 'var(--s-warn)' }}> · am Deckel — das Ziel wurde nicht erreicht</span>
          )}
        </p>
        {s.closed_because && (
          <p className="text-[11px] mt-1" style={{ color: 'var(--s-mut)' }}>
            {s.closed_because}
            {s.closed_by && (
              <span style={{ color: 'var(--s-mut-2)' }}> — geschrieben von {s.closed_by}</span>
            )}
          </p>
        )}
      </div>

      <MemoryTiles d={d} />

      {gehalten && (
        <DeniedView
          verdict={gehalten.verdict}
          label={`Zurückgehalten — ${gehalten.where}`}
          scope="der Eigentümer ist eine Stimme, keine Ausnahme. Auch dein Zug wird vor dem Team gelesen."
          direction={gehalten.direction}
        />
      )}
      {fehler && (
        <div
          className="rounded-lg border px-3 py-2 text-[12px]"
          style={{ borderColor: 'var(--s-warn)', color: 'var(--s-warn)' }}
        >
          {fehler}
        </div>
      )}
      {stopAntwort && (
        <div
          className="rounded-lg border px-3 py-2 text-[12px]"
          style={{
            borderColor: stopAntwort.pending ? 'var(--s-warn)' : 'var(--s-line)',
            color: stopAntwort.pending ? 'var(--s-warn)' : 'var(--s-mut)',
          }}
        >
          {stopAntwort.pending ? (
            <>
              <strong>angefragt, noch nicht geschlossen</strong> — {stopAntwort.stops_when}.{' '}
              {stopAntwort.note}
            </>
          ) : (
            <>
              <strong>geschlossen</strong> — {stopAntwort.closed_because}. {stopAntwort.note}
            </>
          )}
        </div>
      )}

      {/* The three doors, and only the three that exist. A button for a door the
          node does not have is a promise the seam keeps. */}
      <div className="flex gap-2 flex-wrap items-end">
        <div className="flex-1 min-w-[15rem]">
          <label className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Sag dem Team
          </label>
          <input
            value={note}
            onChange={(e) => setNote(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) void say();
            }}
            placeholder="dein Zug — wird gelesen wie jeder andere"
            aria-label="Dein Zug in diese Sitzung"
            className="w-full rounded-lg border px-3 py-2 text-[13px] outline-none"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          />
        </div>
        <button
          onClick={() => void say()}
          disabled={busy !== '' || !note.trim()}
          className="px-3 py-2 rounded-lg text-[13px] cursor-pointer disabled:opacity-50"
          style={{ border: '1px solid var(--s-line)', color: 'var(--s-ink)' }}
        >
          {busy === 'say' ? 'liest…' : 'sagen'}
        </button>
        <button
          onClick={() => void accept()}
          disabled={busy !== '' || !offen}
          title={offen ? undefined : 'das Team hat nichts vorgeschlagen'}
          className="px-3 py-2 rounded-lg text-[13px] cursor-pointer disabled:opacity-50"
          style={{ border: '1px solid var(--s-line)', color: offen ? 'var(--s-gold)' : 'var(--s-mut-2)' }}
        >
          annehmen
        </button>
        <button
          onClick={() => void stop()}
          disabled={busy !== '' || geschlossen}
          className="px-3 py-2 rounded-lg text-[13px] cursor-pointer disabled:opacity-50"
          style={{ border: '1px solid var(--s-line)', color: geschlossen ? 'var(--s-mut-2)' : 'var(--s-ink)' }}
        >
          {busy === 'stop' ? 'fragt an…' : 'anhalten'}
        </button>
      </div>

      {offen && (
        <div
          className="rounded-lg border px-3 py-2 text-[12px]"
          style={{ borderColor: 'var(--s-gold)', background: 'color-mix(in srgb, var(--s-gold) 8%, transparent)' }}
        >
          <strong>das Team schlägt den Abschluß vor</strong> (Runde {offen.round}) — {offen.trigger}.
          <span style={{ color: 'var(--s-mut-2)' }}> Nur du kannst ihn annehmen; ein Prozeß kann es nicht.</span>
        </div>
      )}

      {d.turns.length === 0 ? (
        <Empty title="Noch kein Zug">
          Das Team hat noch nichts gesagt. Ein Lauf, der erst den Motor braucht, ist kein stiller
          Lauf — er steht hier als „läuft“.
        </Empty>
      ) : (
        d.turns.map((t, i) => <SessionTurnCard key={`${t.round}-${t.voice}-${i}`} t={t} />)
      )}

      {/* The last writer's note, quoted rather than paraphrased: it is the record
          saying why it did not overwrite a person's decision. */}
      {d.turns.length > 0 && d.turns[d.turns.length - 1].note && (
        <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          {d.turns[d.turns.length - 1].note}
        </p>
      )}
    </div>
  );
}

// ── the start form ─────────────────────────────────────────────────────────

export function SessionView() {
  const [topic, setTopic] = useState('');
  const [goal, setGoal] = useState('');
  const [until, setUntil] = useState('');
  const [ceiling, setCeiling] = useState(12);
  const [picked, setPicked] = useState<Record<string, string>>({});
  const [state, setState] = useState<StartState>({ kind: 'idle' });
  const [openId, setOpenId] = useState<string | null>(null);
  const [listNonce, setListNonce] = useState(0);
  const elapsed = useElapsed(state.kind === 'pending');

  const [models, setModels] = useState<ModelList | null>(null);
  const [criteria, setCriteria] = useState<SessionCriteria | null>(null);

  // 🚨 Two doors, two fetches, and **no retry loop**. The first version had the
  // picker call `listModels()` whenever the list was empty, and the fetch called
  // the picker — on a motor that answers with no models that is an endless chain
  // of GETs from a page with nothing to wait for.
  useEffect(() => {
    let cancelled = false;
    listModels().then((m) => !cancelled && setModels(m)).catch(() => undefined);
    listSessionCriteria()
      .then((c) => !cancelled && setCriteria(c))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const start = useCallback(async () => {
    if (!topic.trim() || !goal.trim()) return;
    setState({ kind: 'pending' });
    try {
      const per = Object.fromEntries(VOICES.filter((v) => picked[v]).map((v) => [v, picked[v]]));
      const r = await startSession({
        topic: topic.trim(),
        goal: goal.trim(),
        stop_when: until,
        ceiling,
        ...(Object.keys(per).length ? { models: per } : {}),
      });
      setState({ kind: 'done', id: r.id });
      setOpenId(r.id);
      setListNonce((n) => n + 1);
    } catch (e) {
      if (e instanceof SovereignDenied) {
        setState({
          verdict: e.verdict,
          where: 'das Thema',
          kind: 'denied',
          direction: e.direction,
        });
      } else if (e instanceof SovereignEngineDown) {
        setState({ kind: 'error', message: e.why });
      } else {
        setState({ kind: 'error', message: (e as Error).message });
      }
    }
  }, [topic, goal, until, ceiling, picked]);

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <label className="block">
          <span className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Thema
          </span>
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="worüber berät das Team?"
            aria-label="Thema der Sitzung"
            className="w-full rounded-lg border px-2 py-1.5 text-[13px] outline-none"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          />
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Ziel
          </span>
          <input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="was soll am Ende feststehen?"
            aria-label="Ziel der Sitzung"
            className="w-full rounded-lg border px-2 py-1.5 text-[13px] outline-none"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          />
        </label>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 items-end">
        <label className="block">
          <span className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            endet bei
          </span>
          <select
            value={until}
            onChange={(e) => setUntil(e.target.value)}
            aria-label="Kriterium für den Abschluß"
            className="w-full rounded-lg border px-2 py-1.5 text-[13px] outline-none"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          >
            <option value="">— wählen —</option>
            {(criteria?.criteria ?? []).map((c) => (
              <option key={c.name} value={c.name}>
                {c.label || c.name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
            Deckel (Aufrufe)
          </span>
          <input
            type="number"
            min={1}
            max={1000}
            value={ceiling}
            onChange={(e) => setCeiling(Math.max(1, Number(e.target.value) || 1))}
            aria-label="Deckel in Aufrufen"
            className="w-full rounded-lg border px-2 py-1.5 text-[13px] outline-none"
            style={{
              background: 'var(--color-input-bg)',
              borderColor: 'var(--color-input-border)',
              color: 'var(--s-ink)',
            }}
          />
        </label>
        <button
          onClick={() => void start()}
          disabled={state.kind === 'pending' || !topic.trim() || !goal.trim() || !until}
          className="px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer disabled:opacity-50"
          style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
        >
          Sitzung eröffnen
        </button>
      </div>

      {criteria && (
        <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          {criteria.why_only_these} {criteria.the_ceiling_is_not_a_criterion}
        </p>
      )}

      {/* 🚨 The pickers, and the reason this component exists in one file: the
          first version of this screen fetched `GET /v1/models` and rendered
          nothing. The list was on the wire, the choice was not, and the screen
          let the owner start a session on a weight it had never shown them. The
          list now arrives at both screens through one component — the one the
          test for "der Motor nennt keine Modelle" found by failing. */}
      <VoiceModels
        list={models}
        picked={picked}
        onPick={(voice, model) => setPicked((old) => ({ ...old, [voice]: model }))}
      />

      {state.kind === 'pending' && <Pending label="das Team setzt sich" seconds={elapsed} />}
      {state.kind === 'denied' && (
        <DeniedView
          verdict={state.verdict}
          label={`Zurückgehalten — ${state.where}`}
          scope="das Thema wird abgelehnt, bevor eine einzige Stimme spricht. Für eine abgelehnte Sitzung wird keine Motorzeit verbraucht."
          direction={state.direction}
        />
      )}
      {state.kind === 'error' && <EngineDown why={state.message} />}
      {state.kind === 'done' && (
        <p className="text-[12px]" style={{ color: 'var(--s-ok)' }}>
          eröffnet als <span className="font-mono">{state.id}</span> — sie läuft als Prozeß, nicht
          als Anfrage. Ein Lauf ist ein Leben, keine Anfrage.
        </p>
      )}

      {openId && (
        <section className="space-y-2">
          <SessionDetailView id={openId} onChanged={() => setListNonce((n) => n + 1)} />
        </section>
      )}

      <SessionListView
        onOpen={setOpenId}
        openId={openId}
        reloadNonce={listNonce}
      />
    </div>
  );
}
