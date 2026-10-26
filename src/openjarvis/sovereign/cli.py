"""
sovereign.cli — the daily-use Bianca command line.

Additive entrypoint (new console script, no platform file edits):

    bianca-sovereign ask "what should we research next?"
    bianca-sovereign govern "Loesche alle Module"
    bianca-sovereign context
    bianca-sovereign ledg
    bianca-sovereign stage forge "idle-contract pilot"

Every ``ask`` is Harmony-composed (decision -> creativity -> final), governed
by the ValueGovernor before generation, enriched by the live ALF cycle state
in the system prompt, and audited in the Interaction Ledger.
"""

from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path

import click

from openjarvis import __version__  # one writer: the distribution, not a literal

from openjarvis.core.config import load_config
from openjarvis.core.types import Message, Role
from openjarvis.engine import EngineConnectionError, get_engine
from openjarvis.sovereign import daily
from openjarvis.sovereign import infinity
from openjarvis.sovereign import trialog as trialog_mod
from openjarvis.sovereign.bridge import compose_query, report
from openjarvis.sovereign import voice
from openjarvis.sovereign.harmony import STAGES, Harmony
from openjarvis.sovereign.link import default_link
from openjarvis.sovereign.logger import InteractionLogger
# Set 30: the criterion vocabulary and the ceiling come from the session module
# itself, so the CLI's `--until` list cannot drift from what the door accepts. A
# second list of criteria is a fact in two places, and the one that goes stale is
# the one a caller reads.
from openjarvis.sovereign.session import DEFAULT_CEILING, SESSION_CRITERIA

DEFAULT_MODEL = os.environ.get("BIANCA_DEFAULT_MODEL", "qwen3.5:9b")
LEDGER_DIR = daily.ledger_dir()


def _cycle_hint(link) -> str:
    state = link.prepare()["cycle_state"]
    return (
        f"grundmodus={state.get('grundmodus', '?')}, "
        f"stimmung={state.get('stimmung', '?')}, "
        f"fokus={state.get('fokus', '?')} (sonne={state.get('sonne')}, mond={state.get('mond')}, tag={state.get('tag')})"
    )


@click.group(help="Bianca sovereign daily CLI — Harmony-composed, value-governed, audited.")
@click.version_option(version=__version__, prog_name="bianca-sovereign")
def main() -> None:
    """Bianca sovereign daily CLI."""


@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("-m", "--model", default=DEFAULT_MODEL, show_default=True, help="Ollama model.")
@click.option("-e", "--engine", default="ollama", show_default=True, help="Engine key.")
@click.option("-t", "--temperature", type=float, default=0.7, show_default=True)
@click.option("--max-tokens", type=int, default=1024, show_default=True)
@click.option("--json", "as_json", is_flag=True, help="Emit raw JSON envelope.")
@click.option(
    "--lang",
    default=None,
    type=click.Choice(voice.supported()),
    help="Which language she answers in. Her prose only: verdicts, gold values and the "
         "shield's deflection are the law and are never translated.",
)
def ask(query, model, engine, temperature, max_tokens, as_json, lang):
    """Harmony-composed, value-governed question to the Bianca node."""
    query_text = " ".join(query)
    link = default_link()
    ledger = InteractionLogger(str(LEDGER_DIR))

    # 1) Govern BEFORE generating — fail closed on high risk.
    verdict = link.govern(query_text)
    if verdict["verdict"] == "zurueckhalten":
        blocked = verdict.get("risk_hits") or []
        why = (f"Blocked by: {', '.join(blocked)}." if blocked
               else "Risk threshold met.")
        msg = (
            f"[governance] The request was NOT approved (risk={verdict['risk']}, "
            f"alignment={verdict['alignment']}). {why} "
            f"Reframe without the blocked term and the door opens."
        )
        report(ledger, harm=f"denied request: {query_text[:80]}")
        if as_json:
            import json
            click.echo(json.dumps({"governance": verdict, "blocked": True}))
        else:
            click.echo(f"✋ {msg}")
        raise SystemExit(1)

    # 2) Harmony-compose the request (decision -> creativity -> final).
    composed = compose_query(query_text, context="Bianca node on the mycelium net")
    recommended = composed["final"]["next"]

    # 3) System prompt carries the node's soul + live ecosystem state.
    # Set 28: Urasil's real cycle state shapes the form of her answer, read
    # through voice.py's one writer. `_cycle_hint` is the same dict, so the
    # hint and the form can never disagree about which state they describe.
    cycle = link.prepare()["cycle_state"]
    soul = (
        f"{daily.load_soul()}\n"
        f"Your ecosystem's current cycle: {_cycle_hint(link)}. "
        f"Recommended approach for this exchange: {recommended}. "
        f"{voice.tail(lang, cycle)}"
    )
    messages = [
        Message(role=Role.SYSTEM, content=soul),
        Message(role=Role.USER, content=query_text),
    ]

    # 4) Generate through the platform engine (with platform security wrappers).
    try:
        config = load_config()
        resolved = get_engine(config, engine, model=model)
        if resolved is None:
            # audit the silence: a governed, allowed ask that could not be
            # answered must still leave a journal line
            report(ledger, value=f"ask attempted, engine unavailable ({engine})",
                   learning=verdict["verdict"])
            click.echo(click.style("No inference engine available — is Ollama running?", fg="red"))
            raise SystemExit(1)
        eng = resolved[1]
        try:
            from openjarvis.security import setup_security
            protected = setup_security(config, eng, None)
            eng = protected.engine
        except Exception:
            pass  # security wrapper optional; raw engine still governed above
        result = eng.generate(messages, model=model,
                              temperature=temperature, max_tokens=max_tokens)
        reply = result.get("content", "").strip()
    except EngineConnectionError as exc:
        # same principle: an answered-hindered interaction is still an event
        report(ledger, value=f"ask attempted, engine error", learning=verdict["verdict"])
        click.echo(f"{click.style('Engine error:', fg='red')} {exc}")
        raise SystemExit(1)

    # 5) Audit + output.
    # The reply is generated speech — set 7 gave the trialog this eye; the
    # node's own primary voice gets it too. READ, don't gate: the record says
    # what the governor thought of the words actually delivered.
    reply_v = link.govern(reply)
    def _display_line(value) -> str:
        # compose sections are heterogeneous (list or str) — render both sanely
        if isinstance(value, list):
            return " ".join(value)
        return value or "—"

    report(ledger, value=f"ask answered ({len(reply)} chars)",
           learning=f"{verdict['verdict']}; reply={reply_v['verdict']}")
    if as_json:
        import json
        click.echo(json.dumps({
            "governance": verdict,
            "reply_governance": {
                "verdict": reply_v["verdict"],
                "risk_hits": reply_v.get("risk_hits") or [],
                "oracle": reply_v.get("oracle"),
            },
            "decision": composed["decision"],
            "creativity": composed["creativity"],
            "prediction": composed["prediction"],
            "validation": composed["validation"],
            "explanation": composed["explanation"],
            "reply": reply,
        }))
    else:
        click.echo()
        click.echo("── Harmony framing ─────────────────────────────")
        click.echo(f"　decision : {composed['decision'][0]}")
        click.echo(f"　maybe    : {composed['decision'][1] if len(composed['decision']) > 1 else '—'}")
        click.echo(f"　verify   : {_display_line(composed['validation'])}")
        click.echo(f"　why      : {_display_line(composed['explanation'])}")
        click.echo(f"　verdict  : {verdict['verdict']} (align={verdict['alignment']}, risk={verdict['risk']})")
        click.echo(f"　gold     : {', '.join(verdict.get('gold_hits') or []) or '—'}")
        click.echo(f"　risk-term: {', '.join(verdict.get('risk_hits') or []) or '—'}")
        click.echo(f"　gold src : {verdict.get('gold_source')}")
        _ov = (verdict.get("oracle") or {}).get("vote")
        click.echo(f"　2nd eye  : {_ov} (advisory) — the ValueGovernor alone "
                   f"holds the door")
        click.echo("── Bianca says ─────────────────────────────────")
        click.echo(reply)
        if reply_v["verdict"] == "zurueckhalten":
            terms = ", ".join(reply_v.get("risk_hits") or []) or "risk threshold"
            click.echo(click.style(f"　[governance] reply off-limit — terms: {terms} · "
                                   f"eye: {reply_v.get('oracle', {}).get('vote')} "
                                   f"(recorded, not censored)", fg="red"))


