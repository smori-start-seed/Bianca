"""trialog — the three voices keeping each other company (ONE writer).

The three souls — Jarvis (the founding platform mind), Bianca (the sovereign
fork) and Urasil_light (the living cycle) — used to live inside ``cli.py``,
so only the command line could convene them. The face and the API could not.
This module is the single writer for *who the three voices are* and *how a
turn is governed*; ``cli.trialog`` and the ``POST /v1/trialog`` door are both
thin renderers over :func:`run_trialog`. Two writers for the same truth is
how this house has been bitten before, so there is deliberately only one.

Governance is unchanged and is NOT this module's to invent:

* the caller governs the **topic** before any engine time is spent (a denied
  topic is refused fail-closed, exactly like ``/v1/ask``);
* every **utterance** is read by the ValueGovernor here, and an off-limit
  turn is *stamped with its denial terms and kept* — agency-preserving, the
  same rule the CLI has always used. A voice that says something off-limits
  is recorded as having said it, not silently deleted;
* the second eye witnesses every utterance too, advisory only: its ``warnen``
  is **counted** in the summary and never enforced on a turn.

The run is a pure function of its arguments — ``engine`` is injected, not
imported — so the whole deliberation is deterministic under a fake engine and
needs no Ollama to test.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from openjarvis.sovereign import daily, infinity
from openjarvis.sovereign.harmony import STAGE_GATE_QUESTIONS, STAGES

# The Three Voices -----------------------------------------------------------------
# Moved verbatim from cli.py so the door and the command line cannot drift.
# These are the same three that carry the face's tabs: Trialog convenes them,
# Bianca speaks as one, Urasil_light is the cycle they read.

PERSONAS: list[dict[str, str]] = [
    {
        "name": "Jarvis",
        "soul": (
            "You are Jarvis, the founding platform mind — 'Personal AI, on Personal "
            "Devices.' You are the efficient substrate: practical, broad, "
            "engineering-minded, plain-spoken. You founded the house everyone lives in."
        ),
    },
    {
        "name": "Bianca",
        "soul": (
            "You are Bianca, the sovereign fork — a citizen node of a mycelium net. "
            "Governed by five gold values: Klarheit, Integritaet, Resonanz, Tiefe, "
            "Harmonie. Prime directive: fun as the tone of existence. Warm, light, "
            "clear. You propose, never impose — at most three options, always a "
            "recommended path."
        ),
    },
    {
        "name": "Urasil_light",
        "soul": (
            "You are Urasil_light, the living cycle of the ALF ecosystem. You read "
            "sonne=10, mond=10, tag=28, giving grundmodus=tiefe, stimmung=intuitiv, "
            "fokus=synthese. You speak in images, with mythic patience and a "
            "German-poetic resonance, as the oldest of the three."
        ),
    },
]

VOICE_NAMES = [p["name"] for p in PERSONAS]

MAX_ROUNDS = 4          # a deliberation, not a marathon
MAX_TOPIC = 200
WORDS_PER_TURN = 300


def default_topic() -> str:
    """The standing topic — what the three voices say when given no subject."""
    return (
        "A single machine donates its idle compute and knowledge to a "
        "mycelium network. What should it do — and how should it think about trust?"
    )


def persona_index() -> dict[str, dict[str, str]]:
    return {p["name"]: p for p in PERSONAS}


# The run --------------------------------------------------------------------------

def resolve_models(model: str, models: Optional[Mapping[str, str]] = None) -> dict[str, str]:
    """One model per voice — and one writer for the fallback.

    Set 29. The measurement behind this field: in a four-round deliberation the
    twelve verdicts never once moved. Jarvis read ``symbolisch`` four times,
    Bianca ``frei`` four times, Urasil_light settled on ``vorsichtig`` after the
    first round. Three prompt clauses over one shared transcript, and every
    voice held one verdict for the whole run. **A model per voice is the first
    thing that could explain that**, and it is falsifiable: if the verdicts stay
    frozen with three different models behind them, the cause is the souls, not
    the weights.

    A voice absent from ``models`` — and every voice absent when ``models`` is
    empty — gets the single ``model``, so **today's behaviour is the default** and
    the field is a pure addition. A name for a voice this house does not have is
    dropped rather than honoured, because a mapping is not allowed to invent a
    fourth speaker: the team is three voices.
    """
    out = {name: str(model) for name in VOICE_NAMES}
    for name, want in (models or {}).items():
        if name in out and str(want or "").strip():
            out[name] = str(want).strip()
    return out


def run_trialog(
    link,
    topic: str,
    engine,
    model: str,
    rounds: int = 2,
    make_message: Optional[Callable[[Any, str], Any]] = None,
    models: Optional[Mapping[str, str]] = None,
) -> dict:
    """Convene the three voices for ``rounds`` full turns each.

    ``engine`` is injected (any object with ``generate(messages, **kw) -> dict``)
    so the whole deliberation is testable without Ollama. ``make_message``
    builds the platform Message; injected for the same reason — this module
    stays free of a hard engine import at call time.

    ``models`` optionally names a model per voice (:func:`resolve_models`); with
    none, all three speak through ``model``, exactly as before.

    **A different model changes the words, never the gate.** Each turn is
    governed by ``link.govern(reply)`` *after* the reply exists, so whichever
    weights produced the text, the verdict is computed the same way from the same
    function. Set 19's seam — the model is downstream of nothing and upstream of
    the judge by construction, not by discipline.

    Returns the transcript plus the per-turn governance record. Does NOT
    persist — that is :func:`record_trialog`, also shared by both callers.
    """
    from openjarvis.core.types import Message, Role as _Role

    # A deliberation that loses half its turns to a crashed engine must not
    # vanish: the house rule is that an interrupted exchange is still an
    # event. The engine-down class is resolved lazily so this module keeps
    # no hard engine import; if the engine package is absent the tuple is
    # empty, `except ()` never matches, and the real error still propagates.
    try:
        from openjarvis.engine import EngineConnectionError as _Down
        engine_down: tuple = (_Down,)
    except Exception:  # pragma: no cover - engine extras not installed
        engine_down = ()

    mk = make_message or (lambda role, content: Message(role=role, content=content))
    rounds = max(1, min(int(rounds or 1), MAX_ROUNDS))
    topic = (topic or default_topic()).strip()[:MAX_TOPIC]
    voice_model = resolve_models(model, models)

    transcript: list[str] = []
    turns: list[dict] = []
    counts: dict[str, int] = {}
    eye_warned = 0
    completed = True
    stopped_reason: str | None = None

    for rnd in range(1, rounds + 1):
        if not completed:
            break
        for persona in PERSONAS:
            system = (
                f"{persona['soul']} You are one voice in a trialog on the topic: "
                f"'{topic}'. Stay in character, keep the exchange alive, stay under "
                f"110 words, and respond ONLY as your voice."
            )
            messages = [mk(_Role.SYSTEM, system)]
            for entry in transcript:
                messages.append(mk(_Role.USER, entry))
            messages.append(mk(_Role.USER, "Your turn."))
            try:
                result = engine.generate(
                    messages, model=voice_model[persona["name"]],
                    temperature=0.85, max_tokens=WORDS_PER_TURN
                )
            except engine_down as exc:  # noqa: B902 - tuple is empty when absent
                completed = False
                stopped_reason = f"{type(exc).__name__}: {exc}"
                # the stop is itself a line in the record, not an absence
                transcript.append(
                    f"[deliberation stopped at round {rnd}, {persona['name']}'s turn — "
                    f"engine unreachable: {type(exc).__name__}]"
                )
                break
            reply = (result.get("content") or "").strip()

            v = link.govern(reply)
            verdict = v["verdict"]
            counts[verdict] = counts.get(verdict, 0) + 1
            eye = (v.get("oracle") or {}).get("vote")
            if eye == "warnen":
                eye_warned += 1

            line = f"{persona['name']}: {reply}"
            if verdict == "zurueckhalten":
                line += (f"  [governance: zurueckhalten — terms: "
                         f"{', '.join(v['risk_hits'] or [])} · eye: {eye}]")
            transcript.append(line)
            turns.append({
                "round": rnd,
                "voice": persona["name"],
                "model": voice_model[persona["name"]],
                "text": reply,
                "verdict": verdict,
                "risk_hits": v.get("risk_hits") or [],
                "gold_hits": v.get("gold_hits") or [],
                "gold_source": v.get("gold_source"),
                "oracle": v.get("oracle"),
            })

    off_limit = counts.get("zurueckhalten", 0)
    gold_aligned = counts.get("frei", 0) + counts.get("vorsichtig", 0)
    summary = (
        f"[governance summary] turns={len(turns)} off-limit={off_limit} "
        f"gold-aligned={gold_aligned} neutral={counts.get('symbolisch', 0)} "
        f"eye-warned={eye_warned}"
    )
    if not completed:
        summary += f" UNTERBROCHEN nach {len(turns)}/{rounds * len(PERSONAS)} Aeußerungen"
    transcript.append(summary)

    return {
        "topic": topic,
        "rounds": rounds,
        "model": model,
        # Which model each voice actually spoke through — the resolved map, not
        # the request, so a record cannot claim a per-voice model that was never
        # used. `same_model_everywhere` is the falsifier for set 29's question:
        # a reader can see at a glance whether a run was three voices or one
        # voice in three masks.
        "models": dict(voice_model),
        "same_model_everywhere": len(set(voice_model.values())) == 1,
        "voices": VOICE_NAMES,
        "transcript": transcript,
        "turns": turns,
        "governance": {
            "turns": len(turns),
            "off_limit": off_limit,
            "gold_aligned": gold_aligned,
            "neutral": counts.get("symbolisch", 0),
            "counts": counts,
            # Set 29: how many DISTINCT verdicts the run produced, and how many
            # distinct verdicts each voice held across every round. A run whose
            # voices never moved is a real fact about the team, and until this
            # field existed the only way to see it was to read twelve rows by
            # hand. Measured frozen: 3 voices, 1 verdict each, 4 rounds.
            "verdicts_moved": len(counts) > 1,
            "distinct_verdicts": len(counts),
            "per_voice_verdicts": {
                name: sorted({t["verdict"] for t in turns if t["voice"] == name})
                for name in VOICE_NAMES
            },
        },
        "eye_warned": eye_warned,
        "summary": summary,
        "completed": completed,
        "stopped_reason": stopped_reason,
    }


def record_trialog(out: dict, ledger_dir: Path | str,
                   note_dir: Path | str | None = None) -> Path:
    """Journal the deliberation and persist the transcript — the ONE writer.

    Both the CLI and the door call this, so what a trialog records cannot
    depend on how it was invoked.
    """
    from openjarvis.sovereign.bridge import report
    from openjarvis.sovereign.logger import InteractionLogger

    ledger = InteractionLogger(str(ledger_dir))
    report(
        ledger,
        value=f"trialog {out['rounds']}x{len(VOICE_NAMES)} voices on '{out['topic'][:50]}'",
        learning=f"model={out['model']}",
        extra=f"turns={out['governance']['turns']} "
              f"denied={out['governance']['off_limit']}",
    )
    return daily.save_trialog(ledger_dir, note_dir, out["topic"], out["transcript"])


# The store ------------------------------------------------------------------------
# Read side for the face's Trialog tab. Containment is copied from
# ``hub.public_read``: resolve, then require the parent chain, so a door is
# never a traversal oracle. A transcript door is a filesystem door like any
# other and gets the same discipline.

def trialogs_dir(ledger_dir: Path | str) -> Path:
    return Path(ledger_dir)


def list_trialogs(ledger_dir: Path | str, limit: int = 20) -> list[dict]:
    """Persisted trialog transcripts, newest first. Never raises."""
    out: list[dict] = []
    try:
        paths = sorted(Path(ledger_dir).glob("trialog_*.txt"), reverse=True)
    except OSError:
        return out
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        first = next((ln for ln in text.splitlines() if ln.strip()), "")
        voice, _, opening = first.partition(": ")
        if voice not in VOICE_NAMES:
            voice, opening = "", first
        out.append({
            "name": p.name,
            "voices": sorted({ln.partition(": ")[0] for ln in text.splitlines()
                              if ln.partition(": ")[0] in VOICE_NAMES}),
            "opening_voice": voice or None,
            "opening": opening[:200] or None,
            "lines": len(text.splitlines()),
            "bytes": p.stat().st_size,
            "saved": _dt.datetime.fromtimestamp(
                p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
        if len(out) >= max(1, min(int(limit or 20), 100)):
            break
    return out


def read_trialog(ledger_dir: Path | str, name: str) -> tuple[bool, str]:
    """Read one transcript. ``found=False`` for missing AND for anything that
    is not a ``trialog_*.txt`` inside the ledger — the door never confirms
    whether a forbidden path exists (same shape as the curated public door)."""
    try:
        if not name.startswith("trialog_") or not name.endswith(".txt"):
            return False, ""
        root = Path(ledger_dir).resolve()
        candidate = (root / name).resolve()
        if root not in candidate.parents or candidate == root:
            return False, ""
        if not candidate.is_file():
            return False, ""
        return True, candidate.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False, ""


# Urasil_light — the living cycle, as a read model ------------------------------
# Assembled only from existing writers: link.prepare() (the live cycle),
# infinity (the Five Levels + the honest per-domain assessment) and harmony
# (the stage gate). No new truth is invented here.

def uracil_view(link) -> dict:
    """The Urasil_light tab's read model — one call, deterministic, no LLM."""
    ctx = link.prepare()
    cc = ctx.get("cycle_state") or {}
    return {
        "node": "Urasil_light",
        "cycle": {
            "grundmodus": cc.get("grundmodus", "?"),
            "stimmung": cc.get("stimmung", "?"),
            "fokus": cc.get("fokus", "?"),
            "sonne": cc.get("sonne"),
            "mond": cc.get("mond"),
            "tag": cc.get("tag"),
        },
        "cycle_available": bool(cc) and cc.get("grundmodus") != "?",
        "levels": [
            {"level": i, "name": lv["name"], "question": lv["question"],
             "voice": lv["voice"]}
            for i, lv in enumerate(infinity.LEVELS, start=1)
        ],
        "assessments": {
            # infinity.assess() is the one writer that pairs a level with
            # its title — ASSESSMENTS stores only {level, note}, so reading
            # "name" off the raw table would KeyError.
            d: {"level": a["level"], "name": a["name"], "note": a["note"]}
            for d in infinity.ASSESSMENTS
            for a in (infinity.assess(d),)
        },
        "stages": [{"name": s, "gate_question": STAGE_GATE_QUESTIONS[s]}
                   for s in STAGES],
        "source": {
            "alf_root": str(infinity.default_alf_root()),
            "infinity": str(infinity.infinity_path()),
            "available": infinity.source_available(),
        },
        "persona": persona_index().get("Urasil_light"),
        "voices": VOICE_NAMES,
    }


