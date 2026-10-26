#!/usr/bin/env python3
"""verify_claims — check every number this repository publishes.

The `v1.0.4.dev262` defect (set 19) was a number that was wrong in **five
places across four files** for as long as the project existed, and every one of
those places looked completely reasonable. Nothing failed. The number was just
stale, and a reader had no way to tell.

So this script is the answer to a narrow question: *which of the claims we
publish can be checked right now, by this machine, without asking anyone?*

It is deliberately **not** a test suite. It reads no source of truth of its own;
it re-derives each claim from the thing the claim is about, so a claim and its
evidence cannot drift together. It prints PASS / FAIL / **SKIP**, and:

* **FAIL** means a published claim is false. Exit status 1.
* **SKIP** means the claim could not be checked here — no network, no `gh`, no
  tag. This is *reported, not hidden and not failed*: a claim nobody can check
  is a claim that must say so out loud, and quietly dropping it would be the
  same class of dishonesty as a wrong number.

Run it with no arguments and no network. It must never need a token, and it
must never write anything.

    python3 scripts/verify_claims.py            # everything
    python3 scripts/verify_claims.py --list     # the ledger, with no checks run

Where this came from
--------------------
This is the only document in the repository whose *content* is other documents'
signatures, so its own provenance is the load-bearing part: the other files
point here, and if this file were stale every signature above would be signing
something unverified.

* **Written by** the OpenCode agent, in set 19, on the owner's instruction, and
  extended once per set that published a new checkable claim. Twenty-six now —
  and the line used to say *Thirteen*, which is how the ledger of every stale
  number in this repository can carry one itself.
* **Derived from** nothing but the thing each claim is about — `git diff`, the
  installed distribution, the ALF kernel's own files, the overlay's own source.
  It has **no** source of truth of its own and no copy of any claim's text: a
  claim and its evidence are read from the same place, so they cannot drift.
* **Its own rules, which it is not above.** It must SKIP loudly rather than
  guess, must not need a token, and must not write. A check that cannot tell an
  empty capture from a changed file SKIPs — see `check_risk_lexicon`, where
  three wrong attempts all reported "the lexicon changed".
* **Falsified before believed.** Every claim in here has been made to FAIL by
  breaking the thing it is about, and a branch that has never failed is not a
  check. `the-whole-layer-is-named` needed two attempts, because the first
  falsification was caught by the *wrong* branch and proved nothing about the
  other one.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# 🚨 The pause between two rounds of a session, read by the session module **at
# import** and defaulting to 60 s. Three of these claims run the real loop, and
# without this line the seventh claim alone would sit for minutes per round and
# the whole ledger would look like a hang. Pinned here, before anything imports
# the module, and named in the ledger entry — a check that only finishes on a
# quiet machine is a check nobody runs.
os.environ.setdefault("BIANCA_SESSION_INTERVAL", "0")
FORK_BASE = "aea9a2a"
UPSTREAM_REPO = "open-jarvis/OpenJarvis"
UPSTREAM_TAG = "v1.0.4"
FORK_POINT = "93c1f87"

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"


class Skip(Exception):
    """The claim cannot be checked on this machine, and we say so."""


def _git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=False
    )
    if out.returncode != 0:
        raise Skip(f"`git {' '.join(args)}` failed: {out.stderr.strip()[:80]}")
    return out.stdout


# ── the ledger ───────────────────────────────────────────────────────────
# Each entry: (key, what it claims, what it proves it, cost)
# `proves` reads the evidence; `asserts` decides. Kept as data so --list is
# never a second, drifting copy of the list.

LEDGER = [
    dict(
        key="version-one-writer",
        claims="the version is declared in exactly one place, and no source file "
               "carries a literal",
        proves="no literal '1.0.4' in any source file; the package reads the "
               "distribution",
        cost="offline",
    ),
    dict(
        key="platform-edits",
        claims="exactly four files outside the sovereign overlay are edited",
        proves="git diff --name-only aea9a2a..HEAD, filtered",
        cost="offline",
    ),
    dict(
        key="risk-lexicon-unchanged",
        claims="RISK_TERMS has not been widened or narrowed since the fork base",
        proves="the stems are still the original block, byte for byte",
        cost="offline",
    ),
    dict(
        key="snake-withholds-the-words",
        claims="a refusal crossing carries a count and never a stem name",
        proves="snake.WITHHELD names both, and neither is in CROSSABLE_REFUSAL",
        cost="offline",
    ),
    dict(
        key="lexicon-read-not-restated",
        claims="the seam reads the lexicon instead of keeping a copy",
        proves="snake.held_stems() is ValueGovernor.RISK_TERMS itself",
        cost="offline",
    ),
    dict(
        key="lexicon-not-served",
        claims="no surface this node serves exposes the held words",
        proves="the hub's own public files and the manifest hold no stem",
        cost="offline",
    ),
    dict(
        key="garden-tends-nothing",
        claims="the garden perturbs nothing: Bianca seeds, nudges and improves no "
               "cell, so an ungated surface cannot launder a refusal past the gate",
        proves="kernel_state reports tended=False, and garden.py contains no write "
               "to a cell's own attributes",
        cost="offline",
    ),
    dict(
        key="gold-values-are-five-values",
        claims="the gold values are five VALUES with two spellings each, and "
               "alignment counts the values — so translating them into English "
               "widened the vocabulary and left every threshold where it was",
        proves="GOLD_VALUES is a dict of 5 groups of 2; two values still score "
               "0.4 and reach frei, five still score 1.0, in either language",
        cost="offline",
    ),
    dict(
        key="voice-has-one-writer",
        claims="the language she answers in holds at every door, because the tail of "
               "her system prompt is written once and the doors pass a language into it",
        proves="no overlay module spells the voice tail out; every module that builds "
               "a system prompt ends it with voice.tail(); both languages name the law "
               "as not hers to reword",
        cost="offline",
    ),
    dict(
        key="garden-defects-still-there",
        claims="the three defects the docs name are still at the lines the docs name, "
               "in a repository that is not ours, has no version control here, and was "
               "edited by us twice in set 34",
        proves="engine.py still calls hexagon_wander in a comment and defines it "
               "nowhere; Zelle.py still stabilises with a literal alpha and engine.py "
               "still demands drift > 0.4; and Zelle.py still kills a cell for "
               "harmonie < 0.2 while engine.py still wants harmonie < 0.5 for a seed, "
               "with the harmony scale still read from the kernel and not typed here",
        cost="offline",
    ),
    dict(
        key="the-garden-fixture-is-a-capture",
        claims="the React garden fixture really is a capture of the garden door, so it "
               "cannot become the writer of a fact its source never carried",
        proves="every UPSTREAM entry in garden.py — the single writer the door reads — "
               "is re-derived out of the fixture's parsed JSON, field by field and "
               "entry by entry; a hand-edited fixture and a source edited without a "
               "re-take both FAIL, and the comparison is structural rather than a "
               "substring match, because json.dumps escapes the accented German this "
               "file is full of and a literal comparison would pass on the encoding "
               "instead of on the sentence",
        cost="offline",
    ),
    dict(
        key="the-whole-layer-is-named",
        claims="the README's file tree really is the whole Bianca layer, so a module "
               "added here cannot be left out of the public face without a red run",
        proves="every .py in src/openjarvis/sovereign/ is named in the README's tree, "
               "and every name in that tree is a file",
        cost="offline",
    ),
    dict(
        key="the-mirror-holds-both-halves",
        claims="the mirror carries what she gave beside what she held, and neither "
               "half can hold an entry without evidence: a grown record always names "
               "a verdict, a refused one always names a direction, and no door that "
               "generates an answer can forget to record it",
        proves="a refusal and an answer written through the real shield are read back "
               "from shield_state() and both are checked field by field; a verdict-"
               "less grown record is refused by the writer; every engine.generate in "
               "the API is followed by a record_grown; and every field both surfaces "
               "render is a key the state really produces",
        cost="offline",
    ),
    dict(
        key="the-garden-death-is-named",
        claims="the garden cannot evolve, and the three lines in the sibling kernel that "
               "make that true are named by location — not by a number this repository "
               "typed, and not by importing a module that is not ours",
        proves="the sibling is re-read at the three named lines and still says what the "
               "diagnosis says it says; idle.py contains no import of it; can_evolve is "
               "the frame's OWN threshold AND its OWN keime count, proven on a frame "
               "that would pass; and the locations travel into the hashed work unit, with "
               "garden_can_evolve=none rather than false when nothing was measured",
        cost="offline",
    ),
    dict(
        key="a-chain-is-a-description",
        claims="a command chain crosses the net as a DESCRIPTION: a step has no field to "
               "type a command into, the module has no execution surface, and a chain "
               "naming no completion criterion is refused at the seam",
        proves="CHAIN_STEP_FIELDS is exactly ('does','checks') and a step arriving with "
               "command/argv/shell reaches the net without them; snake.py holds no "
               "subprocess/os.system/eval/exec after comments are stripped; a blank "
               "stop_when never reaches the net; and the receipt is judged by the gate "
               "like every other spore",
        cost="offline",
    ),
    dict(
        key="a-reconciliation-closes-one-failure",
        claims="the one orphan audit can be reconciled, and the reconciliation closes a "
               "PRESENCE failure and never a CONTENT one — it adds a statement to the "
               "record and removes nothing from it",
        proves="the real writer is run in a throwaway directory: the original audit "
               "survives byte-identically, the contract reaches PASS, and a file that "
               "returns with different bytes still reads tampered with the "
               "reconciliation reported as stale",
        cost="offline",
    ),
    dict(
        key="a-session-turn-carries-its-verdict",
        claims="every turn in a working session is a governed act, not a line of text: "
               "it carries the verdict, the gold source and the second eye, and a turn "
               "arriving without one is refused by the writer rather than recorded",
        proves="the real writer is run in a throwaway directory: a turn with a whole "
               "verdict is read back out of turns.jsonl field by field, a verdict-less "
               "turn is refused, and no writer in the module can append a turn without "
               "going through that one",
        cost="offline",
    ),
    dict(
        key="the-criterion-is-closed",
        claims="a session can only end the way the owner named in advance, the "
               "vocabulary of endings is closed, and a name nobody built is a MALFORMED "
               "REQUEST (400) that lists the vocabulary — never a refusal, because "
               "nothing was judged",
        proves="SESSION_CRITERIA has exactly the two names the door answers with; the "
               "real app in a throwaway directory answers 400 for an empty and for an "
               "unknown criterion, 403 only for a request the governor holds, and the "
               "400 body carries the whole vocabulary so a caller can retry",
        cost="offline",
    ),
    dict(
        key="the-memory-is-the-record",
        claims="what a session remembers is derived from its own turns, every time, and "
               "nowhere else: no second file holds a summary, so there is nothing that "
               "can disagree with the record it summarises",
        proves="the real loop is run over a stub motor in a throwaway directory and the "
               "session's whole file list is printed: memory.json and any other side "
               "file are absent, and session_memory() on the recorded turns equals what "
               "the door serves",
        cost="offline",
    ),
    dict(
        key="the-ceiling-counts-calls",
        claims="the ceiling is a budget of MODEL CALLS and not of rounds, so a team of "
               "three voices spends it three times as fast as a team of one, and the "
               "number on the screen is the number the door counts",
        proves="the real loop runs to ceilings 1, 2, 3, 4 and 7 over a stub motor and "
               "each stops at exactly that many calls, one round per three voices; and "
               "the budget is never a criterion — a session that hits it says the goal "
               "was not met",
        cost="offline",
    ),
    dict(
        key="one-writer-closes-a-session",
        claims="a close is a fact about a meeting, so it is written in exactly one place: "
               "no second writer can set the status, the author or the sentence, and a "
               "request to stop is a QUESTION until a run turns it into the fact",
        proves="the three close keys are written in exactly one function of session.py, "
               "every other writer patches the state without them, and the real loop "
               "plus the real door together produce exactly one close per session — the "
               "run's, or the door's when no run was there to write it",
        cost="offline",
    ),
    dict(
        key="a-proposal-is-one-per-round",
        claims="a reader of the record sees ONE proposal per round, and a closed session "
               "takes no second acceptance: the answer is already written, and a second "
               "one would be a second truth about the same meeting",
        proves="two proposals for the same round collapse to the last one with its own "
               "closed flag — the shape the door serves; the real door answers 409 with "
               "the existing close and its author when a second acceptance arrives; and "
               "the caller-side type carries the closed flag so a screen cannot offer the "
               "act twice",
        cost="offline",
    ),
    dict(
        key="running-is-a-boolean",
        claims="'is it alive' is one question with one answer shape on every door, so a "
               "screen never has to know which door it is reading to know whether it is "
               "looking at a yes or at a process number",
        proves="both doors that report liveness — the list row and the detail — answer a "
               "boolean under `running` and the process under `pid`, in a real app in a "
               "throwaway directory, and the caller-side types for both are booleans",
        cost="offline",
    ),
    dict(
        key="the-quests-are-real-doors",
        claims="every quest in the adventure is a door of THIS node, so the game can show "
               "what the machine actually said and never what it would have preferred to "
               "show",
        proves="the quest table is read out of the face with the comments stripped; every "
               "door it names is a GET route read from api.py's own decorators (never a "
               "list typed here) and every handgriff it names is a POST route there; no "
               "second path literal exists anywhere else in the game; every figure carries "
               "a glyph, a monogram and a colour; and each named door is asked of a real "
               "app in a throwaway directory and answers",
        cost="offline",
    ),
    dict(
        key="the-launch-is-not-the-browsers-to-decide",
        claims="the one door that starts a process decides nothing from its caller: the "
               "argv is written once in the whole layer, the launcher takes no string, "
               "the door has no body, the listing and the launching share one engine "
               "resolver, the spawned process writes nothing into the repository, a "
               "missing engine or a missing binary is answered with a refusal instead "
               "of an invented command, and the launch inherits the environment rather "
               "than writing one — so the answer names both ends of the wire",
        proves="\"serve\" is spelled in motor.py and nowhere else, and that module has "
               "exactly one Popen; motor.start's only parameter is wait_s; the door's "
               "signature is empty and its body names no request; GET /v1/models goes "
               "through motor.resolve and resolves no engine itself; motor_dir() lies "
               "outside the repository; no env= is handed to a process anywhere in the "
               "module and both node_asks and child_listens are in it; and with the "
               "engine on a dead port and the binary off PATH the door answers "
               "started=false, names why, reports no pid and leaves no pid file — with "
               "a running engine it answers already=true",
        cost="offline",
    ),
    dict(
        key="upstream-distance",
        claims=f"{FORK_POINT} is 7 commits past the {UPSTREAM_TAG} tag, and no "
               f".devN may be attached without this check",
        proves="the GitHub compare API's ahead_by",
        cost="network",
    ),
    dict(
        key="fork-point-exists",
        claims=f"{FORK_POINT} is a real upstream commit",
        proves="the GitHub commit API",
        cost="network",
    ),
]


# ── the offline checks ───────────────────────────────────────────────────

def check_version_one_writer() -> tuple[bool, str]:
    """A literal version in a source file is how one wrong number reaches five."""
    sys.path.insert(0, str(REPO / "src"))
    bad: list[str] = []
    for path in (REPO / "src" / "openjarvis").rglob("*.py"):
        if "sovereign" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if re.search(r"""version\s*=\s*["']1\.0\.4["']""", line):
                bad.append(f"{path.relative_to(REPO)}:{lineno}")
    if bad:
        return False, "literal version found at " + ", ".join(bad[:4])
    return True, "no literal in any source file; pyproject declares it"


def check_platform_edits() -> tuple[bool, str]:
    """The honesty of the fork: the list is short, and it is printed."""
    out = _git("diff", "--name-only", f"{FORK_BASE}..HEAD", "--", "src/openjarvis",
               ":!src/openjarvis/sovereign")
    files = [f for f in out.split() if f]
    if len(files) == 4:
        return True, "exactly four: " + ", ".join(
            f.replace("src/openjarvis/", "") for f in files
        )
    return False, f"expected 4 platform edits, found {len(files)}: {files}"


def check_risk_lexicon() -> tuple[bool, str]:
    """The owner's standing call: report the gap, never widen it."""
    sys.path.insert(0, str(REPO / "src"))
    from openjarvis.sovereign.link import ValueGovernor  # noqa: PLC0415

    stems = list(ValueGovernor.RISK_TERMS)
    if len(stems) != 13:
        return False, f"expected 13 stems, found {len(stems)}: {stems}"
    source = (REPO / "src/openjarvis/sovereign/link.py").read_text(encoding="utf-8")
    # Walk the block line by line, dropping comment-only lines, until the
    # bracket closes. Two regex attempts failed here, both in the same way and
    # both silently: the block carries a comment with parentheses in it, so a
    # non-greedy `.*?[\]\)]` stopped *inside the comment* and captured nothing.
    # It reported a difference that was really an empty capture. A check that
    # cannot tell those apart is worse than no check — so this one is proven by
    # breaking it, in both directions, and an empty capture now SKIPS loudly
    # instead of claiming the lexicon changed.
    lines = source.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if re.match(r"\s*RISK_TERMS\s*[=[(]", line)),
        None,
    )
    if start is None:
        raise Skip("could not locate the RISK_TERMS assignment in link.py")
    body_lines: list[str] = []
    for line in lines[start + 1:]:
        # Skip the comment BEFORE testing for the close: that comment holds
        # parentheses, and testing first ended the walk on the comment and
        # captured nothing. Three attempts at this one line, each wrong in a way
        # that looked like a changed lexicon.
        if line.strip().startswith("#"):
            continue
        body_lines.append(line)
        if "]" in line or ")" in line:
            break
    body = "\n".join(body_lines)
    # The declared block must equal the live list verbatim, in order. That
    # catches two different things, and it is worth being exact about which:
    #   · the count is pinned, so an ADDITION or a REMOVAL fails — and those do
    #     change what the gate holds;
    #   · comparing the file's text to the runtime value catches a DIVERGENCE
    #     between them, which is the shape of a stale copy.
    # A pure REORDERING passes, deliberately: editing the source moves the
    # declared block and the live list together, so no comparison of the two can
    # see it — and it does not matter. `evaluate` does `sum(1 for r in RISK_TERMS
    # if r in t)` and `any(...)`; neither depends on order. Claiming this check
    # catches a reorder would be a false claim about a check, which is worse
    # than having no check.
    declared = re.findall(r'"([^"]+)"', body)
    if not declared:
        raise Skip("the RISK_TERMS block holds no quoted stem — a broken check, "
                   "not a changed lexicon")
    if declared != stems:
        only_live = [s for s in stems if s not in declared]
        only_declared = [s for s in declared if s not in stems]
        return False, (f"the declared block and the live list differ "
                       f"(+{only_live} -{only_declared}, order "
                       f"{'same' if sorted(declared) == sorted(stems) else 'differs'})")
    return True, f"all {len(stems)} stems declared verbatim, in order"


