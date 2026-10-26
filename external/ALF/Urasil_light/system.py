#system.py

from core.frequency import FrequencyEngine, Frequency, FrequencyType
from core.profile import ProfileEngine
from core.trend import TrendEngine
from core.simulation import SimState, PredictiveFrequencySimulation
from infinity.ininity import IninityLog
from infinity.ipc import InfinityPatternClassifier
from meta.mco import MCO4


class FrequencyEconomySystem:
    def __init__(self):
        self.freq = FrequencyEngine()
        self.profiles = ProfileEngine()
        self.trends = TrendEngine()
        self.pfs = PredictiveFrequencySimulation()
        self.ininity = IninityLog()
        self.ipc = InfinityPatternClassifier(self.ininity)
        self.mco4 = MCO4()

    def tick(self) -> None:
        # 1. Snapshot bauen
        state = SimState(
            frequencies={k.name: v for k, v in self.freq.snapshot().items()},
            profiles={pid: p.features for pid, p in self.profiles.profiles.items()},
            trends={tid: [tp.value for tp in t.points] for tid, t in self.trends.trends.items()},
            meta={},
        )

        # 2. Simulation (4.0 / 5.0+)
        future_seq = self.pfs.simulate_sequence(state, steps=4)
        future = future_seq[-1]

        # 3. Ininity‑Fragment (sehr simpel)
        self.ininity.append("GEN", f"Simulated to step {len(future_seq)}")

        # 4. IPC laufen lassen
        signal = self.ipc.run()
        if signal:
            self.ininity.append("IPC", f"{signal.type} / {signal.intensity}")

        # 5. MCO‑4 auf „Kontinuum“ anwenden (hier nur Dummy‑Daten)
        flows = {"AF": 1.0, "PF": 2.0, "RF": 0.5}
        operators = {"∇F": 1.0, "ΔT": 0.5}
        weights = {"C1": 0.7, "C2": 0.3}
        relations = {"R1": 1.0}
        coherence = 0.9

        adjusted = self.mco4.optimize_continuum(
            flows=flows,
            operators=operators,
            superposition_weights=weights,
            relations=relations,
            coherence=coherence,
        )

        # 6. Optional: adjusted in weitere Logik einspeisen
        self.ininity.append("MCO4", f"coherence={adjusted['coherence']}")
