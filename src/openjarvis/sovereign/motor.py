"""motor — the one seam that starts the local engine.

Set 32, and the first thing in this product that *acts* because a screen said so.
Every other surface here reads; this one starts a process. So its limits are
written down before the code rather than discovered after it.

**What it may do.** It starts the engine the node already talks to — Ollama,
resolved through the platform's own :func:`get_engine`, with the host read from
the configuration and never typed here (``11434`` does not appear in this file
and must never). It writes a log and a pid **outside the repository**, the way
:mod:`garden` keeps its frame, because ``paths.py``'s invariant — never write
runtime state inside the repo — is the one that decides where a spawned process's
words may land.

**What it governs, and why that sentence is not an exemption.** The
``ValueGovernor`` judges *words* (``link.govern(text)``); this action carries
none and generates nothing. Starting the engine cannot produce an ungoverned
answer: answers exist only behind ``/v1/ask``, ``/v1/chat``, ``/v1/agent`` and
``/v1/trialog``, and those doors are unchanged by this set. What starting it can
do is add a process to the owner's own machine and write a log there — which is
the thing the owner asked for when they said *add ollama launch into the game*.
A seam with no words does not need the word gate; it needs its own limits, and
those are the next two paragraphs.

**The argv is written once, here.** :func:`start` takes no string a request could
fill, and the door (``POST /v1/engine/start``) has no body at all. That is the
snake's rule again — *a count crosses, a name does not* — and a command a browser
could name is a command with two writers.

**"Is it running?" is asked of the engine, never of the process table.**
``OllamaEngine.health()`` is a 2 s ``GET /api/tags`` (measured, `engine/ollama.py`
line 541), so no pid-liveness test exists in this file at all and the zombie trap
:mod:`garden` had to dodge with ``/proc/<pid>/stat`` cannot arise: we never ask
whether a pid exists, we ask the only party that knows. The price is honest and
named — a server started by someone else looks exactly like one started here,
which is correct, because the game cares that the motor answers, not who owns it.
When a child *does* die during the wait, its own log lines are quoted back
(``child_words``): evidence, not a paraphrase.

**Measured on the owner's machine (2026-10-01):** ``/usr/local/bin/ollama``
0.34.1 answers on 127.0.0.1:11434 as a bare ``ollama serve`` (pid 2176), and
there is **no systemd user unit** — ``systemctl --user is-active ollama`` says
``inactive`` while the server is answering, and ``list-unit-files`` knows no
``ollama.service``. A launcher written as ``systemctl --user start ollama`` would
have shipped a door that never opens on this machine and reported success. So
this starts a process, and it says which binary it resolved.
"""

from __future__ import annotations

import os
import shutil
import subprocess  # noqa: S404 - one fixed argv, no shell, no request input
import time
from pathlib import Path
from typing import Any

#: The binary we look for on ``PATH`` — a **name**, never a machine path. Here it
#: resolves to ``/usr/local/bin/ollama``; on another host to whatever the owner
#: installed, and to nothing at all if they did not. A literal ``/usr/local/…``
#: here would be one machine's path in a fork whose whole point is that it runs
#: on the owner's machine, and it would FAIL honestly on every other one.
BINARY = "ollama"

#: The one argv in the whole layer. Written here, once. The door sends no body
#: and :func:`start` takes no string, so no request can reach it — which is the
#: property the claim ``the-launch-is-not-the-browsers-to-decide`` asserts.
LAUNCH: tuple[str, ...] = (BINARY, "serve")

#: How long the door waits for the port to answer before it says "not yet". Long
#: enough for a cold server to bind (measured on this host: it was already up, so
#: the cold path is **not** claimed), short enough that a browser does not hang.
WAIT_S = 12.0

#: How often it asks while waiting.
POLL_S = 0.25

#: The engine key this seam means. Written once because the read door and the
#: launch door must not be able to disagree about *which* engine they mean; see
#: :func:`resolve_engine`.
ENGINE_KEY = "ollama"


# ── where its words may land ───────────────────────────────────────────────


