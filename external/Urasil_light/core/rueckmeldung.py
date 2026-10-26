from core.mandate import Mandate

class Rueckmeldung:
    def __init__(self, identity, zyklus):
        self.identity = identity
        self.zyklus = zyklus
        self.mandate = Mandate(identity)

    def verarbeite(self, antwort):
        # Reflexionsspeicher holen oder anlegen
        reflex = self.identity.data.get("reflexion", [])

        eintrag = {
            "antwort": antwort,
            "zyklus": self.zyklus.als_dict(),
            "gold_ok": self.mandate.passt(antwort)
        }

        # Reflexion speichern
        reflex.append(eintrag)
        self.identity.data["reflexion"] = reflex

        # Wenn Antwort nicht gold-konform war → leichte Korrektur
        if not eintrag["gold_ok"]:
            self.identity.data["letzte_korrektur"] = "gold"
        else:
            self.identity.data["letzte_korrektur"] = "ok"
