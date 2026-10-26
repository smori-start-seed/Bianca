"""The working session — a team that stays, until the project is finished.

Set 30. The owner in one sentence: *„Nicht als Anzahl von Runden, sondern als
zielorientiertes Team, dauerhaft aktiv, mit oder ohne User, bis zu einem
erfolgreichen Abschluß dieses Projekts."*

Three things follow from that, and each one was measured before it was built.

**A session is a process, not a request.** Not for responsiveness — the node
answers `/health` in 30–60 ms *while* a 117-second deliberation runs, because
FastAPI runs a sync endpoint in a threadpool. For **lifetime**: an HTTP request
can last twelve hours; a file outlives a browser, a laptop lid and a node
restart. The precedent is `idle_loop` — spawned with ``start_new_session=True``,
pidfile-managed, its state on disk — and the difference is one word: a criterion
instead of a CPU threshold.

**A session carries verdicts, not words.** The prompt grows quadratically in the
round number (measured, R² = 1.0000 against n²: 1 · 3.99 · 8.97 · 15.94), so at
forty rounds a voice would re-read ~100,000 characters of its own earlier prose
in a single call. What it reads instead is :func:`session_memory` — a read model
over ``turns.jsonl`` holding what was *decided*. That is the right thing to carry
for a second reason, and the stronger one: a verdict is the only thing on this
node that a different set of weights cannot move. Set 29 measured that across
three different models and four rounds. So the memory is both cheaper and
*safer* than the transcript, and the second reason is the one that matters.

**The memory is derived, never stored.** There is no ``memory.json``. Everything
:func:`session_memory` reports is recomputed from the record on every read, so it
cannot drift from what was said. Same rule as the two orphan lists in
``idle.verify_units``: what can be derived, is derived; a fact about the record is
**set**.

The completion criterion is a **closed vocabulary of two words**. ``stop_when`` is
mandatory, and anything outside the vocabulary is refused at the seam *with the
list*, because a refusal without alternatives is a dead end:

``idle-contract``
    the node closes it itself when ``idle.verify_units()["contract_holds"]`` — and
    the garden diagnosis travels with the close, because *why* it now holds is
    part of the record.
``owner-accepts``
    the team may propose; only the owner's accept closes it.

The ceiling is **not a third form**. It is mandatory, it is named ``ceiling``, and
reaching it produces the status ``ceiling_reached`` and a record that says, in
words, that the goal was **not** met. A ceiling sold as a goal is the lie
``MAX_UNITS_PER_RUN`` in :mod:`idle` currently does not tell.

And the owner is a voice. ``say`` routes their text through the same
:class:`ValueGovernor` as everything else — a held turn is **refused at the door**
and remembered, never censored into the transcript. The distinction from an
off-limit *voice* turn matters and is deliberate: generated speech that trips the
gate is stamped and kept (it happened, it is evidence), while a *request* that
trips it is deflected (it did not happen, and the mirror says so).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from openjarvis.sovereign.daily import default_model
from openjarvis.sovereign.trialog import (
    MAX_TOPIC,
    PERSONAS,
    WORDS_PER_TURN,
    resolve_models,
)

# ── the two words that can end a session ────────────────────────────────────

#: The whole vocabulary. A free-text criterion would be a judge that nobody
#: built and nobody checked, and set 19 already established that the only judge
#: on this node is the gate. Everything outside this tuple is refused at the seam
#: together with the tuple itself.
SESSION_CRITERIA = ("idle-contract", "owner-accepts")

#: The owner's voice in a session. Not one of :data:`VOICE_NAMES` — a team of
#: three does not grow a fourth seat just because the owner dropped in.
OWNER = "Eigentümer"

INTERVAL = int(os.environ.get("BIANCA_SESSION_INTERVAL", "60"))

#: A mandatory ceiling, in **calls**, not rounds: three voices per round, and a
#: call is what actually costs seconds. The default is twenty rounds' worth.
DEFAULT_CEILING = 60

MAX_GOAL = 400
MAX_SAY = 2000
MAX_ID_LEN = 64


def now() -> str:
    """The session's clock — one writer, so two files cannot disagree on a second.

    Timestamps are facts about the record, and a record with two clocks is a
    record whose ordering is a guess. ``api.py`` reads this rather than opening
    its own ``datetime`` import, because a second clock is the same defect as a
    second writer wearing a different hat.
    """
    return _dt.datetime.now().isoformat(timespec="seconds")


def sessions_dir(ledger_dir: Path | str) -> Path:
    return Path(ledger_dir) / "sessions"


def _safe_id(session_id: str) -> str:
    """Reject anything that could leave the sessions directory.

    A session id reaches a URL and a filesystem path. Allowlist, not a blocklist:
    a blocklist of "dangerous" names is a list someone has to remember to extend,
    and this repository has been finding those lists for fifteen sets.
    """
    sid = (session_id or "").strip()
    if not sid or len(sid) > MAX_ID_LEN:
        raise ValueError("no session id")
    for ch in sid:
        if not (ch.isalnum() or ch in "_-"):
            raise ValueError("a session id is letters, digits, _ and -")
    return sid


def new_id() -> str:
    """Second-resolution stamp plus four hex — a session outlives a minute.

    ``save_trialog`` names its files ``%Y%m%d_%H%M`` and writes them
    unconditionally: two deliberations in the same minute would overwrite each
    other. Measured, 116 files and 116 distinct stamps so far — luck, not design.
    A session lives for hours and appends, so it needs both a finer stamp and an
    append-only file.
    """
    return f"s_{_dt.datetime.now().strftime('%Y%m%d_%H%M')}_{uuid.uuid4().hex[:4]}"


def _paths(ledger_dir: Path | str, session_id: str) -> dict[str, Path]:
    root = sessions_dir(ledger_dir) / _safe_id(session_id)
    return {
        "root": root,
        "state": root / "state.json",
        "turns": root / "turns.jsonl",
        "proposals": root / "proposals.jsonl",
        "inbox": root / "inbox.jsonl",
    }


def pidfile_path(session_id: str) -> Path:
    return Path(os.environ.get(
        "BIANCA_SESSIONS_DIR",
        str(Path.home() / ".openjarvis" / "bianca" / "sessions"),
    )) / f"{_safe_id(session_id)}.pid"


# ── state: one writer ───────────────────────────────────────────────────────

def new_state(topic: str, goal: str, stop_when: str, ceiling: int,
              model: str, models: Optional[Mapping[str, str]] = None) -> dict:
    return {
        "id": "",
        "topic": topic,
        "goal": goal,
        "stop_when": stop_when,
        "ceiling": int(ceiling),
        "model": model,
        "models": dict(resolve_models(model, models)),
        "voices": [p["name"] for p in PERSONAS],
        "status": "new",
        "started": now(),
        "closed": None,
        "closed_because": None,
        #: A *request* to stop, not a fact about the close — see :func:`halt`.
        "stop_requested": None,
        #: Who wrote the close. A person's decision here outranks a process exit.
        "closed_by": None,
        #: Whether this run has installed its stop handler **yet**. The first
        #: `ready` appears ~50 ms after spawn (interpreter start), and in that
        #: window a SIGTERM hits Python's default disposition and kills the
        #: process: measured, 3 of 14 spawns with the signal delayed 0–0.04 s.
        #: So the run announces when it can hear, and the door signals only then.
        #: The request itself is in the record either way — this is about the
        #: nudge, never about the request.
        "ready": False,
        "pid": None,
        # 🚨 NO `calls` and NO `rounds` here, and their absence is the point.
        # They were, and a session killed between the append and the state write
        # left them disagreeing with the record they claim to count: one turn on
        # disk in `turns.jsonl`, `calls: 0` beside it in `state.json`. Two counts
        # of one thing, one of them invented — the shared-count shape this repo
        # keeps finding. They are now **derived** from the record on every read,
        # by :func:`session_memory`, and a kill cannot desynchronise a number
        # that was never stored.
    }


def write_state(ledger_dir: Path | str, state: Mapping[str, Any]) -> Path:
    """Persist the state — the ONE writer of ``state.json``."""
    p = _paths(ledger_dir, str(state["id"]))["state"]
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(dict(state), ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(tmp, p)
    return p


def patch_state(ledger_dir: Path | str, session_id: str, **changes: Any) -> Optional[dict]:
    """Change **only** the named fields, on a freshly read state.

    🚨 This function exists because of a defect this set measured, and the
    measurement is the reason it is worth reading. The run loop held one
    ``state`` dict from the top of a round and wrote it back at the end. In
    between, the ``say`` door spawned the process and wrote ``pid`` into the file
    — and the loop's write, made from a copy taken *before* the door's, put
    ``pid`` back to ``None``. Result: a session that was demonstrably running,
    with its pid in the pidfile and its process alive, reported ``pid: null`` in
    the only file that says what the session is. The fix is not "write more
    carefully"; it is **write only what you changed**, so a writer that read the
    file a minute ago cannot undo a writer that read it a second ago.

    That is the shared-count defect's third cousin, and it is why the repository
    keeps meeting it: two writers, one of them holding a stale read. The counters
    went in set 30's first hour (derived instead of stored); the pid went here.
    """
    state = read_state(ledger_dir, session_id)
    if state is None:
        return None
    state.update(changes)
    write_state(ledger_dir, state)
    return state


def read_state(ledger_dir: Path | str, session_id: str) -> Optional[dict]:
    """The state, or ``None``. Never raises — a door is not a crash report."""
    try:
        p = _paths(ledger_dir, session_id)["state"]
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError):
        return None


# ── turns: append-only, one writer ──────────────────────────────────────────

def append_turn(ledger_dir: Path | str, session_id: str, turn: Mapping[str, Any]) -> Path:
    """Append one utterance **whole** — verdict, terms, gold source and eye.

    🚨 Why whole: measured on a real capture, a turn without its text is 337
    characters against 270 characters of text — **55 % of the record is evidence**,
    and the flat ``trialog_*.txt`` archive keeps only the other 45 %. A session has
    a duty of proof; this is the whole duty, one line at a time.

    🚨 And whole means **refused without it**: a turn that carries no verdict and
    no reason for carrying none is raised on, not quietly written. See below.
    """
    p = _paths(ledger_dir, session_id)["turns"]
    genannt = turn.get("verdict")
    # 🚨 The turn's verdict is a **name**, with the evidence in its siblings
    # (`risk_hits`, `gold_hits`, `gold_source`, `oracle`) — that is the shape the
    # loop writes, the door serves and the caller's type declares, checked
    # against a real capture rather than a memory of one. A whole dict is
    # accepted as well, because accepting both costs one line and refusing the
    # shape a future writer would plausibly use would be a guard that fails for
    # the wrong reason.
    name = genannt.get("verdict") if isinstance(genannt, Mapping) else genannt
    gescheitert = bool(str(turn.get("stopped") or "").strip())
    if not str(name or "").strip() and not gescheitert:
        # 🚨 Set 30 found this in the writer of the newest file, and it is the
        # set-16/17/18 defect again: a line that cannot say what the governor
        # thought reached the record. `record_grown` grew the same guard after
        # its own test caught `"verdict": null`; a turn is the same kind of fact
        # and had no guard at all. Refused here, at the door, rather than
        # filtered on the way out — a reader of the file is a reader of the
        # record, and the record has to be checkable on its own.
        #
        # 🚨 **Or it says why there is none.** The guard was first written as
        # "a verdict, or nothing", and it broke the engine-down path: that branch
        # writes `"verdict": ""` beside a `stopped` reason, because there *was*
        # no answer to judge. A check that refuses that line takes down the one
        # path that must never go down — the comment in `session_loop` says so
        # at the very branch. So the second half of the rule is as
        # load-bearing as the first: a turn may carry no verdict **only** by
        # naming what happened instead, and then it is a fact about a failed
        # call rather than a silent gap in a record.
        #
        # Deliberately *not* a check against a list of verdict names: that name
        # is a literal in ten places with no single writer, and restating it
        # here would be the eleventh. Requiring a truthy one closes the hole
        # without inventing a vocabulary nobody owns.
        raise ValueError(
            "a turn must carry the verdict it was given, or say in `stopped` why "
            "there is none — a line that can say neither is not a record"
        )
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(turn), ensure_ascii=False) + "\n")
    return p


def read_turns(ledger_dir: Path | str, session_id: str) -> list[dict]:
    out: list[dict] = []
    try:
        raw = _paths(ledger_dir, session_id)["turns"].read_text(encoding="utf-8")
    except OSError:
        return out
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            # A torn last line is a fact about the record, not a reason to lose
            # the whole thing; skip it and let the count show the gap.
            continue
    return out


def append_proposal(ledger_dir: Path | str, session_id: str,
                    proposal: Mapping[str, Any]) -> Path:
    p = _paths(ledger_dir, session_id)["proposals"]
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(proposal), ensure_ascii=False) + "\n")
    return p


def read_proposals(ledger_dir: Path | str, session_id: str) -> list[dict]:
    """The proposals, **one per round** — the last line for a round wins.

    🚨 Append-only is right for a record, and wrong for a *state*. The file holds
    one line when the team proposes and another when the owner closes, and
    without this collapse `read_proposals` returned both: measured, a reader saw
    ``round=1 closed=False`` beside ``round=1 closed=True`` with nothing saying
    which was current, and the door's own `open_ones` filter then matched the
    stale open line — so a **second** `accept` on an already-closed session
    answered 200 and appended a third line. An open door that reads as closed is
    the same shape as the hub receipt that carried two verdicts under one key,
    and the repair is the same: the current form wins, and the file keeps both.

    Order is by first appearance, so a round's place in the list is where the
    team put it, not where the owner later appended.
    """
    out: list[dict] = []
    stellen: dict[Any, int] = {}
    try:
        raw = _paths(ledger_dir, session_id)["proposals"].read_text(encoding="utf-8")
    except OSError:
        return out
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            p = json.loads(line)
        except ValueError:
            continue
        schluessel = p.get("round")
        if schluessel in stellen:
            out[stellen[schluessel]] = p
        else:
            stellen[schluessel] = len(out)
            out.append(p)
    return out


# ── the inbox: where the owner drops in ──────────────────────────────────────

def say(ledger_dir: Path | str, session_id: str, text: str) -> Path:
    """Leave one utterance for the running session. Append-only, no fsync games."""
    p = _paths(ledger_dir, session_id)["inbox"]
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": now(),
                             "text": text}, ensure_ascii=False) + "\n")
    return p


def read_inbox(ledger_dir: Path | str, session_id: str) -> list[dict]:
    out: list[dict] = []
    try:
        raw = _paths(ledger_dir, session_id)["inbox"].read_text(encoding="utf-8")
    except OSError:
        return out
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def consume_inbox(ledger_dir: Path | str, session_id: str) -> list[dict]:
    """Take whatever the owner left, and say what was taken.

    Read *then* clear, in that order, in one place: the loop needs the text and
    must not consume it twice, and an order that lives in two functions is an
    order that can be wrong in one of them. Returns the utterances so the caller
    can record them — clearing before recording would lose a turn.
    """
    items = read_inbox(ledger_dir, session_id)
    if not items:
        return []
    try:
        _paths(ledger_dir, session_id)["inbox"].write_text("", encoding="utf-8")
    except OSError:
        return []  # could not clear, so the next round would read it again
    return items


# ── the memory: a read model, never a file ──────────────────────────────────

def session_memory(turns: list[Mapping[str, Any]]) -> dict:
    """What this session has **decided** — derived from the record, on every read.

    There is no ``memory.json`` and there must not be one: a stored memory is a
    second copy that can disagree with the turns it claims to summarise, and this
    repository has been finding exactly that shape — the two orphan lists, the
    ``allowed`` next to the verdict it was derivable from, the
    ``per-voice`` count hiding a subset. So nothing here is stored.

    What it deliberately does **not** contain is any measure of understanding,
    agreement or quality. ``cannot_record`` is required for the same reason
    ``record_grown`` requires one: no instrument for that exists here, and a
    field that claimed otherwise would be the mirror's own defect one layer down.
    """
    voices = [p["name"] for p in PERSONAS]
    per_voice: dict[str, list[str]] = {v: [] for v in voices}
    per_voice_models: dict[str, str] = {}
    gold_carried: dict[str, list[str]] = {}
    last_text: dict[str, str] = {}
    counts: dict[str, int] = {}
    eye_warned = 0
    rounds = 0
    owner_turns = 0
    held_owner = 0

    for t in turns:
        voice = str(t.get("voice") or "")
        verdict = str(t.get("verdict") or "")
        if not voice or not verdict:
            continue
        rnd = int(t.get("round") or 0)
        rounds = max(rounds, rnd)
        if voice == OWNER:
            owner_turns += 1
            if verdict == "zurueckhalten":
                held_owner += 1
            continue
        per_voice.setdefault(voice, []).append(verdict)
        counts[verdict] = counts.get(verdict, 0) + 1
        if t.get("model"):
            per_voice_models[voice] = str(t["model"])
        for g in (t.get("gold_hits") or []):
            gold_carried.setdefault(voice, [])
            if g not in gold_carried[voice]:
                gold_carried[voice].append(str(g))
        if ((t.get("oracle") or {}).get("vote")) == "warnen":
            eye_warned += 1
        if t.get("text"):
            last_text[voice] = str(t["text"])

    return {
        "rounds": rounds,
        "calls": sum(counts.values()),
        "counts": counts,
        "distinct_verdicts": len(counts),
        "verdicts_moved": len(counts) > 1,
        "per_voice_verdicts": {v: vs for v, vs in per_voice.items() if vs},
        "per_voice_models": per_voice_models,
        "gold_carried": gold_carried,
        "eye_warned": eye_warned,
        "owner_turns": owner_turns,
        "held_owner_turns": held_owner,
        "last": last_text,
        "carries": ("verdicts, gold values carried, and the last sentence of each "
                    "voice — not the transcript, which grows quadratically and "
                    "would have a voice re-read ~100,000 characters of its own "
                    "prose by round forty"),
        "cannot_record": ("whether anything was understood — no instrument for that "
                          "exists in this node, and a field claiming it would be a "
                          "fiction in a file whose whole purpose is evidence"),
    }


def memory_brief(memory: Mapping[str, Any]) -> str:
    """The memory as a voice reads it: what was decided, and nothing else."""
    if not memory.get("calls"):
        return "Nothing has been decided yet. This is the first round."
    bits = [f"{memory['calls']} utterances in {memory['rounds']} rounds"]
    for voice, verdicts in (memory.get("per_voice_verdicts") or {}).items():
        carried = ", ".join((memory.get("gold_carried") or {}).get(voice, []))
        line = f"{voice}: {', '.join(verdicts)}"
        bits.append(line + (f" (carried {carried})" if carried else ""))
    if memory.get("eye_warned"):
        bits.append(f"the second eye warned {memory['eye_warned']} times (advisory)")
    return " | ".join(bits)


# ── the proposal: a condition on the verdicts, and the owner's decision ─────

def all_voices_freeliest(turns: list[Mapping[str, Any]]) -> bool:
    """Did every voice hold a gold-aligned verdict in the **last** round?

    This is the *trigger* for a completion proposal, and it is deliberately a
    condition on the **governance record**, not on any voice's opinion of itself.
    A model saying "we are done" is a model judging itself; Set 19 already fixed
    where the judge lives. What this says is: *the gate held nothing and warned
    nobody, in the last round every voice spoke* — which is a fact, and a narrow
    one. It is not understanding, and :func:`session_memory` says so in a
    required field.
    """
    if not turns:
        return False
    voices = [p["name"] for p in PERSONAS]
    last_round = max((int(t.get("round") or 0) for t in turns), default=0)
    if last_round < 1:
        return False
    held: dict[str, bool] = {}
    for t in turns:
        if int(t.get("round") or 0) != last_round:
            continue
        voice = str(t.get("voice") or "")
        if voice not in voices:
            continue
        held[voice] = str(t.get("verdict") or "") in ("frei", "vorsichtig")
    return all(held.get(v) for v in voices) and len(held) == len(voices)


# ── the read side for both surfaces ─────────────────────────────────────────

def is_running(session_id: str) -> Optional[int]:
    """The live pid, or ``None``.

    Delegates to :func:`idle.is_alive` with **this** module's name. Set 24 found
    that ``os.kill(pid, 0)`` answers a zombie, and the repair was to read the
    cmdline — but that check was nailed to the string ``openjarvis.sovereign.idle``,
    so a live session would have read ``running: no``. A false *negative* is the
    safe direction and still a lie; the name is a parameter, and there is one
    implementation.
    """
    from openjarvis.sovereign.idle import is_alive, read_pid

    pid = read_pid(pidfile_path(session_id))
    if pid and is_alive(pid, module="openjarvis.sovereign.session"):
        return pid
    return None


def read_session(ledger_dir: Path | str, session_id: str) -> Optional[dict]:
    """Everything one session is: state, turns with evidence, memory, proposals.

    A missing session and a broken one look identical from outside — ``None`` —
    so a door is never an existence oracle over the filesystem.
    """
    state = read_state(ledger_dir, session_id)
    if state is None:
        return None
    turns = read_turns(ledger_dir, session_id)
    return {
        "state": state,
        "turns": turns,
        "memory": session_memory(turns),
        "proposals": read_proposals(ledger_dir, session_id),
        "inbox": len(read_inbox(ledger_dir, session_id)),
        "running": is_running(session_id),
    }


def list_sessions(ledger_dir: Path | str, limit: int = 50) -> dict:
    """All sessions, **grouped by topic** — the owner's words, taken literally.

    One list, sorted under its topic, so a session is *under* the thing it is
    about rather than in a flat feed of runs. ``by_topic`` keeps the grouping and
    ``sessions`` keeps the order, because a screen wants one and a reader wants
    the other; neither is derived by the caller.
    """
    out: list[dict] = []
    root = sessions_dir(ledger_dir)
    cap = max(1, min(int(limit or 50), 200))
    try:
        states = sorted(root.glob("*/state.json"), reverse=True)
    except OSError:
        return {"sessions": [], "by_topic": {}, "topics": 0}
    for p in states:
        try:
            state = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        turns = read_turns(ledger_dir, str(state.get("id") or ""))
        memory = session_memory(turns)
        # One liveness read, used for both fields. Two reads of a question that
        # can change between them would let a single row say "running" and "not
        # running" at once — and that is not a race worth having in a list.
        live = is_running(str(state.get("id") or ""))
        out.append({
            "id": state.get("id"),
            "topic": state.get("topic"),
            "goal": state.get("goal"),
            "stop_when": state.get("stop_when"),
            "status": state.get("status"),
            "started": state.get("started"),
            "rounds": memory["rounds"],
            "calls": memory["calls"],
            "ceiling": state.get("ceiling"),
            # the same derived count, compared to the plan — never a number that
            # was kept beside the record and could drift from it
            "at_ceiling": (memory["calls"] >= int(state.get("ceiling") or 0)),
            "models": state.get("models"),
            # 🚨 `running` is a BOOLEAN on every door, and the pid is its own
            # field. The list used to put the pid here — `running: 323634` — while
            # the detail door put `running: true` in the same field name, so one
            # question had two answer types across two doors and neither screen
            # could be written once. The pid is not a truthiness question and the
            # liveness is not an identity; they are two fields now.
            "running": bool(live),
            "pid": live,
            # 🚨 A stop that was asked for and never answered. This one IS
            # reproducible: a process killed with SIGKILL (or one whose machine
            # went away) leaves a `stop_requested` in `state.json` that no run
            # ever acted on, and the list would say `new` / not running — which
            # reads as a session that simply never began. A record in which a
            # request was made and nothing came of it is a fact, and hiding it
            # behind a clean `new` is the mirror with one half: the door
            # answered "it closes at the next voice boundary" and the boundary
            # never came. Surfaced rather than repaired silently — the run is
            # dead, and nobody should have to guess whether it stopped or died.
            "stop_asked_not_answered": bool(state.get("stop_requested")) and not live,
        })
        if len(out) >= cap:
            break
    by_topic: dict[str, list[dict]] = {}
    for row in out:
        by_topic.setdefault(str(row["topic"] or "(ohne Thema)"), []).append(row)
    return {"sessions": out, "by_topic": by_topic, "topics": len(by_topic)}


# ── the seam: what may start a session ──────────────────────────────────────

def refused_reason(topic: str, goal: str, stop_when: str) -> Optional[str]:
    """Why this session may not start, or ``None``.

    Checked before anything is created, so a refused session leaves no directory
    and no half-written state. The empty criterion is a **refusal, not a
    default**: a session without a completion condition is a run that ends for
    reasons nobody wrote down, which is the thing this whole module exists
    against.
    """
    if not (topic or "").strip():
        return "no topic — a session is about something"
    if not (stop_when or "").strip():
        return ("no completion criterion. A session without one is a run that "
                "stops for reasons nobody wrote down. Choose: "
                + ", ".join(SESSION_CRITERIA))
    if stop_when not in SESSION_CRITERIA:
        return (f"'{stop_when}' is not a criterion this node can check. "
                f"It closes a session on a word, not on a model deciding it is "
                f"finished. Choose: {', '.join(SESSION_CRITERIA)}")
    if not (goal or "").strip():
        return "no goal — a team without an aim is three conversations in turn"
    return None


def create(ledger_dir: Path | str, topic: str, goal: str, stop_when: str,
           ceiling: int = DEFAULT_CEILING, model: str = "",
           models: Optional[Mapping[str, str]] = None) -> dict:
    """Create the session directory. The caller has already governed the words."""
    topic = (topic or "").strip()[:MAX_TOPIC]
    goal = (goal or "").strip()[:MAX_GOAL]
    state = new_state(topic, goal, stop_when, ceiling,
                      model or default_model(), models)
    state["id"] = new_id()
    write_state(ledger_dir, state)
    return state


def close(ledger_dir: Path | str, session_id: str, status: str, because: str,
          by: str = "process") -> dict:
    """Close a session with **both** the status and the sentence, always together.

    ``ceiling_reached`` is not ``complete``, and the sentence says so: *the goal
    was not met*. A status a reader can misread as success, without a sentence
    that cannot be misread, is the `dev262` shape with a smaller blast radius.

    🚨 It refuses a status that is a **question**. ``awaiting_owner`` is what the
    loop writes when the team proposes a close and the owner has not yet spoken;
    written here it stamped ``closed`` and ``closed_by: "process"``, and the
    acceptance door — the one door that exists to hear the owner — then refused
    it with *already closed*. Measured, on a throwaway ledger. The question is
    written with :func:`patch_state` instead, and this function is the writer of
    closes and nothing else.

    ``by`` records **who closed it** — ``process``, ``owner``, ``door`` — and it
    is not bookkeeping. It is the test the loop applies to itself before writing
    (see :func:`session_loop`): a run that woke up to find the session already
    closed by a person must not overwrite a human's decision with its own exit
    code. Without that, ``accept`` racing a slow model call would end with
    ``stopped`` where the owner wrote ``complete``, and the record would depend on
    which of the two was slower.
    """
    state = read_state(ledger_dir, session_id)
    if state is None:
        raise KeyError(session_id)
    # 🚨 A *question* may not be written as a close, and the guard is a prefix
    # rather than a list on purpose: a list of "statuses that are not closes"
    # would be a second vocabulary with no single writer, and the next person to
    # invent a status would have to remember to extend it. `awaiting_` says what
    # it means — a state in which somebody is being asked for something.
    if str(status).startswith("awaiting_"):
        raise ValueError(
            f"{status!r} is a question, not a close — write it with patch_state() "
            "so no reader counts it as finished"
        )
    state["status"] = status
    state["closed"] = now()
    state["closed_because"] = because
    state["closed_by"] = by
    state["stop_requested"] = None
    state["pid"] = None
    write_state(ledger_dir, state)
    return state


# ── the process ─────────────────────────────────────────────────────────────

def criterion_met(ledger_dir: Path | str, state: Mapping[str, Any]) -> tuple[bool, str]:
    """Has the session's own criterion been met? ``(met, why)`` — why always.

    For ``owner-accepts`` this is *always* ``False`` inside the loop: that
    criterion is closed by a human at a door, and the process must not be able to
    close its own session by running long enough. The ``why`` says so, so the
    record carries the reason instead of an absence.
    """
    if state.get("stop_when") == "idle-contract":
        from openjarvis.sovereign.idle import verify_units

        try:
            v = verify_units(ledger_dir)
        except Exception as exc:  # noqa: BLE001 - the door must not die on it
            return False, f"the idle contract could not be read: {type(exc).__name__}"
        if v.get("contract_holds"):
            return True, (f"idle contract holds: {v.get('verified')} verified, "
                          f"{v.get('tampered')} tampered, "
                          f"{len(v.get('orphan_audits_unreconciled') or [])} unreconciled orphans")
        return False, (f"idle contract does not hold yet: {v.get('failures')} "
                       f"failures, garden {v.get('garden', {}).get('can_evolve')}")
    return False, ("the criterion is the owner's acceptance — this process cannot "
                   "close its own session, only the owner can")


#: Set by the stop handler below. **Module level, and read fresh at every check
#: — never copied into a local.** Both halves of that sentence were defects this
#: set found, and they are different defects:
#:
#: *Copied into a local* — the loop did ``stop = STOP`` once at entry, and the
#: handler wrote the module variable, so every SIGTERM arriving while the loop was
#: already running set a flag nobody read. That one is reproducible and is why
#: there is no local any more.
#:
#: *Module level at all* — so a signal that arrives while the engine is still
#: being built is rememberable by a loop that has not started. See
#: :func:`install_stop_handler` for what that does and does not buy, and for the
#: measurement that appeared to justify it and turned out to be invalid.
STOP = False


def _set_stop() -> None:
    """Ask the run to stop from **inside** the process, not by a signal.

    One writer for the flag: the signal handler and the engine-failure path both
    go through here, so there is a single line that says what "stop" means. Two
    writers for a boolean is the smallest version of the defect this repository
    keeps finding, and it is not smaller for being small.
    """
    global STOP
    STOP = True


def _request_stop(signum: int = 0, _frame: Any = None) -> None:
    """Ask the run to stop. Never raises, never closes, never judges."""
    _set_stop()


def install_stop_handler() -> None:
    """Put the handler in place before the engine is built, not after.

    🚨 This is **hardening, and I am labelling it as such because the
    measurement that appeared to justify it turned out to be invalid.** What I
    measured first: imports take 1.86 s and ``get_engine`` 0.52 s on this host, so
    a handler installed inside the loop goes live ~2.4 s after spawn, and four
    SIGTERMs delivered between 0.2 s and 3.0 s left four sessions ``new`` with an
    unanswered ``stop_requested`` and a zero-byte log. That looked like a clean
    finding. It was not: the measuring loop deleted the ledger directory
    underneath each running process, so the process could not have written a close
    to a path that no longer existed. The re-measurement — one ledger, nothing
    deleted, five sessions, SIGTERM at 0.2 / 0.8 / 2.0 / 4.0 / 8.0 s — closed all
    five, each with the owner's own reason in the sentence. So the window was
    never a window.

    Two things survived that mistake, and both are real:

    1. The handler now goes in **before** the heavy work. It is the right place
       on its own merits, and it costs nothing.
    2. A SIGTERM during the engine build has to be *rememberable* by a loop that
       has not started, which is why the flag is module level.

    And one thing was a genuine defect found on the way, which the invalid
    measurement had hidden: the loop read the flag into a **local** once at entry
    and the handler wrote the module variable, so every signal that arrived while
    the loop was already running was ignored. That one is reproducible and is the
    reason `stop = STOP` is gone.
    """
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _request_stop)
        except (ValueError, OSError):  # not the main thread — nothing to install
            pass


def session_loop(
    ledger_dir: Path | str,
    session_id: str,
    stop_after: Optional[int] = None,
    make_message: Optional[Callable[[Any, str], Any]] = None,
    engine: Any = None,
    max_rounds: int = 64,
) -> int:
    """Run the session until its criterion, its ceiling, or a signal.

    Returns the status it closed with. Every exit writes a state and a sentence:
    a session that vanished would be the one failure this node's whole ledger
    exists to prevent, and the version of it that matters is the version where
    the process was killed between rounds.
    """
    # BEFORE the heavy imports, not after them. See `install_stop_handler`.
    install_stop_handler()
    # …and now, and only now, this run can be asked to stop. The record says so,
    # so a door knows whether a signal would be heard or merely fatal.
    patch_state(ledger_dir, session_id, ready=True, ready_at=now())

    from openjarvis.core.types import Message, Role as _Role
    from openjarvis.engine import get_engine
    from openjarvis.core.config import load_config
    from openjarvis.sovereign.link import default_link

    state = read_state(ledger_dir, session_id)
    if state is None:
        raise KeyError(session_id)
    if engine is None:
        resolved = get_engine(load_config(), "ollama", model=state.get("model"))
        if resolved is None:
            close(ledger_dir, session_id, "engine_down",
                  "no inference engine is available on this node")
            return 2
        engine = resolved[1]
    link = default_link()
    mk = make_message or (lambda role, content: Message(role=role, content=content))

    # 🚨 NO local copy of the stop flag. This loop had `stop = STOP`, read once
    # at entry, and the handler wrote the *module* variable — so a SIGTERM
    # delivered while the loop was already running set a flag nobody read, and
    # the run carried on to its ceiling. Measured: four sessions, four SIGTERMs
    # between 0.2 s and 3.0 s, four of them still `new` with a `stop_requested`
    # nobody answered. Reading the global at every check is the fix, and a local
    # copy of a shared flag is the shape this repository has now met three times
    # this set: stale counters, a stale pid, a stale flag. All three were a copy
    # of something that had moved.

    engine_down: tuple = ()
    try:
        from openjarvis.engine import EngineConnectionError as _Down
        engine_down = (_Down,)
    except Exception:  # pragma: no cover - engine extras not installed
        engine_down = ()

    def _stop_sentence(rnd: int) -> str:
        """Why the run stopped — the owner's words if he gave any, else the signal.

        A stop requested through the door carries a **reason**, and that reason is
        the whole point of the door: ``stopped`` alone says nothing about whether
        the owner was satisfied, ran out of patience, or went to bed. The reason
        travels into the record verbatim, and the round it was honoured in is
        named, because a stop that took three seconds and one that took three
        minutes are not the same event.
        """
        req = (read_state(ledger_dir, session_id) or {}).get("stop_requested")
        if isinstance(req, dict) and req.get("reason"):
            return (f"the owner asked for it: {req['reason']} — honoured in round "
                    f"{rnd}, at the next voice boundary")
        return f"stopped by a signal in round {rnd}"

    status, because = "stopped", "stopped by a signal before any round"
    rounds_done = 0
    for rnd in range(1, max_rounds + 1):
        # 🚨 Read the state at the TOP of the round, before writing anything.
        # The last-writer check at the end of the loop was one write too late:
        # the per-round `status = "running"` had already resurrected a session
        # the owner had closed, and the file ended up saying `running` with
        # `closed_by: owner` — two halves of a close, one of them overwritten.
        # Measured, not reasoned: exactly that came out of the check. A person
        # closed the session while the process was in a model call; the process
        # woke up, wrote `running`, and its own end-of-run check then found a
        # close it had not made and stepped aside — too late, because the damage
        # was a write in the middle. So the check comes first here, and the
        # end-of-run check stays as the second line of defence.
        fresh = read_state(ledger_dir, session_id) or {}
        if fresh.get("closed_by") not in (None, "process"):
            status, because = "stopped", (
                f"the owner closed this session ({fresh.get('closed_because')}) "
                f"while the team was at work; the run ended without touching it")
            break
        state = fresh
        if STOP or state.get("stop_requested"):
            status, because = "stopped", _stop_sentence(rnd)
            break

        # ── the owner's turn, if there is one ─────────────────────────────
        # It is governed like anything else, and written into the record with
        # its verdict. The door refuses a held turn before it reaches here
        # (a *request* is deflected), so a `zurueckhalten` on the owner's line
        # means the door was bypassed — it is kept, stamped, and counted, not
        # dropped. Two lines of defence, and the record shows which one fired.
        owner_text = ""
        for item in consume_inbox(ledger_dir, session_id):
            raw = str(item.get("text") or "").strip()[:MAX_SAY]
            if not raw:
                continue
            ov = link.govern(raw)
            append_turn(ledger_dir, session_id, {
                "round": rnd,
                "voice": OWNER,
                "at": item.get("at") or now(),
                "model": None,
                "text": raw,
                "verdict": ov["verdict"],
                "risk_hits": ov.get("risk_hits") or [],
                "gold_hits": ov.get("gold_hits") or [],
                "gold_source": ov.get("gold_source"),
                "oracle": ov.get("oracle"),
            })
            # No counter here either: the owner's turn is a line in the record,
            # and the record is where counts come from. It also does not count
            # against the ceiling, which is measured in **model calls** — an
            # owner's sentence costs no seconds, and a budget that charged for
            # it would be charging for the wrong thing.
            if ov["verdict"] != "zurueckhalten":
                owner_text = raw
            else:
                owner_text = (f"{OWNER} said something this node holds "
                              f"({', '.join(ov.get('risk_hits') or [])}) — recorded, "
                              f"not answered")

        turns_now = read_turns(ledger_dir, session_id)
        memory = session_memory(turns_now)

        # The count is re-derived from the record every round and carried in a
        # LOCAL, so a process killed mid-round cannot leave a number in the
        # state that disagrees with the turns beside it. `made` is voice turns
        # only, because the ceiling is measured in model calls.
        made = memory["calls"]
        turns_of_round = 0
        for persona in PERSONAS:
            # 🚨 Re-read before every voice, not once per round. The stop is
            # asked for through a door while the process is inside a model call,
            # and the first version held `state` from the top of the round — so a
            # stop given in the middle of round 1 was honoured at the start of
            # round 2, not at the next voice boundary as `halt()` promises in its
            # own sentence. Measured: a stop asked for during a 9B call waited
            # three further calls. A sentence that overstates how fast something
            # happens is the `dev262` shape, so the read moved down to where the
            # promise is kept: one small file read per voice.
            fresh = read_state(ledger_dir, session_id) or state
            if fresh.get("stop_requested") and not state.get("stop_requested"):
                state = fresh
            if STOP or state.get("stop_requested"):
                break
            # the ceiling is in calls, so it is honoured *here* — before the
            # next call, not after the round. A round is three calls, and a
            # ceiling of four must not silently become six.
            if made >= int(state["ceiling"]):
                break
            name = persona["name"]
            system = (
                f"{persona['soul']} You are one voice in a working session on the "
                f"topic '{state['topic']}'. The team's aim is: {state['goal']}. "
                f"Stay in character and stay under 110 words. Respond ONLY as your "
                f"voice."
            )
            messages = [mk(_Role.SYSTEM, system)]
            messages.append(mk(_Role.USER, f"What has been decided so far: {memory_brief(memory)}"))
            if owner_text:
                messages.append(mk(_Role.USER, f"{OWNER} said: {owner_text}"))
            if memory.get("last", {}).get(name):
                messages.append(mk(_Role.USER, f"Your last sentence: {memory['last'][name]}"))
            messages.append(mk(_Role.USER, "Your turn."))
            try:
                result = engine.generate(
                    messages, model=state["models"].get(name, state["model"]),
                    temperature=0.85, max_tokens=WORDS_PER_TURN,
                )
            except engine_down as exc:  # noqa: B902 - empty tuple when absent
                append_turn(ledger_dir, session_id, {
                    "round": rnd, "voice": name, "at": now(),
                    "model": state["models"].get(name), "text": "",
                    "verdict": "", "risk_hits": [], "gold_hits": [], "gold_source": None,
                    "oracle": None, "stopped": f"{type(exc).__name__}: {exc}",
                })
                status = "engine_down"
                because = f"engine unreachable in round {rnd}, {name}'s turn: {type(exc).__name__}"
                # `break` already leaves the voice loop; this is the round-level
                # flag, written through the module so a later check sees it.
                # It used to be a local `stop = True` — and since the loop stopped
                # copying the flag into a local, that line became a write to a
                # name that no longer existed. A `NameError` here would have
                # taken the whole run down on the one path that must never
                # crash: the engine disappearing mid-session.
                _set_stop()
                break
            reply = (result.get("content") or "").strip()
            v = link.govern(reply)
            append_turn(ledger_dir, session_id, {
                "round": rnd,
                "voice": name,
                "at": now(),
                "model": state["models"].get(name, state["model"]),
                "text": reply,
                "verdict": v["verdict"],
                "risk_hits": v.get("risk_hits") or [],
                "gold_hits": v.get("gold_hits") or [],
                "gold_source": v.get("gold_source"),
                "oracle": v.get("oracle"),
            })
            made += 1
            turns_of_round += 1
        rounds_done = rnd
        # Only `status` — the one field the run actually knows. See
        # `patch_state`: a write of the whole dict would carry the loop's stale
        # copy of every other field, and `spawn` had written the pid after that
        # copy was taken.
        patch_state(ledger_dir, session_id, status="running")
        state = read_state(ledger_dir, session_id) or state

        turns_now = read_turns(ledger_dir, session_id)

        # ── the owner's criterion: the team may only PROPOSE ─────────────
        # 🚨 BEFORE the ceiling, and the order is the whole point. This block used
        # to sit below the budget check, and the consequence was measured: a
        # session with `stop_when: owner-accepts` and `ceiling: 3` in which all
        # three voices answered `frei` closed as `ceiling_reached` with the
        # sentence "THE GOAL WAS NOT MET" — while the criterion the owner chose
        # was, at that very moment, satisfied. Two lies in one record: the
        # trigger never fired because the loop had already left, and the
        # sentence asserted a non-result about a condition that held. Worse, the
        # owner was then locked out of their own door — `accept` answers 409
        # "no proposal" against a session that is already closed, so the one
        # close a person may make became unreachable at exactly the moment it
        # was earned.
        #
        # A budget and a criterion are different things, and the budget must not
        # be able to overwrite the criterion. Reading the criterion first costs
        # nothing: both paths `break` out of the round, so the ceiling is still
        # respected and no further call is paid for.
        if state.get("stop_when") == "owner-accepts" and all_voices_freeliest(turns_now):
            if not any(p.get("round") == rnd for p in read_proposals(ledger_dir, session_id)):
                append_proposal(ledger_dir, session_id, {
                    "round": rnd,
                    "at": now(),
                    "trigger": ("every voice held a gold-aligned verdict in the last "
                                "round — a condition on the governance record, not "
                                "any voice's opinion of itself"),
                    "evidence": session_memory(turns_now),
                    "closed": False,
                })
            status = "awaiting_owner"
            because = ("the team proposes the close; only the owner can close it. "
                       "Nothing has been completed and nothing was paid for after "
                       "this round"
                       + (" — and the ceiling is spent, so this is the last round "
                          "the budget buys." if made >= int(state["ceiling"]) else ""))
            break

        # The ceiling is counted in CALLS, so it is checked in CALLS. The first
        # version checked it after a whole round, and a ceiling of 4 produced
        # **6** calls: a caller who writes `ceiling: 4` and reads 6 back has been
        # lied to by a field that names its own unit. The sentence says when the
        # round was cut short, because "the ceiling" and "the end of the round"
        # are different events and only one of them is a ceiling.
        if made >= int(state["ceiling"]):
            status = "ceiling_reached"
            because = (f"the ceiling of {state['ceiling']} calls was reached in round "
                       f"{rnd} after {made} calls, "
                       + (f"the round cut short after {turns_of_round} of "
                          f"{len(PERSONAS)} voices. " if turns_of_round < len(PERSONAS)
                          else "every voice had spoken. ")
                       + f"the criterion '{state.get('stop_when')}' was not met — "
                       "a budget is not a result, and this sentence does not claim "
                       "the team did badly. It says the money ran out.")
            break

        met, why = criterion_met(ledger_dir, state)
        if met:
            status, because = "complete", why
            break
        if stop_after is not None and rounds_done >= stop_after:
            status, because = "stopped", f"stopped after {rounds_done} rounds (--stop-after)"
            break
        time.sleep(INTERVAL)

    if status == "stopped" and stop_after is None and rounds_done >= max_rounds:
        status, because = "ceiling_reached", (
            f"the round ceiling of {max_rounds} was reached. THE GOAL WAS NOT MET.")

    # 🚨 The last writer check. A person closed this session while the process
    # was inside a model call; a human's decision outranks this process's exit
    # path, and the two would otherwise race — `accept` writes `complete`, the
    # loop wakes up and writes `stopped`, and which one is in the file depends on
    # which of them was slower. So the loop reads first, and when it finds a
    # close it did not write, it says so **in the record** and leaves the file
    # alone. The lost fact is kept, not dropped: a turn that was paid for after
    # the close belongs in the transcript of what happened.
    current = read_state(ledger_dir, session_id) or {}
    if current.get("closed_by") not in (None, "process"):
        append_turn(ledger_dir, session_id, {
            "round": rounds_done, "voice": OWNER, "at": now(), "model": None,
            "text": "", "verdict": "", "risk_hits": [], "gold_hits": [],
            "gold_source": None, "oracle": None,
            "note": (f"this run stopped with status '{status}' ({because}) but did "
                     f"NOT write the close: the session was already closed by "
                     f"'{current.get('closed_by')}' — "
                     f"{current.get('closed_because')}. The turn is in the record; "
                     f"the decision is not overwritten."),
        })
        return 0
    if status == "awaiting_owner":
        # 🚨 **A proposal is not a close.** This went through `close()` and the
        # cost was the owner losing the only door built to hear him: the team
        # proposed, the record stamped `closed` with `closed_by: "process"`, and
        # `POST …/accept` then answered **409 "this session is already closed"** —
        # measured, on a throwaway ledger, with a one-line proposal in the file
        # and the owner left with nothing to do but start a new session. A status
        # a reader can mistake for "finished", on a field that means it, from a
        # process that finished nothing: the `dev262` shape, and the same family
        # as defect 11, which locked the owner out of his own door for a
        # different reason and one layer along.
        #
        # So the question is written as a question: a status, the moment, and the
        # sentence — and **no close**, which is why it must not go through the one
        # writer of closes. `closed` stays `None`, so the list says the session
        # is open, and `accept` finds no close to refuse.
        patched = patch_state(ledger_dir, session_id, status="awaiting_owner",
                              awaiting_owner_at=now(), awaiting_because=because)
        return 0 if patched is not None else 2
    closed = close(ledger_dir, session_id, status, because)
    return 0 if closed["status"] in ("complete", "stopped") else 2


# ── spawning ────────────────────────────────────────────────────────────────

def spawn(ledger_dir: Path | str, session_id: str) -> Optional[int]:
    """Start the session process, detached, pidfile-managed — the idle pattern."""
    sid = _safe_id(session_id)
    live = is_running(sid)
    if live:
        return live
    pf = pidfile_path(sid)
    pf.parent.mkdir(parents=True, exist_ok=True)
    log_dir = Path(os.environ.get(
        "BIANCA_SESSIONS_DIR", str(Path.home() / ".openjarvis" / "bianca" / "sessions")))
    cmd = [sys.executable, "-m", "openjarvis.sovereign.session", str(ledger_dir), sid]
    with open(log_dir / f"{sid}.log", "a") as logf:
        proc = subprocess.Popen(cmd, start_new_session=True, stdout=logf, stderr=logf)
    try:
        pf.write_text(str(proc.pid), encoding="utf-8")
    except OSError:
        pass
    state = read_state(ledger_dir, sid)
    if state is not None:
        state["pid"] = proc.pid
        write_state(ledger_dir, state)
    return proc.pid


def halt(session_id: str, reason: str, ledger_dir: Path | str) -> dict:
    """Ask a session to stop — and close it **only if nobody else will**.

    🚨 This function is where the set's own second multi-writer defect died, and
    it is worth the words. The first version sent SIGTERM and then called
    :func:`close` itself, so the door wrote ``stopped`` while the process was
    still inside a model call — and when the process finished, it wrote *its*
    sentence over the door's. Two writers of one close, and the file's history
    depended on which one was slower. Measured: a session killed mid-round left
    a turn on disk that the state did not count, and the reason was the same
    family of error — a number kept beside the record instead of derived from it.

    The rule now: **the process owns the close while it is alive; the door owns
    it when there is provably nobody to do it.** A live process is asked (a
    ``stop_requested`` fact, plus the signal) and will write the close at its next
    boundary — which is *not* instant, and the caller is told so rather than being
    handed a status that is not true yet. A dead or absent process is closed by
    the door, because otherwise nothing would ever close it.

    Returns the state plus ``pending``: ``True`` means the record is not final
    yet, and the reader must not report the session as stopped. ``closed_already``
    means the opposite of a refusal: the session **is** stopped, it was closed by
    somebody, and this call changed nothing — the caller is told so instead of
    being handed a success that would suggest its own words were recorded.
    """
    sid = _safe_id(session_id)
    pid = is_running(sid)
    # The request goes into the record FIRST, unconditionally. That is the
    # channel; the signal is only the nudge that makes it fast, and it is
    # skipped when the run has not announced that it can hear — because in that
    # window the nudge is not a nudge, it is a kill. Measured: 3 of 14 spawns
    # died that way, silently, with a zero-byte log and no close.
    state = read_state(ledger_dir, sid)
    # 🚨 A close is taken **once**, and a stop against a closed session must not
    # write a second one. Measured: the second `POST …/stop?reason=…` answered
    # 200 and its reason replaced the first owner's words in the record — the
    # sentence the owner had given, and the reason the session ended, gone,
    # because somebody pressed the button twice. `accept` had already learned
    # this in the same set (its own comment names the defect: *a close is taken
    # once; a second one would be the same decision counted twice*); the stop
    # door had not.
    #
    # Note what is **not** a duplicate: `awaiting_owner` carries no close, so a
    # stop there is a real transition and the owner keeps both acts. The test is
    # the close, never the status.
    if state is not None and state.get("closed"):
        # 🚨 A **flag**, not a copy of the close. The first version returned the
        # four fields in a `closed_already` block, which is a second telling of
        # the same close — and the check that says "one writer closes a session"
        # reported this function as a second writer, correctly, because from the
        # text alone it is one. The door already holds the state this returns and
        # can read the fields off it, so restating them here bought nothing and
        # cost the claim. The record is the record; it is not summarised twice.
        stehend = dict(state)
        stehend["pending"] = False
        stehend["closed_already"] = True
        return stehend
    if state is not None:
        state["stop_requested"] = {"reason": reason, "at": now()}
        write_state(ledger_dir, state)
    heard = bool((state or {}).get("ready"))
    if pid and heard:
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pid = None
    elif pid:
        pid = pid  # alive, but deaf for the first moments — the record will do
    if pid:
        out = read_state(ledger_dir, sid) or {}
        out["pending"] = True
        out["stops_when"] = ("at the next voice boundary — a model call already in "
                             "flight is not interrupted, so this is seconds, not "
                             "milliseconds")
        return out
    # `by="door"`, not the default: nothing ran here, the node acted on the
    # owner's word. Leaving it as "process" would put a claim in the record that
    # is false — a run that never started is not a run that stopped.
    out = close(ledger_dir, sid, "stopped", reason, by="door")
    out["pending"] = False
    return out


if __name__ == "__main__":  # pragma: no cover - process entry
    # There was a `signal.SIG_IGN` here once, put in to cover the window between
    # the process starting and `session_loop` installing the handler. It was
    # measured, it did not work, and it is gone. What it was trying to cover is
    # the **interpreter's own startup** — roughly 50 ms before this module's
    # first line runs — so ignoring SIGTERM from inside the module is already too
    # late. And it carried a real risk for no measured gain: `SIG_IGN` is
    # inherited across `exec` and across the whole process life, so a run whose
    # handler never installed would have been unkillable by SIGTERM.
    #
    # What actually closed the race is the `ready` handshake: the run announces
    # that it can hear, and `halt` signals only then. The request lives in the
    # record the whole time. 14 spawns, signals at 0 … 0.26 s, 14 clean closes.

    # `python -m openjarvis.sovereign.session <ledger_dir> <session_id> [--stop-after N]`
    args = sys.argv[1:]
    after = None
    if "--stop-after" in args:
        i = args.index("--stop-after")
        try:
            after = int(args[i + 1])
        except (IndexError, ValueError):
            print("--stop-after needs a number", file=sys.stderr)
            sys.exit(2)
        del args[i:i + 2]
    if len(args) != 2:
        print("usage: python -m openjarvis.sovereign.session <ledger_dir> <session_id> "
              "[--stop-after N]", file=sys.stderr)
        sys.exit(2)
    sys.exit(session_loop(args[0], args[1], stop_after=after))
