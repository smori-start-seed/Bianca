/**
 * Node & Net — der Knoten und das Myzel.
 *
 * The node's own body: is it alive, does its contract still hold, what has it
 * done today, and what has it published. The platform's own pages (sources,
 * ledger, telemetry, first steps) live under this tab because they are all
 * questions about the substrate — they were not deleted to make the bar
 * tidy, they were given a home whose character matches them.
 */

import { useCallback, useState } from 'react';
import type { ReactNode } from 'react';
import { TabFrame, useSub } from '../components/Bianca/TabFrame';
import { useDoor, useElapsed } from '../components/Bianca/useDoor';
import type { Door } from '../components/Bianca/useDoor';
import {
  DeniedView,
  Empty,
  EngineDown,
  KeyValue,
  Pill,
  Pending,
  Skeleton,
  Tile,
  VerdictCard,
  VerdictPill,
  OraclePill,
} from '../components/Bianca/primitives';
import {
  getHealth,
  getIdle,
  getManifest,
  getSpores,
  postSpore,
  SovereignDenied,
  SovereignEngineDown,
} from '../lib/sovereign-api';
import type { Health, IdleStatus, Manifest, Spore, Verdict } from '../lib/sovereign-api';
import { GOLD, tabById } from '../components/Bianca/tabs';
import type { TabId } from '../components/Bianca/tabs';
import { LogsPage } from './LogsPage';
import { DataSourcesPage } from './DataSourcesPage';
import { DashboardPage } from './DashboardPage';
import { GetStartedPage } from './GetStartedPage';

const DEF = tabById('node')!;

export function NodeNetPage({ tab = 'node' }: { tab?: TabId }) {
  const def = tabById(tab) ?? DEF;
  const [sub, setSub] = useSub(tab, def.subs);

  return (
    <TabFrame
      tab={tab}
      subs={def.subs}
      active={sub}
      onSelect={setSub}
      title="Node & Net"
      lede="Lebenszeichen, Vertrag, Ledger und die öffentliche Fläche des Knotens. Geprüft wird hier nichts neu erfunden — alles kommt aus den Türen, die der Knoten selbst schreibt."
      aside={<Pill tone="gold">der Knoten</Pill>}
    >
      {sub === 'pulse' && <PulseView />}
      {sub === 'netz' && <NetzView />}
      {sub === 'sources' && <Bare><DataSourcesPage /></Bare>}
      {sub === 'ledger' && <Bare><LogsPage /></Bare>}
      {sub === 'telemetry' && <Bare><DashboardPage /></Bare>}
      {sub === 'start' && <Bare><GetStartedPage /></Bare>}
    </TabFrame>
  );
}

/**
 * The platform pages ship their own page chrome (their own max-width, their
 * own scroll). Nesting that inside the tab panel would put two paddings and
 * two scrollbars on one screen, so the frame steps aside for them rather than
 * fighting them.
 */
function Bare({ children }: { children: ReactNode }) {
  return <div className="-m-4">{children}</div>;
}

// ── Puls ───────────────────────────────────────────────────────────────────

function PulseView() {
  const health = useDoor<Health>(() => getHealth(), []);
  const idle = useDoor<IdleStatus>(() => getIdle(), []);

  return (
    <div className="space-y-4">
      {health.kind === 'ready' ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <Tile
              label="zustand"
              value={health.data.ok ? 'lebendig' : 'gestört'}
              tone={health.data.ok ? 'ok' : 'deny'}
            />
            <Tile label="name" value={health.data.name} />
            <Tile label="version" value={health.data.version} />
            <Tile
              label="gold"
              value={health.data.gold_loaded ? 'geladen' : 'fehlt'}
              tone={health.data.gold_loaded ? 'ok' : 'deny'}
            />
          </div>
          <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
            <KeyValue
              rows={[
                ['seele', health.data.soul],
                ['zyklus', `${health.data.cycle.grundmodus} / ${health.data.cycle.stimmung} / ${health.data.cycle.fokus}`],
              ]}
            />
          </section>
        </>
      ) : health.kind === 'down' ? (
        <EngineDown why={health.why} />
      ) : health.kind === 'loading' ? (
        <Skeleton rows={2} />
      ) : (
        <EngineDown why={(health as { message?: string }).message ?? 'unbekannt'} />
      )}

      {idle.kind === 'ready' ? (
        <section
          className="rounded-lg border p-3"
          data-panel="idle"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
        >
          <div className="flex items-center gap-2 mb-2">
            <h2 className="text-[13px] font-medium" style={{ color: 'var(--s-ink)' }}>
              Idle-Vertrag
            </h2>
            <Pill tone={idle.data.running ? 'ok' : 'mut'}>
              {idle.data.running ? 'läuft' : 'gestoppt'}
            </Pill>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <Tile label="units_today" value={idle.data.units_today} />
            <Tile
              label="units_audited"
              value={idle.data.units_audited}
              tone={idle.data.units_audited >= idle.data.units_today ? 'ok' : 'warn'}
              hint="jede Einheit geprüft"
            />
            <Tile label="pid" value={idle.data.pid || '—'} />
            <Tile label="pidfile" value={<span className="font-mono text-[10px]">{idle.data.pidfile || '—'}</span>} />
          </div>
          <p className="text-[11px] mt-2" style={{ color: 'var(--s-mut)' }}>
            Der Vertrag ist ausgeglichen, wenn <span className="font-mono">units_audited</span> nie
            hinter <span className="font-mono">units_today</span> zurückbleibt. Eine unauditierten
            Einheit ist Arbeit, die niemand gesehen hat.
          </p>
        </section>
      ) : idle.kind === 'loading' ? (
        <Skeleton rows={2} />
      ) : idle.kind === 'down' ? (
        <EngineDown why={idle.why} />
      ) : null}
    </div>
  );
}

