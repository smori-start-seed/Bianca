/**
 * Loading a door, with the three refusals handled once.
 *
 * Every sovereign page faces the same three ways a door can say no — refused,
 * engine down, or broken — and if each page invents its own handling, one of
 * them will eventually render a dead engine as an empty answer. So the
 * handling lives here, and the pages only choose what to draw.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  SovereignDenied,
  SovereignEngineDown,
  SovereignInterrupted,
} from '../../lib/sovereign-api';
import type { ShieldDirection, Verdict } from '../../lib/sovereign-api';

export type DoorState<T> =
  | { kind: 'loading' }
  | { kind: 'ready'; data: T }
  // 🚨 `direction` rides along. The door has sent one since set 28 and the parse
  // threw it away until this set's capture caught it, so the field is on the
  // error — and a shared read path that drops it would be the same loss one
  // layer up. Optional, because `/govern` and `/hub/spore` answer without one.
  | { kind: 'denied'; verdict: Verdict; direction?: ShieldDirection }
  | { kind: 'down'; why: string }
  | { kind: 'interrupted'; partial: unknown }
  | { kind: 'error'; message: string };

/**
 * A union plus its reload — declared as a type alias rather than an interface
 * because `DoorState` is a union, and an interface cannot extend one. Getting
 * this wrong fails at every `door.kind` in every page, which is a loud failure;
 * the version of it that would have been quiet is extending a non-union
 * `Partial<...>` and getting `data` typed as possibly-absent on the happy path.
 */
export type Door<T> = DoorState<T> & { reload: () => void };

/**
 * The state of a door that has not delivered. Passed to the shared "not ready"
 * renderer so that renderer can never be handed a payload it has no branch
 * for — the alternative is a function that must return `null` for a case the
 * type system says is impossible, and `null` for an impossible case is a lie
 * that survives exactly until the case becomes possible.
 */
export type DoorPending<T> = Exclude<DoorState<T>, { kind: 'ready' }>;

export function useDoor<T>(load: () => Promise<T>, deps: unknown[] = []): Door<T> {
  const [state, setState] = useState<DoorState<T>>({ kind: 'loading' });
  const [nonce, setNonce] = useState(0);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setState({ kind: 'loading' });
    load()
      .then((data) => {
        if (!cancelled && alive.current) setState({ kind: 'ready', data });
      })
      .catch((e: unknown) => {
        if (cancelled || !alive.current) return;
        if (e instanceof SovereignDenied)
          setState({ kind: 'denied', verdict: e.verdict, direction: e.direction });
        else if (e instanceof SovereignInterrupted) setState({ kind: 'interrupted', partial: e.partial });
        else if (e instanceof SovereignEngineDown) setState({ kind: 'down', why: e.why });
        else setState({ kind: 'error', message: (e as Error)?.message ?? String(e) });
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  return { ...state, reload } as Door<T>;
}
/**
 * Seconds since a write started, ticking once a second.
 *
 * A local model can take a minute and a half here. A spinner with no number
 * is indistinguishable from a hung browser; a number is patience.
 */
export function useElapsed(running: boolean): number {
  const [seconds, setSeconds] = useState(0);
  const started = useRef<number>(0);

  useEffect(() => {
    if (!running) {
      setSeconds(0);
      return;
    }
    started.current = Date.now();
    setSeconds(0);
    const id = window.setInterval(
      () => setSeconds(Math.round((Date.now() - started.current) / 1000)),
      1000,
    );
    return () => window.clearInterval(id);
  }, [running]);

  return seconds;
}