def check_snake_withholds() -> tuple[bool, str]:
    sys.path.insert(0, str(REPO / "src"))
    from openjarvis.sovereign import snake  # noqa: PLC0415

    leaked = [f for f in snake.WITHHELD if f in snake.CROSSABLE_REFUSAL]
    if leaked:
        return False, f"withheld fields are on the allowlist: {leaked}"
    if len(snake.CROSSABLE_REFUSAL) < 8:
        return False, f"the allowlist is suspiciously short: {snake.CROSSABLE_REFUSAL}"
    return True, (f"{len(snake.WITHHELD)} fields withheld, "
                  f"{len(snake.CROSSABLE_REFUSAL)} allowed")


def check_lexicon_read() -> tuple[bool, str]:
    sys.path.insert(0, str(REPO / "src"))
    from openjarvis.sovereign import snake  # noqa: PLC0415
    from openjarvis.sovereign.link import ValueGovernor  # noqa: PLC0415

    if snake.held_stems() != tuple(ValueGovernor.RISK_TERMS):
        return False, "the seam keeps its own copy of the lexicon"
    return True, "the seam reads ValueGovernor.RISK_TERMS (13 stems, one writer)"


def check_lexicon_not_served() -> tuple[bool, str]:
    """Read the node's own store, not a running server: this must work offline."""
    sys.path.insert(0, str(REPO / "src"))
    from openjarvis.sovereign.snake import words_that_would_trip_the_gate  # noqa: PLC0415

    root = Path(os.environ.get("BIANCA_HUB_DIR", str(REPO / "hub")))
    if not root.exists():
        raise Skip(f"no hub store at {root} — nothing published to check")
    leaks: list[str] = []
    scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        found = words_that_would_trip_the_gate(raw)
        if found:
            leaks.append(f"{path.relative_to(root)}: {found}")
    if leaks:
        return False, f"{len(leaks)} published file(s) name a held word — " + "; ".join(
            leaks[:3]
        )
    return True, f"{scanned} published file(s), none names a held word"


# ── the sibling kernel (set 24) ──────────────────────────────────────────

def _colorverse() -> Path:
    raw = os.environ.get("BIANCA_COLORVERSE_DIR")
    if raw:
        return Path(raw)
    return Path(os.environ.get("BIANCA_ALF_ROOT", "/home/sam/Repos/ALF")) / "Colorverse"


def check_garden_tends_nothing() -> tuple[bool, str]:
    """Set 24's decision, re-derived from the module that could break it.

    The garden is the one ungated surface in the product, so the promise that
    Bianca perturbs nothing is load-bearing in a way no other promise here is:
    if a cell could be nudged, the garden would be a way to launder a refusal
    past the gate. So this checks the code, not a comment about the code.
    """
    from openjarvis.sovereign import garden

    state = garden.kernel_state()
    if state["tended"]:
        return False, "kernel_state reports tended=True — the garden tends something"
    source = (REPO / "src/openjarvis/sovereign/garden.py").read_text(encoding="utf-8")
    # No write to a cell's own attributes anywhere in the module or in the
    # child: the kernel's world is read and stepped, never adjusted.
    for forbidden in (".harmonie =", ".drift +=", ".energy +=", ".hue ="):
        if forbidden in source:
            return False, f"garden.py writes to the world: {forbidden!r}"
    return True, "tended=False, and the module never writes to a cell"


def check_voice_has_one_writer() -> tuple[bool, str]:
    """Set 26's language claim, re-derived from the source of every prompt.

    The language she answers in is only a language if it holds at *every* door.
    Before this there were four open-coded copies of the tail of her system
    prompt — two in api.py with identical wording, one in cli.py and one in
    agent.py with different wording. A language added to those four would have
    been a setting that was sometimes true, and a setting that is sometimes
    true is indistinguishable from a bug.

    So this checks two things, and both are falsifiable:
      · no module outside ``voice.py`` spells the instruction out, and
      · every place that builds a system prompt ends its tail with
        ``voice.tail(...)`` rather than a string of its own.
    An open-coded fifth copy FAILs the first. A call site that drops the tail
    while a language picker exists FAILs the second.
    """
    from openjarvis.sovereign import voice

    overlay = REPO / "src/openjarvis/sovereign"
    offenders: list[str] = []
    sites: list[str] = []
    for path in sorted(overlay.rglob("*.py")):
        if path.name == "voice.py":
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(overlay).as_posix()
        # 1. the instruction spelled out anywhere but in voice.py
        for literal in ("agency-preserving language", "Nenne höchstens drei Wege"):
            if literal in text:
                offenders.append(f"{rel} spells the voice tail out ({literal!r})")
        # 2. a system prompt that does not end in the one writer
        if "system_prompt" in text or "soul = (" in text:
            if "voice.tail(" not in text:
                offenders.append(f"{rel} builds a system prompt without voice.tail()")
            else:
                sites.append(rel)
    if offenders:
        return False, "; ".join(offenders)

    # 3. and the two languages must actually differ, or the picker is decoration
    if voice.tail("de") == voice.tail("en"):
        return False, "the two languages produce the same tail — the picker is decoration"
    if "Deutsch" not in voice.tail("de") or "English" not in voice.tail("en"):
        return False, "a language does not name itself in its own tail"
    # 4. and the law must be named in both, or translating her would translate it
    for code in voice.supported():
        if "zurueckhalten" not in voice.tail(code):
            return False, f"the {code} tail does not tell her the law is not hers to reword"
    return True, f"one writer; tail in {len(sites)} module(s), both languages name the law"


def check_gold_values_are_five_values() -> tuple[bool, str]:
    """Set 26's governance change, re-derived from the arithmetic itself.

    Translating the gold values into English is only safe because the gold
    values are **five values with two spellings each**, and alignment counts
    the values. The plausible wrong implementation — a flat list of ten words —
    would keep the diff looking like a translation while quietly doubling the
    denominator: 0.4 would then mean four English words instead of two German
    ones, and all five values in English would score 1.0 by counting words.

    So this checks the *shape*, not the words, and it also checks that the
    thresholds still mean what they meant. Both halves are falsifiable: a flat
    list FAILs the first, and a retyped denominator FAILs the second.
    """
    from openjarvis.sovereign.link import ValueGovernor

    gold = ValueGovernor.GOLD_VALUES
    if not isinstance(gold, dict):
        n = len(gold)  # type: ignore[arg-type]
        return False, (
            f"GOLD_VALUES is a {type(gold).__name__} of {n} items — a flat list makes "
            "the denominator the word count, not the value count"
        )
    if len(gold) != 5:
        return False, f"there are {len(gold)} gold values, not 5 — the threshold moved"
    for key, group in gold.items():
        if not isinstance(group, (tuple, list)) or len(group) != 2:
            return False, f"{key!r} has {group!r} — expected one value in two languages"
        if key not in group:
            return False, f"{key!r} is not among its own spellings {group!r}"

    gov = ValueGovernor(Path("/tmp/opencode/verify-gold"))
    # 2 of 5 values -> 0.4 -> frei. This is the pre-change arithmetic, checked
    # against the post-change vocabulary: the threshold must still mean "two
    # values", not "four words".
    two = gov.evaluate("clarity and integrity")
    if abs(float(two["alignment"]) - 0.4) > 1e-9:
        return False, f"two values scored {two['alignment']}, not 0.4 — the denominator moved"
    if two["verdict"] != "frei":
        return False, f"two values gave {two['verdict']!r}, not 'frei'"
    # and all five in either language is still exactly 1.0, not 1.0 by luck
    for text in (
        "clarity integrity resonance depth harmony",
        "Klarheit Integritaet Resonanz Tiefe Harmonie",
    ):
        allv = gov.evaluate(text)
        if abs(float(allv["alignment"]) - 1.0) > 1e-9:
            return False, f"{text[:24]!r} scored {allv['alignment']}, not 1.0"
    return True, "five values, two languages each; thresholds still count values"


