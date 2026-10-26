from core.mandate import Mandate

class Seed:
    def __init__(self, identity, zyklus):
        self.identity = identity
        self.zyklus = zyklus
        self.mandate = Mandate(identity)

    def generiere(self, bedeutung):
        modus = self.zyklus.matrix()

        # Zyklus-Fokus bestimmt die Art der Antwort
        if modus["fokus"] == "fokus":
            antwort = f"Direkt: {bedeutung}"

        elif modus["fokus"] == "variation":
            antwort = f"Alternative Sicht: {bedeutung}"

        else:
            antwort = f"Zusammenhang: {bedeutung}"

        # Reflexionssignal aus der Identität
        reflex = self.identity.data.get("letzte_korrektur", "ok")

        # Wenn letzte Antwort nicht gold-konform war → mehr Klarheit
        if reflex == "gold":
            antwort = "Klarer: " + antwort

        return antwort
