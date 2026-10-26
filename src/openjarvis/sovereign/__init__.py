"""
sovereign — the additive overlay that makes Bianca *Bianca*.

A pure-Python, zero-modification extension of the upstream platform:

  - harmony.py   : the Harmony Framework — the node's soul/metacognition
                   (5 Stages of Finished, agency-preserving output, escalation,
                   telemetry of value/harm/learning).
  - link.py      : the ALF Global Link — capability profile, live zyklus state,
                   and the gold.txt ValueGovernor (verdicts: frei / vorsichtig /
                   symbolisch / zurueckhalten).
  - logger.py    : the Interaction Ledger — human/AI-readable Markdown audits.
  - bridge.py    : attaches the overlay to native platform seams without editing
                   platform code:
                       * before_tool_call governance hook (fail-closed)
                       * harmony-composed ask wrapper
                       * verdict/telemetry reporting

Design rules (same as the original kernel):
  * every layer degrades gracefully — missing ALF data annotates, never blocks;
  * governance is fail-closed — a hook failure DENIES the tool call;
  * nothing here is imported by upstream code; it is purely additive.
"""

from __future__ import annotations

from openjarvis.sovereign.harmony import Harmony, HarmonyIdentity
from openjarvis.sovereign.link import (
    ALFCapabilityProfile,
    CycleStateReader,
    LinkOrchestrator,
    ValueGovernor,
)
from openjarvis.sovereign.logger import InteractionLogger

__all__ = [
    "Harmony",
    "HarmonyIdentity",
    "ALFCapabilityProfile",
    "CycleStateReader",
    "LinkOrchestrator",
    "ValueGovernor",
    "InteractionLogger",
]