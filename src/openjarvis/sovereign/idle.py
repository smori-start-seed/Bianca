"""idle — the idle-contract operator (Phase 5A).

A quiet background loop: while the machine is idle (CPU below a threshold for
a sustained streak), the node performs verifiable work units — small,
measured, audited contributions to the ecosystem (ledger + notes stats,
cycle snapshot, environment health).

Pure functions (``decide_idle``, ``cpu_percent``, pidfile helpers) are unit
tested; the daemon itself runs out-of-process via ``python -m ...idle`` so
``bianca-sovereign idle start|status|stop`` controls it cleanly.

Design: conservative by default — never loads the box, units are capped per
run, everything is logged to the Interaction Ledger.
"""

from __future__ import annotations

import datetime as _dt
import os
import hashlib
import os
import re
import signal
import sys
import time
from pathlib import Path

from openjarvis.sovereign.daily import memory_stats, units_dir
from openjarvis.sovereign.logger import InteractionLogger

INTERVAL = int(os.environ.get("BIANCA_IDLE_INTERVAL", "30"))
THRESHOLD = int(os.environ.get("BIANCA_IDLE_THRESHOLD", "70"))   # cpu% below = idle
MIN_STREAK = int(os.environ.get("BIANCA_IDLE_MIN_STREAK", "2"))  # consecutive idle samples before a unit
MAX_UNITS_PER_RUN = int(os.environ.get("BIANCA_IDLE_MAX_UNITS", "24"))


def pidfile_path() -> Path:
    return Path(os.environ.get("BIANCA_IDLE_PIDFILE", str(Path.home() / ".openjarvis" / "bianca-idle.pid")))


def cpu_percent(sample_s: float = 0.35) -> float:
    """Busy CPU percent from two /proc/stat samples (0..100)."""
    def _read() -> tuple[int, int]:
        with open("/proc/stat", "r") as f:
            parts = f.readline().split()[1:]
        vals = [int(x) for x in parts]
        idle = vals[3] + (vals[4] if len(vals) > 4 else 0)  # idle + iowait
        return sum(vals), idle
    t0 = _read()
    time.sleep(sample_s)
    t1 = _read()
    d_total = t1[0] - t0[0]
    d_idle = t1[1] - t0[1]
    if d_total <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * (1.0 - d_idle / d_total)))


def decide_idle(cpu: float, threshold: int | None = None, streak: int = 0,
                min_streak: int | None = None) -> bool:
    """True when the box has been idle for the required consecutive samples."""
    threshold = THRESHOLD if threshold is None else threshold
    min_streak = MIN_STREAK if min_streak is None else min_streak
    if cpu >= threshold:
        return False
    return streak + 1 >= min_streak


def write_pidfile(pid: int | None = None) -> Path:
    path = pidfile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(pid or os.getpid()), encoding="utf-8")
    return path


