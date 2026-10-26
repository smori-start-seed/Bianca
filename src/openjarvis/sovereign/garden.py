"""garden — the node's window onto Colorverse, shown exactly as it is.

Round 4 of the owner's framing: Colorverse is not a screensaver but *"the
user's anything-goes environment — a seed that grows, a plant of the user's
choice, and the mycelium connection."* Two doors were decided before any code
was written:

* plants come from :mod:`hub`'s **spores only** — every piece already passed
  the gate, so a refusal never became a plant;
* the garden is **the one ungated surface in the product**, and that is written
  down here rather than left as an unfilled hole.

And then the measurement that shaped everything else. The kernel converges, and
it does not come back (set 24, breath 2, with the kernel's **own**
``build_world``)::

      step   harm   drift  hue-spread  keime  cluster
         1  1.000  0.0081        1.55      0       90
        25  1.000  0.0008      309.31      0       90
       100  1.000  0.0000        0.00      0       90
       900  1.000  0.0000        0.00      0       90

**SET 35 (2026-10-05) — the paragraph above is HISTORY, not the current kernel.**
Set 35 changed the kernel (three edits, each measured on the kernel this host
reads, notes `Bianca/five-levels-notes.md` sections 13-15):

* ``engine.py:70-78`` — the seed marking moved to the **head** of ``step()``,
  so the gate is checked while the neighbourhood variance still carries it. The
  window ``5400 < var <= 8640`` is only just over a step wide (measured: var
  falls by a factor of 0.21 per step), so marking seeds *after* the seven update
  passes was checking a world that had already closed.
* ``Zelle.py:89-101`` and ``Zelle.py:109-117`` — ``failsafe()`` gives a dying
  cell its **neighbours' mean hue** instead of ``0``. Black was the death marker
  *and* a colour value the neighbourhood kept computing with; mixed
  neighbourhoods reached ``var 10 488`` of a maximum 10 800.
* ``saturings.py:77-79`` — ``build_world`` computes ``berechne_drift()`` and
  ``berechne_harmonie()`` after the hex layout, so the birth state is measured
  rather than asserted.

**Measured after, on this host:**

======================  ==================  ===========================
                        before (set 34/35)   after G + H + V
======================  ==================  ===========================
new Clusters             0                   **17-18** (all at step 1)
``flat_at``              55 to 235           **does not occur**
                            (28 worlds)      (1000 steps, measured)
cells with ``hue == 0``  all                 **0**
coloured cells @400      0                   **650**
coloured cells @1000     0                   **608**
======================  ==================  ===========================

**So two sentences that this file used to publish are FALSE now:** *"the garden
has never reproduced"* and *"the garden loses its last hue after 55 to 235
steps"*. Both were true only of a kernel that could not seed. The gate was never
a wall — it was **a door that nobody opened in time**. ``flat_at`` is now
``None``, and the surfaces that print it print *this run's* value beside the
historical range, so a collapse is visible the moment it returns.

**SET 36 (2026-10-09) — the paragraph that stood here is RETRACTED, and the owner
took exactly the decision it named.** It read *"growth is one-shot … there is no
source of disorder, so sustained growth needs one — a semantic decision about the
garden's physics, not a parameter."* The decision was taken: the **Ring** door
smooths its clusters toward the ring's circular mean hue (``RING_GLAETTUNG``) and
re-lights their saturation and brightness (``RING_RELIGHT``); the **Sphere** door
paints the free field a travelling hue wave (``SPHERE_MUSTER_*``) and feeds it
energy. **The kernel now has a disorder source.** Measured on the kernel this host
reads (seeds 1/7/42, 1500 steps): **clusters 90 -> 130/131/131**, ``flat_at =
None``, ~760 cells alive and holding colour — against the set-35 one-shot of 106
clusters with the field fading. **What is still true:** growth is still
**one-shot** (the maximum arrives by ~step 50 and holds, because the new clusters
consume the free field the Sphere paints on) and every process in it is still a
**mean** — the Sphere's wave is the disorder source, not a change of nature.
Sustained growth is **not** achieved, and that is stated rather than implied.

**SET 38 (2026-10-16) — the owner took set 37's growth factor back, and the
wave's crest decides instead: there is no ``WACHSTUMSFAKTOR`` in the kernel any
more.** Set 37 had put a coin on the gate: a free cell became a seed only with
probability 0.6 while the triple gate held (``engine.py:75``). Measured on the
kernel this host reads (seeds 1/7/42, 1500 steps) it cost slightly — **clusters
90 -> 126/127/133** against 130/131/131 without it — and it replaced the cell's
own decision with a global die roll, which is what the owner called the lost
living character. **The replacement is not a number but the field's own phase:**
the Sphere already paints the free field a travelling wave
(``hue = SPHERE_MUSTER_AMP * sin(freq * i + phase)``), so a free cell now carries
a seed only when the **crest stands over it** (``z.hue < 180``, the sign half of
the painted wave, on ``engine.py:75`` — the edit is line-neutral, so the pinned
gate ``engine.py:72-76`` does not move). The crest travels, so ripeness travels.
Measured on the kernel this host reads (seeds 1/7/42, 1500 steps): **clusters
90 -> 125/126/126**, ``flat_at = None``, 822-842 cells alive, colour held, and
the burst now **carries over 22 steps to step 172** instead of 16 steps to step
23. **What is still true, and stated rather than implied:** growth is still
**one-shot and still not sustained.** The measured reason is no longer the
factor: the free field's gate closes on ``harmonie < 0.5`` (a witness inside the
gate: 219 of 221 remaining free cells carry ``drift > 0.4`` and **0** carry
``harmonie < 0.5``), and ``Cluster.mutation()``'s **edger** consumes free cells
(``abs(f.hue - edger.hue) < 20 and f.drift > 0.3`` -> ``in_cluster``; measured:
313 cells ``in_cluster`` after step 1, not the 44 of the real new clusters).
That consumption is not a pure defect — switching it off gives 157/160/158
clusters but the colour field dies (spread 95/44/99 against 229/211/180).

**SET 35, 2026-10-06 — the frame contradicts itself, and both arms are true.**
``born_converged`` says the world can never grow; ``cluster - cluster_start``
says it grew. Both are measurements. The frame therefore carries
``convergence_disputed``, ``cluster_start``, ``grew_at`` beside
``born_converged``, and **every surface prints the disagreement rather than one
arm of it** — the face (``ui.html:1495`` and ``ui.html:1558``), React
(``GardenView.tsx``), and ``idle.py``. ⚠️ **This was found by the owner looking
at a screen, three times over:** I had added the counter-arm to one block of
``ui.html`` and published that as done. Three blocks in one file and one block
in another, each reading a *correct* number — mean drift 0.0017 against a rule
needing 0.40 is exactly right, which is what made the false conclusion look
measured. **A right number makes a wrong claim harder to refute than a wrong
number would**, and that is the form worth remembering.

**And the long run, measured on the owner's own garden:** step **3858**,
``flat_at = None``, 111 clusters, ``spread`` 89 — a run four times longer than
the 1000 steps quoted above, and the furthest any world has been watched on the
post-repair kernel. That is the number a collapse would have to beat.

``converged_at=1`` and ``born_converged=True`` hold in **every** run, and the
reason is the MEAN: the frame's ``drift`` averages 1000 cells and sits near 0.02
against a threshold of 0.40. What is *not* the reason is drift — re-measured on
2026-10-04, drift crosses 0.4 in every phase. The gate that closes is
``harmonie``: a seed needs ``harmonie < 0.5`` (``engine.py:75``), the world
reaches it only in steps 1-6 (harmonie 0.2767) and never again in the following
314 steps (minimum 0.8289). Cluster formation gathers 1..11 seeds at once (molecules, ``engine.py:164-175``);
the best ever measured **on this kernel** was 2 —
see the SET 35 note above: after G + H the world builds 17-18 new Clusters at
step 1, so that figure describes the kernel *before* set 35.

``flat_at`` does **not** repeat: the child never seeds ``random``, so every world
is a different one and the step at which it loses its last hue varies — measured
55 to 235 over 28 worlds **of the kernel before set 35**. On the current
kernel it does not lose its last hue at all, within 1000 steps. An earlier draft of this docstring quoted
``flat_at=2`` as though it were a property of the kernel. It is a property of one
run — the same shape as the ``dev262`` number, and the same fix applies: publish
the range, or publish nothing.

Two further things set 34 learned about ``flat_at``, both measured rather than
assumed. It is **not** the step at which every cell dies: eight worlds agreed
that it was, then a ninth showed 575 cells still carrying brightness at that
step. ``failsafe()`` has a second arm (``Zelle.py:103-122``) that extinguishes a
cell for being *too pure, too bright and too harmonious* and leaves it at
``brightness = 1``. And what the frame can prove without exception, in all 52
worlds measured, is only that every cell carries hue 0 — so that is what both
surfaces say, and they say outright that they do not count living cells.

90 clusters form at step 1 and capture 990 of 1000 cells. By step 100 every cell
holds the same hue and stays there. That is a **fixed point, not a decay**. The
owner decided: **show it as it is, and carry the two defects as an upstream
question for ALF.** So nothing in this module perturbs a cell, seeds a value,
or "improves" the kernel. The beauty of the garden, such as it is, is the
kernel's; and the *reason* it is short-lived is on the same screen as the
colour.

**Why a child process, and why that is not a style choice.** ``engine.py``
opens with ``from config import *`` and ``from engine import Engine`` — flat
imports, so loading it means putting ``Colorverse/`` on ``sys.path`` and letting
``config``, ``engine``, ``Zelle``, ``Cluster`` … into ``sys.modules`` *of the
process that serves the guarded door*. And this repository already owns two of
those names: ``src/openjarvis/evals/core/config.py`` and
``src/openjarvis/workflow/engine.py``. So the kernel runs in its own child, and
the import happens **there**. The door only ever reads a frame file.

**Why a frame file and not a pipe.** The latest frame must survive a restart of
the door, and a pipe would make the child's death indistinguishable from
"nothing has happened yet". A file carries its own step and wall time, which is
what makes staleness *reportable* — and a stale frame that reads as a live one
is the present-but-wrong evidence this repository has now found four times.

**Why the hashes.** ``/home/sam/Repos/ALF`` is **not a git repository at all**
(``git rev-parse`` fails there), so a live kernel subprocess has no version
identity whatsoever. A recorded SHA-256 of every file the kernel imported is
the only way a reader can check *which* kernel produced a frame months later.
"""