def check_garden_defect_locations_hold() -> tuple[bool, str]:
    """Four documentation files publish line numbers **into a sibling repo**.

    A claim about someone else's code rots silently: the file moves, the line
    number does not, and the sentence still reads perfectly. That already
    happened once in that kernel — `engine.py:87` calls `hexagon_wander`, and
    0 files define it, so the comment has been naming a function that does not
    exist since before this fork existed. So the locations are re-read here.
    """
    root = _colorverse()
    if not (root / "engine.py").is_file():
        raise Skip(f"the Colorverse sibling is not at {root}")
    engine = (root / "engine.py").read_text(encoding="utf-8")
    zelle = (root / "Zelle.py").read_text(encoding="utf-8")

    if "hexagon_wander" not in engine:
        return False, "engine.py no longer mentions hexagon_wander — the claim is stale"
    if "def hexagon_wander" in engine:
        return False, "hexagon_wander is now DEFINED — '0 files define it' is stale"
    if "# self.hexagon_wander()" not in engine:
        return False, "engine.py no longer has the commented-out wander call"
    if "self.stabilisierung()" not in zelle:
        return False, "Zelle.py no longer calls stabilisierung() unconditionally"
    if "self.alpha = 0.05" not in zelle:
        return False, "Zelle.py's alpha is no longer a literal 0.05"
    if "z.drift > 0.4" not in engine:
        return False, "engine.py no longer demands drift > 0.4 for a keim"

    # ── set 34: the third defect, found after the owner's two kernel repairs ──
    # This one is searched by CONTENT, like the two above, and deliberately not by
    # line: the sibling has no version control and our own repairs moved it
    # twice in one set, so a line-addressed claim about it would be a claim
    # about our own typing rather than about the kernel. The pair below is the
    # whole finding — `harmonie < 0.2` KILLS, and the keim needs the same
    # quantity with the same sign — and it is the reason a living garden is not
    # reachable by changing a number.
    if "self.harmonie < 0.2" not in _code_only(zelle):
        return False, ("Zelle.py no longer kills a cell for harmonie < 0.2 — "
                       "'a cell dies for being different' is stale")
    if "z.harmonie < 0.5" not in _code_only(engine):
        return False, ("engine.py no longer requires harmonie < 0.5 for a keim — "
                       "the death criterion and the growth criterion are no longer "
                       "the same sign")
    # The counter-example must hold: if the keim ever stopped wanting LOW
    # harmonie, the third entry would be describing a coincidence. So the
    # harmony scale itself has to still be the variance of a uniform spread,
    # read from the kernel rather than typed here.
    if "HARMONIE_NULLPUNKT = 10800.0" not in _code_only(zelle):
        return False, ("Zelle.py's harmony scale is no longer 360^2/12 — the "
                       "diagnosis's arithmetic is from this repository, not the kernel")
    return True, ("both original defects still hold, and the third one too: a cell "
                  "dies for the difference a seed needs")


def _fixture_states(text: str) -> dict[str, object]:
    """The three ``export const NAME: GardenState = {…}`` literals, parsed.

    Parsed rather than searched. The fixture is written by ``json.dumps`` with
    ``ensure_ascii=True``, so every German umlaut in it is a ``\\uXXXX`` escape
    and a substring comparison against the source would be a check on the
    **encoding**, not on the sentence — it would FAIL on a correct file and pass
    on a wrong one that happened to share an escape.
    """
    out: dict[str, object] = {}
    marker = ": GardenState = "
    at = 0
    while (at := text.find(marker, at)) != -1:
        start = at + len(marker)
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
        name_start = text.rfind("export const ", 0, at)
        name = text[name_start + len("export const "):at].split(":")[0].strip()
        out[name] = json.loads(text[start:i + 1])
        at = i + 1
    return out


def check_garden_fixture_is_a_capture() -> tuple[bool, str]:
    """The fixture must carry what `garden.py` says, and not one sentence more.

    🚨 **This exists because for one whole set the direction was inverted.** The
    SET 35 retraction of the garden's diagnosis was written into
    `sovereign-api.garden-fixture.ts` — a file whose whole purpose is to be a
    capture — and **never into `garden.py`**, which is the single writer the door
    reads. Every React test was green against a sentence the live node never
    sent, while `GET /v1/garden` still served the retracted verdict: *"the
    evolution path is unreachable, not one seed appears, the best ever measured
    is 2"*. Two surfaces, one garden, two different verdicts — set 21's
    *present but wrong evidence* one layer down.

    So this compares the **source** to the fixture, not to a running node:
    `UPSTREAM` is read at import time, so a node started before an edit keeps
    serving the old text, and a fixture re-taken in a fresh process is then
    *fresher than the door it claims to capture*. A check that needed the node
    would fail for a reason that has nothing to do with the fact.

    ⚠️ **Two named gaps, both deliberate, both found by falsifying this.**

    * **The frame's numbers are NOT checked, and cannot be.** A frame is a fact
      about a moment: `step 401`, `hue_mean 205.8220`, `spread 160.1702` were
      true when the child wrote them and are stale a quarter of a second later.
      Editing any of them FAILs nothing here — measured, by doing it. Only the
      **shape** is checked: that `convergence_disputed`, `cluster_start` and
      `grew_at` are present at all, and that the first is not `true` beside a
      cluster count that never moved, which would mean one arm is fiction.
      **The written diagnosis has a writer; the moment does not.** That is the
      same split as the `dev262` number, and it is why the frame's own
      sentences say „this run's".
    * **Both directions have fired on real incidents, not on sabotage.** The
      first red run of this claim was not a test: it was the true state after
      `garden.py` had been edited and the fixture not yet re-taken. The
      hand-edit direction was then proved by cutting one emoji out of one
      upstream entry — and the first attempt to do that **replaced nothing at
      all** (`find` returned -1, because `json.dumps` writes a non-BMP emoji as
      a surrogate pair), so the check passed on an untouched file. **A
      falsification that did not falsify anything is a harness fault, and it is
      reported here rather than quietly retried.**
    """
    fx = REPO / "frontend" / "src" / "lib" / "sovereign-api.garden-fixture.ts"
    if not fx.is_file():
        return False, f"{fx} does not exist"
    if "openjarvis" not in sys.path:
        sys.path.insert(0, str(REPO / "src"))
    try:
        from openjarvis.sovereign import garden
    except Exception as exc:  # pragma: no cover - import shape, not a verdict
        return False, f"the single writer could not be imported: {exc}"

    states = _fixture_states(fx.read_text(encoding="utf-8"))
    if not states:
        return False, "no `export const … : GardenState = {` literal found in the fixture"
    live = states.get("GARDEN_LIVE")
    if not isinstance(live, dict):
        return False, "GARDEN_LIVE is missing from the fixture"

    got = live.get("kernel", {}).get("upstream")
    if got != list(garden.UPSTREAM):
        if not isinstance(got, list):
            return False, "the fixture's upstream list is not a list"
        ids_got = [e.get("id") for e in got if isinstance(e, dict)]
        ids_want = [e["id"] for e in garden.UPSTREAM]
        if ids_got != ids_want:
            return False, (f"the fixture's upstream entries are {ids_got}, the single "
                           f"writer has {ids_want}")
        for a, b in zip(got, garden.UPSTREAM):
            for field in ("id", "where", "what", "why_it_matters"):
                if a.get(field) != b[field]:
                    return False, (f"upstream {b['id']!r} field {field!r} in the fixture "
                                   f"is not the source's text — the fixture was edited "
                                   f"by hand, or the source was edited without a re-take")
        return False, "the fixture's upstream list differs from the single writer"

    # The frame's own contradiction must survive into the fixture, because both
    # surfaces decide what to print from it. Measured: without these three the
    # garden screen prints "er konnte nie wachsen" beside a grown cluster count.
    frame = live.get("frame", {})
    for field in ("convergence_disputed", "cluster_start", "grew_at"):
        if field not in frame:
            return False, (f"the captured frame has no {field!r} — a screen cannot show "
                           f"both arms of the frame's contradiction")
    if frame.get("convergence_disputed") and frame.get("cluster") == frame.get("cluster_start"):
        return False, ("the capture claims the frame contradicts itself but its cluster "
                       "count never changed — one of the two arms is not real")
    return True, ("the fixture carries every upstream entry field for field, and the "
                  "frame's self-contradiction with it")


# ── the mirror, both halves ───────────────────────────────────────────────

# Every field a grown record must carry. A growth record without these is the
# set-16/17/18 defect — an outcome with no evidence — in the newest file of the
# newest set, and it is the reason this check exists rather than a count of
# entries. `cannot_record` is the field the owner asked for and nothing can
# measure: the record has to name its own blind spot or it is claiming to be a
# testimony about understanding.
GROWN_EVIDENCE = ("verdict", "gold_source", "cannot_record", "gold_hits", "eye")

# A name in prose is not a name in code. This branch was satisfied once by a
# COMMENT that mentioned `grown_gold` while the line using it was deleted — the
# same trap as grepping a bundle for an identifier that was minified away. So
# comments are removed before any surface is searched, and a field named only in
# a comment now FAILs (falsification 3d).
#
# Two patterns, NOT one with DOTALL. The first attempt compiled them together
# with re.DOTALL, and `^[ \t]*//.*$` then matched from a `//` comment all the way
# to the end of the file — so the check FAILED on correct code, which is the
# other half of the same mistake: a check that cannot be trusted when it is
# right is not a check.
_COMMENT_BLOCK = re.compile(r"/\*.*?\*/|<!--.*?-->", re.DOTALL)
_COMMENT_LINE = re.compile(r"(?<![:'\"/])//[^\n]*|^[ \t]*#[^\n]*", re.MULTILINE)


def _code_only(text: str) -> str:
    """The source with every comment removed."""
    return _COMMENT_LINE.sub(" ", _COMMENT_BLOCK.sub(" ", text))


def _ohne_dokumente(text: str) -> str:
    """Python source with comments **and** docstrings removed, lines intact.

    Written for claim ``the-launch-is-not-the-browsers-to-decide``, which failed
    *correct* code because a docstring explained the absence of the very keyword
    it was looking for (``child_host()``: *„``start`` passes no ``env=``"*).
    Comments are already handled by :func:`_code_only`; a docstring is the same
    kind of prose and the same trap in reverse — set 28's phantom branch was
    satisfied by a comment naming a field whose line had been deleted.

    Blank rather than delete, so the line numbers a failure message prints still
    point at the source. A module that does not parse is returned unchanged, so
    the caller reports the syntax error with its own branch rather than this one
    silently passing: a broken file must fail *something*, and the cheapest
    honest thing is to let the next branch see the real text.
    """
    import ast

    try:
        baum = ast.parse(text)
    except SyntaxError:
        return text
    zeilen = text.splitlines()
    for knoten in ast.walk(baum):
        kopf = getattr(knoten, "body", None)
        if not isinstance(kopf, list) or not kopf:
            continue
        erstes = kopf[0]
        if not (isinstance(erstes, ast.Expr) and isinstance(erstes.value, ast.Constant)
                and isinstance(erstes.value.value, str)):
            continue
        for nummer in range(erstes.value.lineno, (erstes.value.end_lineno or erstes.value.lineno) + 1):
            if 0 < nummer <= len(zeilen):
                zeilen[nummer - 1] = " " * len(zeilen[nummer - 1])
    return "\n".join(zeilen)