def read_pid(path: Path | str | None = None) -> int | None:
    """The recorded pid, or ``None``.

    Set 30: ``path`` is a parameter because the working-session module has one
    pidfile per session and would otherwise have to write a second reader. One
    reader, two callers — the same rule as one writer.
    """
    target = Path(path) if path is not None else pidfile_path()
    if not target.exists():
        return None
    try:
        return int(target.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


#: The module a pidfile must name for the cmdline check to mean anything. It is
#: the default because :mod:`idle` is the first user; the session module passes
#: its own name. Set 30 found this nailed to a literal: a live session process
#: would have read ``running: no``, which is the safe direction and still a lie.
DEFAULT_PID_MODULE = "openjarvis.sovereign.idle"


def is_alive(pid: int, module: str = DEFAULT_PID_MODULE) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # The pid is live — but is it OUR daemon? A recycled PID (any unrelated
    # process) would answer "running" to signal-0. Verify the cmdline names the
    # module; where /proc is unavailable, keep the signal-0 verdict.
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().decode(errors="replace")
        if module not in cmdline:
            return False
    except (OSError, FileNotFoundError):
        pass
    return True


def remove_pidfile() -> None:
    try:
        pidfile_path().unlink(missing_ok=True)
    except OSError:
        pass


def today_units() -> int:
    """Count today's work units (filenames: work_%Y-%m-%d_%H%M%S.md)."""
    today = _dt.datetime.now().strftime("%Y-%m-%d")
    return sum(1 for f in units_dir().glob("work_*.md") if today in f.name)


#: The garden's three structural facts, named by where the rule lives. These are
#: **locations in a sibling repository**, not code of ours, and they are written
#: down as strings on purpose: this file must never import from, edit, or depend
#: on the kernel's behaviour — it may only say what it measured. A number typed
#: here instead of read from there is a claim about someone else's code that
#: nothing would notice going stale, which is the rule the snake already follows
#: for the risk lexicon and the one the garden follows for ``DRIFT_THRESHOLD``.
#:
#: 🚨 **SET 35 (2026-10-05) — these three were once read as "why the garden
#: cannot grow", and that reading was FALSE.** All three statements below are
#: still true of the kernel; what was wrong was the conclusion drawn from them.
#: The garden **does** grow: 17-18 new Clusters at step 1 on the set-35 kernel,
#: **129** (90 → 129) once the set-36 doors are open, and `flat_at` does not
#: occur in 1000 steps. Nothing here was the blocker — the blocker was *when* the
#: seed gate was tested: `engine.py` marked its seeds at the **end** of `step()`,
#: after seven update passes had pulled the neighbourhood variance down by a
#: factor of 0.21, so a door nobody opened in time was measured as a wall.
#: Measured on the kernel this host reads; notes `five-levels-notes.md` 13-15
#: (set 35) and 16 (set 36).
#:
#: **SET 36 (2026-10-09) — the limit is still one-shot growth, but the reason
#: changed.** The Ring and Sphere doors now give the kernel a *disorder source*
#: (a wave on the free field) and re-light the clusters, so growth reaches 129
#: and ~760 cells stay alive rather than fading. What remains is **one-shot**:
#: the maximum arrives by ~step 50 and holds, because the new clusters consume
#: the very free field the Sphere paints on. The three facts below are still true
#: of the kernel; what they no longer carry is "no source of disorder".
#:
#: **SET 38 (2026-10-16) — the owner took set 37's growth factor back; the crest
#: of the wave decides instead.** There is no `WACHSTUMSFAKTOR` any more. Set 37
#: had gated seeding with a coin (`random() < 0.6`, `engine.py:75`); measured it
#: cost slightly (90 → 126/127/133 against 130/131/131) and replaced the cell's
#: own decision with a global die roll. Now a free cell seeds only when the
#: Sphere's travelling wave has its **crest** over it (`z.hue < 180`, the sign
#: half of the painted wave, on `engine.py:75`). Measured (seeds 1/7/42, 1500
#: steps): 90 → 125/126/126, 822-842 cells alive, `flat_at` never, and the burst
#: now carries over 22 steps to step 172 (set 37: 16 steps to step 23). Growth is
#: still **one-shot** — and the measured cause is no longer the factor: the free
#: field's gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of 221
#: free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and
#: `Cluster.mutation()`'s edger consumes free cells (313 `in_cluster` after step
#: 1, not the real 44). Notes: `five-levels-notes.md` set 38.
GARDEN_DEATH: tuple[dict[str, str], ...] = (
    {
        "what": "the neighbourhood is a ring, not a field",
        "where": "Colorverse/saturings.py:19-29",
        "reads": "every cell i sees cells i±1, i±2, i±3 of one ordered list",
    },
    {
        "what": "averaging is the only rule there is for hue",
        # Set 34: the owner changed the sibling kernel (see the notes), and 19
        # added lines above moved this from :95 to :114. The address is part of
        # the claim, so `the-garden-death-is-named` FAILed on the move — which is
        # the check working. What the line SAYS is unchanged: the averaging rule
        # is still the only hue rule there is, and it is still unconditional.
        "where": "Colorverse/Zelle.py:130",
        "reads": "hue = (1-alpha)*hue + alpha*avg_hue — diffusion on a connected graph",
    },
    {
        "what": "and the seed needs the opposite quantity",
        "where": "Colorverse/engine.py:72-76",
        "reads": "an evolutionskeim requires drift > 0.4, i.e. a difference",
    },
)


def garden_diagnosis() -> dict:
    """Measure the garden and name, from the measurement, what limits it.

    Set 29 built this to answer *Wachstum*, and it first measured that there is
    no growth to have: the frame is 742 bytes and is ``os.replace``d onto one
    fixed path, so it has overwritten itself thousands of times without growing
    by a byte. **A cap on that is a cap on nothing**, and the honest instrument
    is a diagnosis that runs and says so.

    🚨 **Set 35 retracted the conclusion, not the instrument.** For four sets
    this function answered "why the garden cannot grow", and that answer is
    false: the kernel now builds **17-18 new Clusters at step 1** and holds
    colour for **1000 steps** (`flat_at` never fires). What had been diagnosed
    as a wall was **a door nobody opened in time** — the seed gate was tested
    after seven update passes had already cut the neighbourhood variance by a
    factor of 0.21.

    🚨 **Set 36 (2026-10-09) took the decision set 35 left open.** The owner
    opened the Ring and Sphere doors, so the kernel now has the *disorder source*
    it lacked: growth reaches **129 (90 → 129)** and ~760 cells stay alive and
    hold colour. The rules below are still named and still true; what they no
    longer carry is "no source of disorder". Growth is still **one-shot** — the
    maximum arrives by ~step 50 and holds, because the new clusters consume the
    free field the Sphere paints on. Time-bound, not space-bound — lowering a
    cell-pool constant changes nothing, and that is the one measurement worth
    repeating rather than re-deriving.

    🚨 **Set 38 (2026-10-16) — the owner took set 37's growth factor back; the
    crest of the wave decides instead.** There is no `WACHSTUMSFAKTOR` any more.
    Set 37 had gated seeding with a coin (`random() < 0.6`, `engine.py:75`);
    measured it cost slightly (90 → 126/127/133 against 130/131/131) and replaced
    the cell's own decision with a global die roll. Now a free cell seeds only
    when the Sphere's travelling wave has its **crest** over it (`z.hue < 180`, the
    sign half of the painted wave). Measured: **90 → 125/126/126** (seeds 1/7/42,
    1500 steps), 822-842 cells alive, `flat_at` never, and the burst now carries
    **over 22 steps to step 172** instead of 16 steps to step 23. Growth is still
    **one-shot**, and the measured cause is no longer the factor: the free
    field's gate closes on `harmonie < 0.5` (a witness inside the gate: 219 of
    221 free cells carry `drift > 0.4` and **0** carry `harmonie < 0.5`), and
    `Cluster.mutation()`'s **edger** consumes free cells (`abs(f.hue - edger.hue)
    < 20`, measured: 313 `in_cluster` after step 1, not the real 44).

    Everything here is read *after* the frame exists and reaches no door: it
    cannot move a verdict, because there is no verdict anywhere in it. When the
    garden has not been started, the answer is that it has not been started —
    not a guess about why, and never a zero.
    """
    from openjarvis.sovereign import garden

    f = garden.frame()
    if not f.get("present") or f.get("error"):
        return {
            "measured": False,
            "reason": f.get("error") or "no frame yet — the garden has not been started",
            "rule": GARDEN_DEATH,
        }

    drift = f.get("drift")
    threshold = (f.get("thresholds") or {}).get("drift")
    # `can_evolve` is the kernel's own conjunction, in the kernel's own words,
    # and the threshold is the one the frame carries — never a literal here.
    keime = f.get("keime") or 0
    can_evolve = bool(threshold is not None and drift is not None
                      and drift > threshold and keime > 0)
    # 🚨 **Set 35 (2026-10-06). `can_evolve` ist FALSCH und war es lange.**
    # Es vergleicht den *Mittelwert* des Drifts über 1000 Zellen mit 0.4 und
    # fragt dann, ob `keime > 0`. Der Mittelarm ist damit zweimal falsch: ein
    # Mittel ist keine Zahl (Fortpflanzung braucht 11 Saaten gleichzeitig), und
    # `keime > 0` ist mit einem einzigen Samen zufrieden, den es nie gab.
    # Gemessen am Owner-Lauf, Schritt 1579: `drift 0.000128` → `orders 3`,
    # `keime 208`, `cluster 111` bei `cluster_start 90`, `grew_at 1`.
    # Die ehrliche Antwort auf "kann er sich fortpflanzen" ist deshalb nicht
    # `can_evolve`, sondern die Clusterzahl — und die stimmt: er kann es.
    grew_at = f.get("grew_at")
    cluster_start = f.get("cluster_start")
    cluster_now = f.get("cluster")
    grew = (
        isinstance(grew_at, int) and isinstance(cluster_start, int)
        and isinstance(cluster_now, int) and cluster_now > cluster_start
    )
    # Nur meaningful when the world is *below* the rule. A `0` here would read
    # as "evenly below", and a negative number as "above by n orders", when the
    # honest answer for a drifting garden is "that question does not apply".
    orders = None
    if isinstance(drift, (int, float)) and isinstance(threshold, (int, float)) \
            and 0 < drift < threshold:
        import math
        orders = round(math.log10(threshold / drift))
    # 🚨 **Set 35b (2026-10-06). `orders_below_threshold` ist `None` aus ZWEI
    # entgegengesetzten Gründen**, und bislang kannte nur diese Funktion den
    # Unterschied — die Flächen nicht:
    #
    #   (a) `drift >= threshold` → die Welt liegt *nicht* unter der Regel, die
    #       Frage trifft nicht zu. Das ist der Fall, den die bestehende Probe
    #       hält (`drift 0.9`, "only meaningful below").
    #   (b) `drift == 0` → sie liegt *unter* der Regel, aber `log10(0.4 / 0)`
    #       ist eine Division durch Null: unendlich viele Größenordnungen,
    #       keine endliche Zahl. `0 < drift` verwirft diesen Fall, und die
    #       Begründung oben ("a `0` here would read as evenly below") nennt ihn
    #       gar nicht — sie beschreibt nur `drift == threshold` und
    #       `drift > threshold`.
    #
    # Gemessen am laufenden Garten, Schritt 8173: `drift` **exakt `0.0`**,
    # `orders None`. Die Warum-Box druckte daraufhin "liegt None Größenordnungen
    # unter der Schwelle", die CLI "drift is None orders of magnitude below".
    # Ein `None`, das in einer Zahlenschlange als Wort erscheint, sieht harmlos
    # aus — es ist dieselbe Klasse Fehler wie eine richtige Zahl an falscher
    # Stelle, nur leichter zu übersehen. Also wird der Grund benannt, damit keine
    # Fläche raten muß, welcher der beiden Fälle vorliegt.
    if orders is not None:
        orders_reason = None
    elif not isinstance(drift, (int, float)) or not isinstance(threshold, (int, float)):
        orders_reason = "not_measured"
    elif drift == 0:
        orders_reason = "drift_is_zero"
    else:
        orders_reason = "not_below_the_rule"

    return {
        "measured": True,
        "step": f.get("step"),
        "cells": f.get("cells"),
        "drift": drift,
        "drift_threshold": threshold,
        # The count itself, and — since set 35b — *why* it is absent. One fact
        # per field: `orders_below_threshold: null` alone had two opposite
        # meanings, and a surface forced to guess picks the wrong one.
        "orders_below_threshold": orders,
        "orders_undefined_because": orders_reason,
        "keime": keime,
        "spread": f.get("spread"),
        "born_converged": f.get("born_converged"),
        # 🚨 **Set 35 (2026-10-06), Nachtrag.** Diese drei Felder standen in
        # Abschnitt 16 zuerst nur im Bericht des Work-Unit-Texts, und die
        # Web-Oberfläche sah sie nicht — sie zeigte weiter „Er kann nicht
        # wachsen" und daneben „+21 Cluster gewachsen", aus zwei Bloecken
        # derselben Datei. Der Owner hat den Widerspruch zuerst gesehen, und er
        # hat recht: **eine Fläche, die eine stimmende Kennzahl zeigt, ohne den
        # Widerspruch zu pruefen, den der Rahmen selbst mitliefert, ist die
        # gefaehrlichere Form des Fehlers.** `orders_below_threshold` == 3 war
        # eine richtige Zahl und machte die falsche Aussage schwer widerlegbar.
        "convergence_disputed": f.get("convergence_disputed"),
        "cluster_start": cluster_start,
        "cluster": cluster_now,
        "grew_at": grew_at,
        # The answer to the owner's question, in the kernel's own unit. Not a
        # boolean derived from a mean: a measured comparison of two counts.
        "grew": grew,
        "new_clusters": (cluster_now - cluster_start)
                        if isinstance(cluster_start, int) and isinstance(cluster_now, int)
                        else None,
        # 🚨 **Set 35: the frame contradicts itself, so the disagreement is
        # carried as its own field rather than resolved by picking an arm.**
        # `born_converged` comes from the MEAN drift over 1000 cells; measured
        # on the current kernel the frame at step 262 reads `born_converged:
        # true`, `converged_at: 1` **and** `cluster_start: 90 → cluster: 109`
        # with `grew_at: 1`. Both are true. The garden grows and the mean
        # condition is never met, because growth needs seeds gathered into a
        # cluster (1..11 at once, `engine.py:164-175`) and the mean is not a
        # count. Collapsing this to
        # one boolean would be the `dev262` shape: a number that cannot be
        # false.
        "cluster_start": f.get("cluster_start"),
        "cluster": f.get("cluster"),
        "grew_at": f.get("grew_at"),
        "convergence_disputed": f.get("convergence_disputed"),
        "converged_at": f.get("converged_at"),
        "flat_at": f.get("flat_at"),
        "can_evolve": can_evolve,
        # The frame file's own size, in bytes: the number a cap would have had
        # to bound. Reported so the claim "there is no growth" is re-derivable
        # from the record instead of taken from this docstring.
        "frame_bytes": garden.frame_path().stat().st_size
        if garden.frame_path().is_file() else None,
        "rule": GARDEN_DEATH,
    }


# 🚨 **Set 35b.** The FACT is written once, by `garden_diagnosis()` above; this
# is only its ENGLISH WORDING, shared by the two English surfaces (the CLI and
# the work-unit report) so they cannot drift apart. The face writes its own
# German wording — a translation of a fact is not a second writer of it.
def garden_orders_prose(state: dict) -> str:
    """One sentence for the order count, whichever of the three cases holds."""
    orders = state.get("orders_below_threshold")
    if orders is not None:
        return f"drift is {orders} orders of magnitude below the rule that needs it"
    reason = state.get("orders_undefined_because")
    if reason == "drift_is_zero":
        return ("the mean drift is exactly 0 — below the rule, but the ratio to it "
                "is undefined (division by zero), so there is no order count")
    if reason == "not_below_the_rule":
        return "the drift is not below the rule, so no order count applies"
    # An unknown reason must not be answered with a direction: guessing which of
    # the two cases holds is exactly the defect this field was added to remove.
    return "the order count is absent, and no reason for its absence was supplied"


def do_work_unit(ledger: InteractionLogger, notes_dir: Path | None = None) -> dict:
    """One verifiable unit of idle work; returns and records its summary."""
    from openjarvis.sovereign.link import default_link
    link = default_link()
    ctx = link.prepare()
    mem = memory_stats()
    garden_state = garden_diagnosis()
    stamp = _dt.datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")  # _%f: two units in the same second must not collide — a collision would silently overwrite one artifact while the ledger keeps two audits
    unit = {
        "stamp": stamp,
        "cycle": ctx["cycle_state"].get("grundmodus", "?"),
        "gold_loaded": ctx["gold_manifest"],
        "memory_documents": mem["documents"],
        "cpu_at_unit": round(cpu_percent(0.25), 1),
    }
    d = units_dir()
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# Work unit {stamp}", ""]
    lines += [f"- **{k}**: {v}" for k, v in unit.items()]

    # Set 29: the garden's own diagnosis, in the unit. Prose, not a verdict —
    # this is the one ungated surface of the product, and the only thing this
    # loop does with it is name, from the measurement, which lines of a sibling
    # repository prevent it from growing. It is written here rather than in a
    # second file so the hash below covers it: a unit that recorded a garden
    # claim no receipt covers would be the mirror's "outcome without evidence"
    # defect one layer down.
    lines += ["", "## The garden, measured", ""]
    if garden_state.get("measured"):
        lines += [
            f"- **step**: {garden_state.get('step')} (cells {garden_state.get('cells')})",
            f"- **drift**: {garden_state.get('drift')} against a threshold of"
            f" {garden_state.get('drift_threshold')}"
            # Set 35b: the old form wrote nothing when the count was absent —
            # honest (it invented no number) but it hid the fact that the mean
            # drift is exactly 0. The reason is now stated instead of skipped.
            f" — {garden_orders_prose(garden_state)}",
            f"- **keime / spread**: {garden_state.get('keime')} / {garden_state.get('spread')}",
            f"- **born_converged**: {garden_state.get('born_converged')}"
            f" (converged_at {garden_state.get('converged_at')},"
            f" flat_at {garden_state.get('flat_at')})",
            # 🚨 Set 35: when the frame's own fields disagree, the receipt says so
            # rather than printing the arm it happens to prefer. Growth needs 11
            # seeds at once; the mean drift is not a count.
            *(
                [f"- **the frame contradicts itself, and both arms are true**:"
                 f" born_converged says the condition is never met, and the world"
                 f" grew {garden_state.get('cluster', 0) - (garden_state.get('cluster_start') or 0)}"
                 f" Clusters from step {garden_state.get('grew_at')}"
                 f" ({garden_state.get('cluster_start')} -> {garden_state.get('cluster')})."
                 f" Measured 2026-10-05; the mean condition is a mean and the gate"
                 f" is a count of 11."]
                if garden_state.get("convergence_disputed") else []
            ),
            f"- **can evolve**: {garden_state.get('can_evolve')}"
            f" — ⚠️ **das ist die Mittel-Drift und damit irrefuehrend**;"
            f" gemessen an den Clustern: gewachsen = {garden_state.get('grew')}"
            f" (+{garden_state.get('new_clusters')} Cluster ab Schritt"
            f" {garden_state.get('grew_at')})",
            f"- **frame bytes**: {garden_state.get('frame_bytes')}"
            "  — one fixed path, overwritten in place; this is the number a cap"
            " would have had to bound",
        ]
    else:
        lines.append(f"- not measured: {garden_state.get('reason')}")
    # The three locations travel in BOTH cases. They are a standing fact about
    # the kernel, independent of whether a frame happens to exist right now, and
    # a receipt that named them only when it had a measurement would leave the
    # ungated surface unexplained exactly when it is unobserved.
    lines += ["", "What limits the garden, by location in a sibling repository",
              "(still true; the set-35 retraction was about the conclusion, not these):"]
    for rule in garden_state.get("rule", ()):
        lines.append(f"- `{rule['where']}` — {rule['what']} ({rule['reads']})")

    text = "\n".join(lines) + "\n"
    (d / f"work_{stamp}.md").write_text(text, encoding="utf-8")
    # audit names the artifact and commits its content hash, so every ledger
    # row is a tamper-evident receipt: unit=<file> sha=<digest>
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    # `can_evolve` rides in the audit, not just the file: the receipt is what
    # `verify_units` re-reads, and a claim only the file makes is a claim the
    # verifier cannot see. `none` rather than `False` for the unmeasured case —
    # "not measured" and "measured, cannot evolve" must never read alike.
    evo = (str(garden_state["can_evolve"]).lower() if garden_state.get("measured")
           else "none")
    ledger.log_event(
        "WORK_UNIT",
        f"unit={stamp} sha={digest} cycle={unit['cycle']} gold={unit['gold_loaded']} "
        f"mem_docs={unit['memory_documents']} cpu={unit['cpu_at_unit']}% "
        f"garden_can_evolve={evo} garden_keime={garden_state.get('keime', 'none')}",
        actor="Bianca/idle",
    )
    return {**unit, "garden": garden_state}


#: Set 29. A reconciliation is a *dated admission* that an audit's file is not
#: recoverable. It never removes the audit, and it never claims the file was
#: verified — it says the opposite, in the record, where the verifier can see it.
RECONCILIATION_TYPE = "WORK_UNIT_RECONCILED"


def reconcile_orphan(
    stamp: str,
    reason: str,
    ledger: InteractionLogger,
    ledger_dir: str | Path | None = None,
) -> dict:
    """Admit, in the record, that an orphan audit's file is unrecoverable.

    The owner's completion criterion is ``verify_units`` -> PASS, and the single
    failure standing in its way is one audit naming a unit whose file is gone.
    **Deleting the audit would make the number right and the record false**, and
    that is the single act this ledger exists to prevent — so this function
    refuses to delete anything at all. It adds a dated, reasoned statement, and
    :func:`verify_units` then reports the orphan as *reconciled* rather than
    failing on it.

    The property that keeps this from being a loophole: a reconciliation names
    the hash it is standing in for, so **a returning file with different bytes
    still reads as ``tampered``**. It closes a *presence* failure and never a
    *content* one. :func:`verify_units` re-derives the hash from the file and
    compares it against the audit, not against the reconciliation, so the
    reconciliation is overridden by the file the moment the file exists.
    """
    from openjarvis.sovereign import daily
    ld = Path(ledger_dir or daily.ledger_dir())

    if not str(reason or "").strip():
        raise ValueError("a reconciliation without a reason is a deletion with extra steps")
    if not str(stamp or "").strip():
        raise ValueError("a reconciliation must name the unit it stands in for")

    # The hash is read out of the audit being reconciled, never supplied by the
    # caller: a reconciliation that could name any hash would be a blank cheque.
    found: str | None = None
    for ev in daily.read_ledger_events(ld):
        if ev["type"] != "WORK_UNIT":
            continue
        m = re.search(r"unit=([^\s]+)\s+sha=([0-9a-f]+)", ev["message"])
        if m and m.group(1) == stamp:
            found = m.group(2)
    if found is None:
        raise ValueError(f"no WORK_UNIT audit names unit={stamp} with a sha — nothing to reconcile")

    entry = {
        "stamp": stamp,
        "sha": found,
        "reason": str(reason).strip(),
        "units_dir": str(units_dir()),
        "dir_present": units_dir().is_dir(),
    }
    ledger.log_event(
        RECONCILIATION_TYPE,
        f"unit={stamp} sha={found} reason={entry['reason']!r} "
        f"units_dir={entry['units_dir']} dir_present={str(entry['dir_present']).lower()}",
        actor="Bianca/idle",
    )
    return entry


def verify_units(ledger_dir: str | Path | None = None, units: Path | None = None) -> dict:
    """Prove the work-unit contract end-to-end: every unit file must be named
    by a WORK_UNIT audit whose content hash matches the file.

    Statuses per unit file — ``verified`` (audit names it and sha matches),
    ``legacy`` (audit names it but predates hashes), ``missing-audit`` (no
    audit at all), ``tampered`` (hash mismatch). Audits naming files that do
    not exist surface as ``orphan_audits``; pre-hash audits that cannot be
    tied to any file count as ``legacy_events``.
    """
    from openjarvis.sovereign import daily
    ld = Path(ledger_dir or daily.ledger_dir())
    ud = units or units_dir()

    audits: dict[str, str] = {}   # unit stamp -> audit message
    legacy_events = 0
    reconciled: dict[str, str] = {}  # unit stamp -> the admission that stands in for it
    for ev in daily.read_ledger_events(ld):
        if ev["type"] == RECONCILIATION_TYPE:
            m = re.search(r"unit=([^\s]+)\s+sha=([0-9a-f]+)", ev["message"])
            if m:
                reconciled[m.group(1)] = ev["message"]
            continue
        if ev["type"] != "WORK_UNIT":
            continue
        m = re.search(r"unit=([^\s]+)", ev["message"])
        if m:
            audits[m.group(1)] = ev["message"]
        else:
            legacy_events += 1

    findings: list[dict] = []
    per_file: set[str] = set()
    for f in sorted(ud.glob("work_*.md")):
        stamp = f.name[len("work_"):-len(".md")]
        digest = hashlib.sha256(
            f.read_text(encoding="utf-8", errors="replace").encode("utf-8")).hexdigest()[:12]
        per_file.add(stamp)
        audit = audits.get(stamp)
        if audit is None:
            status = "missing-audit"
        elif "sha=" not in audit:
            status = "legacy"
        elif digest in audit:
            status = "verified"
        else:
            status = "tampered"
        # A file that came back is judged against its own audit, above, and a
        # reconciliation never reaches this branch — so a reconciled orphan that
        # reappears with the wrong bytes still reads `tampered`. That is the
        # whole difference between a reconciliation and a deletion, and it is
        # why the sha is compared to `audit` and never to the admission.
        findings.append({
            "stamp": stamp, "status": status, "sha": digest,
            "reconciled": stamp in reconciled or None,
        })

    counts = {s: sum(1 for fn in findings if fn["status"] == s)
              for s in ("verified", "legacy", "missing-audit", "tampered")}
    orphans = sorted(s for s in audits if s not in per_file)
    # Set 29: an orphan may be *reconciled* — admitted as unrecoverable, in the
    # record, with the hash kept. Two lists, never one summed number: a shared
    # count is how one half of a thing starts quietly counting the other, which
    # is the defect set 28 found in the mirror and would be the same defect here.
    orphans_reconciled = sorted(s for s in orphans if s in reconciled)
    orphans_unreconciled = sorted(s for s in orphans if s not in reconciled)
    # A reconciliation for a stamp that has a file is not a reconciliation, it
    # is a stale admission; it is reported so it cannot sit unnoticed.
    stale_reconciliations = sorted(
        s for s in reconciled if s in per_file and s not in orphans)
    # pre-anchor-era audits cannot be tied to a specific file, but each one
    # plausibly certifies one untraceable file; only the excess is a breach
    unreconciled = max(0, counts["missing-audit"] - legacy_events)
    failures = counts["tampered"] + len(orphans_unreconciled) + unreconciled
    return {
        "findings": findings,
        "verified": counts["verified"],
        "legacy": counts["legacy"],
        "missing_audit": counts["missing-audit"],
        "tampered": counts["tampered"],
        "orphan_audits": orphans,
        "orphan_audits_reconciled": orphans_reconciled,
        "orphan_audits_unreconciled": orphans_unreconciled,
        "stale_reconciliations": stale_reconciliations,
        "legacy_events": legacy_events,
        "failures": failures,
        "contract_holds": failures == 0,
    }


def idle_loop(ledger_dir: str, stop_after_units: int | None = None) -> None:
    """Run the idle loop until SIGTERM/SIGINT (or unit budget exhausted)."""
    stop = False
    def _handle(signum, _frame) -> None:
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, _handle)
    signal.signal(signal.SIGINT, _handle)

    ledger = InteractionLogger(ledger_dir)
    streak = 0
    units_done = 0
    stop_after = MAX_UNITS_PER_RUN if stop_after_units is None else stop_after_units
    while not stop:
        cpu = cpu_percent()
        if decide_idle(cpu, streak=streak):
            streak += 1
            if streak >= MIN_STREAK:
                do_work_unit(ledger)
                units_done += 1
                streak = 0  # one unit per window; stay gentle on CPU
                if units_done >= stop_after:
                    stop = True
        else:
            streak = 0
        if not stop:
            time.sleep(INTERVAL)
    remove_pidfile()
    sys.exit(0)


