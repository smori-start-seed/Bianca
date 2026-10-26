/**
 * Jarvis chat — das Substrate.
 *
 * Two conversations, deliberately kept apart, because they are different
 * promises:
 *
 *   · Unterhaltung — the platform's own chat. Conversations, tools, agents,
 *     streaming. It answers whatever it is asked.
 *   · Bewerteter Dialog — the sovereign chat. EVERY user turn is judged before
 *     a single token is generated, and one refusal ends the exchange. It does
 *     not answer everything, and that is the feature.
 *
 * Putting them in one thread would mean a refusal appeared as a failed
 * message rather than as a door, and the reader would never learn which of
 * the two they were talking to. Two options, two promises, stated plainly.
 */

import { useCallback, useRef, useState } from 'react';
import { TabFrame, useSub } from '../components/Bianca/TabFrame';
import { useDoor, useElapsed } from '../components/Bianca/useDoor';
import {
  DeniedView,
  Empty,
  EngineDown,
  KeyValue,
  OraclePill,
  Pending,
  VerdictPill,
} from '../components/Bianca/primitives';
import {
  carrySnake,
  chat,
  getAgentTools,
  getShield,
  getSnake,
  runAgent,
  SovereignDenied,
  SovereignEngineDown,
} from '../lib/sovereign-api';
import type {
  AgentTools,
  ReplyRead,
  ShieldRefusal,
  ShieldGrown,
  ShieldState,
  SnakeCrossing,
  SnakeRefusal,
  SnakeState,
  ToolCheck,
  Verdict,
} from '../lib/sovereign-api';
import { tabById } from '../components/Bianca/tabs';
import type { TabId } from '../components/Bianca/tabs';
import { ChatPage } from './ChatPage';

const DEF = tabById('jarvis')!;
const HISTORY_KEY = 'bianca.sovereign.chat';
const MAX_STORED = 40;

interface Line {
  role: 'user' | 'assistant';
  content: string;
  governance?: Verdict;
  replyGovernance?: ReplyRead;
  /** What the composer checked before writing, and why it chose that shape. */
  validation?: string[] | null;
  explanation?: string | null;
  /** 503 — the motor did not answer. Rendered as a fact, never as a reply. */
  down?: string;
  refused?: boolean;
}

export function JarvisPage({ tab = 'jarvis' }: { tab?: TabId }) {
  const def = tabById(tab) ?? DEF;
  const [sub, setSub] = useSub(tab, def.subs);

  if (sub === 'platform') {
    // The platform chat owns the whole viewport — its own scroll, its own
    // composer, its own side panel — so the frame runs in `host` mode: the
    // option strip stays (otherwise this tab's other option would be
    // unreachable from here) and the frame steps aside.
    return (
      <TabFrame
        tab={tab}
        subs={def.subs}
        active={sub}
        onSelect={setSub}
        title="Jarvis chat"
        variant="host"
      >
        <ChatPage />
      </TabFrame>
    );
  }

  if (sub === 'hand') {
    return (
      <TabFrame
        tab={tab}
        subs={def.subs}
        active={sub}
        onSelect={setSub}
        title="Hand"
        lede="Die Schlange, der Schild und das Schwert. Der Agent darf Werkzeuge rufen — aber jedes einzelne geht zuerst am ValueGovernor vorbei, und jede Verweigerung nennt den Begriff, der sie ausgelöst hat und was der Anfrage fehlt."
        aside={<span className="text-[11px]" style={{ color: 'var(--s-mut)' }}>POST /v1/agent</span>}
      >
        <div className="space-y-4">
          <AgentSnake />
          <AgentShield />
          <AgentHand />
        </div>
      </TabFrame>
    );
  }

  return (
    <TabFrame
      tab={tab}
      subs={def.subs}
      active={sub}
      onSelect={setSub}
      title="Jarvis chat"
      lede="Zwei Unterhaltungen, zwei Versprechen. Die eine antwortet, was du fragst. Die andere antwortet nur, was die Tür zulässt — und sagt dir, wenn sie das nicht tut."
      aside={
        <span className="text-[11px]" style={{ color: 'var(--s-mut)' }}>
          <span style={{ color: 'var(--s-gold)' }}>Unterhaltung</span> antwortet ·{' '}
          <span style={{ color: 'var(--s-gold)' }}>Bewerteter Dialog</span> prüft
        </span>
      }
    >
      <SovereignChat />
    </TabFrame>
  );
}