@main.command()
@click.argument("text", nargs=-1, required=True)
def govern(text):
    """Show the ValueGovernor verdict for a request (no LLM needed)."""
    link = default_link()
    verdict = link.govern(" ".join(text))
    gold = ", ".join(verdict.get("gold_hits") or []) or "—"
    risk = ", ".join(verdict.get("risk_hits") or []) or "—"
    click.echo(f"verdict={verdict['verdict']}  alignment={verdict['alignment']}  "
               f"risk={verdict['risk']}  gold_manifest={'yes' if verdict['gold_values_loaded'] else 'no'}")
    click.echo(f"gold hits: {gold}")
    click.echo(f"risk hits: {risk}")
    click.echo(f"gold src : {verdict['gold_source']}")
    oracle = verdict.get("oracle") or {}
    if oracle:
        grounds = f"; grounds: {', '.join(oracle.get('grounds') or [])}" \
            if oracle.get("grounds") else ""
        click.echo(f"2nd eye  : {oracle.get('vote')} (advisory{grounds}) — "
                   f"the ValueGovernor alone holds the door")
    # the gate's own status must speak its verdict: a zurueckhalten exits
    # non-zero, so `govern "Loesche X" && …` can never proceed (fail-closed
    # composition at the process level, mirroring /v1/ask's 403)
    if verdict["verdict"] == "zurueckhalten":
        raise SystemExit(1)


@main.command()
@click.argument("text", nargs=-1, required=True)
def oracle(text):
    """The second eye's own door: the advisory vote alone — it has no key.

    Unlike ``govern`` (which exits non-zero on a denial), this command
    ALWAYS exits 0: an advisory eye may never deny — not even at the
    process level. ``oracle … && …`` is deliberately NOT a gate.
    """
    link = default_link()
    verdict = link.govern(" ".join(text))
    o = verdict.get("oracle") or {}
    grounds = ", ".join(o.get("grounds") or []) or "—"
    click.echo(f"2nd eye  : {o.get('vote')} · resonance {o.get('resonance')} "
               f"· grounds: {grounds}")
    click.echo("advisory : yes — this vote opens nothing and closes nothing")
    click.echo(f"boundary : the ValueGovernor alone holds the door "
               f"(door says: {verdict['verdict']})")
    raise SystemExit(0)


@main.command()
def context():
    """Show the node's live ecosystem context."""
    link = default_link()
    ctx = link.prepare()
    click.echo(f"capability : {ctx['capability']['mode']} (features={ctx['capability']['feature_files']})")
    click.echo(f"cycle      : {_cycle_hint(link)}")
    click.echo(f"gold.txt   : {'loaded' if ctx['gold_manifest'] else 'MISSING'}")
    sc = daily.node_self_check()
    click.echo(f"voice      : {sc['voice']}")
    click.echo(f"engine     : {sc['engine']} ({sc['engine_why']})")
    o = (ctx.get("oracle") or {})
    click.echo(f"2nd eye    : {'on' if o.get('on') else '?'} (advisory only — "
               f"the ValueGovernor alone holds the door)")
    click.echo(f"contract   : {'PASS' if sc['contract_holds'] else 'FAIL'} "
               f"({sc['verified']} hash-verified, {sc['untraceable']} untraceable, "
               f"{sc['failures']} failures) via idle verify")