if __name__ == "__main__":
    # Daemon entry: python -m openjarvis.sovereign.idle <ledger_dir> [stop_after_units]
    #
    # Set 29: this entry point used to take `sys.argv[1]` as the ledger directory
    # with no validation, so `python -m openjarvis.sovereign.idle verify` — a
    # command that reads like the one in `cli.py` and means nothing here — became
    # a *directory named "verify"* and started the daemon. Measured: this set ran
    # it, the loop began, and it was killed within seconds; nothing was written
    # because the first unit comes after `INTERVAL` (30 s).
    #
    # A word that is not a path is refused rather than believed. The check is on
    # the shape of the argument, not on a list of the words that have been tried:
    # a blocklist of known-mistaken words is a list the next typo has to be
    # added to, and this one is about the *kind* of thing the argument must be.
    args = sys.argv[1:]
    if args and not Path(args[0]).is_absolute():
        sys.stderr.write(
            "[!] this entry point takes a ledger DIRECTORY, not a subcommand.\n"
            f"    got {args[0]!r}, which is not a path.\n"
            "    subcommands live on the CLI: `bianca-sovereign idle "
            "status|start|stop|verify|garden|reconcile`.\n"
            "    daemon form: python -m openjarvis.sovereign.idle <abs-ledger-dir> [units]\n"
        )
        raise SystemExit(2)
    write_pidfile()
    ledger_dir = args[0] if args else str(Path.home() / ".openjarvis" / "bianca" / "ledger")
    try:
        stop_after = int(args[1]) if len(args) > 1 else None
    except ValueError:
        sys.stderr.write(f"[!] stop_after_units must be a whole number, got {args[1]!r}\n")
        raise SystemExit(2)
    idle_loop(ledger_dir, stop_after_units=stop_after)