def motor_dir() -> Path:
    """Where the log and the pid live. Outside the repository, like
    :func:`garden.garden_dir` — ``paths.py`` forbids runtime state inside the
    repo, and a spawned engine's output is runtime state."""
    if raw := os.environ.get("BIANCA_MOTOR_DIR"):
        return Path(raw)
    return Path.home() / ".openjarvis" / "bianca" / "motor"


def log_path() -> Path:
    """The child's own words, appended — the last run's last words stay readable."""
    return motor_dir() / "engine.log"


def pid_path() -> Path:
    """The pid of the engine *this seam* started, if it started one.

    A record, not a liveness test. Nothing here reads it back to decide whether a
    process is alive — the engine answers that itself — so the zombie trap
    :mod:`garden` documents cannot arise in this module."""
    return motor_dir() / "engine.pid"


# ── the engine, asked rather than assumed ──────────────────────────────────


def resolve_engine(model: str | None = None) -> tuple[str, Any] | None:
    """The engine this node means, or ``None`` if it is registered but down.

    Shared with ``GET /v1/models`` on purpose. The door that *lists* the models
    and the door that *starts* the server must not be able to disagree about
    which engine they are talking about; a second ``get_engine`` call in
    ``api.py`` would be a second answer to that question, and the game would show
    the motor of one engine next to the launch of another.

    Raises whatever ``get_engine`` raises — ``resolve`` below turns that into a
    sentence, and swallowing it here would hide the type name from a reader asking
    what failed.
    """
    from openjarvis.core.config import load_config
    from openjarvis.engine import get_engine

    return get_engine(load_config(), ENGINE_KEY, model=model)


def resolve() -> tuple[tuple[str, Any] | None, str | None]:
    """:func:`resolve_engine` as ``(resolved, why)``, never raising.

    The read door needs both halves in one request, and resolving twice would make
    one door answer one question at two different moments.
    """
    try:
        return resolve_engine(), None
    except Exception as exc:  # noqa: BLE001 - a door that raises is a door that hides
        return None, f"{type(exc).__name__}: {exc}"


def engine_host(engine: Any) -> str | None:
    """The host the engine resolved *for itself*, or ``None``.

    Read off the instance rather than recomputed from the configuration:
    ``OllamaEngine`` resolves explicit host > ``OLLAMA_HOST`` > its default, and
    re-implementing that priority here would be a second writer of a value the
    engine already knows. It is a private attribute — the price of asking one
    question in exactly one place.
    """
    host = getattr(engine, "_host", None)
    return str(host) if host else None


def engine_alive(engine: Any) -> bool:
    """Ask the engine itself. Never look at the process table.

    ``health()`` is the platform's own 2 s ``GET /api/tags`` and it catches its
    own errors, so a bool is the whole truth. An engine without a ``health`` is
    also ``False``: an engine that cannot say it lives has not said it lives, and
    the answer says so in ``why`` rather than quietly reporting a model list.
    """
    probe = getattr(engine, "health", None)
    if not callable(probe):
        return False
    try:
        return bool(probe())
    except Exception:  # noqa: BLE001 - same rule: a hidden error is a hidden engine
        return False


def describe(resolved: tuple[str, Any] | None = None,
             why: str | None = None) -> dict[str, Any]:
    """Is the engine there, and at which host? One answer, for both doors.

    The shape is fixed and the words are the engine's own — a down engine says
    what a down engine means, and it says why an empty list is *not* a statement
    that no models exist. That sentence is the whole reason this exists: before
    it, ``GET /v1/models`` answered ``models: []`` with an authoritative-sounding
    note for two different facts — *nobody answered* and *you have no models* —
    and a game cannot offer to start a motor without telling them apart.
    """
    if why:
        return {"key": ENGINE_KEY, "reachable": False, "host": None, "why": why}
    if not resolved:
        return {
            "key": ENGINE_KEY, "reachable": False, "host": None,
            "why": "the engine is registered but did not answer — an empty list means "
                   "nobody answered, not that no models exist",
        }
    key, engine = resolved
    alive = engine_alive(engine)
    return {
        "key": key, "reachable": alive, "host": engine_host(engine),
        "why": None if alive else "the engine did not answer its own health check",
    }