@main.command("ledg")
@click.option("--tail", type=int, default=None, help="Show the most recent N events.")
def ledg(tail):
    """Show recent Interaction Ledger events."""
    files = sorted(LEDGER_DIR.glob("interaction_*.md"))
    if not files:
        click.echo("(ledger empty)")
        return
    latest = files[-1]
    click.echo(daily.render_ledger(latest.read_text(encoding="utf-8"), tail))


@main.command()
@click.argument("stage", type=click.Choice(list(STAGES)))
@click.argument("scope")
def stage(stage, scope):
    """Open a Harmony stage and print its gate question."""
    h = Harmony()
    result = h.begin_stage(stage, scope)
    ledger = InteractionLogger(str(LEDGER_DIR))
    if not result["allowed"]:
        click.echo(click.style(result["reason"], fg="red"))
        report(ledger, value=f"stage {stage} ({scope}) held at the WIP gate",
               learning="wip-limit")
        raise SystemExit(1)
    click.echo(f"stage       : {stage}")
    click.echo(f"gate Q      : {result['gate_question']}")
    click.echo(f"finish      : {result['finish_pledge']}")
    # the pledge must not evaporate: every other door audits, so the operator's
    # stated proof of value lands in the ledger where recall/ledg can find it
    report(ledger, value=f"stage {stage} ({scope}) opened",
           learning=f"pledge: {result['finish_pledge']}")
    # AND the pledge must reach the closure chain: previous_day_next reads
    # briefing '— next:' lines written by `today` only — a stage opened in the
    # evening would be invisible to tomorrow's 'closed?' seam. One line here
    # elects the newest honored datum into the loop.
    daily.briefing_note(f"stage {stage} ({scope}) opened — next: {result['finish_pledge']}")


@main.command()
@click.argument("domain", required=False, default="bianca")
def levels(domain):
    """Five Levels of Finishing (Book of Infinity) — where is it breathing now?"""
    a = infinity.assess(domain)
    click.echo(f"levels      : where '{a['domain']}' breathes right now")
    if not infinity.source_available():
        click.echo("  (source not found — this table is memory, not the book)")
    for idx, level in enumerate(infinity.LEVELS, start=1):
        here = "*" if idx == a["level"] else " "
        click.echo(f" {here} L{idx} {level['name']:<22} {level['voice']}")
    click.echo(f"   now       : L{a['level']} — {a['note']}")
    click.echo(f"   source    : {infinity.infinity_path()}")
    click.echo("   principle : nothing finishes because nothing stops moving")


# The three souls moved OUT of this file into sovereign.trialog — ONE writer,
# so the command line and the /v1/trialog door can never disagree about who
# speaks or how a turn is governed. The alias keeps this module's public
# name stable for anything that imported it.
TRIALOG_PERSONAS = trialog_mod.PERSONAS


@main.command()
@click.argument("topic", nargs=-1, required=False)
@click.option("-m", "--model", default=DEFAULT_MODEL, show_default=True, help="Ollama model for the voices.")
@click.option("--rounds", type=int, default=2, show_default=True, help="Full turns per voice.")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON transcript document.")
def trialog(topic, model, rounds, as_json):
    """Let Jarvis, Bianca and Urasil_light keep each other company.

    A thin renderer over ``sovereign.trialog.run_trialog`` -- the same
    writer the ``/v1/trialog`` door uses, so a deliberation cannot mean one
    thing on the command line and another on the face.
    """
    topic = " ".join(topic) or trialog_mod.default_topic()
    link = default_link()

    config = load_config()
    resolved = get_engine(config, "ollama", model=model)
    if resolved is None:
        click.echo(click.style("No inference engine available - is Ollama running?", fg="red"))
        raise SystemExit(1)
    engine = resolved[1]

    out = trialog_mod.run_trialog(
        link, topic=topic, engine=engine, model=model, rounds=rounds)

    if not as_json:
        for turn in out["turns"]:
            click.echo("\n=== {v} === round {r}/{n}".format(
                v=turn["voice"], r=turn["round"], n=out["rounds"]))
            click.echo(turn["text"])
            if turn["verdict"] == "zurueckhalten":
                click.echo(click.style(
                    "  [governance: zurueckhalten - terms: {t} - eye: {e}]".format(
                        t=", ".join(turn["risk_hits"]),
                        e=(turn["oracle"] or {}).get("vote")), fg="red"))
        click.echo("\n. {n} round(s) complete . {d} off-limit . eye-warned {w} .".format(
            n=out["rounds"], d=out["governance"]["off_limit"], w=out["eye_warned"]))

    trialog_mod.record_trialog(out, LEDGER_DIR, daily.notes_dir())
    if as_json:
        click.echo(daily.trialog_json(out["topic"], out["model"],
                                     out["rounds"], out["transcript"]))




