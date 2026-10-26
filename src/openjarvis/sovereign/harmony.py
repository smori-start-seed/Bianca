"""
Harmony Framework — the local metacognition of the Bianca node.
Ported verbatim from the OpenJarvis kernel (OpenJarvis/kernel/harmony.py).

See the Harmony spec: identity & scope, prime directive (fun as the tone of
existence), ethics whitelist, meta-command hierarchy, bridge & root functions,
pipeline, Five Stages of Finished, 90-day cycle (30-day micro-cycle),
escalation signal, telemetry, and output format (max 3 options, recommended
first, agency-preserving "maybe").
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Identity & Scope
# ---------------------------------------------------------------------------

class HarmonyIdentity:
    """Static identity of the Harmony agent."""

    LANGUAGE = "en-US"
    TONE = "warm, light, clear"
    PRIME_DIRECTIVE = "Fun as the tone of existence."
    ETHICS_WHITELIST = ("fun", "existence", "good-light-laughter", "togetherness")
    META_COMMAND_HIERARCHY = ("fun", "play", "maybe", "beyond", "anything")


# ---------------------------------------------------------------------------
# Exit codes / enums for stage checks
# ---------------------------------------------------------------------------

RISK_LEVELS = ("low", "medium", "high")

STAGES = ("frame", "forge", "fit", "field", "flow")

STAGE_GATE_QUESTIONS = {
    "frame": "What would make this not worth finishing?",
    "forge": "What is the smallest proof of value?",
    "fit": "Who is impacted and how do they consent?",
    "field": "What will we measure and what will we stop if the signal is bad?",
    "flow": "What deserves continued care, and what deserves a graceful end?",
}


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------

@dataclass
class Telemetry:
    value_created: str = ""
    harm_avoided: str = ""
    learning_generated: str = ""
    negative_streak: int = 0

    def as_dict(self) -> Dict[str, str]:
        return {
            "value_created": self.value_created,
            "harm_avoided": self.harm_avoided,
            "learning_generated": self.learning_generated,
        }


# ---------------------------------------------------------------------------
# The Harmony agent
# ---------------------------------------------------------------------------

class Harmony:
    def __init__(self, identity: Optional[HarmonyIdentity] = None):
        self.identity = identity or HarmonyIdentity()
        self.telemetry = Telemetry()
        self.in_progress: Dict[str, int] = {s: 0 for s in STAGES}  # WIP counter
        self.max_wip_per_stage = 2
        self.cycle_days = 90

    # -- Bridge & Root Functions ---------------------------------------------

    def resonate(self, intent: str, constraints: List[str], context: str) -> dict:
        """Align with intent, constraints, and context (the 'why')."""
        return {
            "intent": intent,
            "constraints": list(constraints),
            "context": context,
            "tone": self.identity.TONE,
        }

    def root(self, reality: str) -> dict:
        """Ground in reality and constraints (the 'is')."""
        return {"grounding": reality, "assumption_note": "Roughly calculated unless verified."}

    def pulse(self, signals: List[str]) -> dict:
        """Sense signals, risks, energy (the 'watch')."""
        risks = [s for s in signals if s.lower() in ("risk", "danger", "blocked", "medium", "high")]
        return {"signals": list(signals), "risks_detected": risks}

    def flow(self, steps: List[str]) -> List[str]:
        """Simplify, reduce friction, timebox. SUBTRACTION-FIRST: remove before adding."""
        # Minimal friction-avoiding heuristic: drop empty/redundant steps first.
        unique = list(dict.fromkeys(s.strip() for s in steps if s.strip()))
        if len(unique) > 3:
            unique = unique[:3]  # timebox: keep it short
        return unique

    def spark(self, options: List[str], max_options: int = 3) -> List[str]:
        """Inject novelty, propose vivid options. HARD LIMIT: max 3."""
        return options[:max_options]

    def song(self, narrative: str) -> str:
        """Maintain narrative coherence (the 'thread')."""
        return narrative.strip()

    # -- Agency-preserving constraint helpers ---------------------------------

    def maybe(self, statement: str) -> str:
        """Agency-preserving phrasing: propose, don't impose."""
        return f"maybe {statement}"

    # -- Pipeline -------------------------------------------------------------

    def compose(self, user_input: str, intent: str, constraints: List[str],
                context: str, options: List[str], grounding: str = "") -> dict:
        """
        Pipeline: [User Input] -> Harmony (resonate, root, pulse) -> Decision
        -> maybe Prediction -> Creativity -> Validation -> Explanation -> Final
        """
        decision = self.flow(self._decide_steps(intent, context, options))

        # creativity = options, limited to max 3
        creativity = self.spark(options)

        validation = self._validate(intent, creativity)

        explanation = (
            f"Resonated with '{intent}' within '{context}'. "
            f"Constraints respected: {len(constraints)}. "
            "Assumptions stated; ask only if truly blocking."
        )

        final = self._final_step(creativity)

        return {
            "decision": decision,
            "prediction": self._prediction(intent, creation_options=creativity),
            "creativity": creativity,
            "validation": validation,
            "explanation": explanation,
            "final": final,
        }

    # -- internal pipeline helpers --------------------------------------------

    def _decide_steps(self, intent: str, context: str, options: List[str]) -> List[str]:
        # Decision = plan, 1-3 steps, lead with recommended path.
        steps = [f"{options[0] if options else 'Resonate and define intent'} (recommended)"]
        if len(options) > 1:
            steps.append(self.maybe(options[1]))
        if len(options) > 2:
            steps.append(self.maybe(options[2]))
        steps.append(f"Stop when outcome for '{intent}' is true.")
        return steps

    def _prediction(self, intent: str, creation_options: List[str]) -> str:
        # Brief outcomes/risks. Keep it grounded and honest.
        return (f"Expected: shared clarity and a thin, testable slice. "
                f"Risk if ignored: drifting from '{intent}'.")

    def _validate(self, intent: str, creativity: List[str]) -> list:
        # Validation = checks.
        checks = [
            "Ethics whitelist respected (fun / existence / good-light-laughter / togetherness).",
            "Current zyklus of the ecosystem considered.",
        ]
        return checks

    def _final_step(self, creativity: List[str]) -> dict:
        # Final = actionable next step + up to 2 alternatives.
        return {
            "next": creativity[0] if creativity else "Compose the smallest proof of value.",
            "alternatives": creativity[1:3],
        }

    # -- Five Stages of Finished ----------------------------------------------

    def begin_stage(self, stage: str, scope: str) -> dict:
        """Open a stage and return its gate question."""
        if stage not in STAGES:
            raise ValueError(f"Unknown stage '{stage}'. Valid: {STAGES}")
        if self.in_progress[stage] >= self.max_wip_per_stage:
            return {"allowed": False, "reason": f"WIP limit reached for stage '{stage}' (max {self.max_wip_per_stage})."}
        self.in_progress[stage] += 1
        return {
            "allowed": True,
            "stage": stage,
            "scope": scope,
            "gate_question": STAGE_GATE_QUESTIONS[stage],
            "finish_pledge": self._finish_pledge(scope),
        }

    def _finish_pledge(self, scope: str) -> str:
        return (f"Stop when [the {scope} outcome is achieved] is true; "
                f"else sunset or re-frame.")

    def close_stage(self, stage: str) -> None:
        if self.in_progress.get(stage, 0) > 0:
            self.in_progress[stage] -= 1

    def cycle_calendar(self, total_days: Optional[int] = None) -> List[dict]:
        """90-day cycle template (compressible to a 30-day micro-cycle)."""
        days = total_days or self.cycle_days
        bounds = [(1, 7), (8, 30), (31, 45), (46, 75), (76, 90)]
        if days <= 30:
            # 30-day micro-cycle for small scopes
            bounds = [(1, 3), (4, 10), (11, 15), (16, 25), (26, 30)]
        return [
            {"stage": s, "days": f"{lo}-{hi}"}
            for s, (lo, hi) in zip(STAGES, bounds)
        ]

    # -- Escalation -----------------------------------------------------------

    def escalate(self, risk_level: str, telemetry_negative_twice: bool = False) -> str:
        """
        If ethics/consent/coherence risk >= medium OR telemetry negative twice
        -> sparkle-escalate: pause, notify, propose 1-2 mitigations, decide in 72h.
        Low risk -> advisory only.
        """
        if risk_level in ("medium", "high") or telemetry_negative_twice:
            return (
                "sparkle-escalate: PAUSE. Notify stakeholders. Propose 1-2 "
                "mitigations. Decide within 72h."
            )
        return "advisory: continue with awareness (no full pause)."

    # -- Telemetry ------------------------------------------------------------

    def report_telemetry(self, value: str, harm: str, learning: str,
                         was_negative: bool = False) -> dict:
        self.telemetry.value_created = value
        self.telemetry.harm_avoided = harm
        self.telemetry.learning_generated = learning
        if was_negative:
            self.telemetry.negative_streak += 1
        else:
            self.telemetry.negative_streak = 0
        return self.telemetry.as_dict()