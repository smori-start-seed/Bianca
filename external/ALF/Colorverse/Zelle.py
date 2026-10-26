import math
from config import *

#: Divisor der Harmonieskala (Zelle.berechne_harmonie).
#:
#: Die Varianz, bei der „unharmonisch" voll zaehlt, ist die Varianz einer
#: Gleichverteilung ueber den ganzen Farbkreis: hue laeuft von 0 bis 360
#: (Zelle.clamp: self.hue %= 360; build_world: random.uniform(0, 360)), also
#: Var = 360^2 / 12 = 10800.
#:
#: 🚨 Vorher stand hier 180 — die Zahl aus berechne_drift, wo sie richtig ist
#: (maximaler mittlerer Kreisabstand / 180 ergibt 1.0). Fuer die Varianz ist
#: 180 um den Faktor 60 zu klein: bei Zufallsfarben ist var ~ 10800, also
#: var/180 ~ 60, also harmonie = 1 - min(1, 60) = 0.0 fuer praktisch jede
#: Zelle — und Zelle.failsafe() toetet genau daran (harmonie < 0.2).
#: Gemessen 2026-10-02: 989 von 1000 Zellen standen nach build_world auf
#: hue = 0.0. Ein Divisor, der eine Groesse in 0..1 verspricht und statt
#: dessen immer 0 liefert, ist kein Messwert, sondern ein stiller Todesfall.
HARMONIE_NULLPUNKT = 10800.0


class Zelle:
    def __init__(self, hue=0.0, saturation=0.5, brightness=0.5, energy=1.0):
        # Grundwerte
        self.hue = hue
        self.saturation = saturation
        self.brightness = brightness
        self.energy = energy

        # Dynamische Werte
        self.drift = 0.0
        self.harmonie = 1.0

        # Nachbarn (Engine setzt das)
        self.nachbarn = []

        # Parameter
        self.alpha = 0.05
        self.beta  = 0.03
        self.gamma = 0.02

        # Micro‑Hexagon
        self.hex = None

        # Cluster‑Status
        self.in_cluster = False

        # Evolutionskeim
        self.evolutionskeim = False

    def clamp(self):
        self.hue %= 360
        self.saturation = max(0, min(1, self.saturation))
        self.brightness = max(0, min(1, self.brightness))
        self.energy = max(0, min(1, self.energy))
        self.drift = max(0, min(1, self.drift))
        self.harmonie = max(0, min(1, self.harmonie))

    def berechne_drift(self):
        if not self.nachbarn:
            self.drift = 0.0
            return

        diffs = []
        for n in self.nachbarn:
            d = abs(self.hue - n.hue)
            d = min(d, 360 - d)
            diffs.append(d)

        self.drift = (sum(diffs) / len(diffs)) / 180.0

    def berechne_harmonie(self):
        if not self.nachbarn:
            self.harmonie = 1.0
            return

        hues = [n.hue for n in self.nachbarn]
        avg = sum(hues) / len(hues)
        var = sum((h - avg)**2 for h in hues) / len(hues)

        self.harmonie = 1.0 - min(1.0, var / HARMONIE_NULLPUNKT)

    def failsafe(self):
        if (self.saturation < 0.15 or
            self.brightness < 0.05 or
            self.drift > 0.7 or
            self.harmonie < 0.2):

            # Der Tod ist keine Farbe. `hue = 0` war Todesmarke UND Farbwert,
            # und die Nachbarschaft hat mitgerechnet: gemischte Nachbarschaften
            # erreichten var 10 488 bei einem Maximum von 10 800 (Abschnitt 9b),
            # 160 Zellen starben allein im ersten Schritt daran. Die sterbende
            # Zelle uebernimmt den Nachbarmittelwert; sie stirbt weiterhin,
            # denn saturation und brightness stehen danach auf 0.
            self.hue = (sum(n.hue for n in self.nachbarn) / len(self.nachbarn)
                        if self.nachbarn else self.hue)
            self.saturation = 0
            self.brightness = 0
            self.drift = 0
            self.harmonie = 1
            return True

        if (self.saturation > 0.85 and
            self.brightness > 0.95 and
            self.harmonie > 0.8):

            # Derselbe Grund im zweiten Arm, und er ist nicht laenger latent:
            # auf der sterbenden Welt feuerte er 0-mal in 400 Schritten — nach
            # V lebt der Garten, eine Zelle erreicht sat > 0.85, bri > 0.95 und
            # harmonie > 0.8, und der Arm feuert. Eine Zelle, die fuer
            # Vortrefflichkeit erlischt, ist genauso wenig tot wie eine, die
            # fuer Andersartigkeit stirbt; auch sie nimmt den Nachbarmittelwert
            # statt Schwarz. `brightness = 1` bleibt: das ist ihr Zustand,
            # nicht der Tod — er wird von den beiden anderen Feldern getragen.
            self.hue = (sum(n.hue for n in self.nachbarn) / len(self.nachbarn)
                        if self.nachbarn else self.hue)
            self.saturation = 0
            self.brightness = 1
            self.drift = 0
            self.harmonie = 1
            return True

        return False

    def stabilisierung(self):
        if not self.nachbarn:
            return

        avg_hue = sum(n.hue for n in self.nachbarn) / len(self.nachbarn)
        self.hue = (1 - self.alpha) * self.hue + self.alpha * avg_hue

        self.saturation += self.beta * (self.harmonie - 0.5)
        self.brightness -= self.gamma * self.drift

        self.clamp()

    def update(self):
        if self.hex:
            self.hex.apply(self)
            print(f"[ZELLE] hue={self.hue:.2f} sat={self.saturation:.2f} bri={self.brightness:.2f} energy={self.energy:.2f}")


        self.clamp()
        self.berechne_drift()
        self.berechne_harmonie()

        if self.failsafe():
            return

        self.stabilisierung()
