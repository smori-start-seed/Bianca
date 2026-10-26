/**
 * Der Garten — Colorverse, read, not tended.
 *
 * This screen is the one surface in Bianca that is **ungated**. That is not an
 * oversight to be tidied away; it is the boundary, drawn once, in the place
 * where someone might otherwise assume there was a gate. So the screen leads
 * with `tended: false` and the note explaining why, rather than with a colour.
 *
 * Three things it must never do:
 *
 *  1. **Improve the kernel.** The colour shown is the kernel's own
 *     `hue_mean`, and nothing else. A prettier hue would be Bianca inventing
 *     the beauty it was asked to display.
 *  2. **Publish one run as a property — or call death a colour.**
 *     `flat_at` — the step at which every cell carries the same hue — is 82
 *     in one world and 235 in the next, because the child never seeds
 *     `random`. So the number is labelled as *this run's*, with the measured
 *     range beside it. Set 24 shipped `flat_at=2` as though it were a
 *     constant; that was the `dev262` shape.
 *     🚨 **SET 35 (2026-10-05): `flat_at` no longer occurs, and `hue = 0`
 *     never appears.** Measured on the kernel this host reads, after three
 *     edits (notes `five-levels-notes.md` 13-15): 17-18 new Clusters are built
 *     at step 1, `flat_at` does not fire in 1000 steps, and 650 cells still
 *     carry brightness at step 400 (608 at step 1000). Two causes, neither a
 *     threshold: `engine.py` marked its seeds at the **end** of `step()`, after
 *     the neighbourhood variance had already fallen by a factor of 0.21, and
 *     `Zelle.py` wrote the death colour `hue = 0` back into a live
 *     neighbourhood. **So the `flat_at` branches below are unreachable on the
 *     current kernel — kept, because a regression must still be visible, and
 *     the range is now printed as history beside this run's value.**
 *     🚨 **Set 34 measured what `flat_at` actually is: the step at which the
 *     world has lost every hue.** `failsafe()` (`Zelle.py:83-114`) writes
 *     `hue = 0` on both of its arms, so a dead cell sits at hue 0 — and over
 *     52 measured worlds, in the exact step `flat_at` is set, the mean hue was
 *     `0.0`, every time.
 *     🚨 **It is *not* the step at which every cell dies, and this surface
 *     said so for one commit.** Eight worlds agreed, then a ninth showed 575
 *     cells still carrying brightness at that step, and 530–581 cells at the
 *     collapse step hold `hue == 0` with brightness strictly between 0 and 1.
 *     `failsafe()` has a **second arm** (`:103-122`) that extinguishes a cell
 *     for being *too pure, too bright and too harmonious* and leaves it at
 *     `brightness = 1`. Measured latent here (0 hits in 3 runs) — but it is
 *     why the death claim was false, and it is the mirror image of the defect
 *     we carry at `:87`.
 *     So the frame states the weaker thing that holds without exception —
 *     *no colour left* — and says outright that it does not count living
 *     cells. Before set 34 this surface said "one colour: all cells the same"
 *     about a world that had merely lost its hue: true, and this repo's
 *     sharpest defect, evidence present and wrong surviving a reviewer.
 *  3. **Call a dead garden live.** `live` is `fresh` AND a child running. A
 *     frame written by a child that has since died is still fresh, and
 *     `stop()` deliberately keeps it — the last thing the kernel was is still
 *     a fact about it.
 *
 * The three defects in the sibling kernel are shown with their file:line,
 * because they are claims about a repository this one does not control and
 * nothing here would notice if a line moved.
 *
 * 🚨 The heading below used to say "two defects — carried, not fixed", and both
 * halves had gone out of date. There are three entries now, and set 34 DID edit
 * the sibling on the owner's decision: `build_world` now builds instead of
 * stepping, and the harmonie scale was made honest. `ALF/Colorverse` has no
 * version control, so that before/after lives in `five-levels-notes.md` (set
 * 34) and nowhere else — that was the owner's decision over `git init`. So
 * "carried, not fixed" is now false for two of the three, and saying so is
 * cheaper than letting the face quietly understate what was done to a kernel
 * that has no history of its own.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useDoor } from './useDoor';
import type { DoorPending } from './useDoor';
import { getGarden, startGarden, stopGarden } from '../../lib/sovereign-api';
import type { GardenState, GardenUpstream } from '../../lib/sovereign-api';
import { Empty, EngineDown, KeyValue, Pill, Skeleton, Tile } from './primitives';

function DoorBody({ door }: { door: DoorPending<GardenState> }) {
  if (door.kind === 'loading') return <Skeleton rows={5} />;
  if (door.kind === 'down') return <EngineDown why={door.why} />;
  if (door.kind === 'denied') return <EngineDown why="dieser Weg ist nicht freigegeben" />;
  if (door.kind === 'interrupted') return <EngineDown why="die Lesung wurde unterbrochen" />;
  return <EngineDown why={door.message} />;
}

function fmt(x: number | null | undefined, d = 3): string {
  return x === null || x === undefined ? '—' : Number(x).toFixed(d);
}

/**
 * The colour, and nothing else.
 *
 * `hue_mean` is degrees from the kernel. Lightness and saturation are Bianca's
 * — a dark, quiet wash, because this is a surface to read words on. The face
 * uses the identical value, so the two surfaces cannot drift apart here.
 */
