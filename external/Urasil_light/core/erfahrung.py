from core.ininity import Ininity

class Erfahrung:
    def __init__(self, identity, zyklus):
        self.identity = identity
        self.zyklus = zyklus
        self.ininity = Ininity()

    def speichern(self, bedeutung):
        # Nur speichern, wenn reif
        if not self.ininity.ist_reif(bedeutung):
            return  # unreife Erfahrung wird ignoriert

        erf = self.identity.data.get("erfahrung", [])
        erf.append(bedeutung)
        self.identity.data["erfahrung"] = erf