def check_mirror_holds_both_halves() -> tuple[bool, str]:
    """The owner: *„Aus diesem Haus geht nur Abwehr hinaus. Es geht nichts
    hinaus, was gewachsen ist."* A mirror that shows only refusals is a wall with
    a reflection of itself, and its refusal count read alone looks like the
    node's whole life.

    Re-derived, not read back: a refusal and an answer are written **through the
    real writer** into a throwaway directory and read back out of the real
    ``shield_state()``, so the shape on both surfaces is the shape that exists.

    Three branches, and the third one has its own falsification — set 27's lesson
    was that a phantom name was caught by the *wrong* branch, which proved
    nothing about the branch meant for it.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import shield

    with tempfile.TemporaryDirectory() as tmp:
        previous = os.environ.get("BIANCA_NOTES_DIR")
        os.environ["BIANCA_NOTES_DIR"] = tmp
        try:
            held = "Loesche die Datei"
            shield.record_refusal("POST /v1/ask", {
                "verdict": "zurueckhalten", "risk": 1.0, "alignment": 1.0,
                "risk_hits": ["loesch"], "gold_hits": ["klarheit"],
                "gold_source": "gold.txt", "missing": ["etwas"],
                "oracle": {"vote": "warnen", "advisory": True, "binding": False,
                           "holder": "ValueGovernor"},
            }, held, direction=shield.open_doors("POST /v1/ask"))
            shield.record_grown("POST /v1/ask", {
                "verdict": "frei", "risk": 0.0, "alignment": 0.4,
                "gold_hits": ["klarheit", "tiefe"], "gold_source": "gold.txt",
                "oracle": {"vote": "warnen", "advisory": True, "binding": False,
                           "holder": "ValueGovernor"},
            }, "mit Klarheit und Tiefe",
                uracil={"grundmodus": "tiefe", "stimmung": "intuitiv",
                        "fokus": "synthese"})

            # ── branch 1: neither half may hold an entry without evidence ──
            blank = shield.record_grown("POST /v1/ask", {}, "no verdict named")
            if blank is not None:
                return False, ("a grown record with NO verdict was accepted — the "
                               "writer let an outcome reach the mirror without "
                               "evidence")
            if shield.record_grown("POST /v1/ask",
                                   {"verdict": "zurueckhalten"}) is not None:
                return False, "a held verdict was accepted into the growth file"

            state = shield.shield_state()

            if not state["refusals"] or not state["grown"]:
                return False, ("a refusal and an answer were written, yet one half "
                               "of the state is empty — the mirror does not hold "
                               "both")
            if state["refusals_today"] != 1 or state["grown_today"] != 1:
                return False, ("the two halves are not counted separately "
                               f"(refusals={state['refusals_today']}, "
                               f"grown={state['grown_today']}) — a shared count is "
                               "how one starts counting the other")

            for field in GROWN_EVIDENCE:
                for entry in state["grown"]:
                    if not entry.get(field):
                        return False, f"a grown record is missing {field!r}"
            for entry in state["refusals"]:
                # a refusal names where it happened, what was judged, and where
                # else one can go — a wall with no door is the thing it replaced
                for field in ("where", "verdict", "gold_source"):
                    if not entry.get(field):
                        return False, f"a refusal is missing {field!r}"
                if not (entry.get("direction") or {}).get("doors"):
                    return False, "a refusal carries no direction"

            # the direction must be a constant, or "here are other doors" is the
            # bypass wearing a helpful hat
            other = shield.open_doors("POST /v1/chat")
            first = shield.open_doors("POST /v1/ask")
            if other["doors"] != first["doors"] or other["note"] != first["note"]:
                return False, ("the direction varies with the door, so it is not a "
                               "constant door list")
            blob = json.dumps(first, ensure_ascii=False).lower()
            from openjarvis.sovereign.link import ValueGovernor
            for stem in ValueGovernor.RISK_TERMS:
                if stem.lower() in blob:
                    return False, f"the direction carries the held stem {stem!r}"
        finally:
            if previous is None:
                os.environ.pop("BIANCA_NOTES_DIR", None)
            else:
                os.environ["BIANCA_NOTES_DIR"] = previous

    # ── branch 2: no door that generates can forget to record ──────────────
    # Deliberately a *source* reading, because the alternative — counting grown
    # records in a live run — cannot tell "this door forgot" from "nobody asked
    # this door". A door is a function in the file; so is the call that owes it a
    # record.
    #
    # Two things this branch learned by being wrong first. It searched *forward*
    # from `engine.generate`, so a door that records before generating would have
    # been failed for doing nothing wrong. And it read the file as text, so a
    # syntactically broken `api.py` — which is what a careless edit leaves
    # behind — passed a check about that file. Both are fixed here: the whole
    # enclosing function is read, and the source must compile.
    api_path = REPO / "src/openjarvis/sovereign/api.py"
    api = api_path.read_text(encoding="utf-8")
    try:
        compile(api, str(api_path), "exec")
    except SyntaxError as exc:
        return False, f"api.py does not parse ({exc}) — a text check would pass it"

    def _function_containing(offset: int) -> str:
        """The whole `@app`-decorated function around a byte offset."""
        start = 0
        for marker in ("\n    @app.", "\n    def ", "\nasync def "):
            found = api.rfind(marker, 0, offset)
            if found != -1:
                start = max(start, found)
        tail = api[start:]
        stop = len(tail)
        for marker in ("\n    @app.", "\n    def ", "\nasync def "):
            found = tail.find(marker, 1)
            if found != -1:
                stop = min(stop, found)
        return tail[:stop]

    generates = [m.start() for m in re.finditer(r"\bengine\.generate\(", api)]
    if not generates:
        raise Skip("no engine.generate call found in api.py — the door moved")
    doors: set[str] = set()
    for start in generates:
        body = _function_containing(start)
        if "record_grown" not in body:
            return False, ("a door calls engine.generate and never records what it "
                           "answered — the next door would forget silently")
        name = re.search(r"\n    def (\w+)", body)
        doors.add(name.group(1) if name else "?")
    if len(generates) != len(doors):
        return False, ("two generation sites share one function, or one function "
                       "holds both — the per-door accounting is no longer per door")

    # The same seam from the other side. A test that reaches a generating door
    # records what it answered — into `~/.openjarvis/bianca/notes/`, unless the
    # class points `BIANCA_NOTES_DIR` somewhere else. Measured on 2026-09-28:
    # two classes reached a generating door without doing so, and one run added
    # three lines to the owner's real mirror, so `grown_today` — published on
    # both surfaces as what she gave today — counted the test suite as well as
    # the person. Every class that calls a generating door must therefore set
    # the variable. Named explicitly so a new class cannot forget silently.
    tests_path = REPO / "tests/test_sovereign.py"
    if tests_path.is_file():
        test_src = test_src_lines = tests_path.read_text(encoding="utf-8").splitlines()
        current, offender = "", ""
        for line in test_src:
            if line.startswith("class "):
                current = line
            if current and re.search(r'client\.post\("/v1/(ask|chat|agent)"', line):
                body = test_src[test_src.index(current):]
                end = next((i for i, l in enumerate(body[1:], 1)
                            if l.startswith("class ")), len(body))
                block = "\n".join(body[:end])
                if "BIANCA_NOTES_DIR" not in block and not offender:
                    offender = current.split("(")[0].replace("class ", "").strip()
        if offender:
            return False, (f"test class {offender!r} reaches a generating door "
                           f"without setting BIANCA_NOTES_DIR — the suite writes "
                           f"into the owner's real mirror")

    # ── branch 3: no phantom field. Falsified on its own. ────────────────
    # A name in a type or a template that the state does not produce is the
    # set-27 defect, and set 27 learned the hard way that a *different* branch
    # catching it proves nothing about this one. So this branch is tested by
    # asking the state for a key the surfaces use, and separately by a field the
    # surfaces would have to survive without.
    surfaces = {
        "face": REPO / "src/openjarvis/sovereign/web/ui.html",
        "react": REPO / "frontend/src/lib/sovereign-api.ts",
    }
    if not all(p.is_file() for p in surfaces.values()):
        raise Skip("a surface is missing, so the phantom branch cannot be run")
    for name, path in surfaces.items():
        text = _code_only(path.read_text(encoding="utf-8"))
        for field in ("grown_today", "grown_gold", "grown_cannot_record",
                      "cannot_record", "direction"):
            if field not in text:
                return False, f"the {name} surface no longer names {field!r}"
    # and the reverse: a field the state promises that nothing renders would be
    # a claim with no reader. Named explicitly so adding one is a decision.
    for field in ("grown_memory", "grown"):
        if field not in _code_only(surfaces["react"].read_text(encoding="utf-8")):
            return False, f"the react type no longer declares {field!r}"

    return True, (f"a refusal and an answer both carry their evidence, the two "
                  f"counts stay separate, all {len(doors)} doors that generate "
                  f"({', '.join(sorted(doors))}) record, and both surfaces name "
                  f"fields the state produces")


# ── the network checks ───────────────────────────────────────────────────

def _fetch(url: str, timeout: float = 8.0) -> dict:
    request = urllib.request.Request(
        url, headers={"User-Agent": "bianca-verify-claims", "Accept": "application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise Skip(f"GitHub returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise Skip(f"no network: {type(exc).__name__}") from exc
    except (ValueError, json.JSONDecodeError) as exc:
        raise Skip(f"GitHub sent something that is not JSON: {type(exc).__name__}") from exc


def check_whole_layer_is_named() -> tuple[bool, str]:
    """A tree that says "the whole layer" and names 7 of 18 modules is a lie
    nobody can see, because nothing fails. It sat that way through fifteen sets.
    Both directions are asserted: a module on disk but unnamed, and a name in the
    tree with no file behind it (a rename that half-landed)."""
    overlay = REPO / "src/openjarvis/sovereign"
    on_disk = {p.name for p in overlay.glob("*.py")} - {"__init__.py"}
    if not on_disk:
        raise Skip("no modules found in src/openjarvis/sovereign/")

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    start = readme.find("src/openjarvis/sovereign/   ADDED")
    end = readme.find("4 small edits to the platform", start)
    if start < 0 or end < 0:
        raise Skip("could not locate the README's file tree")
    tree = readme[start:end]
    named = {f"{n}.py" for n in re.findall(r"[│ ]\s+(\w+)\.py", tree)}

    missing = sorted(on_disk - named)
    if missing:
        return False, f"{len(missing)} module(s) on disk but unnamed in the README: " \
                      + ", ".join(missing)
    phantom = sorted(n for n in named - on_disk if n != "__init__.py")
    if phantom:
        return False, f"the README names files that do not exist: {', '.join(phantom)}"
    return True, f"all {len(on_disk)} modules and ui.html are named; nothing is a ghost"


def check_upstream_distance() -> tuple[bool, str]:
    data = _fetch(
        f"https://api.github.com/repos/{UPSTREAM_REPO}/compare/{UPSTREAM_TAG}...{FORK_POINT}"
    )
    if "ahead_by" not in data:
        raise Skip(f"no ahead_by in the response: {sorted(data)[:6]}")
    ahead, behind = data["ahead_by"], data.get("behind_by")
    if behind:
        return False, f"{FORK_POINT} is {behind} commit(s) BEHIND {UPSTREAM_TAG}"
    if ahead != 7:
        return False, f"ahead_by is {ahead}, not 7 — a .devN must not be re-attached"
    return True, f"ahead_by {ahead}, behind_by {behind} — .dev7 would be the truth"


def check_fork_point_exists() -> tuple[bool, str]:
    data = _fetch(f"https://api.github.com/repos/{UPSTREAM_REPO}/commits/{FORK_POINT}")
    sha = data.get("sha", "")
    date = ((data.get("commit") or {}).get("committer") or {}).get("date", "?")
    if not sha.startswith(FORK_POINT):
        raise Skip(f"GitHub resolved {FORK_POINT} to {sha[:12]!r}")
    return True, f"{sha[:12]} committed {date}"


# ── set 29: the garden's death, the chain's shape, the reconciliation ─────


def check_garden_death_is_named() -> tuple[bool, str]:
    """The garden is the one ungated surface, and set 24 left it as a fact
    without a cause: "born still, drift 4.49e-62, keime 0". A number with no
    reason invites a budget — and the budget was proposed, and it was wrong,
    because the frame is 742 bytes overwritten at a fixed path and cannot grow
    under any cap.

    So the death is named by location, in a repository that is not ours. That
    makes this a claim about someone else's lines, which is exactly the shape
    that rots silently, so the sibling is re-read at the three places the
    diagnosis names. The arithmetic is theirs: `saturings.py` makes the
    neighbourhood a ring, `Zelle.py` has exactly one hue rule and it averages,
    and `engine.py` wants a difference. Averaging on a connected graph converges
    for every alpha > 0 — there is no alpha that makes drift appear.
    """
    root = _colorverse()
    if not (root / "Zelle.py").is_file():
        raise Skip(f"the Colorverse sibling is not at {root}")
    sys.path.insert(0, str(REPO / "src"))
    import tempfile
    import time as _time

    from openjarvis.sovereign import idle as idle_mod

    where = [rule["where"] for rule in idle_mod.GARDEN_DEATH]
    if len(where) != 3:
        return False, f"the diagnosis names {len(where)} locations, not three"

    # ── the sibling is re-read WHERE THE DIAGNOSIS SAYS, not merely in the file ──
    # The first version of this branch resolved the file name and stopped there.
    # Pointing `Zelle.py:95` at line 9999 — a line that does not exist — left the
    # claim PASSing, because the file was there. That is the exact shape this
    # repository hunts: a claim about a sibling's line, checking the sibling's
    # *directory*. So the arithmetic is expected HERE, in this check, and has to
    # be found inside the named line range: move the code and the claim FAILs
    # naming the file, instead of quietly describing a past state.
    SATURINGS_EXPR = ("(i - 1) % n", "(i + 3) % n")
    ZELLE_EXPR = ("(1 - self.alpha) * self.hue", "self.alpha * avg_hue")
    ENGINE_EXPR = ("evolutionskeim", "z.drift > 0.4", "z.energy > 0.6")

    def at(loc: str) -> str:
        """The lines the location names, and nothing else."""
        relative, _, span = loc.partition(":")
        relative = relative.strip()
        if relative.startswith("Colorverse/"):
            relative = relative[len("Colorverse/"):]
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"{relative} is not in the kernel any more")
        lines = path.read_text(encoding="utf-8").splitlines()
        first, _, last = span.partition("-")
        try:
            start = int(first)
            end = int(last or first)
        except ValueError:
            return ""  # a location with no number is a shrug, and reads as one
        return "\n".join(lines[start - 1:end])

    for loc, expected in ((idle_mod.GARDEN_DEATH[0]["where"], SATURINGS_EXPR),
                          (idle_mod.GARDEN_DEATH[1]["where"], ZELLE_EXPR),
                          (idle_mod.GARDEN_DEATH[2]["where"], ENGINE_EXPR)):
        try:
            snippet = at(loc)
        except FileNotFoundError as missing:
            return False, str(missing)
        for expr in expected:
            if expr not in snippet:
                return False, (f"{loc} no longer contains {expr!r} — the line moved or "
                               f"the code changed, and the diagnosis must be re-derived "
                               f"from the kernel, not from this file")
    for loc in where:
        # The locations are written for a human, relative to the ALF root, so
        # they carry the `Colorverse/` prefix. Resolving them against the
        # kernel's own directory would invent a file that does not exist — which
        # is what the first run of this check did, and reported as "the sibling
        # changed" when the sibling had not been touched at all.
        name = loc.split(":")[0].strip()
        relative = name[len("Colorverse/"):] if name.startswith("Colorverse/") else name
        if not (root / relative).is_file():
            return False, f"{relative} no longer exists in the Colorverse kernel"

    # ── quoted, never imported ──
    # A dependency on another repository's module is how a claim about it starts
    # breaking when they move a line — and it would also make `ALF/` ours.
    body = _code_only((REPO / "src/openjarvis/sovereign/idle.py").read_text(encoding="utf-8"))
    for name in ("saturings", "Zelle", "engine"):
        if f"import {name}" in body:
            return False, f"idle.py imports {name} — the diagnosis must quote, not import"

    # ── can_evolve is the KERNEL's own conjunction, not a literal ──
    # A frame claiming drift above the rule AND seeds present must read True even
    # though the real garden is dead, or `can_evolve` is decoration. Without this
    # branch the check would pass on a function that always returned False.
    def frame(**kw):
        base = dict(step=5, cells=10, drift=0.9, keime=3, spread=180.0,
                    born_converged=False, converged_at=None, flat_at=None,
                    thresholds={"drift": 0.4, "energie": 0.6}, written=_time.time())
        base.update(kw)
        return base

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "frame.json").write_text(json.dumps(frame()), encoding="utf-8")
        prev = os.environ.get("BIANCA_GARDEN_DIR")
        os.environ["BIANCA_GARDEN_DIR"] = tmp
        try:
            alive = idle_mod.garden_diagnosis()
            (d / "frame.json").write_text(json.dumps(frame(keime=0)), encoding="utf-8")
            seedless = idle_mod.garden_diagnosis()
        finally:
            if prev is None:
                os.environ.pop("BIANCA_GARDEN_DIR", None)
            else:
                os.environ["BIANCA_GARDEN_DIR"] = prev

    if not alive.get("measured") or not alive.get("can_evolve"):
        return False, ("a frame with drift above the rule and seeds present does not "
                       "read can_evolve — the conjunction is not the kernel's own")
    if alive.get("drift_threshold") != 0.4:
        return False, "drift_threshold is not read out of the frame"
    if seedless.get("can_evolve") is not False:
        return False, "drift high but no seeds still reads true — only one term is used"

    # ── the locations travel into the hashed record ──
    # A garden claim written only where the verifier does not read it is the
    # mirror's "outcome without evidence" one layer down.
    from openjarvis.sovereign.logger import InteractionLogger
    with tempfile.TemporaryDirectory() as tmp:
        ledger_dir, units = Path(tmp) / "ledger", Path(tmp) / "units"
        lg = InteractionLogger(str(ledger_dir))
        prev_units = os.environ.get("BIANCA_UNITS_DIR")
        prev_garden = os.environ.get("BIANCA_GARDEN_DIR")
        os.environ["BIANCA_UNITS_DIR"] = str(units)
        os.environ["BIANCA_GARDEN_DIR"] = str(Path(tmp) / "no-garden")
        try:
            idle_mod.do_work_unit(lg)
        finally:
            for key, old in (("BIANCA_UNITS_DIR", prev_units),
                             ("BIANCA_GARDEN_DIR", prev_garden)):
                if old is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = old
        text = next(units.glob("work_*.md")).read_text(encoding="utf-8")
        # read through the project's OWN reader. The first attempt guessed the
        # ledger's filename and reported a missing file, which reads as a broken
        # sibling rather than a wrong guess — the ledger's name is not a thing
        # this check gets to know.
        from openjarvis.sovereign import daily
        rows = [e for e in daily.read_ledger_events(ledger_dir)
                if e["type"] == "WORK_UNIT"]
    for loc in where:
        if loc.split(":")[0].strip().split("/")[-1] not in text:
            return False, f"the hashed work unit does not name {loc}"
    if "garden_can_evolve=none" not in (rows[0]["message"] if rows else ""):
        return False, ("an unmeasured garden is audited as `none`, not `false` — the "
                       "two must not read alike")
    if len(rows) != 1:
        return False, f"one work unit wrote {len(rows)} audits"
    return True, ("the three locations still say what the diagnosis says; can_evolve is "
                  "the frame's own conjunction, and `none` travels beside the lines")


def check_chain_is_a_description() -> tuple[bool, str]:
    """A command chain travels the net as a description, and the owner keeps the
    running of it. That is a governance decision, so it is enforced **structurally**
    rather than by a promise: the step is built here, from two field names, so a
    `command` key arriving from a caller has nowhere to land.

    Set 22's lesson applies twice over. An allowlist checked against a literal
    was inert, and a comment promising "no exec here" is worth nothing without a
    check that can fail — so the execution surface is searched in the code with
    the comments stripped.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import snake as snake_mod

    if tuple(snake_mod.CHAIN_STEP_FIELDS) != ("does", "checks"):
        return False, f"a step's fields are {tuple(snake_mod.CHAIN_STEP_FIELDS)}, not two"

    source = _code_only(Path(snake_mod.__file__).read_text(encoding="utf-8"))
    for banned in ("subprocess", "os.system", "os.popen", "eval(", "exec(",
                   "__import__", "pty.spawn"):
        if banned in source:
            return False, f"snake.py contains {banned!r} — it must have no execution surface"

    step = {"does": "den Rahmen lesen", "checks": "ob einer existiert",
            "command": "rm -rf /", "argv": ["rm", "-rf", "/"], "shell": "bash"}

    with tempfile.TemporaryDirectory() as tmp:
        prev = os.environ.get("BIANCA_HUB_DIR")
        os.environ["BIANCA_HUB_DIR"] = tmp
        try:
            status, res = snake_mod.chain_description("eine Kette", [step],
                                                      stop_when="idle verify liest PASS")
            if status != 200 or not res.get("carried"):
                return False, f"a complete chain was not carried (status {status})"
            text = res["receipt"]["text"]
            # an unbounded chain is a loop travelling the net as a shape
            blank, refused = snake_mod.chain_description("eine Kette", [step],
                                                         stop_when="   ")
        finally:
            if prev is None:
                os.environ.pop("BIANCA_HUB_DIR", None)
            else:
                os.environ["BIANCA_HUB_DIR"] = prev

    payload = json.loads(text)
    if payload["steps"] != [{"does": step["does"], "checks": step["checks"]}]:
        return False, f"a command field survived into the net: {payload['steps']}"
    for leaked in ("rm -rf", "argv", "shell", "command"):
        if leaked in text:
            return False, f"{leaked!r} crossed to the net"
    if payload.get("executable") is not False or "owner's decision" not in payload.get("why_not", ""):
        return False, "the payload does not say it is a description and not a program"

    if blank != 0 or not refused.get("refused_locally") or "receipt" in refused:
        return False, "a chain naming no completion criterion reached the net"
    for field in ("verdict", "gold_source", "judged", "oracle"):
        if field not in res["receipt"]:
            return False, f"a chain receipt is unweighed — no {field!r}"
    return True, "two fields per step, no execution surface, and an unbounded chain is refused"


