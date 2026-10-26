/**
 * Display primitives shared by every Bianca tab.
 *
 * These exist so the React surface and the sovereign face can say the same
 * things the same way. A verdict that looks different on two screens of one
 * product is two products wearing one name — and worse, a reader who has
 * learned to trust the red on one surface has learned nothing on the other.
 *
 * Colour discipline, inherited from the token layer: gold is the accent,
 * DENY RED AND WARN AMBER ARE RESERVED FOR GOVERNANCE OUTCOMES. If red could
 * mean "error" as well as "refused", it would mean neither.
 */

import type { ReactNode } from 'react';
import { AlertTriangle, Ban, Eye, Loader2 } from 'lucide-react';
import type {
  AnyVerdict,
  Oracle,
  OracleBoundary,
  ReplyRead,
  ShieldDirection,
  Spore,
  Verdict,
} from '../../lib/sovereign-api';
import { ENGINE_DOWN_NOTE } from '../../lib/sovereign-api';
import { GOLD } from './tabs';

// ── the five gold values ───────────────────────────────────────────────────

export function GoldChips({ hits = [] }: { hits?: string[] }) {
  const found = new Set(hits.map((h) => h.toLowerCase()));
  return (
    <div className="flex flex-wrap gap-1.5" role="list" aria-label="Die fünf Goldwerte">
      {GOLD.map((g) => {
        const hit = found.has(g.id);
        return (
          <span
            key={g.id}
            role="listitem"
            title={g.en}
            className="px-2 py-0.5 rounded-full text-[11px] border transition-colors"
            style={{
              borderColor: hit ? 'var(--s-gold)' : 'var(--s-line)',
              background: hit ? 'color-mix(in srgb, var(--s-gold) 16%, transparent)' : 'transparent',
              color: hit ? 'var(--s-gold)' : 'var(--s-mut)',
              fontWeight: hit ? 600 : 400,
            }}
          >
            {g.de}
          </span>
        );
      })}
    </div>
  );
}

// ── pills ──────────────────────────────────────────────────────────────────

export function Pill({
  children,
  tone = 'mut',
  title,
}: {
  children: ReactNode;
  tone?: 'ok' | 'warn' | 'deny' | 'mut' | 'gold' | 'info';
  title?: string;
}) {
  const color =
    tone === 'ok'
      ? 'var(--s-ok)'
      : tone === 'warn'
        ? 'var(--s-warn)'
        : tone === 'deny'
          ? 'var(--s-deny)'
          : tone === 'gold'
            ? 'var(--s-gold)'
            : tone === 'info'
              ? 'var(--s-info)'
              : 'var(--s-mut)';
  return (
    <span
      title={title}
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] border whitespace-nowrap"
      style={{
        color,
        borderColor: `color-mix(in srgb, ${color} 42%, transparent)`,
        background: `color-mix(in srgb, ${color} 10%, transparent)`,
      }}
    >
      {children}
    </span>
  );
}

export function verdictTone(v: string): 'ok' | 'warn' | 'deny' | 'mut' {
  if (v === 'frei') return 'ok';
  if (v === 'zurueckhalten') return 'deny';
  if (v === 'vorsichtig') return 'warn';
  return 'mut';
}

export function VerdictPill({ verdict }: { verdict: string }) {
  return (
    <Pill tone={verdictTone(verdict)} title={`Verdikt: ${verdict}`}>
      {verdict}
    </Pill>
  );
}

/**
 * The second eye. Always says what it is: advisory, and not the holder.
 * A reader who cannot tell advice from authority will one day treat a warning
 * as a ruling — or a ruling as dismissible.
 *
 * It takes BOTH shapes the node sends, and the difference is not cosmetic. On a
 * **verdict** the eye has voted and the vote is the news, so it is shown. On
 * the **identity door** it has not been asked anything, so there is no vote —
 * and rendering `2nd eye · {undefined}` there would be the set-21 defect one
 * layer down: a claim on screen that is present and wrong, and it survives a
 * reviewer because it looks like evidence. So the boundary-only shape says
 * *on · advisory · holds nothing* and names no vote, because there is none.
 */
export function OraclePill({ oracle }: { oracle?: Oracle | OracleBoundary | null }) {
  if (!oracle) return null;
  const voted = 'vote' in oracle;
  return (
    <Pill tone={voted && oracle.vote === 'warnen' ? 'warn' : 'mut'} title="Das zweite Auge rät; es bindet nichts.">
      <Eye size={11} aria-hidden />
      2nd eye · {voted ? oracle.vote : 'on · berät'}
      {oracle.binding === false ? ' · berät' : ''}
    </Pill>
  );
}

