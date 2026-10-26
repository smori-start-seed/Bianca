import math

class Sphere:
    def __init__(self, ring_liste):
        if len(ring_liste) == 0:
            raise ValueError("Eine Sphäre benötigt mindestens 1 Ring.")

        self.ringe = ring_liste

        # Sphären-Zustände
        self.zustand_hue = 0.0
        self.zustand_saturation = 0.0
        self.zustand_brightness = 0.0

        self.drift_avg = 0.0
        self.harmonie_avg = 0.0
        self.varianz = 0.0

    # ---------------------------------------------------------
    # 1. Update aller Ringe
    # ---------------------------------------------------------
    def update(self):
        for r in self.ringe:
            r.update()

        self.berechne_sphaerenwerte()
        self.berechne_zustand()
        self.transition()

    # ---------------------------------------------------------
    # 2. Sphärenwerte berechnen
    # ---------------------------------------------------------
    def berechne_sphaerenwerte(self):
        hues = []
        sats = []
        bris = []
        drifts = []
        harmonien = []

        for r in self.ringe:
            h, s, b = r.get_muster()
            hues.append(h)
            sats.append(s)
            bris.append(b)
            drifts.append(r.drift_avg)
            harmonien.append(r.harmonie_avg)

        # Durchschnittswerte
        self.drift_avg = sum(drifts) / len(drifts)
        self.harmonie_avg = sum(harmonien) / len(harmonien)

        # Varianz der Hue-Werte
        avg_hue = sum(hues) / len(hues)
        self.varianz = sum((h - avg_hue)**2 for h in hues) / len(hues)

        # Mittelwerte für globalen Zustand
        self.zustand_hue = avg_hue
        self.zustand_saturation = sum(sats) / len(sats)
        self.zustand_brightness = sum(bris) / len(bris)

    # ---------------------------------------------------------
    # 3. Sphären-Zustand berechnen (Semantik)
    # ---------------------------------------------------------
    def berechne_zustand(self):
        # Drift senkt globale Helligkeit
        self.zustand_brightness -= 0.2 * self.drift_avg

        # Harmonie erhöht globale Saturation
        self.zustand_saturation += 0.15 * (self.harmonie_avg - 0.5)

        # Varianz erzeugt leichte Hue-Verschiebung
        self.zustand_hue += (self.varianz / 180.0) * 15.0

        # Grenzen clampen
        self.zustand_hue %= 360
        self.zustand_saturation = max(0.0, min(1.0, self.zustand_saturation))
        self.zustand_brightness = max(0.0, min(1.0, self.zustand_brightness))

    # ---------------------------------------------------------
    # 4. Zustandsübergänge (Failsafe der Sphäre)
    # ---------------------------------------------------------
    def transition(self):
        # Schwarz-Reset der Sphäre
        if (self.zustand_saturation < 0.1 or
            self.zustand_brightness < 0.05 or
            self.drift_avg > 0.75 or
            self.harmonie_avg < 0.2):

            self.zustand_hue = 0
            self.zustand_saturation = 0
            self.zustand_brightness = 0
            return

        # Weiß-Sättigung der Sphäre
        if (self.zustand_saturation > 0.9 and
            self.zustand_brightness > 0.95 and
            self.harmonie_avg > 0.85):

            self.zustand_hue = 0
            self.zustand_saturation = 0
            self.zustand_brightness = 1
            return

    # ---------------------------------------------------------
    # 5. Ausgabe als Nuance
    # ---------------------------------------------------------
    def get_zustand(self):
        return (
            self.zustand_hue,
            self.zustand_saturation,
            self.zustand_brightness
        )

