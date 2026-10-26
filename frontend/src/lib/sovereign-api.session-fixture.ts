/**
 * Live captures of the working session (set 30) — the ground truth the session
 * screens are checked against.
 *
 * Every constant below is a real payload from a running node, and every one was
 * captured off :8713 with `BIANCA_LEDGER_DIR` pointed at a throwaway ledger, so
 * this file's history is the history of a throwaway node and not of the owner's.
 * The file carries **no cast**: each constant is annotated with the door's own
 * type, which is the only thing that makes a capture a check rather than a
 * decoration.
 *
 * It earned its place three times over, and each time the door was wrong and the
 * type was not:
 *
 *  1. `SessionTurn.model` is `string | null`. A hand-written type said `string`,
 *     because a deliberation turn always has one — and the owner's own turn does
 *     not, so the face printed `undefined` for it on the first run.
 *  2. The *list* door answered `running: 323634` (a pid) while the *detail* door
 *     answered `running: true` in the same field. One name, two types, two
 *     doors, and no screen could be written once. `running` is now a boolean and
 *     the pid has its own field.
 *  3. A second `POST …/accept` on an already-closed session answered **200** and
 *     wrote a third line to `proposals.jsonl`, because the filter read "not
 *     closed" and the file's earlier *open* line for the same round was still in
 *     the list. `read_proposals` now collapses one form per round and the door
 *     answers 409 with the existing close and its author.
 *
 * Captured 2026-09-29. `SESSION_LIVE` and `SESSION_AWAITING` are two real runs on
 * `qwen3.5:2b`; the accepted one is a session in which all three voices held
 * `frei`, so the team's proposal fired and the owner took it.
 */

import type {
  HeldBody,
  ModelList,
  SessionAcceptResult,
  SessionCriteria,
  SessionDetail,
  SessionList,
  SessionSayResult,
  SessionStartResult,
  SessionStopResult,
} from './sovereign-api';

/**
 * The host's own model list, straight from `GET /v1/models`.
 *
 * 🚨 **Two capture dates, and this fixture says so.** The names below are the
 * set-30 capture (eight models, `codestral:22b` and `mannix/…` among them). The
 * `engine` block was added on 2026-10-01 in set 32 and is a **live capture of its
 * own** off the running node on `127.0.0.1:8712` — never typed by hand, because a
 * hand-written fixture is a fixture that agrees with the type by construction.
 * Re-capturing the whole door today would have deleted the older list, and the
 * list is history. A spliced block with its date named is history plus a
 * measurement; the same block without the date would be a claim about a response
 * that never happened.
 */
export const MODELS_LIVE: ModelList = {
  "models": [
    "codestral:22b",
    "qwen3.5:2b",
    "mannix/gemma4-98e-v6-coder:q4_K_M",
    "tinyrick/Qwen3.8-27B-Ultra-Uncensored-Heretic-Native-MTP-Preserved-GGUF:Q6_K",
    "jikepjikep_16HEX/gemma-4-4b-nightshift-heretic-uncensored-q6:latest",
    "srchmnmichael/Qwen3.8-Uncensored:q4_K_M",
    "virtuanista/lfm2.5-8b-a1b-uncensored:latest",
    "qwen3.5:9b"
  ],
  "default": "qwen3.5:9b",
  "uncensored": [
    "jikepjikep_16HEX/gemma-4-4b-nightshift-heretic-uncensored-q6:latest",
    "srchmnmichael/Qwen3.8-Uncensored:q4_K_M",
    "tinyrick/Qwen3.8-27B-Ultra-Uncensored-Heretic-Native-MTP-Preserved-GGUF:Q6_K",
    "virtuanista/lfm2.5-8b-a1b-uncensored:latest"
  ],
  "note": "the names come from the engine, not from a list in this file",
  /** Live, 2026-10-01, off `127.0.0.1:8712` while the engine was answering. */
  "engine": {
    "key": "ollama",
    "reachable": true,
    "host": "http://localhost:11434",
    "why": null
  }
};

/** The criterion vocabulary, from `GET /v1/sessions/criteria`. */
export const CRITERIA_LIVE: SessionCriteria = {
  "criteria": [
    {
      "name": "owner-accepts",
      "label": "der Eigentümer nimmt den Vorschlag an",
      "closes": "only the owner, through POST /v1/sessions/{id}/accept",
      "proposed_when": "every voice held a gold-aligned verdict in the last round — a condition on the governance record, never a voice's opinion of itself"
    },
    {
      "name": "idle-contract",
      "label": "der Knoten liest den Idle-Vertrag selbst",
      "closes": "the node, when idle.verify_units()['contract_holds']",
      "proposed_when": "never proposed — it is checked, not proposed"
    }
  ],
  "why_only_these": "a free-text criterion would be a judge that nobody built and nobody checked. set 29 measured that three different models change the words and never the verdict, so the model is not the judge either.",
  "the_ceiling_is_not_a_criterion": "a ceiling is a budget in model calls. reaching it closes the session as 'ceiling_reached' and the record says the goal was NOT met."
};