from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ── where the kernel lives ────────────────────────────────────────────────────

#: The files the kernel actually imports. This list is the *deflection*: when
#: the kernel is missing, naming these ten is not a guess but the fix, because
#: the mechanism knows precisely what it wants. That is the difference from
#: ``ValueGovernor._missing``, which must stop at the boundary because a gate
#: cannot know intent (set 21). Same words, opposite honesty.
KERNEL_FILES: tuple[str, ...] = (
    "config.py",
    "engine.py",
    "Zelle.py",
    "Cluster.py",
    "Ring.py",
    "Sphere.py",
    "MetaSphere.py",
    "UniverseNode.py",
    "saturn_hexagon_core.py",
    "saturings.py",
)

#: Seconds between advances. The kernel costs ~39 ms per step with its own
#: ``build_world`` (measured), and ``engine.main()`` is ``while True`` — it never
#: returns — so the tick is what keeps the child bounded and the door free.
TICK_S = float(os.environ.get("BIANCA_GARDEN_TICK", "0.25"))

#: A frame older than this many ticks is reported ``stale``, never as current.
STALE_AFTER_S = max(2.0, TICK_S * 3)


def colorverse_dir() -> Path:
    """The sibling kernel. ``BIANCA_COLORVERSE_DIR`` overrides it."""
    if raw := os.environ.get("BIANCA_COLORVERSE_DIR"):
        return Path(raw)
    alf = os.environ.get("BIANCA_ALF_ROOT")
    if alf:
        return Path(alf) / "Colorverse"
    local = Path(__file__).resolve().parents[3] / "external" / "ALF" / "Colorverse"
    if local.exists():
        return local
    local2 = Path(__file__).resolve().parents[3] / "external" / "Colorverse"
    if local2.exists():
        return local2
    return Path("/home/sam/Repos/ALF") / "Colorverse"


