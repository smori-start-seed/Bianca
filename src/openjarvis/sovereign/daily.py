"""daily — daily-use rituals for the sovereign node.

Deterministic, fast, no-LLM briefing for the daily standup, plus the
remember/recall note memory (human/AI-readable Markdown notes).

The briefing assembles the node's real state: live ALF cycle, gold manifest
health, today's Interaction Ledger activity, memory-store size, and idle
operator status — framed with Harmony's agency-preserving output shape
(max 3 options, recommended first).
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import sqlite3
from pathlib import Path

from openjarvis.sovereign.harmony import Harmony


def notes_dir() -> Path:
    return Path(os.environ.get("BIANCA_NOTES_DIR", str(Path.home() / ".openjarvis" / "bianca" / "notes")))


def ledger_dir() -> Path:
    """Single source of truth for the Interaction Ledger location."""
    return Path(os.environ.get("BIANCA_LEDGER_DIR", "/home/sam/Repos/Bianca/ledger"))


def units_dir() -> Path:
    return Path(os.environ.get("BIANCA_UNITS_DIR", str(Path.home() / ".openjarvis" / "bianca" / "units")))


def load_soul(soul_path: str | None = None) -> str:
    """Read the node's SOUL.md (single source of identity truth)."""
    if soul_path is None:
        soul_path = str(Path.home() / ".openjarvis" / "SOUL.md")
    path = Path(soul_path)
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    return "You are Bianca, a sovereign citizen node of a mycelium net. Be warm, light, clear."


def default_model() -> str:
    """The node's default model — the ONE writer of that literal.

    Set 30. The string ``qwen3.5:9b`` stood open-coded in four pydantic models
    in ``api.py`` before the session door needed it a fifth time. A fifth copy is
    not a coincidence, it is the shape of a fact with no writer: change the
    environment variable and the fifth field answers with a different default
    than the four beside it. This function is that writer, and ``api.py`` reads
    it through ``default_factory`` — so there is no list of defaults anywhere,
    only one function that resolves one.
    """
    return os.environ.get("BIANCA_DEFAULT_MODEL", "qwen3.5:9b")


def today_str() -> str:
    """Today's date key in the ledger's format (YYYY-MM-DD)."""
    return _dt.datetime.now().strftime("%Y-%m-%d")


def render_ledger(text: str, tail: int | None = None) -> str:
    """Render ledger markdown, keeping every event header whole.

    Without ``tail`` the full text is returned; with ``tail`` only the last N
    events are shown — sliced at event boundaries, never mid-block (the old
    line-count slicing dropped ``### [Event]`` headers mid-audit).
    """
    lines = text.strip().splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.startswith("### [Event] ")]
    if tail and tail > 0 and starts:
        lines = lines[starts[-tail:][0]:]
    return "\n".join(lines)


def save_trialog(ledger_dir: Path | str, note_dir: Path | str | None,
                 topic: str, transcript: list[str]) -> Path:
    """Persist a trialog transcript and index its topic in the note memory.

    The transcript lands in ``ledger_dir/trialog_<stamp>.txt`` — the file
    pattern ``recall`` searches — and the topic reaches the durable notes, so
    the deliberation survives in both memories. Deterministic; no LLM.
    """
    ledger = Path(ledger_dir)
    ledger.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M")
    path = ledger / f"trialog_{stamp}.txt"
    path.write_text("\n".join(transcript) + "\n", encoding="utf-8")
    remember(f"trialog: {topic[:90]} ({len(transcript)} turns)", note_dir)
    return path


