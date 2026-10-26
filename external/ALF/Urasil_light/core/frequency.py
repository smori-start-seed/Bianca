from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class FrequencyType(Enum):
    AF = "Affective"
    PF = "Performance"
    RF = "Regulation"


@dataclass
class Frequency:
    type: FrequencyType
    value: float
    meta: Dict[str, Any] | None = None


class FrequencyEngine:
    def __init__(self):
        self.state: Dict[FrequencyType, float] = {
            FrequencyType.AF: 0.0,
            FrequencyType.PF: 0.0,
            FrequencyType.RF: 0.0,
        }

    def apply(self, freq: Frequency) -> None:
        self.state[freq.type] += freq.value

    def snapshot(self) -> Dict[FrequencyType, float]:
        return dict(self.state)
