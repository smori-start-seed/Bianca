# MetaSphere.py – Harmonische Aggregation der Sphere-Ebene
from config import *

class MetaSphere:
    def __init__(self, spheren_liste):
        # Liste von Spheres (meist 1)
        self.spheren = spheren_liste

        # Aggregierte Meta-Werte
        self.hue_avg = 0.3
        self.sat_avg = 0.2
        self.bri_avg = 0.4

        self.energy_avg = 0.2
        self.harmonie_avg = 0.4
        self.drift_avg = 0.3

    # ---------------------------------------------------------
    # 1. Öffentliche Update-Methode
    # ---------------------------------------------------------
    def update(self):
        self.update_metasphere()

    # ---------------------------------------------------------
    # 2. MetaSphere-Update: Spheres updaten + Aggregation
    # ---------------------------------------------------------
    def update_metasphere(self):

        # 2.1 Alle Spheres updaten
        for s in self.spheren:
            s.update()

        # 2.2 Meta-Werte aggregieren
        self.berechne_metasphere()

    # ---------------------------------------------------------
    # 3. Aggregation der Sphere-Werte
    # ---------------------------------------------------------
    def berechne_metasphere(self):
        if not self.spheren:
            return

        hues = []
        sats = []
        bris = []
        energies = []
        harmonies = []
        drifts = []

        for s in self.spheren:
            hues.append(s.hue_avg)
            sats.append(s.sat_avg)
            bris.append(s.bri_avg)

            energies.append(s.energy_avg)
            harmonies.append(s.harmonie_avg)
            drifts.append(s.drift_avg)

        # Durchschnittswerte
        self.hue_avg = sum(hues) / len(hues)
        self.sat_avg = sum(sats) / len(sats)
        self.bri_avg = sum(bris) / len(bris)

        self.energy_avg = sum(energies) / len(energies)
        self.harmonie_avg = sum(harmonies) / len(harmonies)
        self.drift_avg = sum(drifts) / len(drifts)

    # ---------------------------------------------------------
    # 4. Ausgabe für UniverseNode
    # ---------------------------------------------------------
    def get_meta(self):
        return {
            "hue": self.hue_avg,
            "sat": self.sat_avg,
            "bri": self.bri_avg,
            "energy": self.energy_avg,
            "harmonie": self.harmonie_avg,
            "drift": self.drift_avg
        }
    def get_farbsatz(self):
        return (self.hue_avg, self.sat_avg, self.bri_avg)

