import os

class Mandate:
    def __init__(self, identity):
        self.identity = identity
        self.gold = self._lade_gold()

    def _lade_gold(self):
        pfad = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "gold.txt"
        )

        if not os.path.exists(pfad):
            return []

        with open(pfad, "r") as f:
            inhalt = f.read().strip()

        # gold.txt wird in einzelne Leitlinien zerlegt
        return [zeile.strip() for zeile in inhalt.split("\n") if zeile.strip()]

    def ideal(self):
        # gibt die Liste der Ideal‑Mandate zurück
        return self.gold

    def passt(self, text):
        # prüft, ob eine Antwort den gold‑Werten entspricht
        for wert in self.gold:
            if wert.lower() in text.lower():
                return True
        return False

