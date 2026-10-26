# Ring.py – Colorverse Evolution
import math
from config import *
class Ring:
    def __init__(self, cluster_liste):
        # Liste von Clustern (11 Zellen pro Cluster)
        self.cluster = cluster_liste

        # Aggregierte Farbsätze
        self.hue_avg = 0.0
        self.sat_avg = 0.0
        self.bri_avg = 0.0

    # ---------------------------------------------------------
    # 1. Öffentliche Update-Methode
    # ---------------------------------------------------------
    def update(self):
        self.update_ring()

    # ---------------------------------------------------------
    # 2. Ring-Update: Cluster updaten + Farbsatz aggregieren
    # ---------------------------------------------------------
    def update_ring(self):

        # 2.1 Alle Cluster updaten
        for c in self.cluster:
            c.update()

        # 2.2 Farbsatz aggregieren
        self.berechne_ring_farbsatz()

        # 2.3 Die Tür: die Clusterfarbe wirklich schreiben, nicht nur messen
        self.rueckkopplung_ins_evolutionsfeld()

        print(f"[RING] hue={self.hue_avg:.2f} sat={self.sat_avg:.2f} bri={self.bri_avg:.2f}")

    # ---------------------------------------------------------
    # 3. Aggregierten Farbsatz berechnen
    # ---------------------------------------------------------
    def berechne_ring_farbsatz(self):
        if not self.cluster:
            self.hue_avg = 0.0
            self.sat_avg = 0.0
            self.bri_avg = 0.0
            return

        hues, sats, bris = [], [], []
        for c in self.cluster:
            h, s, b = c.get_farbsatz()
            hues.append(h)
            sats.append(s)
            bris.append(b)

        self.hue_avg = sum(hues) / len(hues)
        self.sat_avg = sum(sats) / len(sats)
        self.bri_avg = sum(bris) / len(bris)

    # ---------------------------------------------------------
    # 4. Ausgabe für Sphere / MetaSphere
    # ---------------------------------------------------------
    def get_farbsatz(self):
        return (self.hue_avg, self.sat_avg, self.bri_avg)

    # ---------------------------------------------------------
    # 5. Die Tür (Set 36): Kreismittel + unbedingtes Re-Licht
    # ---------------------------------------------------------
    def rueckkopplung_ins_evolutionsfeld(self):
        """Glättet die Farbe der Cluster-Zellen zum Kreismittelwert.

        Nur `z.in_cluster` zählt. Das ist tragend, nicht ordentlich: die Zellen
        der 90 Anfangs-Cluster sind das *freie Feld* (in_cluster ist False), und
        eine Ring-Tür, die sie anfasst, löscht die Sphere-Welle aus.

        Ein arithmetisches Mittel über Hue ist falsch (350° und 10° mitteln zu
        180°, also zur Gegenfarbe); deshalb Sinus/Cosinus und atan2.
        """
        zellen = [z for c in self.cluster for z in c.zellen if z.in_cluster]
        if zellen:
            sin_sum = sum(math.sin(math.radians(z.hue)) for z in zellen)
            cos_sum = sum(math.cos(math.radians(z.hue)) for z in zellen)
            if abs(sin_sum) > 1e-12 or abs(cos_sum) > 1e-12:
                mittel = math.degrees(math.atan2(sin_sum, cos_sum)) % 360.0
                for z in zellen:
                    delta = (mittel - z.hue + 180.0) % 360.0 - 180.0
                    z.hue = (z.hue + RING_GLAETTUNG * delta) % 360.0

        if RING_RELIGHT:
            for z in zellen:
                z.saturation = max(z.saturation, 0.5)
                z.brightness = max(z.brightness, 0.5)