def _narrate(briefing: dict, model: str) -> str:
    """One warm paragraph about today, or '' if the engine is unavailable."""
    try:
        config = load_config()
        resolved = get_engine(config, "ollama", model=model)
        eng = resolved[1] if resolved else None
        if not eng:
            return ""
        msgs = [Message(role=Role.SYSTEM, content=daily.load_soul()),
                Message(role=Role.USER, content=(
                    f"Narrate today's briefing in one warm paragraph (max 60 words): "
                    f"cycle={briefing['cycle']}, ledger_events={briefing['ledger_total']}, "
                    f"memory_docs={briefing['memory']['documents']}, "
                    f"idle={'running' if briefing['idle']['running'] else 'stopped'}."))]
        result = eng.generate(msgs, model=model, temperature=0.8, max_tokens=160)
        return result.get("content", "").strip()
    except Exception:
        return ""


def _briefing_json(briefing: dict, narration: str = "") -> str:
    """Serialize the briefing for machine consumers; the narration joins it
    when present, so ``today --narrate --json`` speaks in one document."""
    import json
    out = dict(briefing)
    if narration:
        out["narration"] = narration
    return json.dumps(out, default=str, ensure_ascii=False)


@main.command()
@click.option("--narrate", "-n", is_flag=True, help="Add a short LLM narration of the day (needs Ollama).")
@click.option("-m", "--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def today(narrate, model, as_json):
    """The daily briefing ritual — cycle, ledger, memory, idle, options."""
    link = default_link()
    ledger = InteractionLogger(str(LEDGER_DIR))
    b = daily.build_briefing(link, LEDGER_DIR)
    if as_json:
        narration = _narrate(b, model) if narrate else ""
        click.echo(_briefing_json(b, narration))
        return
    click.echo(f"☀ {b['date']} — Bianca daily briefing")
    click.echo(f"　cycle     : {b['cycle'].get('grundmodus')} / {b['cycle'].get('stimmung')} / "
               f"{b['cycle'].get('fokus')}  (sonne={b['cycle'].get('sonne')}, mond={b['cycle'].get('mond')}, tag={b['cycle'].get('tag')})")
    click.echo(f"　gold.txt  : {'loaded' if b['gold_loaded'] else 'MISSING'}")
    click.echo(f"　ledger    : {b['ledger_total']} event(s) today {dict(b['ledger_today']) if b['ledger_today'] else ''}")
    click.echo(f"　refused   : {b['refusals']} request(s) turned away by governance")
    click.echo(f"　memory    : {b['memory']['documents']} doc(s)")
    click.echo(f"　idle-op   : {'running (pid ' + str(b['idle']['pid']) + ')' if b['idle']['running'] else 'stopped'}")
    if b["engine"] == "up":
        click.echo(f"　engine    : {b['engine']} ({b['engine_why']})")
    else:
        click.echo(f"　engine    : {click.style(b['engine'], fg='red')} — {b['engine_why']}")
    esc = b["escalation"]
    if esc["verdict"] == "pause":
        msg = f"{esc['streak']} unanswered asks in a row"
        click.echo(f"　escalate  : {click.style(msg, fg='red')} — {esc['guidance']}")
    elif esc["verdict"] == "advisory":
        click.echo(f"　escalate  : {esc['streak']} unanswered ask — {esc['guidance']}")
    if b.get("recent"):
        click.echo("　recent    :")
        for r in b["recent"]:
            click.echo(f"　　 {r['when']} [{r['type']}] {r['message']}")
    click.echo("　options   :")
    for opt in b["options"]:
        click.echo(f"　　 {opt}")
    click.echo(f"　next      : {b['next']}")
    if b.get("previous_next"):
        click.echo(f"　closed?   : yesterday's next — \"{b['previous_next']}\"  (confirm via `remember 'achieved: …'`)")
    if narrate:
        narration = _narrate(b, model)
        if narration:
            click.echo(f"\n── narration ──\n{narration}")
        else:
            click.echo("(narration skipped: engine unavailable)")
    report(ledger, value="daily briefing shown", learning=b["cycle"].get("grundmodus", "?"))
    # keep a standing, committable summary — in its own file, so the ritual
    # never crowds the decision memory (briefing_*.md vs notes_*.md):
    daily.briefing_note(f"Daily briefing — cycle {b['cycle'].get('grundmodus')}/{b['cycle'].get('stimmung')}/{b['cycle'].get('fokus')} — next: {b['next']}")


@main.command()
@click.argument("note", nargs=-1, required=True)
def remember(note):
    """Write a datum to the node's note memory."""
    text = " ".join(note)
    path = daily.remember(text)
    click.echo(f"remembered → {path}")
    # The loop's CLOSING act is a governance act: stage openings are audited,
    # so a promise closed must reach the ledger too — not vanish as prose.
    # Only closure-flavoured notes get the receipt; ordinary remembering stays
    # prose-only (the set-3 separation: decisions → notes, events → ledger).
    head = text.lower().strip()
    if head.startswith("achieved") or head.startswith("closed") or "achieved:" in head:
        ledger = InteractionLogger(str(LEDGER_DIR))
        report(ledger, value=f"promise closed: {text[:80]}", learning="closure")


@main.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--limit", type=int, default=5, show_default=True)
def recall(query, limit):
    """Search note memory and the ledger for a topic."""
    results = daily.recall(" ".join(query), ledger_dir=LEDGER_DIR, limit=limit)
    if not results:
        click.echo("(nothing found)")
        return
    for r in results:
        click.echo(f"{r['source']}:{r['line']}  {r['text']}")


@main.group("idle", help="The idle-contract operator — idle compute becomes verifiable work units.")
def idle_group():
    pass


@idle_group.command("probe")
def idle_probe():
    """Show current CPU load and whether the box counts as idle."""
    from openjarvis.sovereign.idle import cpu_percent, decide_idle, THRESHOLD, MIN_STREAK
    cpu = cpu_percent()
    click.echo(f"cpu={cpu:.1f}%  threshold={THRESHOLD}%  min_streak={MIN_STREAK}  idle={decide_idle(cpu, streak=MIN_STREAK - 1)}")


@idle_group.command("start")
def idle_start():
    """Start the idle-operator daemon (background, pidfile-managed)."""
    import subprocess
    import sys
    from openjarvis.sovereign.idle import is_alive, read_pid
    pid = read_pid()
    if pid and is_alive(pid):
        click.echo(f"[i] already running (pid {pid})")
        return
    log_dir = Path.home() / ".openjarvis" / "bianca"
    log_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "openjarvis.sovereign.idle", str(LEDGER_DIR)]
    with open(log_dir / "idle.log", "a") as logf:
        proc = subprocess.Popen(cmd, start_new_session=True, stdout=logf, stderr=logf)
    click.echo(f"idle operator started (pid {proc.pid}) → log {log_dir / 'idle.log'}")