// ── a verdict, shown whole ─────────────────────────────────────────────────

/**
 * The governance record, in full: the verdict, the gold source, the blocked
 * stems, and the second eye. Every verdict in this app renders through this
 * component, so `gold src` can never be quietly dropped from one of them.
 *
 * It accepts EITHER kind of judgement the node sends:
 *
 *   · a `Verdict` — a full read of a REQUEST, with provenance (gold source,
 *     alignment, risk, the gold values that fired). Rendered whole.
 *   · a `ReplyRead` — the lighter read of DELIVERED WORDS, which the doors
 *     deliberately send as just verdict + risk terms + the eye. Rendered with
 *     everything it actually carries, and **no gold source, because there
 *     isn't one to show** — the values that governed the request are the same
 *     ones shown on the request's own verdict.
 *
 * The union is the point. The old contract typed a reply read as a full
 * `Verdict`, so this card asked for `gold_source` on a field the node never
 * sends and would have printed the string `undefined` into a governance
 * panel. Accepting the true shape makes that impossible rather than merely
 * unlikely, and it means a reply read can be shown with the same care as a
 * request read instead of being dropped for being incomplete.
 */
export function VerdictCard({
  verdict,
  label = 'Urteil',
  dense = false,
}: {
  verdict: AnyVerdict;
  label?: string;
  dense?: boolean;
}) {
  const denied = verdict.verdict === 'zurueckhalten';
  // A reply read carries no scores and no provenance. Detect it by what it
  // HAS, not by where it came from, so a door that starts sending the full
  // shape is picked up automatically.
  const full: (Verdict | Spore) | null =
    'gold_source' in verdict ? (verdict as Verdict | Spore) : null;
  return (
    <div
      className="rounded-lg border p-3"
      style={{
        borderColor: denied
          ? 'color-mix(in srgb, var(--s-deny) 45%, transparent)'
          : 'var(--s-line)',
        background: denied ? 'color-mix(in srgb, var(--s-deny) 8%, transparent)' : 'var(--s-surface)',
      }}
    >
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-[11px] uppercase tracking-wider" style={{ color: 'var(--s-mut)' }}>
          {label}
        </span>
        <VerdictPill verdict={verdict.verdict} />
        <OraclePill oracle={verdict.oracle} />
        {full && (
          <span className="text-[11px] ml-auto tabular-nums" style={{ color: 'var(--s-mut)' }}>
            align {fmt(full.alignment)} · risk {fmt(full.risk)}
          </span>
        )}
      </div>

      {verdict.risk_hits.length > 0 && (
        <div className="mt-2 text-[12px]" style={{ color: 'var(--s-deny)' }}>
          <Ban size={12} className="inline mr-1" aria-hidden />
          risk hits : {[...verdict.risk_hits].join(', ')}
        </div>
      )}

      {/* Set 21 — the deflector answers "what is missing?", not just "no".
          Rendered HERE, in the ONE place a verdict renders, so every refusal
          surface on this app inherits it. Re-deriving it per screen is how this
          repo found the same "outcome without evidence" defect in four places. */}
      {full && full.missing && full.missing.length > 0 && (
        <div className="mt-1.5 text-[11px]" style={{ color: 'var(--s-mut)' }}>
          es fehlt : {[...full.missing].join(' · ')}
        </div>
      )}

      {full ? (
        <div className="mt-2 text-[11px]" style={{ color: 'var(--s-mut)' }}>
          gold src : {full.gold_source || '—'}
        </div>
      ) : (
        // Said rather than left blank, because a missing line reads as an
        // oversight and this is a deliberate difference between two kinds of
        // read.
        <div className="mt-2 text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          reply read — die Worte selbst, nicht die Anfrage. Ihre Herkunft ist die
          Goldquelle der Anfrage oben.
        </div>
      )}

      {full && !dense && <GoldChips hits={[...full.gold_hits]} />}

      {denied && (
        <div
          className="mt-2 pt-2 border-t text-[12px]"
          style={{ borderColor: 'color-mix(in srgb, var(--s-deny) 25%, transparent)', color: 'var(--s-deny)' }}
        >
          <strong>no means no</strong> — hier wurde nicht verhandelt.
        </div>
      )}
    </div>
  );
}