def garden_dir() -> Path:
    """Where the frame lives. Outside the repository, like :func:`daily.units_dir`."""
    if raw := os.environ.get("BIANCA_GARDEN_DIR"):
        return Path(raw)
    return Path.home() / ".openjarvis" / "bianca" / "garden"


def frame_path() -> Path:
    return garden_dir() / "frame.json"


def pid_path() -> Path:
    return garden_dir() / "child.pid"


# ── the upstream question, carried as data ───────────────────────────────────

#: The defects found in the sibling kernel, named by location so a reader can
#: check the claim instead of taking it. Each entry names the exact lines.
#:
#: 🚨 **Set 34: this repository changed the sibling, on the owner's decision,
#: and the addresses below were moved by that change.** `ALF/Colorverse` has no
#: version control, so the before/after of both edits lives in
#: `five-levels-notes.md` (set 34, Ebene 2) and nowhere else — that was the
#: owner's decision over the alternative, `git init`. Two consequences, both
#: load-bearing:
#:
#: * an address here is a claim about lines in a file we do not control, and
#:   :38/:121/:141 were re-read from the kernel after the edit, not carried over;
#: * `the-garden-death-is-named` reads `Zelle.py` **at the line it names** and
#:   FAILed on the move. That is the check working: it would have passed on a
#:   file whose numbers had gone stale.
#:
#: One of the two original defects is therefore no longer "carried, not fixed":
#: the world is born alive now (measured 0 dead cells after `build_world`, was
#: 360). It was a hidden step, not a rule, and it is named in the notes.
UPSTREAM: tuple[dict[str, str], ...] = (
    {
        "id": "stabiliser-vs-evolution",
        "where": "Zelle.py:38, Zelle.py:130, Zelle.py:150 vs engine.py:72-76, engine.py:156-160",
        "what": (
            "Zelle.update() calls stabilisierung() unconditionally; it pulls every "
            "cell toward its neighbours' mean hue by a hardcoded alpha = 0.05, so "
            "neighbourhood hue variance decays. engine.py then requires drift > 0.4 "
            "AND harmonie < 0.5 for an evolution seed, and builds a NEW Cluster "
            "only from 11 seeds at once."
        ),
        "why_it_matters": (
            "🚨 **SET 35 (2026-10-05) — this entry's CONCLUSION is retracted; its "
            "locations and what they say are still true.** For four sets this table "
            "read *“the real blocker is one number”*, and the garden would not "
            "breed. By set 35 it bred: **17-18 new Clusters at step 1**; with the "
            "set-36 doors open it reaches **129 (90 → 129)** (below). No threshold "
            "was ever lowered to get there. `engine.py` marked its seeds at the "
            "**end** of `step()`, after seven update passes had already pulled the "
            "neighbourhood variance down by a factor of **0.21** — so the gate was "
            "tested against a world that had already closed. Moving the marking to "
            "the **head** of `step()` (`engine.py:72-76`) opens it: **a door nobody "
            "opened in time, measured as a wall.** The seed gate is also "
            "**threefold** (`drift > 0.4` **and** `energy > 0.6` **and** "
            "`harmonie < 0.5`), not twofold as this entry says.\n\n"
            "**The arithmetic below is history, not a verdict** — and it was never "
            "wrong about what it measured: 1 → 3 → 10 seeds as the harmonie gate "
            "opens 0.5 → 0.9 → 0.99, against the 11 a `Cluster` needs. What was "
            "wrong was the assumption underneath it, that the gate is tested once, "
            "early. It was tested after the variance had already decayed.\n\n"
            "**SET 36 (2026-10-09) — the paragraph that stood here is RETRACTED, "
            "and the owner took exactly the decision it named.** It read *“growth "
            "is one-shot … there is no source of disorder, so sustained growth "
            "needs one — a semantic decision about the garden’s physics, not a "
            "parameter.”* The decision was taken: the **Ring** door smooths its "
            "clusters toward the ring’s circular mean hue (`RING_GLAETTUNG`) and "
            "re-lights their saturation and brightness (`RING_RELIGHT`); the "
            "**Sphere** door paints the free field a travelling hue wave "
            "(`SPHERE_MUSTER_*`) and feeds it energy. **The kernel now has a "
            "disorder source.** Measured on the kernel this host reads (seeds "
            "1/7/42, 1500 steps): **clusters 90 → 130/131/131**, `flat_at = None`, "
            "~760 cells alive and holding colour. **What is still true:** growth is "
            "still **one-shot** (the maximum arrives by ~step 50 and holds, because "
            "the new clusters consume the free field the Sphere paints on), and "
            "every process in the kernel is still a **mean** — the Sphere’s wave is "
            "the disorder source, not a change of nature. Sustained growth is "
            "**not** achieved.\n\n"
            "**SET 38 (2026-10-16) — the owner took set 37’s growth factor back, and "
            "the crest of the wave decides instead: there is no `WACHSTUMSFAKTOR` in "
            "the kernel any more.** Set 37 had put a coin on the gate — a free cell "
            "became a seed only with probability 0.6 while the triple gate held "
            "(`engine.py:75`). Measured on the kernel this host reads (seeds 1/7/42, "
            "1500 steps) it cost slightly (**clusters 90 → 126/127/133** against "
            "130/131/131 without it) and it replaced the cell’s own decision with a "
            "global die roll — the owner’s *lost living character*. **The replacement "
            "is not a number but the field’s own phase.** The Sphere already paints "
            "the free field a travelling wave (`hue = SPHERE_MUSTER_AMP * sin(freq * "
            "i + phase)`), so a free cell now carries a seed only when the **crest "
            "stands over it** (`z.hue < 180`, the sign half of the painted wave, on "
            "`engine.py:75`; the edit is **line-neutral**, so the pinned gate "
            "`engine.py:72-76` does not move). The crest travels, so ripeness "
            "travels. Measured on the kernel this host reads (seeds 1/7/42, 1500 "
            "steps): **clusters 90 → 125/126/126**, `flat_at = None`, 822-842 cells "
            "alive and holding colour; the burst now **carries over 22 steps to step "
            "172** instead of 16 steps to step 23. **What is still true, and stated "
            "rather than implied:** growth is still **one-shot and still not "
            "sustained.** The measured reason is no longer the factor — the free "
            "field’s gate closes on `harmonie < 0.5` (a witness inside the gate: 219 "
            "of 221 remaining free cells carry `drift > 0.4` and **0** carry "
            "`harmonie < 0.5`), and `Cluster.mutation()`’s **edger** consumes free "
            "cells (`abs(f.hue - edger.hue) < 20 and f.drift > 0.3` → `in_cluster`; "
            "measured: 313 cells `in_cluster` after step 1, not the 44 of the real "
            "new clusters). That consumption is not a pure defect — switching it off "
            "gives 157/160/158 clusters but the colour field dies (spread 95/44/99 "
            "against 229/211/180).\n\n"
            "🚨 **SET 35 (2026-10-06) — and the FRAME now contradicts itself, and "
            "both arms are true.** `born_converged` says the world can never grow; "
            "`cluster - cluster_start` says it grew. Both are measurements, because "
            "they answer different questions: a seed needs **11 at once**, and a mean "
            "is not a count. The frame therefore carries `convergence_disputed`, "
            "`cluster_start` and `grew_at` beside `born_converged`, and every surface "
            "prints the disagreement rather than one arm of it. **The owner's own run "
            "reached step 3858 with `flat_at = None`** and 111 clusters — four times "
            "the 1000 steps measured the day before, and the furthest any world has "
            "been watched on the repaired kernel.\n\n"
            "⚠️ **That block was nearly absent from this file.** It had been written "
            "into the React **fixture** instead, so the live door served the retracted "
            "verdict for a whole set while every React test passed against text the "
            "node never sent. A fixture is a *capture*; the moment it is edited by "
            "hand it stops being evidence and becomes a copy — and two surfaces then "
            "disagree about one garden, which is set 21's “present but wrong "
            "evidence” one layer down. **This file is the only writer.**\n\n"
            "🚨 **Set 34 retracted this claim twice, and the real blocker is one "
            "number.** It used to say the evolution path is unreachable, citing "
            "'best drift 0.0426' — a figure taken on the pre-repair world, which "
            "was dead at birth, so it measured a corpse. Re-measured, the drift "
            "story is the WRONG DOOR: drift reaches 0.6886-0.7075 and stays "
            "there, above the seed threshold of 0.4 in every phase — and 0.7 is "
            "the death threshold (Zelle.py:86), so the maximum drift is the "
            "failing line seen from below, not a sign of health. What closes is "
            "the other gate. A seed needs harmonie < 0.5 (engine.py:75), which "
            "by Zelle.py:81 means a neighbour-hue variance above 5400 (half of "
            "HARMONIE_NULLPUNKT = 10800). In steps 1-6 the variance is there, "
            "harmonie falls to 0.2767, and seeds can form. From step 7 on, over "
            "314 steps, harmonie never goes below 0.8289 — variance 1848 "
            "against the 5400 needed, short by a factor of 2.9 — and not one "
            "seed appears. The cause is the line this entry already names: "
            "stabilisierung() is called unconditionally (Zelle.py:150) and pulls "
            "every cell onto its neighbours' mean, so neighbour variance decays "
            "to nothing. alpha is a literal in Zelle.__init__, not a config "
            "knob. Reproduction then needs 11 such seeds at once, and the best "
            "ever measured is 2. "
            "🚨 **And the wall is arithmetic, not tuning:** with the drift gate "
            "open, opening the harmonie gate from 0.5 to 0.9 raised the seed "
            "count from 1 to 3, and to 0.99 it reached 10 — still one short of "
            "the 11 a Cluster needs. The reason is that stabilisierung() drives "
            "neighbour hue variance to EXACTLY 0, so Zelle.py:81 returns "
            "harmonie = 1.0 for most cells, and every threshold below 1.0 is "
            "then unreachable at once. No value for this threshold repairs it: "
            "the quantity it reads is gone. All three defects named in this "
            "table trace back to that one call."
        ),
    },
    {
        "id": "wander-system-is-a-comment",
        "where": "engine.py:114",
        "what": (
            "the only perturbation source in the kernel is a comment: "
            "'# 8. Optional: Wander-System' / '# self.hexagon_wander()'"
        ),
        "why_it_matters": (
            "hexagon_wander appears once in the whole kernel and 0 files define it. "
            "A comment naming a function that does not exist is a claim, and it is "
            "false — the same shape as set 23's lesson about a comment describing a "
            "check."
        ),
    },
    {
        "id": "a-cell-dies-for-being-different",
        "where": "Zelle.py:81, Zelle.py:87 vs engine.py:75",
        "what": (
            "Zelle.failsafe() lists 'harmonie < 0.2' among the four conditions that "
            "kill a cell outright (hue, saturation, brightness and drift all go to "
            "0), and Zelle.berechne_harmonie() derives harmonie as "
            "1 - min(1, var / HARMONIE_NULLPUNKT) from the spread of its "
            "neighbours' hues"
        ),
        "why_it_matters": (
            "the quantity a seed needs is a difference and the quantity the kernel "
            "kills for is also a difference — so the death criterion and the growth "
            "criterion are the same sign. Measured 2026-10-02 with the kernel's own "
            "build_world: 792 of 1000 cells died in their FIRST update, at "
            "harmonie 0.0218, from starting hues drawn uniform(0, 360). Set 34's "
            "second repair made harmonie an honest 0-1 quantity — and an honest "
            "reading is zero for a newborn cell, because that is what 'your "
            "neighbours are all different colours' means. No parameter repairs "
            "this: it is the kernel's definition of death, not a scale."
        ),
    },
)


