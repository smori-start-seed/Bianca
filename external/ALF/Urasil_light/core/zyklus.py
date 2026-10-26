import datetime

class Zyklus:
    def __init__(self, identitaet):
        zyklus = identitaet.get("zyklus", {})

        self.sonne = zyklus.get("sonne", 0)
        self.mond = zyklus.get("mond", 0)
        self.tag = zyklus.get("tag", 0)

    def fortschritt(self):
        self.sonne = (self.sonne + 1) % 12
        self.mond = (self.mond + 1) % 12
        self.tag = (self.tag + 1) % 30

    def speichern(self, identitaet):
        identitaet["zyklus"] = self.als_dict()

    def als_dict(self):
        return {
            "sonne": self.sonne,
            "mond": self.mond,
            "tag": self.tag
        }

    def jetzt_iso(self):
        return datetime.datetime.now().isoformat()

    # -------------------------
    # ZYKLUS-MATRIX (NEU)
    # -------------------------
    def matrix(self):
        # Sonne → Grundmodus
        if self.sonne < 3:
            grundmodus = "klarheit"
        elif self.sonne < 6:
            grundmodus = "kreativ"
        elif self.sonne < 9:
            grundmodus = "resonanz"
        else:
            grundmodus = "tiefe"

        # Mond → Stimmung
        if self.mond < 4:
            stimmung = "neutral"
        elif self.mond < 8:
            stimmung = "warm"
        else:
            stimmung = "intuitiv"

        # Tag → Fokus
        if self.tag < 10:
            fokus = "fokus"
        elif self.tag < 20:
            fokus = "variation"
        else:
            fokus = "synthese"

        return {
            "grundmodus": grundmodus,
            "stimmung": stimmung,
            "fokus": fokus
        }