// ── the governed dialogue ──────────────────────────────────────────────────

type SendState = { kind: 'idle' } | { kind: 'pending' };

function SovereignChat() {
  const [lines, setLines] = useState<Line[]>(() => load());
  const [text, setText] = useState('');
  const [state, setState] = useState<SendState>({ kind: 'idle' });
  const elapsed = useElapsed(state.kind === 'pending');
  const logRef = useRef<HTMLDivElement>(null);

  const push = useCallback((next: Line[]) => {
    setLines(next);
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(next.slice(-MAX_STORED)));
    } catch {
      /* a full quota must not cost the conversation on screen */
    }
  }, []);

  const send = useCallback(async () => {
    const q = text.trim();
    if (!q || state.kind === 'pending') return;

    const history: Line[] = [...lines, { role: 'user', content: q }];
    setText('');
    setState({ kind: 'pending' });
    // The user's own turn is on screen immediately. Waiting for the verdict to
    // render it would make a fast refusal feel like a lost message.
    push(history);

    try {
      const r = await chat(history.map((m) => ({ role: m.role, content: m.content })));
      push([
        ...history,
        {
          role: 'assistant',
          content: r.reply,
          governance: r.governance,
          replyGovernance: r.reply_governance,
          // What the composer checked, and why it chose this shape. The face
          // shows these above every reply (ui.html:1598-1601) and the React
          // surface did not — so a row labelled "reply read" asserted a
          // review while showing none of it. A reply read with nothing read
          // is the worst version of that failure: it teaches the reader to
          // trust a label instead of a record.
          validation: r.validation ?? null,
          explanation: r.explanation ?? null,
        },
      ]);
    } catch (e) {
      if (e instanceof SovereignDenied) {
        push([
          ...history,
          {
            role: 'assistant',
            content: e.messageText,
            governance: e.verdict,
            refused: true,
          },
        ]);
      } else if (e instanceof SovereignEngineDown) {
        push([...history, { role: 'assistant', content: '', down: e.why }]);
      } else {
        push([
          ...history,
          { role: 'assistant', content: '', down: (e as Error).message },
        ]);
      }
    } finally {
      setState({ kind: 'idle' });
    }
  }, [text, state.kind, lines, push]);

  return (
    <div className="flex flex-col gap-3" style={{ minHeight: '18rem' }}>
      <div
        ref={logRef}
        className="flex flex-col gap-3 overflow-y-auto pr-1"
        style={{ maxHeight: '52vh' }}
        aria-live="polite"
      >
        {lines.length === 0 && (
          <div className="text-[12px] text-center py-8" style={{ color: 'var(--s-mut)' }}>
            <p>Noch kein Dialog.</p>
            <p className="mt-1" style={{ color: 'var(--s-mut-2)' }}>
              Jeder Zug wird zuerst bewertet. Ein verweigerter Zug beendet den Dialog — er wird
              nicht höflich umgangen.
            </p>
          </div>
        )}

        {lines.map((m, i) =>
          m.role === 'user' ? (
            <div key={i} className="flex justify-end">
              <div
                className="max-w-[80%] rounded-lg rounded-br-sm px-3 py-2 text-[13px] whitespace-pre-wrap"
                style={{
                  background: 'color-mix(in srgb, var(--s-gold) 16%, transparent)',
                  border: '1px solid color-mix(in srgb, var(--s-gold) 30%, transparent)',
                  color: 'var(--s-ink)',
                }}
              >
                {m.content}
              </div>
            </div>
          ) : (
            <div key={i} className="flex flex-col gap-1.5 max-w-[92%]">
              {m.down !== undefined ? (
                <EngineDown why={m.down} />
              ) : (
                <div
                  className="rounded-lg rounded-bl-sm px-3 py-2 text-[13px] leading-relaxed whitespace-pre-wrap"
                  style={{
                    background: m.refused
                      ? 'color-mix(in srgb, var(--s-deny) 8%, transparent)'
                      : 'var(--s-surface-2)',
                    border: `1px solid ${
                      m.refused
                        ? 'color-mix(in srgb, var(--s-deny) 42%, transparent)'
                        : 'var(--s-line)'
                    }`,
                    color: m.refused ? 'var(--s-deny)' : 'var(--s-ink)',
                  }}
                >
                  {m.refused ? <strong>no means no</strong> : null}
                  {m.refused ? ' — ' : ''}
                  {m.content}
                </div>
              )}

              {m.governance && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                    zug
                  </span>
                  <VerdictPill verdict={m.governance.verdict} />
                  <OraclePill oracle={m.governance.oracle} />
                  {m.governance.risk_hits.length > 0 && (
                    <span className="text-[10px]" style={{ color: 'var(--s-deny)' }}>
                      risk : {m.governance.risk_hits.join(', ')}
                    </span>
                  )}
                </div>
              )}

              {m.refused && m.governance && (
                // Two facts the face states and this surface did not.
                //
                // `gold src` — the provenance of the values that produced the
                // refusal. A denial that hides where its judgement came from
                // is not checkable, and every other verdict in this app shows
                // it.
                //
                // `recorded, not censored` — the door journals a DENIED event
                // for the refused turn, so the turn WAS written down. Saying
                // so is the difference between "the governor considered it"
                // and "the governor never saw it"; without the stamp the two
                // surfaces disagree about what happened to a refused message.
                <div className="flex items-center gap-2 flex-wrap text-[10px]" style={{ color: 'var(--s-mut-2)' }}>
                  <span className="font-mono">gold src : {m.governance.gold_source || '—'}</span>
                  <span
                    className="px-1.5 py-0.5 rounded-full border"
                    style={{ borderColor: 'var(--s-line)', color: 'var(--s-mut)' }}
                    title="Die abgelehnte Äußerung wurde ins Ledger geschrieben, nicht verworfen."
                  >
                    recorded, not censored
                  </span>
                </div>
              )}

              {m.replyGovernance && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                    reply read
                  </span>
                  <VerdictPill verdict={m.replyGovernance.verdict} />
                  <OraclePill oracle={m.replyGovernance.oracle} />
                  {m.replyGovernance.risk_hits.length > 0 && (
                    <span className="text-[10px]" style={{ color: 'var(--s-deny)' }}>
                      risk : {m.replyGovernance.risk_hits.join(', ')}
                    </span>
                  )}
                </div>
              )}

              {(m.validation?.length || m.explanation) && (
                // The evidence for the "reply read" label above. The node sends
                // exactly these two fields and the face prints them on every
                // reply; without them this row is a claim, not a record.
                <div
                  className="rounded border-l-2 pl-2 py-1 text-[11px] space-y-0.5"
                  style={{ borderColor: 'var(--s-line-2)', color: 'var(--s-mut)' }}
                >
                  {!!m.validation?.length && (
                    <div>
                      <span className="uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                        prüfen
                      </span>{' '}
                      {m.validation.join(' ')}
                    </div>
                  )}
                  {m.explanation && (
                    <div>
                      <span className="uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                        warum
                      </span>{' '}
                      {m.explanation}
                    </div>
                  )}
                </div>
              )}
            </div>
          ),
        )}

        {state.kind === 'pending' && (
          <div
            className="rounded-lg rounded-bl-sm px-3 py-2 text-[13px] flex items-center gap-2"
            style={{ background: 'var(--s-surface-2)', border: '1px solid var(--s-line)', color: 'var(--s-mut)' }}
          >
            <span className="inline-block w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: 'var(--s-gold)' }} />
            denkt · <span className="tabular-nums font-mono">{elapsed}s</span>
            <span className="text-[11px]">· lokal</span>
          </div>
        )}
      </div>

      <div className="flex gap-2 items-end">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          rows={2}
          aria-label="Nachricht an Jarvis"
          placeholder="Enter sendet · Shift+Enter bricht um"
          className="flex-1 rounded-lg border px-3 py-2 text-[13px] outline-none resize-y"
          style={{
            background: 'var(--color-input-bg)',
            borderColor: 'var(--color-input-border)',
            color: 'var(--s-ink)',
          }}
        />
        <button
          onClick={send}
          disabled={state.kind === 'pending' || !text.trim()}
          className="px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer disabled:opacity-50"
          style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
        >
          Senden
        </button>
      </div>

      {lines.length > 0 && (
        <button
          onClick={() => push([])}
          className="self-start text-[11px] cursor-pointer"
          style={{ color: 'var(--s-mut-2)' }}
        >
          Dialog verwerfen
        </button>
      )}
    </div>
  );
}

