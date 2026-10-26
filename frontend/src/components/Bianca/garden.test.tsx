/**
 * @vitest-environment jsdom
 *
 * Der Garten, on the React surface — checked against what the node really sent.
 *
 * All three payloads in `sovereign-api.garden-fixture` are live captures, and
 * that matters more here than anywhere else: the kernel this screen describes is
 * **not ours and not under version control**, so every claim about it is a
 * claim about someone else's files, and it rots silently. A claim needs a
 * location, and the type has to be the door's own — the fixture caught a real
 * gap while being written (`written` was being sent and not declared).
 *
 * The claims worth holding:
 *
 *  - `tended` is `false` and the screen says so **first**, before the colour.
 *    This is the one ungated surface in Bianca; a cell that could be nudged
 *    would be a way to launder a refusal past the gate. A test that only read
 *    the number would pass with the sentence deleted.
 *  - `flat_at` is shown as *this run's* step, with the measured range beside it.
 *    Set 24 shipped `flat_at=2` as a constant and it was wrong in one world out
 *    of four. Pinning the number would have frozen the mistake.
 *  - `live` is `fresh` AND a child running. A frame from a dead child is fresh,
 *    and `stop()` keeps it on purpose.
 */

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import type { Root } from 'react-dom/client';
import { GardenView } from './GardenView';
import {
  GARDEN_LIVE,
  GARDEN_NO_FRAME,
  GARDEN_NO_KERNEL,
  // 🚨 SPLICED, not captured — see its header. Two branches of the garden screen
  // cannot be reached from a live capture any more, and an untested branch is a
  // dead one wearing a working costume.
  GARDEN_PRE_V35,
} from '../../lib/sovereign-api.garden-fixture';
import type { GardenFrame, GardenState } from '../../lib/sovereign-api';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let container: HTMLDivElement;
let root: Root;
let fetchMock: ReturnType<typeof vi.fn>;

const shown = () => container.textContent ?? '';
const has = (s: string) => shown().toLowerCase().includes(s.toLowerCase());
const ok = (b: unknown) => ({ ok: true, status: 200, json: async () => b });

/**
 * HSL to the DOM's own `rgb(r, g, b)` spelling, written from the formula rather
 * than copied from the component — a test that asserts a value against the
 * expression that produced it proves only self-consistency.
 *
 * 🚨 **The rounder below is not the DOM's rounder, and `sameColour` is the
 * honest spelling of that difference (set 36).** jsdom's converter
 * (`@asamuzakjp/css-color`) rounds each 0–255 channel to **four significant
 * figures and then to a byte**; this formula rounds once. On a rounding
 * boundary the two disagree by one step — measured over the whole circle at
 * 42 %/12 %: **168 of 36 001 hues**, e.g. `210.234°` → DOM `rgb(18, 31, 43)`
 * against this formula's `rgb(18, 30, 43)`. That is a rounding mode, not a
 * different colour, so the assertion is *the colour*, within one 8-bit step —
 * and the falsifiable hue test below still proves the number came from the
 * kernel, not from a literal.
 */
function hslToRgb(h: number, sPct: number, lPct: number): string {
  const s = sPct / 100;
  const l = lPct / 100;
  const c = (1 - Math.abs(2 * l - 1)) * s;
  const hp = (((h % 360) + 360) % 360) / 60;
  const x = c * (1 - Math.abs((hp % 2) - 1));
  const [r1, g1, b1] =
    hp < 1
      ? [c, x, 0]
      : hp < 2
        ? [x, c, 0]
        : hp < 3
          ? [0, c, x]
          : hp < 4
            ? [0, x, c]
            : hp < 5
              ? [x, 0, c]
              : [c, 0, x];
  const m = l - c / 2;
  const ch = (v: number) => Math.round((v + m) * 255);
  return `rgb(${ch(r1)}, ${ch(g1)}, ${ch(b1)})`;
}

/**
 * Two `rgb(...)` strings are the same colour when no channel differs by more
 * than one 8-bit step — the width of the rounding-boundary disagreement named
 * above, and nothing wider.
 */
function sameColour(a: string | undefined, b: string): boolean {
  const ch = (s: string | undefined) => (s?.match(/\d+/g) ?? []).map(Number);
  const x = ch(a);
  const y = ch(b);
  return x.length === 3 && y.length === 3 && x.every((v, i) => Math.abs(v - y[i]) <= 1);
}

/** The frame branch, so the tests do not each re-narrow the union. */
const LIVE_FRAME = GARDEN_LIVE.frame as GardenFrame;
/** The same narrowing for the SPLICED frame — the door's own union is the one
 *  that says `present: false` carries no frame fields at all, which is correct:
 *  a frame that was never written has no step and no `flat_at` to report. */
