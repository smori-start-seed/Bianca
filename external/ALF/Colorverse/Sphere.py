# Sphere.py – Colorverse Evolution (Ring-basiert, harmonisch)
import math
from config import *

class Sphere:
    def __init__(self, ring_liste):
        # Liste von Ringen (jeder Ring enthält Cluster)
        self.ringe = ring_liste

        # Aggregierte Farbsätze der Sphere
        self.hue_avg = 0.0
        self.sat_avg = 0.0
        self.bri_avg = 0.0

        # Meta-Werte der Sphere
        self.energy_avg = 0.0
        self.harmonie_avg = 0.0
        self.drift_avg = 0.0

        # Phase der wandernden Hue-Welle (Set 36)
        self.muster_phase = 0.0

    # ---------------------------------------------------------
    # 1. Öffentliche Update-Methode
    # ---------------------------------------------------------
    def update(self):
        self.update_sphere()

    # ---------------------------------------------------------
    # 2. Sphere-Update: Ringe updaten + Farbsatz aggregieren
    # ---------------------------------------------------------
    def update_sphere(self):

        # 2.1 Alle Ringe updaten
        for r in self.ringe:
            r.update()

        # 2.2 Farbsatz aggregieren
        self.berechne_sphere_farbsatz()
        print(f"[SPHERE] hue={self.hue_avg:.2f} sat={self.sat_avg:.2f} bri={self.bri_avg:.2f}")

    # ---------------------------------------------------------
    # 3. Aggregierten Farbsatz berechnen
    # ---------------------------------------------------------
    def berechne_sphere_farbsatz(self):
        if not self.ringe:
            self.hue_avg = 0.0
            self.sat_avg = 0.0
            self.bri_avg = 0.0
            return

        hues, sats, bris = [], [], []
        for r in self.ringe:
            h, s, b = r.get_farbsatz()
            hues.append(h)
            sats.append(s)
            bris.append(b)

        if hues:
            s_h = sum(math.sin(math.radians(h)) for h in hues)
            c_h = sum(math.cos(math.radians(h)) for h in hues)
            if abs(s_h) > 1e-12 or abs(c_h) > 1e-12:
                self.hue_avg = math.degrees(math.atan2(s_h, c_h)) % 360.0
            else:
                self.hue_avg = sum(hues) / len(hues)
        self.sat_avg = sum(sats) / len(sats) if sats else 0.0
        self.bri_avg = sum(bris) / len(bris) if bris else 0.0

        self.energy_avg = sum(r.hue_avg for r in self.ringe) / len(self.ringe)
        self.harmonie_avg = 1.0
        self.drift_avg = 0.0

    # ---------------------------------------------------------
    # 4. Ausgabe für MetaSphere / Universe
    # ---------------------------------------------------------
    def get_farbsatz(self):
        return (self.hue_avg, self.sat_avg, self.bri_avg)

    # ---------------------------------------------------------
    # 5. Die Tür (Set 36): eine wandernde Welle, keine weitere Mitte
    # ---------------------------------------------------------
    def rueckkopplung_ins_evolutionsfeld(self, zellen):
        """Malt dem freien Feld eine Hue-Welle über den Zellindex.

        Das ist die Streuungsquelle, die der Kern bis hierher nicht hatte: jeder
        andere Schritt mittelt (stabilisierung, Cluster.mutation, UniverseNode
        dämpft mit 0.9) und treibt das Feld auf einen Spread von ~9.5. Die Welle
        schreibt ein *Muster* und führt dem Feld Energie zu.

        `z.in_cluster` wird übersprungen. Das ist tragend: die Zellen der 90
        Anfangs-Cluster sind das freie Feld, und die Ring-Tür glättet nur die
        echten Cluster-Zellen — zwei Türen, die dieselbe Zelle anfassen, würden
        sich gegenseitig auslöschen.

        `drift`/`harmonie` werden sofort neu gerechnet, weil die Saatprüfung am
        Kopf von `step()` sie unmittelbar danach liest.
        """
        self.muster_phase = (self.muster_phase + SPHERE_MUSTER_SPEED) % (2.0 * math.pi)

        frei = []
        k = SPHERE_MUSTER_FREQ
        for i, z in enumerate(zellen):
            if z.in_cluster:
                continue
            welle = SPHERE_MUSTER_AMP * math.sin(k * i + self.muster_phase)
            z.hue = (z.hue + welle) % 360.0
            z.energy = min(1.0, z.energy + SPHERE_ENERGIE)
            frei.append(z)

        for z in frei:
            z.berechne_drift()
            z.berechne_harmonie()
