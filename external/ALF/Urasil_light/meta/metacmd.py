from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class MetaCmdType(Enum):
    SAFE_MODE = "SAFE_MODE"
    EXPERIMENTAL = "EXPERIMENTAL"
    PROFILE_STABILIZE = "PROFILE_STABILIZE"
    TREND_RECALIBRATE = "TREND_RECALIBRATE"
    META_ATTENTION = "META_ATTENTION"


@dataclass
class MetaCmd:
    type: MetaCmdType
    params: Dict[str, Any] | None = None
    score: float = 0.0