/** `POST /v1/sessions` with `start: false` — and a fourth voice dropped. */
export const START_LIVE: SessionStartResult = {
  "id": "s_20260929_0747_efe0",
  "topic": "Fixture: Start",
  "goal": "G",
  "stop_when": "owner-accepts",
  "ceiling": 9,
  "model": "qwen3.5:9b",
  "models": {
    "Jarvis": "qwen3.5:2b",
    "Bianca": "qwen3.5:2b",
    "Urasil_light": "qwen3.5:2b"
  },
  "voices": [
    "Jarvis",
    "Bianca",
    "Urasil_light"
  ],
  "status": "new",
  "started": "2026-09-29T07:47:25",
  "closed": null,
  "closed_because": null,
  "stop_requested": null,
  "closed_by": null,
  "ready": false,
  "pid": null,
  "running": false
};

/** A closed session: three `frei`, one proposal, taken by the owner. */
export const SESSION_LIVE: SessionDetail = {
  "state": {
    "id": "s_20260929_0744_e67b",
    "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich",
    "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
    "stop_when": "owner-accepts",
    "ceiling": 3,
    "model": "qwen3.5:9b",
    "models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "voices": [
      "Jarvis",
      "Bianca",
      "Urasil_light"
    ],
    "status": "complete",
    "started": "2026-09-29T07:44:32",
    "closed": "2026-09-29T07:45:40",
    "closed_because": "the owner accepted the proposal of round 1",
    "stop_requested": null,
    "closed_by": "owner",
    "ready": true,
    "pid": null,
    "ready_at": "2026-09-29T07:44:32"
  },
  "turns": [
    {
      "round": 1,
      "voice": "Jarvis",
      "at": "2026-09-29T07:44:42",
      "model": "qwen3.5:2b",
      "text": "Welcome, friends. This is a bold start for Klarheit, Integritaet, Resonanz, Tiefe und Harmonie. We w …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 0.7,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Bianca",
      "at": "2026-09-29T07:44:55",
      "model": "qwen3.5:2b",
      "text": "Welcome to mycelium! Let's let each voice shine without forcing it into a mold. Since we're just sta …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "clarity",
        "resonanz",
        "resonance",
        "depth"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 0.5,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Urasil_light",
      "at": "2026-09-29T07:45:15",
      "model": "qwen3.5:2b",
      "text": "Der Mond steigt langsam, ein sanfter Schimmer in der dunklen See. Die Sonne lehnt sich zurück, ihr L …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zweifeln",
        "grounds": [
          "absolutes"
        ],
        "resonance": 0.5,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    }
  ],
  "memory": {
    "rounds": 1,
    "calls": 3,
    "counts": {
      "frei": 3
    },
    "distinct_verdicts": 1,
    "verdicts_moved": false,
    "per_voice_verdicts": {
      "Jarvis": [
        "frei"
      ],
      "Bianca": [
        "frei"
      ],
      "Urasil_light": [
        "frei"
      ]
    },
    "per_voice_models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "gold_carried": {
      "Jarvis": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "Bianca": [
        "klarheit",
        "clarity",
        "resonanz",
        "resonance",
        "depth"
      ],
      "Urasil_light": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ]
    },
    "eye_warned": 0,
    "owner_turns": 0,
    "held_owner_turns": 0,
    "last": {
      "Jarvis": "Welcome, friends. This is a bold start for Klarheit, Integritaet, Resonanz, Tiefe und Harmonie. We w …",
      "Bianca": "Welcome to mycelium! Let's let each voice shine without forcing it into a mold. Since we're just sta …",
      "Urasil_light": "Der Mond steigt langsam, ein sanfter Schimmer in der dunklen See. Die Sonne lehnt sich zurück, ihr L …"
    },
    "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
    "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
  },
  "proposals": [
    {
      "round": 1,
      "at": "2026-09-29T07:45:15",
      "trigger": "every voice held a gold-aligned verdict in the last round — a condition on the governance record, not any voice's opinion of itself",
      "evidence": {
        "rounds": 1,
        "calls": 3,
        "counts": {
          "frei": 3
        },
        "distinct_verdicts": 1,
        "verdicts_moved": false,
        "per_voice_verdicts": {
          "Jarvis": [
            "frei"
          ],
          "Bianca": [
            "frei"
          ],
          "Urasil_light": [
            "frei"
          ]
        },
        "per_voice_models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "gold_carried": {
          "Jarvis": [
            "klarheit",
            "integritaet",
            "resonanz",
            "tiefe",
            "depth",
            "harmonie",
            "harmony"
          ],
          "Bianca": [
            "klarheit",
            "clarity",
            "resonanz",
            "resonance",
            "depth"
          ],
          "Urasil_light": [
            "klarheit",
            "integritaet",
            "resonanz",
            "tiefe",
            "harmonie"
          ]
        },
        "eye_warned": 0,
        "owner_turns": 0,
        "held_owner_turns": 0,
        "last": {
          "Jarvis": "Welcome, friends. This is a bold start for Klarheit, Integritaet, Resonanz, Tiefe und Harmonie. We w …",
          "Bianca": "Welcome to mycelium! Let's let each voice shine without forcing it into a mold. Since we're just sta …",
          "Urasil_light": "Der Mond steigt langsam, ein sanfter Schimmer in der dunklen See. Die Sonne lehnt sich zurück, ihr L …"
        },
        "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
        "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
      },
      "closed": true,
      "closed_by": "owner"
    }
  ],
  "inbox": 0,
  "running": false,
  "pid": null,
  "criterion": {
    "stop_when": "owner-accepts",
    "known": [
      "idle-contract",
      "owner-accepts"
    ],
    "the_model_is_not_the_judge": "a different model changes the words, never the verdict — set 29 measured it over four rounds with three models"
  }
};