# ── the kernel's own state, readable without starting anything ──────────────


def file_hashes() -> dict[str, str]:
    """SHA-256 (first 16 hex chars) of every kernel file that exists.

    Short by design: this is a fingerprint for a reader to compare against the
    file on disk, not a trust anchor. The files are not ours and not version
    controlled, so there is nothing stronger to point at.
    """
    root = colorverse_dir()
    out: dict[str, str] = {}
    for name in KERNEL_FILES:
        candidate = root / name
        if not candidate.is_file():
            continue
        out[name] = hashlib.sha256(candidate.read_bytes()).hexdigest()[:16]
    return out


def missing_files() -> list[str]:
    root = colorverse_dir()
    return [n for n in KERNEL_FILES if not (root / n).is_file()]


def kernel_state() -> dict[str, Any]:
    """What the kernel is, whether it is there, and what is missing.

    Never raises. A missing kernel is a **deflection that names the fix**,
    because the mechanism knows exactly which files it wants — not silence,
    because silence is the hard barrier the owner rejected, and not a traceback,
    because the prettiest thing on the product must not be its most fragile one.
    """
    root = colorverse_dir()
    missing = missing_files()
    state: dict[str, Any] = {
        "path": str(root),
        "present": not missing,
        "wanted": list(KERNEL_FILES),
        "missing": missing,
        "files": file_hashes(),
        "tick_s": TICK_S,
        "upstream": list(UPSTREAM),
        "tended": False,
        "tended_note": (
            "Bianca injects nothing. The owner decided the garden is shown as it "
            "is, so no cell is perturbed, seeded or 'improved' here."
        ),
    }
    if not missing:
        state["missing_note"] = ""
        return state
    if not root.is_dir():
        state["missing_note"] = (
            f"Der Garten hat keinen Boden: {root} gibt es nicht. "
            f"Lege dort die {len(KERNEL_FILES)} Dateien ab "
            f"({', '.join(KERNEL_FILES[:4])}, …) — dann wächst er von selbst."
        )
    else:
        state["missing_note"] = (
            f"Dem Garten fehlen {len(missing)} von {len(KERNEL_FILES)} Dateien: "
            f"{', '.join(missing)}. Sie gehören nach {root}."
        )
    return state