// ── Netz ───────────────────────────────────────────────────────────────────

type SporeState =
  | { kind: 'idle' }
  | { kind: 'pending' }
  | { kind: 'done'; s: Spore }
  // The whole verdict, never just its name. This is the door whose refusals are
  // the node's PUBLIC face, so it is the last place that may answer "no" to a
  // stranger without showing why.
  | { kind: 'denied'; verdict: Verdict; why: string }
  | { kind: 'down'; why: string }
  | { kind: 'error'; message: string };

function NetzView() {
  const manifest = useDoor<Manifest>(() => getManifest(), []);
  const spores = useDoor<{ spores: Spore[] }>(() => getSpores(12), []);
  const [text, setText] = useState('');
  const [state, setState] = useState<SporeState>({ kind: 'idle' });
  const elapsed = useElapsed(state.kind === 'pending');

  const send = useCallback(async () => {
    if (!text.trim()) return;
    setState({ kind: 'pending' });
    try {
      setState({ kind: 'done', s: await postSpore(text.trim(), 'desktop', 'spore') });
      setText('');
      spores.reload();
    } catch (e) {
      if (e instanceof SovereignDenied) setState({ kind: 'denied', verdict: e.verdict, why: e.messageText });
      else if (e instanceof SovereignEngineDown) setState({ kind: 'down', why: e.why });
      else setState({ kind: 'error', message: (e as Error).message });
    }
  }, [text, spores]);

  return (
    <div className="space-y-4">
      {manifest.kind === 'ready' ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <Tile label="knoten" value={manifest.data.node} />
            <Tile label="hub" value={manifest.data.hub_version} />
            <Tile
              label="vertrag"
              value={manifest.data.contract.holds ? 'hält' : 'gebrochen'}
              tone={manifest.data.contract.holds ? 'ok' : 'deny'}
              hint={`${manifest.data.contract.verified} geprüft`}
            />
            <Tile
              label="sporen"
              value={manifest.data.pulse.spores_total}
              hint={`${manifest.data.pulse.spore_denied} abgelehnt`}
            />
          </div>

          <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}>
            <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
              Das Auge über dem Netz
            </h2>
            <div className="flex items-center gap-2 flex-wrap">
              <OraclePill oracle={manifest.data.capability.oracle} />
              <Pill tone="mut">halter · {manifest.data.capability.oracle.holder ?? 'ValueGovernor'}</Pill>
            </div>
            <div className="mt-2">
              <KeyValue
                rows={[
                  ['netz · gold', manifest.data.gold.join(' · ') || '—'],
                  ['cycle', `${manifest.data.cycle.grundmodus} / ${manifest.data.cycle.stimmung} / ${manifest.data.cycle.fokus}`],
                  ['öffentliche fläche', <span key="p" className="font-mono text-[11px]">{manifest.data.public_dir}</span>],
                ]}
              />
            </div>
          </section>

          <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
            <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
              Eine Spore senden
            </h2>
            <p className="text-[11px] mb-2" style={{ color: 'var(--s-mut)' }}>
              Jede Spore wird bewertet, bevor sie gespeichert wird. Gehört sie nicht auf die
              öffentliche Fläche, ist sie trotzdem im Ledger — nur eben nicht öffentlich.
            </p>
            <div className="flex gap-2 flex-wrap">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={2}
                aria-label="Text der Spore"
                placeholder="Klarheit und Integrität zählen im Netz mehr als Tempo."
                className="flex-1 min-w-[16rem] rounded-lg border px-3 py-2 text-[13px] outline-none resize-y"
                style={{
                  background: 'var(--color-input-bg)',
                  borderColor: 'var(--color-input-border)',
                  color: 'var(--s-ink)',
                }}
              />
              <button
                onClick={send}
                disabled={state.kind === 'pending'}
                className="self-start px-4 py-2 rounded-lg text-[13px] font-medium cursor-pointer disabled:opacity-50"
                style={{ background: 'var(--s-gold)', color: '#fffdf6' }}
              >
                Senden
              </button>
            </div>
            <div className="mt-2 space-y-2">
              {state.kind === 'pending' && <Pending label="Sporen-Eingang wird bewertet" seconds={elapsed} />}
              {state.kind === 'down' && <EngineDown why={state.why} />}
              {state.kind === 'error' && <EngineDown why={state.message} />}
              {state.kind === 'denied' && (
                // The spore door's refusals are the node's PUBLIC face — the
                // one place a stranger most needs to be able to check the
                // judgement. It answered "no" with a sentence and no evidence:
                // no risk terms, no gold source, and no second eye on a vote
                // the doctrine says must carry the eye's boundary. The face
                // shows all of it, so the record is now the whole verdict, and
                // the door's own sentence rides with it.
                <DeniedView
                  verdict={state.verdict}
                  label="Spore abgelehnt"
                  scope={
                    <>
                      die Spore gehört nicht auf die öffentliche Fläche — und ist trotzdem
                      aufgezeichnet, nicht verworfen.
                      {state.why ? (
                        <span className="block mt-1 font-mono text-[11px]">{state.why}</span>
                      ) : null}
                    </>
                  }
                />
              )}
              {state.kind === 'done' && <VerdictCard verdict={state.s} label="Angenommen" />}
            </div>
          </section>
        </>
      ) : manifest.kind === 'loading' ? (
        <Skeleton rows={4} />
      ) : manifest.kind === 'down' ? (
        <EngineDown why={manifest.why} />
      ) : (
        <EngineDown why={(manifest as { message?: string }).message ?? 'unbekannt'} />
      )}

      <section className="rounded-lg border p-3" style={{ borderColor: 'var(--s-line)' }}>
        <h2 className="text-[13px] font-medium mb-2" style={{ color: 'var(--s-ink)' }}>
          Sporen im Eingang
        </h2>
        <SporeList door={spores} />
      </section>
    </div>
  );
}

