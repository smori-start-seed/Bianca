from dataclasses import dataclass
from typing import List, Dict, Any
from .ininity import IninityLog, IninityFragment


@dataclass
class MetaSignal:
    type: str
    intensity: float
    direction: str
    confidence: float
    meta: Dict[str, Any]


class InfinityPatternClassifier:
    def __init__(self, log: IninityLog):
        self.log = log

    def extract_features(self, fragments: List[IninityFragment]) -> Dict[str, float]:
        # Platzhalter: einfache Zählung nach Tags
        features: Dict[str, float] = {}
        for f in fragments:
            features[f.tag] = features.get(f.tag, 0.0) + 1.0
        return features

    def classify(self, features: Dict[str, float]) -> str:
        # Platzhalter: simple Heuristik
        if any("HYPER" in k for k in features):
            return "HYPER_EVENT"
        if any("SING" in k for k in features):
            return "SINGULARITY_EVENT"
        if any("ECO" in k for k in features):
            return "ECOSYSTEM_EVENT"
        return "GENERIC_META"

    def generate_signal(self, cls: str, features: Dict[str, float]) -> MetaSignal:
        intensity = sum(features.values())
        return MetaSignal(
            type=cls,
            intensity=intensity,
            direction="UP",
            confidence=0.5,
            meta={"features": features},
        )

    def run(self) -> MetaSignal | None:
        fragments = self.log.last_n(256)
        if not fragments:
            return None
        features = self.extract_features(fragments)
        cls = self.classify(features)
        return self.generate_signal(cls, features)