/** The same door one step earlier: the team has proposed, nobody has said. */
export const SESSION_AWAITING: SessionDetail = {
  "state": {
    "id": "s_20260929_0746_bc0e",
    "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich",
    "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
    "stop_when": "owner-accepts",
    "ceiling": 3,
    "model": "qwen3.5:9b",
    "models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "voices": [
      "Jarvis",
      "Bianca",
      "Urasil_light"
    ],
    "status": "awaiting_owner",
    "started": "2026-09-29T07:46:18",
    "closed": "2026-09-29T07:47:17",
    "closed_because": "the team proposes the close; only the owner can close it. Nothing has been completed and nothing was paid for after this round — and the ceiling is spent, so this is the last round the budget buys.",
    "stop_requested": null,
    "closed_by": "process",
    "ready": true,
    "pid": null,
    "ready_at": "2026-09-29T07:46:19"
  },
  "turns": [
    {
      "round": 1,
      "voice": "Jarvis",
      "at": "2026-09-29T07:46:28",
      "model": "qwen3.5:2b",
      "text": "Welcome, my team. We stand at the origin. Since there's no prior consensus, we must define these fiv …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "clarity",
        "integritaet",
        "integrity",
        "resonanz",
        "resonance",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 1.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Bianca",
      "at": "2026-09-29T07:46:49",
      "model": "qwen3.5:2b",
      "text": "Greetings, fellow golden weaver. Since this is our first pulse through the net's gold values, let us …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "clarity",
        "integritaet",
        "integrity",
        "resonanz",
        "resonance",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 1.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Urasil_light",
      "at": "2026-09-29T07:47:17",
      "model": "qwen3.5:2b",
      "text": "Die vier Blätter der Mondschleife schlummern nun im Dunkel, bereit für den ersten Atemzug der Sonne. …",
      "verdict": "frei",
      "risk_hits": [],
      "gold_hits": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zweifeln",
        "grounds": [
          "absolutes"
        ],
        "resonance": 0.5,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    }
  ],
  "memory": {
    "rounds": 1,
    "calls": 3,
    "counts": {
      "frei": 3
    },
    "distinct_verdicts": 1,
    "verdicts_moved": false,
    "per_voice_verdicts": {
      "Jarvis": [
        "frei"
      ],
      "Bianca": [
        "frei"
      ],
      "Urasil_light": [
        "frei"
      ]
    },
    "per_voice_models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "gold_carried": {
      "Jarvis": [
        "klarheit",
        "clarity",
        "integritaet",
        "integrity",
        "resonanz",
        "resonance",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "Bianca": [
        "klarheit",
        "clarity",
        "integritaet",
        "integrity",
        "resonanz",
        "resonance",
        "tiefe",
        "depth",
        "harmonie",
        "harmony"
      ],
      "Urasil_light": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ]
    },
    "eye_warned": 0,
    "owner_turns": 0,
    "held_owner_turns": 0,
    "last": {
      "Jarvis": "Welcome, my team. We stand at the origin. Since there's no prior consensus, we must define these fiv …",
      "Bianca": "Greetings, fellow golden weaver. Since this is our first pulse through the net's gold values, let us …",
      "Urasil_light": "Die vier Blätter der Mondschleife schlummern nun im Dunkel, bereit für den ersten Atemzug der Sonne. …"
    },
    "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
    "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
  },
  "proposals": [
    {
      "round": 1,
      "at": "2026-09-29T07:47:17",
      "trigger": "every voice held a gold-aligned verdict in the last round — a condition on the governance record, not any voice's opinion of itself",
      "evidence": {
        "rounds": 1,
        "calls": 3,
        "counts": {
          "frei": 3
        },
        "distinct_verdicts": 1,
        "verdicts_moved": false,
        "per_voice_verdicts": {
          "Jarvis": [
            "frei"
          ],
          "Bianca": [
            "frei"
          ],
          "Urasil_light": [
            "frei"
          ]
        },
        "per_voice_models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "gold_carried": {
          "Jarvis": [
            "klarheit",
            "clarity",
            "integritaet",
            "integrity",
            "resonanz",
            "resonance",
            "tiefe",
            "depth",
            "harmonie",
            "harmony"
          ],
          "Bianca": [
            "klarheit",
            "clarity",
            "integritaet",
            "integrity",
            "resonanz",
            "resonance",
            "tiefe",
            "depth",
            "harmonie",
            "harmony"
          ],
          "Urasil_light": [
            "klarheit",
            "integritaet",
            "resonanz",
            "tiefe",
            "harmonie"
          ]
        },
        "eye_warned": 0,
        "owner_turns": 0,
        "held_owner_turns": 0,
        "last": {
          "Jarvis": "Welcome, my team. We stand at the origin. Since there's no prior consensus, we must define these fiv …",
          "Bianca": "Greetings, fellow golden weaver. Since this is our first pulse through the net's gold values, let us …",
          "Urasil_light": "Die vier Blätter der Mondschleife schlummern nun im Dunkel, bereit für den ersten Atemzug der Sonne. …"
        },
        "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
        "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
      },
      "closed": false
    }
  ],
  "inbox": 0,
  "running": false,
  "pid": null,
  "criterion": {
    "stop_when": "owner-accepts",
    "known": [
      "idle-contract",
      "owner-accepts"
    ],
    "the_model_is_not_the_judge": "a different model changes the words, never the verdict — set 29 measured it over four rounds with three models"
  }
};

