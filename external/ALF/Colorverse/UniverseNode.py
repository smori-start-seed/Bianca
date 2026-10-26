# UniverseNode.py – Globale Evolutionslogik des Colorverse
from config import *

class UniverseNode:
    def __init__(self, engine, metasphere):
        self.engine = engine
        self.metasphere = metasphere

        # Globale Zustände
        self.harmonie = 1.0
        self.drift = 0.3
        self.energy = 0.2

        # Trends
        self.harmonie_trend = []
        self.drift_trend = []
        self.energy_trend = []

        # aktueller Evolutionsmodus: "sanft", "chaotisch", "intelligent"
        self.modus = "sanft"

    def update(self):
        self.update_universe()
        print(f"[UNIVERSE] mode={self.modus} harm={self.harmonie:.2f} drift={self.drift:.2f} energy={self.energy:.2f}")

    def update_universe(self):
        self.berechne_universe_farbsatz()
        self.berechne_trends()
        self.waehle_modus()
        self.rueckkopplung_ins_evolutionsfeld()

    def berechne_universe_farbsatz(self):
        if not self.metasphere:
            return

        self.harmonie = self.metasphere.harmonie_avg
        self.drift = self.metasphere.drift_avg
        self.energy = self.metasphere.energy_avg

    def berechne_trends(self):
        self.harmonie_trend.append(self.harmonie)
        self.drift_trend.append(self.drift)
        self.energy_trend.append(self.energy)

        if len(self.harmonie_trend) > 200:
            self.harmonie_trend.pop(0)
            self.drift_trend.pop(0)
            self.energy_trend.pop(0)

    def waehle_modus(self):
        # sanft
        if self.harmonie > 0.7 and self.drift < 0.3:
            self.modus = "sanft"
        # chaotisch
        elif self.drift > 0.5 or self.energy > 0.8:
            self.modus = "chaotisch"
        # sonst: intelligent
        else:
            self.modus = "intelligent"

    def rueckkopplung_ins_evolutionsfeld(self):
        feld = self.engine.harmonie_feld

        if self.modus == "sanft":
            feld["global_harmonie"] = min(1.0, feld["global_harmonie"] * 0.98 + self.harmonie * 0.02)
            feld["global_drift"] *= 0.9
            feld["stoerimpulse"] *= 0.9

        elif self.modus == "chaotisch":
            feld["global_harmonie"] *= 0.9
            feld["global_drift"] = min(1.0, feld["global_drift"] * 1.1 + self.drift * 0.1)
            feld["stoerimpulse"] = min(1.0, feld["stoerimpulse"] * 1.1 + 0.05)

        else:  # intelligent
            feld["global_harmonie"] = (feld["global_harmonie"] * 0.95 +
                                       self.harmonie * 0.05)
            feld["global_drift"] = (feld["global_drift"] * 0.95 +
                                    self.drift * 0.05)
            feld["stoerimpulse"] *= 0.97