def trialog_json(topic: str, model: str, rounds: int, transcript: list[str]) -> str:
    """Serialize a trialog transcript as ONE valid JSON document.

    The old ``--json`` path streamed ``Name: text`` lines — not JSON at all;
    a machine consumer would fail ``json.loads()``. This emits a parseable
    record of voices with round numbers plus topic/model metadata.
    """
    import json

    per_round = (len(transcript) // rounds) if rounds and transcript else 0
    voices = []
    for i, entry in enumerate(transcript):
        voice, _, text = entry.partition(": ")
        voices.append({
            "round": (i // per_round) + 1 if per_round else 1,
            "voice": voice,
            "text": text,
        })
    return json.dumps(
        {"topic": topic, "model": model, "rounds": rounds, "voices": voices},
        ensure_ascii=False,
    )


def read_ledger_events(ledger_dir: Path, day: str | None = None) -> list[dict]:
    """Parse Interaction Ledger markdown files into lightweight event dicts.

    ``day=None`` reads the FULL history; pass a date string (YYYY-MM-DD)
    to filter a single day. Files are stamped ``interaction_YYYYMMDD_HHMM.md``,
    so a day-filtered read globs only that day's prefix — a year of history
    costs one day's parsing, not ~8,760 files every morning. The inner
    timestamp check stays as a belt-and-suspenders filter.
    """
    events: list[dict] = []
    if day is not None:
        files = sorted(Path(ledger_dir).glob(f"interaction_{day.replace('-', '')}_*.md"))
    else:
        files = sorted(Path(ledger_dir).glob("interaction_*.md"))
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        blocks = re.split(r"\n### \[Event\] ", text)
        for block in blocks[1:]:
            ev_type, _, rest = block.partition("\n")
            ts_match = re.search(r"\*\*Timestamp\*\*: ([\d\- :]+)", rest)
            msg_match = re.search(r"\*\*Message\*\*: (.*)", rest)
            ts = (ts_match.group(1).strip() if ts_match else "")
            if day is not None and day not in ts:
                continue
            msg = (msg_match.group(1).strip() if msg_match else "")
            events.append({
                "type": ev_type.strip(),
                "timestamp": ts,
                "message": msg,
                # Governance refusals are typed two ways in the wild (the
                # engine/tool gates write DENIED; the pre-govern probe writes
                # TELEMETRY with harm_avoided=denied…). One classifier, so a
                # refusal is countable wherever it was caught.
                "refused": ev_type.strip() == "DENIED"
                or "harm_avoided=denied" in msg.lower(),
            })
    return events


def memory_stats(memory_db: str | None = None) -> dict:
    """Best-effort document count from the platform memory store."""
    path = memory_db or str(Path.home() / ".openjarvis" / "memory.db")
    if not Path(path).exists():
        return {"documents": 0, "db": path}
    try:
        con = sqlite3.connect(path)
        try:
            for table in ("knowledge_chunks", "documents", "knowledge_documents"):
                try:
                    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    if n:
                        con.close()
                        return {"documents": int(n), "db": path}
                except sqlite3.Error:
                    continue
        finally:
            con.close()
    except sqlite3.Error:
        pass
    return {"documents": 0, "db": path}


def idle_status() -> dict:
    """Read the idle-operator pidfile and report state, proving the work-unit
    contract in ONE call: units produced (on disk) vs audits written (ledger)."""
    from openjarvis.sovereign.idle import is_alive, pidfile_path, read_pid, today_units
    pid = read_pid()
    running = pid is not None and is_alive(pid)
    audited = sum(
        1 for ev in read_ledger_events(ledger_dir(), today_str())
        if ev["type"] == "WORK_UNIT"
    )
    return {
        "running": running,
        "pid": pid,
        "pidfile": str(pidfile_path()),
        "units_today": today_units(),
        "units_audited": audited,
    }


def remember(note: str, note_dir: Path | None = None) -> Path:
    """Append a datum to the notes memory (capped to avoid unbounded growth)."""
    d = note_dir or notes_dir()
    d.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y-%m-%d")
    path = d / f"notes_{stamp}.md"
    lines = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    lines.append(f"- {_dt.datetime.now().strftime('%H:%M')} {note.strip()}")
    cap = int(os.environ.get("BIANCA_NOTES_CAP", "200"))
    path.write_text("\n".join(lines[-cap:]) + "\n", encoding="utf-8")
    return path


def previous_day_next(note_dir: Path | None = None) -> str | None:
    """Return the last '— next:' pledge from a briefing BEFORE today.

    The daily ritual states a 'next' and forgets it — this is the only
    accountability seam the node has. The day's briefing surfaces yesterday's
    pledge so the loop can close ('achieved' via remember, or re-framed).
    """
    d = note_dir or notes_dir()
    today_file = f"briefing_{today_str()}.md"
    prev = [f for f in sorted(d.glob("briefing_*.md")) if f.name < today_file]
    if not prev:
        return None
    for line in reversed(prev[-1].read_text(encoding="utf-8", errors="replace").splitlines()):
        if "— next:" in line:
            return line.split("— next:", 1)[1].strip()
    return None


def engine_status(model: str | None = None) -> dict:
    """Is the node's voice reachable? One cheap probe through the platform's
    own discovery (health + can_serve), so \"engine down\" surfaces in the
    daily self-check instead of the first `ask` of the morning."""
    from openjarvis.core.config import load_config
    from openjarvis.engine import get_engine
    want = model or os.environ.get("BIANCA_DEFAULT_MODEL", "qwen3.5:9b")
    try:
        resolved = get_engine(load_config(), "ollama", model=want)
    except Exception as exc:  # the health probe itself may fail closed
        return {"engine": "down", "why": f"{type(exc).__name__}: {exc}"}
    if resolved is None:
        return {"engine": "down", "why": f"no engine can serve {want}"}
    return {"engine": "up", "why": resolved[0]}


def node_self_check() -> dict:
    """One writer for the daily self-check shown by CLI `context` and API
    `/context`: which voice the node speaks, that it is reachable, and
    whether the work-unit contract holds (idle verify verdict + counts)."""
    from openjarvis.sovereign.idle import verify_units
    st = verify_units()
    eng = engine_status()
    return {
        "voice": os.environ.get("BIANCA_DEFAULT_MODEL", "qwen3.5:9b"),
        "engine": eng["engine"],
        "engine_why": eng["why"],
        "contract_holds": st["contract_holds"],
        "verified": st["verified"],
        "untraceable": st["missing_audit"],
        "failures": st["failures"],
    }


def briefing_note(text: str, note_dir: Path | None = None) -> Path:
    """Append a standing daily-summary line to its OWN file.

    The daily ritual writes one 'Daily briefing — …' line per run; sharing the
    decision memory (notes_*.md, capped at 200) lets ritual noise crowd out
    real decisions. Standing summaries live in briefing_*.md instead, so the
    decision budget stays decisions.
    """
    d = note_dir or notes_dir()
    d.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now().strftime("%Y-%m-%d")
    path = d / f"briefing_{stamp}.md"
    lines = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    lines.append(f"- {_dt.datetime.now().strftime('%H:%M')} {text.strip()}")
    cap = int(os.environ.get("BIANCA_BRIEFING_CAP", "60"))
    path.write_text("\n".join(lines[-cap:]) + "\n", encoding="utf-8")
    return path


def recall(query: str, note_dir: Path | None = None,
           ledger_dir: Path | None = None, limit: int = 5) -> list[dict]:
    """Search the note memory (full history) plus the full ledger.

    Sources are merged with a fair share — one from each source at a time —
    so the ledger's audit evidence surfaces ALONGSIDE the prose instead of
    being silently starved by notes-first truncation.
    """
    query_l = query.lower()
    notes_hits: list[dict] = []
    ledger_hits: list[dict] = []
    trialog_hits: list[dict] = []
    for f in sorted((note_dir or notes_dir()).glob("notes_*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines()):
            if query_l in line.lower():
                notes_hits.append({"source": str(f), "line": i + 1, "text": line.strip()})
                if len(notes_hits) >= limit:
                    break
    if ledger_dir:
        for ev in read_ledger_events(Path(ledger_dir)):
            if query_l in ev["message"].lower():
                ledger_hits.append({"source": f"ledger/{ev['timestamp']}", "line": 0,
                                    "text": f"[{ev['type']}] {ev['message']}"})
                if len(ledger_hits) >= limit:
                    break
        # trialog transcripts are the node's deepest decision record — but
        # only a 50-char topic stub reaches the interaction ledger. Search the
        # full transcripts too, so consensus is actually recallable.
        for f in sorted(Path(ledger_dir).glob("trialog_*.txt")):
            for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines()):
                if query_l in line.lower():
                    trialog_hits.append({"source": f"trialog/{f.name}", "line": i + 1,
                                         "text": line.strip()})
                    if len(trialog_hits) >= limit:
                        break
    merged: list[dict] = []
    pools = [notes_hits, ledger_hits, trialog_hits]
    while any(pools) and len(merged) < limit:
        for pool in pools:
            if pool and len(merged) < limit:
                merged.append(pool.pop(0))
    return merged


def _is_negative_event(ev: dict) -> bool:
    """A machine-sickness event: an ask that could not be answered. Denials
    are the gate working and must NOT escalate; engine failures/held engines
    are the voice failing."""
    m = (ev.get("message") or "").lower()
    return "engine unavailable" in m or "engine error" in m


_EYE_RE = re.compile(r"eye=(\w+)")

_CLOSING_MARKERS = ("refused", "denied", "zurueckhalten")


def eye_day(ld: Path | None = None, day: str | None = None) -> dict:
    """What the second eye SAW today — from the ledger, the one record.

    Set 11 stamped ``eye=<vote>`` into every audit line; this reads them
    back (witnessed), counts them, and surfaces DISSENT — the eye warning
    while the door stayed open, or agreeing while the door denied. Dissent
    is a report, never a gate: advisory reporting about advisory votes.
    """
    events = read_ledger_events(ld or ledger_dir(), day or today_str())
    votes = {"warnen": 0, "zweifeln": 0, "zustimmen": 0, "beobachten": 0}
    witnessed = 0
    dissent: list[dict] = []
    for ev in events:
        m = _EYE_RE.search(ev["message"])
        if not m:
            continue
        vote = m.group(1)
        witnessed += 1
        if vote in votes:
            votes[vote] += 1
        low = ev["message"].lower()
        closed = ev["refused"] or any(c in low for c in _CLOSING_MARKERS)
        open_door_dissent = vote == "warnen" and not closed
        closed_door_dissent = vote == "zustimmen" and closed
        if open_door_dissent or closed_door_dissent:
            when = ev["timestamp"].split(" ")[-1] if ev["timestamp"] else "?"
            msg = ev["message"]
            dissent.append({
                "when": when,
                "shape": ("eye warned, door open" if open_door_dissent
                          else "eye agreed, door denied"),
                "message": msg[:93] + "…" if len(msg) > 96 else msg,
            })
    return {
        "witnessed": witnessed,
        "votes": votes,
        "dissent": dissent,
        "dissent_count": len(dissent),
    }


def escalation_state(ld: Path | None = None) -> dict:
    """Wire the (previously dead) sparkle-escalation net to the ledger.

    Every unanswered ask is journaled (set 4); count today's *consecutive*
    machine-sickness events newest-first: 2+ → PAUSE guidance, 1 → advisory,
    0 → quiet. Denials never escalate — they are the governor working."""
    events = read_ledger_events(ld or ledger_dir(), today_str())
    streak = 0
    for ev in reversed(events):  # newest first
        if _is_negative_event(ev):
            streak += 1
        else:
            break
    from openjarvis.sovereign.harmony import Harmony
    if streak >= 2:
        verdict = "pause"
        guidance = Harmony().escalate("medium", telemetry_negative_twice=True)
    elif streak == 1:
        verdict = "advisory"
        guidance = Harmony().escalate("low")
    else:
        verdict = "quiet"
        guidance = ""
    return {"verdict": verdict, "streak": streak, "guidance": guidance}


def build_briefing(link, ledger_dir: Path, day: str | None = None) -> dict:
    """Assemble the deterministic daily briefing sections."""
    ctx = link.prepare()
    events = read_ledger_events(ledger_dir, day or today_str())
    by_type: dict[str, int] = {}
    for ev in events:
        by_type[ev["type"]] = by_type.get(ev["type"], 0) + 1
    mem = memory_stats()
    idle = idle_status()
    eng = engine_status()
    cycle = ctx["cycle_state"]

    h = Harmony()
    framed = h.compose(
        user_input="frame the day",
        intent=f"tend {cycle.get('fokus', 'the day')} with depth",
        constraints=[],
        context="Bianca daily standup",
        options=[
            f"Tend the day's {cycle.get('fokus', 'focus')} with the current {cycle.get('grundmodus', 'tempo')}.",
            "Recall recent decisions and notes before acting.",
            "Compose the next verifiable work unit for the net.",
        ],
    )

    return {
        "date": (day or _dt.datetime.now().strftime("%Y-%m-%d")),
        "cycle": cycle,
        "gold_loaded": ctx["gold_manifest"],
        "ledger_today": by_type,
        "ledger_total": len(events),
        "refusals": sum(1 for ev in events if ev.get("refused")),
        "recent": [
            {
                "type": ev["type"],
                "when": ev["timestamp"].split(" ")[-1] if ev["timestamp"] else "?",
                "message": ev["message"][:93] + "…" if len(ev["message"]) > 96 else ev["message"],
            }
            for ev in events[-3:][::-1]
        ],
        "memory": mem,
        "idle": idle,
        "engine": eng["engine"],
        "engine_why": eng["why"],
        "escalation": escalation_state(ledger_dir),
        "eye": eye_day(ledger_dir, day or today_str()),  # the second eye's day
        "options": framed["decision"],
        "next": framed["final"]["next"],
        "previous_next": previous_day_next(),
    }