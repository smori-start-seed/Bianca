/**
 * The frame every tab page sits in: the option strip, then the panel.
 *
 * One frame means one spacing scale and one focus treatment, which is the
 * mechanical half of "coherent" — the half that survives contact with a
 * future contributor who never saw the sovereign face.
 *
 * The selected option lives in the URL (`/node?sub=netz`), not in component
 * state. That costs one search param and buys three things a stateful tab bar
 * does not have: a bookmark lands on the option you were looking at, the back
 * button walks your option history, and a legacy URL can redirect to a
 * specific option rather than to a tab's first page. A tab bar that keeps its
 * own copy of where you are will eventually disagree with the address bar, and
 * the address bar is the one the user can see.
 */

import { useCallback } from 'react';
import type { ReactNode } from 'react';
import { useSearchParams } from 'react-router';
import { SubTabs } from './TabBar';
import type { SubView, TabId } from './tabs';

/**
 * The option currently named in the URL, falling back to the first option.
 *
 * Extracted from the hook as a pure function so the URL contract is testable
 * without a DOM. The contract is small and worth pinning, because it is what
 * decides whether a bookmark, a back-button press, and a legacy redirect all
 * land on the same screen.
 */
export function resolveSub(subs: SubView[], asked: string | null | undefined): string {
  // An unknown option falls back to the first rather than rendering an empty
  // panel: a hand-edited or stale URL should show the tab, not a void.
  return subs.some((s) => s.id === asked) ? (asked as string) : subs[0].id;
}

/**
 * What to put in the URL for an option. The first option is the default, so it
 * is left off entirely — a clean `/node` is a better bookmark than
 * `/node?sub=pulse`, and a default that appears in every copied link is a
 * default that will be wrong the moment the order changes.
 */
export function subParam(subs: SubView[], id: string): string | null {
  return id === subs[0].id ? null : id;
}

export function useSub(tab: TabId, subs: SubView[]): [string, (id: string) => void] {
  const [params, setParams] = useSearchParams();
  const active = resolveSub(subs, params.get('sub'));
  const select = useCallback(
    (id: string) => {
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          const param = subParam(subs, id);
          if (param === null) next.delete('sub');
          else next.set('sub', param);
          return next;
        },
        { replace: false },
      );
    },
    [setParams, subs],
  );
  return [active, select];
}

/**
 * How much chrome the frame draws around its child.
 *
 * `panel` — the sovereign surfaces. Title, purpose, option strip, and a
 * bordered panel. This is the house style.
 *
 * `host` — a platform page that ships its own full-bleed chrome (its own
 * scroll, its own composer, its own side panel). The frame keeps the option
 * strip — it must, or the tab's other options become unreachable — and then
 * gets out of the way. Wrapping the platform chat in a padded bordered box
 * would put a second padding and a second scrollbar around a layout designed
 * to fill the window, and the result is a page that looks trapped in a card.
 */
export type TabVariant = 'panel' | 'host';

export function TabFrame({
  tab,
  subs,
  active,
  onSelect,
  title,
  lede,
  children,
  aside,
  variant = 'panel',
}: {
  tab: TabId;
  subs: SubView[];
  active: string;
  onSelect: (sub: string) => void;
  title: string;
  lede?: string;
  children: ReactNode;
  aside?: ReactNode;
  variant?: TabVariant;
}) {
  const host = variant === 'host';
  const strip = (
    <div className={host ? 'px-3 pt-2.5' : 'mt-3'}>
      <SubTabs tab={tab} subs={subs} active={active} onSelect={onSelect} />
    </div>
  );

  // tabIndex=0 on the panel so a keyboard user can scroll a long option
  // without tabbing through every control inside it first.
  const panel = (
    <div
      role="tabpanel"
      id={`subpanel-${tab}-${active}`}
      aria-labelledby={`sub-${tab}-${active}`}
      tabIndex={0}
      className={
        host
          ? 'flex-1 min-h-0 flex flex-col'
          : 'rounded-xl border p-4 min-h-0'
      }
      style={host ? undefined : { borderColor: 'var(--s-line)', background: 'var(--s-surface)' }}
    >
      {children}
    </div>
  );

  if (host) {
    return (
      <div className="flex-1 min-h-0 flex flex-col">
        {strip}
        {panel}
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto min-h-0">
      <div className="max-w-5xl mx-auto px-5 py-5">
        <header className="mb-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="min-w-0">
              <h1 className="text-lg font-semibold" style={{ color: 'var(--s-ink)' }}>
                {title}
              </h1>
              {lede && (
                <p className="text-[13px] mt-1 max-w-2xl" style={{ color: 'var(--s-mut)' }}>
                  {lede}
                </p>
              )}
            </div>
            {aside}
          </div>
          {strip}
        </header>
        {panel}
      </div>
    </div>
  );
}
