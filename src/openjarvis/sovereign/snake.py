"""snake — the one seam where the inner world reaches the mycelium.

The owner's thread: *"Urasil entspricht meinem verständnis nach dem
Sternenbildes des Schlangenträgers, dessen symbol immer noch für apotheken
gilt. Seine Schlange ist Python und dessen werken im colorverse welches
komplexität und emergenz aus einfachen regeln hält. Dies ist die innere und
äußere welt in code. Die schlangen tragen die info ins myzell netz — einfach,
klein und klar."*

Two halves existed and nothing joined them. The snake existed: Urasil_light's
real cycle, read by :class:`CycleStateReader`. The net existed:
:mod:`hub`, with a governed ingress. So this module is the **seam** — and per
the owner's decision it is *one* writer with *two* callers, because two writers
is how this repository has now found six multi-writer defects.

**What may cross, and why the words do not.** A refusal is *by construction*
the record of words the governor holds, and ``hub.accept_spore`` refuses words
the governor holds. Measured, not assumed (set 22, breath 1)::

    the mood spore             -> 200  vorsichtig
    the refusal TEXT           -> 403  zurueckhalten  stems=['loesch']
    the refusal, stems named   -> 403  zurueckhalten  stems=['loesch']
    the refusal, gap only      -> 200  symbolisch
    the refusal, evidence only -> 200  symbolisch

The stems cannot cross *even as a list*, because a stem is itself a
``RISK_TERMS`` entry. And nothing served by this node exposes the lexicon
today — so carrying stems would be the first act in this repository's history
that published the node's held words to strangers. The list *is* the bypass
surface: anyone who can ``GET /hub/spores`` would learn exactly which words
this node holds.

So the line is exact, and it is the owner's own principle one level out:

* the **local** mirror (:func:`~openjarvis.sovereign.shield.read_refusals`,
  bound to 127.0.0.1) names the stems — the owner must know which word tripped
  the gate;
* the **net** carries the *shape* of a refusal and never the words that caused
  it. A count crosses; a name does not.

A deflector takes the impact so the body does not. Set 21 kept the impact off
the requester. This keeps it off the net.

**Two independent guards, on purpose.** The payload is built from an
*allowlist* (:data:`CROSSABLE_REFUSAL`) — so a new field cannot leak by being
added to a dict somewhere else — and then *proved* against the governor's own
stems before it is sent. A bug in either is caught by the other, and the
lexicon is **read** from :class:`ValueGovernor`, never re-typed here.
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterable, Mapping

from openjarvis.sovereign import hub
from openjarvis.sovereign.link import ValueGovernor, default_link

#: The ONLY fields of a refusal that may cross. Anything not named here does
#: not reach the net — not because a filter dropped it, but because it was
#: never in the list. An allowlist is the only honest way to keep a field out:
#: a denylist has to be right about everything that does not exist yet.
#:
#: The field the payload is built FROM, and the field that ends up in the net
#: differ by design, and the mapping is here rather than inline — because an
#: allowlist that is only checked against a hardcoded dict literal is decoration
#: (set 22 found that the hard way: adding a name here changed nothing, because
#: the literal did not have it). So the list below is consulted for the value of
#: every field, and a name added here really does open the seam.
CROSSABLE_REFUSAL: tuple[str, ...] = (
    "kind",          # "refusal" — what this is
    "seam",          # where it was held: a door name, never a payload
    "verdict",
    "risk",
    "alignment",
    "held_count",    # how MANY words tripped it — a number is not an attack
    "missing",       # the gap: the deflection, measured safe above
    "gold_hits",
    "gold_source",   # provenance, so a stranger can weigh the claim
    "eye",           # the second eye, advisory as everywhere else
)

#: Where each carried field is READ FROM on the shield's own record, for the
#: names that differ. A field **not** listed here is read from the refusal under
#: its own name — so widening :data:`CROSSABLE_REFUSAL` genuinely opens the seam
#: rather than quietly doing nothing, which is what the first version of this
#: module got wrong.
FROM_THE_REFUSAL: dict[str, str] = {
    "seam": "where",   # the shield calls the door `where`; the net reads `seam`
}

#: Fields that must NEVER appear, named explicitly so their absence is a
#: deliberate, testable statement rather than an oversight.
WITHHELD: tuple[str, ...] = ("request", "risk_hits")

#: What the snake says when it refuses to carry its own payload. This is a
#: local stop, not a 403: nothing was offered to the net, so nothing was
#: judged by it, and reporting a verdict here would be inventing one.
REFUSED_LOCALLY = "the payload carries a word the gate holds; it was not sent"


def held_stems() -> tuple[str, ...]:
    """The node's risk lexicon, **read** from its one writer.

    Never re-typed here. This module is the second place in the repository
    that would otherwise restate the list, and set 19's lesson was that a fact
    stated in two places reaches five.
    """
    return tuple(ValueGovernor.RISK_TERMS)


def words_that_would_trip_the_gate(text: str) -> list[str]:
    """Every lexicon entry present in ``text``, by the governor's own matching.

    Not a re-implementation: it asks the same stem list the gate asks, so the
    proof and the gate cannot disagree about what a word is.
    """
    low = text.lower()
    return [s for s in held_stems() if s in low]


def _refusal_spore(refusal: dict[str, Any]) -> dict[str, Any]:
    """Build a refusal spore **from the allowlist**, consulting it for every field.

    A name added to :data:`CROSSABLE_REFUSAL` really does open the seam, and the
    local guard in :func:`carry` is what then has to stop it. That is the point
    of two independent guards: an allowlist that cannot be widened is a filter
    pretending to be a policy, and a policy nobody can widen is a constant.
    """
    spore: dict[str, Any] = {"kind": "refusal"}
    for field in CROSSABLE_REFUSAL:
        if field == "kind":
            continue
        if field == "held_count":
            # a number crosses; the name it counts does not. Read here, not
            # copied, so widening the list cannot smuggle the stems in.
            spore[field] = len(refusal.get("risk_hits") or ())
            continue
        value = refusal.get(FROM_THE_REFUSAL.get(field, field))
        if isinstance(value, (list, tuple)):
            spore[field] = list(value)
        elif isinstance(value, dict):
            spore[field] = dict(value)
        else:
            spore[field] = value
    return spore


def _mood_spore(cycle: dict[str, Any]) -> dict[str, Any]:
    """The cycle, as it stands — three fields, read, not invented.

    ``einfach, klein und klar`` taken literally: the inner world's mood is
    already exactly three named values in ``identity.json``, and re-deriving
    them here would be the seventh restatement of a fact this repo already
    carries.
    """
    return {
        "kind": "cycle",
        "grundmodus": cycle.get("grundmodus"),
        "stimmung": cycle.get("stimmung"),
        "fokus": cycle.get("fokus"),
    }


def carry(payload: dict[str, Any], kind: str = "snake",
          source: str = "urasil",
          ledger_dir: str | None = None) -> tuple[int, dict[str, Any]]:
    """The one writer. Both callers come through here; there is no second way.

    Three steps, and the order is the point:

    1. **Prove** the serialized payload against the governor's own stems.
    2. **Stop locally** if any is present — before the net is offered anything,
       so no fiction of a net-side judgement is created.
    3. **Hand it to the net's own governed door**, which judges it a second,
       independent time and is free to refuse for its own reasons.
    """
    text = json.dumps(payload, ensure_ascii=False)
    found = words_that_would_trip_the_gate(text)
    if found:
        return 0, {
            "carried": False,
            "refused_locally": True,
            "why": REFUSED_LOCALLY,
            # The count, not the words. Reporting which word tripped the gate to
            # whoever asked for the spore is the exact thing this seam exists
            # to prevent — and the caller here is the net.
            "held_count": len(found),
            "kind": kind,
        }
    status, body = hub.accept_spore(text, source=source, kind=kind,
                                    ledger_dir=ledger_dir)
    return status, {"carried": status == 200, "status": status, "receipt": body}


def _already_crossed(payload: dict[str, Any]) -> bool:
    """Has this exact payload crossed before?

    Compares against the net's own record rather than a private digest, so the
    dedupe cannot drift from what the net actually stored. The cycle runs on a
    12-step rotation, so without this the net would collect the same mood
    dozens of times a day — which is not ``einfach, klein und klar``, it is
    noise wearing the snake's name.
    """
    text = json.dumps(payload, ensure_ascii=False)
    return any(row.get("text") == text for row in crossings())


def carry_once(payload: dict[str, Any], kind: str = "snake",
               source: str = "urasil",
               ledger_dir: str | None = None) -> tuple[int, dict[str, Any]]:
    """Carry it, unless it is already in the net. The common entry point."""
    if _already_crossed(payload):
        return 200, {"carried": False, "status": 200, "already": True,
                     "kind": kind}
    return carry(payload, kind=kind, source=source, ledger_dir=ledger_dir)


#: Set 29. The owner's answer 6 C: *„Jede python schlange ist ein individueller
#: python befehlskette."* Taken literally that is **remote code execution over
#: the mycelium net**, and this repository's entire purpose is the gate that
#: stops it. So the net learns what kind of thing travels, and the decision to
#: ever *execute* one is the owner's, argued from a threat model — not an
#: oversight in a Python file.
#:
#: The two properties that make a description safe, and neither of them is a
#: policy that could be forgotten:
#:
#: 1. **A step has no field to type a command into.** ``chain_description``
#:    builds a fixed shape, and the shape has ``does`` (what would be attempted,
#:    in words) and ``checks`` (what must be true afterwards). There is no
#:    ``command``, no ``argv``, no ``shell`` — so there is nothing to fill in
#:    later, by this version or the next. The same reasoning as
#:    :data:`OPEN_DOORS` holding no request-derived text: the leak is
#:    structurally impossible, not filtered.
#: 2. **A chain without a checkable completion is refused here**, at the seam
#:    that describes it. The owner's standing instruction is *„dauerhaft aktiv
#:    bis zum erfolgreichen Abschluß"*, and a description that named no end would
#:    be an unbounded loop travelling the net as a *shape*. So ``stop_when`` is
#:    required and cannot be empty — the sentence has to say what success is,
#:    and saying it is what makes the description worth carrying.
#:
#: What is deliberately absent from this module: any ``exec``, ``eval``,
#: ``subprocess``, ``os.system`` or ``import`` of the step payload. There is no
#: execution surface here, and a test asserts the absence rather than trusting
#: this comment.
CHAIN_STEP_FIELDS: tuple[str, ...] = ("does", "checks")

#: Refused at the description seam, in the same shape as every other local stop.
CHAIN_UNBOUNDED = ("a chain without a checkable completion is not a chain, "
                   "it is a loop travelling the net as a shape")


def chain_description(
    goal: str,
    steps: Iterable[Mapping[str, str]],
    stop_when: str,
    source: str = "urasil",
    ledger_dir: str | None = None,
) -> tuple[int, dict[str, Any]]:
    """Describe a chain of intent and carry the *description* to the net.

    Returns the same ``(status, result)`` shape as every other seam here, so a
    caller cannot tell a description from a cycle by its return type — the
    difference is in what crossed, and the receipt says so.

    ``stop_when`` is required, non-empty, and travels in the payload. A
    description that cannot say what success is does not get to become data.
    """
    reason = str(stop_when or "").strip()
    if not reason:
        return 0, {
            "carried": False,
            "refused_locally": True,
            "why": CHAIN_UNBOUNDED,
            "held_count": 0,
            "kind": "chain",
        }

    described: list[dict[str, str]] = []
    for raw in steps:
        row = {k: str(raw.get(k, "")).strip() for k in CHAIN_STEP_FIELDS}
        # A step with nothing to attempt, or nothing to check, is not a step.
        if not row["does"] or not row["checks"]:
            continue
        described.append(row)

    payload: dict[str, Any] = {
        "kind": "chain",
        "goal": str(goal or "").strip(),
        "steps": described,
        "stop_when": reason,
        "executable": False,
        "why_not": "a description crosses; execution is the owner's decision, "
                   "argued from a threat model",
    }
    return carry(payload, kind="chain", source=source, ledger_dir=ledger_dir)


def carry_refusal(refusal: dict[str, Any], ledger_dir: str | None = None
                  ) -> tuple[int, dict[str, Any]]:
    """Caller 1 — the shield's half: the shape of a refusal, never its words."""
    return carry_once(_refusal_spore(refusal), kind="refusal", source="urasil",
                      ledger_dir=ledger_dir)


