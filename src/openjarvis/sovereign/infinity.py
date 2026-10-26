"""
The Five Levels of Finishing — bare ground, drawn from the Urasil_light
manuscript: ``ALF/Urasil_light/data/Ininity.txt`` ("THE 5 LEVELS OF FINISHING").

The overlay's Harmony STAGES (frame/forge/fit/field/flow) are the engine's
gate-discipline; the Five Levels are the breathing cycle from the book that
everything — the node included — moves through. Level 3 ("Changing") speaks
of responding, not correcting: this module gives Bianca that source
vocabulary as a deterministic, no-LLM self-assessment that degrades
gracefully when the book is absent.
"""

from openjarvis.sovereign.link import default_alf_root

# Names and questions follow the manuscript verbatim where sensible.
LEVELS = [
    {
        "name": "Looking",
        "question": "Does this exist? Is it real?",
        "voice": "“We looked at it.”",
    },
    {
        "name": "Inspecting",
        "question": "Does it work? Is it clear? Does it land?",
        "voice": "Review and assessment.",
    },
    {
        "name": "Changing",
        "question": "Refinement based on what's seen.",
        "voice": "Responding, not correcting.",
    },
    {
        "name": "Testing & Confirming",
        "question": "Does it transform? Does it spread?",
        "voice": "Real-world application. Good.",
    },
    {
        "name": "Distributing",
        "question": "Sharing widely. Telling the story.",
        "voice": "“We did something great.”",
    },
]

SOURCE = "Urasil_light/data/Ininity.txt"

# The node's honest breathing-level per domain, each with its evidence.
# A snapshot the owner can drift, correct, or extend — stated as a claim,
# never as gospel.
ASSESSMENTS = {
    "bianca": {
        "level": 4,
        "note": "daily driver: governed, tested (90), distributed via ledger + manual; context shows voice + engine liveness + live contract verdict",
    },
    "agent": {
        "level": 4,
        "note": "governed tool-agent proven end-to-end, fail-closed on three paths",
    },
    "api": {
        "level": 4,
        "note": "governed door e2e-proven (health/govern/today/ask/audit); /v1/ask returns the full Harmony framing incl. gold_source + per-ask 503 journaling; /context mirrors the CLI self-check (voice/engine/contract); denials name blocked stems + the way out",
    },
    "idle": {
        "level": 4,
        "note": "daemon e2e-proven; idle verify proves unit↔audit↔sha end-to-end (unique %H%M%S_%f stamps); units are metadata receipts — governed by construction (no ungoverned prose)",
    },
    "trialog": {
        "level": 4,
        "note": "transcripts persist + topic note-indexed; --json emits one valid document; ask/gold transparency carried by the framing",
    },
    "ritual": {
        "level": 4,
        "note": "the morning loop keeps its pledge: today surfaces yesterday's 'next' (closed?) and the voice's liveness, stage pledges are journaled not evaporated, briefings live apart from decisions",
    },
    "web ui": {
        "level": 4,
        "note": "the face lives: GET / serves a local-only, no-build UI (gold values, Zustand/Heute/Idle/Verdikt/Frage) with per-request nonce-CSP + nosniff and a ui command; verdicts carry gold_source and the reply-read honesty ('recorded, not censored'); the Heute panel unhides with the ledger pulse",
    },
    "net": {
        "level": 4,
        "note": "hub door live: manifest (never fails) + governed spore ingress (fail-closed, audited — denied words recorded, never stored) + spore ledger + curated public/ (secrets hard-excluded, excluded==missing); peering protocol is the next level",
    },
    "oracle": {
        "level": 4,
        "note": "the second eye is live on every verdict surface (cli govern/oracle/ask/trialog, api /govern + /v1/ask, hub spore, agent): an independent advisory vote with its own fresh register (pressure/prying/absolutes, gold resonance DE+EN, whole-word matches) — advisory only: a warning never denies, an agreement never affirms; the boundary rides in the vote, on the manifest, and on the face's auge row; the eye itself has no process key (oracle exits 0 even on warnen)",
    },
}


def infinity_path():
    """Path to the Book of Infinity, resolved through the ecosystem root."""
    return default_alf_root() / SOURCE


def source_available() -> bool:
    return infinity_path().exists()


def assess(domain: str) -> dict:
    """Honest self-assessment: where is this domain breathing right now?

    ``level`` is 1..5, every claim carries a ``note``, and ``name`` is the
    level's title. Unknown domains degrade to Level 1 — Looking — with an
    open question, per the book ("each re-reading is a new Level 1 with new
    questions").
    """
    entry = ASSESSMENTS.get(domain.strip().lower())
    if entry:
        return {
            "domain": domain,
            "name": LEVELS[entry["level"] - 1]["name"],
            **entry,
        }
    return {
        "domain": domain,
        "name": LEVELS[0]["name"],
        "level": 1,
        "note": "new ground — not yet looked at as its own thing",
    }