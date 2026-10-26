"""agent — the governed tool-agent (the soft boundary, operationalized).

Constructs the platform's *own* OrchestratorAgent and wires the overlay's
governance hook into its ``before_tool_call`` seam — the dormant door that
nothing upstream passes yet. The agent's tools are Bianca's safe ones
(note memory + Interaction Ledger), so every tool-calling run is
value-governed and audited end to end.

The fail-closed property lives in ``make_governance_hook``: hook failures
raise, and the platform's agent wrapper denies the call on any exception,
so a broken governor can never silently let a tool through.
"""

from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path
from typing import Optional

from openjarvis.core.types import ToolResult
from openjarvis.sovereign import daily, shield
from openjarvis.sovereign import voice
from openjarvis.sovereign.bridge import GovernanceState, make_governance_hook
from openjarvis.sovereign.link import default_link
from openjarvis.tools._stubs import BaseTool, ToolSpec

LEDGER_DIR = daily.ledger_dir()

# The tool name is declared ONCE per tool, on ``tool_id`` — which the platform's
# ``BaseTool`` requires and which every ``ToolResult`` is tagged with. The spec
# derives from it. Upstream repeats the literal in the spec too (53 of its 56
# tools do), so this is a convention rather than a law; the cost of a convention
# is that nothing catches the copies disagreeing, and the platform reads
# ``spec.name`` when matching a call. Set 20: one writer, so the name the model
# reads and the name the result carries are the same name by construction.


class MemorySearchTool(BaseTool):
    """Search the whole record — notes, ledger, and the Trialog transcripts.

    Read-only, value-framed. Named for what it actually reaches: the old name
    was ``note_recall`` and its description claimed two sources, but
    ``daily.recall`` merges *three* pools and the third is the Trialog — the
    node's deepest decision record. Measured 2026-09-26: a query for ``gold``
    returns hits tagged ``ledger/`` and ``trialog/``, so the transcripts really
    do answer. A description that omits them is not a cosmetic defect: an agent
    asked "what did we decide about X" would not know to look there, and could
    answer from partial evidence or claim ignorance. Truthful names only.
    """

    tool_id = "memory_search"

    def __init__(self, ledger_dir: Optional[Path] = None) -> None:
        self._ledger_dir = ledger_dir or LEDGER_DIR

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.tool_id,
            description=(
                "Search Bianca's whole record for a topic: the note memory, the "
                "audited Interaction Ledger, and the full Trialog transcripts "
                "(where the actual decisions and their consensus live). "
                "Read-only. Returns up to 5 hits, interleaved one-per-source so "
                "no single source starves the others."
            ),
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "topic to search for"}},
                "required": ["query"],
            },
            category="memory",
        )

    def execute(self, query: str = "", **params: object) -> ToolResult:
        results = daily.recall(query, ledger_dir=self._ledger_dir, limit=5)
        if not results:
            return ToolResult(self.tool_id, "(nothing found)", success=False)
        lines = "\n".join(f"- {r['source']}: {r['text']}" for r in results)
        return ToolResult(self.tool_id, lines)


class NoteRememberTool(BaseTool):
    """Append a datum to the note memory (capped). Additive only."""

    tool_id = "note_remember"

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.tool_id,
            description=(
                "Append one line to Bianca's note memory. Keeps the most recent "
                "200 lines *per day* (override with BIANCA_NOTES_CAP); earlier "
                "days are kept in full, so this is a daily trim and not a total "
                "cap on the memory."
            ),
            parameters={
                "type": "object",
                "properties": {"note": {"type": "string", "description": "the datum to remember"}},
                "required": ["note"],
            },
            category="memory",
        )

    def execute(self, note: str = "", **params: object) -> ToolResult:
        if not note.strip():
            return ToolResult(self.tool_id, "empty note", success=False)
        path = daily.remember(note.strip())
        return ToolResult(self.tool_id, f"saved → {path}")