def carry_cycle(ledger_dir: str | None = None) -> tuple[int, dict[str, Any]]:
    """Caller 2 — the cycle's half: the inner world's mood, as it stands."""
    ctx = default_link().prepare()
    return carry_once(_mood_spore(ctx.get("cycle_state") or {}), kind="cycle",
                      source="urasil", ledger_dir=ledger_dir)


def carry_all(ledger_dir: str | None = None) -> dict[str, Any]:
    """What the snake would carry now: the cycle, plus every new refusal.

    Carrying is an **explicit act**, never an automatic side effect of a
    refusal. The sword's own rule — full reach is a decision argued from the
    recorded measurements, not an oversight — applies to the net exactly as it
    does to the tools. So there is a door, and nothing leaves without it.
    """
    out: list[dict[str, Any]] = []
    _status, cycle = carry_cycle(ledger_dir=ledger_dir)
    out.append(cycle)
    from openjarvis.sovereign import shield

    for refusal in reversed(shield.read_refusals(limit=20)):
        _st, res = carry_refusal(refusal, ledger_dir=ledger_dir)
        out.append(res)
    return {
        "offered": len(out),
        "carried": sum(1 for r in out if r.get("carried")),
        "already": sum(1 for r in out if r.get("already")),
        "refused_locally": sum(1 for r in out if r.get("refused_locally")),
        "results": out,
    }