def child_host() -> str | None:
    """The host the child **will be told to listen on**, or ``None``.

    Read from this process's own environment, because that is what the child
    inherits: :func:`start` passes no ``env=``, deliberately (a written ``env``
    would be a second writer of an address — see the claim). So the answer to
    *„wo hört das Kind auf?"* is a single read of ``OLLAMA_HOST`` and nothing
    else.

    🚨 **This exists because of a measurement, not a plan** (2026-10-01), and the
    measurement has been corrected twice — which is why the correction is written
    down instead of the conclusion.

    *What happened.* A cold start produced ``ready: false`` after the full wait
    while the child's own log said ``Listening on 127.0.0.1:11503``.

    *What I first concluded, and why it was wrong.* That a configured host beats
    the environment — ``OllamaEngine.__init__`` does prefer an explicit ``host=``,
    and ``_discovery.py:17,69`` hands it ``config.engine.ollama_host`` when that
    is non-empty. 🚨 **But on this host it is empty** (measured:
    ``load_config().engine.ollama_host == ''``), so the environment is what this
    node honours, and the explanation could not have been the cause here. A rule
    read from a source file is not a measurement.

    *What the cause is.* The node and the child wanted **the same port**. A
    second cold start with the node on 11506 and ``OLLAMA_HOST`` on 11507 came up
    in 0.30 s with ``ready: true``; with both on one port the child dies with
    ``bind: address already in use`` in its own words. Same trap the throwaway
    harnesses hit. The published cause was the ``dev262`` shape with a smaller
    blast radius: a plausible mechanism in the place of a fact about this box.

    *Why the function survives the correction.* The door does not repair a
    mismatch — it reports both ends of the wire, because the two can differ and
    the reader is the one who has to decide which end is wrong. Writing an
    address here would make the module a second writer of one (the snake's rule
    applied to a port: a count crosses, a name does not).
    """
    raw = os.environ.get("OLLAMA_HOST")
    return raw.rstrip("/") if raw else None


def find_binary() -> str | None:
    """``which ollama`` — a name looked up on ``PATH``, or nothing.

    ``None`` is a real answer here, not a failure: the door reports it and starts
    nothing. It is also what makes the honest-failure branch checkable without
    touching the owner's machine: with a ``PATH`` that has no ``ollama`` in it,
    the door must say so and spawn nothing, and a hardcoded absolute path would
    have sailed past that check.
    """
    return shutil.which(BINARY)


def _log_tail(lines: int = 6) -> str:
    """The child's own last words, quoted rather than paraphrased."""
    try:
        text = log_path().read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    return " · ".join(row.strip() for row in text[-lines:] if row.strip())


# ── the handgriff ─────────────────────────────────────────────────────────