# ── the frame: the only thing the door ever reads ────────────────────────────


def frame(max_age_s: float | None = None) -> dict[str, Any]:
    """The latest frame, with freshness judged here and nowhere else.

    ``live`` means *a child is running and the frame is young*. ``stale`` means
    the numbers are real but the world behind them has stopped moving, and the
    payload says so rather than letting an old colour pass for a living one.
    """
    age_limit = STALE_AFTER_S if max_age_s is None else max_age_s
    path = frame_path()
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {
            "present": False,
            "live": False,
            "stale": False,
            "step": 0,
            "error": "no frame yet — the garden has not been started",
        }
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        # A frame that exists but cannot be read is NOT the same fact as a frame
        # that does not exist. Reporting "no frame yet" for a corrupt file would
        # be a comfortable lie: it points the reader at the start button when the
        # real fault is on disk.
        return {
            "present": False,
            "live": False,
            "stale": False,
            "step": 0,
            "error": (
                "the frame on disk is not a frame — it was not written by the "
                f"child ({type(exc).__name__}). Delete it and start the garden again."
            ),
        }
    if not isinstance(payload, dict):
        return {
            "present": False,
            "live": False,
            "stale": False,
            "step": 0,
            "error": "the frame on disk is not a frame — it is not an object",
        }

    written = float(payload.get("written", 0.0) or 0.0)
    age = max(0.0, time.time() - written) if written else float("inf")
    fresh = age <= age_limit
    running = child_alive()
    payload["present"] = True
    payload["age_s"] = None if age == float("inf") else round(age, 2)
    payload["fresh"] = fresh
    payload["child_running"] = running
    payload["live"] = fresh and running
    payload["stale"] = not payload["live"]
    if payload["stale"]:
        payload["stale_note"] = (
            "This frame is real but it has stopped moving: no child is running, "
            "or the frame is older than "
            f"{age_limit:.1f}s. It is the last thing the kernel was, not the "
            "kernel now."
        )
    return payload