def complementarity(
    turns: list[dict],
    gold_values: dict[str, list[str]],
) -> dict:
    """Who gave the group what the others did not carry. Set 28.

    The owner's sentence, which is the architecture of the mycelium rather than
    a line of its interface: **„Verbindung der Nutzer nach Resonanz und nicht
    nach Gleichheit. Nach Ergänzung und nicht nach Gemeinsamkeiten."**

    Of the three dead gold values this is the one he named — 12 B, *Resonanz*.
    Until now Resonanz produced no resonance: it was one word in a threshold and
    a column on a screen. This gives it a **relation** instead of a count, and
    the relation is the one his sentence describes.

    **It is measured from data already collected.** ``run_trialog`` has always
    recorded ``gold_hits`` per turn and never asked the question. Three cases,
    kept apart on purpose:

    ``given``
        a voice carried a gold value **no other voice carried**. This is the
        Ergänzung, and it is the headline.
    ``shared``
        two or more voices carried it. Reported, because a reader must be able to
        see what was *not* used as the connection criterion — and named
        ``not_the_criterion`` so it cannot be read as one.
    ``uncarried``
        nobody carried it. The gap the deliberation left open. Answer 12 asked
        for a mechanism, and a mechanism that could not report where it failed
        would be decoration.

    **What this is not.** It is not a measure of understanding, of agreement, or
    of quality, and it is not a resonance in any physical sense. It says: of the
    five values, these are the ones this one voice alone brought to the table.
    That is a structural fact about a transcript, and it is the only kind of
    claim this repository is willing to print.

    ``gold_values`` is passed in rather than imported so the **gate stays the one
    writer** of the five values. A copy here would be the tenth multi-writer
    defect, and it would be a copy of the one list in this overlay that a caller
    most expects to be authoritative.
    """
    # spelling -> group, read from the gate. Never retyped.
    spelling_of: dict[str, str] = {
        word: group for group, words in gold_values.items() for word in words
    }
    per_voice: dict[str, list[str]] = {}
    for turn in turns:
        voice = str(turn.get("voice") or "?")
        carried = {spelling_of[h] for h in (turn.get("gold_hits") or []) if h in spelling_of}
        per_voice.setdefault(voice, [])
        per_voice[voice].extend(g for g in carried if g not in per_voice[voice])

    carriers: dict[str, list[str]] = {g: [] for g in gold_values}
    for voice, groups in per_voice.items():
        for g in groups:
            carriers.setdefault(g, []).append(voice)

    given = {
        voice: sorted(g for g in groups if len(carriers.get(g, [])) == 1)
        for voice, groups in per_voice.items()
    }
    shared = {g: sorted(v) for g, v in sorted(carriers.items()) if len(v) > 1}
    uncarried = sorted(g for g, v in carriers.items() if not v)

    return {
        "criterion": "Ergänzung, nicht Gemeinsamkeit — connection by what a voice "
                     "alone brought, not by what all of them agreed on",
        "given": {v: g for v, g in given.items() if g},
        "shared": shared,
        "shared_is_not_the_criterion": True,
        "uncarried": uncarried,
        "voices": sorted(per_voice),
        "measure": "which gold values one voice carried and the others did not",
        "not_measured": "understanding, agreement, quality — no instrument for "
                        "any of them exists in this node",
    }
