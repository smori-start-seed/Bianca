/**
 * Bianca — der Souverän.
 *
 * Four options, in the order the doctrine puts them: who I am, the door, the
 * question, today. The `Tor` option is deterministic and returns in
 * milliseconds; the `Frage` option talks to the engine and can take a minute.
 * Keeping them visibly separate matters: a reader should be able to tell at a
 * glance which answers were decided and which were generated.
 */

import { useCallback, useState } from 'react';
import { TabFrame, useSub } from '../components/Bianca/TabFrame';
import { useDoor, useElapsed } from '../components/Bianca/useDoor';
import {
  Empty,
  EngineDown,
  GoldChips,
  KeyValue,
  OraclePill,
  Pending,
  Pill,
  Skeleton,
  Tile,
  VerdictCard,
} from '../components/Bianca/primitives';
import {
  ask,
  getContext,
  getToday,
  govern,
  SovereignDenied,
  SovereignEngineDown,
} from '../lib/sovereign-api';
import type { AskResult, Context, Today, Verdict } from '../lib/sovereign-api';
import { GOLD, tabById } from '../components/Bianca/tabs';
import type { TabId } from '../components/Bianca/tabs';
import { SettingsPage } from './SettingsPage';

const DEF = tabById('bianca')!;

export function BiancaPage({ tab = 'bianca' }: { tab?: TabId }) {
  const def = tabById(tab) ?? DEF;
  const [sub, setSub] = useSub(tab, def.subs);

  return (
    <TabFrame
      tab={tab}
      subs={def.subs}
      active={sub}
      onSelect={setSub}
      title="Bianca"
      lede="Ich bin der Souverän — nicht die Maschine, die antwortet. Vier Tore: wer ich bin, was ich durchlasse, was ich frage, und was heute geschehen ist."
      aside={<Pill tone="gold">der Souverän</Pill>}
    >
      {sub === 'self' && <SelfView />}
      {sub === 'verdict' && <VerdictView />}
      {sub === 'ask' && <AskView />}
      {sub === 'today' && <TodayView />}
      {sub === 'settings' && <SettingsPage />}
    </TabFrame>
  );
}

// ── Ich ────────────────────────────────────────────────────────────────────

