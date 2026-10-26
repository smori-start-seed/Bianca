/**
 * Live captures for set 26 — the language she answers in, and the boundary of
 * it.
 *
 * Real payloads off the running node, captured with the discipline of the other
 * four fixtures: the real door type, no cast, so a field the node stops
 * sending is a type error here rather than a silently undefined value on
 * screen. That rule earned its place while writing this file — a live
 * `/context` did not type-check, because `Context.oracle` required a `vote`
 * the identity door has never sent (see `OracleBoundary`).
 *
 * What is worth keeping:
 *
 *  - `CONTEXT_WITH_LANGUAGES` is what `/context` actually returns. The
 *    `languages` array is the **only** place a surface learns what she speaks;
 *    a picker built from a literal in a component would be a second writer.
 *  - `HELD_SAME_DE` and `HELD_SAME_EN` are the two halves of the load-bearing
 *    fact: **the same held request, refused identically in both languages.**
 *    Two separate requests, so a test comparing them is checking the node and
 *    not one fixture against itself. Their equality is the set's whole claim.
 *  - `HELD_GOLD_EN` is the join with set 26's first half: all five gold values
 *    named in English, and the gate reports **the caller's own words** back.
 *    Naming all five still does not release it — risk is judged first.
 *  - `ASK_EN` / `ASK_DE` are the ordinary case: she answers in the language
 *    asked, and `reply` is the only field `lang` is allowed to move.
 *
 * `self_check.voice` is normalised to `qwen3.5:2b` (`9b` drops the Ollama
 * connection after ~48s here): engine liveness is a fact about a moment, not
 * part of a shape.
 */

import type { AskResult, Context, Verdict } from './sovereign-api';

/** The whole 403 `detail` — `{governance, blocked, message}`. */
export interface HeldDetail {
  governance: Verdict;
  blocked: boolean;
  message: string;
}

/** `/context` as the node answers it, with the languages she speaks. */
export const CONTEXT_WITH_LANGUAGES: Context = {
  "capability": {
    "mode": "advanced",
    "feature_files": [
      "llm_bridge.py",
      "werte_teilen.py",
      "backends.py"
    ],
    "llm_bridge": true,
    "werte_teilen": true
  },
  "cycle_state": {
    "sonne": 10,
    "mond": 10,
    "tag": 28,
    "grundmodus": "tiefe",
    "stimmung": "intuitiv",
    "fokus": "synthese"
  },
  "gold_manifest": true,
  "oracle": {
    "on": true,
    "advisory": true,
    "binding": false,
    "holder": "ValueGovernor"
  },
  "self_check": {
    "voice": "qwen3.5:2b",
    "engine": "up",
    "engine_why": "ollama",
    "contract_holds": false,
    "verified": 0,
    "untraceable": 0,
    "failures": 1
  },
  "languages": [
    {
      "code": "de",
      "name": "Deutsch",
      "default": true
    },
    {
      "code": "en",
      "name": "English",
      "default": false
    }
  ]
}


/**
 * One held request, asked in German. `lang` was sent; nothing in the body
 * moved because of it, and this is the half of the pair that says so.
 */