function hueCss(hue: number | null | undefined): string {
  if (hue === null || hue === undefined || Number.isNaN(hue)) return 'transparent';
  return `hsl(${hue} 42% 12%)`;
}

function UpstreamRow({ u }: { u: GardenUpstream }) {
  return (
    <div
      className="rounded-md border p-2.5"
      style={{ borderColor: 'var(--s-line)', background: 'var(--s-bg-2)' }}
    >
      <div className="flex items-baseline gap-2 flex-wrap">
        <span className="text-[12px] font-medium" style={{ color: 'var(--s-ink)' }}>
          {u.id}
        </span>
        <span className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
          {u.where}
        </span>
      </div>
      <p className="text-[11px] mt-1" style={{ color: 'var(--s-ink)' }}>
        {u.what}
      </p>
      <p className="text-[10px] mt-1" style={{ color: 'var(--s-mut-2)' }}>
        Warum es zählt: {u.why_it_matters}
      </p>
    </div>
  );
}

export function GardenView() {
  const door = useDoor<GardenState>(getGarden, []);
  const [busy, setBusy] = useState(false);
  const [said, setSaid] = useState<string | null>(null);
  const [live, setLive] = useState(false);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  /**
   * Polling follows the child, not a fixed interval's hope: it keeps asking
   * while the garden is alive and stops the moment it is not, so a stopped
   * garden does not keep asking a question whose answer cannot change.
   */
  useEffect(() => {
    if (!live) return;
    const t = setInterval(() => door.reload(), 2000);
    return () => clearInterval(t);
  }, [live, door]);

  const act = useCallback(
    async (what: 'start' | 'stop') => {
      setBusy(true);
      try {
        if (what === 'start') {
          const r = await startGarden();
          if (!alive.current) return;
          setSaid(r.reason ?? (r.started ? 'gestartet' : 'nicht gestartet'));
          if (r.started) setLive(true);
        } else {
          const r = await stopGarden();
          if (!alive.current) return;
          setSaid(r.reason ?? (r.stopped ? 'gestoppt' : 'nicht gestoppt'));
          if (r.stopped) setLive(false);
        }
        door.reload();
      } catch {
        if (alive.current) setSaid('die Tür antwortete nicht');
      } finally {
        if (alive.current) setBusy(false);
      }
    },
    [door],
  );

  if (door.kind !== 'ready') return <DoorBody door={door} />;
  const { kernel, frame } = door.data;

  return (
    <div className="space-y-4">
      {/* ── the one ungated surface, said first ─────────────────────────── */}
      <div
        className="rounded-lg border p-3"
        style={{ borderColor: 'var(--s-line)', background: 'var(--s-bg-2)' }}
      >
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-[13px] font-medium" style={{ color: 'var(--s-ink)' }}>
            Die eine ungatete Fläche
          </h3>
          <Pill tone={kernel.tended ? 'deny' : 'ok'}>
            {kernel.tended ? 'GARTEN GESTALTET' : 'GESTALTET NICHTS'}
          </Pill>
        </div>
        <p className="text-[11px] mt-1.5" style={{ color: 'var(--s-mut)' }}>
          {kernel.tended_note}
        </p>
      </div>

      {/* ── the colour, and the kernel's own line under it ───────────────── */}
      <div
        className="rounded-lg border p-4 transition-colors duration-1000"
        style={{
          borderColor: 'var(--s-line)',
          background: frame.present ? hueCss(frame.hue_mean) : 'var(--s-bg-2)',
        }}
      >
        <div className="flex items-baseline justify-between gap-3 flex-wrap">
          <span className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--s-mut-2)' }}>
            hue_mean des Kerns
          </span>
          <span className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            {frame.present ? `${fmt(frame.hue_mean, 2)}° · hsl(h 42% 12%)` : 'kein Rahmen'}
          </span>
        </div>
        {frame.present ? (
          <p className="text-[11px] mt-2 font-mono" style={{ color: 'var(--s-mut)' }}>
            {frame.readout || '—'}
          </p>
        ) : (
          <p className="text-[11px] mt-2" style={{ color: 'var(--s-mut)' }}>
            noch kein Rahmen
          </p>
        )}
      </div>

      {/* ── the two controls ─────────────────────────────────────────────── */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          type="button"
          className="text-[11px] px-2.5 py-1 rounded border disabled:opacity-50"
          style={{ borderColor: 'var(--s-line)', color: 'var(--s-ink)' }}
          disabled={busy}
          onClick={() => void act('start')}
        >
          wachsen lassen
        </button>
        <button
          type="button"
          className="text-[11px] px-2.5 py-1 rounded border disabled:opacity-50"
          style={{ borderColor: 'var(--s-line)', color: 'var(--s-ink)' }}
          disabled={busy}
          onClick={() => void act('stop')}
        >
          anhalten
        </button>
        {said && (
          <span className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            {said}
          </span>
        )}
      </div>

      {/* ── the kernel floor ─────────────────────────────────────────────── */}
      {!kernel.present ? (
        <div
          className="rounded-md border p-3"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-bg-2)' }}
        >
          <KeyValue rows={[['Boden', kernel.path || '—']]} />
          <p className="text-[11px] mt-2" style={{ color: 'var(--s-warn, var(--s-ink))' }}>
            {kernel.missing_note}
          </p>
          <p className="text-[10px] font-mono mt-1" style={{ color: 'var(--s-mut-2)' }}>
            fehlt: {(kernel.missing || []).join(', ') || '—'}
          </p>
        </div>
      ) : frame.present && frame.error ? (
        <div
          className="rounded-md border p-3"
          style={{ borderColor: 'var(--s-line)', background: 'var(--s-bg-2)' }}
        >
          <p className="text-[11px] font-mono" style={{ color: 'var(--s-ink)' }}>
            {frame.error}
          </p>
        </div>
      ) : frame.present ? (
        <>
          {/* 🚨 `cluster` was NOT on this face, and a test had been asserting
              it was. The assertion was passing on the substring "90" inside
              the prose "…from 1 to 900" in a docstring — a check that fires on
              the wrong text is not a check, and set 34's re-take of the fixture
              made it fire for real and go red. So the reading is now really
              here: the cluster count is the garden's only reproduction
              number, and it is the number that has never moved off 90. Showing
              it costs one tile and stops the claim from being prose. */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-2">
            <Tile label="schritt" value={String(frame.step)} />
            <Tile label="zellen" value={String(frame.cells)} />
            <Tile label="harmonie" value={fmt(frame.harm)} />
            <Tile label="drift" value={fmt(frame.drift, 6)} />
            <Tile label="energie" value={fmt(frame.energie)} />
            <Tile label="keime" value={String(frame.keime)} tone={frame.keime > 0 ? 'ok' : 'warn'} />
            <Tile label="cluster" value={String(frame.cluster)} tone="warn" />
          </div>

          {/* The two deaths, as two facts with two steps. The threshold is the
              kernel's OWN, read out of the kernel — measured drift is never
              exactly 0.0, because a float does not get there. */}
          <div
            className="rounded-md border p-3"
            style={{
              borderColor: 'var(--s-line)',
              background: 'var(--s-bg-2)',
            }}
          >
            <p className="text-[11px]" style={{ color: 'var(--s-ink)' }}>
              {frame.convergence_disputed ? (
                // 🚨 Set 35 (2026-10-06). This branch was MISSING here, and the
                // face had it in two places — so React said "Schon geboren
                // still, er konnte nie wachsen" next to a live garden that had
                // built 16 clusters. Same defect, third surface, found the same
                // way the owner found the first: by looking at the screen.
                //
                // The trap is the *number*: mean drift 0.00166 against a rule
                // needing 0.40 is CORRECT, and it made the false conclusion look
                // measured. A right number makes a wrong claim harder to refute
                // than a wrong number would.
                <>
                  <b>Der Rahmen widerspricht sich, und beide Arme sind wahr.</b> Der{' '}
                  <i>mittlere</i> Drift liegt bei{' '}
                  <span className="font-mono">{fmt(frame.drift, 5)}</span>, der Kern verlangt{' '}
                  <span className="font-mono">{fmt(frame.thresholds?.drift, 2)}</span> — und die
                  Welt hat trotzdem <b>ab Schritt {frame.grew_at} {frame.cluster - (frame.cluster_start ?? 0)} neue Cluster gebaut</b> ({frame.cluster_start} →{' '}
                  {frame.cluster}). Der Mittelarm ist <b>nein</b>, der Clusterarm <b>ja</b>.
                  Fortpflanzung braucht <b>11 Saaten gleichzeitig</b>, ein Mittel ist keine Zahl.
                </>
              ) : frame.born_converged ? (
                <>
                  <b>Schon geboren still.</b> Schritt 1 hatte Drift{' '}
                  <span className="font-mono">{fmt(frame.drift, 6)}</span> — der Kern verlangt{' '}
                  <span className="font-mono">{fmt(frame.thresholds?.drift, 2)}</span> für einen
                  Keim. Er <b>konnte</b> nie wachsen.
                </>
              ) : frame.converged_at ? (
                <>
                  Kann seit <b>Schritt {frame.converged_at}</b> keinen Keim mehr setzen (Drift ≤{' '}
                  <span className="font-mono">{fmt(frame.thresholds?.drift, 2)}</span>).
                </>
              ) : (
                <>Kann noch einen Keim setzen.</>
              )}
              {frame.flat_at ? (
                // 🚨 Set 35 (2026-10-06). This sentence was the *second* place
                // the same number had two texts: the face said "55–235 **vor Set
                // 35**" and this said "nach der Reparatur gemessen 55–235", as
                // though the range belonged to the kernel that is running. It
                // does not. 55–235 was measured on the kernel BEFORE `Zelle.py`'s
                // `failsafe` gave a dying cell its neighbours' mean instead of
                // hue 0; on the current kernel the step at which the last hue
                // dies **does not occur** — measured at 1000 steps by me and at
                // **3858** on the owner's own run, `flat_at = None`.
                //
                // So this branch is now a **regression notice**, and it says so.
                // The run-to-run variation is real, but it is a property of the
                // OLD kernel; reading it as "a property of the run, not the
                // kernel" on the current kernel would be the dev262 shape once
                // more — a number from a world that no longer exists, published
                // beside a screen that can no longer produce it.
                <>
                  {' '}
                  Ab <b>Schritt {frame.flat_at} dieses Laufs</b> hat die Welt <b>keine Farbe</b>{' '}
                  mehr: alle {frame.cells} Zellen tragen hue 0. Das sieht aus wie eine
                  Einheitsfarbe und ist eine Welt ohne Farbe. Ob dort noch Zellen leben, sagt
                  dieser Rahmen nicht — er zählt es nicht. 🚨 <b>Auf dem Kern von heute ist das eine
                  Regression:</b> hier kommt der Schritt nicht vor —{' '}
                  <span className="font-mono">55–235</span> war gemessen{' '}
                  <b>vor Set 35</b>, als eine sterbende Zelle hue 0 bekam. Erscheint die
                  Zahl jetzt, hat sich der Kern geändert.
                </>
              ) : null}
            </p>
          </div>

          <div className="text-[10px] font-mono" style={{ color: 'var(--s-mut-2)' }}>
            {Object.keys(frame.files || {}).length} Dateien ·{' '}
            {frame.live ? (
              <b style={{ color: 'var(--s-ok, var(--s-ink))' }}>lebendig</b>
            ) : (
              <b>nicht lebendig</b>
            )}
            {frame.stale ? ` — ${frame.stale_note || ''}` : ''}
            {frame.child_running ? ' · Kind läuft' : ' · kein Kind'}
          </div>
        </>
      ) : (
        <Empty title="Der Kern steht, er läuft noch nicht">
          <span className="text-[11px]">
            {Object.keys(kernel.files || {}).length} Dateien, alle gehasht. Drücke{' '}
            <b>wachsen lassen</b> — das ist eine Entscheidung, keine Nebenwirkung: diese Seite liest
            nur, sie startet nie etwas.
          </span>
        </Empty>
      )}

      {/* ── the file fingerprints, so the colour is traceable ────────────── */}
      <details className="rounded-md border" style={{ borderColor: 'var(--s-line)' }}>
        <summary className="text-[11px] px-3 py-2 cursor-pointer" style={{ color: 'var(--s-mut)' }}>
          Datei-Fingerprints ({Object.keys(kernel.files || {}).length}) — der Boden, auf dem diese
          Farbe steht
        </summary>
        <div className="px-3 pb-3 grid gap-1">
          {Object.entries(kernel.files || {}).map(([f, h]) => (
            <div key={f} className="flex gap-3 text-[10px] font-mono">
              <span className="w-44 shrink-0" style={{ color: 'var(--s-mut-2)' }}>
                {f}
              </span>
              <span style={{ color: 'var(--s-mut)' }}>{h}</span>
            </div>
          ))}
        </div>
      </details>

      {/* ── the three upstream defects: two repaired, none verifiable here ───── */}
      <div className="space-y-1.5">
        <h4 className="text-[12px] font-medium" style={{ color: 'var(--s-ink)' }}>
          Drei Fehler im Nachbar-Kern — zwei davon in Set 34 behoben
        </h4>
        {(kernel.upstream || []).map((u) => (
          <UpstreamRow key={u.id} u={u} />
        ))}
      </div>
    </div>
  );
}
