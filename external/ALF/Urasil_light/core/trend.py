from dataclasses import dataclass
from typing import List


@dataclass
class TrendPoint:
    t: float
    value: float


@dataclass
class Trend:
    id: str
    points: List[TrendPoint]


class TrendEngine:
    def __init__(self):
        self.trends: dict[str, Trend] = {}

    def add_point(self, tid: str, t: float, value: float) -> None:
        if tid not in self.trends:
            self.trends[tid] = Trend(id=tid, points=[])
        self.trends[tid].points.append(TrendPoint(t=t, value=value))