/**
 * The spore inbox.
 *
 * Split out so the narrowing happens once, in one place, before any list is
 * drawn. A nested ternary that ends in a length check looks equivalent but is
 * not: TypeScript narrows the union on `kind === 'loading'` and
 * `kind === 'down'`, and has nothing left to narrow on by the time it reaches
 * the third branch — so the happy path would be typed as possibly-absent
 * exactly where the real data lives.
 */
function SporeList({ door }: { door: Door<{ spores: Spore[] }> }) {
  if (door.kind !== 'ready') {
    if (door.kind === 'loading') return <Skeleton rows={3} />;
    if (door.kind === 'down') return <EngineDown why={door.why} />;
    if (door.kind === 'denied') return <EngineDown why="der Sporen-Eingang ist nicht freigegeben" />;
    if (door.kind === 'interrupted') return <EngineDown why="die Liste wurde unterbrochen" />;
    return <EngineDown why={door.message} />;
  }

  const spores = door.data.spores ?? [];
  if (spores.length === 0) {
    return (
      <Empty title="Noch keine Spore">
        Der Eingang ist leer. Das ist ein Zustand, kein Fehler.
      </Empty>
    );
  }

  return (
    <ul className="space-y-1.5">
      {spores.map((s) => (
        <li
          key={s.stamp}
          className="rounded-lg border p-2.5"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface-2)' }}
        >
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-[10px]" style={{ color: 'var(--s-mut-2)' }}>
              {s.stamp}
            </span>
            <VerdictPill verdict={s.verdict} />
            <OraclePill oracle={s.oracle} />
            <span className="text-[10px] ml-auto" style={{ color: 'var(--s-mut-2)' }}>
              {s.source}
            </span>
          </div>
          <p className="text-[12px] mt-1" style={{ color: 'var(--s-ink-2)' }}>
            {s.text}
          </p>
        </li>
      ))}
    </ul>
  );
}
