from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Profile:
    id: str
    features: Dict[str, float] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


class ProfileEngine:
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}

    def get_or_create(self, pid: str) -> Profile:
        if pid not in self.profiles:
            self.profiles[pid] = Profile(id=pid)
        return self.profiles[pid]

    def apply_drift(self, pid: str, deltas: Dict[str, float]) -> None:
        p = self.get_or_create(pid)
        for k, dv in deltas.items():
            p.features[k] = p.features.get(k, 0.0) + dv
