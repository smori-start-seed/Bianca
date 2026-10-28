"""api — the governed front door of the node.

A small FastAPI surface for clients and integrations (Web UI, cron digest,
monitoring). Bound to 127.0.0.1 by default — the node only opens doors it
chooses to open. Every path is governed or read-only:

    GET  /               the node's face — local-only, no-build Web UI
    GET  /health         soul present? gold loaded? (never fails)
    GET  /context        capability / cycle / gold (read-only)
    GET  /govern         ValueGovernor verdict for a text (no LLM)
    GET  /today          deterministic daily briefing
    GET  /idle/status    idle-operator state
    GET  /urasil         Urasil_light: the live cycle + the Five Levels
    POST /v1/ask         Harmony-composed, governed, engine-backed reply
    POST /v1/chat        multi-turn; every user turn governed before generation
    GET  /v1/agent/tools the governed agent's tool inventory (derived, never stale)
    POST /v1/agent       the governed tool-agent; every tool call judged first
    POST /v1/trialog     Jarvis x Bianca x Urasil_light; every utterance governed
    GET  /v1/trialogs    persisted trialog transcripts, newest first
    GET  /hub/manifest   the node's public self-description (never fails)
    POST /hub/spore      governed spore ingress (fail-closed, audited)
    GET  /hub/spores     the curated spore ledger, newest first
    GET  /hub/public     curated public surface (secrets hard-excluded)
    GET  /v1/snake       what the snake has carried into the mycelium
    POST /v1/snake       carry what is new (explicit — never automatic)
    GET  /v1/garden      the Colorverse world, as it is (never raises)
    POST /v1/garden/start  grow it — explicit, never per request
    POST /v1/garden/stop   stop growing; the frame stays
    POST /v1/engine/start  start the local model server  no body, explicit
    GET  /v1/external_agents/info    list registered external agent types
    GET  /v1/external_agents/info/{agent_type}  get info for a specific agent type
    POST /v1/external_agents/govern  govern an external agent's request
    POST /v1/external_agents/tool_check  govern an external agent's tool use
    POST /v1/external_agents/batch_govern  govern multiple requests in a batch
    GET  /v1/external_agents/status  get external agent governance statistics
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import AfterValidator, BaseModel, Field

from openjarvis import __version__
from openjarvis.sovereign import daily, garden, hub, motor, session as session_mod, shield, snake
from openjarvis.sovereign import trialog as trialog_mod
from openjarvis.sovereign import external_agents
from openjarvis.sovereign.bridge import compose_query
from typing import Any, Dict

from typing_extensions import Annotated

from openjarvis.sovereign import voice
from openjarvis.sovereign.link import ValueGovernor, default_link

# Read from the distribution, not a literal. Set 19 breath 2: the version was
# hardcoded in three places (pyproject, this module, the CLI), which is a
# multi-writer defect waiting to produce the next wrong number -- and this repo
# had already shipped one wrong version in five places.
APP_VERSION = __version__

# The React/Tauri app (the desktop/web surface) runs on the platform's port
# and must read this node's governed data. The sovereign door is bound to
# 127.0.0.1 and stays otherwise same-origin; this is the ONE relaxation, and
# it is deliberately narrow: loopback origins only, no credentials, only the
# verbs the doors actually use. A platform proxy was the alternative and was
# rejected -- it would mean editing server/app.py, breaking the additive
# overlay rule the whole fork rests on.
LOOPBACK_ORIGIN_RE = r"^https?://(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$"

_UI_PATH = Path(__file__).resolve().parent / "web" / "ui.html"


def _hold(
    where: str,
    noun: str,
    verdict: dict,
    request: str,
    ledger,
    log_prefix: str,
) -> None:
    """Withhold an action — and remember it. The ONE place this happens.

    Set 21. Four doors each open-coded the same three steps: log a ``DENIED``
    line, build a detail body, raise a 403. Adding "and remember it" to four
    sites would have been the seventh fact-in-two-places this repository has
    found, and the next door added would have silently forgotten. So the three
    steps live here once, and the doors pass their own wording.

    ``GET /govern`` is deliberately NOT routed through here. It also answers 403
    for a held request, but it *judges* — nothing was attempted, so nothing was
    withheld, and a dry run is not a refusal that landed. Recording it would put
    a fiction in the mirror.

    Set 28 adds the deflection's *direction*: when a door is held, which other
    doors stand open. See :data:`OPEN_DOORS` for why that is a fixed list and
    not a sentence about the request.

    Raises; never returns.
    """
    ledger.log_event(
        "DENIED",
        f"{log_prefix}: risk={verdict['risk']} "
        f"eye={verdict.get('oracle', {}).get('vote')} :: {request[:80]}",
        actor="Bianca/api",
    )
    direction = shield.open_doors(where)
    shield.record_refusal(where, verdict, request, direction=direction)
    raise HTTPException(status_code=403, detail={
        "governance": verdict,
        "blocked": True,
        "direction": direction,
        "message": f"The {noun} was NOT approved (risk={verdict['risk']}, "
                   f"alignment={verdict['alignment']}). Verdict: {verdict['verdict']}.",
    })


def _load_face() -> str:
    """One writer for the node's face: the packaged ui.html on disk."""
    try:
        return _UI_PATH.read_text(encoding="utf-8")
    except OSError:  # a missing face must never take the door down
        return ("<!doctype html><html lang='de'><body><h1>Bianca</h1>"
                "<p>face missing: web/ui.html could not be read.</p></body></html>")


#: The one description, on every door, so the four of them cannot drift.
_LANG_DOC = (
    "Which language she answers in: 'de' (the default) or 'en'. "
    "Applies to her prose only — verdicts, gold values, the 'missing' "
    "sentence and the shield's deflection are the law and stay as the gate "
    "writes them. An unknown language is a 422, never a 403: a malformed "
    "request is not a refusal."
)


def _check_lang(value: str | None) -> str | None:
    """Reject a language she does not speak, at the door, as a 422.

    A module-level function rather than a closure so a test can call it
    directly, without building a pydantic model around the question.

    Why 422 and not 403: 403 in this product means *the gate held your
    request*, and it carries a verdict. A language nobody speaks is a
    malformed request, and a malformed request must never be dressed as a
    refusal — a caller who typo'd ``"en"`` would otherwise read "Bianca denied
    me" and be wrong about the most important thing on the screen.
    """
    if value is None:
        return None
    try:
        return voice.resolve(value)
    except voice.UnknownLanguage as exc:
        raise ValueError(str(exc)) from exc


