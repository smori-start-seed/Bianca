# Urasil_light/core/alf_bridge.py

from core.identity import Identity
from core.zyklus import Zyklus
from core.seed import Seed
from core.silky_edge import SilkyEdge
from core.erfahrung import Erfahrung
from core.interpretation import Interpretation
from core.rueckmeldung import Rueckmeldung

class UrasilAgent:
    def __init__(self):
        self.identity = Identity.load()
        self.zyklus = Zyklus(self.identity.data)
        self.seed = Seed(self.identity, self.zyklus)
        self.se = SilkyEdge(self.identity, self.zyklus)
        self.interpretation = Interpretation(self.identity, self.zyklus)
        self.erfahrung = Erfahrung(self.identity, self.zyklus)
        self.rueck = Rueckmeldung(self.identity, self.zyklus)

    def decide(self, world_meaning: dict) -> dict:
        # hier kannst du später komplexer werden
        decision = {}

        if world_meaning.get("chaos"):
            decision["increase_harmony"] = True
        if world_meaning.get("energie_low"):
            decision["inject_noise"] = True
        if world_meaning.get("drift_hoch"):
            decision["increase_harmony"] = True

        return decision