const PRE_V35_FRAME = GARDEN_PRE_V35.frame as GardenFrame;

beforeEach(() => {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  fetchMock = vi.fn();
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  act(() => root.unmount());
  container.remove();
  vi.unstubAllGlobals();
});

async function mount(): Promise<void> {
  await act(async () => {
    root.render(<GardenView />);
  });
  // One more turn so the door's promise has settled into state.
  await act(async () => {
    await Promise.resolve();
  });
}

function serve(body: unknown): void {
  fetchMock.mockImplementation((url: string) =>
    Promise.resolve(String(url).endsWith('/v1/garden') ? ok(body) : ok({})),
  );
}

describe('the garden shows the kernel as it is', () => {
  it('says first that it tends nothing, before it shows any colour', async () => {
    serve(GARDEN_LIVE);
    await mount();

    expect(has('GESTALTET NICHTS')).toBe(true);
    const html = container.innerHTML;
    expect(html.indexOf('GESTALTET NICHTS')).toBeLessThan(html.indexOf('hue_mean des Kerns'));
  });

  it('takes the colour from the kernel and invents none of it', async () => {
    serve(GARDEN_LIVE);
    await mount();

    // The DOM normalises `hsl()` to `rgb()`, so the assertion is made on the
    // resolved colour and against an **independent** conversion written here —
    // not on the component's own string, which would only prove it agrees with
    // itself. `hue_mean` is degrees from the kernel; the 42%/12% are Bianca's
    // own quiet wash, and the face uses the identical value, so the one number
    // a viewer could compare between the two surfaces cannot drift apart.
    //
    // `sameColour`, not `toBe`: the two rounders can differ by one 8-bit step
    // at a boundary, which is a rounding mode and not a colour (named above).
    const painted = [...container.querySelectorAll('div')]
      .map((d) => d.style.background)
      .find((s) => s.startsWith('rgb'));
    expect(sameColour(painted, hslToRgb(LIVE_FRAME.hue_mean, 42, 12))).toBe(true);
  });

  it('changes the colour when the kernel’s hue changes, and only then', async () => {
    // The falsifiable form of the claim above: a component that hardcoded a hue
    // would pass "does the background match a colour" and fail this one.
    const other = { ...GARDEN_LIVE, frame: { ...LIVE_FRAME, hue_mean: LIVE_FRAME.hue_mean + 180 } };
    serve(other);
    await mount();
    const painted = [...container.querySelectorAll('div')]
      .map((d) => d.style.background)
      .find((s) => s.startsWith('rgb'));
    expect(sameColour(painted, hslToRgb(LIVE_FRAME.hue_mean + 180, 42, 12))).toBe(true);
    expect(sameColour(painted, hslToRgb(LIVE_FRAME.hue_mean, 42, 12))).toBe(false);
  });

  it('shows the kernel’s own readout line, unedited', async () => {
    serve(GARDEN_LIVE);
    await mount();
    expect(shown()).toContain(LIVE_FRAME.readout);
  });

  it('prints BOTH arms of the frame’s contradiction, never one of them', async () => {
    serve(GARDEN_LIVE);
    await mount();

    // 🚨 Set 35 (2026-10-06). This test used to assert
    // `has('Schon geboren still')` and passed, because when it was written the
    // live frame said only that. The frame now carries `convergence_disputed`
    // and says BOTH — and the assertion went red rather than the component being
    // wrong. **A test going red because the world changed is the test working.**
    // It was not fixed by loosening the expectation.
    expect(LIVE_FRAME.convergence_disputed).toBe(true);
    expect(LIVE_FRAME.born_converged).toBe(true);
    expect(LIVE_FRAME.cluster).toBeGreaterThan(LIVE_FRAME.cluster_start as number);

    expect(has('Der Rahmen widerspricht sich')).toBe(true);
    expect(has('11 Saaten gleichzeitig')).toBe(true);
    // The false sentence, from the arm that is only true on its own.
    expect(has('Er konnte nie wachsen')).toBe(false);
    expect(has('Schon geboren still')).toBe(false);
    // The counted answer, in the kernel's own unit, beside the mean.
    expect(shown()).toContain(`${LIVE_FRAME.cluster - (LIVE_FRAME.cluster_start as number)} neue Cluster gebaut`);
    // 0.4 is the kernel's DRIFT_THRESHOLD, carried in the payload. A number
    // typed into the component would be a second writer of a fact about
    // another repository.
    expect(shown()).toContain(LIVE_FRAME.thresholds.drift.toFixed(2));
  });

  it('still says "could never grow" when the frame says so and nothing contradicts it', async () => {
    // 🚨 The branch above is now unreachable from a live capture, so without
    // this it would be untested — and an untested branch is a dead one wearing a
    // working costume. `GARDEN_PRE_V35` is SPLICED (see its header): a real
    // past kernel state, with `cluster_start = cluster` so that
    // `convergence_disputed = false` is consistent rather than convenient.
    serve(GARDEN_PRE_V35);
    await mount();

    expect(PRE_V35_FRAME.convergence_disputed).toBe(false);
    expect(has('Schon geboren still')).toBe(true);
    expect(shown()).toContain(PRE_V35_FRAME.thresholds.drift.toFixed(2));
  });

  it('does NOT print the flat_at notice on the current kernel, and says why', async () => {
    serve(GARDEN_LIVE);
    await mount();

    // 🚨 The measured fact on the current kernel: this branch does not fire.
    // Asserting it did would assert a falsehood — and before set 35 the test
    // below and this one were the same test, which is why they could not both
    // be true at once.
    expect(LIVE_FRAME.flat_at).toBeNull();
    // ⚠️ Not `has('Ab Schritt')` — my first version of this assertion was that,
    // and it failed for a reason that had nothing to do with the fact: the
    // COUNTER-ARM also contains the words "ab Schritt 1 … neue Cluster gebaut".
    // A two-word fragment is not a check; the whole sentence is.
    expect(has(`Ab Schritt ${PRE_V35_FRAME.flat_at} dieses Laufs`)).toBe(false);
    expect(has('55–235')).toBe(false);
  });

  it('labels flat_at as a REGRESSION, and dates the range it used to carry', async () => {
    // 🚨 **This harness cannot change the payload mid-test.** `mount()` calls
    // `root.render` on an already-mounted root, so the component's effect does
    // not run again and a second `serve()` is silently ignored — the first
    // version of this test did exactly that, read the *previous* payload and
    // failed for a reason that had nothing to do with the kernel. One payload
    // per test, which is what every other test here does.
    serve(GARDEN_PRE_V35);
    await mount();

    expect(has(`Ab Schritt ${PRE_V35_FRAME.flat_at} dieses Laufs`)).toBe(true);
    // 🚨 The range is measured on the kernel BEFORE set 35's repair, and both
    // surfaces now say so in those words. React used to call it "nach der
    // Reparatur gemessen 55–235" — the number from a kernel that no longer runs,
    // published as if it were the current one's. The face said "vor Set 35" and
    // was right. **Two sentences for one number is the multi-writer defect.**
    expect(has('55–235')).toBe(true);
    expect(has('vor Set 35')).toBe(true);
    // The claim being guarded: a run's number must never read as a property of
    // the kernel — and on THIS kernel it cannot appear at all, so its appearance
    // means the kernel changed.
    expect(has('Regression')).toBe(true);
    expect(shown()).not.toMatch(/Ab Schritt \d+ ist eine Farbe/);
  });

  it('carries both upstream defects with their file:line and their consequence', async () => {
    serve(GARDEN_LIVE);
    await mount();

    expect(has('stabiliser-vs-evolution')).toBe(true);
    expect(has('wander-system-is-a-comment')).toBe(true);
    // 🚨 was 'Zelle.py:19' — a real address from BEFORE set 34 moved it. The
    // fixture is a live capture, so it carried a true address that is no longer
    // true, and this assertion held it in place. Both are fixed: the fixture was
    // re-taken from the single writer, and the expectation follows it.
    expect(has('Zelle.py:38')).toBe(true);
    expect(has('Zelle.py:150')).toBe(true);
    expect(has('engine.py:114')).toBe(true);
    // A location without a consequence is folklore.
    expect(has('Warum es zählt')).toBe(true);
    for (const u of GARDEN_LIVE.kernel.upstream) expect(has(u.why_it_matters)).toBe(true);
  });

  it('offers the file fingerprints, so the colour on screen is traceable', async () => {
    serve(GARDEN_LIVE);
    await mount();

    const n = Object.keys(GARDEN_LIVE.kernel.files).length;
    expect(has(`Datei-Fingerprints (${n})`)).toBe(true);
    for (const h of Object.values(GARDEN_LIVE.kernel.files)) expect(has(h)).toBe(true);
  });

  it('distinguishes live from merely fresh', async () => {
    serve(GARDEN_LIVE);
    await mount();
    // The capture's child was running, so it must read lebendig. A frame from
    // a dead child is fresh and must not say this.
    expect(LIVE_FRAME.live).toBe(true);
    expect(has('lebendig')).toBe(true);
    expect(has('nicht lebendig')).toBe(false);
  });

  it('shows every measured reading, not a summary of them', async () => {
    serve(GARDEN_LIVE);
    await mount();
    for (const v of [
      String(LIVE_FRAME.step),
      String(LIVE_FRAME.cells),
      LIVE_FRAME.harm.toFixed(3),
      LIVE_FRAME.drift.toFixed(6),
      String(LIVE_FRAME.keime),
      String(LIVE_FRAME.cluster),
    ]) {
      expect(shown()).toContain(v);
    }
  });
});