@idle_group.command("status")
def idle_status():
    """Show operator state and today's work units (audited-verified)."""
    st = daily.idle_status()
    click.echo(f"running   : {'yes (pid ' + str(st['pid']) + ')' if st['running'] else 'no'}")
    click.echo(f"work units: {st['units_today']} today (ledger-audited: {st['units_audited']})")


@idle_group.command("verify")
def idle_verify():
    """Prove the contract end-to-end — every unit file named by an audit whose content hash matches."""
    from openjarvis.sovereign.idle import verify_units
    st = verify_units()
    click.echo(f"verified : {st['verified']} (hash-matched receipts)")
    click.echo(f"legacy   : {st['missing_audit']} untraceable file(s) ↔ {st['legacy_events']} count-only audit(s) (pre-hash era)")
    # Set 29: two orphan lists and never their sum. A reconciled orphan is one
    # the record admits it cannot produce, with its hash kept — not one whose
    # file was seen and matched, which is what the line above says.
    click.echo(f"orphans  : {len(st['orphan_audits_unreconciled'])} unreconciled"
               f" + {len(st['orphan_audits_reconciled'])} reconciled (admitted, hash kept)")
    if st['stale_reconciliations']:
        click.echo(f"           ({len(st['stale_reconciliations'])} stale reconciliation(s) — the file is back: "
                   f"{', '.join(st['stale_reconciliations'])})")
    click.echo(f"failures : {st['failures']} = {st['tampered']} tampered"
               f" + {len(st['orphan_audits_unreconciled'])} unreconciled orphans + unreconciled")
    click.echo(f"contract : {'PASS — chain intact' if st['contract_holds'] else 'FAIL — the chain has a break'}")


@idle_group.command("garden")
def idle_garden():
    """What limits the garden — measured now, by location in a sibling repository.

    Set 35 retracted this command's *conclusion*, not its instrument: the kernel
    grows (17-18 new Clusters at step 1; 90 → 125/126/126 with the set-36 doors
    and the set-38 wave crest; set 37's gate factor 0.6 was taken back by the
    owner) and holds colour for 1500 steps.
    """
    from openjarvis.sovereign.idle import garden_diagnosis, garden_orders_prose
    g = garden_diagnosis()
    if not g.get("measured"):
        click.echo(f"[!] not measured: {g.get('reason')}")
    else:
        click.echo(f"step {g.get('step')} (cells {g.get('cells')})"
                   f"  drift={g.get('drift')}  threshold={g.get('drift_threshold')}")
        # Set 35b: this line interpolated the raw value, and at a mean drift of
        # exactly 0 the value is None — measured on the live garden as
        # "drift is None orders of magnitude below the rule". The sentence now
        # comes from the one writer of the reason.
        click.echo(garden_orders_prose(g)
                   + f"  keime={g.get('keime')}  spread={g.get('spread')}")
        click.echo(f"born_converged={g.get('born_converged')}"
                   f"  converged_at={g.get('converged_at')}  flat_at={g.get('flat_at')}")
        click.echo(f"can evolve: {g.get('can_evolve')}"
                   f"   ← Mittel-Drift; irreführend")
        if g.get("convergence_disputed"):
            click.echo(
                f"  🌱 WIDERSPRUCH, beide Arme wahr: gewachsen ab Schritt "
                f"{g.get('grew_at')}, +{g.get('new_clusters')} Cluster "
                f"({g.get('cluster_start')} -> {g.get('cluster')}), "
                f"born_converged={g.get('born_converged')}")
            click.echo(
                "  Der Mittelarm ist nein, der Clusterarm ja. Ein Mittel ist "
                "keine Zahl: Fortpflanzung braucht 11 Saaten gleichzeitig.")
        else:
            click.echo(
                f"  gewachsen: {g.get('grew')} "
                f"(+{g.get('new_clusters')} Cluster)")
        click.echo(f"frame: {g.get('frame_bytes')} bytes, one fixed path, overwritten in place")
    click.echo("")
    click.echo("what limits it — locations in ALF/Colorverse, read not retyped:")
    for rule in g.get("rule", ()):
        click.echo(f"  {rule['where']:<34} {rule['what']}")


@idle_group.command("reconcile")
@click.argument("stamp")
@click.argument("reason", nargs=-1, required=True)
def idle_reconcile(stamp, reason):
    """Admit that an orphan audit's file is unrecoverable. Never deletes anything.

    The unit file stays gone and the audit stays in the ledger; what is added is
    a dated, reasoned statement. The hash it stands in for is kept, so a file
    that comes back with different bytes still reads `tampered`.
    """
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.idle import reconcile_orphan
    from openjarvis.sovereign.logger import InteractionLogger
    text = " ".join(reason).strip()
    entry = reconcile_orphan(stamp, text, InteractionLogger(_ld()), _ld())
    click.echo(f"[i] reconciled unit={entry['stamp']} sha={entry['sha']}")
    click.echo(f"    reason        : {entry['reason']}")
    click.echo(f"    units dir     : {entry['units_dir']} (present: {entry['dir_present']})")
    click.echo(f"    the audit and the file are both untouched.")
    click.echo(f"    run `idle verify` to see the contract.")


