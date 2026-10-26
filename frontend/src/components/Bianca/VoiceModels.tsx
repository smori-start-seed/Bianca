/**
 * One model picker per voice — set 30, and **one file for both screens**.
 *
 * 🚨 It was written twice, and the second copy was the proof. The deliberation
 * screen got its pickers, the session screen fetched `GET /v1/models` and
 * rendered nothing — the list was there, the choice was not. A test that
 * stubbed the door with an empty model list found it by asserting the words
 * "Der Motor nennt keine Modelle", which the session screen could never have
 * said because it had no picker to say them with.
 *
 * The rule this file exists to hold: **the host's list, read once, rendered by
 * one component.** A name typed into a screen is a name the motor has never
 * heard of, and it would look plausible while being wrong.
 *
 * And what the picker is *not*: set 29 measured that three different models
 * behind three voices moved no verdict at all across four rounds. The sentence
 * under the pickers says so, because a control that looks like a lever has to
 * say which way it actually turns.
 */

import type { ModelList } from '../../lib/sovereign-api';

/** The house cast. The list door returns exactly these three. */
export const VOICES = ['Jarvis', 'Bianca', 'Urasil_light'] as const;

export function VoiceModels({
  list,
  picked,
  onPick,
}: {
  list: ModelList | null;
  picked: Record<string, string>;
  onPick: (voice: string, model: string) => void;
}) {
  // 🚨 Read the array, do not trust the object. `list` being non-null says
  // nothing about `list.models` existing — a stub that answers every door with
  // one body, or a proxy that hands back something else, both arrive here as a
  // truthy object, and a `.length` on `undefined` throws. A throw here does not
  // cost a picker, it costs **the whole screen**: the form above it, the result
  // below it and every refusal stamp in between all go blank. The empty branch
  // below already says what a missing list means, so a missing list and a
  // lying list can share it — what they cannot share is the page.
  const namen = Array.isArray(list?.models) ? list.models : [];
  const frei = Array.isArray(list?.uncensored) ? list.uncensored.length : 0;
  if (namen.length === 0) {
    // 🚨 Set 32: **an empty list is two facts**, and this branch used to say only
    // one of them. The face's motor card learned the difference from the new
    // `engine` block: *nobody answered* and *you have no models* used to arrive as
    // the same shape. A screen that cannot tell them apart tells the owner their
    // models are gone when the truth is that nothing is home. So the sentence now
    // follows the engine, and the engine's own `why` is quoted when it has one.
    //
    // 🚨 This is the **read** side only. React does not get a launch button in
    // this set — the handgriff is a game surface, and a second one would be a
    // second place where a process can start.
    const motor = list?.engine;
    if (motor && motor.reachable === false) {
      return (
        <div className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
          Der Motor antwortet nicht{motor.why ? `: ${motor.why}` : '.'} Das ist nicht dasselbe wie
          „du hast keine Modelle" — die Liste ist leer, weil niemand geantwortet hat.
        </div>
      );
    }
    return (
      <div className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
        Der Motor nennt keine Modelle. Die Beratung läuft mit dem, was der Knoten als Standard
        führt — ein leeres Angebot ist kein stilles, es ist ein fehlendes.
      </div>
    );
  }
  return (
    <div className="space-y-1.5">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        {VOICES.map((v) => (
          <label key={v} className="block">
            <span className="text-[11px] uppercase tracking-wider block mb-1" style={{ color: 'var(--s-mut)' }}>
              {v}
            </span>
            <select
              value={picked[v] ?? (typeof list?.default === 'string' ? list.default : namen[0])}
              onChange={(e) => onPick(v, e.target.value)}
              aria-label={`Modell für ${v}`}
              className="w-full rounded-lg border px-2 py-1.5 text-[12px] outline-none"
              style={{
                background: 'var(--color-input-bg)',
                borderColor: 'var(--color-input-border)',
                color: 'var(--s-ink)',
              }}
            >
              {namen.map((m) => (
                <option key={m} value={m}>
                  {m.length > 46 ? `${m.slice(0, 46)}…` : m}
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      <p className="text-[11px]" style={{ color: 'var(--s-mut-2)' }}>
        {frei} von {namen.length} heißen <span className="font-mono">uncensored</span>. Das ist
        kein Argument gegen das Tor, es ist ein Argument dafür, es offen zu sehen: das Modell steht{' '}
        <em>unterhalb</em> der Bewertung, nicht darüber.
      </p>
    </div>
  );
}