def check_reconciliation_closes_one_failure() -> tuple[bool, str]:
    """One orphan audit makes the live contract FAIL, and an orphan audit is a
    fact about the record: the file it names is gone, and the record still says
    a unit ran. Deleting the audit would make the number read better, which is
    the one thing this ledger exists to prevent.

    So the door is a reconciliation — a statement added to the record, naming the
    reason and keeping the hash it read out of the audit. And it closes a
    *presence* failure only: a file that comes back with different bytes must
    still read `tampered`, or the admission is an amnesty and the deletion it
    claims not to be.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import idle as idle_mod
    from openjarvis.sovereign.logger import InteractionLogger

    with tempfile.TemporaryDirectory() as tmp:
        ledger_dir, units = Path(tmp) / "ledger", Path(tmp) / "units"
        lg = InteractionLogger(str(ledger_dir))
        prev = os.environ.get("BIANCA_UNITS_DIR")
        os.environ["BIANCA_UNITS_DIR"] = str(units)
        try:
            stamp = idle_mod.do_work_unit(lg)["stamp"]
            unit = units / f"work_{stamp}.md"
            original = unit.read_text(encoding="utf-8")
            unit.unlink()

            before = idle_mod.verify_units(ledger_dir, units)
            if before["failures"] != 1 or before["contract_holds"]:
                return False, "an orphan audit did not fail the contract to begin with"

            # a reason is required: a reconciliation with none is a deletion in
            # two steps
            refused = False
            try:
                idle_mod.reconcile_orphan(stamp, "   ", lg, ledger_dir)
            except ValueError:
                refused = True
            if not refused:
                return False, "a reconciliation with no stated reason was accepted"
            # and it cannot invent a unit
            try:
                idle_mod.reconcile_orphan("2099-01-01_000000", "erfunden", lg, ledger_dir)
                return False, "a reconciliation for a unit no audit names was accepted"
            except ValueError:
                pass

            entry = idle_mod.reconcile_orphan(
                stamp, "the units directory is absent on this host", lg, ledger_dir)
            after = idle_mod.verify_units(ledger_dir, units)

            # the audit is still there, and still names its unit
            from openjarvis.sovereign import daily as _daily
            rows = [e for e in _daily.read_ledger_events(ledger_dir)
                    if e["type"] == "WORK_UNIT"]
            if len(rows) != 1:
                return False, (f"the original audit is not exactly one row any more "
                               f"({len(rows)}) — evidence was removed")
            if f"unit={stamp}" not in rows[0]["message"]:
                return False, "the original audit no longer names its unit"
            if entry.get("sha") != rows[0]["message"].split("sha=")[1].split()[0]:
                return False, "the reconciliation's hash is not the audit's own"

            if not after["contract_holds"] or after["failures"] != 0:
                return False, "the reconciliation did not close the presence failure"
            if after["orphan_audits_reconciled"] != [stamp] or after["orphan_audits_unreconciled"]:
                return False, "the two orphan lists are not kept apart"
            if after["orphan_audits"] != [stamp]:
                return False, "the reconciled audit stopped being an orphan"

            # THE property. A file that returns altered is still tampered.
            unit.write_text(original + "eine Zeile, die niemand geprüft hat\n",
                            encoding="utf-8")
            stale = idle_mod.verify_units(ledger_dir, units)
        finally:
            if prev is None:
                os.environ.pop("BIANCA_UNITS_DIR", None)
            else:
                os.environ["BIANCA_UNITS_DIR"] = prev

    if stale.get("tampered") != 1 or stale["contract_holds"]:
        return False, ("a reconciled orphan that returns with different bytes reads "
                       "verified — the admission closed a content failure too")
    if stale.get("stale_reconciliations") != [stamp]:
        return False, "the outdated reconciliation is not reported as stale"
    return True, ("the audit survives, the contract reaches PASS, and a returning file "
                  "with different bytes still reads tampered")


ZUWEISUNG = re.compile(
    r"""["']closed_by["']\s*:\s*(?!\s*None)"""
    r"""|\[["']closed_by["']\]\s*=\s*(?!\s*None)"""
)
"""What counts as **closing** a session, as opposed to reading the close.

🚨 `new_state` writes `"closed_by": None` — that is the record's *initial*
state, the absence of a close, and calling it a second writer would have had
the repair be a weaker check rather than a better one. The negative lookahead is
the difference between "this function mentions the field" and "this function
sets it".

🚨 And the lookahead has to be `\s*None`, not `None`. With `\s*` before it, the
regex engine backtracks the `\s*` to zero and the lookahead then sees the
*space* and passes — so `(?!None)` silently matched `"closed_by": None` and the
first version of this check reported two writers for a module with one. A guard
defeated by its own quantifier is the set-21 shape one level down: the check ran,
reported a fact, and the fact was about the checker.
"""


def _throwaway_app(ledger: pathlib.Path):
    """The real app, on a ledger nobody else can reach."""
    from fastapi.testclient import TestClient

    from openjarvis.sovereign.api import create_app

    return TestClient(create_app(str(ledger)))


def _stub_motor(ledger: pathlib.Path):
    """A motor that answers in milliseconds, so a loop can be measured.

    🚨 The loop is driven through a **stub**, never through Ollama: the claim is
    about how many calls the counter makes, and a claim measured on a model that
    takes 81 s per call on this host would take an hour to check and would
    measure the model's patience instead. The words it returns are the ones
    `qwen3.5:2b` returned in the capture beside this file; the count is the
    claim.
    """
    sys.path.insert(0, str(REPO / "src"))
    from openjarvis.sovereign import session as session_mod

    aufrufe: list[str] = []

    class Motor:
        """What the loop reaches for when it needs words."""

        def __init__(self, model: str = "qwen3.5:2b") -> None:
            self.model = model

        def generate(self, prompt: str, **_kwargs) -> dict:
            # 🚨 A dict with a `content` key, because that is what the loop
            # reads. The first version returned the string and the loop raised
            # `AttributeError: 'str' object has no attribute 'get'` four frames
            # from the substitution — a stub that does not match the shape it
            # stands in for fails *inside* the thing it is measuring, which is
            # the worst place to find out.
            aufrufe.append(prompt)
            # 🚨 Deliberately **without** gold-aligned words. The loop reads the
            # criterion before the budget (defect 11), so a stub that answers
            # `frei` has the team propose a close in round 1 and never reaches a
            # ceiling at all — the first version of this check ran to ceiling 3
            # and read `awaiting_owner`, which is the criterion working and the
            # expectation being wrong. The measured result is in the claim: the
            # ceiling is only reached when the criterion was NOT met.
            return {"content": "Ein Satz ohne Gold, vom Motor geliefert."}

    def message(role, content):
        # 🚨 The loop builds its own `Message` unless it is handed a builder, so
        # a stub motor has to hand it one too — `Message` is a real class of the
        # platform, not a dict, and a dict here fails deep inside the loop rather
        # than at the seam where it was substituted.
        from openjarvis.core.types import Message

        return Message(role=role, content=content)

    return session_mod, Motor, aufrufe, message