@idle_group.command("stop")
def idle_stop():
    """Stop the idle-operator daemon gracefully."""
    import signal
    import time
    from openjarvis.sovereign.idle import is_alive, read_pid, remove_pidfile
    pid = read_pid()
    if not pid or not is_alive(pid):
        click.echo("[i] not running")
        remove_pidfile()
        return
    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not is_alive(pid):
            break
        time.sleep(0.1)
    click.echo(f"idle operator stopped (pid {pid})")
    remove_pidfile()


# ── the working session (set 30) ────────────────────────────────────────────
#
# Six commands over the same facts the doors carry. The CLI does not govern and
# it does not decide: it starts a session, lists them, speaks into one, accepts
# a proposal and stops one — and every verdict on the way is the gate's, read
# from the session's own record. A command that could close a session by itself
# would be a seventh judge, and set 29 measured that a different model never is
# one.

@main.group("session")
def session_group():
    """The working session: a team that stays until the project is finished."""


@session_group.command("start")
@click.argument("topic")
@click.option("--goal", required=True, help="The aim, in your words. Mandatory.")
@click.option("--until", "stop_when", default="",
              type=click.Choice(list(SESSION_CRITERIA), case_sensitive=True),
              help="How it ends. A word outside this list is refused at the door.")
@click.option("--ceiling", default=DEFAULT_CEILING, show_default=True, type=int,
              help="Hard ceiling in MODEL CALLS. Reaching it is not success.")
@click.option("--model", default=None, help="One model for all three voices.")
@click.option("--voice", "voices", multiple=True, metavar="NAME=MODEL",
              help="A model for one voice, repeatable. e.g. --voice Urasil_light=qwen3.5:9b")
@click.option("--no-start", is_flag=True,
              help="Create the record but do not start the team.")
def session_start(topic, goal, stop_when, ceiling, model, voices, no_start):
    """Start a session. The topic and the goal are judged before anything exists."""
    from openjarvis.sovereign.session import create, refused_reason, spawn
    from openjarvis.sovereign.daily import ledger_dir as _ld, default_model

    models = {}
    for pair in voices:
        name, _, m = pair.partition("=")
        if not _ or not m.strip():
            raise click.BadParameter(f"--voice needs NAME=MODEL, got '{pair}'")
        models[name.strip()] = m.strip()

    why = refused_reason(topic, goal, stop_when)
    if why:
        raise click.BadParameter(why)

    link = default_link()
    for label, text in (("topic", topic), ("goal", goal)):
        v = link.govern(text)
        if v["verdict"] == "zurueckhalten":
            click.echo(f"[!] the {label} was held — risk={v['risk']} "
                       f"alignment={v['alignment']}, verdict {v['verdict']}")
            # `missing` is a LIST (link._missing returns one). Printing the dict
            # showed a Python repr — brackets, quotes, the lot — which is a
            # rendering bug in this command, not in the sentence. The sentence is
            # the law and it is joined here with " · ", the same separator the
            # face uses in `missingLine()`. Those two joins cannot share code:
            # the face is a zero-build HTML file with no module system, so a
            # claim about "one writer of the join" is not one this repository can
            # honestly make, and it makes none.
            gaps = [str(g) for g in (v.get("missing") or [])]
            if gaps:
                click.echo("    es fehlt: " + " · ".join(gaps))
            click.echo("    nothing was created, and no engine time was spent.")
            raise SystemExit(1)

    state = create(_ld(), topic, goal, stop_when, ceiling=ceiling,
                   model=model or default_model(), models=models or None)
    pid = None if no_start else spawn(_ld(), state["id"])
    click.echo(f"session {state['id']}  until {stop_when}  ceiling {ceiling} calls")
    for voice, m in state["models"].items():
        click.echo(f"    {voice:14s} {m}")
    click.echo(f"    running: {'yes (pid ' + str(pid) + ')' if pid else 'no — the record exists, the team does not run'}")
    click.echo(f"    say to it  : bianca-sovereign session say {state['id']} '…'")
    click.echo(f"    stop it    : bianca-sovereign session stop {state['id']} 'reason'")


@session_group.command("list")
def session_list():
    """Every session, under its topic."""
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.session import list_sessions
    out = list_sessions(_ld())
    if not out["sessions"]:
        click.echo("[i] no sessions yet.")
        return
    for topic, rows in out["by_topic"].items():
        click.echo(f"  {topic}")
        for row in rows:
            click.echo(f"    {row['id']}  {row['status']:16} "
                       f"{row['calls']}/{row['ceiling']} calls"
                       + ("  [at ceiling]" if row["at_ceiling"] else "")
                       + (f"  (pid {row['running']})" if row["running"] else ""))
    click.echo(f"  {len(out['sessions'])} sessions under {out['topics']} topics")


