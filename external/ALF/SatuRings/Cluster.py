import math

class Cluster:
    def __init__(self, zellen):
        if len(zellen) != 11:
            raise ValueError("Ein Cluster besteht aus genau 11 Zellen.")

        self.zellen = zellen

        # Cluster-Zustände
        self.farbsatz_hue = 0.0
        self.farbsatz_saturation = 0.0
        self.farbsatz_brightness = 0.0

        self.drift_avg = 0.0
        self.harmonie_avg = 0.0
        self.varianz = 0.0

    # ---------------------------------------------------------
    # 1. Update aller Zellen
    # ---------------------------------------------------------
    def update(self):
        for z in self.zellen:
            z.update()

        self.berechne_clusterwerte()
        self.berechne_farbsatz()

    # ---------------------------------------------------------
    # 2. Clusterwerte berechnen
    # ---------------------------------------------------------
    def berechne_clusterwerte(self):
        hues = [z.hue for z in self.zellen]
        sats = [z.saturation for z in self.zellen]
        bris = [z.brightness for z in self.zellen]
        drifts = [z.drift for z in self.zellen]
        harmonien = [z.harmonie for z in self.zellen]

        # Durchschnittswerte
        self.drift_avg = sum(drifts) / len(drifts)
        self.harmonie_avg = sum(harmonien) / len(harmonien)

        # Varianz der Hue-Werte
        avg_hue = sum(hues) / len(hues)
        self.varianz = sum((h - avg_hue)**2 for h in hues) / len(hues)

        # Mittelwerte für Farbsatz
        self.farbsatz_hue = avg_hue
        self.farbsatz_saturation = sum(sats) / len(sats)
        self.farbsatz_brightness = sum(bris) / len(bris)

    # ---------------------------------------------------------
    # 3. Farbsatz berechnen (Cluster-Semantik)
    # ---------------------------------------------------------
    def berechne_farbsatz(self):
        # Drift beeinflusst Helligkeit
        self.farbsatz_brightness -= 0.1 * self.drift_avg

        # Harmonie beeinflusst Saturation
        self.farbsatz_saturation += 0.1 * (self.harmonie_avg - 0.5)

        # Varianz beeinflusst Hue leicht
        self.farbsatz_hue += (self.varianz / 180.0) * 5.0

        # Grenzen clampen
        self.farbsatz_hue %= 360
        self.farbsatz_saturation = max(0.0, min(1.0, self.farbsatz_saturation))
        self.farbsatz_brightness = max(0.0, min(1.0, self.farbsatz_brightness))

    # ---------------------------------------------------------
    # 4. Ausgabe als Nuance (für Ringe)
    # ---------------------------------------------------------
    def get_farbsatz(self):
        return (
            self.farbsatz_hue,
            self.farbsatz_saturation,
            self.farbsatz_brightness
        )

