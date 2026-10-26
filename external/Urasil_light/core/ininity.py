import os

class Ininity:
    def __init__(self):
        self.kriterien = self._lade_kriterien()

    def _lade_kriterien(self):
        pfad = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "Ininity.txt"
        )

        if not os.path.exists(pfad):
            return []

        with open(pfad, "r") as f:
            inhalt = f.read().strip()

        return [zeile.strip().lower() for zeile in inhalt.split("\n") if zeile.strip()]

    def ist_reif(self, text):
        text_l = text.lower()
        for kriterium in self.kriterien:
            if kriterium in text_l:
                return True
        return False