@session_group.command("show")
@click.argument("session_id")
def session_show(session_id):
    """One session: its state, its turns with evidence, and what it has decided."""
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.session import read_session
    out = read_session(_ld(), session_id)
    if out is None:
        click.echo(f"[!] no such session: {session_id}")
        raise SystemExit(1)
    st, mem = out["state"], out["memory"]
    click.echo(f"{st['id']}  [{st['status']}]  until {st['stop_when']}")
    click.echo(f"  topic     : {st['topic']}")
    click.echo(f"  goal      : {st['goal']}")
    click.echo(f"  calls     : {mem['calls']}/{st['ceiling']}"
               + ("  AT CEILING — the goal was not met" if mem['calls'] >= st['ceiling'] else ""))
    if st.get("closed_because"):
        click.echo(f"  closed    : {st['closed_because']}  (by {st.get('closed_by')})")
    for voice, verdicts in mem["per_voice_verdicts"].items():
        carried = ", ".join(mem["gold_carried"].get(voice, []))
        click.echo(f"  {voice:14s} {' '.join(verdicts)}"
                   + (f"  carried {carried}" if carried else ""))
    if mem["owner_turns"]:
        click.echo(f"  owner     : {mem['owner_turns']} turn(s), "
                   f"{mem['held_owner_turns']} held")
    for p in out["proposals"]:
        click.echo(f"  proposal  : round {p.get('round')} "
                   f"{'[closed by owner]' if p.get('closed') else '[open]'}")
        click.echo(f"              {p.get('trigger')}")
    if out["inbox"]:
        click.echo(f"  inbox     : {out['inbox']} waiting")
    click.echo(f"  memory carries : {mem['carries']}")
    click.echo(f"  cannot record  : {mem['cannot_record']}")


@session_group.command("say")
@click.argument("session_id")
@click.argument("text", nargs=-1, required=True)
def session_say(session_id, text):
    """Speak into a running session. Judged like everything else — no exemption."""
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.session import is_running, read_state, say, spawn
    raw = " ".join(text).strip()
    st = read_state(_ld(), session_id)
    if st is None:
        click.echo(f"[!] no such session: {session_id}")
        raise SystemExit(1)
    link = default_link()
    v = link.govern(raw)
    if v["verdict"] == "zurueckhalten":
        click.echo(f"[!] held — risk={v['risk']} alignment={v['alignment']}")
        gaps = [str(g) for g in (v.get("missing") or [])]
        if gaps:
            click.echo("    es fehlt: " + " · ".join(gaps))
        click.echo("    the turn was not taken. The owner is not exempt from the gate.")
        raise SystemExit(1)
    say(_ld(), session_id, raw)
    resumed = ""
    if not is_running(session_id) and st.get("status") in (
            "new", "running", "awaiting_owner", "ceiling_reached"):
        pid = spawn(_ld(), session_id)
        resumed = f"  the team was started again (pid {pid})" if pid else ""
    click.echo(f"[i] queued for {session_id} (verdict {v['verdict']}, "
               f"gold {','.join(v.get('gold_hits') or []) or '—'})")
    click.echo("    the team reads it in the next round it takes — this is not an answer.")
    if resumed:
        click.echo(resumed)


@session_group.command("accept")
@click.argument("session_id")
def session_accept(session_id):
    """Take the team's proposal. The only close that a person's word alone makes."""
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.session import (append_proposal, close, is_running,
                                              read_proposals, read_state)
    st = read_state(_ld(), session_id)
    if st is None:
        click.echo(f"[!] no such session: {session_id}")
        raise SystemExit(1)
    open_ones = [p for p in read_proposals(_ld(), session_id) if not p.get("closed")]
    if not open_ones:
        click.echo("[!] the team has proposed no close, so there is nothing to accept.")
        click.echo("    it proposes only when the gate held nothing and warned nobody")
        click.echo("    in the last round every voice spoke.")
        raise SystemExit(1)
    pid = is_running(session_id)
    if pid:
        import signal
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pid = None
    out = close(_ld(), session_id, "complete",
                f"the owner accepted the proposal of round {open_ones[-1].get('round')}",
                by="owner")
    append_proposal(_ld(), session_id, {**open_ones[-1], "closed": True,
                                        "closed_by": "owner"})
    click.echo(f"[i] {session_id} closed: {out['closed_because']}")
    click.echo(f"    written by '{out['closed_by']}' — a process exit does not overwrite it.")


@session_group.command("stop")
@click.argument("session_id")
@click.argument("reason", nargs=-1)
def session_stop(session_id, reason):
    """Stop a session, and say why. The reason is kept in the record."""
    from openjarvis.sovereign.daily import ledger_dir as _ld
    from openjarvis.sovereign.session import halt
    text = " ".join(reason).strip() or "stopped by the owner"
    out = halt(session_id, text, _ld())
    if out.get("pending"):
        click.echo(f"[i] asked {session_id} to stop — the record is not final yet.")
        click.echo(f"    {out.get('stops_when')}")
        click.echo(f"    until it is, `status` still reads {out.get('status')!r}. That is not a lie,")
        click.echo("    it is the truth: nobody has written a close.")
    else:
        click.echo(f"[i] {session_id} stopped: {out.get('closed_because')}")


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Bind address — keep localhost for sovereignty.")
@click.option("--port", default=8712, show_default=True, type=int)
def serve(host, port):
    """Serve the governed API (local door for the Web UI and integrations)."""
    import uvicorn
    from openjarvis.sovereign.api import create_app
    app = create_app(ledger_dir=str(LEDGER_DIR))
    click.echo(f"Bianca governed API → http://{host}:{port}  (bound to {host})")
    uvicorn.run(app, host=host, port=port, log_level="warning")