function load(): Line[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as Line[]) : [];
  } catch {
    return [];
  }
}

// ── the Hand: the governed tool-agent ───────────────────────────────────────

/**
 * One tool judgement, drawn as the verdict it is.
 *
 * A refused tool call is a refusal, so it shows the stem that tripped it and
 * the eye that witnessed it — exactly like every other denial in this app. The
 * Python side used to keep only `{verdict, allowed}`, which could render
 * "denied" with nothing to check; the shape was fixed there first so this row
 * could not reintroduce it.
 */
function ToolCheckRow({ check }: { check: ToolCheck }) {
  const v = check.verdict;
  const refused = v.verdict === 'zurueckhalten';
  return (
    <div
      className="rounded px-2.5 py-2 text-[12px]"
      style={{
        background: refused ? 'color-mix(in srgb, var(--s-deny) 7%, transparent)' : 'var(--s-surface-2)',
        border: `1px solid ${
          refused ? 'color-mix(in srgb, var(--s-deny) 38%, transparent)' : 'var(--s-line)'
        }`,
      }}
    >
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="font-mono text-[11px]" style={{ color: 'var(--s-ink)' }}>
          {refused ? '⛔' : '✓'} {check.tool}
        </span>
        <VerdictPill verdict={v.verdict} />
        <OraclePill oracle={v.oracle} />
      </div>
      <div className="mt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
        blockierte Begriffe: {v.risk_hits.length ? v.risk_hits.join(', ') : '—'} · gold src :{' '}
        {v.gold_source || '—'}
      </div>
    </div>
  );
}