// ── a refusal, shown as a record ───────────────────────────────────────────

/**
 * A refused DOOR, shown as the governance record it is.
 *
 * This component exists because one defect appeared in three places: a page
 * caught the `SovereignDenied`, kept `e.verdict.verdict` — a *string* — and
 * threw the rest of the verdict away, then rendered "no means no" as a bare
 * sentence. What that costs is not elegance. The reader is told the request was
 * refused and given no way to check it: no risk terms, no gold source, and **no
 * second eye on a vote that the doctrine says must carry the eye's boundary**.
 * The sovereign face shows all of it, so the two surfaces disagreed about what
 * a refusal looks like — and the worst instance sat on the spore door, whose
 * refusals are the node's public face.
 *
 * So a refusal is a `Verdict` and goes through the same `VerdictCard` as every
 * other verdict on this surface. That is the whole discipline: one renderer for
 * a verdict is the only way `gold src` stays present, and it is why this lives
 * in `primitives` rather than in a page — three tabs needed it, and a component
 * with three callers in three tabs is not a page component.
 *
 * `scope` is the one thing the card cannot carry: what was refused and what
 * becomes of it. "No voice was asked" and "this is written to the ledger" are
 * different facts, and a reader looking at an empty result needs to know
 * whether the work never began or merely produced nothing.
 */
/**
 * Where the refusal points.
 *
 * 🚨 Rendered here, once, and optional. Set 28 gave every refusal a *direction*
 * — the other doors of this node that stand open, each with what is behind it —
 * and the claim behind it is checkable rather than decorative: *follow the
 * direction, submit the same request, get the same verdict.* A refusal card that
 * shows only the verdict is a wall with a label on it.
 *
 * The two branches are both real answers and neither is a failure:
 *
 *  - a **request** names other doors. There is somewhere to go.
 *  - a **tool call** names *none*, and says why: the run carried on without it.
 *    Rendering an empty list as a broken list would teach a reader that the
 *    deflection failed, when the honest answer there is that the run continued.
 */