def crossings(spore_dir: Iterable[str] | None = None) -> list[dict[str, Any]]:
    """What the snake has already carried, newest first.

    Read from the store the net wrote, so this is the net's own record and not
    a second ledger. Unreadable lines are skipped rather than raised: a mirror
    that can fail is a mirror that hides.
    """
    import pathlib

    root = pathlib.Path(spore_dir) if spore_dir else hub.spores_dir()
    if not root.exists():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("spore_*.json"), reverse=True):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def _parsed(row: dict[str, Any]) -> dict[str, Any] | None:
    """The payload a receipt carried, parsed — or ``None`` if it is not ours.

    A spore is stored by the net as *text*, because the net judges text. That
    is right for the net and wrong for a reader: making every surface
    ``JSON.parse`` a string inside a JSON object is the writer pushing its own
    work onto each of them, and set 22 already found that once today (the
    receipt's ``verdict``). So the door parses it once, here, and hands the
    surfaces a shape. The raw ``text`` stays in the record untouched.
    """
    try:
        value = json.loads(row.get("text") or "")
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def snake_state() -> dict[str, Any]:
    """The read model, small on purpose — what the surfaces show.

    Says both halves of the seam out loud: what was carried, and what was
    deliberately left behind. A screen that only showed successes would teach
    the reader that the net accepts everything, which is a different product.
    """
    import datetime as _dt

    rows = crossings()
    for row in rows:
        row["carried"] = _parsed(row)
    refusals = [r for r in rows if (r.get("carried") or {}).get("kind") == "refusal"]
    cycles = [r for r in rows if (r.get("carried") or {}).get("kind") == "cycle"]
    return {
        "carried": len(rows),
        "refusals_carried": len(refusals),
        "cycles_carried": len(cycles),
        "crossings": rows[:20],
        "at": _dt.datetime.now().isoformat(timespec="seconds"),
        "words_withheld": list(WITHHELD),
        "not_carried": "the request text and the stem names — a count crosses, "
                       "a name does not. the lexicon is not published by this "
                       "node, and this seam is why.",
        "guard": "allowlist, then proven against the governor's own stems, "
                 "then the net's own door",
    }