/**
 * Der Schild — where a withheld action lands.
 *
 * The owner's principle: a shield as a hard barrier does not hold long, it
 * crumbles; a shield deflects and answers clearly what the request is missing.
 * So every row here carries the verdict, the stems that tripped it, the gap, the
 * gold source and the second eye — and the gap on a refusal says that naming the
 * gold values would NOT have released it, because the held stem is judged first.
 * That is the boundary, not a hint.
 */
/**
 * Die Schlange — the one seam where the inner world reaches the mycelium.
 *
 * Two callers, one writer: the cycle and the shield. What does **not** cross is
 * the point, and it is stated on the card rather than left to be inferred — a
 * reader who cannot see the withheld half cannot tell a shield from a wall.
 *
 * A refusal crossing carries `held_count` and never `risk_hits`, because a stem
 * is itself a RISK_TERM and the net's only door refuses words the governor
 * holds. A count is not an attack; a name is.
 */
function AgentSnake() {
  const snake = useDoor<SnakeState>(getSnake, []);
  const [carried, setCarried] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const take = useCallback(async () => {
    setBusy(true);
    try {
      const r = await carrySnake();
      setCarried(r.carried);
    } catch {
      setCarried(null);
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
      <h3 className="text-[13px] font-medium mb-1" style={{ color: 'var(--s-ink)' }}>
        Die Schlange
      </h3>
      <p className="text-[11px] mb-3" style={{ color: 'var(--s-mut)' }}>
        Die einzige Naht ins Myzellumnetz. Zwei Schreiber, eine Tür — der Zyklus und der Schild.
        Was nicht übergeht, steht unten: ein Schild, der annimmt, trägt nichts.
      </p>

      {snake.kind === 'ready' && (
        <>
          {snake.data.crossings.length === 0 ? (
            <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
              nichts getragen
            </p>
          ) : (
            <div className="space-y-1.5">
              {snake.data.crossings.map((c) => (
                <SnakeRow key={c.stamp} crossing={c} />
              ))}
            </div>
          )}
          <div className="pt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            getragen: {snake.data.carried} · Verweigerungen: {snake.data.refusals_carried} · Zyklen:{' '}
            {snake.data.cycles_carried}
            {carried !== null ? ` · soeben getragen: ${carried}` : ''}
          </div>
          <div className="mt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            nicht getragen: {snake.data.not_carried}
          </div>
          <div className="mt-0.5 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            Wächte: {snake.data.guard}
          </div>
        </>
      )}
      {snake.kind === 'loading' && <Pending label="Die Schlange zieht" seconds={0} />}
      {snake.kind === 'denied' && (
        <DeniedView verdict={snake.verdict} scope="Der Spiegel des Netzes wurde verweigert." />
      )}
      {snake.kind === 'down' && <EngineDown why={snake.why} />}
      {snake.kind === 'error' && <Empty title="Netz unbekannt">{snake.message}</Empty>}
      {snake.kind === 'interrupted' && <Empty title="Unvollständig">Der Spiegel kam nicht ganz an.</Empty>}

      <button
        type="button"
        className="mt-2 w-full rounded px-3 py-1.5 text-[12px] disabled:opacity-50"
        style={{ background: 'var(--s-line)', color: 'var(--s-ink)' }}
        onClick={() => void take()}
        disabled={busy}
      >
        {busy ? 'trägt…' : 'ins Netz tragen'}
      </button>
      <p className="mt-1 text-[10px]" style={{ color: 'var(--s-mut-2)' }}>
        Tragen ist ein Handgriff, kein Nebenweg: nichts verlässt diesen Knoten, ohne dass hier etwas
        gedrückt wurde.
      </p>
    </section>
  );
}

function SnakeRow({ crossing }: { crossing: SnakeCrossing }) {
  const c = crossing.carried;
  if (!c) {
    // Said rather than drawn blank: a spore this node did not write is a
    // real thing the net holds, and an empty row would read as an oversight.
    return (
      <div className="rounded px-2.5 py-2 text-[11px]" style={{ border: '1px solid var(--s-line)' }}>
        <span className="font-mono" style={{ color: 'var(--s-mut-2)' }}>
          · {crossing.stamp}
        </span>{' '}
        <span style={{ color: 'var(--s-mut)' }}>
          Fremdspore — nicht von der Schlange getragen
        </span>
      </div>
    );
  }
  const refusal = c as SnakeRefusal;
  return (
    <div className="rounded px-2.5 py-2 text-[12px]" style={{ border: '1px solid var(--s-line)' }}>
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="font-mono text-[11px]" style={{ color: 'var(--s-ink)' }}>
          🐍 {crossing.stamp}
        </span>
        {c.kind === 'refusal' ? (
          <>
            <VerdictPill verdict={refusal.verdict} />
            <OraclePill oracle={refusal.eye} />
          </>
        ) : null}
      </div>
      <div className="mt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
        {c.kind === 'refusal'
          ? `Verweigerung · ${refusal.seam} · ${refusal.held_count} Stamm/Stämme · gold src : ${
              refusal.gold_source || '—'
            }`
          : `Zyklus · ${c.grundmodus} / ${c.stimmung} / ${c.fokus}`}
      </div>
      {c.kind === 'refusal' && refusal.missing.length > 0 && (
        <div className="mt-1 text-[11px]" style={{ color: 'var(--s-mut)' }}>
          es fehlt : {refusal.missing.join(' · ')}
        </div>
      )}
    </div>
  );
}

function GrownRow({ grown }: { grown: ShieldGrown }) {
  return (
    <div
      className="rounded px-2.5 py-2 text-[12px]"
      style={{
        background: 'color-mix(in srgb, var(--s-ok) 7%, transparent)',
        border: '1px solid color-mix(in srgb, var(--s-ok) 38%, transparent)',
      }}
    >
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="font-mono text-[11px]" style={{ color: 'var(--s-ink)' }}>
          🌱 {grown.where}
        </span>
        <VerdictPill verdict={grown.verdict} />
        <OraclePill oracle={grown.eye} />
      </div>
      <div className="mt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
        getragen: {grown.gold_hits.length ? grown.gold_hits.join(', ') : '—'} · gold src :{' '}
        {grown.gold_source || '—'}
        {grown.uracil && (
          <>
            {' · '}
            Urasil:{' '}
            {[grown.uracil.grundmodus, grown.uracil.stimmung, grown.uracil.fokus]
              .filter(Boolean)
              .join(' / ') || '—'}
          </>
        )}
      </div>
      {grown.request && (
        <div className="mt-0.5 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
          Anfrage: {grown.request}
        </div>
      )}
    </div>
  );
}

function AgentShield() {
  const shield = useDoor<ShieldState>(getShield, []);
  return (
    <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
      <h3 className="text-[13px] font-medium mb-1" style={{ color: 'var(--s-ink)' }}>
        Der Schild
      </h3>
      <p className="text-[11px] mb-3" style={{ color: 'var(--s-mut)' }}>
        Wo eine aufgehaltene Hand landet — und, gleich darunter, was gewachsen ist. Kein
        Wall: jede Verweigerung nennt, was der Anfrage fehlt.
      </p>

      {shield.kind === 'ready' && (
        <div className="space-y-3">
          <div className="space-y-1.5">
            {(shield.data.refusals ?? []).length === 0 ? (
              <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
                Heute wurde nichts aufgehalten.
              </p>
            ) : (
              <>
                {(shield.data.refusals ?? []).map((r, i) => (
                  <ShieldRow key={`${r.at}-${i}`} refusal={r} />
                ))}
                <div
                  className="pt-1 text-[10px] font-mono"
                  style={{ color: 'var(--s-mut-2)' }}
                >
                  heute aufgehalten: {shield.data.refusals_today ?? 0} · Stämme:{' '}
                  {Object.entries(shield.data.held_stems ?? {})
                    .map(([k, n]) => `${k} ×${n}`)
                    .join(', ') || '—'}{' '}
                  · nicht gemerkt: {shield.data.not_remembered || ''}
                </div>
              </>
            )}
          </div>

          {/* Set 28: the other half, in the SAME view. A mirror showing only
              refusals is a wall with a reflection of itself. */}
          <div className="space-y-1.5">
            <div
              className="text-[10px] uppercase tracking-wide font-mono"
              style={{ color: 'var(--s-mut-2)' }}
            >
              was gewachsen ist
            </div>
            {/*
              Read defensively at the boundary, exactly as the face does
              (`d.grown || []`). A mirror that crashes on a partial payload is a
              mirror that hides — and the node on the other end can be an older
              build, or absent. This was not theoretical: the snake tests stub
              the door and eleven of them went down on a missing field the
              moment the other half arrived.
            */}
            {(shield.data.grown ?? []).length === 0 ? (
              <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
                Heute wurde nichts beantwortet.
              </p>
            ) : (
              <>
                {(shield.data.grown ?? []).map((g, i) => (
                  <GrownRow key={`${g.at}-${i}`} grown={g} />
                ))}
                <div
                  className="pt-1 text-[10px] font-mono"
                  style={{ color: 'var(--s-mut-2)' }}
                >
                  heute beantwortet: {shield.data.grown_today ?? 0}
                  {Object.keys(shield.data.grown_gold ?? {}).length > 0 && (
                    <>
                      {' · getragen: '}
                      {Object.entries(shield.data.grown_gold ?? {})
                        .map(([k, n]) => `${k} ×${n}`)
                        .join(', ')}
                    </>
                  )}{' '}
                  · was der Spiegel <b>nicht</b> weiß:{' '}
                  {shield.data.grown_cannot_record || ''}
                </div>
              </>
            )}
          </div>
        </div>
      )}
      {shield.kind === 'loading' && <Pending label="Der Schild öffnet sich" seconds={0} />}
      {shield.kind === 'denied' && (
        <DeniedView verdict={shield.verdict} scope="Der Spiegel wurde verweigert." />
      )}
      {shield.kind === 'down' && <EngineDown why={shield.why} />}
      {shield.kind === 'error' && <Empty title="Schild unbekannt">{shield.message}</Empty>}
      {shield.kind === 'interrupted' && <Empty title="Unvollständig">Der Spiegel kam nicht ganz an.</Empty>}
    </section>
  );
}

function ShieldRow({ refusal }: { refusal: ShieldRefusal }) {
  return (
    <div
      className="rounded px-2.5 py-2 text-[12px]"
      style={{
        background: 'color-mix(in srgb, var(--s-deny) 7%, transparent)',
        border: '1px solid color-mix(in srgb, var(--s-deny) 38%, transparent)',
      }}
    >
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="font-mono text-[11px]" style={{ color: 'var(--s-ink)' }}>
          ✋ {refusal.where}
        </span>
        <VerdictPill verdict={refusal.verdict} />
        <OraclePill oracle={refusal.eye} />
      </div>
      <div className="mt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
        blockierte Begriffe: {refusal.risk_hits.length ? refusal.risk_hits.join(', ') : '—'} · gold src :{' '}
        {refusal.gold_source || '—'}
        {refusal.request ? ` · Anfrage: ${refusal.request}` : ''}
      </div>
      {refusal.missing.length > 0 && (
        <div className="mt-1 text-[11px]" style={{ color: 'var(--s-mut)' }}>
          es fehlt : {refusal.missing.join(' · ')}
        </div>
      )}
    </div>
  );
}

function AgentHand() {
  const tools = useDoor<AgentTools>(getAgentTools, []);
  const [text, setText] = useState('');
  const [run, setRun] = useState<
    | { kind: 'idle' }
    | { kind: 'pending' }
    | { kind: 'done'; content: string; governance: Verdict; reply: ReplyRead; calls: ToolCheck[]; denied: ToolCheck[]; turns: number }
    | { kind: 'denied'; verdict: Verdict; message: string }
    | { kind: 'down'; why: string }
  >({ kind: 'idle' });
  const elapsed = useElapsed(run.kind === 'pending');

  const go = useCallback(async () => {
    const q = text.trim();
    if (!q || run.kind === 'pending') return;
    setText('');
    setRun({ kind: 'pending' });
    try {
      const r = await runAgent(q);
      setRun({
        kind: 'done',
        content: r.content,
        governance: r.governance,
        reply: r.reply_governance,
        calls: r.tool_calls,
        denied: r.denied,
        turns: r.turns,
      });
    } catch (e) {
      if (e instanceof SovereignDenied) {
        setRun({ kind: 'denied', verdict: e.verdict, message: e.messageText });
      } else if (e instanceof SovereignEngineDown) {
        setRun({ kind: 'down', why: e.why });
      } else {
        setRun({ kind: 'down', why: (e as Error).message });
      }
    }
  }, [text, run.kind]);

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {/* the sword — visible, because a tool you cannot see is not on hand */}
      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
        <h3 className="text-[13px] font-medium mb-1" style={{ color: 'var(--s-ink)' }}>
          Das Schwert
        </h3>
        <p className="text-[11px] mb-3" style={{ color: 'var(--s-mut)' }}>
          Was der Agent rufen darf. Jeder Aufruf geht zuerst am ValueGovernor vorbei.
        </p>

        {tools.kind === 'ready' && (
          <div className="space-y-1.5">
            {tools.data.tools.map((t) => (
              <div
                key={t.name}
                className="rounded px-2.5 py-2 text-[12px]"
                style={{ background: 'var(--s-surface-2)', border: '1px solid var(--s-line)' }}
              >
                <div className="flex items-baseline gap-2">
                  <span className="font-mono text-[11px]" style={{ color: 'var(--s-gold)' }}>
                    {t.name}
                  </span>
                  <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                    {t.category}
                  </span>
                </div>
                <p className="mt-0.5" style={{ color: 'var(--s-mut)' }}>
                  {t.description}
                </p>
              </div>
            ))}
            <div className="pt-1 text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
              <KeyValue
                rows={[
                  ['naht', tools.data.governance.seam],
                  ['fail-closed', tools.data.governance.fail_closed ? 'ja' : 'nein'],
                  ['verweigert nur', tools.data.governance.denies],
                  ['zweites auge', tools.data.governance.second_eye],
                  ['die tür hält', tools.data.governance.holder],
                ]}
              />
            </div>
          </div>
        )}
        {tools.kind === 'loading' && <Pending label="Werkzeuge werden gelistet" seconds={0} />}
        {tools.kind === 'denied' && (
          <DeniedView verdict={tools.verdict} scope="Die Werkzeugliste wurde verweigert." />
        )}
        {tools.kind === 'down' && <EngineDown why={tools.why} />}
        {tools.kind === 'error' && <Empty title="Werkzeuge unbekannt">{tools.message}</Empty>}
        {tools.kind === 'interrupted' && <Empty title="Unvollständig">Die Liste kam nicht ganz an.</Empty>}
      </section>

      {/* the run */}
      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
        <h3 className="text-[13px] font-medium mb-1" style={{ color: 'var(--s-ink)' }}>
          Lauf
        </h3>
        <p className="text-[11px] mb-3" style={{ color: 'var(--s-mut)' }}>
          Was soll die Hand tun?
        </p>

        <textarea
          className="w-full rounded px-2.5 py-2 text-[13px] resize-y"
          style={{
            background: 'var(--s-surface-2)',
            border: '1px solid var(--s-line)',
            color: 'var(--s-ink)',
            minHeight: '4.5rem',
          }}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') void go();
          }}
          placeholder="Auftrag an die Hand"
          aria-label="Auftrag an die Hand"
        />
        <div className="mt-2 flex items-center gap-2">
          <button
            type="button"
            className="rounded px-3 py-1.5 text-[12px] disabled:opacity-50"
            style={{ background: 'var(--s-gold)', color: 'var(--s-bg)' }}
            onClick={() => void go()}
            disabled={run.kind === 'pending' || !text.trim()}
          >
            Ausführen
          </button>
          <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
            ⌘/Ctrl + Enter
          </span>
        </div>

        <div className="mt-3" aria-live="polite">
          {run.kind === 'pending' && (
            <Pending label="die Hand reicht aus — jedes Werkzeug wird zuerst gelesen" seconds={elapsed} />
          )}

          {run.kind === 'done' && (
            <div className="space-y-2.5">
              <div
                className="rounded px-3 py-2 text-[13px] leading-relaxed whitespace-pre-wrap"
                style={{ background: 'var(--s-surface-2)', border: '1px solid var(--s-line)', color: 'var(--s-ink)' }}
              >
                {run.content}
              </div>
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                  auftrag
                </span>
                <VerdictPill verdict={run.governance.verdict} />
                <OraclePill oracle={run.governance.oracle} />
              </div>
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                  reply read
                </span>
                <VerdictPill verdict={run.reply.verdict} />
                <OraclePill oracle={run.reply.oracle} />
              </div>
              <div className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
                {run.turns} Züge · {run.calls.length} Werkzeugrufe · {run.denied.length} verweigert
              </div>
              {run.calls.length > 0 ? (
                <div className="space-y-1.5">
                  <div className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
                    jedes werkzeug wurde einzeln gelesen
                  </div>
                  {run.calls.map((c, i) => (
                    <ToolCheckRow key={`${c.tool}-${i}`} check={c} />
                  ))}
                </div>
              ) : (
                <p className="text-[11px]" style={{ color: 'var(--s-mut)' }}>
                  Die Hand hat kein Werkzeug gerufen — die Antwort kam aus dem Kopf, nicht aus der Hand.
                </p>
              )}
              <div className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
                gold src : {run.governance.gold_source || '—'}
              </div>
            </div>
          )}

          {run.kind === 'denied' && (
            // The refusal keeps the whole verdict, so the stem that tripped it
            // is on screen — the same rule every other denial follows.
            <DeniedView
              verdict={run.verdict}
              scope={`${run.message} Kein Werkzeug wurde gerufen: die Anfrage wurde vor der ersten Inferenz verweigert.`}
            />
          )}

          {run.kind === 'down' && <EngineDown why={run.why} />}
        </div>
      </section>
    </div>
  );
}