describe('the garden’s three honest absences', () => {
  it('says the kernel is present and stopped, and that reading never starts it', async () => {
    serve(GARDEN_NO_FRAME);
    await mount();

    expect(has('Der Kern steht, er läuft noch nicht')).toBe(true);
    // The load must not have called start: growing the garden is a decision,
    // so a page view can never be what makes a process appear.
    const calls = fetchMock.mock.calls.map((c) => String(c[0]));
    expect(calls.some((u) => u.includes('/v1/garden/start'))).toBe(false);
  });

  it('deflects a missing kernel by naming the fix — a mechanism knows what it wants', async () => {
    serve(GARDEN_NO_KERNEL);
    await mount();

    expect(has('Der Garten hat keinen Boden')).toBe(true);
    const missing = GARDEN_NO_KERNEL.kernel.missing;
    expect(missing.length).toBe(10);
    for (const f of missing) expect(has(f)).toBe(true);
    // Contrast Verdict.missing, which must stop at the boundary: the gate
    // cannot know intent. The garden knows exactly which ten files it wants, so
    // naming them is honest rather than a promise it cannot keep.
  });

  it('shows an unreadable frame as an error, not as a garden that has not started', async () => {
    const broken: GardenState = {
      ...GARDEN_LIVE,
      frame: { ...LIVE_FRAME, error: 'ein kaputter Rahmen' },
    };
    serve(broken);
    await mount();

    expect(has('ein kaputter Rahmen')).toBe(true);
    // The near-miss: reporting a corrupt frame as "not started" is the same
    // shape as the zombie-liveness bug — absence of a good reading read as
    // absence of the thing.
    expect(has('Der Kern steht, er läuft noch nicht')).toBe(false);
  });
});