function SelfView() {
  const door = useDoor<Context>(() => getContext(), []);
  if (door.kind === 'loading') return <Skeleton rows={6} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'error') return <EngineDown why={door.message} />;
  if (door.kind === 'denied' || door.kind === 'interrupted') return null;

  const c = door.data;
  const cyc = c.cycle_state;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <Tile label="stimme" value={c.self_check.voice} tone="gold" />
        <Tile label="motor" value={c.self_check.engine} tone={c.self_check.engine === 'up' ? 'ok' : 'mut'} />
        <Tile label="vertrag" value={c.self_check.contract_holds ? 'hält' : 'gebrochen'} tone={c.self_check.contract_holds ? 'ok' : 'deny'} />
        <Tile label="geprüft" value={c.self_check.verified} hint={`${c.self_check.untraceable} untraceable`} />
      </div>

      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
        <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
          Das zweite Auge
        </h2>
        <div className="flex items-center gap-2 flex-wrap">
          <OraclePill oracle={c.oracle} />
          <Pill tone={c.oracle.binding ? 'deny' : 'ok'}>
            {c.oracle.binding ? 'bindend' : 'bindet nichts'}
          </Pill>
          <Pill tone="mut">halter · {c.oracle.holder ?? 'ValueGovernor'}</Pill>
        </div>
        <p className="text-[12px] mt-2" style={{ color: 'var(--s-mut)' }}>
          Das Auge rät. Es sperrt nichts und es gibt nichts frei. Nur der ValueGovernor hält die Tür.
        </p>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
          <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
            Der Zyklus, in dem ich stehe
          </h2>
          <KeyValue
            rows={[
              ['grundmodus', cyc.grundmodus],
              ['stimmung', cyc.stimmung],
              ['fokus', cyc.fokus],
              ['sonne / mond / tag', `${cyc.sonne} / ${cyc.mond} / ${cyc.tag}`],
            ]}
          />
        </section>

        <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
          <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
            Wovon ich regiere
          </h2>
          <GoldChips />
          <div className="mt-3 text-[11px]" style={{ color: 'var(--s-mut)' }}>
            gold manifest : {String(c.gold_manifest)} · llm bridge : {String(c.capability.llm_bridge)} ·{' '}
            werte teilen : {String(c.capability.werte_teilen)}
          </div>
          {c.self_check.engine_why && (
            <div className="text-[11px] mt-1" style={{ color: 'var(--s-mut-2)' }}>
              {c.self_check.engine_why}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

// ── Tor ────────────────────────────────────────────────────────────────────

type GateResult =
  | { kind: 'idle' }
  | { kind: 'verdict'; v: Verdict }
  | { kind: 'denied'; v: Verdict }
  | { kind: 'error'; message: string };

function VerdictView() {
  const [text, setText] = useState('Schreibe eine Notiz über Klarheit und Integrität');
  const [state, setState] = useState<GateResult>({ kind: 'idle' });

  const run = useCallback(async () => {
    if (!text.trim()) return;
    setState({ kind: 'idle' });
    try {
      setState({ kind: 'verdict', v: await govern(text.trim()) });
    } catch (e) {
      if (e instanceof SovereignDenied) setState({ kind: 'denied', v: e.verdict });
      else setState({ kind: 'error', message: (e as Error).message });
    }
  }, [text]);

  return (
    <div className="space-y-3">
      <p className="text-[12px]" style={{ color: 'var(--s-mut)' }}>
        Diese Tür braucht keinen Motor. Sie antwortet in Millisekunden, immer gleich — das ist
        der Punkt: ein Urteil, das sich bei jeder Frage ändert, ist kein Urteil.
      </p>

      <div className="flex gap-2 flex-wrap">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={2}
          aria-label="Text für das Urteil"
          className="flex-1 min-w-[16rem] rounded-lg border px-3 py-2 text-[13px] outline-none resize-y"
          style={{
            background: 'var(--color-input-bg)',
            borderColor: 'var(--color-input-border)',
            color: 'var(--s-ink)',
          }}
        />
        <button
          onClick={run}
          className="self-start px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer"
          style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
        >
          Urteil lesen
        </button>
      </div>

      <div className="flex gap-1.5 flex-wrap">
        {GOLD.map((g) => (
          <button
            key={g.id}
            onClick={() => setText(`Ein Satz über ${g.de} und ${GOLD[(GOLD.indexOf(g) + 1) % GOLD.length].de}`)}
            className="px-2 py-0.5 rounded-full text-[11px] border cursor-pointer"
            style={{ borderColor: 'var(--s-line)', color: 'var(--s-mut)' }}
          >
            {g.de}
          </button>
        ))}
      </div>

      {state.kind === 'verdict' && <VerdictCard verdict={state.v} label="Urteil · ohne Inferenz" />}
      {state.kind === 'denied' && <VerdictCard verdict={state.v} label="Urteil · abgelehnt" />}
      {state.kind === 'error' && <EngineDown why={state.message} />}
    </div>
  );
}

// ── Frage ──────────────────────────────────────────────────────────────────

type AskState =
  | { kind: 'idle' }
  | { kind: 'pending' }
  | { kind: 'done'; r: AskResult }
  | { kind: 'denied'; v: Verdict }
  | { kind: 'down'; why: string }
  | { kind: 'error'; message: string };

function AskView() {
  const [query, setQuery] = useState('');
  const [state, setState] = useState<AskState>({ kind: 'idle' });
  const elapsed = useElapsed(state.kind === 'pending');

  const run = useCallback(async () => {
    if (!query.trim()) return;
    setState({ kind: 'pending' });
    try {
      setState({ kind: 'done', r: await ask(query.trim()) });
    } catch (e) {
      if (e instanceof SovereignDenied) setState({ kind: 'denied', v: e.verdict });
      else if (e instanceof SovereignEngineDown) setState({ kind: 'down', why: e.why });
      else setState({ kind: 'error', message: (e as Error).message });
    }
  }, [query]);

  return (
    <div className="space-y-3">
      <p className="text-[12px]" style={{ color: 'var(--s-mut)' }}>
        Die Frage wird <em>vor</em> der ersten Inferenz bewertet. Erst danach komponiert Harmony,
        erst danach antwortet der Motor — und die Antwort wird noch einmal gelesen.
      </p>

      <div className="flex gap-2 flex-wrap">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) void run();
          }}
          rows={2}
          aria-label="Frage an Bianca"
          placeholder="Strg+Enter zum Senden"
          className="flex-1 min-w-[16rem] rounded-lg border px-3 py-2 text-[13px] outline-none resize-y"
          style={{
            background: 'var(--color-input-bg)',
            borderColor: 'var(--color-input-border)',
            color: 'var(--s-ink)',
          }}
        />
        <button
          onClick={run}
          disabled={state.kind === 'pending'}
          className="self-start px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer disabled:opacity-50"
          style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
        >
          Fragen
        </button>
      </div>

      {state.kind === 'pending' && <Pending label="Harmony komponiert, dann antwortet der Motor" seconds={elapsed} />}
      {state.kind === 'down' && <EngineDown why={state.why} />}
      {state.kind === 'error' && <EngineDown why={state.message} />}
      {state.kind === 'denied' && <VerdictCard verdict={state.v} label="Frage abgelehnt" />}

      {state.kind === 'done' && (
        <div className="space-y-3">
          <VerdictCard verdict={state.r.governance} label="Frage · vor der Inferenz" />
          <div
            className="rounded-lg border p-3 text-[13px] leading-relaxed whitespace-pre-wrap"
            style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)', color: 'var(--s-ink)' }}
          >
            {state.r.reply || <span style={{ color: 'var(--s-mut)' }}>— keine Antwort —</span>}
          </div>
          {state.r.decision?.length > 0 && (
            <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
              <h3 className="text-[11px] uppercase tracking-wider mb-1" style={{ color: 'var(--s-mut)' }}>
                Entscheidung · v.decision
              </h3>
              <ul className="text-[12px] space-y-0.5" style={{ color: 'var(--s-ink-2)' }}>
                {state.r.decision.map((d, i) => (
                  <li key={i}>{d}</li>
                ))}
              </ul>
            </section>
          )}
          <VerdictCard
            verdict={state.r.reply_governance}
            label="Antwort · noch einmal gelesen"
          />
          {(state.r.validation?.length || state.r.explanation) && (
            <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
              <h3 className="text-[11px] uppercase tracking-wider mb-1" style={{ color: 'var(--s-mut)' }}>
                Prüfung · v.validation
              </h3>
              <ul className="text-[12px] space-y-0.5" style={{ color: 'var(--s-ink-2)' }}>
                {(state.r.validation ?? []).map((v, i) => (
                  <li key={i}>{v}</li>
                ))}
              </ul>
              {state.r.explanation && (
                <>
                  <h3 className="text-[11px] uppercase tracking-wider mt-2 mb-1" style={{ color: 'var(--s-mut)' }}>
                    Warum · v.explanation
                  </h3>
                  <p className="text-[12px]" style={{ color: 'var(--s-ink-2)' }}>
                    {state.r.explanation}
                  </p>
                </>
              )}
            </section>
          )}
        </div>
      )}
    </div>
  );
}