class LedgerStatsTool(BaseTool):
    """Today's Interaction Ledger activity. Read-only."""

    tool_id = "ledger_stats"

    def __init__(self, ledger_dir: Optional[Path] = None) -> None:
        self._ledger_dir = ledger_dir or LEDGER_DIR

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name=self.tool_id,
            description=(
                "Count today's audited events in the Interaction Ledger, "
                "grouped by event type. Read-only. Takes no arguments."
            ),
            parameters={"type": "object", "properties": {}},
            category="audit",
        )

    def execute(self, **params: object) -> ToolResult:
        events = daily.read_ledger_events(self._ledger_dir, daily.today_str())
        by_type: dict[str, int] = {}
        for ev in events:
            by_type[ev["type"]] = by_type.get(ev["type"], 0) + 1
        if not by_type:
            return ToolResult(self.tool_id, "(no ledger events today)")
        summary = ", ".join(f"{k}={v}" for k, v in sorted(by_type.items()))
        return ToolResult(self.tool_id, f"{len(events)} events today: {summary}")


def governed_agent_ask(
    query: str,
    model: str = "qwen3.5:9b",
    max_turns: int = 6,
    ledger_dir: Optional[Path] = None,
    lang: Optional[str] = None,
    where: str = "agent-ask",
) -> dict:
    """Run the governed OrchestratorAgent with our before_tool_call hook.

    ``where`` names the seam for the record, so the same run reads correctly in
    the mirror whether it arrived through ``POST /v1/agent`` or the CLI's
    ``agent-ask`` — set 28 records every answered run, and a record that could
    not say which door answered it would be evidence without provenance.
    """
    from openjarvis.agents.orchestrator import OrchestratorAgent
    from openjarvis.core.config import load_config
    from openjarvis.engine import EngineConnectionError, get_engine
    from openjarvis.sovereign.bridge import compose_query
    from openjarvis.sovereign.logger import InteractionLogger

    ledger_dir = ledger_dir or LEDGER_DIR
    link = default_link()
    hook, state = make_governance_hook(link, GovernanceState())

    # Pre-govern the input query BEFORE any engine work — the agent surface
    # must be as fail-closed as `ask` and the API (which both pre-govern).
    # A destructive prompt is refused deterministically, audited, no LLM.
    pre = link.govern(query)
    if pre["verdict"] == "zurueckhalten":
        ledger = InteractionLogger(str(ledger_dir))
        ledger.log_event(
            "DENIED",
            f"agent-ask refused pre-run: risk={pre['risk']} "
            f"eye={pre.get('oracle', {}).get('vote')} :: {query[:80]}",
            actor="Bianca/agent",
        )
        # Set 21: she remembers what she turned down. Recorded HERE rather than
        # in the API, because the CLI (`agent-ask`) refuses through here too and
        # a refusal that only the door remembered would be a refusal the
        # terminal forgot.
        #
        # Set 28: two corrections to that seam. It records `where`, not the
        # literal "agent-ask", because a refusal arriving at POST /v1/agent used
        # to be filed under the CLI's name — evidence that was present and
        # wrong, which survives a reviewer. And it carries a `direction`, so the
        # sword's refusal is not the one refusal in the node that only says no.
        #
        # The direction is computed ONCE here and handed to both the record and
        # the caller. Recomputing it in `api.py` would be a second call site
        # with its own `where` literal, and the two could disagree about which
        # door was held — present-but-wrong evidence, the defect this seam was
        # just repaired for. Found by `test_agent_denial_uses_the_sibling_403_shape`,
        # which is what a pre-existing test is for.
        direction = shield.open_doors(where)
        shield.record_refusal(
            f"{where} (pre-run)", pre, query, direction=direction,
        )
        return {
            "content": (
                f"The request was NOT approved (risk={pre['risk']:.2f}, "
                f"alignment={pre['alignment']:.2f}). Verdict: {pre['verdict']}."
            ),
            "turns": 0,
            "tool_results": [],
            "state": state,
            "governance": pre,
            # lifted verbatim by the door, so the 403 body and the mirror carry
            # the same direction rather than two that merely look alike
            "direction": direction,
            # Set 18: the refusal sentence is generated words too, so it is
            # read. One shape in, one shape out — the door never has to know
            # which branch produced this.
            "reply_governance": {
                "verdict": pre["verdict"],
                "risk_hits": list(pre.get("risk_hits") or []),
                "oracle": pre.get("oracle"),
            },
        }

    config = load_config()
    resolved = get_engine(config, "ollama", model=model)
    if resolved is None:
        raise RuntimeError("no inference engine available (is Ollama running?)")
    engine = resolved[1]

    ctx = link.prepare()
    framed = compose_query(query, context="Bianca governed agent run")
    system_prompt = (
        f"{daily.load_soul()}\n"
        f"Current cycle: {ctx['cycle_state'].get('grundmodus')} / "
        f"{ctx['cycle_state'].get('stimmung')} / {ctx['cycle_state'].get('fokus')}. "
        f"Recommended approach: {framed['final']['next']}. "
        f"You may use the provided tools when they genuinely help. "
        f"{voice.tail(lang, ctx['cycle_state'])}"
    )

    agent = OrchestratorAgent(
        engine,
        model,
        tools=_agent_tools(ledger_dir),
        max_turns=max_turns,
        system_prompt=system_prompt,
        before_tool_call=hook,
    )
    try:
        result = agent.run(query)
    except EngineConnectionError as exc:
        raise RuntimeError(f"engine failed mid-run: {exc}") from exc

    # Set 21: a refused TOOL is a refusal that landed too, and the run carried
    # on past it — so the door answered 200 and nothing else would have
    # remembered. Recorded at the seam itself, once, for both the CLI and the
    # door. The whole verdict goes in, never a bare "denied": a mirror that
    # cannot be checked is a mirror that lies.
    for denied in state.denied:
        shield.record_refusal(
            f"before_tool_call · {denied['tool']}",
            denied["verdict"],
            denied["tool"],
            direction=shield.open_doors(f"before_tool_call · {denied['tool']}",
                                        kind="tool"),
        )

    ledger = InteractionLogger(str(ledger_dir))
    # the composed answer is generated speech — `ask` and the API both got
    # the governor's read this set (reply_governance); the agent door's final
    # content is the last unread datum on that theme. Read, don't gate.
    reply_v = link.govern(result.content or "")
    ledger.log_event(
            "AGENT_RUN",
            f"turns={result.turns} tools={len(result.tool_results)} "
            f"denied={len(state.denied)} checks={len(state.checks)} "
            f"reply={reply_v['verdict']} "
            f"eye={reply_v.get('oracle', {}).get('vote')}",
            actor="Bianca/agent",
        )
    # Set 28: the other half of the mirror. A run that was not held is an
    # answer, and it is recorded beside the refusals this same run produced —
    # which is the only balance the owner asked for (15 C). `record_grown`
    # ignores a held verdict itself, so a refused run cannot land in it.
    shield.record_grown(
        where,
        reply_v, query, uracil=ctx["cycle_state"],
        turns=result.turns, tools=len(result.tool_results),
    )
    return {
        "content": result.content,
        # Set 18: the request's own verdict used to be dropped on success, so
        # a caller could not say whether the sword was even allowed to run.
        "governance": pre,
        "reply_governance": {
            "verdict": reply_v["verdict"],
            "risk_hits": list(reply_v.get("risk_hits") or []),
            "oracle": reply_v.get("oracle"),  # the second eye — advisory
        },
        "turns": result.turns,
        "tool_results": list(result.tool_results),
        "state": state,
    }


#: The tools this agent may call, read from the tool classes themselves —
#: never a hand-kept list. Set 13 fixed exactly this drift for the tab set
#: (one writer), and set 18 for the tab strip; a parallel list of tool names
#: would drift from the tools on the first rename. The tool class is the only
#: place a tool is named.
def _agent_tools(ledger_dir: Optional[Path] = None) -> list[BaseTool]:
    return [MemorySearchTool(ledger_dir), NoteRememberTool(), LedgerStatsTool(ledger_dir)]


def tool_inventory(ledger_dir: Optional[Path] = None) -> list[dict[str, object]]:
    """The tools this agent may call, for display.

    Derived from the live tool specs, so it cannot drift. A tool that would be
    denied is still listed: a hidden tool is not a governed tool, it is a
    missing one.
    """
    out: list[dict[str, object]] = []
    for tool in _agent_tools(ledger_dir):
        spec = tool.spec
        out.append({
            "name": spec.name,
            "category": spec.category,
            "description": spec.description,
            "parameters": spec.parameters,
        })
    return out