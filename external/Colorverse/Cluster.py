import math
# Cluster.py – Harmonische Aggregation zwischen Zelle und Ring
from config import *

class Cluster:
    def __init__(self, zellen, engine=None):
        if len(zellen) < 1 or len(zellen) > 11:
            raise ValueError("Ein Cluster besteht aus 1 bis 11 Zellen (Set 40).")

        self.zellen = list(zellen)
        self.engine = engine

        # Aggregierte Werte (für Ring + Sphere)
        self.hue_avg = 0.0
        self.sat_avg = 0.0
        self.bri_avg = 0.0
        self.energy_avg = 0.0

        # Meta-Werte
        self.harmonie_avg = 0.0
        self.drift_avg = 0.0
        self.varianz = 0.0

        # Farbsatz (für get_farbsatz)
        self.farbsatz_hue = 0.0
        self.farbsatz_saturation = 0.0
        self.farbsatz_brightness = 0.0

    # ---------------------------------------------------------
    # Öffentliche Update-Methode
    # ---------------------------------------------------------
    def update(self):
        self.update_cluster()

        # interne Hex-Stabilisierung
        for i, z in enumerate(self.zellen):
            left = self.zellen[(i - 1) % len(self.zellen)]
            right = self.zellen[(i + 1) % len(self.zellen)]
            z.nachbarn = [left, right]

    # ---------------------------------------------------------
    # 1. Update aller Zellen + Mutation
    # ---------------------------------------------------------
    def update_cluster(self):

        # 1.1 Zellen updaten
        for z in self.zellen:
            z.update()

        # 1.2 Clusterwerte berechnen
        self.berechne_clusterwerte()
        self.berechne_farbsatz()

        # 1.3 Mutation anwenden
        self.mutation()

    # ---------------------------------------------------------
    # 2. Clusterwerte berechnen
    # ---------------------------------------------------------
    def berechne_clusterwerte(self):
        hues = [z.hue for z in self.zellen]
        sats = [z.saturation for z in self.zellen]
        bris = [z.brightness for z in self.zellen]
        energies = [z.energy for z in self.zellen]
        drifts = [z.drift for z in self.zellen]
        harmonien = [z.harmonie for z in self.zellen]

        # Durchschnittswerte
        self.hue_avg = sum(hues) / len(hues)
        self.sat_avg = sum(sats) / len(sats)
        self.bri_avg = sum(bris) / len(bris)
        self.energy_avg = sum(energies) / len(energies)

        self.drift_avg = sum(drifts) / len(drifts)
        self.harmonie_avg = sum(harmonien) / len(harmonien)

        # Varianz für Farbdynamik
        self.varianz = sum((h - self.hue_avg)**2 for h in hues) / len(hues)

    # ---------------------------------------------------------
    # 3. Farbsatz berechnen (für Ring)
    # ---------------------------------------------------------
    def berechne_farbsatz(self):
        self.farbsatz_hue = (self.hue_avg + (self.varianz / 180.0) * 5.0) % 360
        self.farbsatz_saturation = max(0.0, min(1.0, self.sat_avg + 0.1 * (self.harmonie_avg - 0.5)))
        self.farbsatz_brightness = max(0.0, min(1.0, self.bri_avg - 0.1 * self.drift_avg))

    # ---------------------------------------------------------
    # 4. Mutation
    # ---------------------------------------------------------
    def mutation(self):
        if self.engine is None:
            return

        # Kern
        kern = self.zellen[:min(3, len(self.zellen))]
        for z in kern:
            z.drift *= 0.8
            z.harmonie = min(1.0, z.harmonie + 0.05)

        # Sub-Moleküle
        if len(self.zellen) > 3:
            sub = self.zellen[3:min(10, len(self.zellen))]
            for z in sub:
                z.hue += z.drift * 2.0
                z.saturation += (z.energy - 0.5) * 0.05
                if self.engine is not None and isinstance(getattr(self.engine, 'harmonie_feld'), dict):
                    z.brightness += (1 - self.engine.harmonie_feld["global_harmonie"]) * 0.02
                z.clamp()

        # Edger
        if len(self.zellen) == 0 or self.engine is None:
            return
        edger = self.zellen[-1]
        freie = [z for z in self.engine.zellen if not z.in_cluster]

        gedockt = 0
        for f in freie:
            if abs(f.hue - edger.hue) < 20 and f.drift > 0.3:
                f.in_cluster = True
                self.zellen.append(f)
                gedockt += 1
                f.energy = min(1.0, f.energy * 0.5 + 0.1)
                f.drift *= 0.3
                f.harmonie = min(1.0, f.harmonie + 0.1)
                if isinstance(self.engine.harmonie_feld, dict):
                    self.engine.harmonie_feld["fusionsenergie"] = self.engine.harmonie_feld.get("fusionsenergie", 0.0) + 0.05

                if len(self.zellen) > 11:
                    gedroppt = self.zellen[:-11]
                    self.zellen = self.zellen[-11:]
                    for d in gedroppt:
                        if d.in_cluster and not any(d in c.zellen for c in self.engine.cluster):
                            d.in_cluster = False
                if gedockt >= 2 and len(self.zellen) < 11 and len(self.zellen) >= 2:
                    zwilling = f
                    if zwilling in self.zellen:
                        self.zellen.remove(zwilling)
                    zwilling.in_cluster = False
                    zwilling.evolutionskeim = True
                    zwilling.energy = min(1.0, zwilling.energy + 0.2)
                    zwilling.drift = min(1.0, zwilling.drift + 0.1)
                    if isinstance(self.engine.harmonie_feld, dict):
                        self.engine.harmonie_feld["fusionsenergie"] = self.engine.harmonie_feld.get("fusionsenergie", 0.0) + 0.1
                    break

    # ---------------------------------------------------------
    # 5. Ausgabe für Ring
    # ---------------------------------------------------------
    def get_farbsatz(self):
        return (
            self.farbsatz_hue,
            self.farbsatz_saturation,
            self.farbsatz_brightness
        )