#: The field type itself, so a request model writes ``lang: Lang = None`` and
#: every door gets the validation, the description and the 422 for free. The
#: "one writer" idea applied to a *type*: four separately decorated fields
#: would be four chances to forget the validator, and one of them would.
Lang = Annotated[
    str | None,
    Field(default=None, description=_LANG_DOC),
    AfterValidator(_check_lang),
]


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    lang: Lang = None
    model: str = Field(default_factory=daily.default_model)


class AskResponse(BaseModel):
    governance: dict
    reply_governance: dict
    decision: list[str]
    reply: str
    prediction: str | None = None
    validation: list[str] | None = None
    explanation: str | None = None


class SporeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    source: str = Field(default="<anonymous>", max_length=200)
    kind: str = Field(default="spore", max_length=40)


class ChatTurn(BaseModel):
    role: str = Field(default="user", pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    messages: list[ChatTurn] = Field(..., min_length=1, max_length=24)
    lang: Lang = None
    model: str = Field(default_factory=daily.default_model)


class ChatResponse(BaseModel):
    governance: dict
    reply_governance: dict
    decision: list[str]
    reply: str
    prediction: str | None = None
    validation: list[str] | None = None
    explanation: str | None = None
    turns: int
    model: str


class TrialogRequest(BaseModel):
    topic: str = Field(default="", max_length=trialog_mod.MAX_TOPIC)
    lang: Lang = None
    rounds: int = Field(default=2, ge=1, le=trialog_mod.MAX_ROUNDS)
    model: str = Field(default_factory=daily.default_model)
    #: Set 29: a model per voice. Absent or empty means *one model for all three*,
    #: which is exactly what this door did before the field existed — so a caller
    #: that knows nothing about it gets the behaviour it always had. A name for a
    #: voice this house does not have is dropped, not honoured: a mapping must not
    #: be able to invent a fourth speaker.
    #:
    #: It cannot move a verdict. Each turn is governed by `link.govern(reply)`
    #: *after* the reply exists, so whichever weights wrote the words, the gate
    #: reads them the same way. The reason the field exists is a measurement, not
    #: a preference: over four rounds the twelve verdicts never once moved.
    models: Dict[str, str] = Field(default_factory=dict)


class SessionRequest(BaseModel):
    """Start a working session. The seam refuses what it cannot measure."""

    topic: str = Field(..., min_length=1, max_length=trialog_mod.MAX_TOPIC)
    #: The aim, in the owner's words. Mandatory: a team without an aim is three
    #: conversations in turn, and the record would say so.
    goal: str = Field(..., min_length=1, max_length=400)
    #: The OWNER's decision, from set 30: a criterion *or* the owner. Two words
    #: only, and anything else is refused at the door with the list — because a
    #: free-text completion condition would be a judge that nobody built and
    #: nobody checked. The model is not that judge: set 29 measured that three
    #: different weights change the words and never the verdict.
    stop_when: str = Field(default="", max_length=40)
    #: A mandatory ceiling, in CALLS, named as a ceiling. Reaching it closes the
    #: session as `ceiling_reached` and the record says the goal was not met.
    ceiling: int = Field(default=session_mod.DEFAULT_CEILING, ge=1, le=1000)
    model: str = Field(default_factory=daily.default_model)
    models: Dict[str, str] = Field(default_factory=dict)
    #: Do not start the process. The record exists, the team does not run until
    #: somebody says so — and the door says that plainly, because a session that
    #: looks started and is not is the one state nobody can tell from outside.
    start: bool = True


class SessionSayRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class AgentRequest(BaseModel):
    """One governed tool-agent run. The sword, behind a door.

    Set 18: `max_turns` is capped here for the same reason the topic is capped
    on the trialog door — a run that cannot be audited in one sitting is not a
    door, it is a slot machine.
    """

    query: str = Field(..., min_length=1, max_length=4000)
    lang: Lang = None
    model: str = Field(default_factory=daily.default_model)
    max_turns: int = Field(default=6, ge=1, le=12)


class ToolCheck(BaseModel):
    """One tool judgement — the whole verdict, so a refusal shows its evidence.

    Set 18: this is a verdict, not a boolean. An earlier shape kept only
    `allowed`, which could not name the stem that tripped the call.
    """

    tool: str
    verdict: dict


class AgentResponse(BaseModel):
    governance: dict
    reply_governance: dict
    content: str
    turns: int
    tool_results: list[dict]
    tool_calls: list[ToolCheck]
    denied: list[ToolCheck]
    model: str


# External Agents API Models
class ExternalAgentInfoResponse(BaseModel):
    agents: dict
    count: int


class ExternalAgentGovernRequest(BaseModel):
    request: str = Field(..., min_length=1, max_length=4000, description="The text or action to govern")
    agent_type: str = Field(default="generic", description="Type of agent (claude, llama, mistral, generic)")
    agent_id: Optional[str] = Field(default=None, description="Optional unique identifier for this agent instance")
    context: Optional[str] = Field(default=None, description="Optional context about the request")
    source: str = Field(default="external_api", description="Where this request originated from")


class ExternalAgentToolCheckRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool the agent wants to use")
    tool_args: dict = Field(default_factory=dict, description="Arguments the agent wants to pass to the tool")
    agent_type: str = Field(default="generic", description="Type of agent")
    agent_id: Optional[str] = Field(default=None, description="Optional agent instance identifier")
    source: str = Field(default="external_api", description="Origin of the request")


class ExternalAgentBatchGovernRequest(BaseModel):
    requests: list[str] = Field(..., min_length=1, max_length=20, description="List of requests to govern")
    agent_type: str = Field(default="generic", description="Type of agent making the requests")
    agent_id: Optional[str] = Field(default=None, description="Optional agent instance identifier")
    source: str = Field(default="external_api", description="Origin of the requests")


class ExternalAgentGovernResponse(BaseModel):
    verdict: str
    risk: float
    alignment: float
    risk_hits: list[str]
    gold_hits: list[str]
    oracle: dict
    agent_type: str
    agent_info: dict
    timestamp: str
    evidence: dict
    governance: dict
    cycle_state: Optional[dict] = None


class ExternalAgentBatchResponse(BaseModel):
    results: list[ExternalAgentGovernResponse]
    count: int


class ExternalAgentStatusResponse(BaseModel):
    status: str
    statistics: dict
    governance: dict
    timestamp: str


def create_app(ledger_dir: str | None = None) -> FastAPI:
    app = FastAPI(title="Bianca Sovereign API", version=APP_VERSION)
    ledger_dir = ledger_dir or str(daily.ledger_dir())
    ui_html = _load_face()
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=LOOPBACK_ORIGIN_RE,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/", response_class=HTMLResponse)
    def face() -> HTMLResponse:
        # the face is served hardened: a per-request nonce substitutes into
        # the template's meta-CSP and the inline script tag (one writer), so
        # the node's own page may run while embedding and base-tag tricks
        # stay closed. The nonce changes every request.
        nonce = secrets.token_urlsafe(16)
        csp = (
            "default-src 'self'; "
            f"script-src 'nonce-{nonce}'; "
            "style-src 'unsafe-inline'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'; "
            "form-action 'self'"
        )
        page = ui_html.replace("__CSP__", csp).replace("__NONCE__", nonce)
        return HTMLResponse(
            page,
            headers={
                "Content-Security-Policy": csp,
                "X-Content-Type-Options": "nosniff",
            },
        )

    @app.get("/hub/manifest")
    def hub_manifest() -> dict:
        # who is this node? deterministic public self-description, never fails
        return hub.manifest()

    @app.post("/hub/spore", status_code=200)
    def hub_spore(req: SporeRequest) -> dict:
        # a foreign word entering the node is judged on arrival — fail-closed
        status, body = hub.accept_spore(
            req.text, source=req.source, kind=req.kind,
            ledger_dir=ledger_dir)
        if status == 403:
            raise HTTPException(status_code=403, detail=body)
        if status == 503:
            raise HTTPException(status_code=503, detail=body)
        return body

    @app.get("/hub/spores")
    def hub_spores(limit: int = 10) -> dict:
        # the curated spore ledger — accepted spores, newest first
        return {"spores": hub.list_spores(limit=max(1, min(limit, 100)))}

    @app.get("/hub/public")
    def hub_public() -> dict:
        # names only — the curated surface, secrets hard-excluded by construction
        return {"files": hub.public_list()}

    @app.get("/hub/public/{name}")
    def hub_public_file(name: str) -> dict:
        # excluded and missing look IDENTICAL from outside: 410, same shape —
        # the door never confirms whether a forbidden path exists
        found, content = hub.public_read(name)
        if not found:
            raise HTTPException(status_code=410, detail={
                "error": "not served", "name": name})
        return {"name": name, "content": content}

    @app.get("/health")
    def health() -> dict:
        link = default_link()
        ctx = link.prepare()
        return {
            "ok": True,
            "name": "bianca",
            "version": APP_VERSION,
            "soul": "/home/sam/.openjarvis/SOUL.md",
            "cycle": ctx["cycle_state"],
            "gold_loaded": ctx["gold_manifest"],
        }

    @app.get("/v1/snake")
    def snake_door() -> dict:
        # Set 22: the seam where the inner world reaches the mycelium. Read side.
        # It states the withheld half out loud, because a screen that only
        # showed successes would teach the reader that the net accepts
        # everything — which is a different product.
        return snake.snake_state()

    @app.post("/v1/snake")
    def snake_carry() -> dict:
        # Explicit by design: the sword's rule (full reach is a decision
        # argued from the recorded measurements, not an oversight) applies to
        # the net exactly as it does to the tools. Nothing leaves without this.
        return snake.carry_all()

    @app.get("/v1/garden")
    def garden_door() -> dict:
        # Set 24: the node's window onto Colorverse. Read side, and it never
        # raises — a missing kernel is a deflection that names the fix, because
        # the mechanism knows precisely which ten files it wants. Silence would
        # be the hard barrier the owner rejected, and a traceback would make the
        # prettiest thing on the product its most fragile one.
        #
        # Set 29: `why` is `idle.garden_diagnosis()` — **read, never re-derived**.
        # One writer of the diagnosis, two doors that show it, because a second
        # computation of "why it cannot grow" is how two surfaces would come to
        # disagree about the one ungated surface of the product. The card
        # already says the garden is still; this says which lines keep it there.
        from openjarvis.sovereign.idle import garden_diagnosis
        out = dict(garden.status())
        out["why"] = garden_diagnosis()
        return out

    @app.post("/v1/garden/start")
    def garden_start() -> dict:
        # Explicit, like `idle start`. Growing the garden is an action someone
        # takes: a page view must never be what makes this process appear, or
        # every request would carry a world's worth of CPU.
        return garden.start()

    @app.post("/v1/garden/stop")
    def garden_stop() -> dict:
        # The frame stays. The last thing the kernel was is still a fact about
        # the kernel; deleting it would make the garden lie by omission.
        return garden.stop()

    @app.get("/v1/shield")
    def shield_door(limit: int = 20) -> dict:
        # Set 21: where a withheld action lands. The deflector, not a wall —
        # every refusal carries the verdict, the stems that tripped it, what the
        # request was MISSING, where the values were read from, and the second
        # eye. A read model over a local file; never raises, because a mirror
        # that can fail is a mirror that hides.
        return shield.shield_state()

    @app.get("/context")
    def context() -> dict:
        out = default_link().prepare()
        out["self_check"] = daily.node_self_check()
        # Set 26: the languages she speaks, from voice.py, so no surface has to
        # restate the list. A picker that hardcodes ["de", "en"] is a second
        # writer: add a language to voice.py and the picker would still offer
        # two, which looks like the language does not exist.
        out["languages"] = [
            {"code": code, "name": voice.LANGUAGES[code], "default": code == voice.DEFAULT_LANG}
            for code in voice.supported()
        ]
        return out

    @app.get("/govern")
    def govern(text: str = "") -> dict:
        verdict = default_link().govern(text)
        # the gate's status speaks its verdict: deny = 403 with the verdict
        # body, exactly like /v1/ask — a status-checking consumer hears it
        if verdict["verdict"] == "zurueckhalten":
            raise HTTPException(status_code=403, detail=verdict)
        return verdict

    @app.get("/today")
    def today() -> dict:
        return daily.build_briefing(default_link(), Path(ledger_dir))

    @app.get("/idle/status")
    def idle() -> dict:
        return daily.idle_status()

    @app.get("/idle/contract")
    def idle_contract() -> dict:
        """The work-unit contract, and the garden's own diagnosis — one call.

        Set 29. The owner asked for *dauerhaft aktiv bis zum erfolgreichen
        Abschluß*, and a loop needs a completion criterion that can be checked.
        This is it, next to the reason the set was opened: the garden is measured
        here rather than described in a document, so a reader can see that the
        one ungated surface of this product is flat, by how much, and which lines
        of a sibling repository keep it that way.

        It **reads two existing writers** (``verify_units`` and
        ``garden_diagnosis``) and writes nothing, so it cannot become a door that
        changes state by being looked at — the same rule ``garden.start()`` obeys.
        """
        from openjarvis.sovereign.idle import garden_diagnosis, verify_units
        return {
            "contract": verify_units(),
            "garden": garden_diagnosis(),
        }

    @app.get("/urasil")
    def urasil() -> dict:
        # the living cycle, as a read model. Assembled only from existing
        # writers (link.prepare, infinity, harmony) and never fails: a
        # missing ALF degrades to '?' rather than taking the tab down.
        return trialog_mod.uracil_view(default_link())

    @app.get("/v1/trialogs")
    def trialogs(limit: int = 20) -> dict:
        # what the three voices have already said — the read side of the
        # store run_trialog writes. Newest first, never raises.
        return {"trialogs": trialog_mod.list_trialogs(ledger_dir, limit=limit)}

    @app.get("/v1/trialogs/{name}")
    def trialog_transcript(name: str) -> dict:
        # a transcript door is a filesystem door: missing and non-trialog
        # names look IDENTICAL from outside (410), never an existence oracle
        found, content = trialog_mod.read_trialog(ledger_dir, name)
        if not found:
            raise HTTPException(status_code=410, detail={
                "error": "not served", "name": name})
        return {"name": name, "content": content}

    @app.post("/v1/chat", response_model=ChatResponse)
    def chat(req: ChatRequest) -> ChatResponse:
        # Multi-turn, fail-closed in the same shape as /v1/ask: EVERY user
        # turn is judged before a single token is generated, and the first
        # denial refuses the whole exchange with the verdict body attached.
        from openjarvis.sovereign.logger import InteractionLogger

        link = default_link()
        ledger = InteractionLogger(ledger_dir)
        user_turns = [m for m in req.messages if m.role == "user"]
        if not user_turns:
            raise HTTPException(status_code=422, detail={
                "error": "no user turn", "message": "a chat needs at least one user turn"})
        blocked: dict | None = None
        blocked_text = ""
        for turn in user_turns:
            v = link.govern(turn.content)
            if v["verdict"] == "zurueckhalten":
                blocked = v
                # Set 21: remember the turn that TRIPPED the gate, not the first
                # one. This door used to log user_turns[0], which in a long
                # exchange is the innocent opening line — so the mirror showed a
                # refusal and attributed it to the wrong words. A shield that
                # names the wrong request is worse than no shield, because it
                # looks like evidence.
                blocked_text = turn.content
                break
        if blocked is not None:
            _hold("POST /v1/chat", "exchange", blocked, blocked_text,
                  ledger, "api chat refused")

        last = user_turns[-1].content
        verdict = link.govern(last)
        composed = compose_query(last, context="Bianca node via API chat")
        recommended = composed["final"]["next"]

        from openjarvis.core.config import load_config
        from openjarvis.core.types import Message, Role
        from openjarvis.engine import EngineConnectionError, get_engine

        config = load_config()
        resolved = get_engine(config, "ollama", model=req.model)
        if resolved is None:
            ledger.log_event("CHAT", "api chat attempted, engine unavailable (503)",
                             actor="Bianca/api")
            raise HTTPException(status_code=503,
                                detail="no inference engine available (is Ollama running?)")
        engine = resolved[1]
        # Set 26: the tail is written once, in voice.py. It was open-coded
        # here twice with identical wording and once in the CLI with different
        # wording, which is how a language ends up honoured at three doors and
        # forgotten at the fourth.
        cycle = link.prepare()["cycle_state"]
        soul = (f"{daily.load_soul()}\n"
                f"Current cycle: {cycle}. "
                f"Recommended approach: {recommended}. "
                f"{voice.tail(req.lang, cycle)}")
        messages = [Message(role=Role.SYSTEM, content=soul)]
        for m in req.messages:
            messages.append(Message(
                role=Role.USER if m.role == "user" else Role.ASSISTANT,
                content=m.content))
        try:
            result = engine.generate(messages, model=req.model,
                                     temperature=0.7, max_tokens=1024)
        except EngineConnectionError as exc:
            ledger.log_event("CHAT", "api chat attempted, engine error", actor="Bianca/api")
            raise HTTPException(status_code=503, detail=f"engine error: {exc}")
        reply = (result.get("content") or "").strip()
        # the delivered words meet the governor too — the record says what
        # the governor thought of the reply actually written
        reply_v = link.govern(reply)
        ledger.log_event(
            "CHAT",
            f"api chat answered ({len(req.messages)} turns, {len(reply)} chars) "
            f"reply={reply_v['verdict']} eye={reply_v.get('oracle', {}).get('vote')}",
            actor="Bianca/api",
        )
        # Set 28: the other half of the mirror — see POST /v1/ask.
        shield.record_grown("POST /v1/chat", reply_v, last,
                            uracil=cycle, turns=len(req.messages),
                            reply_chars=len(reply))
        return ChatResponse(
            governance=verdict,
            reply_governance={
                "verdict": reply_v["verdict"],
                "risk_hits": reply_v.get("risk_hits") or [],
                "oracle": reply_v.get("oracle"),
            },
            decision=composed["decision"],
            reply=reply,
            prediction=composed["prediction"],
            validation=composed["validation"],
            explanation=composed["explanation"],
            turns=len(req.messages),
            model=req.model,
        )

    @app.get("/v1/agent/tools")
    def agent_tools() -> dict:
        """The sword's inventory, derived from the live tool specs.

        Set 18: "tools on hand" is only true if you can see them. The governed
        agent already existed behind a CLI command; a door that shows what it
        may call is what makes it a Jarvis rather than a chat window.
        """
        from openjarvis.sovereign.agent import tool_inventory

        return {
            "tools": tool_inventory(),
            "governance": {
                "seam": "before_tool_call",
                "fail_closed": True,
                "denies": "zurueckhalten only",
                "second_eye": "advisory, never binding",
                "holder": "ValueGovernor",
            },
        }

    @app.post("/v1/agent", response_model=AgentResponse)
    def agent(req: AgentRequest) -> AgentResponse:
        # The governed tool-agent, behind a door. Fail-closed in the same shape
        # as /v1/ask and /v1/chat: the query is judged BEFORE any engine work,
        # and a denial refuses the whole run with the verdict attached.
        from openjarvis.sovereign.agent import governed_agent_ask
        from openjarvis.sovereign.logger import InteractionLogger

        ledger = InteractionLogger(ledger_dir)
        try:
            out = governed_agent_ask(
                req.query, model=req.model, max_turns=req.max_turns,
                ledger_dir=Path(ledger_dir), lang=req.lang,
                where="POST /v1/agent",
            )
        except RuntimeError as exc:
            # A dead engine is never drawn as an answer. 503, and the surface
            # shows ENGINE_DOWN rather than an empty bubble.
            ledger.log_event("AGENT", f"api agent attempted, engine unavailable: {exc}",
                             actor="Bianca/api")
            raise HTTPException(status_code=503, detail=str(exc))

        governance = out.get("governance") or {}
        if governance.get("verdict") == "zurueckhalten":
            raise HTTPException(status_code=403, detail={
                "governance": governance,
                "blocked": True,
                # lifted, not recomputed: the agent computed it once and used the
                # same object for the mirror, so the caller and the owner read
                # one direction rather than two that could drift apart
                "direction": out.get("direction"),
                "message": (
                    f"The run was NOT approved (risk={governance.get('risk')}, "
                    f"alignment={governance.get('alignment')}). "
                    f"Verdict: {governance.get('verdict')}."
                ),
            })

        state = out["state"]
        checks = [{"tool": c["tool"], "verdict": c["verdict"]} for c in state.checks]
        return AgentResponse(
            governance=governance,
            reply_governance=out.get("reply_governance") or {},
            content=out.get("content") or "",
            turns=int(out.get("turns") or 0),
            tool_results=[
                {
                    "tool": getattr(r, "tool_name", "?"),
                    "content": getattr(r, "content", ""),
                    "success": bool(getattr(r, "success", True)),
                }
                for r in out.get("tool_results") or []
            ],
            tool_calls=checks,
            denied=[{"tool": d["tool"], "verdict": d["verdict"]} for d in state.denied],
            model=req.model,
        )

    @app.post("/v1/trialog")
    def trialog(req: TrialogRequest) -> dict:
        # Three voices, one topic. The TOPIC is judged first — a denied topic
        # costs no engine time and is refused exactly like /v1/ask. Every
        # utterance is then governed by the shared writer (off-limit turns
        # are stamped and KEPT, not deleted), and the whole deliberation is
        # journaled and persisted by the same record_trialog the CLI uses.
        from openjarvis.sovereign.logger import InteractionLogger

        link = default_link()
        ledger = InteractionLogger(ledger_dir)
        topic = (req.topic or "").strip() or trialog_mod.default_topic()
        topic_v = link.govern(topic)
        if topic_v["verdict"] == "zurueckhalten":
            _hold("POST /v1/trialog", "topic", topic_v, topic, ledger,
                  "api trialog refused at the topic")

        from openjarvis.core.config import load_config
        from openjarvis.core.types import Message, Role
        from openjarvis.engine import get_engine

        config = load_config()
        resolved = get_engine(config, "ollama", model=req.model)
        if resolved is None:
            ledger.log_event("TRIALOG", "api trialog attempted, engine unavailable (503)",
                             actor="Bianca/api")
            raise HTTPException(status_code=503,
                                detail="no inference engine available (is Ollama running?)")

        out = trialog_mod.run_trialog(
            link, topic=topic, engine=resolved[1], model=req.model,
            rounds=req.rounds,
            make_message=lambda role, content: Message(role=role, content=content),
            models=req.models,
        )
        # A deliberation interrupted by a dead engine is STILL PERSISTED, and
        # the door answers 503 like every other engine failure — an opaque 500
        # would hide both the cause and the work already done. The partial
        # record travels with the refusal so nothing is silently swallowed.
        saved = trialog_mod.record_trialog(out, ledger_dir, daily.notes_dir())
        if not out["completed"]:
            ledger.log_event(
                "TRIALOG",
                f"api trialog interrupted at turn {out['governance']['turns']}"
                f"/{out['rounds'] * len(out['voices'])} (engine unreachable); "
                f"partial record kept as {saved.name}",
                actor="Bianca/api",
            )
            raise HTTPException(status_code=503, detail={
                "error": "deliberation interrupted",
                "reason": out["stopped_reason"],
                "completed": False,
                "topic": out["topic"],
                "rounds": out["rounds"],
                "model": out["model"],
                # the same two fields on the interrupted path: a deliberation that
                # stopped after four turns still ran through three models, and a
                # partial record that does not say which is a record that cannot
                # be compared with a complete one.
                "models": out["models"],
                "same_model_everywhere": out["same_model_everywhere"],
                "voices": out["voices"],
                "turns": out["turns"],
                "transcript": out["transcript"],
                "governance": out["governance"],
                "topic_governance": topic_v,
                "eye_warned": out["eye_warned"],
                "summary": out["summary"],
                "saved": saved.name,
            })
        # Set 28: Resonanz gets a relation instead of a count — who brought what
        # the others did not. `GOLD_VALUES` is read off the gate, never copied,
        # and the read model says out loud what it cannot measure.
        out["complementarity"] = trialog_mod.complementarity(
            out["turns"], ValueGovernor.GOLD_VALUES,
        )
        return {
            "topic": out["topic"],
            "rounds": out["rounds"],
            "model": out["model"],
            # 🚨 SET 29, a defect THIS SET CREATED, found by the live capture and
            # repaired in the open rather than quietly: `run_trialog` returns
            # `models` and `same_model_everywhere`, this hand-written response
            # listed its keys one by one, and the two new ones were not on the
            # list. The request side worked — the turns really were generated
            # through different models — so the record said `null` while the
            # turns each carried their own model. Two of our own sides disagreed,
            # and the type in React declared both fields required, which is what
            # a captured fixture is for: it type-checks against the door's own
            # type with no cast, so this cannot come back.
            "models": out["models"],
            "same_model_everywhere": out["same_model_everywhere"],
            "voices": out["voices"],
            "transcript": out["transcript"],
            "turns": out["turns"],
            "governance": out["governance"],
            "complementarity": out["complementarity"],
            "topic_governance": topic_v,
            "eye_warned": out["eye_warned"],
            "summary": out["summary"],
            "completed": True,
            "saved": saved.name,
        }

    # ── the working session (set 30) ─────────────────────────────────────────
    #
    # Seven doors, and the governance order is the same everywhere: **the words
    # are judged before anything is created**. A held topic, a held goal or an
    # unknown criterion costs no engine time, no directory and no process, and
    # goes through `_hold()` — the existing seam — so a session does not become
    # the sixth place a refusal is written by hand.

    @app.post("/v1/sessions")
    def create_session(req: SessionRequest) -> dict:
        from openjarvis.sovereign.logger import InteractionLogger

        link = default_link()
        ledger = InteractionLogger(ledger_dir)
        topic_v = link.govern(req.topic)
        if topic_v["verdict"] == "zurueckhalten":
            _hold("POST /v1/sessions", "topic", topic_v, req.topic, ledger,
                  "api session refused at the topic")
        goal_v = link.govern(req.goal)
        if goal_v["verdict"] == "zurueckhalten":
            _hold("POST /v1/sessions", "goal", goal_v, req.goal, ledger,
                  "api session refused at the goal")

        # The criterion is not judged — it is *checked*: a word outside the
        # vocabulary is a 400 with the vocabulary in it, not a 403. A 403 would
        # say "Bianca refused you", and she did not: nobody said something held,
        # the caller asked for a door that does not exist. The same distinction
        # set 26 drew for an unknown language (422, never 403).
        why = session_mod.refused_reason(req.topic, req.goal, req.stop_when)
        if why:
            raise HTTPException(status_code=400, detail=why)

        state = session_mod.create(ledger_dir, req.topic, req.goal, req.stop_when,
                                   ceiling=req.ceiling, model=req.model,
                                   models=req.models or None)
        pid = session_mod.spawn(ledger_dir, state["id"]) if req.start else None
        state = session_mod.read_state(ledger_dir, state["id"]) or state
        state["running"] = bool(pid)
        ledger.log_event(
            "SESSION",
            f"session {state['id']} on '{req.topic[:50]}' until {req.stop_when} "
            f"(ceiling {req.ceiling} calls, {'running' if pid else 'not started'})",
            actor="Bianca/api",
        )
        return state

    @app.get("/v1/sessions")
    def sessions(limit: int = 50) -> dict:
        # The owner's words, taken literally: a session is listed *under* its
        # topic. One list, grouped, and the grouping is computed once here so a
        # second screen cannot invent a second order.
        return session_mod.list_sessions(ledger_dir, limit=limit)

    # 🚨 Declared BEFORE `/v1/sessions/{session_id}` on purpose. FastAPI matches
    # in declaration order, so a `/v1/sessions/criteria` door added below the
    # parameter door would be read as a session whose id is "criteria" — and it
    # would answer 410 for a question about the vocabulary, which is the exact
    # "a door that does not exist" answer to a question it could answer. Tested
    # by asking for both and reading the two statuses.
    @app.get("/v1/sessions/criteria")
    def session_criteria() -> dict:
        return {
            "criteria": [
                {"name": "owner-accepts",
                 "label": "der Eigentümer nimmt den Vorschlag an",
                 "closes": "only the owner, through POST /v1/sessions/{id}/accept",
                 "proposed_when": "every voice held a gold-aligned verdict in the last "
                                  "round — a condition on the governance record, never "
                                  "a voice's opinion of itself"},
                {"name": "idle-contract",
                 "label": "der Knoten liest den Idle-Vertrag selbst",
                 "closes": "the node, when idle.verify_units()['contract_holds']",
                 "proposed_when": "never proposed — it is checked, not proposed"},
            ],
            "why_only_these": (
                "a free-text criterion would be a judge that nobody built and nobody "
                "checked. set 29 measured that three different models change the words "
                "and never the verdict, so the model is not the judge either."),
            "the_ceiling_is_not_a_criterion": (
                "a ceiling is a budget in model calls. reaching it closes the session as "
                "'ceiling_reached' and the record says the goal was NOT met."),
        }

    @app.get("/v1/sessions/{session_id}")
    def session_detail(session_id: str) -> dict:
        out = session_mod.read_session(ledger_dir, session_id)
        if out is None:
            # A missing session and a broken one look identical — 410, never a
            # filesystem existence oracle.
            raise HTTPException(status_code=410, detail="no such session")
        # 🚨 `running` is a boolean at THIS level, and the pid has its own field —
        # the same rule the list door now follows, in the same shape. This door
        # did the opposite: it injected a boolean *into the state* and left the
        # pid under the outer `running`, so one payload carried the same fact in
        # two places under two types, and a screen had to know which door it was
        # reading to know whether `running` was a yes or a process number.
        #
        # The state is the record. It carries what is **stored** — and `pid` is
        # stored, so it is there and it is enough. Nothing derived is written
        # into it, or the next reader cannot tell a stored fact from a computed
        # one.
        pid = out.get("running")
        out["state"].pop("running", None)
        out["running"] = bool(pid)
        out["pid"] = pid
        out["criterion"] = {
            "stop_when": out["state"]["stop_when"],
            "known": list(session_mod.SESSION_CRITERIA),
            "the_model_is_not_the_judge": (
                "a different model changes the words, never the verdict — set 29 "
                "measured it over four rounds with three models"),
        }
        return out

    @app.post("/v1/sessions/{session_id}/say")
    def session_say(session_id: str, req: SessionSayRequest) -> dict:
        from openjarvis.sovereign.logger import InteractionLogger

        state = session_mod.read_state(ledger_dir, session_id)
        if state is None:
            raise HTTPException(status_code=410, detail="no such session")
        # The owner is a voice, not an exemption. A held request is deflected at
        # the door and remembered, never censored into the transcript — the
        # distinction from an off-limit *voice* turn is deliberate: generated
        # speech that trips the gate is stamped and kept (it happened, it is
        # evidence), a *request* that trips it did not happen.
        link = default_link()
        v = link.govern(req.text)
        if v["verdict"] == "zurueckhalten":
            _hold("POST /v1/sessions/say", "turn", v, req.text,
                  InteractionLogger(ledger_dir), "api session refused the owner's turn")
        session_mod.say(ledger_dir, session_id, req.text)
        InteractionLogger(ledger_dir).log_event(
            "SESSION", f"owner spoke into {session_id} "
                       f"({v['verdict']}, gold={','.join(v.get('gold_hits') or []) or '—'})",
            actor="Bianca/api")
        resumed = False
        if not session_mod.is_running(session_id) and state.get("status") in (
                "new", "running", "awaiting_owner", "ceiling_reached"):
            resumed = bool(session_mod.spawn(ledger_dir, session_id))
        return {"id": session_id, "queued": True, "verdict": v,
                "resumed": resumed,
                "note": ("the turn is queued, not answered — the team reads it in "
                         "the next round it takes")}

    @app.post("/v1/sessions/{session_id}/accept")
    def session_accept(session_id: str) -> dict:
        from openjarvis.sovereign.logger import InteractionLogger

        state = session_mod.read_state(ledger_dir, session_id)
        if state is None:
            raise HTTPException(status_code=410, detail="no such session")
        # 🚨 A closed session cannot be closed again. Measured before this line
        # existed: a second `POST …/accept` on a session the owner had already
        # accepted answered **200** and wrote a third line to `proposals.jsonl` —
        # the door filtered on "not closed", and the file's earlier open line for
        # the same round was still in the list. A person's close is a decision;
        # taking it twice is not a second decision, it is the same one counted
        # twice, and a count that can grow without an event is the defect this
        # repository keeps meeting in a new costume.
        #
        # 409, not 403: nothing was judged here, and a door that answers a
        # refusal to a request that was never governed would be teaching the
        # reader that Bianca blocked an acceptance she never read.
        # 🚨 Two guards, not one, and the second is the load-bearing one. The
        # state is written so that `awaiting_owner` carries **no** close, so the
        # line below already lets it through — but the reason the owner was
        # locked out of his own door once was a status meaning two things, and a
        # status meaning two things should not be load-bearing on a single
        # convention. The criterion `owner-accepts` exists for exactly this
        # moment: the team proposes, the owner accepts. A door that can refuse
        # that is not a guard, it is a wall.
        if state.get("status") == "awaiting_owner":
            offen = [x for x in session_mod.read_proposals(ledger_dir, session_id)
                     if not x.get("closed")]
            if not offen:
                raise HTTPException(
                    status_code=409,
                    detail=("the team asked the owner to accept and left no open "
                            "proposal behind — the record is inconsistent, and this "
                            "door will not invent the proposal it was meant to hear."))
            # straight through to the acceptance below
        elif state.get("closed") and state.get("status") not in ("new", "running"):
            raise HTTPException(
                status_code=409,
                detail=("this session is already closed as "
                        f"'{state.get('status')}', written by "
                        f"'{state.get('closed_by') or 'unknown'}' at "
                        f"{state.get('closed')}: {state.get('closed_because')}. "
                        "A close is taken once; a second one would be the same "
                        "decision counted twice."))
        proposals = session_mod.read_proposals(ledger_dir, session_id)
        open_ones = [p for p in proposals if not p.get("closed")]
        if not open_ones:
            raise HTTPException(
                status_code=409,
                detail=("the team has proposed no close. This session ends on the "
                        "owner's word alone only when the gate held nothing and "
                        "warned nobody in the last round — that condition has not "
                        "been met."))
        # 🚨 Kill, then close **once, and by the owner**. The first version wrote
        # the fields here by hand, which made this door a fourth writer of
        # `state.json` and left the race open: `accept` writes `complete`, the
        # loop wakes from a model call and writes its own exit status, and the
        # file ends up saying whichever was slower. Now the close goes through
        # `close(..., by="owner")` — the same writer, with the authorship
        # recorded — and the loop reads that authorship before its own write and
        # steps aside.
        pid = session_mod.is_running(session_id)
        if pid:
            import os as _os
            import signal as _signal
            try:
                _os.kill(pid, _signal.SIGTERM)
            except OSError:
                pid = None
        out = session_mod.close(
            ledger_dir, session_id, "complete",
            f"the owner accepted the proposal of round {open_ones[-1].get('round')}",
            by="owner",
        )
        # the proposal is marked in place, by appending the closed form, so the
        # file itself says which one was taken rather than leaving that to the
        # reader's inference
        session_mod.append_proposal(ledger_dir, session_id, {
            "round": open_ones[-1].get("round"),
            "at": open_ones[-1].get("at"),
            "trigger": open_ones[-1].get("trigger"),
            "evidence": open_ones[-1].get("evidence"),
            "closed": True,
            "closed_by": "owner",
        })
        InteractionLogger(ledger_dir).log_event(
            "SESSION", f"owner accepted the close of {session_id}", actor="Bianca/api")
        return {"id": session_id, "status": out["status"],
                "closed_because": out["closed_because"],
                "closed_by": out["closed_by"],
                "accepted_round": open_ones[-1].get("round"),
                "process_was_running": bool(pid),
                "note": ("the process was asked to stop and does not write over "
                         "this — a person's close outranks a process exit")}

    @app.post("/v1/sessions/{session_id}/stop")
    def session_stop(session_id: str, reason: str = "stopped by the owner") -> dict:
        state = session_mod.halt(session_id, reason, ledger_dir)
        if state.get("closed_already"):
            # 409, not 200: the session *is* stopped, but not by this call, and a
            # 200 would tell the owner their reason is in the record when it is
            # not. Same status and the same shape as `accept`'s refusal, because
            # it is the same fact: a close was taken once.
            raise HTTPException(
                status_code=409,
                detail=("this session is already closed as "
                        f"'{state.get('status')}', written by "
                        f"'{state.get('closed_by') or 'unknown'}' at "
                        f"{state.get('closed')}: {state.get('closed_because')}. "
                        "Your reason is NOT in the record — the words that ended "
                        "it are the ones already there."))
        # `pending` is the honest half: a live process closes at its next voice
        # boundary, so reporting `stopped` here would be a status the record does
        # not hold yet. The owner is told the difference instead of being handed
        # a tidy answer a few seconds before it becomes true.
        return {
            "id": state.get("id", session_id),
            "status": state.get("status"),
            "closed_because": state.get("closed_because"),
            "pending": bool(state.get("pending")),
            **({"stops_when": state["stops_when"]} if state.get("pending") else {}),
            "note": ("a stop is not instant: a model call already in flight is not "
                     "interrupted, so the record becomes final at the next voice "
                     "boundary — read `status` again, or watch the session"
                     if state.get("pending") else
                     "the record is final: no process was running to write it"),
        }

    @app.get("/v1/models")
    def models() -> dict:
        # Set 30. The owner decided this door, and overrode my set-29 reasoning
        # that a model list is host information. It is, and it stays here: this
        # node is bound to 127.0.0.1, the CORS allowlist is loopback-only, and
        # the list never reaches the hub, a spore or the ledger. What the owner
        # must be able to see is that four of the eight models on this host
        # describe themselves as uncensored — that is a fact about the choice
        # being offered, and a choice nobody can see is not a choice.
        #
        # 🚨 Set 32: this door now resolves the engine through `motor` instead of
        # doing it itself, and it carries the engine's **own** reachability. One
        # reason: a second `get_engine` call here would let the door that *lists*
        # the models and the door that *starts* the server disagree about which
        # engine they mean. Two reasons it answers 200 with `models: []` today, and
        # it said the same authoritative note for both — `get_engine` returns None
        # when Ollama is down, so *nobody answered* and *you have no models*
        # arrived as one shape, and the note ("the names come from the engine")
        # reads like proof in both cases. A screen cannot offer to start a motor
        # without telling them apart, so it may not be asked to.
        resolved, why = motor.resolve()
        try:
            names = list(resolved[1].list_models()) if resolved else []
        except Exception as exc:  # noqa: BLE001 - the door must never raise
            why = f"{type(exc).__name__}: {exc}"
            return {"models": [], "default": daily.default_model(),
                    "engine": motor.describe(None, why),
                    "error": why,
                    "note": "the list is empty because the engine could not be "
                            "reached — this is not a statement that no models exist"}
        return {
            "models": names,
            "default": daily.default_model(),
            "uncensored": sorted(n for n in names if "uncensored" in n.lower()),
            "engine": motor.describe(resolved, why),
            "note": "the names come from the engine, not from a list in this file",
        }

    @app.post("/v1/engine/start")
    def engine_start() -> dict:
        # Set 32, and the first door here that *acts*: it starts a process. That
        # is why it takes **no body**. The argv is written once, in `motor.py`, and
        # nothing a caller can send reaches it — the same rule the snake keeps
        # about held words, and the reason a browser cannot become a second writer
        # of what this node executes. It is not governed, and that needs its
        # reason rather than an omission: the ValueGovernor judges words, and this
        # carries none and generates nothing — answers exist only behind /v1/ask,
        # /v1/chat, /v1/agent and /v1/trialog, all unchanged. It is explicit, like
        # `garden/start`: a view must never be what makes a process appear.
        return motor.start()

    @app.post("/v1/ask", response_model=AskResponse)
    def ask(req: AskRequest) -> AskResponse:
        from openjarvis.sovereign.logger import InteractionLogger

        link = default_link()
        ledger = InteractionLogger(ledger_dir)
        verdict = link.govern(req.query)
        if verdict["verdict"] == "zurueckhalten":
            _hold("POST /v1/ask", "request", verdict, req.query, ledger, "api ask refused")
        composed = compose_query(req.query, context="Bianca node via API")
        recommended = composed["final"]["next"]

        from openjarvis.core.config import load_config
        from openjarvis.core.types import Message, Role
        from openjarvis.engine import EngineConnectionError, get_engine

        config = load_config()
        resolved = get_engine(config, "ollama", model=req.model)
        if resolved is None:
            ledger.log_event("ASK", "api ask attempted, engine unavailable (503)", actor="Bianca/api")
            raise HTTPException(status_code=503, detail="no inference engine available (is Ollama running?)")
        engine = resolved[1]
        # Set 26: the tail is written once, in voice.py. It was open-coded
        # here twice with identical wording and once in the CLI with different
        # wording, which is how a language ends up honoured at three doors and
        # forgotten at the fourth.
        cycle = link.prepare()["cycle_state"]
        soul = (f"{daily.load_soul()}\n"
                f"Current cycle: {cycle}. "
                f"Recommended approach: {recommended}. "
                f"{voice.tail(req.lang, cycle)}")
        try:
            result = engine.generate(
                [Message(role=Role.SYSTEM, content=soul),
                 Message(role=Role.USER, content=req.query)],
                model=req.model, temperature=0.7, max_tokens=1024,
            )
        except EngineConnectionError as exc:
            ledger.log_event("ASK", f"api ask attempted, engine error", actor="Bianca/api")
            raise HTTPException(status_code=503, detail=f"engine error: {exc}")
        reply = result.get("content", "").strip()
        # the generated reply meets the governor too — the record says what
        # the governor thought of the words actually delivered (set 7 eye);
        # the second eye (set 11) witnesses that read as well — advisory only
        reply_v = link.govern(reply)
        ledger.log_event(
            "ASK",
            f"api ask answered ({len(reply)} chars) reply={reply_v['verdict']} "
            f"eye={reply_v.get('oracle', {}).get('vote')}",
            actor="Bianca/api",
        )
        # Set 28: the other half of the mirror. One call, three doors — and a
        # claim in verify_claims.py asserts that every door which generates an
        # answer records one, so the next door added cannot forget silently.
        shield.record_grown("POST /v1/ask", reply_v, req.query,
                            uracil=cycle, reply_chars=len(reply))
        return AskResponse(
            governance=verdict,
            reply_governance={
                "verdict": reply_v["verdict"],
                "risk_hits": reply_v.get("risk_hits") or [],
                "oracle": reply_v.get("oracle"),
            },
            decision=composed["decision"],
            reply=reply,
            prediction=composed["prediction"],
            validation=composed["validation"],
            explanation=composed["explanation"],
        )

    # External Agents API Routes

    @app.get("/v1/external_agents/info")
    def external_agents_info() -> ExternalAgentInfoResponse:
        agents = external_agents.EXTERNAL_AGENTS
        return ExternalAgentInfoResponse(agents=agents, count=len(agents))

    @app.get("/v1/external_agents/info/{agent_type}")
    def external_agent_info(agent_type: str) -> dict:
        agent_info = external_agents.get_agent_info(agent_type)
        if not agent_info:
            raise HTTPException(status_code=404, detail={"error": "Agent type not found", "type": agent_type})
        return {"agent_type": agent_type, **agent_info}

    @app.post("/v1/external_agents/govern")
    def external_agent_govern(req: ExternalAgentGovernRequest) -> ExternalAgentGovernResponse:
        result = external_agents.govern_external_request(
            request=req.request,
            agent_type=req.agent_type,
            agent_id=req.agent_id,
            context=req.context,
            ledger_dir=Path(ledger_dir) if ledger_dir else None,
            source=req.source,
        )
        return ExternalAgentGovernResponse(**result)

    @app.post("/v1/external_agents/tool_check")
    def external_agent_tool_check(req: ExternalAgentToolCheckRequest) -> ExternalAgentGovernResponse:
        result = external_agents.check_external_tool_use(
            tool_name=req.tool_name,
            tool_args=req.tool_args,
            agent_type=req.agent_type,
            agent_id=req.agent_id,
            ledger_dir=Path(ledger_dir) if ledger_dir else None,
            source=req.source,
        )
        return ExternalAgentGovernResponse(**result)

    @app.post("/v1/external_agents/batch_govern")
    def external_agent_batch_govern(req: ExternalAgentBatchGovernRequest) -> ExternalAgentBatchResponse:
        results = external_agents.batch_govern_external(
            requests=req.requests,
            agent_type=req.agent_type,
            agent_id=req.agent_id,
            ledger_dir=Path(ledger_dir) if ledger_dir else None,
            source=req.source,
        )
        return ExternalAgentBatchResponse(results=[ExternalAgentGovernResponse(**r) for r in results], count=len(results))

    @app.get("/v1/external_agents/status")
    def external_agents_status() -> ExternalAgentStatusResponse:
        result = external_agents.get_external_agent_status(ledger_dir=Path(ledger_dir) if ledger_dir else None)
        return ExternalAgentStatusResponse(**result)

    return app


app = create_app()