function Deflection({ direction }: { direction: ShieldDirection }) {
  const tuer = direction.doors.length > 0;
  return (
    <div
      className="rounded-lg border px-3 py-2 text-[12px]"
      style={{
        borderColor: 'color-mix(in srgb, var(--s-line) 100%, transparent)',
        background: 'var(--s-surface-2)',
        color: 'var(--s-mut)',
      }}
    >
      <div>
        <strong style={{ color: 'var(--s-ink)' }}>gehalten bei</strong>{' '}
        <span className="font-mono">{direction.held_at}</span>{' '}
        <span style={{ color: 'var(--s-mut-2)' }}>({direction.kind})</span>
      </div>
      {tuer ? (
        <>
          <div className="mt-1.5" style={{ color: 'var(--s-mut-2)' }}>
            Diese Tür bleibt zu. Diese hier stehen offen — und auf ihnen gilt dasselbe Tor.
          </div>
          <ul className="mt-1 space-y-0.5">
            {direction.doors.map((t) => (
              <li key={t.door}>
                <span className="font-mono" style={{ color: 'var(--s-ink)' }}>
                  {t.door}
                </span>
                <span className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
                  {' '}
                  — {t.opens}
                </span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <div className="mt-1.5" style={{ color: 'var(--s-mut-2)' }}>
          Der Lauf ging weiter — es gab keine andere Tür, denn ein gehaltenes Werkzeug lässt den
          Lauf nicht sterben. Es fehlt ihm nur die Wirkung.
        </div>
      )}
    </div>
  );
}

export function DeniedView({
  verdict,
  label = 'abgelehnt',
  scope,
  direction,
}: {
  verdict: AnyVerdict;
  label?: string;
  scope: ReactNode;
  /**
   * The deflection, when the door sent one. Absent on `/govern` and
   * `/hub/spore` and on an unreadable 403, so a screen may not assume it.
   */
  direction?: ShieldDirection;
}) {
  return (
    <div className="space-y-2">
      <VerdictCard verdict={verdict} label={label} />
      <div className="text-[12px]" style={{ color: 'var(--s-mut)' }}>
        <strong style={{ color: 'var(--s-deny)' }}>no means no</strong> — {scope}
      </div>
      {direction && <Deflection direction={direction} />}
    </div>
  );
}

// ── the engine is down ─────────────────────────────────────────────────────

/**
 * Said the same way on every surface, so "the motor is down" is never read as
 * "the answer was empty". Mirrors ENGINE_DOWN_NOTE in the sovereign face; if
 * one changes, both must.
 */
export function EngineDown({ why }: { why: string }) {
  return (
    <div
      className="rounded-lg border p-3 text-[13px]"
      style={{
        borderColor: 'color-mix(in srgb, var(--s-warn) 45%, transparent)',
        background: 'color-mix(in srgb, var(--s-warn) 9%, transparent)',
        color: 'var(--s-warn)',
      }}
      role="status"
    >
      <div className="flex items-center gap-2 font-semibold">
        <AlertTriangle size={14} aria-hidden />
        Der Motor antwortet nicht (503).
      </div>
      <div className="mt-1" style={{ color: 'var(--s-ink)' }}>
        {why}
      </div>
      <div className="mt-1" style={{ color: 'var(--s-mut)' }}>
        {ENGINE_DOWN_NOTE}
      </div>
    </div>
  );
}

// ── small pieces ───────────────────────────────────────────────────────────

export function Tile({
  label,
  value,
  hint,
  tone = 'mut',
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: 'mut' | 'ok' | 'warn' | 'deny' | 'gold';
}) {
  const color =
    tone === 'ok'
      ? 'var(--s-ok)'
      : tone === 'warn'
        ? 'var(--s-warn)'
        : tone === 'deny'
          ? 'var(--s-deny)'
          : tone === 'gold'
            ? 'var(--s-gold)'
            : 'var(--s-ink)';
  return (
    <div
      className="rounded-lg border px-3 py-2 min-w-0"
      style={{ borderColor: 'var(--s-line)', background: 'var(--s-surface)' }}
    >
      <div className="text-[10px] uppercase tracking-wider truncate" style={{ color: 'var(--s-mut)' }}>
        {label}
      </div>
      <div className="text-lg font-semibold tabular-nums leading-tight" style={{ color }}>
        {value}
      </div>
      {hint && (
        <div className="text-[11px] truncate" style={{ color: 'var(--s-mut)' }}>
          {hint}
        </div>
      )}
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div
      className="rounded-lg border border-dashed p-6 text-center"
      style={{ borderColor: 'var(--s-line-2)', color: 'var(--s-mut)' }}
    >
      <div className="text-sm font-medium" style={{ color: 'var(--s-ink-2)' }}>
        {title}
      </div>
      {children && <div className="text-[12px] mt-1 max-w-prose mx-auto">{children}</div>}
    </div>
  );
}

export function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-label="lädt">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-3 rounded mb-2 animate-pulse"
          style={{
            width: `${100 - i * 14}%`,
            background: 'var(--s-surface-3)',
            animationDelay: `${i * 90}ms`,
          }}
        />
      ))}
    </div>
  );
}

/**
 * A write in progress: WHAT it is doing, and HOW LONG it has been.
 * A real `/v1/ask` measures 83s on this host. Silence for 83s reads as a
 * hung browser, not as thinking.
 */
export function Pending({ label, seconds }: { label: string; seconds: number }) {
  return (
    <div
      className="rounded-lg border p-3 text-[12px] flex items-center gap-2 flex-wrap"
      style={{ borderColor: 'var(--s-line)', color: 'var(--s-mut)' }}
      role="status"
    >
      <Loader2 size={14} className="animate-spin" style={{ color: 'var(--s-gold)' }} aria-hidden />
      <span style={{ color: 'var(--s-ink-2)' }}>{label}</span>
      <span className="tabular-nums font-mono">{seconds}s</span>
      <span className="text-[11px]">· lokal, kein Cloud-Hopping</span>
    </div>
  );
}

export function KeyValue({ rows }: { rows: [string, ReactNode][] }) {
  return (
    <dl className="grid gap-1.5">
      {rows.map(([k, v]) => (
        <div key={k} className="flex gap-3 items-baseline">
          <dt className="text-[11px] uppercase tracking-wider w-32 shrink-0" style={{ color: 'var(--s-mut)' }}>
            {k}
          </dt>
          <dd className="text-[13px] min-w-0 break-words" style={{ color: 'var(--s-ink)' }}>
            {v}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export function fmt(n: number | undefined | null, digits = 2): string {
  if (n === undefined || n === null || Number.isNaN(n)) return '—';
  return Number(n).toFixed(digits);
}