def start(wait_s: float = WAIT_S) -> dict[str, Any]:
    """Start the local engine if it is not already answering. Once.

    Explicit, like ``idle start`` and :func:`garden.start`: a *view* of the game
    must never be what makes a process appear, or every 15 s poll would be a
    launch. The door is the only caller, the game asks for it by clicking, and
    the intent is written beside the button.

    Nothing is logged to the interaction ledger, and that is deliberate: the
    ledger records *words asked of a model*, and this is a handgriff on a
    process. Its evidence is its own log file and the pid below.
    """
    resolved, why = resolve()
    saw = describe(resolved, why)

    base: dict[str, Any] = {
        "already": False, "host": saw["host"], "log": str(log_path()),
        "why": saw["why"],
        # Both ends of the wire, side by side. 🚨 Measured: a cold start on 11503
        # produced `ready: false` after 12 s while the child listened on 11503 —
        # the node asks the host from *its configuration*, which can differ from
        # the environment the child inherited. Two fields, two sources, no second
        # writer of an address; see :func:`child_host`.
        "node_asks": saw["host"] or "die Host-Angabe der Konfiguration (unbekannt, "
                                   "die Engine löste nicht auf)",
        "child_listens": child_host() or "der eigene Standard des Kindes — OLLAMA_HOST "
                                         "ist in dieser Umgebung nicht gesetzt",
    }

    # Already answering: spawn nothing. This branch is the whole idempotence —
    # a second click must not leave a second server behind, and the pid the door
    # reports then is **not** the pid it made.
    if saw["reachable"]:
        return dict(base, started=False, already=True, reachable=True, ready=True,
                    spawned_pid=None, waited_s=0.0,
                    reason="the engine already answers — nothing was started")

    binary = find_binary()
    if not binary:
        return dict(base, started=False, already=False, reachable=False, ready=False,
                    spawned_pid=None, waited_s=0.0, child_words="",
                    launched=None, reason=f"no {BINARY} on PATH — the door will not "
                                          f"invent a binary")

    motor_dir().mkdir(parents=True, exist_ok=True)
    argv = [binary, *LAUNCH[1:]]
    began = time.monotonic()
    with log_path().open("a", encoding="utf-8") as log:
        log.write(f"\n--- {argv} gestartet {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        log.flush()
        proc = subprocess.Popen(  # noqa: S603 - fixed argv, no shell, no request input
            argv,
            stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True, cwd=str(motor_dir()),
        )
    pid_path().write_text(str(proc.pid), encoding="utf-8")

    # Bounded wait, in the same two steps as everywhere else: resolve, then ask
    # through :func:`engine_alive`. 🚨 Not "did resolve return something" —
    # ``get_engine`` happens to health-check internally, and leaning on that would
    # make this the one place in the file whose meaning depends on somebody else's
    # private behaviour. One pattern in the module is worth two cheap local GETs.
    ready, exited = False, None
    deadline = began + max(0.0, wait_s)
    while True:
        if proc.poll() is not None:
            exited = proc.returncode
            break
        live, _ = resolve()
        if live is not None and engine_alive(live[1]):
            ready = True
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(POLL_S)

    waited = round(time.monotonic() - began, 2)
    answer = dict(base, launched=list(argv), spawned_pid=proc.pid, waited_s=waited,
                  child_words=_log_tail())
    if exited is not None:
        return dict(answer, started=False, reachable=False, ready=False,
                    reason=f"the child exited with code {exited} — its own words are in child_words")
    if not ready:
        # 🚨 Hoisted out of the sentence on purpose: the first version interpolated
        # `child_host() or 'seinem eigenen Standard'` straight into the f-string, and
        # the apostrophe in *seinem* closed the literal — a syntax error that no
        # claim and no test caught, because both read the file as text. Only
        # importing the module found it. German prose with apostrophes inside an
        # f-string is a trap; the value belongs in a variable.
        #
        # 🚨 And the sentence names *both* ends without claiming to know which one
        # is wrong. The first version blamed ``OLLAMA_HOST`` against the
        # configuration — read off `ollama.py:124`, true as a rule, and false as
        # a cause on this host (`ollama_host` is empty here; the real cause of the
        # 2026-10-01 observation was the node and the child sharing a port). See
        # `child_host`. A wait that ran out does not know its own reason, and a
        # sentence that guesses is the `dev262` shape.
        hort = child_host() or "seinem eigenen Standard"
        return dict(answer, started=True, reachable=False, ready=False,
                    reason=f"der Motor hört nach {waited:.1f} s noch nicht — er läuft, "
                           f"antwortet aber nicht. Das ist keine Fertigmeldung, sondern eine "
                           f"Wartezeit. Der Knoten fragt {answer['node_asks']}, das Kind "
                           f"hört auf {hort}. Sind beide gleich und es antwortet trotzdem "
                           f"nicht, dann bindet es woanders oder gar nicht — seine eigenen "
                           f"Worte stehen in child_words.")
    return dict(answer, started=True, reachable=True, ready=True,
                reason=f"der Motor antwortet nach {waited:.1f} s")