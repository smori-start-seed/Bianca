"""
bridge — attaches the Sovereign overlay to native platform seams.

Additive by design: we never edit upstream platform code. We plug into the
seams the platform already exposes:

  Seam 1 — ``before_tool_call(tool_name, tool_args) -> bool``
      OrchestratorAgent calls this hook before executing any tool. It is
      FAIL-CLOSED: a hook exception denies the tool. We return False when the
      ValueGovernor verdict is ``zurueckhalten`` (high risk).

  Seam 2 — harmony-composed ask
      ``compose_query`` runs the user's request through the Harmony pipeline
      (resonate/root/pulse -> decision -> options -> final) so every Bianca
      exchange is agency-preserving, max 3 options, recommended-path-first.

  Seam 3 — verdict + telemetry reporting
      ``report`` records value created / harm avoided / learning generated
      into the Interaction Ledger (same readable Markdown format as the kernel).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from openjarvis.sovereign.harmony import Harmony
from openjarvis.sovereign.link import LinkOrchestrator, default_link
from openjarvis.sovereign.logger import InteractionLogger


class GovernanceState:
    """Mutable state a hooked agent can inspect after a run."""

    def __init__(self) -> None:
        self.checks: List[Dict[str, Any]] = []
        self.denied: List[Dict[str, Any]] = []

    def record(self, tool_name: str, verdict: Dict[str, Any]) -> None:
        """Record one tool judgement — with its evidence, never without it.

        Set 18: this used to take a bare verdict string plus a bool, so a
        denied tool call could only ever render as "denied" with no reason.
        The evidence rule says a refusal must show the verdict, the stems
        that tripped it, where the values were read from, and the second eye.
        A tool refusal is a refusal, so the whole verdict is kept here.
        """
        self.checks.append({"tool": tool_name, "verdict": verdict})
        if verdict.get("verdict") == "zurueckhalten":
            self.denied.append({"tool": tool_name, "verdict": verdict})


def make_governance_hook(
    link: Optional[LinkOrchestrator] = None,
    state: Optional[GovernanceState] = None,
) -> tuple[Callable[[str, Dict[str, Any]], bool], GovernanceState]:
    """
    Build a ``before_tool_call``-compatible hook.

    The hook builds a policy sentence from the tool name + arguments and asks
    the ValueGovernor for a verdict. Only ``zurueckhalten`` is denied outright;
    every other verdict passes (governance annotates; boundaries enforce).
    Hook failures raise -> the platform's fail-closed wrapper denies the call.
    """
    link = link or default_link()
    state = state or GovernanceState()

    def hook(tool_name: str, tool_args: Dict[str, Any]) -> bool:
        parts = [tool_name]
        for value in dict(tool_args or {}).values():
            if isinstance(value, (str, int, float, bool)):
                parts.append(str(value))
            elif isinstance(value, (list, tuple)):
                parts.append(" ".join(str(v) for v in value[:8]))
        policy_text = " ".join(parts)
        verdict = link.govern(policy_text)
        allowed = verdict["verdict"] != "zurueckhalten"
        state.record(tool_name, verdict)
        return allowed

    return hook, state


def compose_query(
    user_input: str,
    intent: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    context: str = "Bianca node on the mycelium net",
    options: Optional[List[str]] = None,
    harmony: Optional[Harmony] = None,
) -> Dict[str, Any]:
    """
    Run a user request through the Harmony pipeline.

    Returns the full compose dict (decision/prediction/creativity/validation/
    explanation/final). Options default to a gentle sovereign framing so the
    output is always agency-preserving.
    """
    h = harmony or Harmony()
    intent = intent or user_input
    options = options or [
        f"Address '{user_input}' directly.",
        "Reframe the request into its smallest proof of value.",
        "Pause and gather more context first.",
    ]
    return h.compose(
        user_input=user_input,
        intent=intent,
        constraints=constraints or [],
        context=context,
        options=options,
    )


def report(
    ledger: InteractionLogger,
    value: str = "",
    harm: str = "",
    learning: str = "",
    extra: Optional[str] = None,
) -> str:
    """Report telemetry into the Interaction Ledger and return the log path."""
    msg = f"value={value or '—'} | harm_avoided={harm or '—'} | learning={learning or '—'}"
    if extra:
        msg = f"{msg} | {extra}"
    return ledger.log_event("TELEMETRY", msg, actor="Bianca/sovereign")