def _pid_is_live(pid: int) -> bool:
    """Is this pid a *running* process, rather than one that merely exists?

    ``os.kill(pid, 0)`` is the usual answer and it is **wrong here**: it succeeds
    for a zombie, so a child that has exited but not been reaped — which is
    exactly what a dead-but-unwaited child looks like — would be reported as
    alive, and the node would call a stopped garden ``live``. ``/proc`` carries
    the process state, so read it. Zombies (Z) and dead (X) are not running.
    """
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        # No /proc (not Linux): fall back to the weaker test and say so, because
        # a weaker liveness test that is not named is a lie the node cannot see.
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    # state is the field after the comm, and comm can contain spaces and parens
    state = stat.rpartition(")")[2].split()
    return bool(state) and state[0] not in ("Z", "X", "x")


def child_alive() -> bool:
    """Is the child process still there *and running*?"""
    try:
        pid = int(pid_path().read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    return _pid_is_live(pid)


def status() -> dict[str, Any]:
    """Everything a reader needs to check the garden, in one payload."""
    return {
        "kernel": kernel_state(),
        "frame": frame(),
        "child_running": child_alive(),
        "tick_s": TICK_S,
    }


# ── the child: the kernel, unmodified, in its own process ───────────────────

#: Runs in the child. Note what it does *not* do: it does not patch config, does
#: not write a cell's attributes, does not call anything the kernel's own
#: ``main()`` would not. ``build_world`` + ``step()`` is the kernel's own entry
#: path, and the only difference is where the stdout went.
_CHILD = r"""
import contextlib, hashlib, io, json, os, sys, time

kernel = sys.argv[1]
frame = sys.argv[2]
tick = float(sys.argv[3])
sys.path.insert(0, kernel)

def write(payload):
    payload["written"] = time.time()
    tmp = frame + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    os.replace(tmp, frame)

def hashes(root, names):
    out = {}
    for name in names:
        p = os.path.join(root, name)
        if os.path.isfile(p):
            with open(p, "rb") as fh:
                out[name] = hashlib.sha256(fh.read()).hexdigest()[:16]
    return out

# Passed in, never interpolated into this source: the child is a program, not a
# template, and a seed that had to survive %-formatting would be one step away
# from being a string that lies about what it is.
WANTED = json.loads(sys.argv[4])

try:
    # The kernel prints one line per step; capture the last ENGINE line as its
    # own unedited readout rather than letting it reach the node's console.
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        from config import DRIFT_THRESHOLD, ENERGY_THRESHOLD, WORLD_SIZE
        from engine import Engine
        from saturings import build_world
        world = Engine()
        build_world(world)
        cells = world.zellen
        n = len(cells)
        step = 0
        # Three deaths and three steps, and they are not the same fact. The
        # thresholds are read out of the kernel, never retyped here — the rule
        # the snake follows for RISK_TERMS: a number written down in this file
        # is a claim about the kernel that nothing would notice going stale.
        born_converged = None
        converged_at = None
        flat_at = None
        # 🚨 **Set 35 (2026-10-05).** The frame carried three fields that were
        # mutually contradictory and only one of them was true. `can_evolve` is
        # computed from the **mean** drift over 1000 cells, so it says "cannot
        # evolve" about a world that is, in fact, building Clusters: measured on
        # the current kernel the frame at step 262 reports `born_converged: true`,
        # `converged_at: 1`, `keime: 235` **and** `cluster: 108`. A frame that
        # says both "can never evolve" and "here are the 18 clusters it grew" is
        # not a diagnosis, it is a shrug with two arms.
        #
        # So the frame now measures **growth** in the only unit the kernel has:
        # a `Cluster` object. `born_converged` and `converged_at` are not
        # *deleted* — surfaces and tests hold them, and a field that vanishes is
        # a silent retraction — but they are **qualified** by a measured
        # contradiction, and the surfaces are told which arm to trust.
        cluster_start = None
        grew_at = None
        # 🚨 Read BEFORE the first `step()`. All of the growth happens in step 1
        # (measured: the cluster maximum is reached there and never exceeded), so
        # a baseline taken inside the loop would compare step 262 against step 1
        # and report `grew_at: null` for a world that grew 19 Clusters — which is
        # exactly what the first attempt at this did. A baseline measured after
        # the thing it is supposed to precede is not a baseline.
        cluster_born = len(world.cluster)
        while True:
            world.step()
            step += 1
            lines = [l for l in log.getvalue().splitlines() if l.startswith("[ENGINE]")]
            readout = lines[-1] if lines else ""
            hues = [c.hue for c in cells]
            drift = sum(c.drift for c in cells) / n
            keime = sum(1 for c in cells if c.evolutionskeim)
            spread = max(hues) - min(hues)
            if cluster_start is None:
                cluster_start = cluster_born
            if grew_at is None and len(world.cluster) > cluster_start:
                grew_at = step
            # "Converged" is NOT drift == 0.0. drift is a float and never reaches
            # 0, so an equality test could never fire: it would have gone on
            # reporting "still growing" about a world that visibly died at step
            # 11. The honest test is the kernel's own — the world is converged
            # when it can no longer produce the seed its own rule demands.
            can_evolve = drift > DRIFT_THRESHOLD and keime > 0
            if converged_at is None and not can_evolve:
                converged_at = step
            if born_converged is None:
                born_converged = not can_evolve
            if flat_at is None and spread == 0.0:
                flat_at = step
            write({
                "step": step,
                "cells": n,
                "hue_mean": sum(hues) / n,
                "harm": sum(c.harmonie for c in cells) / n,
                "drift": drift,
                "energie": sum(c.energy for c in cells) / n,
                "spread": spread,
                "keime": keime,
                "cluster": len(world.cluster),
                "cluster_start": cluster_start,
                # None until measured; a number the moment the world builds one.
                "grew_at": grew_at,
                # True when the frame's own fields disagree — i.e. when the
                # mean-drift arm and the Cluster arm say opposite things. A
                # surface that prints `born_converged` without reading this is
                # printing one arm of a contradiction.
                "convergence_disputed": bool(born_converged) and grew_at is not None,
                "readout": readout,
                "thresholds": {
                    "drift": DRIFT_THRESHOLD,
                    "energie": ENERGY_THRESHOLD,
                },
                "born_converged": born_converged,
                "converged_at": converged_at,
                "flat_at": flat_at,
                "files": hashes(kernel, WANTED),
                "error": None,
            })
            time.sleep(tick)
except BaseException as exc:  # noqa: BLE001 - the child must report, not vanish
    write({"step": 0, "converged_at": None, "error": "%s: %s" % (type(exc).__name__, exc),
           "files": {}})
    sys.exit(1)
"""


def start(wait_s: float = 8.0) -> dict[str, Any]:
    """Start the child, once. Explicit, like ``idle start`` — never per request.

    The door only ever *reads* (:func:`frame`). Growing the garden is an action
    someone takes, so a page view can never be what makes this process appear.
    """
    state = kernel_state()
    if not state["present"]:
        return {"started": False, "reason": state["missing_note"], "kernel": state}
    if child_alive():
        return {"started": False, "reason": "already running", "kernel": state}

    directory = garden_dir()
    directory.mkdir(parents=True, exist_ok=True)
    # Not named `frame`: that is the module's public reader, and a local of the
    # same name shadows it — which is how a door ends up returning a path where
    # a verdict should be.
    frame_file = frame_path()
    try:
        frame_file.unlink()
    except OSError:
        pass

    argv = [
        sys.executable,
        "-c",
        _CHILD,
        str(colorverse_dir()),
        str(frame_file),
        str(TICK_S),
        json.dumps(list(KERNEL_FILES)),
    ]
    # The kernel writes its own files; keep its output out of the node's log and
    # let it die with the node rather than outliving it.
    proc = subprocess.Popen(  # noqa: S603 - fixed argv, no shell
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        cwd=str(colorverse_dir()),
    )
    pid_path().write_text(str(proc.pid), encoding="utf-8")

    deadline = time.time() + max(0.0, wait_s)
    while time.time() < deadline:
        if frame_file.is_file():
            return {"started": True, "pid": proc.pid, "kernel": state, "frame": frame(max_age_s=1e9)}
        if proc.poll() is not None:
            got = frame()
            return {
                "started": False,
                "reason": got.get("error") or f"the child exited with {proc.returncode}",
                "kernel": state,
            }
        time.sleep(0.1)
    return {
        "started": False,
        "reason": (
            "the child is running but has not produced a frame yet — it is "
            "building the world, which takes a moment"
        ),
        "pid": proc.pid,
        "kernel": state,
    }


def stop(timeout_s: float = 4.0) -> dict[str, Any]:
    """Stop the child. The frame stays: the last thing the kernel was is still
    a fact about the kernel, and deleting it would make the garden lie by
    omission rather than by error."""
    try:
        pid = int(pid_path().read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return {"stopped": False, "reason": "no child was recorded"}
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        return {"stopped": False, "reason": f"could not signal {pid}: {exc}"}
    deadline = time.time() + max(0.0, timeout_s)
    while time.time() < deadline:
        if not _pid_is_live(pid):
            pid_path().unlink(missing_ok=True)
            return {"stopped": True, "pid": pid}
        time.sleep(0.1)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
    pid_path().unlink(missing_ok=True)
    return {"stopped": True, "pid": pid, "forced": True}