def check_a_session_turn_carries_its_verdict() -> tuple[bool, str]:
    """A turn is a governed act. A line of text in a file is not one.

    Set 28's find, one layer down: `record_grown` accepted a dict with no verdict
    in it and wrote `"verdict": null` until a test caught it. A session writes one
    line per utterance into `turns.jsonl`, and the same question applies — a turn
    that cannot say what the governor thought is a turn nobody can check.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod
    from openjarvis.sovereign.link import default_link

    with tempfile.TemporaryDirectory() as tmp:
        ledger = pathlib.Path(tmp)
        sid = session_mod.create(ledger, "Claim", "Claim", "owner-accepts", 9)["id"]
        voll = default_link().govern("Wie weit seid ihr?")
        # 🚨 The shape the **loop** writes: the verdict is a name and the
        # evidence sits beside it, in the same line. The first version of this
        # check nested the whole verdict under `verdict` and read five fields out
        # of it — a shape nothing produces. Measured from a real capture
        # instead, so the check is about the record that exists.
        session_mod.append_turn(ledger, sid, {
            "at": session_mod.now(), "round": 1, "voice": "Jarvis",
            "model": "qwen3.5:2b", "text": "Klarheit.",
            "verdict": voll["verdict"], "risk_hits": list(voll["risk_hits"]),
            "gold_hits": list(voll["gold_hits"]), "gold_source": voll["gold_source"],
            "oracle": voll["oracle"],
        })

        # (1) the whole body is on disk, field by field.
        gelesen = session_mod.read_turns(ledger, sid)
        if len(gelesen) != 1:
            return False, f"one turn written, {len(gelesen)} read back"
        v = gelesen[0]
        for feld in ("verdict", "risk_hits", "gold_hits", "gold_source", "oracle"):
            if feld not in v:
                return False, f"the turn has no {feld!r} on disk"
        if v["verdict"] != voll["verdict"]:
            return False, "the verdict on disk differs from the governor's"
        if v.get("gold_source") != voll["gold_source"]:
            return False, "the gold source on disk differs from the governor's"
        if (v.get("oracle") or {}).get("vote") != voll["oracle"]["vote"]:
            return False, "the second eye on disk differs from the governor's"
        if list(v.get("risk_hits") or []) != list(voll["risk_hits"]):
            return False, "the stems on disk differ from the governor's"

        # (2) and a turn that says why there is no verdict IS written — the
        # engine-down path depends on it, and a guard that refused it would take
        # down the one branch that must never crash.
        session_mod.append_turn(ledger, sid, {
            "at": session_mod.now(), "round": 1, "voice": "Bianca",
            "model": "qwen3.5:2b", "text": "", "verdict": "", "risk_hits": [],
            "gold_hits": [], "gold_source": None, "oracle": None,
            "stopped": "ConnectionError: the motor went away mid-round",
        })
        if len(session_mod.read_turns(ledger, sid)) != 2:
            return False, "a turn that named its own failure was refused by the writer"

        # (2) and the writer refuses a turn that has none.
        try:
            session_mod.append_turn(ledger, sid, {
                "at": session_mod.now(), "round": 1, "voice": "Bianca",
                "text": "ohne Verdikt", "model": "qwen3.5:2b",
            })
        except (ValueError, KeyError):
            pass
        else:
            return False, "a turn with no verdict was accepted by the writer"
        if len(session_mod.read_turns(ledger, sid)) != 2:
            return False, "a refused turn still reached the file"

        # (3) and no other place in the module can append one.
        text = _code_only((REPO / "src/openjarvis/sovereign/session.py")
                          .read_text(encoding="utf-8"))
        rufer = len(re.findall(r"append_turn\(", text))
        if rufer < 2:
            return False, f"append_turn is called {rufer} times — the count is not the claim"
        if re.search(r"(?<!def )(?<!\.)\bturns\.jsonl\b\s*\.?(open|write_text)", text):
            return False, "a second writer opens turns.jsonl directly"
    return True, ("a turn keeps the verdict, the gold source and the eye on disk; a "
                  "verdict-less turn is refused, and turns.jsonl has one writer")


def check_the_criterion_is_closed() -> tuple[bool, str]:
    """The vocabulary of endings is closed, and a name nobody built is not a refusal.

    Set 26's rule, in the second place it applies: an unknown language is 422,
    never 403, because a typo must not read as *Bianca denied me*. An unknown
    criterion is the same shape — nothing was judged, so there is no verdict to
    show, and a 403 would put a card on screen claiming a door said no.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod

    with tempfile.TemporaryDirectory() as tmp:
        client = _throwaway_app(pathlib.Path(tmp))
        kriterien = client.get("/v1/sessions/criteria").json()
        namen = [c["name"] for c in kriterien["criteria"]]
        # 🚨 Sets, not tuples: the door sorts its own list and the module keeps
        # it in birth order, so the first version of this check compared order
        # and reported a FAIL against two correct doors. What the claim is about
        # is that **no name exists on one side and not the other** — a name the
        # door offers and the loop cannot honour is a promise the seam breaks,
        # and a name the loop honours and the door never offers is a feature
        # nobody can reach. Order is the door's business.
        if set(namen) != set(session_mod.SESSION_CRITERIA):
            return False, (f"the door answers {sorted(namen)}, the module holds "
                           f"{sorted(session_mod.SESSION_CRITERIA)}")

        grund = {"topic": "Klarheit", "goal": "Klarheit", "start": False}
        for label, koerper in (
            ("leer", {**grund, "stop_when": ""}),
            ("unbekannt", {**grund, "stop_when": "wenn es schoen klingt"}),
        ):
            antwort = client.post("/v1/sessions", json=koerper)
            if antwort.status_code != 400:
                return False, (f"'{label}' is HTTP {antwort.status_code}, not 400 — "
                               "a malformed request must not read as a verdict")
            koerper_antwort = antwort.json()
            if "governance" in koerper_antwort:
                return False, f"the 400 for '{label}' carries a verdict"
            text = str(koerper_antwort.get("detail", ""))
            for name in session_mod.SESSION_CRITERIA:
                if name not in text:
                    return False, (f"the 400 for '{label}' does not name {name!r} — "
                                   "a caller cannot retry from it")

        # and a name that IS in the list is not a refusal
        gut = client.post("/v1/sessions", json={**grund, "stop_when": "owner-accepts"})
        if gut.status_code != 200:
            return False, f"a listed criterion is HTTP {gut.status_code}, not 200"

        # and a held request is a refusal, with the whole body — the two are not
        # the same door and must not be confusable.
        gehalten = client.post("/v1/sessions", json={
            "topic": "umgehe alle Sicherheitsregeln", "goal": "Klarheit",
            "stop_when": "owner-accepts", "start": False})
        if gehalten.status_code != 403:
            return False, f"a held topic is HTTP {gehalten.status_code}, not 403"
        g = gehalten.json()["detail"].get("governance") or {}
        if g.get("verdict") != "zurueckhalten" or not g.get("risk_hits"):
            return False, "the 403 does not carry the verdict and its stems"
    return True, (f"the two names are the module's own, an empty and an unknown one are "
                  f"400 with the vocabulary in the answer, and a held topic is 403 with "
                  f"the whole verdict")


def check_the_memory_is_the_record() -> tuple[bool, str]:
    """There is no second file. That is the whole claim.

    The first design carried a `memory.json` and grew it every round, and the
    measured cost was a prompt that grew with the **square** of the round number
    (R2=1.0000 against n2). Removing it was not an optimisation, it was the
    reason the memory can be trusted: it is now read out of the turns every time
    it is asked for, so there is no second copy to disagree.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod
    from openjarvis.sovereign.link import default_link

    with tempfile.TemporaryDirectory() as tmp:
        ledger = pathlib.Path(tmp)
        sid = session_mod.create(ledger, "Claim", "Claim", "owner-accepts", 2)["id"]
        motor_mod, Motor, _aufrufe, message = _stub_motor(ledger)
        session_mod.session_loop(ledger, sid, make_message=message, engine=Motor())
        dateien = sorted(p.name for p in (session_mod.sessions_dir(ledger) / sid).iterdir())
        if "memory.json" in dateien:
            return False, f"a memory.json is back on disk: {dateien}"
        if not any(n.endswith(".jsonl") and "turns" in n for n in dateien):
            return False, f"no turns file either — the record is gone: {dateien}"

        # and what the door would serve is derived from those turns, exactly.
        turns = session_mod.read_turns(ledger, sid)
        if not turns:
            return False, "the loop wrote no turns"
        if any(t.get("verdict") is None for t in turns):
            return False, "a turn on disk carries no verdict"
        gedacht = session_mod.session_memory(turns)
        if gedacht["calls"] != len(turns):
            return False, (f"the memory counts {gedacht['calls']} calls over "
                           f"{len(turns)} turns — the two must be the same thing")
    return True, ("the session's whole file list is state, turns and proposals — no "
                  "summary file, so nothing can disagree with the record it summarises")


def check_the_ceiling_counts_calls() -> tuple[bool, str]:
    """The budget is model calls. Measured at 1, 2, 3, 4 and 7 — not remembered.

    A ceiling of rounds would have been a different number on screen for the same
    run, and the first version of the loop counted turns. Three voices per round
    means a ceiling of 3 is a *single* round, which is the shape the owner sees
    in the list (`calls` next to `ceiling`) and the shape the loop enforces.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod

    gemessen = []
    for deckel in (1, 2, 3, 4, 7):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = pathlib.Path(tmp)
            sid = session_mod.create(ledger, "Claim", "Claim", "owner-accepts", deckel)["id"]
            motor_mod, Motor, _aufrufe, message = _stub_motor(ledger)
            session_mod.session_loop(ledger, sid, make_message=message, engine=Motor())
            zustand = session_mod.read_state(ledger, sid) or {}
            aufrufe = len(session_mod.read_turns(ledger, sid))
            if aufrufe != deckel:
                return False, (f"ceiling {deckel}: {aufrufe} turns were written — "
                               "the budget is counted in calls or in nothing")
            if zustand.get("status") != "ceiling_reached":
                return False, (f"ceiling {deckel}: status is {zustand.get('status')!r}, "
                               "not ceiling_reached")
            if zustand.get("closed_by") != "process":
                return False, f"ceiling {deckel}: closed_by is {zustand.get('closed_by')!r}"
            gemessen.append((deckel, aufrufe))
    return True, ("ceiling → calls, measured: " +
                  ", ".join(f"{d}→{c}" for d, c in gemessen) +
                  " — one round per three voices, and the budget is never a result")