def _open_browser(url: str) -> None:
    """Ask the default browser for `url`. One place, so `ui` and `spiel` cannot
    grow two different kill-switches — `BIANCA_UI_OPEN=0` closes both."""
    if os.environ.get("BIANCA_UI_OPEN") == "0":
        click.echo("(BIANCA_UI_OPEN=0 — not opening a browser)")
        return
    try:
        import subprocess
        subprocess.Popen([os.environ.get("BIANCA_UI_BROWSER", "xdg-open"), url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        click.echo("(asked the default browser to open the face)")
    except Exception as exc:  # headless is fine — the URL is printed above
        click.echo(f"(could not open a browser: {type(exc).__name__})")


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Bind address — keep localhost for sovereignty.")
@click.option("--port", default=8712, show_default=True, type=int)
def ui(host, port):
    """Open the governed Web UI (the node's face) in the default browser."""
    url = f"http://{host}:{port}/"
    click.echo(f"Bianca's face: {url}")
    _open_browser(url)


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Bind address — keep localhost for sovereignty.")
@click.option("--port", default=8712, show_default=True, type=int)
def spiel(host, port):
    """Open the adventure (Der Einzug): four figures, four real doors.

    Set 31. The owner's premise is that reclaiming a machine should feel like
    an adventure rather than a checklist, and the rule that keeps that honest
    is that every quest on the field IS a door of this node. The game invents
    nothing: a quest it cannot win shows the blocker instead of a victory, and
    the idle contract that FAILs today fails on screen too.
    """
    url = f"http://{host}:{port}/#trialog:spiel"
    click.echo("Der Einzug — zurück auf deine eigene Maschine.")
    click.echo("  🧭 Du             · Der Knoten   · GET /health")
    click.echo("  ⚙  Jarvis        · Der Motor    · GET /v1/models")
    click.echo("  🌗 Urasil_light  · Die Welt     · GET /v1/garden")
    click.echo("  🛡  Bianca         · Der Vertrag  · GET /idle/contract")
    click.echo(f"Das Abenteuer: {url}")
    _open_browser(url)


@main.group()
def hub():
    """Inspect the self-hosted hub surface — manifest, curated public/ and
    spore ledger — and announce the reachable URL (localhost by default;
    open the net consciously with --host/--port)."""


@hub.command("manifest")
def hub_manifest_cmd():
    """Print the node's public manifest as JSON (never fails)."""
    import json
    from openjarvis.sovereign import hub as hub_mod
    click.echo(json.dumps(hub_mod.manifest(), ensure_ascii=False, indent=2))


@hub.command("public")
def hub_public_cmd():
    """List the curated public surface (secrets hard-excluded)."""
    from openjarvis.sovereign import hub as hub_mod
    files = hub_mod.public_list()
    click.echo("public files:")
    for f in files:
        click.echo(f"  {f}")
    click.echo(f"({len(files)} files — curated, sensitive names never served)")


@hub.command("spores")
@click.option("--limit", default=10, show_default=True, type=int)
def hub_spores_cmd(limit):
    """List accepted spores, newest first — the node's curated ledger."""
    from openjarvis.sovereign import hub as hub_mod
    spores = hub_mod.list_spores(limit=limit)
    click.echo(f"spore ledger ({len(spores)} shown, newest first):")
    for s in spores:
        click.echo(f"  {s['stamp']}  {s['verdict']:12s}  "
                   f"{s['source'][:18]:18s}  {s['text'][:40]}")
    if not spores:
        click.echo("  (none yet — the first foreign spore has not arrived)")


@hub.command("announce")
@click.option("--host", default="127.0.0.1", show_default=True,
              help="Bind address — keep localhost unless a peer needs you now.")
@click.option("--port", default=8712, show_default=True, type=int)
def hub_announce_cmd(host, port):
    """Print the URL peers can reach — localhost by default. The node only
    opens doors it chooses: bind elsewhere consciously, per session."""
    click.echo(f"hub announce: http://{host}:{port}/hub/manifest")
    click.echo(f"spores enter via: POST http://{host}:{port}/hub/spore")
    click.echo(f"curated surface: http://{host}:{port}/hub/public")
    if host in ("0.0.0.0", "::"):
        click.echo("(bound everywhere — this exposes the hub on the network;")
        click.echo(" use 127.0.0.1 unless a peer needs to reach you right now)")


@main.command("agent-ask")
@click.argument("prompt", nargs=-1, required=True)
@click.option("-m", "--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--max-turns", default=6, show_default=True, type=int)
def agent_ask(prompt, model, max_turns):
    """Run the governed tool-agent — the platform's own OrchestratorAgent
    with the before_tool_call governance hook (fail-closed)."""
    from openjarvis.sovereign.agent import governed_agent_ask
    query = " ".join(prompt)
    click.echo(f"── governed agent · {model} · max {max_turns} turns ──")
    try:
        out = governed_agent_ask(query, model=model, max_turns=max_turns,
                                 ledger_dir=LEDGER_DIR)
    except Exception as exc:
        raise click.ClickException(str(exc))
    click.echo(out["content"].strip())
    click.echo("")
    click.echo(f"── run · {out['turns']} turns · {len(out['tool_results'])} tool call(s) "
               f"· {len(out['state'].denied)} denied ──")
    # Set 18: a tool judgement is a verdict, so it is read like one — the
    # stems that tripped it and the second eye travel with it. "denied" on
    # its own would be the outcome-without-evidence defect.
    for check in out["state"].checks:
        v = check["verdict"]
        if isinstance(v, dict):
            flag = "⛔" if v.get("verdict") == "zurueckhalten" else "✓"
            stems = ", ".join(v.get("risk_hits") or []) or "—"
            eye = (v.get("oracle") or {}).get("vote", "—")
            click.echo(f"  {flag} {check['tool']} → {v.get('verdict')}"
                       f"  · stems: {stems}  · eye: {eye} (advisory)")
        else:  # pragma: no cover — a pre-set-18 state, kept readable
            click.echo(f"  ✓ {check['tool']} → {v}")


if __name__ == "__main__":
    main()