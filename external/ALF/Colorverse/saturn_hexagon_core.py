# saturn_hexagon_core.py
import math
import random
from config import *
class SaturnHexagon:
    def __init__(self):
        # A = Zentrum (globaler Drift-Anker)
        self.A = {
            "af": 0.5,   # Hue-Faktor
            "pf": 0.5,   # Saturation-Faktor
            "rf": 0.5,   # Brightness-Faktor
            "mass": 1000.0,
            "drift": 0.00005
        }

        # B & C = Orbit-Paar
        self.B = {
            "angle": 0.0,
            "density": 1.0,
            "af": 0.4,
            "pf": 0.6,
            "rf": 0.5
        }

        self.C = {
            "angle": math.pi,
            "density": 0.7,
            "af": 0.6,
            "pf": 0.4,
            "rf": 0.5
        }

        self.RADIUS = 1.0

    # ---------------------------------------------------------
    # interne Saturn-Logik (wie dein Original)
    # ---------------------------------------------------------
    def _update_saturn(self):
        B = self.B
        C = self.C
        A = self.A

        # B rotiert
        B["angle"] += 0.015
        B["x"] = self.RADIUS * math.cos(B["angle"])
        B["y"] = self.RADIUS * math.sin(B["angle"])

        # C folgt B (180° versetzt)
        C["angle"] = B["angle"] + math.pi
        C["x"] = self.RADIUS * math.cos(C["angle"])
        C["y"] = self.RADIUS * math.sin(C["angle"])

        # Frequenz-Drift durch Dichte
        B["af"] += (A["af"] - B["af"]) * 0.02 * B["density"]
        C["af"] += (B["af"] - C["af"]) * 0.02 * C["density"]

        # Rückkopplung auf A
        A["af"] += (C["af"] - A["af"]) * A["drift"]

    # ---------------------------------------------------------
    # apply() = Colorverse-Regel
    # ---------------------------------------------------------
    def apply(self, z):
        # Saturn-System updaten
        self._update_saturn()

        A = self.A
        B = self.B
        C = self.C

        # -----------------------------------------------------
        # 1. Hue beeinflussen (über af)
        # -----------------------------------------------------
        saturn_hue = (A["af"] + B["af"] + C["af"]) / 3.0
        z.hue += (saturn_hue - 0.5) * 4.0   # leichte Drift

        # -----------------------------------------------------
        # 2. Saturation beeinflussen (über pf)
        # -----------------------------------------------------
        saturn_sat = (A["pf"] + B["pf"] + C["pf"]) / 3.0
        z.saturation += (saturn_sat - 0.5) * 0.05

        # -----------------------------------------------------
        # 3. Brightness beeinflussen (über rf)
        # -----------------------------------------------------
        saturn_bri = (A["rf"] + B["rf"] + C["rf"]) / 3.0
        z.brightness += (saturn_bri - 0.5) * 0.05

        # -----------------------------------------------------
        # 4. Energie driftet leicht
        # -----------------------------------------------------
        z.energy += (random.random() - 0.5) * 0.02

        # -----------------------------------------------------
        # 5. leichte Chaos-Komponente
        # -----------------------------------------------------
        z.hue += (random.random() - 0.5) * 1.5
        z.saturation += (random.random() - 0.5) * 0.02
        z.brightness += (random.random() - 0.5) * 0.02

