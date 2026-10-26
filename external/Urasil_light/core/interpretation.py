class Interpretation:
    def __init__(self, identity, zyklus):
        self.identity = identity
        self.zyklus = zyklus

    def verarbeite(self, text):
        modus = self.zyklus.matrix()

        # Grundmodus entscheidet, wie Bedeutung extrahiert wird
        if modus["grundmodus"] == "klarheit":
            # nüchtern, direkt
            return text.strip()

        elif modus["grundmodus"] == "kreativ":
            # spielerisch, assoziativ
            return f"Kreativer Impuls: {text.strip()}"

        elif modus["grundmodus"] == "resonanz":
            # emotionaler Kern
            return f"Gefühl dahinter: {text.strip()}"

        else:
            # tiefe, philosophische Bedeutung
            return f"Tiefer Gedanke: {text.strip()}"
