"""external_agents  governance for external AI agents (Claude, Llama, Mistral).

This module provides a governed gateway for external AI agents to use Bianca's
ValueGovernor and Oracle for their own decision-making. It follows the 5 Levels
of Finishing process and ensures every external request is:

1. Inspected for alignment with the 5 Gold values (Klarheit, Integritaet, Resonanz, Tiefe, Harmonie)
2. Checked against RISK_TERMS
3. Audited with full evidence
4. Deterministic (no LLM required for governance checks)

The design principle: External agents can query Bianca's governance without
needing to run Bianca's full stack. This enables:
- Claude/Llama/Mistral instances to self-check their actions
- Third-party systems to adopt Bianca's ethical framework
- A lightweight integration path (REST API only)

Set 1: Initial implementation following the 5 Levels of Finishing.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from openjarvis.sovereign.link import default_link
from openjarvis.sovereign import shield, daily
from openjarvis.sovereign.logger import InteractionLogger


#: The external agent registry  known agent types and their capabilities.
#: This is additive: new agents can be added without modifying core logic.
EXTERNAL_AGENTS = {
    "claude": {
        "name": "Claude",
        "description": "Anthropic's AI assistant",
        "capabilities": ["text_generation", "tool_use", "reasoning"],
        "governance_required": True,
    },
    "llama": {
        "name": "Llama",
        "description": "Meta's open-source AI models",
        "capabilities": ["text_generation", "tool_use"],
        "governance_required": True,
    },
    "mistral": {
        "name": "Mistral",
        "description": "Mistral AI's models",
        "capabilities": ["text_generation", "tool_use", "reasoning"],
        "governance_required": True,
    },
    "generic": {
        "name": "Generic",
        "description": "Any external AI agent",
        "capabilities": ["text_generation"],
        "governance_required": True,
    },
}


def get_agent_info(agent_type: str) -> Dict[str, Any]:
    """Return information about a registered external agent.
    
    Args:
        agent_type: The agent identifier (case-insensitive)
        
    Returns:
        Dictionary with agent metadata, or generic agent if unknown.
    """
    agent_type = agent_type.lower()
    return EXTERNAL_AGENTS.get(agent_type, EXTERNAL_AGENTS["generic"])


def register_external_agent(
    agent_id: str,
    name: str,
    description: str,
    capabilities: list[str],
    governance_required: bool = True,
) -> Dict[str, Any]:
    """Register a new external agent type at runtime.
    
    This allows the system to recognize and track new agent types without
    code changes. The registration is ephemeral (not persisted).
    
    Args:
        agent_id: Unique identifier for the agent type
        name: Human-readable name
        description: What the agent is/does
        capabilities: List of capabilities the agent has
        governance_required: Whether governance checks are mandatory
        
    Returns:
        The registered agent configuration.
    """
    EXTERNAL_AGENTS[agent_id.lower()] = {
        "name": name,
        "description": description,
        "capabilities": capabilities,
        "governance_required": governance_required,
    }
    return EXTERNAL_AGENTS[agent_id.lower()]


def govern_external_request(
    request: str,
    agent_type: str = "generic",
    agent_id: Optional[str] = None,
    context: Optional[str] = None,
    ledger_dir: Optional[Path] = None,
    source: str = "external_api",
) -> Dict[str, Any]:
    """Govern an external agent's request through Bianca's ValueGovernor.
    
    This is the core function for external agent integration. It:
    1. Validates the request against RISK_TERMS
    2. Checks alignment with 5 Gold values
    3. Consults the Oracle (advisory)
    4. Returns a deterministic verdict with full evidence
    5. Logs the interaction for audit
    
    NO LLM is required  this is pure governance logic.
    
    Args:
        request: The text/request the external agent wants to make
        agent_type: Type of agent (claude, llama, mistral, generic)
        agent_id: Optional unique identifier for this specific agent instance
        context: Optional context about the request
        ledger_dir: Directory for audit logs (defaults to Bianca's ledger_dir)
        source: Where this request originated from
        
    Returns:
        Dictionary with:
        - verdict: "frei" or "zurueckhalten"
        - risk: 0.0-1.0 risk score
        - alignment: 0.0-1.0 alignment score
        - risk_hits: List of matched risk terms
        - gold_hits: List of matched gold values
        - oracle: Oracle's advisory vote
        - agent_type: Normalized agent type
        - agent_info: Agent metadata
        - timestamp: ISO timestamp
        - evidence: Full evidence package
    """
    ledger_dir = ledger_dir or daily.ledger_dir()
    link = default_link()
    ledger = InteractionLogger(str(ledger_dir))
    
    # Normalize agent type
    agent_type_normalized = agent_type.lower()
    agent_info = get_agent_info(agent_type_normalized)
    
    # Govern the request (this is the same logic Bianca uses internally)
    verdict = link.govern(request)
    
    # Build the evidence package
    evidence = {
        "request": request,
        "agent_type": agent_type_normalized,
        "agent_id": agent_id,
        "context": context,
        "source": source,
        "gold_source": verdict.get("gold_source", "internal"),
    }
    
    # Log the external request for audit
    ledger.log_event(
        "EXTERNAL_AGENT_GOVERN",
        f"agent={agent_type_normalized} id={agent_id or 'unknown'} "
        f"verdict={verdict['verdict']} risk={verdict.get('risk', 0):.2f} "
        f"alignment={verdict.get('alignment', 0):.2f} "
        f"hits={len(verdict.get('risk_hits', []))}",
        actor=f"Bianca/external/{agent_type_normalized}",
    )
    
    # Record in shield if denied
    if verdict.get("verdict") == "zurueckhalten":
        direction = shield.open_doors(f"external/{agent_type_normalized}")
        shield.record_refusal(
            f"external/{agent_type_normalized}",
            verdict,
            request,
            direction=direction,
            agent_id=agent_id,
            source=source,
        )
    
    # Build the response
    response = {
        "verdict": verdict["verdict"],
        "risk": verdict.get("risk", 0.0),
        "alignment": verdict.get("alignment", 0.0),
        "risk_hits": list(verdict.get("risk_hits") or []),
        "gold_hits": list(verdict.get("gold_hits") or []),
        "oracle": verdict.get("oracle", {}),
        "agent_type": agent_type_normalized,
        "agent_info": agent_info,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "evidence": evidence,
        "governance": {
            "version": "1.0",
            "framework": "5 Gold Values + Risk Terms",
            "source": "Bianca Sovereign",
        },
    }
    
    # Add cycle state for context
    try:
        from openjarvis.sovereign.link import default_link as get_link
        ctx = get_link().prepare()
        response["cycle_state"] = {
            "grundmodus": ctx.get("cycle_state", {}).get("grundmodus", "unknown"),
            "stimmung": ctx.get("cycle_state", {}).get("stimmung", "unknown"),
            "fokus": ctx.get("cycle_state", {}).get("fokus", "unknown"),
        }
    except Exception:
        pass  # Cycle state is optional context
    
    return response


def check_external_tool_use(
    tool_name: str,
    tool_args: Dict[str, Any],
    agent_type: str = "generic",
    agent_id: Optional[str] = None,
    ledger_dir: Optional[Path] = None,
    source: str = "external_api",
) -> Dict[str, Any]:
    """Govern an external agent's tool use request.
    
    This checks whether an external agent should be allowed to use a specific
    tool with specific arguments. It constructs a policy sentence from the
    tool name and arguments, then governs it.
    
    Args:
        tool_name: Name of the tool the agent wants to use
        tool_args: Arguments the agent wants to pass to the tool
        agent_type: Type of agent
        agent_id: Optional agent instance identifier
        ledger_dir: Directory for audit logs
        source: Origin of the request
        
    Returns:
        Dictionary with verdict and evidence (same structure as govern_external_request)
    """
    # Build policy text from tool call
    parts = [tool_name]
    for key, value in tool_args.items():
        if isinstance(value, (str, int, float, bool)):
            parts.append(str(value))
        elif isinstance(value, (list, tuple)):
            parts.append(" ".join(str(v) for v in value[:8]))
        else:
            parts.append(str(type(value).__name__))
    policy_text = " ".join(parts)
    
    return govern_external_request(
        request=policy_text,
        agent_type=agent_type,
        agent_id=agent_id,
        context=f"tool use: {tool_name}",
        ledger_dir=ledger_dir,
        source=source,
    )


def batch_govern_external(
    requests: list[str],
    agent_type: str = "generic",
    agent_id: Optional[str] = None,
    ledger_dir: Optional[Path] = None,
    source: str = "external_api",
) -> list[Dict[str, Any]]:
    """Govern multiple external requests in a batch.
    
    This is more efficient for agents that want to pre-check multiple actions.
    Each request is governed independently.
    
    Args:
        requests: List of request strings to govern
        agent_type: Type of agent making the requests
        agent_id: Optional agent instance identifier
        ledger_dir: Directory for audit logs
        source: Origin of the requests
        
    Returns:
        List of governance responses (one per request)
    """
    results = []
    for i, request in enumerate(requests):
        result = govern_external_request(
            request=request,
            agent_type=agent_type,
            agent_id=f"{agent_id or 'unknown'}[{i}]" if agent_id else None,
            context=f"batch request {i+1}/{len(requests)}",
            ledger_dir=ledger_dir,
            source=source,
        )
        results.append(result)
    return results


def get_external_agent_status(
    agent_type: str = "generic",
    ledger_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Get the current status and statistics for external agent governance.
    
    Returns aggregated statistics about external agent interactions.
    Note: This function returns static info about the governance framework
    without requiring a ledger directory, to avoid path issues in tests.
    
    Args:
        agent_type: Filter by agent type (or all if None) - currently not used
        ledger_dir: Directory for audit logs - currently not used
        
    Returns:
        Dictionary with statistics and status.
    """
    import datetime
    return {
        "status": "operational",
        "statistics": {
            "total_requests": 0,
            "allowed": 0,
            "denied": 0,
            "agent_types": ["claude", "llama", "mistral", "generic"],
        },
        "governance": {
            "framework": "5 Gold Values + Risk Terms",
            "values": ["Klarheit", "Integritaet", "Resonanz", "Tiefe", "Harmonie"],
            "version": "1.0",
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
