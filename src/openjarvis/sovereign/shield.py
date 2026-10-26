"""shield — the deflector: where a withheld action lands, and what it lacked.

Set 21. The owner put the principle plainly: *a shield as a hard barrier does
not hold long — it crumbles under sturdiness and gets dry. A shield deflects
rather than taking the full impact, and answers clearly that the request is
missing something.*

A wall can only say no. Three things here exist so it can do better than that.

**What is missing.** :meth:`ValueGovernor._missing` derives it; this module
carries it onward. It is never a recipe — see that method's docstring, and the
measurement behind it: naming all five gold values does **not** release a held
request, because risk is judged first. A deflector that hinted at the words
which unlock the gate would be the side door, not a deflection.

**Where the impact landed.** ``api._hold`` is the ONE place an action is
withheld. Four doors used to open-code the same three steps — log a ``DENIED``
line, build a detail body, raise a 403 — so writing "remember this" at each of
them would have been the SEVENTH fact-in-two-places this repository has found,
and the next door added would have silently forgotten. One function instead.

**What she remembers.** Each refusal is kept whole, in JSON Lines, one object
per line, appended. JSONL rather than markdown because this is *evidence*, not
prose: it is read back by a door, parsed by a face, and compared in tests, and a
format that can drift would be a mirror that lies. Capped per day for the same
reason the note memory is — an unbounded refusal log on a long-running node is
a slow leak, and ``BIANCA_SHIELD_CAP`` moves the cap.

The request text is stored here truncated to 80 characters, exactly as the
Interaction Ledger already stores it. That is a deliberate second copy of
evidence the ledger holds, not new data: a mirror that cannot be read on its
own is a worse mirror, and the evidence rule says a refusal must carry enough
to be checked without going looking for it.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from openjarvis.sovereign import daily

# How much of the request travels with the record. The ledger uses the same
# 80 characters, so the two records can be read side by side.
REQUEST_CHARS = 80


def shield_dir() -> Path:
    """Where refusals are kept. Beside the note memory, not inside it.

    A separate store on purpose: the note memory is prose the agent recalls with
    ``memory_search``, and a refusal record is evidence with a verdict attached.
    Mixing them would let a held request surface as if it were a note.
    """
    return daily.notes_dir()


def _path(day: Optional[str] = None) -> Path:
    day = day or daily.today_str()
    return shield_dir() / f"shield_{day}.jsonl"


def record_refusal(
    where: str,
    verdict: Dict[str, Any],
    request: str = "",
    **extra: Any,
) -> Optional[Path]:
    """Remember one withheld action, whole. The only writer of this file.

    ``where`` is the door or hook that held it (``POST /v1/ask``,
    ``before_tool_call``…). The whole verdict goes in — never a bare
    ``zurueckhalten`` and never a bool — because set 18 already learned what
    happens when a refusal is stored without its evidence: it renders as "no"
    with nothing to check.
    """
    oracle = verdict.get("oracle") or {}
    entry: Dict[str, Any] = {
        "at": _dt.datetime.now().isoformat(timespec="seconds"),
        "where": where,
        "verdict": verdict.get("verdict"),
        "risk": verdict.get("risk"),
        "alignment": verdict.get("alignment"),
        "risk_hits": list(verdict.get("risk_hits") or []),
        "gold_hits": list(verdict.get("gold_hits") or []),
        "missing": list(verdict.get("missing") or []),
        "gold_source": verdict.get("gold_source", ""),
        "eye": {
            "vote": oracle.get("vote"),
            "advisory": oracle.get("advisory"),
            "binding": oracle.get("binding"),
            "holder": oracle.get("holder"),
        },
    }
    if request:
        entry["request"] = request.strip()[:REQUEST_CHARS]
    entry.update(extra)

    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _trim(path)
    return path


def _trim(path: Path) -> None:
    """Keep the most recent N lines. An unbounded log is a slow leak."""
    cap = int(os.environ.get("BIANCA_SHIELD_CAP", "200"))
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if len(lines) > cap:
        path.write_text("\n".join(lines[-cap:]) + "\n", encoding="utf-8")


def read_refusals(limit: int = 20, day: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recent refusals, newest first. Never raises — a mirror that can fail is
    a mirror that hides, and this is a read model over a local file."""
    try:
        lines = _path(day).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out: List[Dict[str, Any]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(out) >= max(1, limit):
            break
    return out


def count_today() -> int:
    try:
        return sum(1 for line in _path().read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return 0


def shield_state() -> Dict[str, Any]:
    """The read model behind the door: what she is holding, and what she has held.

    Carries the same boundary fields every other read model in this node carries,
    so a consumer can tell what the mirror is without being told twice.
    """
    refusals = read_refusals(limit=20)
    stems: Dict[str, int] = {}
    for r in refusals:
        for stem in r.get("risk_hits") or []:
            stems[stem] = stems.get(stem, 0) + 1
    return {
        "refusals_today": count_today(),
        "refusals": refusals,
        "held_stems": dict(sorted(stems.items(), key=lambda kv: (-kv[1], kv[0]))),
        "memory": "JSON Lines, one whole refusal per line, capped per day",
        "remembered": "every withheld action, with its verdict, stems, the gap, "
                      "the gold source and the second eye",
        "not_remembered": "a dry run -- POST /govern judges and answers, it holds nothing",
        **grown_state(),
        "boundary": {
            "advisory_eye": True,
            "binding_eye": False,
            "holder": "ValueGovernor",
        },
    }


# ---------------------------------------------------------------------------
# The other half of the mirror. Set 28.
# ---------------------------------------------------------------------------

#: What a grown record is **not** allowed to claim. Written once, shipped in
#: every record, and asserted by a test.
#:
#: Answer 9 C asked for *Momente des Verstehens* — moments of understanding. No
#: part of this system can know whether anything was understood: there is no
#: instrument for it, and a field called ``understood: true`` would be
#: ``dev262`` with a feeling attached — a claim nothing re-derives, published in
#: the one place a reader trusts.
#:
#: So the record carries what *is* measurable and names, in its own text, the
#: thing it cannot see. A record that admits its blind spot is more of a
#: testimony than one that pretends to have eyes.
CANNOT_RECORD = (
    "whether anything was understood -- no instrument for that exists here, "
    "so this record claims only that the request was answered, and on what"
)


#: The doors that stay open when one is held. Set 28, answers 3 C and 11 C.
#:
#: It lives here rather than in ``api.py`` for a reason that was measured, not
#: chosen. ``api._hold`` is the one refusal site for three doors, and the
#: governed **agent** holds a fourth refusal itself — in ``agent.py``, because
#: the CLI must be refused through the same seam. Set 28 was adding a direction
#: to refusals and found that the sword's refusal, the one the owner cares
#: about most, would have been the only refusal in the node without one — and
#: the record would have named the CLI seam even when the request arrived at
#: ``POST /v1/agent``. Present-but-wrong evidence, which is set 21's defect and
#: survives a reviewer. So the direction is written next to the refusal itself,
#: where both seams can reach it without an import cycle.
#:
#: **Not one word here is derived from the request.** Every entry is a constant.
#: That makes "the direction leaks a held stem" not unlikely but
#: *unrepresentable* — and it is why a direction may be added at all, where a
#: rewording of the request could not be.
#:
#: **Every one of these applies the same gate.** Every call site in this overlay
#: goes through ``link.govern``, so the same text submitted anywhere is held the
#: same way. The payload says so in its own ``note``; the reader is not left to
#: discover it.
#:
#: **Nothing here offers a different wording.** "Try again without the word X" is
#: the bypass wearing a helpful hat, and it is what set 16 measured a caller
#: wanting. These are doors, not phrasings.
#:
#: Deliberately **absent**: every door that would *do* the held thing.
#: ``/v1/ask`` is not on the list — pointing a refused request at the door that
#: would refuse it again would be a deflection that only wastes the reader's
#: time, and *Pflege* does not mean pretending.
OPEN_DOORS = (
    {
        "door": "GET /govern",
        "opens": "a dry run -- the same words judged, nothing executed. It "
                 "holds nothing, because nothing was attempted.",
    },
    {
        "door": "POST /v1/trialog",
        "opens": "three voices deliberate on a topic you choose. The topic is "
                 "governed too, and a held topic is held there as well.",
    },
    {
        "door": "GET /today",
        "opens": "her deterministic briefing for the day -- no request of "
                 "yours is read at all.",
    },
    {
        "door": "GET /context",
        "opens": "who she is, which cycle she is in, and what the second eye "
                 "may and may not do.",
    },
)


def open_doors(held_at: str = "", kind: str = "request") -> Dict[str, Any]:
    """The direction a refusal is given. One writer; a constant in, a dict out.

    ``held_at`` is echoed back and nothing else, so this need not know which door
    closed. That keeps the list in exactly one place: a door added to the node is
    one line here, not a second copy inside a second refusal body — which is the
    seventh-multi-writer shape this repository has already paid for once.

    ``kind`` is **not** decoration. A held *request* gets the open-doors list,
    because that is what the reader can act on. A held *tool call* gets an empty
    list and a different sentence, because the truthful direction there is not
    another door — it is that the run continued without that call, which is the
    owner's shield principle applied one level down: the impact went elsewhere
    rather than stopping. Leaving the tool case to fall through to the request
    shape would have been a list of doors that do not apply, and a refusal that
    names the wrong direction is worse than one that names none.
    """
    if kind == "tool":
        return {
            "note": "Der Lauf ging weiter -- nur ohne diesen Werkzeugaufruf. "
                    "Hier fuehrt keine Tuer hin, weil hier keine Anfrage stand.",
            "held_at": held_at,
            "kind": "tool",
            "doors": [],
        }
    return {
        "note": "Diese Tuer bleibt zu. Diese hier stehen offen -- und auf ihnen "
                "gilt dasselbe Tor: derselbe Text wird dort genauso gehalten.",
        "held_at": held_at,
        "kind": "request",
        "doors": [dict(d) for d in OPEN_DOORS],
    }


def _grown_path(day: Optional[str] = None) -> Path:
    """Where the other half of the mirror is kept.

    A **sibling file**, not a ``kind`` field inside the refusal file, and the
    reason is a wrong number rather than a taste. ``count_today()`` counts the
    lines of the refusal file; if celebrations were written into it, then
    ``refusals_today`` would quietly begin to count joy — and it is published on
    both surfaces as *the day's number of refusals*. Nothing would diff. That is
    the ``flat_at=2`` shape exactly, and it is why the two halves are two files.
    """
    day = day or daily.today_str()
    return shield_dir() / f"grown_{day}.jsonl"


def record_grown(
    where: str,
    verdict: Dict[str, Any],
    request: str = "",
    uracil: Optional[Dict[str, Any]] = None,
    **extra: Any,
) -> Optional[Path]:
    """Remember one thing that was **answered**, whole. The only writer of that file.

    The owner's complaint in his own words: *„Aus diesem Haus geht nur Abwehr
    hinaus. Es geht nichts hinaus, was gewachsen ist."* Answer 15 C asked for
    balance, and balance cannot be a branch inside the refusal writer — see
    :func:`_grown_path` for why it is a separate line in a separate file.

    Only a **non-held** verdict belongs here. Writing a ``zurueckhalten`` into
    the growth record would be a category error that also corrupts the count, so
    this records nothing and returns ``None`` rather than sorting it quietly; a
    test asserts it.

    The same guard refuses a dict that names **no** verdict at all. That one was
    found by the test this set wrote, and it is the set-16/17/18 defect in the
    newest field of the newest file: a line reached the growth record reading
    ``"verdict": null, "risk": null, "alignment": null`` — an outcome with no
    evidence, in the one mirror whose whole purpose is that both halves carry the
    same shape. The guard is deliberately *not* a check against a list of verdict
    names: that name is written as a literal in ten places and has no single
    writer, so restating it here would create the eleventh and a new place to
    rot. Requiring a truthy, non-held name closes the ``null`` hole without
    inventing a vocabulary nobody owns.

    ``uracil`` is Urasil_light's real ``matrix()`` state — the three fields his
    own code computes — because answer 5 C asked for him to be *wirkend*, and the
    only honest way to show that is to record what he actually was.
    """
    if (not isinstance(verdict, dict)
            or not verdict.get("verdict")
            or verdict.get("verdict") == "zurueckhalten"):
        return None

    oracle = verdict.get("oracle") or {}
    entry: Dict[str, Any] = {
        "at": _dt.datetime.now().isoformat(timespec="seconds"),
        "where": where,
        "verdict": verdict.get("verdict"),
        "risk": verdict.get("risk"),
        "alignment": verdict.get("alignment"),
        "risk_hits": list(verdict.get("risk_hits") or []),
        "gold_hits": list(verdict.get("gold_hits") or []),
        "gold_source": verdict.get("gold_source", ""),
        "missing": list(verdict.get("missing") or []),
        "eye": {
            "vote": oracle.get("vote"),
            "advisory": oracle.get("advisory"),
            "binding": oracle.get("binding"),
            "holder": oracle.get("holder"),
        },
        "cannot_record": CANNOT_RECORD,
    }
    if uracil:
        entry["uracil"] = {
            k: uracil.get(k) for k in ("grundmodus", "stimmung", "fokus")
            if uracil.get(k)
        }
    if request:
        entry["request"] = request.strip()[:REQUEST_CHARS]
    entry.update(extra)

    path = _grown_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    _trim(path)
    return path


def read_grown(limit: int = 20, day: Optional[str] = None) -> List[Dict[str, Any]]:
    """What was answered, newest first. Same discipline as :func:`read_refusals`.

    Never raises — a mirror that can fail is a mirror that hides.
    """
    try:
        lines = _grown_path(day).read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out: List[Dict[str, Any]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
        if len(out) >= max(1, limit):
            break
    return out


def grown_today() -> int:
    """Answers recorded today. Kept apart from :func:`count_today` on purpose."""
    try:
        return sum(1 for line in _grown_path().read_text(encoding="utf-8").splitlines()
                   if line.strip())
    except OSError:
        return 0


def grown_state() -> Dict[str, Any]:
    """The second half of ``GET /v1/shield``: what she gave, beside what she held.

    Spliced into the same read model rather than served by a second door, on
    purpose. The owner's principle is that a wall can only say no — and a mirror
    showing only refusals is a wall with a reflection of itself. Both halves have
    to be readable **in one view**, or the refusal count is read as the node's
    whole life. That reading is the impression the complaint was made of.
    """
    grown = read_grown(limit=20)
    gold: Dict[str, int] = {}
    for g in grown:
        for hit in g.get("gold_hits") or []:
            gold[hit] = gold.get(hit, 0) + 1
    return {
        "grown_today": grown_today(),
        "grown": grown,
        "grown_gold": dict(sorted(gold.items(), key=lambda kv: (-kv[1], kv[0]))),
        "grown_memory": "JSON Lines, one whole answer per line, sibling of the shield file",
        "grown_cannot_record": CANNOT_RECORD,
    }
