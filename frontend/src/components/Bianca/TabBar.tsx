/**
 * The five-tab bar, and the segmented control for a tab's options.
 *
 * Keyboard parity is the floor for an enterprise tool, not a nicety: the
 * sovereign face already promises roving tabindex, arrow keys, Home and End.
 * If this surface shipped pointer-only navigation, "coherent" would mean
 * coherent-looking and nothing else.
 */

import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router';
import type { KeyboardEvent } from 'react';
import { TABS } from './tabs';
import type { SubView, TabId } from './tabs';

export function TabBar({
  active,
  onSelect,
}: {
  active: TabId;
  onSelect: (id: TabId) => void;
}) {
  const navigate = useNavigate();
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});

  // Roving tabindex: exactly one tab is tabbable, and the arrows move within
  // the row. Two tabbable tabs would put two stops in the tab order for one
  // widget, which is the classic tab-bar accessibility bug.
  const move = (from: number, delta: number) => {
    const next = (from + delta + TABS.length) % TABS.length;
    const t = TABS[next];
    onSelect(t.id);
    requestAnimationFrame(() => refs.current[t.id]?.focus());
  };

  const onKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number) => {
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        move(index, 1);
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        move(index, -1);
        break;
      case 'Home':
        e.preventDefault();
        move(0, 0);
        break;
      case 'End':
        e.preventDefault();
        move(TABS.length - 1, 0);
        break;
      default:
    }
  };

  return (
    <div
      role="tablist"
      aria-label="Bianca — die fünf Stimmen des Knotens"
      className="flex items-stretch gap-0 overflow-x-auto"
      style={{ scrollbarWidth: 'none' }}
    >
      {TABS.map((t, i) => {
        const selected = t.id === active;
        const Icon = t.icon;
        return (
          <button
            key={t.id}
            ref={(el) => {
              refs.current[t.id] = el;
            }}
            role="tab"
            id={`tab-${t.id}`}
            aria-selected={selected}
            aria-controls={`tabpanel-${t.id}`}
            tabIndex={selected ? 0 : -1}
            onKeyDown={(e) => onKeyDown(e, i)}
            onClick={() => {
              onSelect(t.id);
              navigate(t.path);
            }}
            title={t.hint}
            className="relative flex flex-col items-start gap-0.5 px-4 py-2.5 shrink-0 cursor-pointer transition-colors"
            style={{
              background: 'transparent',
              border: 'none',
              borderBottom: `2px solid ${selected ? 'var(--s-gold)' : 'transparent'}`,
              color: selected ? 'var(--s-ink)' : 'var(--s-mut)',
              minWidth: 0,
            }}
          >
            <span className="flex items-center gap-2 whitespace-nowrap">
              <Icon size={15} style={{ color: selected ? 'var(--s-gold)' : 'inherit' }} aria-hidden />
              <span className="text-[13px] font-medium whitespace-nowrap">{t.label}</span>
            </span>
            <span className="text-[10px] whitespace-nowrap" style={{ color: 'var(--s-mut-2)' }}>
              {t.hint}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export function SubTabs({
  tab,
  subs,
  active,
  onSelect,
}: {
  tab: TabId;
  subs: SubView[];
  active: string;
  onSelect: (sub: string) => void;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const index = Math.max(
    0,
    subs.findIndex((s) => s.id === active),
  );

  const move = (from: number, delta: number) => {
    const next = (from + delta + subs.length) % subs.length;
    onSelect(subs[next].id);
    requestAnimationFrame(() => refs.current[subs[next].id]?.focus());
  };

  const onKeyDown = (e: KeyboardEvent<HTMLButtonElement>, i: number) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      move(i, 1);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      move(i, -1);
    } else if (e.key === 'Home') {
      e.preventDefault();
      move(0, 0);
    } else if (e.key === 'End') {
      e.preventDefault();
      move(subs.length - 1, 0);
    }
  };

  return (
    <div role="tablist" aria-label={`${tab} — Optionen`} className="flex items-center gap-1 flex-wrap">
      {subs.map((s, i) => {
        const selected = s.id === active;
        return (
          <button
            key={s.id}
            ref={(el) => {
              refs.current[s.id] = el;
            }}
            role="tab"
            id={`sub-${tab}-${s.id}`}
            aria-selected={selected}
            aria-controls={`subpanel-${tab}-${s.id}`}
            tabIndex={selected ? 0 : -1}
            onKeyDown={(e) => onKeyDown(e, i)}
            onClick={() => onSelect(s.id)}
            title={s.hint}
            className="px-3 py-1 rounded-full text-[12px] cursor-pointer transition-colors"
            style={{
              border: `1px solid ${selected ? 'color-mix(in srgb, var(--s-gold) 55%, transparent)' : 'var(--s-line)'}`,
              background: selected
                ? 'color-mix(in srgb, var(--s-gold) 14%, transparent)'
                : 'transparent',
              color: selected ? 'var(--s-gold)' : 'var(--s-mut)',
              fontWeight: selected ? 600 : 400,
            }}
          >
            {s.label}
            {s.platform && (
              <span className="ml-1.5 text-[10px]" style={{ color: 'var(--s-mut-2)' }} title="Bestehende Plattform-Seite">
                ●
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