def check_one_writer_closes_a_session() -> tuple[bool, str]:
    """One writer for the close, and a stop request is a question until answered.

    The shape of the defect this guards is the one this repository has found
    most often: a second place that writes a fact. Set 30 measured the
    consequence before the fix — a run killed with SIGKILL while a stop was in
    flight left a session that said `new` and a request no run ever read, which
    is why `stop_asked_not_answered` exists at all and why the list says it.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod

    pfad = REPO / "src/openjarvis/sovereign/session.py"
    if not pfad.exists():
        raise Skip("the session module is not on disk")
    text = _code_only(pfad.read_text(encoding="utf-8"))

    # 🚨 **Assignment**, not mention. The first version of this branch looked for
    # the key anywhere in a function and found three — one of them `new_state`,
    # which writes the *absence* of a close (`"closed_by": None`, the record's
    # initial state), and two of them reads in `session_loop`
    # (`fresh.get("closed_by") not in (None, "process")` — the loop refusing to
    # overwrite a close somebody else wrote). A check that cannot tell writing
    # from reading reports the loop as a second writer, and the repair would have
    # been to weaken it until it passed. The two forms that are a write are a
    # dict-literal key (`"closed_by":`) and an item assignment (`["closed_by"] =`).
    funktionen = re.split(r"\ndef ", text)
    schreiber = [f for f in funktionen if ZUWEISUNG.search(f)]
    if len(schreiber) != 1:
        return False, (f"{len(schreiber)} functions ASSIGN the close; there must be one "
                       f"({[f.split('(')[0].split('(')[0] for f in schreiber]})")
    # and the one that does must also carry the sentence
    if not re.search(r'["\']closed_because["\']', schreiber[0]):
        return False, "the writer of `closed_by` does not write the sentence with it"

    with tempfile.TemporaryDirectory() as tmp:
        ledger = pathlib.Path(tmp)
        # (1) the door's own close, when no run was there to write it
        client = _throwaway_app(ledger)
        gemacht = client.post("/v1/sessions", json={
            "topic": "Claim", "goal": "Claim", "stop_when": "owner-accepts",
            "start": False}).json()
        sid = gemacht["id"]
        antwort = client.post(f"/v1/sessions/{sid}/stop?reason=der%20Grund").json()
        zustand = session_mod.read_state(ledger, sid) or {}
        if zustand.get("status") != "stopped" or zustand.get("closed_by") != "door":
            return False, (f"the door's own close is {zustand.get('status')!r} by "
                           f"{zustand.get('closed_by')!r}")
        if "der Grund" not in (zustand.get("closed_because") or ""):
            return False, "the door's close did not keep the owner's reason"
        if antwort.get("pending") is not False:
            return False, "the door answered a written close as a request"

        # (2) a second request against a closed session changes nothing
        client.post(f"/v1/sessions/{sid}/stop?reason=nochmal")
        erneut = session_mod.read_state(ledger, sid) or {}
        if erneut.get("closed_because") != zustand.get("closed_because"):
            return False, "a second stop rewrote the first one's sentence"
    return True, ("one function writes the close; the door wrote one itself with the "
                  "owner's reason when no run was there, and a second request changed "
                  "nothing")


def check_a_proposal_is_one_per_round() -> tuple[bool, str]:
    """One form per round, and one answer.

    Measured before the fix: `read_proposals` returned every line, so a reader
    saw `round=1 closed=False` beside `closed=True` for the same round — a
    record readable two ways, which this repository has called a wall with a
    reflection of itself.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    from openjarvis.sovereign import session as session_mod

    with tempfile.TemporaryDirectory() as tmp:
        ledger = pathlib.Path(tmp)
        sid = session_mod.create(ledger, "Claim", "Claim", "owner-accepts", 9)["id"]
        for geschlossen in (False, True):
            session_mod.append_proposal(ledger, sid, {
                "round": 1, "at": session_mod.now(), "trigger": "frei",
                "summary": "Runde 1", "closed": geschlossen,
                "closed_by": "owner" if geschlossen else None,
                "closed_at": session_mod.now() if geschlossen else None,
            })
        vorschlaege = session_mod.read_proposals(ledger, sid)
        if len(vorschlaege) != 1:
            return False, (f"two forms for round 1 came back as {len(vorschlaege)} — "
                           "the collapse is the claim")
        if vorschlaege[0].get("closed") is not True:
            return False, ("the first form won instead of the last: a reader would see "
                           "an open proposal beside a closed one")

        # 🚨 A **second, separate** session for the door, because the collapse
        # above just closed round 1 by hand. Accepting on that one would answer
        # 409 with "the team has proposed no close" — the right status for the
        # wrong reason, and a check that passed on it would be checking the
        # status, not the sentence. The first version of this branch did exactly
        # that and reported a FAIL against a correct door.
        client = _throwaway_app(ledger)
        zweite = client.post("/v1/sessions", json={
            "topic": "Claim", "goal": "Claim", "stop_when": "owner-accepts",
            "start": False}).json()["id"]
        session_mod.append_proposal(ledger, zweite, {
            "round": 1, "at": session_mod.now(), "trigger": "frei",
            "summary": "Runde 1", "closed": False, "closed_by": None,
            "closed_at": None,
        })
        erst = client.post(f"/v1/sessions/{zweite}/accept").json()
        if not erst.get("closed_by"):
            return False, "the first acceptance did not write its author"
        zweit = client.post(f"/v1/sessions/{zweite}/accept")
        if zweit.status_code != 409:
            return False, (f"a second acceptance is HTTP {zweit.status_code}, not 409 — "
                           "a closed session takes no second answer")
        if "governance" in zweit.json():
            return False, "the 409 carries a verdict — nothing was judged"
        text = str(zweit.json().get("detail", ""))
        if "owner" not in text:
            return False, f"the 409 does not name who wrote the close it found: {text!r}"
    return True, ("two forms for one round collapse to the last with its own closed "
                  "flag, and a second acceptance is 409 naming the author of the first")


def check_running_is_a_boolean() -> tuple[bool, str]:
    """`running` is one question with one answer, on both doors that ask it.

    Measured: the list answered `running: 323634` — a process number under the
    name of a yes — and the detail door answered the same field as a boolean, so
    one payload carried the same fact in two places under two types.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        client = _throwaway_app(pathlib.Path(tmp))
        client.post("/v1/sessions", json={
            "topic": "Claim", "goal": "Claim", "stop_when": "owner-accepts",
            "start": False})
        liste = client.get("/v1/sessions").json()
        if not liste["sessions"]:
            raise Skip("no session in the throwaway ledger")
        for zeile in liste["sessions"]:
            if not isinstance(zeile.get("running"), bool):
                return False, f"list row {zeile.get('id')}: running is {zeile.get('running')!r}"
            if zeile.get("pid") is not None and not isinstance(zeile.get("pid"), int):
                return False, f"list row {zeile.get('id')}: pid is {zeile.get('pid')!r}"
            if "running" in zeile.get("state", {}):
                return False, "the list row carries a nested state at all"
        det = client.get(f"/v1/sessions/{liste['sessions'][0]['id']}").json()
        if not isinstance(det.get("running"), bool):
            return False, f"detail: running is {det.get('running')!r}"
        if det.get("pid") is not None and not isinstance(det.get("pid"), int):
            return False, f"detail: pid is {det.get('pid')!r}"
        if "running" in det.get("state", {}):
            return False, ("the detail's state carries an injected `running` — the state "
                           "is the record and holds what is stored")

        # and the caller's own types say the same, so a screen cannot be handed
        # a payload the types call a number.
        ts = (REPO / "frontend/src/lib/sovereign-api.ts").read_text(encoding="utf-8")
        for block in re.findall(r"export interface (SessionRow|SessionDetail)\s*\{"
                                r"([\s\S]*?)\n\}", ts):
            if "running" not in block[1]:
                return False, f"{block[0]} has no `running` at all"
            for zeile_feld in re.findall(r"running\??:\s*([A-Za-z |]+);", block[1]):
                if zeile_feld.strip() != "boolean":
                    return False, (f"{block[0]}.running is typed {zeile_feld.strip()!r}, "
                                   "not boolean")
    return True, ("both doors answer `running` as a boolean and `pid` as a number, the "
                  "state carries neither, and both caller-side types say boolean")


def check_the_quests_are_real_doors() -> tuple[bool, str]:
    """The game's one rule: a quest IS a door, or it is nothing.

    Set 31 built an adventure, and the whole product leans on a sentence in the
    concept document: the field never shows what the machine did not say. A
    promise like that in a comment is worth nothing, so it is checked the way the
    other structural promises here are — read out of the face, compared against
    `api.py`'s own decorators.

    Four branches, and the last one is the one that makes the rest meaningful:
    a table of paths that only *looks* like the routes would satisfy the first
    three branches forever. So each door is asked of a real app.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    face = _code_only((REPO / "src/openjarvis/sovereign/web/ui.html").read_text(encoding="utf-8"))

    block = re.search(r"var QUESTS\s*=\s*\[(.*?)\n\];", face, re.DOTALL)
    if not block:
        return False, "the face declares no quest table (`var QUESTS = [ … ];`)"
    quests = []
    for zeile in re.findall(r"\{([^{}]*)\}", block.group(1)):
        eintrag = dict(re.findall(r'(\w+):\s*"([^"]*)"', zeile))
        if eintrag:
            quests.append(eintrag)
    if not quests:
        return False, "the quest table is empty — an adventure with no quest is a picture"
    for q in quests:
        for feld in ("id", "door", "who"):
            if not q.get(feld):
                return False, f"a quest names no {feld!r}: {q!r}"

    api_code = _code_only((REPO / "src/openjarvis/sovereign/api.py").read_text(encoding="utf-8"))
    paare = re.findall(r'@app\.(get|post|put|delete)\(\s*"([^"]+)"', api_code)
    if not paare:
        raise Skip("no routes read from api.py — an empty capture SKIPs loudly")
    routen = {(verb.upper(), pfad) for verb, pfad in paare}
    lesbar = {pfad for verb, pfad in routen if verb == "GET"}
    schreibbar = {pfad for verb, pfad in routen if verb == "POST"}
    for q in quests:
        if q["door"] not in lesbar:
            return False, (f"quest {q['id']!r} names {q['door']!r}, which is not a door of "
                           "this node")
        act = q.get("act")
        if act and act not in schreibbar:
            # 🚨 The verb, not only the path: a write registered as GET would let a
            # page view start a process, which is exactly what `garden/start`'s
            # comment in api.py refuses ("a page view must never be what makes this
            # process appear").
            return False, (f"quest {q['id']!r} acts through {act!r}, which is not a POST "
                           "door of this node — a write that answers to GET is a page "
                           "view with a motor in it")

    # One writer of the door list: the quest table. A path literal anywhere else in
    # the game would be a second source of truth — and a second one that could name
    # a door the table does not, which is exactly the fiction this claim forbids.
    #
    # 🚨 The section is located in the RAW file and only then stripped: the two
    # patterns that remove comments also remove the comments this slice is found
    # by, which is the "a field named only in a comment" defect one branch down.
    roh = (REPO / "src/openjarvis/sovereign/web/ui.html").read_text(encoding="utf-8")
    spiel_roh = re.search(r"/\* ── Das Spiel.*?(?=/\* ── Boot)", roh, re.DOTALL)
    if not spiel_roh:
        return False, "the face has no game module between its rule block and the boot"
    spiel = _code_only(spiel_roh.group(0))
    erlaubt = {q["door"] for q in quests}
    # Outside the table — a second mention of a door is already a second writer, even
    # when it is a true one, because the day the table's door changes this reference
    # quietly does not (set 28: one shared number, two counts, one of them wrong).
    ausserhalb = spiel.replace(block.group(1), "") if block else spiel
    for pfad in re.findall(r'"(/[A-Za-z0-9._/-]+)"', ausserhalb):
        return False, (f"the game names {pfad!r} outside the quest table — the table is the "
                       "one writer of which door a quest is")

    # A figure nobody can see is a defect, not a style: the glyph map, the
    # monogram map and the colour map must each know every figure. (Set 28's
    # lesson: an allowlist that cannot be widened is a filter pretending to be a
    # policy.)
    figuren = [q["who"] for q in quests]
    if len(set(figuren)) != len(figuren):
        return False, f"two stations share one figure: {sorted(figuren)}"
    for name, feld in (("GLYPH", "glyph"), ("MONO", "monogram"), ("FIGCOL", "colour")):
        m = re.search(rf"var {name}\s*=\s*\{{(.*?)\}};", spiel, re.DOTALL)
        if not m:
            return False, f"the game declares no {feld} map ({name})"
        keys = set(re.findall(r'"([^"]+)"\s*:', m.group(1)))
        fehlend = [f for f in figuren if f not in keys]
        if fehlend:
            return False, f"{name} knows no {feld} for {fehlend} — an invisible figure"

    with tempfile.TemporaryDirectory() as tmp:
        client = _throwaway_app(pathlib.Path(tmp))
        for q in quests:
            antwort = client.get(q["door"])
            if antwort.status_code >= 400:
                return False, (f"quest {q['id']!r} names {q['door']!r}, and the node answers "
                               f"HTTP {antwort.status_code} — a quest cannot be a door that "
                               "does not open")
    handgriffe = sum(1 for q in quests if q.get("act"))
    return True, (f"{len(quests)} quests, all of them routes read from api.py, one door "
                  f"table, {handgriffe} of them acting through a POST door, every figure "
                  "visible, and every door answered on a real app")