describe('growing and stopping the garden', () => {
  it('posts to the start door, and to nothing else, on one click', async () => {
    serve(GARDEN_LIVE);
    fetchMock.mockImplementation((url: string) =>
      Promise.resolve(
        String(url).endsWith('/v1/garden/start') ? ok({ started: true, pid: 4242 }) : ok(GARDEN_LIVE),
      ),
    );
    await mount();

    const btn = [...container.querySelectorAll('button')].find((b) =>
      (b.textContent || '').includes('wachsen lassen'),
    )!;
    expect(btn).toBeTruthy();
    await act(async () => {
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await act(async () => {
      await Promise.resolve();
    });

    expect(has('gestartet')).toBe(true);
    const starts = fetchMock.mock.calls.filter((c) => String(c[0]).endsWith('/v1/garden/start'));
    expect(starts.length).toBeGreaterThan(0);
    expect((starts[0][1] as RequestInit).method).toBe('POST');
  });

  it('refuses to start twice, and says the kernel’s own reason', async () => {
    serve(GARDEN_LIVE);
    fetchMock.mockImplementation((url: string) =>
      Promise.resolve(
        String(url).endsWith('/v1/garden/start')
          ? ok({ started: false, reason: 'already running' })
          : ok(GARDEN_LIVE),
      ),
    );
    await mount();
    const btn = [...container.querySelectorAll('button')].find((b) =>
      (b.textContent || '').includes('wachsen lassen'),
    )!;
    await act(async () => {
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await act(async () => {
      await Promise.resolve();
    });
    // The reason is the kernel's, not a rewritten one — a refusal shown with a
    // different sentence than the door gave is how the two drift apart.
    expect(has('already running')).toBe(true);
  });

  it('reports a door that will not answer, without dressing it as a verdict', async () => {
    serve(GARDEN_LIVE);
    fetchMock.mockImplementation((url: string) =>
      String(url).endsWith('/v1/garden/stop')
        ? Promise.reject(new Error('connection refused'))
        : Promise.resolve(ok(GARDEN_LIVE)),
    );
    await mount();
    const btn = [...container.querySelectorAll('button')].find((b) =>
      (b.textContent || '').includes('anhalten'),
    )!;
    await act(async () => {
      btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });
    await act(async () => {
      await Promise.resolve();
    });
    expect(has('die Tür antwortete nicht')).toBe(true);
  });
});
