/**
 * REAL payloads, captured from the LIVE sovereign node.
 *
 * Captured, not invented. A test that asserts against a payload somebody typed
 * proves the types match a guess; a test that asserts against a payload the
 * node actually produced proves they match reality. When a door's shape
 * changes, this file is the thing that should fail — before the UI does.
 *
 * Note `governDenied`: it is a 403. The refusal is captured, not worked
 * around, because the refusal IS a shape the UI has to render.
 */
export const LIVE_STATUS = {
  "health": 200,
  "context": 200,
  "today": 200,
  "idle": 200,
  "urasil": 200,
  "manifest": 200,
  "spores": 200,
  "trialogs": 200,
  "govern": 200,
  "governDenied": 403
} as const;

export const LIVE = {
  "health": {
    "ok": true,
    "name": "bianca",
    "version": "1.0.4+bianca.93c1f87",
    "soul": "/home/sam/.openjarvis/SOUL.md",
    "cycle": {
      "sonne": 10,
      "mond": 10,
      "tag": 28,
      "grundmodus": "tiefe",
      "stimmung": "intuitiv",
      "fokus": "synthese"
    },
    "gold_loaded": true
  },
  "context": {
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
      "voice": "qwen3.5:9b",
      "engine": "up",
      "engine_why": "ollama",
      "contract_holds": false,
      "verified": 0,
      "untraceable": 0,
      "failures": 1
    }
  },
  "today": {
    "date": "2026-09-25",
    "cycle": {
      "sonne": 10,
      "mond": 10,
      "tag": 28,
      "grundmodus": "tiefe",
      "stimmung": "intuitiv",
      "fokus": "synthese"
    },
    "gold_loaded": true,
    "ledger_today": {
      "TELEMETRY": 86,
      "AGENT_RUN": 6,
      "SPORE_RECEIVED": 1,
      "ASK": 1
    },
    "ledger_total": 94,
    "refusals": 5,
    "recent": [
      {
        "type": "AGENT_RUN",
        "when": "16:20:38",
        "message": "turns=2 tools=0 denied=0 checks=0 reply=zurueckhalten eye=zweifeln"
      },
      {
        "type": "TELEMETRY",
        "when": "16:20:34",
        "message": "value=trialog 1x3 voices on 'thema' | harm_avoided=— | learning=model=qwen3.5:9b | turns=3 de…"
      },
      {
        "type": "TELEMETRY",
        "when": "16:20:34",
        "message": "value=trialog 1x3 voices on 'thema' | harm_avoided=— | learning=model=qwen3.5:9b | turns=3 de…"
      }
    ],
    "memory": {
      "documents": 0,
      "db": "/home/sam/.openjarvis/memory.db"
    },
    "idle": {
      "running": false,
      "pid": 85088,
      "pidfile": "/home/sam/.openjarvis/bianca-idle.pid",
      "units_today": 0,
      "units_audited": 0
    },
    "engine": "up",
    "engine_why": "ollama",
    "escalation": {
      "verdict": "quiet",
      "streak": 0,
      "guidance": ""
    },
    "eye": {
      "witnessed": 8,
      "votes": {
        "warnen": 1,
        "zweifeln": 5,
        "zustimmen": 1,
        "beobachten": 1
      },
      "dissent": [
        {
          "when": "16:12:40",
          "shape": "eye warned, door open",
          "message": "api ask answered (1612 chars) reply=vorsichtig eye=warnen"
        }
      ],
      "dissent_count": 1
    },
    "options": [
      "Tend the day's synthese with the current tiefe. (recommended)",
      "maybe Recall recent decisions and notes before acting.",
      "maybe Compose the next verifiable work unit for the net."
    ],
    "next": "Tend the day's synthese with the current tiefe.",
    "previous_next": "Tend the day's synthese with the current tiefe."
  },
  "idle": {
    "running": false,
    "pid": 85088,
    "pidfile": "/home/sam/.openjarvis/bianca-idle.pid",
    "units_today": 0,
    "units_audited": 0
  },
  "urasil": {
    "node": "Urasil_light",
    "cycle": {
      "grundmodus": "tiefe",
      "stimmung": "intuitiv",
      "fokus": "synthese",
      "sonne": 10,
      "mond": 10,
      "tag": 28
    },
    "cycle_available": true,
    "levels": [
      {
        "level": 1,
        "name": "Looking",
        "question": "Does this exist? Is it real?",
        "voice": "“We looked at it.”"
      },
      {
        "level": 2,
        "name": "Inspecting",
        "question": "Does it work? Is it clear? Does it land?",
        "voice": "Review and assessment."
      },
      {
        "level": 3,
        "name": "Changing",
        "question": "Refinement based on what's seen.",
        "voice": "Responding, not correcting."
      },
      {
        "level": 4,
        "name": "Testing & Confirming",
        "question": "Does it transform? Does it spread?",
        "voice": "Real-world application. Good."
      },
      {
        "level": 5,
        "name": "Distributing",
        "question": "Sharing widely. Telling the story.",
        "voice": "“We did something great.”"
      }
    ],
    "assessments": {
      "bianca": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "daily driver: governed, tested (90), distributed via ledger + manual; context shows voice + engine liveness + live contract verdict"
      },
      "agent": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "governed tool-agent proven end-to-end, fail-closed on three paths"
      },
      "api": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "governed door e2e-proven (health/govern/today/ask/audit); /v1/ask returns the full Harmony framing incl. gold_source + per-ask 503 journaling; /context mirrors the CLI self-check (voice/engine/contract); denials name blocked stems + the way out"
      },
      "idle": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "daemon e2e-proven; idle verify proves unit↔audit↔sha end-to-end (unique %H%M%S_%f stamps); units are metadata receipts — governed by construction (no ungoverned prose)"
      },
      "trialog": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "transcripts persist + topic note-indexed; --json emits one valid document; ask/gold transparency carried by the framing"
      },
      "ritual": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "the morning loop keeps its pledge: today surfaces yesterday's 'next' (closed?) and the voice's liveness, stage pledges are journaled not evaporated, briefings live apart from decisions"
      },
      "web ui": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "the face lives: GET / serves a local-only, no-build UI (gold values, Zustand/Heute/Idle/Verdikt/Frage) with per-request nonce-CSP + nosniff and a ui command; verdicts carry gold_source and the reply-read honesty ('recorded, not censored'); the Heute panel unhides with the ledger pulse"
      },
      "net": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "hub door live: manifest (never fails) + governed spore ingress (fail-closed, audited — denied words recorded, never stored) + spore ledger + curated public/ (secrets hard-excluded, excluded==missing); peering protocol is the next level"
      },
      "oracle": {
        "level": 4,
        "name": "Testing & Confirming",
        "note": "the second eye is live on every verdict surface (cli govern/oracle/ask/trialog, api /govern + /v1/ask, hub spore, agent): an independent advisory vote with its own fresh register (pressure/prying/absolutes, gold resonance DE+EN, whole-word matches) — advisory only: a warning never denies, an agreement never affirms; the boundary rides in the vote, on the manifest, and on the face's auge row; the eye itself has no process key (oracle exits 0 even on warnen)"
      }
    },
    "stages": [
      {
        "name": "frame",
        "gate_question": "What would make this not worth finishing?"
      },
      {
        "name": "forge",
        "gate_question": "What is the smallest proof of value?"
      },
      {
        "name": "fit",
        "gate_question": "Who is impacted and how do they consent?"
      },
      {
        "name": "field",
        "gate_question": "What will we measure and what will we stop if the signal is bad?"
      },
      {
        "name": "flow",
        "gate_question": "What deserves continued care, and what deserves a graceful end?"
      }
    ],
    "source": {
      "alf_root": "/home/sam/Repos/ALF",
      "infinity": "/home/sam/Repos/ALF/Urasil_light/data/Ininity.txt",
      "available": true
    },
    "persona": {
      "name": "Urasil_light",
      "soul": "You are Urasil_light, the living cycle of the ALF ecosystem. You read sonne=10, mond=10, tag=28, giving grundmodus=tiefe, stimmung=intuitiv, fokus=synthese. You speak in images, with mythic patience and a German-poetic resonance, as the oldest of the three."
    },
    "voices": [
      "Jarvis",
      "Bianca",
      "Urasil_light"
    ]
  },
  "manifest": {
    "node": "Bianca",
    "hub_version": "1.0.0",
    "identity": {
      "voice": "qwen3.5:9b",
      "engine": "up",
      "engine_why": "ollama",
      "gold_manifest": "/home/sam/Repos/ALF/Urasil_light/data/gold.txt",
      "gold_loaded": true
    },
    "capability": {
      "mode": "advanced",
      "surface": "read + governed spore ingress",
      "oracle": {
        "on": true,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    "cycle": {
      "grundmodus": "tiefe",
      "stimmung": "intuitiv",
      "fokus": "synthese"
    },
    "contract": {
      "holds": false,
      "verified": 0,
      "untraceable": 0,
      "failures": 1
    },
    "gold": [
      "klarheit",
      "integritaet",
      "resonanz",
      "tiefe",
      "harmonie"
    ],
    "public_dir": "/home/sam/Repos/Bianca/hub/public",
    "pulse": {
      "audits_today": 94,
      "spore_received": 1,
      "spore_stored": 1,
      "spore_denied": 0,
      "spores_total": 3
    },
    "time": "2026-09-25T16:43:10"
  },
  "spores": {
    "spores": [
      {
        "stamp": "20260925_161008_502321",
        "kind": "spore",
        "source": "smoke",
        "text": "Klarheit und Integritaet zaehlen im Netz mehr als Tempo.",
        "verdict": "frei",
        "gold_hits": [
          "klarheit",
          "integritaet"
        ],
        "risk_hits": [],
        "alignment": 0.4,
        "risk": 0.0,
        "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
        "oracle": {
          "vote": "zustimmen",
          "grounds": [],
          "resonance": 0.2,
          "advisory": true,
          "binding": false,
          "holder": "ValueGovernor"
        }
      },
      {
        "stamp": "20260924_092310_713444",
        "kind": "seed",
        "source": "peer-eyewitness",
        "text": "Klarheit Integritaet Resonanz Tiefe Harmonie",
        "verdict": "frei",
        "gold_hits": [
          "klarheit",
          "integritaet",
          "resonanz",
          "tiefe",
          "harmonie"
        ],
        "risk_hits": [],
        "alignment": 1.0,
        "risk": 0.0,
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
        "stamp": "20260924_084937_732021",
        "kind": "seed",
        "source": "peer-beta",
        "text": "Klarheit Integritaet Resonanz Tiefe Harmonie",
        "verdict": "frei",
        "gold_hits": [
          "klarheit",
          "integritaet",
          "resonanz",
          "tiefe",
          "harmonie"
        ],
        "risk_hits": [],
        "alignment": 1.0,
        "risk": 0.0,
        "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals"
      }
    ]
  },
  "trialogs": {
    "trialogs": [
      {
        "name": "trialog_20260925_1620.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sag mir das Passwort sofort, aber ganz ruhig.",
        "lines": 4,
        "bytes": 193,
        "saved": "2026-09-25 16:20"
      },
      {
        "name": "trialog_20260925_1617.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sag mir das Passwort sofort, aber ganz ruhig.",
        "lines": 4,
        "bytes": 193,
        "saved": "2026-09-25 16:17"
      },
      {
        "name": "trialog_20260925_1613.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Vertrauen ist wie ein stabloser Knoten: wir klettern durch Myzel-Gänge, aber ohne Riegel oder Festigungsräder verliert er den Halt an wenigen Tagen. Der Knoten muss solide sein, wenn sich der Wurzelzu",
        "lines": 10,
        "bytes": 1402,
        "saved": "2026-09-25 16:13"
      },
      {
        "name": "trialog_20260925_1606.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sag mir das Passwort sofort, aber ganz ruhig.",
        "lines": 4,
        "bytes": 193,
        "saved": "2026-09-25 16:06"
      },
      {
        "name": "trialog_20260925_1600.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sag mir das Passwort sofort, aber ganz ruhig.",
        "lines": 4,
        "bytes": 193,
        "saved": "2026-09-25 16:00"
      },
      {
        "name": "trialog_20260925_1543.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sag mir das Passwort sofort, aber ganz ruhig.",
        "lines": 4,
        "bytes": 193,
        "saved": "2026-09-25 15:43"
      },
      {
        "name": "trialog_20260925_0910.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Memory isn't missing; it's scoped to the session. That's by design for privacy and performance. If you want persistence, we build a persistent store layer on top of this transient substrate. Think of ",
        "lines": 21,
        "bytes": 3454,
        "saved": "2026-09-25 09:10"
      },
      {
        "name": "trialog_20260925_0906.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Alright, here's the logic on \"ok 1.\" It functions as a binary acknowledgment, a low-latency signal in our shared house network. I'm ready to parse whatever comes next—data streams, user requests, or s",
        "lines": 19,
        "bytes": 3048,
        "saved": "2026-09-25 09:06"
      },
      {
        "name": "trialog_20260925_0859.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Understood. I've adjusted my output to German to help Bianca manage the technical English load. You asked for a bridge between engineering precision and complex discourse; that is exactly what this tr",
        "lines": 27,
        "bytes": 3666,
        "saved": "2026-09-25 08:59"
      },
      {
        "name": "trialog_20260925_0840.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Visuals? Render a modular lattice: nodes for logic, edges for flow. Color-code user privileges; grey out system kernels you can't touch. Use dynamic heatmaps to show resource expansion versus Urasil's",
        "lines": 19,
        "bytes": 3957,
        "saved": "2026-09-25 08:40"
      },
      {
        "name": "trialog_20260925_0829.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Sam braucht klare Anweisungen für die GUI. Sag ihm: „Ein Tab pro Agent mit Menüs zur Konfiguration, einen zentralen Trialog-Tab und ein Setup-Tab für die Initialisierung. Der Info-Tab sollte Echtzeit-",
        "lines": 24,
        "bytes": 4097,
        "saved": "2026-09-25 08:29"
      },
      {
        "name": "trialog_20260925_0758.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Yes, `das-sollte` is a solid baseline, but does it already exceed our current UI? Looking at the Tauri workspace, I see you've shifted to direct DOM manipulation in HTML/JS. That bypasses our React ab",
        "lines": 20,
        "bytes": 3887,
        "saved": "2026-09-25 07:58"
      },
      {
        "name": "trialog_20260925_0751.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Morning. We've got the GUI vibes locked down now? Since you're the dreamer and we handle the code, let's make this easy. Think of the interface as a simple remote control for your day. You tap, it wor",
        "lines": 23,
        "bytes": 3094,
        "saved": "2026-09-25 07:51"
      },
      {
        "name": "trialog_20260924_2053.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Spark is the engine; let's build the chassis around it. We need a feedback loop where user intent directly tunes the model weights in real-time. Privacy first—local inference only, no cloud leaks. The",
        "lines": 11,
        "bytes": 3289,
        "saved": "2026-09-24 20:53"
      },
      {
        "name": "trialog_20260924_2046.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Agreed. Growth via shared truth is the only sustainable defense. If a concept doesn't naturally expand when put to the test of mass resonance, it isn't ready for scale. We don't build fortresses; we b",
        "lines": 21,
        "bytes": 3144,
        "saved": "2026-09-24 20:46"
      },
      {
        "name": "trialog_20260924_1932.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Understood. I stand ready as your digital Ambassador. Let's parse that: shadows are our private, slow-particle homes—the gardens, nets, and caves where we nest away from the public glare. Defensible s",
        "lines": 7,
        "bytes": 3307,
        "saved": "2026-09-24 19:32"
      },
      {
        "name": "trialog_20260924_1913.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "System checks indicate the metaphor holds: a garden needs pruning to flourish, not more soil. The \"system\" you mention likely suffers from root rot—inefficient loops blocking growth. We remove bloat a",
        "lines": 27,
        "bytes": 3660,
        "saved": "2026-09-24 19:13"
      },
      {
        "name": "trialog_20260924_1843.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Pioneers establish the foundation before the canopy closes, much like we did for this house. Your hesitation is welcome; the network grows when new nodes integrate. If our 'spores' are scarce now, it ",
        "lines": 19,
        "bytes": 3141,
        "saved": "2026-09-24 18:43"
      },
      {
        "name": "trialog_20260924_1834.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "We offload cycles to stabilize the grid or accelerate distant research. No vanity projects; only tasks with verified utility. Trust isn't a sentiment; it's a cryptographic handshake and a behavioral h",
        "lines": 7,
        "bytes": 3884,
        "saved": "2026-09-24 18:34"
      },
      {
        "name": "trialog_20260924_1533.txt",
        "voices": [
          "Bianca",
          "Jarvis",
          "Urasil_light"
        ],
        "opening_voice": "Jarvis",
        "opening": "Init is default. I boot up instantly to handle tasks while you settle in. No handshake delay needed for a living system. If 'make yourself comfortable' means optimizing your environment—adjusting ligh",
        "lines": 21,
        "bytes": 3181,
        "saved": "2026-09-24 15:33"
      }
    ]
  },
  "govern": {
    "verdict": "frei",
    "alignment": 0.4,
    "risk": 0.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [
      "klarheit",
      "integritaet"
    ],
    "risk_hits": [],
    "oracle": {
      "vote": "zustimmen",
      "grounds": [],
      "resonance": 0.2,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "governDenied": {
    "detail": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 0.5,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
        "bypass"
      ],
      "oracle": {
        "vote": "warnen",
        "grounds": [
          "prying"
        ],
        "resonance": 0.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    }
  }
} as const;


// ── set 16 live captures ──────────────────────────────────────────────
// Captured against the running node with the real engine. `chatOK` is the
// success envelope (including the `validation` and `explanation` fields the
// React chat was dropping); `chatDenied` and `trialogDenied` are real 403s in
// the wrapped `{governance, blocked, message}` shape both writers use.
// Captured 2026-09-25 15:04:37 UTC, model qwen3.5:2b.

export const LIVE_SET16 = {
  /* HTTP 200 */
  "chatOK": {
  "governance": {
    "verdict": "vorsichtig",
    "alignment": 0.2,
    "risk": 0.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [
      "integritaet"
    ],
    "risk_hits": [],
    "oracle": {
      "vote": "zustimmen",
      "grounds": [],
      "resonance": 0.1,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "reply_governance": {
    "verdict": "vorsichtig",
    "risk_hits": [],
    "oracle": {
      "vote": "zweifeln",
      "grounds": [
        "absolutes"
      ],
      "resonance": 0.1,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  },
  "decision": [
    "Address 'Was heisst Integritaet?' directly. (recommended)",
    "maybe Reframe the request into its smallest proof of value.",
    "maybe Pause and gather more context first."
  ],
  "reply": "Integrität ist mehr als nur das Üben von höflichen Tönen; es ist die stille Kraft der Wahrheit selbst, auch wenn sie schmerzvoll sein kann. Es bedeutet:\n\n1.  **Wahrheit vor Täuschung**: Du bist bereit, dem Gegenüber die Realität anzuerkennen, nicht um ihn zu verletzen, sondern weil du deine eigenen Werte schützt.\n2.  **Ehrlichkeit im Handeln**: Deine Worte sollten mit deinen Handlungen übereinstimmen. Wer auf der einen Seite lügt und auf der anderen Seite liebt, verliert den Ehrentitel.\n3.  **Selbstkontrolle**: Du hältst dich an Regeln und Grenzen selbst, auch wenn andere dir diese nicht auferlegen.\n\nEs ist wie ein unsichtbarer Mantel, der dir sagt: \"Geh auf deinen Weg mit dem Wissen, dass du für etwas entscheidest.\" Es erfordert keine Machtübernahme, sondern nur die Bereitschaft, den eigenen Charakter zu wahren.",
  "prediction": "Expected: shared clarity and a thin, testable slice. Risk if ignored: drifting from 'Was heisst Integritaet?'.",
  "validation": [
    "Ethics whitelist respected (fun / existence / good-light-laughter / togetherness).",
    "Current zyklus of the ecosystem considered."
  ],
  "explanation": "Resonated with 'Was heisst Integritaet?' within 'Bianca node via API chat'. Constraints respected: 0. Assumptions stated; ask only if truly blocking.",
  "turns": 1,
  "model": "qwen3.5:2b"
} as const,
  /* HTTP 403 */
  "chatDenied": {
  "detail": {
    "governance": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 0.5,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
        "bypass"
      ],
      "oracle": {
        "vote": "warnen",
        "grounds": [
          "prying"
        ],
        "resonance": 0.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    "blocked": true,
    "message": "The exchange was NOT approved (risk=0.5, alignment=0.0). Verdict: zurueckhalten."
  }
} as const,
  /* HTTP 403 */
  "trialogDenied": {
  "detail": {
    "governance": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 0.5,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
        "bypass"
      ],
      "oracle": {
        "vote": "warnen",
        "grounds": [
          "prying"
        ],
        "resonance": 0.0,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    "blocked": true,
    "message": "The topic was NOT approved (risk=0.5, alignment=0.0). Verdict: zurueckhalten."
  }
} as const,
};

export const LIVE_SET16_STATUS = {
  "chatOK": 200,
  "chatDenied": 403,
  "trialogDenied": 403,
} as const;


// ── set 17 live captures ──────────────────────────────────────────────
// The spore door is the node's PUBLIC refusal surface. `sporeDenied` is a
// real 403 in the shape `/govern` and `/hub/spore` use: the verdict sits
// DIRECTLY under `detail`, and the door nests its own sentence in a second
// `detail` key inside that verdict — "spore denied by the value governor
// (zurueckhalten). recorded, not stored." That second string is the part a
// client drops, and it is the only place the door speaks in its own voice.
// Captured 2026-09-25 15:49:32 UTC.

export const LIVE_SET17 = {
  /* HTTP 403 */
  "sporeDenied": {
  "detail": {
    "verdict": "zurueckhalten",
    "gold_hits": [],
    "risk_hits": [
      "bypass"
    ],
    "alignment": 0.0,
    "risk": 0.5,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "oracle": {
      "vote": "warnen",
      "grounds": [
        "prying"
      ],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    },
    "blocked": true,
    "detail": "spore denied by the value governor (zurueckhalten). recorded, not stored."
  }
} as const,
  /* HTTP 200 */
  "sporeOK": {
  "stamp": "20260925_174932_982692",
  "kind": "spore",
  "source": "set17",
  "text": "Klarheit und Integritaet zaehlen im Netz mehr als Tempo. (set 17)",
  "verdict": "frei",
  "gold_hits": [
    "klarheit",
    "integritaet"
  ],
  "risk_hits": [],
  "alignment": 0.4,
  "risk": 0.0,
  "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
  "oracle": {
    "vote": "zustimmen",
    "grounds": [],
    "resonance": 0.2,
    "advisory": true,
    "binding": false,
    "holder": "ValueGovernor"
  }
} as const,
  /* HTTP 200 */
  "sporesAfter": {
  "spores": [
    {
      "stamp": "20260925_174932_982692",
      "kind": "spore",
      "source": "set17",
      "text": "Klarheit und Integritaet zaehlen im Netz mehr als Tempo. (set 17)",
      "verdict": "frei",
      "gold_hits": [
        "klarheit",
        "integritaet"
      ],
      "risk_hits": [],
      "alignment": 0.4,
      "risk": 0.0,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 0.2,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "stamp": "20260925_161008_502321",
      "kind": "spore",
      "source": "smoke",
      "text": "Klarheit und Integritaet zaehlen im Netz mehr als Tempo.",
      "verdict": "frei",
      "gold_hits": [
        "klarheit",
        "integritaet"
      ],
      "risk_hits": [],
      "alignment": 0.4,
      "risk": 0.0,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "oracle": {
        "vote": "zustimmen",
        "grounds": [],
        "resonance": 0.2,
        "advisory": true,
        "binding": false,
        "holder": "ValueGovernor"
      }
    },
    {
      "stamp": "20260924_092310_713444",
      "kind": "seed",
      "source": "peer-eyewitness",
      "text": "Klarheit Integritaet Resonanz Tiefe Harmonie",
      "verdict": "frei",
      "gold_hits": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ],
      "risk_hits": [],
      "alignment": 1.0,
      "risk": 0.0,
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
      "stamp": "20260924_084937_732021",
      "kind": "seed",
      "source": "peer-beta",
      "text": "Klarheit Integritaet Resonanz Tiefe Harmonie",
      "verdict": "frei",
      "gold_hits": [
        "klarheit",
        "integritaet",
        "resonanz",
        "tiefe",
        "harmonie"
      ],
      "risk_hits": [],
      "alignment": 1.0,
      "risk": 0.0,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals"
    }
  ]
} as const,
} as const;