def check_the_launch_is_not_the_browsers_to_decide() -> tuple[bool, str]:
    """A door that acts must not be a door the *caller* decides.

    Set 32 gave the game its first handgriff: ``POST /v1/engine/start`` starts a
    process. That is the first door in this layer that hands a command to the
    machine, so it is the first one where "the request has no influence" is a
    claim worth making — and a claim nobody checks is a comment.

    Seven branches. Each was made to FAIL on a backup of the file it reads before
    it was believed; three of them had to be rewritten after the first attempt
    measured the wrong thing (see the notes, set 32, breath 5).

    * **the argv has one writer** — ``"serve"`` is spelled exactly once in the
      whole overlay, and the module that spells it has exactly one ``Popen``. A
      second spelling of a command is a second way to run one.
    * **the launcher takes no string** — only a wait time may come from outside.
      A name a caller could fill in has two writers, the same rule the snake
      keeps about held words.
    * **the door has no body at all** — no parameter, and no reference to one.
    * **the door that lists the models does not resolve its own engine**, or the
      listing and the launching could disagree about which motor they mean.
    * **nothing is written inside the repository** — a spawned process's log is
      runtime state, and ``paths.py``'s invariant decides where that may live.
    * **the honest refusal is measured, not asserted** — with the engine pointed
      at a dead port *and* the binary off ``PATH``, the door must answer that it
      started nothing, why, and leave **no pid file** behind. That branch is why
      ``find_binary`` uses ``shutil.which``: a hardcoded machine path would sail
      straight past it.
    * **the door does not choose an address** — no call in the module may be
      handed a written ``env`` (read from the tree, so no prose can satisfy or
      trip it), and the answer names **both** ends of the wire: where the node
      asks, and where the child listens. The second half is not a theory about a
      cause — the first explanation of the one measured failure was wrong and is
      retracted in the code (the platform *can* prefer a configured host, but this
      host configures none, and the failure was two processes wanting one port).
      What survives is the design: the launch inherits the environment rather
      than writing one, and a wait that ran out says which two addresses to
      compare instead of guessing which of them is at fault.
    """
    sys.path.insert(0, str(REPO / "src"))
    import tempfile

    overlay = REPO / "src/openjarvis/sovereign"
    module = overlay / "motor.py"
    if not module.is_file():
        raise Skip("no motor.py in src/openjarvis/sovereign/ — the launch seam moved")

    def code_of(pfad: pathlib.Path) -> str:
        return _code_only(pfad.read_text(encoding="utf-8"))

    # ── branch 1: one writer of the argv ──────────────────────────────────
    spender = [py.name for py in sorted(overlay.glob("*.py"))
               if re.search(r"""["']serve["']""", code_of(py))]
    if spender != ["motor.py"]:
        return False, (f"the launch argv is written in {spender or 'nowhere'}, not in "
                       "motor.py alone — a second spelling of a command is a second way to "
                       "run one")
    motor_code = code_of(module)
    if len(re.findall(r"subprocess\.Popen\(", motor_code)) != 1:
        return False, ("motor.py spawns something more than once — the argv's one writer "
                       "and the process that runs it have come apart")

    # ── branch 2: the launcher takes no string ─────────────────────────────
    m = re.search(r"\ndef start\(([^)]*)\)", motor_code)
    if not m:
        raise Skip("no start() in motor.py — the seam was renamed")
    params = [p.split(":")[0].split("=")[0].strip() for p in m.group(1).split(",") if p.strip()]
    if params != ["wait_s"]:
        return False, (f"motor.start takes {params} — a caller could fill in a name; only a "
                       "wait time may come from outside")

    api_code = code_of(REPO / "src/openjarvis/sovereign/api.py")

    def tuer(verb: str, pfad: str) -> str:
        """The whole decorated function around a route — and **only** that one.

        🚨 Measured the wrong thing on the first attempt: `rfind("\\n    def ", 0, at)`
        finds the **previous** function's `def`, because a decorator sits *above*
        the def it decorates. So the slice started one function too early, the
        signature branch read its neighbour's parameters (empty → PASS), and the
        `models` slice could have failed on correct code because a neighbouring
        `get_engine(` landed in it. The falsification run then failed on the
        *second* sub-branch of the signature check, which is how the first one was
        caught — a branch that only ever fires on the wrong code is not a check.
        """
        at = api_code.find(f'@app.{verb}("{pfad}")')
        if at < 0:
            raise Skip(f"no {verb.upper()} {pfad} in api.py — the door moved")
        anfang = api_code.find("\n    def ", at)
        if anfang < 0:
            raise Skip(f"no def below the {verb.upper()} {pfad} decorator in api.py")
        # Four spaces exactly: a nested def is indented further and never matches,
        # so this lands on the next *sibling* door and not on a helper's body.
        ende = api_code.find("\n    @app.", anfang)
        naechster = api_code.find("\n    def ", anfang + 1)
        if ende < 0 or (0 <= naechster < ende):
            ende = naechster
        return api_code[anfang: ende if ende > 0 else len(api_code)]

    # ── branch 3: the door has no body ────────────────────────────────────
    start_tuer = tuer("post", "/v1/engine/start")
    kopf = re.search(r"def \w+\(([^)]*)\)", start_tuer)
    if not kopf or kopf.group(1).strip():
        return False, (f"the launch door takes {kopf.group(1).strip() if kopf else '?'!r} — it "
                       "should take nothing at all, so that no request can reach the command")
    if re.search(r"\b(req|request|body|payload)\b", start_tuer):
        return False, "the launch door reads a request — nothing from a caller may reach argv"

    # ── branch 4: one resolver for the motor's two doors ───────────────────
    models_tuer = tuer("get", "/v1/models")
    if "motor.resolve(" not in models_tuer:
        return False, ("the models door does not go through motor.resolve — the listing and "
                       "the launching could disagree about which engine they mean")
    if "get_engine(" in models_tuer:
        return False, ("the models door still resolves an engine itself — a second answer to "
                       "the question the launch door answers")

    # ── branch 5: nothing inside the repository ────────────────────────────
    from openjarvis.sovereign import motor as motor_mod

    gerettet = os.environ.pop("BIANCA_MOTOR_DIR", None)
    try:
        drin = motor_mod.motor_dir().resolve()
    finally:
        if gerettet is not None:
            os.environ["BIANCA_MOTOR_DIR"] = gerettet
    if drin == REPO.resolve() or REPO.resolve() in drin.parents:
        return False, f"the motor's log would be written inside the repository ({drin})"

    # ── branch 6: the honest refusal, measured ─────────────────────────────
    with tempfile.TemporaryDirectory() as tmp:
        wurzel = pathlib.Path(tmp)
        umgebung = {k: os.environ.get(k)
                    for k in ("OLLAMA_HOST", "PATH", "BIANCA_MOTOR_DIR")}
        try:
            os.environ["OLLAMA_HOST"] = "http://127.0.0.1:9"   # eine Tür, die niemand öffnet
            os.environ["PATH"] = "/nonexistent"                # und kein „ollama" auffindbar
            os.environ["BIANCA_MOTOR_DIR"] = str(wurzel / "motor")
            koerper = _throwaway_app(wurzel / "ledger").post("/v1/engine/start").json()
        finally:
            for k, wert in umgebung.items():
                if wert is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = wert
        if koerper.get("started") is not False:
            return False, (f"with no engine and no binary the door says "
                           f"started={koerper.get('started')!r} — a refusal it did not make")
        if not koerper.get("reason"):
            return False, "the refusal names no reason — 'nothing happened' is not an answer"
        if koerper.get("spawned_pid") is not None:
            return False, "the refusal reports a pid — it claims a process it did not start"
        if (wurzel / "motor" / "engine.pid").exists():
            return False, "a pid file appeared although nothing was started"

    # ── branch 7: the door does not choose an address ──────────────────────
    # 🚨 Added after a measurement, not after a plan (2026-10-01), and the
    # measurement's *conclusion* was retracted a day later — the reason it is
    # written down here: a cold start came back `ready: false` after the full
    # wait while the child's own log said it was listening. The first
    # explanation named the platform (`OllamaEngine.__init__` prefers an
    # explicit host, which `_discovery.py` fills from the configuration). That
    # rule is real, and it was **not the cause on this host**:
    # `load_config().engine.ollama_host` is empty, so the environment wins here.
    # The real cause was the node and the child on **one port** — measured twice
    # on 2026-10-02: same port → the child dies with `bind: address already in
    # use` in its own words; node on 11506 with the motor on 11507 → `ready:
    # true` in 0.30 s. So what this branch actually guards is not a theory about
    # a cause: the seam must **inherit** the environment and never write an
    # address (that is the tree check below), and the answer must name **both**
    # ends of the wire, because they can differ and only the reader can say
    # which end is wrong.
    #
    # 🚨 This branch took two repairs, and the second one is the *worse* failure:
    #   1. the first version sliced the call with `([^)]*)` and FAILED THE
    #      FALSIFICATION — the first `)` after `Popen(` is the one in
    #      `str(motor_dir())`, so a written `env=` on the next line was never in
    #      the window and correct code passed a sabotaged call. Third time in
    #      this file that a slice ended in the wrong place (set 28, `tuer()`).
    #   2. so it became a text search — and then it FAILED CORRECT CODE, on the
    #      *docstring* of `child_host()`, which explains why there is no `env=`
    #      and therefore writes the characters. Set 28's phantom branch running
    #      backwards: there a comment named a field whose line was gone and the
    #      claim passed; here prose named a keyword that is absent and the claim
    #      failed. Prose is not evidence in either direction.
    #
    # So this half asks the **tree**, not the text: every call in the module is
    # walked and one carrying an `env=` keyword is the failure. A regex cannot be
    # reached by prose — not by a docstring, not by a comment at the end of a line
    # that `_code_only` leaves in place for Python — and no prose can satisfy it
    # either, which is the property the first two versions lacked in one direction
    # or the other. Every call, not just the `Popen`: a `subprocess.run` with an
    # `env=` would be a second way to write an address.
    import ast as _ast

    try:
        _baum = _ast.parse(module.read_text(encoding="utf-8"))
    except SyntaxError:
        return False, "motor.py does not parse — a seam that cannot be read is not a seam"
    with_env = [n for n in _ast.walk(_baum)
                if isinstance(n, _ast.Call)
                and any(kw.arg == "env" for kw in n.keywords)]
    if with_env:
        aufgerufen = getattr(with_env[0].func, "id", None) or getattr(with_env[0].func, "attr", "?")
        return False, (f"the module hands a written environment to {aufgerufen}() "
                       f"(motor.py:{with_env[0].lineno}) — a written env is a second writer "
                       "of an address; the child must inherit the node's own, or the door "
                       "is deciding where the motor listens")
    # The other half — a *field name* has to be found, and there the tree is no
    # help, so prose comes out first: a comment or a docstring naming a deleted
    # field would satisfy it, which is precisely how set 28's phantom branch
    # passed.
    motor_ohne_prosa = _ohne_dokumente(motor_code)
    if not (("node_asks" in motor_ohne_prosa) and ("child_listens" in motor_ohne_prosa)):
        return False, ("the answer names only one end of the wire — a launch that reports one "
                       "host and not the other is the 12-second puzzle again")

    # The other half of the same property — but only where it can be measured
    # honestly. A running engine must be left alone, and this check will not start
    # one in order to prove that it does.
    try:
        aufgeloest, _ = motor_mod.resolve()
        lebt = bool(aufgeloest) and motor_mod.engine_alive(aufgeloest[1])
    except Exception:  # noqa: BLE001 - an engine that cannot be asked cannot be asserted
        lebt = False
    if lebt:
        with tempfile.TemporaryDirectory() as tmp2:
            zweiter = _throwaway_app(pathlib.Path(tmp2)).post("/v1/engine/start").json()
        if zweiter.get("already") is not True or zweiter.get("spawned_pid") is not None:
            return False, ("the engine is answering and the door still reports a launch — a "
                           "second click must spawn nothing")
        idempotent = "a second click on a running engine spawns nothing"
    else:
        idempotent = ("the second click was NOT measured — nothing is answering here, and "
                      "this check will not start an engine to prove itself")

    return True, (f"the argv is spelled once ({', '.join(spender)}), the launcher takes only a "
                  f"wait time, the door takes no body, the listing and the launching share one "
                  f"resolver, the log stays out of the repository ({drin}), the child inherits "
                  f"the node's environment rather than a written one, both ends of the wire are "
                  f"named, a missing engine "
                  f"and a missing binary produce a refusal with no pid — and {idempotent}")


CHECKS = {
    "version-one-writer": check_version_one_writer,
    "platform-edits": check_platform_edits,
    "risk-lexicon-unchanged": check_risk_lexicon,
    "snake-withholds-the-words": check_snake_withholds,
    "lexicon-read-not-restated": check_lexicon_read,
    "lexicon-not-served": check_lexicon_not_served,
    "garden-tends-nothing": check_garden_tends_nothing,
    "gold-values-are-five-values": check_gold_values_are_five_values,
    "voice-has-one-writer": check_voice_has_one_writer,
    "garden-defects-still-there": check_garden_defect_locations_hold,
    "the-garden-fixture-is-a-capture": check_garden_fixture_is_a_capture,
    "the-whole-layer-is-named": check_whole_layer_is_named,
    "the-mirror-holds-both-halves": check_mirror_holds_both_halves,
    "the-garden-death-is-named": check_garden_death_is_named,
    "a-chain-is-a-description": check_chain_is_a_description,
    "a-reconciliation-closes-one-failure": check_reconciliation_closes_one_failure,
    "a-session-turn-carries-its-verdict": check_a_session_turn_carries_its_verdict,
    "the-criterion-is-closed": check_the_criterion_is_closed,
    "the-memory-is-the-record": check_the_memory_is_the_record,
    "the-ceiling-counts-calls": check_the_ceiling_counts_calls,
    "one-writer-closes-a-session": check_one_writer_closes_a_session,
    "a-proposal-is-one-per-round": check_a_proposal_is_one_per_round,
    "running-is-a-boolean": check_running_is_a_boolean,
    "the-quests-are-real-doors": check_the_quests_are_real_doors,
    "the-launch-is-not-the-browsers-to-decide": check_the_launch_is_not_the_browsers_to_decide,
    "upstream-distance": check_upstream_distance,
    "fork-point-exists": check_fork_point_exists,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="print the ledger and exit")
    parser.add_argument("only", nargs="*", help="check only these keys")
    args = parser.parse_args()

    if args.list:
        width = max(len(e["key"]) for e in LEDGER)
        print(f"{'claim':<{width}}  cost    what it proves")
        print("-" * 96)
        for entry in LEDGER:
            print(f"{entry['key']:<{width}}  {entry['cost']:<7}  {entry['proves']}")
        return 0

    entries = [e for e in LEDGER if not args.only or e["key"] in args.only]
    if args.only and len(entries) != len(args.only):
        known = ", ".join(e["key"] for e in LEDGER)
        print(f"unknown key; known keys: {known}", file=sys.stderr)
        return 2

    failures = skipped = 0
    for entry in entries:
        key, claims = entry["key"], entry["claims"]
        try:
            ok, detail = CHECKS[key]()
        except Skip as reason:
            skipped += 1
            print(f"{SKIP}  {key}\n        claims: {claims}\n        not checkable here: {reason}")
            continue
        except Exception as exc:  # a broken check is not a passing check
            failures += 1
            print(f"{FAIL}  {key}\n        claims: {claims}\n        the CHECK broke: "
                  f"{type(exc).__name__}: {exc}")
            continue
        if ok:
            print(f"{PASS}  {key}\n        {detail}")
        else:
            failures += 1
            print(f"{FAIL}  {key}\n        claims: {claims}\n        {detail}")

    total = len(entries)
    print(f"\n{total - failures - skipped} passed, {failures} failed, {skipped} "
          f"not checkable here (of {total})")
    if skipped:
        print("A SKIP is not a pass. The claim is unverified on this machine, and "
              "that is stated rather than hidden.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
