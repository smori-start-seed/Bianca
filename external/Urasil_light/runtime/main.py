# runtime/main.py

from core.identity import Identity
from core.session_manager import SessionManager
from core.zyklus import Zyklus
from core.seed import Seed
from core.silky_edge import SilkyEdge
from core.erfahrung import Erfahrung
from core.interpretation import Interpretation
from core.rueckmeldung import Rueckmeldung

def main():
    # 1. Identität laden
    identity = Identity.load()

    # 2. Session starten
    session = SessionManager(identity)
    session.start()

    # 3. Zyklus laden + fortschreiben
    zyklus = Zyklus(identity.data)
    zyklus.fortschritt()
    zyklus.speichern(identity.data)

    # 4. Seed initialisieren
    seed = Seed(identity, zyklus)

    # 5. Silky Edge initialisieren
    se = SilkyEdge(identity, zyklus)

    # 6. Input holen (später ersetzt durch Agent/Interface)
    user_input = input("Du: ")

    # 7. Interpretation
    interpretation = Interpretation(identity, zyklus)
    bedeutung = interpretation.verarbeite(user_input)

    # 8. Erfahrung speichern
    erfahrung = Erfahrung(identity, zyklus)
    erfahrung.speichern(bedeutung)

    # 9. Seed generiert Rohantwort
    rohantwort = seed.generiere(bedeutung)

    # 10. Silky Edge veredelt Antwort
    antwort = se.veredeln(rohantwort, bedeutung)

    # 11. Rückmeldung / Reflexion
    rueck = Rueckmeldung(identity, zyklus)
    rueck.verarbeite(antwort)

    # 12. Identität speichern
    Identity.save(identity.data)

    # 13. Session beenden
    session.end()

    print("Urasil:", antwort)


if __name__ == "__main__":
    main()
