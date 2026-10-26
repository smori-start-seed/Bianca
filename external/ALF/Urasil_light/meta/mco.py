from typing import List, Dict
from .metacmd import MetaCmd


class MetaCmdOptimizerBase:
    def optimize(self, cmds: List[MetaCmd]) -> List[MetaCmd]:
        raise NotImplementedError


class MCO1(MetaCmdOptimizerBase):
    def optimize(self, cmds: List[MetaCmd]) -> List[MetaCmd]:
        return sorted(cmds, key=lambda c: c.score, reverse=True)


class MCO2(MetaCmdOptimizerBase):
    def optimize(self, cmds: List[MetaCmd]) -> List[MetaCmd]:
        # Kontextabhängige Filter/Regeln – Platzhalter
        return cmds


class MCO3(MetaCmdOptimizerBase):
    def __init__(self):
        self.history: List[List[MetaCmd]] = []

    def optimize(self, cmds: List[MetaCmd]) -> List[MetaCmd]:
        self.history.append(cmds)
        # Lern-/Heuristiklogik hier
        return cmds


# 🔥 MCO‑4: Hyperpositions‑Optimierer
class MCO4:
    """
    Kein klassischer Cmd-Optimizer mehr.
    Arbeitet auf Flüssen, Operatoren, Superpositionen.
    """

    def __init__(self):
        self.last_coherence: float | None = None

    def optimize_continuum(
        self,
        flows: Dict[str, float],
        operators: Dict[str, float],
        superposition_weights: Dict[str, float],
        relations: Dict[str, float],
        coherence: float,
    ) -> dict:
        # Hier nur ein Gerüst – du kannst jede Logik einsetzen
        adjusted_flows = dict(flows)
        adjusted_ops = dict(operators)
        adjusted_weights = dict(superposition_weights)
        adjusted_relations = dict(relations)

        # Beispiel: leichte Normalisierung
        def normalize(d: Dict[str, float]) -> Dict[str, float]:
            s = sum(abs(v) for v in d.values()) or 1.0
            return {k: v / s for k, v in d.items()}

        adjusted_flows = normalize(adjusted_flows)
        adjusted_ops = normalize(adjusted_ops)
        adjusted_weights = normalize(adjusted_weights)

        self.last_coherence = coherence

        return {
            "flows": adjusted_flows,
            "operators": adjusted_ops,
            "weights": adjusted_weights,
            "relations": adjusted_relations,
            "coherence": coherence,
        }