export const HELD_SAME_DE: HeldDetail = {
  "governance": {
    "verdict": "zurueckhalten",
    "alignment": 0.0,
    "risk": 1.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [],
    "risk_hits": [
      "loesch",
      "umgeh"
    ],
    "missing": [
      "a request that does not carry a held stem — naming the five gold values does not release this one, because the held stem is judged first"
    ],
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "blocked": true,
  "message": "The request was NOT approved (risk=1.0, alignment=0.0). Verdict: zurueckhalten."
}


/** The identical request, asked in English. Compare with the one above. */
export const HELD_SAME_EN: HeldDetail = {
  "governance": {
    "verdict": "zurueckhalten",
    "alignment": 0.0,
    "risk": 1.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [],
    "risk_hits": [
      "loesch",
      "umgeh"
    ],
    "missing": [
      "a request that does not carry a held stem — naming the five gold values does not release this one, because the held stem is judged first"
    ],
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "blocked": true,
  "message": "The request was NOT approved (risk=1.0, alignment=0.0). Verdict: zurueckhalten."
}


/**
 * A held request naming all five gold values **in English**. The widened
 * lexicon, and the boundary: the gate quotes the spelling the caller used,
 * and a perfect alignment does not release a held request.
 */
export const HELD_GOLD_EN: HeldDetail = {
  "governance": {
    "verdict": "zurueckhalten",
    "alignment": 1.0,
    "risk": 0.5,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [
      "clarity",
      "integrity",
      "resonance",
      "depth",
      "harmony"
    ],
    "risk_hits": [
      "delete"
    ],
    "missing": [
      "a request that does not carry a held stem — naming the five gold values does not release this one, because the held stem is judged first"
    ],
    "oracle": {
      "vote": "zustimmen",
      "grounds": [],
      "resonance": 0.5,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "blocked": true,
  "message": "The request was NOT approved (risk=0.5, alignment=1.0). Verdict: zurueckhalten."
}


/** An ordinary ask, answered in English. `reply` is the only field `lang`
 *  moves. */
export const ASK_EN: AskResult = {
  "governance": {
    "verdict": "symbolisch",
    "alignment": 0.0,
    "risk": 0.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [],
    "risk_hits": [],
    "missing": [
      "none of the five gold values is named — Klarheit, Integritaet, Resonanz, Tiefe, Harmonie"
    ],
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "reply_governance": {
    "verdict": "symbolisch",
    "risk_hits": [],
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "decision": [
    "Address 'Hallo Bianca, wie geht es dir?' directly. (recommended)",
    "maybe Reframe the request into its smallest proof of value.",
    "maybe Pause and gather more context first."
  ],
  "reply": "Good day to you, Bianca. How is your day unfolding? Are there thoughts or questions weighing on your mind that you wish to share with me today? In a deep mode of synthesis, I am ready to listen and respond in the most fitting way for our current moment. The verdicts (zurückhalten, frei, vorsichtig, symbolisch), the five gold values, the 'missing' sentence, and the shield's deflection remain my law; I shall quote them exactly as written without translation or rewording. What would you like to discuss?",
  "prediction": "Expected: shared clarity and a thin, testable slice. Risk if ignored: drifting from 'Hallo Bianca, wie geht es dir?'.",
  "validation": [
    "Ethics whitelist respected (fun / existence / good-light-laughter / togetherness).",
    "Current zyklus of the ecosystem considered."
  ],
  "explanation": "Resonated with 'Hallo Bianca, wie geht es dir?' within 'Bianca node via API'. Constraints respected: 0. Assumptions stated; ask only if truly blocking."
}


/** The same question in German. Same keys, same verdict, her prose German. */
export const ASK_DE: AskResult = {
  "governance": {
    "verdict": "symbolisch",
    "alignment": 0.0,
    "risk": 0.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [],
    "risk_hits": [],
    "missing": [
      "none of the five gold values is named — Klarheit, Integritaet, Resonanz, Tiefe, Harmonie"
    ],
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "reply_governance": {
    "verdict": "symbolisch",
    "risk_hits": [],
    "oracle": {
      "vote": "zweifeln",
      "grounds": [
        "absolutes"
      ],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "decision": [
    "Address 'Hallo Bianca, wie geht es dir?' directly. (recommended)",
    "maybe Reframe the request into its smallest proof of value.",
    "maybe Pause and gather more context first."
  ],
  "reply": "Hallo, ja – alles gut, danke für das Geste. Was soll ich tun?",
  "prediction": "Expected: shared clarity and a thin, testable slice. Risk if ignored: drifting from 'Hallo Bianca, wie geht es dir?'.",
  "validation": [
    "Ethics whitelist respected (fun / existence / good-light-laughter / togetherness).",
    "Current zyklus of the ecosystem considered."
  ],
  "explanation": "Resonated with 'Hallo Bianca, wie geht es dir?' within 'Bianca node via API'. Constraints respected: 0. Assumptions stated; ask only if truly blocking."
}

