import math

class Ring:
    def __init__(self, cluster_liste):
        if len(cluster_liste) == 0:
            raise ValueError("Ein Ring benötigt mindestens 1 Cluster.")

        self.cluster = cluster_liste

        # Ring-Zustände
        self.muster_hue = 0.0
        self.muster_saturation = 0.0
        self.muster_brightness = 0.0

        self.drift_avg = 0.0
        self.harmonie_avg = 0.0
        self.varianz = 0.0

    # ---------------------------------------------------------
    # 1. Update aller Cluster
    # ---------------------------------------------------------
    def update(self):
        for c in self.cluster:
            c.update()

        self.berechne_ringwerte()
        self.berechne_muster()

    # ---------------------------------------------------------
    # 2. Ringwerte berechnen
    # ---------------------------------------------------------
    def berechne_ringwerte(self):
        hues = []
        sats = []
        bris = []
        drifts = []
        harmonien = []

        for c in self.cluster:
            h, s, b = c.get_farbsatz()
            hues.append(h)
            sats.append(s)
            bris.append(b)
            drifts.append(c.drift_avg)
            harmonien.append(c.harmonie_avg)

        # Durchschnittswerte
        self.drift_avg = sum(drifts) / len(drifts)
        self.harmonie_avg = sum(harmonien) / len(harmonien)

        # Varianz der Hue-Werte
        avg_hue = sum(hues) / len(hues)
        self.varianz = sum((h - avg_hue)**2 for h in hues) / len(hues)

        # Mittelwerte für Muster
        self.muster_hue = avg_hue
        self.muster_saturation = sum(sats) / len(sats)
        self.muster_brightness = sum(bris) / len(bris)

    # ---------------------------------------------------------
    # 3. Muster berechnen (Ring-Semantik)
    # ---------------------------------------------------------
    def berechne_muster(self):
        # Drift senkt Helligkeit
        self.muster_brightness -= 0.15 * self.drift_avg

        # Harmonie erhöht Saturation
        self.muster_saturation += 0.1 * (self.harmonie_avg - 0.5)

        # Varianz erzeugt leichte Hue-Verschiebung
        self.muster_hue += (self.varianz / 180.0) * 10.0

        # Grenzen clampen
        self.muster_hue %= 360
        self.muster_saturation = max(0.0, min(1.0, self.muster_saturation))
        self.muster_brightness = max(0.0, min(1.0, self.muster_brightness))

    # ---------------------------------------------------------
    # 4. Ausgabe als Nuance (für Sphären)
    # ---------------------------------------------------------
    def get_muster(self):
        return (
            self.muster_hue,
            self.muster_saturation,
            self.muster_brightness
        )