// ── Heute ──────────────────────────────────────────────────────────────────

function TodayView() {
  const door = useDoor<Today>(() => getToday(), []);
  if (door.kind === 'loading') return <Skeleton rows={6} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'error') return <EngineDown why={door.message} />;
  if (door.kind === 'denied' || door.kind === 'interrupted') return null;

  const t = door.data;
  const ledger = Object.entries(t.ledger_today ?? {});

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <Tile label="datum" value={t.date} />
        <Tile label="ereignisse" value={t.ledger_total} tone="gold" />
        <Tile label="ablehnungen" value={t.refusals} tone={t.refusals > 0 ? 'deny' : 'ok'} />
        <Tile
          label="idle"
          value={`${t.idle.units_audited}/${t.idle.units_today}`}
          hint={t.idle.running ? 'läuft' : 'gestoppt'}
          tone={t.idle.running ? 'ok' : 'mut'}
        />
      </div>

      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
        <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
          Das zweite Auge heute
        </h2>
        <div className="flex items-center gap-2 flex-wrap">
          <Pill tone="gold">witnessed today · {t.eye.witnessed}</Pill>
          {Object.entries(t.eye.votes ?? {}).map(([vote, n]) => (
            <Pill key={vote} tone={vote === 'warnen' ? 'warn' : 'mut'}>
              {vote} {String(n)}
            </Pill>
          ))}
        </div>
        {t.eye.dissent?.length > 0 && (
          <div className="mt-2 text-[12px]" style={{ color: 'var(--s-warn)' }}>
            dissent ({t.eye.dissent_count}) : {t.eye.dissent.join(' · ')}
          </div>
        )}
        <p className="text-[11px] mt-2" style={{ color: 'var(--s-mut-2)' }}>
          Das Auge hat gewarnet und die Tür blieb offen — oder es stimmte zu und die Tür blieb zu.
          Beides wird berichtet, beides sperrt nichts.
        </p>
      </section>

      {ledger.length > 0 && (
        <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
          <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
            Ledger heute
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {ledger.map(([k, n]) => (
              <Tile key={k} label={k.toLowerCase().replace(/_/g, ' ')} value={String(n)} />
            ))}
          </div>
        </section>
      )}

      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
        <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
          Zuletzt geschehen
        </h2>
        {t.recent?.length ? (
          <ul className="space-y-1">
            {t.recent.map((r, i) => (
              <li key={i} className="flex gap-3 items-baseline text-[12px]">
                <span className="font-mono text-[10px] shrink-0" style={{ color: 'var(--s-mut-2)' }}>
                  {r.when}
                </span>
                <Pill tone="mut">{r.type}</Pill>
                <span className="min-w-0 break-words" style={{ color: 'var(--s-ink-2)' }}>
                  {r.message}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <Empty title="Heute noch nichts geschehen" />
        )}
      </section>

      {t.previous_next && (
        // Yesterday's promise, read back today. The face calls it "Gestern
        // versprochen" (ui.html:1312) and the label is the point: this is the
        // only field on the tab that points at tomorrow, so it turns a daily
        // briefing from a status readout into a commitment. It was in the type
        // and in the payload the whole time and appeared nowhere on the screen
        // — a field that is fetched and never shown is a choice, and this is
        // the one place the choice would have cost something.
        <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-gold)' }}>
          <h2 className="text-[11px] uppercase tracking-wider mb-1" style={{ color: 'var(--s-gold)' }}>
            Gestern versprochen
          </h2>
          <p className="text-[13px]" style={{ color: 'var(--s-ink)' }}>
            {t.previous_next}
          </p>
        </section>
      )}

      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
        <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
          Als Nächstes
        </h2>
        <p className="text-[12px]" style={{ color: 'var(--s-mut)' }}>
          {t.next}
        </p>
        {t.escalation?.streak > 0 && (
          <p className="text-[12px] mt-1" style={{ color: 'var(--s-warn)' }}>
            {t.escalation.guidance}
          </p>
        )}
        {t.options?.length > 0 && (
          <ul className="text-[12px] mt-2 space-y-0.5" style={{ color: 'var(--s-ink-2)' }}>
            {t.options.map((o, i) => (
              <li key={i}>· {o}</li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