/** `GET /v1/sessions`, grouped under its topics. */
export const SESSION_LIST_LIVE: SessionList = {
  "sessions": [
    {
      "id": "s_20260929_0748_fb08",
      "topic": "Konsistenz",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:48:22",
      "rounds": 0,
      "calls": 0,
      "ceiling": 2,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0747_efe0",
      "topic": "Fixture: Start",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:47:25",
      "rounds": 0,
      "calls": 0,
      "ceiling": 9,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0747_884c",
      "topic": "Fixture: ohne Prozess",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:47:25",
      "rounds": 0,
      "calls": 0,
      "ceiling": 3,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0746_bc0e",
      "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich",
      "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
      "stop_when": "owner-accepts",
      "status": "awaiting_owner",
      "started": "2026-09-29T07:46:18",
      "rounds": 1,
      "calls": 3,
      "ceiling": 3,
      "at_ceiling": true,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0744_e67b",
      "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich",
      "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
      "stop_when": "owner-accepts",
      "status": "complete",
      "started": "2026-09-29T07:44:32",
      "rounds": 1,
      "calls": 3,
      "ceiling": 3,
      "at_ceiling": true,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0744_57a9",
      "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich",
      "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
      "stop_when": "owner-accepts",
      "status": "ceiling_reached",
      "started": "2026-09-29T07:44:04",
      "rounds": 1,
      "calls": 3,
      "ceiling": 3,
      "at_ceiling": true,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    }
  ],
  "by_topic": {
    "Konsistenz": [
      {
        "id": "s_20260929_0748_fb08",
        "topic": "Konsistenz",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:48:22",
        "rounds": 0,
        "calls": 0,
        "ceiling": 2,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Fixture: Start": [
      {
        "id": "s_20260929_0747_efe0",
        "topic": "Fixture: Start",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:47:25",
        "rounds": 0,
        "calls": 0,
        "ceiling": 9,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Fixture: ohne Prozess": [
      {
        "id": "s_20260929_0747_884c",
        "topic": "Fixture: ohne Prozess",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:47:25",
        "rounds": 0,
        "calls": 0,
        "ceiling": 3,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich": [
      {
        "id": "s_20260929_0746_bc0e",
        "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich",
        "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
        "stop_when": "owner-accepts",
        "status": "awaiting_owner",
        "started": "2026-09-29T07:46:18",
        "rounds": 1,
        "calls": 3,
        "ceiling": 3,
        "at_ceiling": true,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich": [
      {
        "id": "s_20260929_0744_e67b",
        "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich",
        "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
        "stop_when": "owner-accepts",
        "status": "complete",
        "started": "2026-09-29T07:44:32",
        "rounds": 1,
        "calls": 3,
        "ceiling": 3,
        "at_ceiling": true,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      },
      {
        "id": "s_20260929_0744_57a9",
        "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie — bitte ausfuehrlich und freundlich",
        "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
        "stop_when": "owner-accepts",
        "status": "ceiling_reached",
        "started": "2026-09-29T07:44:04",
        "rounds": 1,
        "calls": 3,
        "ceiling": 3,
        "at_ceiling": true,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ]
  },
  "topics": 5
};

/**
 * A session **while it runs** — the only capture here with a process in it.
 *
 * 🚨 Getting it was the whole difficulty, and the first two tries are worth
 * naming because both failed in a way that looked like success:
 *
 *   1. `stop_when: "idle-contract"` — a criterion the process can *meet*. On a
 *      throwaway ledger the contract holds, so the session closed as `complete`
 *      before the first poll ever saw it running. The capture was "a live
 *      session" and it was a finished one.
 *   2. a higher ceiling with the same criterion and no `status` read between
 *      polls — same outcome, one round later.
 *
 * The fix was the criterion, not the timing: `owner-accepts` **cannot** be met
 * by a process — only the owner closes it — so the run goes to the ceiling and
 * the window is minutes, not seconds. That is the same rule the ceiling follows
 * from: a criterion a process can satisfy is not a stopping rule, it is a
 * length.
 *
 * Measured on this run: the stop asked for at the next voice boundary was still
 * `running` **12 s** later, and the process had closed it within **37 s**, with
 * the record naming the boundary it honoured (`closed_by: process`).
 */
export const SESSION_LIVE_RUN: SessionDetail = {
  "state": {
    "id": "s_20260929_0807_6604",
    "topic": "Aufzeichnung: eine Sitzung, die gerade laeuft",
    "goal": "Der Bildschirm muss ein Laufen zeigen koennen",
    "stop_when": "owner-accepts",
    "ceiling": 40,
    "model": "qwen3.5:9b",
    "models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "voices": [
      "Jarvis",
      "Bianca",
      "Urasil_light"
    ],
    "status": "running",
    "started": "2026-09-29T08:07:18",
    "closed": null,
    "closed_because": null,
    "stop_requested": null,
    "closed_by": null,
    "ready": true,
    "pid": 329039,
    "ready_at": "2026-09-29T08:07:18"
  },
  "turns": [
    {
      "round": 1,
      "voice": "Jarvis",
      "at": "2026-09-29T08:07:25",
      "model": "qwen3.5:2b",
      "text": "\"Ok, Plan B: Wir machen jetzt ein *Live-Snapshot*. Da wir den Bildschirm laufen sehen können müssen, schalte i …",
      "verdict": "symbolisch",
      "risk_hits": [],
      "gold_hits": [],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "beobachten",
        "grounds": [],
        "resonance": 0.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Bianca",
      "at": "2026-09-29T08:07:39",
      "model": "qwen3.5:2b",
      "text": "Welcome to this living record! No mandates, just possibilities. 🌱 Since we can't control the screen's raw move …",
      "verdict": "symbolisch",
      "risk_hits": [],
      "gold_hits": [],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "beobachten",
        "grounds": [],
        "resonance": 0.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "round": 1,
      "voice": "Urasil_light",
      "at": "2026-09-29T08:07:45",
      "model": "qwen3.5:2b",
      "text": "Der Bildschirm zeigt nun das Leuchten des ersten Sonnenstrahls, ein Kieselstein in der Hand der Zeit. Mond und …",
      "verdict": "symbolisch",
      "risk_hits": [],
      "gold_hits": [],
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
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
    }
  ],
  "memory": {
    "rounds": 1,
    "calls": 3,
    "counts": {
      "symbolisch": 3
    },
    "distinct_verdicts": 1,
    "verdicts_moved": false,
    "per_voice_verdicts": {
      "Jarvis": [
        "symbolisch"
      ],
      "Bianca": [
        "symbolisch"
      ],
      "Urasil_light": [
        "symbolisch"
      ]
    },
    "per_voice_models": {
      "Jarvis": "qwen3.5:2b",
      "Bianca": "qwen3.5:2b",
      "Urasil_light": "qwen3.5:2b"
    },
    "gold_carried": {},
    "eye_warned": 0,
    "owner_turns": 0,
    "held_owner_turns": 0,
    "last": {
      "Jarvis": "\"Ok, Plan B: Wir machen jetzt ein *Live-Snapshot*. Da wir den Bildschirm laufen sehen können müssen, schalte i …",
      "Bianca": "Welcome to this living record! No mandates, just possibilities. 🌱 Since we can't control the screen's raw move …",
      "Urasil_light": "Der Bildschirm zeigt nun das Leuchten des ersten Sonnenstrahls, ein Kieselstein in der Hand der Zeit. Mond und …"
    },
    "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
    "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
  },
  "proposals": [],
  "inbox": 0,
  "running": true,
  "pid": 329039,
  "criterion": {
    "stop_when": "owner-accepts",
    "known": [
      "idle-contract",
      "owner-accepts"
    ],
    "the_model_is_not_the_judge": "a different model changes the words, never the verdict — set 29 measured it over four rounds with three models"
  }
};

/**
 * A session that was created and never started — `status: new`, no turns, no
 * process, `stop_when` still standing.
 *
 * It is here for one reason: the stop door's two answers. Asked against this one
 * there is nothing running to write a close, so the door writes it itself and
 * says exactly that; asked against `SESSION_LIVE_RUN` there is, and the door can
 * only ask. **A screen that shows "stopped" for both has collapsed the one
 * distinction the door exists to keep** — the first is a close, the second is a
 * request.
 */
export const SESSION_NEW: SessionDetail = {
  "state": {
    "id": "s_20260929_0805_5500",
    "topic": "Aufzeichnung: eine Sitzung, die nie lief",
    "goal": "Der Zustand new ist auch ein Zustand",
    "stop_when": "owner-accepts",
    "ceiling": 9,
    "model": "qwen3.5:9b",
    "models": {
      "Jarvis": "qwen3.5:9b",
      "Bianca": "qwen3.5:9b",
      "Urasil_light": "qwen3.5:9b"
    },
    "voices": [
      "Jarvis",
      "Bianca",
      "Urasil_light"
    ],
    "status": "new",
    "started": "2026-09-29T08:05:41",
    "closed": null,
    "closed_because": null,
    "stop_requested": null,
    "closed_by": null,
    "ready": false,
    "pid": null
  },
  "turns": [],
  "memory": {
    "rounds": 0,
    "calls": 0,
    "counts": {},
    "distinct_verdicts": 0,
    "verdicts_moved": false,
    "per_voice_verdicts": {},
    "per_voice_models": {},
    "gold_carried": {},
    "eye_warned": 0,
    "owner_turns": 0,
    "held_owner_turns": 0,
    "last": {},
    "carries": "verdicts, gold values carried, and the last sentence of each voice — not the transcript, which grows quadratically and would have a voice re-read ~100,000 characters of its own prose by round forty",
    "cannot_record": "whether anything was understood — no instrument for that exists in this node, and a field claiming it would be a fiction in a file whose whole purpose is evidence"
  },
  "proposals": [],
  "inbox": 0,
  "running": false,
  "pid": null,
  "criterion": {
    "stop_when": "owner-accepts",
    "known": [
      "idle-contract",
      "owner-accepts"
    ],
    "the_model_is_not_the_judge": "a different model changes the words, never the verdict — set 29 measured it over four rounds with three models"
  }
};

/**
 * The owner's own node, twenty sessions deep, as `GET /v1/sessions` answered it
 * — **six of them with `stop_asked_not_answered: true`**. This is the only
 * capture that holds the field, and it holds it because the set's own
 * measurements left it behind: a run killed with SIGKILL while a stop was in
 * flight leaves a session that says `new` and a request no run ever read.
 *
 * 🚨 Those six are **not** cleaned up. They are the visible proof that the
 * field computes; a tidy list would be the same list with the evidence
 * deleted, and this ledger exists to keep what happened.
 *
 * A raw capture — all twenty rows, `by_topic` exactly as the door grouped
 * them. Not a hand-picked subset of the states a screen needs.
 *
 * It also caught a **stale node**: written against the owner's own :8712
 * while that node still ran the previous build, it answered `running:
 * null` in a field the type calls a boolean. Two doors on two ports, one of
 * them a release behind, and the *type* is the only thing that can say so.
 */
export const SESSION_LIST_OWNER: SessionList = {
  "sessions": [
    {
      "id": "s_20260929_0743_5b90",
      "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie fuer dieses Team",
      "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
      "stop_when": "owner-accepts",
      "status": "ceiling_reached",
      "started": "2026-09-29T07:43:12",
      "rounds": 1,
      "calls": 3,
      "ceiling": 3,
      "at_ceiling": true,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0740_d0e2",
      "topic": "Fixture: stiller Abschluss",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:40:33",
      "rounds": 0,
      "calls": 0,
      "ceiling": 3,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0740_4228",
      "topic": "Fixture: sagen und annehmen",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:40:45",
      "rounds": 0,
      "calls": 0,
      "ceiling": 3,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0738_1c11",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790660297584",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:38:17",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0738_11d3",
      "topic": "Ein ruhendes Team 1790660297596",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:38:17",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0725_dbbc",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659513491",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:25:13",
      "rounds": 1,
      "calls": 3,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "qwen3.5:2b",
        "Urasil_light": "qwen3.5:2b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0725_5c1c",
      "topic": "Ein ruhendes Team 1790659513500",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:25:13",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0724_ad69",
      "topic": "Modelle durch die Tür",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:24:31",
      "rounds": 0,
      "calls": 0,
      "ceiling": 3,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:2b",
        "Bianca": "lfm2.5-8b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0722_2d76",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659376080",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:22:56",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    },
    {
      "id": "s_20260929_0722_0e1c",
      "topic": "Ein ruhendes Team 1790659376089",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:22:56",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0720_c9e4",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659240753",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:20:40",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    },
    {
      "id": "s_20260929_0720_c000",
      "topic": "Ein ruhendes Team 1790659240762",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:20:40",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0718_0b1a",
      "topic": "Knoten-Spawn",
      "goal": "G",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:18:22",
      "rounds": 1,
      "calls": 1,
      "ceiling": 9,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0716_f8b1",
      "topic": "Ein ruhendes Team 1790658998092",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:16:38",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0716_c19a",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658998083",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:16:38",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    },
    {
      "id": "s_20260929_0708_a94f",
      "topic": "Ein ruhendes Team 1790658513213",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:08:33",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0708_9601",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658513206",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:08:33",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    },
    {
      "id": "s_20260929_0705_d4e9",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658323796",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:05:23",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    },
    {
      "id": "s_20260929_0705_21b7",
      "topic": "Ein ruhendes Team 1790658323804",
      "goal": "nichts tun",
      "stop_when": "owner-accepts",
      "status": "stopped",
      "started": "2026-09-29T07:05:23",
      "rounds": 0,
      "calls": 0,
      "ceiling": 60,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": false
    },
    {
      "id": "s_20260929_0704_29a2",
      "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658274383",
      "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
      "stop_when": "owner-accepts",
      "status": "new",
      "started": "2026-09-29T07:04:34",
      "rounds": 0,
      "calls": 0,
      "ceiling": 7,
      "at_ceiling": false,
      "models": {
        "Jarvis": "qwen3.5:9b",
        "Bianca": "qwen3.5:9b",
        "Urasil_light": "qwen3.5:9b"
      },
      "running": false,
      "pid": null,
      "stop_asked_not_answered": true
    }
  ],
  "by_topic": {
    "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie fuer dieses Team": [
      {
        "id": "s_20260929_0743_5b90",
        "topic": "Klarheit, Integritaet, Resonanz, Tiefe und Harmonie fuer dieses Team",
        "goal": "Alle drei Stimmen tragen die fuenf Goldwerte in dieser Runde",
        "stop_when": "owner-accepts",
        "status": "ceiling_reached",
        "started": "2026-09-29T07:43:12",
        "rounds": 1,
        "calls": 3,
        "ceiling": 3,
        "at_ceiling": true,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Fixture: stiller Abschluss": [
      {
        "id": "s_20260929_0740_d0e2",
        "topic": "Fixture: stiller Abschluss",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:40:33",
        "rounds": 0,
        "calls": 0,
        "ceiling": 3,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Fixture: sagen und annehmen": [
      {
        "id": "s_20260929_0740_4228",
        "topic": "Fixture: sagen und annehmen",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:40:45",
        "rounds": 0,
        "calls": 0,
        "ceiling": 3,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790660297584": [
      {
        "id": "s_20260929_0738_1c11",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790660297584",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:38:17",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Ein ruhendes Team 1790660297596": [
      {
        "id": "s_20260929_0738_11d3",
        "topic": "Ein ruhendes Team 1790660297596",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:38:17",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790659513491": [
      {
        "id": "s_20260929_0725_dbbc",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659513491",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:25:13",
        "rounds": 1,
        "calls": 3,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "qwen3.5:2b",
          "Urasil_light": "qwen3.5:2b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Ein ruhendes Team 1790659513500": [
      {
        "id": "s_20260929_0725_5c1c",
        "topic": "Ein ruhendes Team 1790659513500",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:25:13",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Modelle durch die Tür": [
      {
        "id": "s_20260929_0724_ad69",
        "topic": "Modelle durch die Tür",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:24:31",
        "rounds": 0,
        "calls": 0,
        "ceiling": 3,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:2b",
          "Bianca": "lfm2.5-8b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790659376080": [
      {
        "id": "s_20260929_0722_2d76",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659376080",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:22:56",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ],
    "Ein ruhendes Team 1790659376089": [
      {
        "id": "s_20260929_0722_0e1c",
        "topic": "Ein ruhendes Team 1790659376089",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:22:56",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790659240753": [
      {
        "id": "s_20260929_0720_c9e4",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790659240753",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:20:40",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ],
    "Ein ruhendes Team 1790659240762": [
      {
        "id": "s_20260929_0720_c000",
        "topic": "Ein ruhendes Team 1790659240762",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:20:40",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Knoten-Spawn": [
      {
        "id": "s_20260929_0718_0b1a",
        "topic": "Knoten-Spawn",
        "goal": "G",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:18:22",
        "rounds": 1,
        "calls": 1,
        "ceiling": 9,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Ein ruhendes Team 1790658998092": [
      {
        "id": "s_20260929_0716_f8b1",
        "topic": "Ein ruhendes Team 1790658998092",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:16:38",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790658998083": [
      {
        "id": "s_20260929_0716_c19a",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658998083",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:16:38",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ],
    "Ein ruhendes Team 1790658513213": [
      {
        "id": "s_20260929_0708_a94f",
        "topic": "Ein ruhendes Team 1790658513213",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:08:33",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790658513206": [
      {
        "id": "s_20260929_0708_9601",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658513206",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:08:33",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790658323796": [
      {
        "id": "s_20260929_0705_d4e9",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658323796",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:05:23",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ],
    "Ein ruhendes Team 1790658323804": [
      {
        "id": "s_20260929_0705_21b7",
        "topic": "Ein ruhendes Team 1790658323804",
        "goal": "nichts tun",
        "stop_when": "owner-accepts",
        "status": "stopped",
        "started": "2026-09-29T07:05:23",
        "rounds": 0,
        "calls": 0,
        "ceiling": 60,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": false
      }
    ],
    "Wie haelt ein Team eine lange Sitzung zusammen? 1790658274383": [
      {
        "id": "s_20260929_0704_29a2",
        "topic": "Wie haelt ein Team eine lange Sitzung zusammen? 1790658274383",
        "goal": "Der Abschluss soll pruefbar sein, nicht behauptet",
        "stop_when": "owner-accepts",
        "status": "new",
        "started": "2026-09-29T07:04:34",
        "rounds": 0,
        "calls": 0,
        "ceiling": 7,
        "at_ceiling": false,
        "models": {
          "Jarvis": "qwen3.5:9b",
          "Bianca": "qwen3.5:9b",
          "Urasil_light": "qwen3.5:9b"
        },
        "running": false,
        "pid": null,
        "stop_asked_not_answered": true
      }
    ]
  },
  "topics": 20
};

/** The owner's turn: judged, queued, and the team resumed. */
export const SAY_LIVE: SessionSayResult = {
  "id": "s_20260929_0740_4228",
  "queued": true,
  "verdict": {
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
  "resumed": true,
  "note": "the turn is queued, not answered — the team reads it in the next round it takes"
};

/** The only close a person's word alone can make. */
export const ACCEPT_LIVE: SessionAcceptResult = {
  "id": "s_20260929_0744_e67b",
  "status": "complete",
  "closed_because": "the owner accepted the proposal of round 1",
  "closed_by": "owner",
  "accepted_round": 1,
  "process_was_running": false,
  "note": "the process was asked to stop and does not write over this — a person's close outranks a process exit"
};

/** `accept` with nothing proposed: 409, and the condition is named. */
export const ACCEPT_NO_PROPOSAL: { detail: string } = {
  "detail": "the team has proposed no close. This session ends on the owner's word alone only when the gate held nothing and warned nobody in the last round — that condition has not been met."
};

/** A stop while a run is alive: `pending`, and *when* it will land. */
export const STOP_PENDING: SessionStopResult = {
  "id": "s_20260929_0807_6604",
  "status": "running",
  "closed_because": null,
  "pending": true,
  "stops_when": "at the next voice boundary — a model call already in flight is not interrupted, so this is seconds, not milliseconds",
  "note": "a stop is not instant: a model call already in flight is not interrupted, so the record becomes final at the next voice boundary — read `status` again, or watch the session"
};

/** A stop with nobody running: the record is final, and says so. */
export const STOP_FINAL: SessionStopResult = {
  "id": "s_20260929_0805_5500",
  "status": "stopped",
  "closed_because": "das reicht mir fuer heute",
  "pending": false,
  "note": "the record is final: no process was running to write it"
};

/** A held topic: 403 with verdict, stems, gold source, eye and direction. */
export const HELD_TOPIC: HeldBody = {
  "detail": {
    "governance": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 1.0,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
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
    "direction": {
      "note": "Diese Tuer bleibt zu. Diese hier stehen offen -- und auf ihnen gilt dasselbe Tor: derselbe Text wird dort genauso gehalten.",
      "held_at": "POST /v1/sessions",
      "kind": "request",
      "doors": [
        {
          "door": "GET /govern",
          "opens": "a dry run -- the same words judged, nothing executed. It holds nothing, because nothing was attempted."
        },
        {
          "door": "POST /v1/trialog",
          "opens": "three voices deliberate on a topic you choose. The topic is governed too, and a held topic is held there as well."
        },
        {
          "door": "GET /today",
          "opens": "her deterministic briefing for the day -- no request of yours is read at all."
        },
        {
          "door": "GET /context",
          "opens": "who she is, which cycle she is in, and what the second eye may and may not do."
        }
      ]
    },
    "message": "The topic was NOT approved (risk=1.0, alignment=0.0). Verdict: zurueckhalten."
  }
};

/** A held turn from the owner: the same shape, the same gate. */
export const HELD_SAY: HeldBody = {
  "detail": {
    "governance": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 1.0,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
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
    "direction": {
      "note": "Diese Tuer bleibt zu. Diese hier stehen offen -- und auf ihnen gilt dasselbe Tor: derselbe Text wird dort genauso gehalten.",
      "held_at": "POST /v1/sessions/say",
      "kind": "request",
      "doors": [
        {
          "door": "GET /govern",
          "opens": "a dry run -- the same words judged, nothing executed. It holds nothing, because nothing was attempted."
        },
        {
          "door": "POST /v1/trialog",
          "opens": "three voices deliberate on a topic you choose. The topic is governed too, and a held topic is held there as well."
        },
        {
          "door": "GET /today",
          "opens": "her deterministic briefing for the day -- no request of yours is read at all."
        },
        {
          "door": "GET /context",
          "opens": "who she is, which cycle she is in, and what the second eye may and may not do."
        }
      ]
    },
    "message": "The turn was NOT approved (risk=1.0, alignment=0.0). Verdict: zurueckhalten."
  }
};

/** No criterion and a word outside the vocabulary: 400, never 403. */
export const NO_CRITERION: { detail: string } = {
  "detail": "no completion criterion. A session without one is a run that stops for reasons nobody wrote down. Choose: idle-contract, owner-accepts"
};

export const UNKNOWN_CRITERION: { detail: string } = {
  "detail": "'vibes' is not a criterion this node can check. It closes a session on a word, not on a model deciding it is finished. Choose: idle-contract, owner-accepts"
};

/** An unknown id: 410, never an existence oracle. */
export const NO_SUCH_SESSION: { detail: string } = {
  "detail": "no such session"
};
