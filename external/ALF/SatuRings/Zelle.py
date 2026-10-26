import math

class Zelle:
    def __init__(self, hue, saturation, brightness, nachbarn=None):
        self.hue = hue              # 0–360
        self.saturation = saturation  # 0–1
        self.brightness = brightness  # 0–1

        self.drift = 0.0
        self.harmonie = 1.0

        self.nachbarn = nachbarn if nachbarn else []

        # Parameter
        self.alpha = 0.05   # Hue‑Anpassung
        self.beta  = 0.03   # Saturation‑Anpassung
        self.gamma = 0.02   # Brightness‑Dämpfung

    # ---------------------------------------------------------
    # 1. Werte clampen
    # ---------------------------------------------------------
    def clamp(self):
        self.hue = self.hue % 360
        self.saturation = max(0.0, min(1.0, self.saturation))
        self.brightness = max(0.0, min(1.0, self.brightness))
        self.drift = max(0.0, min(1.0, self.drift))
        self.harmonie = max(0.0, min(1.0, self.harmonie))

    # ---------------------------------------------------------
    # 2. Drift berechnen
    # ---------------------------------------------------------
    def berechne_drift(self):
        if not self.nachbarn:
            self.drift = 0
            return

        diffs = [abs(self.hue - n.hue) for n in self.nachbarn]
        avg_diff = sum(diffs) / len(diffs)
        self.drift = avg_diff / 180.0  # normiert

    # ---------------------------------------------------------
    # 3. Harmonie berechnen
    # ---------------------------------------------------------
    def berechne_harmonie(self):
        if not self.nachbarn:
            self.harmonie = 1
            return

        hues = [n.hue for n in self.nachbarn]
        avg = sum(hues) / len(hues)

        var = sum((h - avg)**2 for h in hues) / len(hues)
        self.harmonie = 1.0 - min(1.0, var / 180.0)

    # ---------------------------------------------------------
    # 4. Failsafe prüfen
    # ---------------------------------------------------------
    def failsafe(self):
        # Schwarz‑Reset
        if (self.saturation < 0.15 or
            self.brightness < 0.05 or
            self.drift > 0.7 or
            self.harmonie < 0.2):

            self.hue = 0
            self.saturation = 0
            self.brightness = 0
            self.drift = 0
            self.harmonie = 1
            return True

        # Weiß‑Sättigung
        if (self.saturation > 0.85 and
            self.brightness > 0.95 and
            self.harmonie > 0.8):

            self.hue = 0
            self.saturation = 0
            self.brightness = 1
            self.drift = 0
            self.harmonie = 1
            return True

        return False

    # ---------------------------------------------------------
    # 5. Stabilisierung
    # ---------------------------------------------------------
    def stabilisierung(self):
        if not self.nachbarn:
            return

        avg_hue = sum(n.hue for n in self.nachbarn) / len(self.nachbarn)

        # Hue angleichen
        self.hue = (1 - self.alpha) * self.hue + self.alpha * avg_hue

        # Saturation an Harmonie koppeln
        self.saturation += self.beta * (self.harmonie - 0.5)

        # Brightness durch Drift dämpfen
        self.brightness -= self.gamma * self.drift

        self.clamp()

    # ---------------------------------------------------------
    # 6. Update‑Pipeline
    # ---------------------------------------------------------
    def update(self):
        self.clamp()
        self.berechne_drift()
        self.berechne_harmonie()

        if self.failsafe():
            return

        self.stabilisierung()

