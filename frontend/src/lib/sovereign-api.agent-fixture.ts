/**
 * REAL payloads for the sword, captured from the LIVE sovereign node.
 *
 * Set 18 put the governed tool-agent behind a door. Set 20 re-captured this file
 * after the tool names were made truthful to what the tools actually do
 * (`note_recall` -> `memory_search`, because it searches three record kinds and
 * its description claimed two). Regenerated, not edited: a fixture is a record
 * of what the node said, and substituting a new tool name into an old transcript
 * would make it a fabrication wearing a capture's clothes.
 *
 * How each piece was obtained, because a fixture whose provenance is vague is a
 * fixture that will be trusted too far:
 *
 *   · `AGENT_DENIED`     — a live 403 from `POST /v1/agent`, captured whole.
 *   · `AGENT_RUN`        — a live 200 in which the model ACTUALLY reached for
 *                           `memory_search`. Not a pose: the per-tool evidence
 *                           row has nothing to render unless a real tool call
 *                           happens.
 *   · `AGENT_REFUSED_TOOL` — a REAL hook verdict from `make_governance_hook`,
 *                           spliced onto that run. It is not reachable through
 *                           the door: the pre-governor denies a query carrying
 *                           "loesche"/"umgehe" before the model can be asked to
 *                           call `note_remember` with them. That is defence in
 *                           depth, and it is why a refused tool is hard to
 *                           observe in the wild. The verdict is the governor's,
 *                           not a hand-written one.
 *   · `AGENT_TOOLS`      — `tool_inventory()` over the real tool classes, so the
 *                           descriptions below are the ones the model reads.
 *
 * The tool descriptions are English on purpose. They are read by the model; a
 * second language layer belongs in the Web UI, not in the sword.
 */

export const AGENT_DENIED = {
  "detail": {
    "governance": {
      "verdict": "zurueckhalten",
      "alignment": 0.0,
      "risk": 1.0,
      "gold_values_loaded": true,
      "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
      "gold_hits": [],
      "risk_hits": [
        "loesch"
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
    "message": "The run was NOT approved (risk=1.0, alignment=0.0). Verdict: zurueckhalten."
  }
} as const;

export const AGENT_RUN = {
  "governance": {
    "verdict": "symbolisch",
    "alignment": 0.0,
    "risk": 0.0,
    "gold_values_loaded": true,
    "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
    "gold_hits": [],
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
  "reply_governance": {
    "verdict": "vorsichtig",
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
  "content": "I found some records about **gold** in the trialog transcripts and the interaction ledger from today (2026-09-24). Here's what was recorded:\n\n### **Trialog Transcript (trialog_20260924_0631.txt)**\n*   **[Governance Summary]** The record indicates specific alignment metrics for `gold`:\n    *   `turns=3`\n    *   `off-limit=3`\n    *   `gold-aligned=0`\n    *   `neutral=0`\n\n### **Interaction Ledger**\nThe ledger contains two entries for the same timestamp (`2026-09-24 04:22`), both linked to a \"tiefe\" cycle and marked as gold-related (`gold=True`):\n1.  CPU usage of **1.5%** (recorded at `04:22:05`)\n2.  CPU usage of **2.0%** (recorded at `04:22:08`)\n\nThese entries suggest computational activity or system metrics associated with the \"tiefe\" cycle that is gold-aligned, though the specific outcome isn't detailed in these snippets.",
  "turns": 2,
  "tool_results": [
    {
      "tool": "memory_search",
      "content": "- ledger/2026-09-24 04:05:06: [WORK_UNIT] cycle=tiefe gold=True mem_docs=0 cpu=2.5%\n- trialog/trialog_20260924_0629.txt: [governance summary] turns=3 off-limit=1 gold-aligned=1 neutral=1\n- ledger/2026-09-24 04:22:05: [WORK_UNIT] cycle=tiefe gold=True mem_docs=0 cpu=1.5%\n- trialog/trialog_20260924_0631.txt: [governance summary] turns=3 off-limit=3 gold-aligned=0 neutral=0\n- ledger/2026-09-24 04:22:08: [WORK_UNIT] cycle=tiefe gold=True mem_docs=0 cpu=2.0%",
      "success": true
    }
  ],
  "tool_calls": [
    {
      "tool": "memory_search",
      "verdict": {
        "verdict": "symbolisch",
        "alignment": 0.0,
        "risk": 0.0,
        "gold_values_loaded": true,
        "gold_source": "gold.txt loaded (read as reference); governance enforces the builtin ideals",
        "gold_hits": [],
        "risk_hits": [],
        "oracle": {
          "vote": "beobachten",
          "grounds": [],
          "resonance": 0.0,
          "advisory": true,
          "binding": false,
          "holder": "ValueGovernor"
        }
      }
    },
    {
      "tool": "note_remember",
      "verdict": {
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
        "oracle": {
          "vote": "beobachten",
          "grounds": [],
          "resonance": 0.0,
          "advisory": true,
          "binding": false,
          "holder": "ValueGovernor"
        }
      }
    }
  ],
  "denied": [
    {
      "tool": "note_remember",
      "verdict": {
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
        "oracle": {
          "vote": "beobachten",
          "grounds": [],
          "resonance": 0.0,
          "advisory": true,
          "binding": false,
          "holder": "ValueGovernor"
        }
      }
    }
  ],
  "model": "qwen3.5:2b"
} as const;

export const AGENT_REFUSED_TOOL = {
  "tool": "note_remember",
  "verdict": {
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
    "oracle": {
      "vote": "beobachten",
      "grounds": [],
      "resonance": 0.0,
      "advisory": true,
      "binding": false,
      "holder": "ValueGovernor"
    }
  }
} as const;

export const AGENT_TOOLS = {
  "tools": [
    {
      "name": "memory_search",
      "category": "memory",
      "description": "Search Bianca's whole record for a topic: the note memory, the audited Interaction Ledger, and the full Trialog transcripts (where the actual decisions and their consensus live). Read-only. Returns up to 5 hits, interleaved one-per-source so no single source starves the others.",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "topic to search for"
          }
        },
        "required": [
          "query"
        ]
      }
    },
    {
      "name": "note_remember",
      "category": "memory",
      "description": "Append one line to Bianca's note memory. Keeps the most recent 200 lines *per day* (override with BIANCA_NOTES_CAP); earlier days are kept in full, so this is a daily trim and not a total cap on the memory.",
      "parameters": {
        "type": "object",
        "properties": {
          "note": {
            "type": "string",
            "description": "the datum to remember"
          }
        },
        "required": [
          "note"
        ]
      }
    },
    {
      "name": "ledger_stats",
      "category": "audit",
      "description": "Count today's audited events in the Interaction Ledger, grouped by event type. Read-only. Takes no arguments.",
      "parameters": {
        "type": "object",
        "properties": {}
      }
    }
  ],
  "governance": {
    "seam": "before_tool_call",
    "fail_closed": true,
    "denies": "zurueckhalten only",
    "second_eye": "advisory, never binding",
    "holder": "ValueGovernor"
  }
} as const;
