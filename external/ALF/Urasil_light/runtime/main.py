#!/usr/bin/env python3
"""
Main Runtime Module für Urasil_light

Dieses Modul ist der Einstiegspunkt für Urasil_light.
Es implementiert die vollständige Pipeline mit:
1. Identitätsladung
2. Session-Management
3. Zyklus-Fortschritt
4. Interpretation
5. Seed-Generierung (mit LLM-Bridge)
6. WerteTeilen-Bewertung
7. Silky Edge (Stilistische Veredelung)
8. Erfahrungsspeicherung
9. Rückmeldung
10. Identitätsspeicherung

Beispiel:
    python3 -m runtime.main

Konfiguration:
    - use_llm: True/False (LLM aktivieren/deaktivieren)
    - llm_backends: Dictionary mit Backend-Konfigurationen
    - grundton: Grundton der Identität (z. B. "neutral", "offen")
"""

from core.identity import Identity
from core.session_manager import SessionManager
from core.zyklus import Zyklus
from core.interpretation import Interpretation
from core.silky_edge import SilkyEdge
from core.erfahrung import Erfahrung
from core.rueckmeldung import Rueckmeldung
from core.llm_bridge import LLMBridge
from core.backends import create_default_backends
from core.werte_teilen import WerteTeilen


def main():
    """
    Hauptfunktion für Urasil_light.
    
    Implementiert die vollständige Pipeline:
    1. Identität laden
    2. Session starten
    3. Zyklus fortschreiben
    4. Nutzer-Input verarbeiten
    5. Interpretation durchführen
    6. Seed generieren (mit LLM-Bridge)
    7. WerteTeilen-Bewertung durchführen
    8. Silky Edge anwenden
    9. Erfahrung speichern
    10. Rückmeldung verarbeiten
    11. Identität speichern
    12. Session beenden
    """
    # 1. Identität laden
    identity = Identity.load()
    
    # 2. Backends und Brücken initialisieren
    backends = create_default_backends(use_llm=identity.data.get("use_llm", True))
    llm_bridge = LLMBridge(identity.data, backends) if identity.data.get("use_llm", True) else None
    werte_teilen = WerteTeilen(identity.data)
    
    # 3. Session starten
    session = SessionManager(identity)
    session.start()
    
    # 4. Zyklus laden + fortschreiben
    zyklus = Zyklus(identity.data)
    zyklus.fortschritt()
    zyklus.speichern(identity.data)
    
    # 5. Input holen
    user_input = input("Du: ")
    
    # 6. Interpretation
    interpretation = Interpretation(identity.data, zyklus)
    bedeutung = interpretation.verarbeite(user_input)
    
    # 7. Seed generieren (mit LLM-Bridge)
    from core.seed import Seed
    seed = Seed(identity.data, zyklus, llm_bridge)
    
    # Aktuelles Mandat und Modus
    mandat = identity.data.get("mandat", {})
    modus = zyklus.matrix().get("fokus", "fokus")
    
    rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
    
    # 8. WerteTeilen-Bewertung (für Kontext)
    kontext = {
        "input": user_input,
        "mandat": mandat,
        "modus": modus,
        "deutung": bedeutung,
        "kontext_id": "du",  # Annahme: Nutzer ist "du"
        "kontext_typ": "privat"
    }
    
    # Bewertung durchführen
    bewertung = werte_teilen.bewerte_interaktion(
        nutzer_input=user_input,
        antwort_entwurf=rohantwort,
        mandat=mandat,
        modus=modus,
        deutung=bedeutung,
        kontext_id=kontext["kontext_id"],
        kontext_typ=kontext["kontext_typ"]
    )
    
    # Bewertung zum Kontext hinzufügen
    kontext["bewertung"] = bewertung
    
    # Bewertung anzeigen (für Debugging/Transparenz)
    print(werte_teilen.format_bewertung(bewertung))
    
    # 9. Silky Edge anwenden
    se = SilkyEdge(identity.data, zyklus)
    antwort = se.veredeln(rohantwort, bedeutung)
    
    # 10. Erfahrung speichern (mit WerteTeilen-Filter)
    erfahrung = Erfahrung(identity.data, zyklus, werte_teilen)
    erfahrung.speichern(bedeutung, kontext=kontext)
    
    # 11. Rückmeldung verarbeiten
    rueck = Rueckmeldung(identity.data, zyklus, werte_teilen)
    rueck.verarbeite(antwort, kontext=kontext)
    
    # 12. Identität speichern
    Identity.save(identity.data)
    
    # 13. Session beenden
    session.end()
    
    # 14. Antwort ausgeben
    print(f"\n{identity.data.get('name', 'URASIL')}: {antwort}")


def run_interactive():
    """
    Führt eine interaktive Session mit Urasil_light aus.
    
    Diese Funktion:
    - Lädt die Identität
    - Startet eine interaktive Schleife
    - Verarbeitet jede Nutzer-Eingabe durch die Pipeline
    - Speichert die Identität nach jeder Interaktion
    
    Beendet mit: exit, quit, beenden, Ende
    """
    print("=" * 60)
    print("URASIL_LIGHT - Interaktiver Modus")
    print("=" * 60)
    print("Tipps:")
    print("  - Beende mit: exit, quit, beenden, Ende")
    print("  - Zeige Stats mit: /stats")
    print("  - Zeige Zyklus mit: /zyklus")
    print("  - Zeige Identität mit: /id")
    print("=" * 60)
    
    # Initialisierung
    identity = Identity.load()
    backends = create_default_backends(use_llm=identity.data.get("use_llm", True))
    llm_bridge = LLMBridge(identity.data, backends) if identity.data.get("use_llm", True) else None
    werte_teilen = WerteTeilen(identity.data)
    
    # Session starten
    session = SessionManager(identity)
    session.start()
    
    # Hauptschleife
    while True:
        try:
            user_input = input("\nDu: ").strip()
            
            # Spezialbefehle
            if user_input.lower() in ["exit", "quit", "beenden", "ende"]:
                print("Beende Session...")
                break
            
            if user_input == "/stats":
                print("\n" + "=" * 40)
                print("STATISTIKEN")
                print("=" * 40)
                
                # LLM-Stats
                if llm_bridge:
                    llm_stats = llm_bridge.get_stats()
                    print(f"\nLLM-Brücke:")
                    print(f"  - Gesamtaufrufe: {llm_stats['gesamt_aufrufe']}")
                    print(f"  - Bevorzugte Modelle: {llm_stats['bevorzugte_modelle']}")
                
                # WerteTeilen-Stats
                werte_stats = werte_teilen.get_stats()
                print(f"\nWerteTeilen:")
                print(f"  - Gesamtinteraktionen: {werte_stats['gesamt_interaktionen']}")
                print(f"  - Vertrauen: {werte_stats['vertrauen_zu_kontexten']}")
                print(f"  - Bewertungen: {werte_stats['bewertungs_statistik']}")
                
                # Erfahrung-Stats
                from core.erfahrung import Erfahrung
                erf = Erfahrung(identity.data, None, None)
                erf_stats = erf.get_stats()
                print(f"\nErfahrungen:")
                print(f"  - Gesamt: {erf_stats['gesamt']}")
                print(f"  - Kategorien: {erf_stats['kategorien']}")
                
                # Rückmeldung-Stats
                from core.rueckmeldung import Rueckmeldung
                rueck = Rueckmeldung(identity.data, None, None)
                rueck_stats = rueck.get_stats()
                print(f"\nRückmeldungen:")
                print(f"  - Gesamt: {rueck_stats['gesamt']}")
                print(f"  - Gold-OK-Rate: {rueck_stats['gold_ok_rate']:.2%}")
                print(f"  - Werte-Statistik: {rueck_stats['werte_statistik']}")
                print("=" * 40)
                continue
            
            if user_input == "/zyklus":
                zyklus = Zyklus(identity.data)
                matrix = zyklus.matrix()
                print(f"\nAktueller Zyklus:")
                print(f"  - Sonne: {zyklus.sonne} ({matrix.get('grundmodus', '?')})")
                print(f"  - Mond: {zyklus.mond} ({matrix.get('stimmung', '?')})")
                print(f"  - Tag: {zyklus.tag} ({matrix.get('fokus', '?')})")
                continue
            
            if user_input == "/id":
                print(f"\nIdentität:")
                print(f"  - Name: {identity.data.get('name', '?')}")
                print(f"  - Grundton: {identity.data.get('grundton', '?')}")
                print(f"  - Version: {identity.data.get('version', '?')}")
                print(f"  - Use LLM: {identity.data.get('use_llm', False)}")
                continue
            
            # Normale Verarbeitung
            zyklus = Zyklus(identity.data)
            zyklus.fortschritt()
            zyklus.speichern(identity.data)
            
            # Interpretation
            interpretation = Interpretation(identity.data, zyklus)
            bedeutung = interpretation.verarbeite(user_input)
            
            # Seed generieren
            seed = Seed(identity.data, zyklus, llm_bridge)
            mandat = identity.data.get("mandat", {})
            modus = zyklus.matrix().get("fokus", "fokus")
            rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
            
            # WerteTeilen-Bewertung
            kontext = {
                "input": user_input,
                "mandat": mandat,
                "modus": modus,
                "deutung": bedeutung,
                "kontext_id": "du",
                "kontext_typ": "privat"
            }
            
            bewertung = werte_teilen.bewerte_interaktion(
                nutzer_input=user_input,
                antwort_entwurf=rohantwort,
                mandat=mandat,
                modus=modus,
                deutung=bedeutung,
                kontext_id=kontext["kontext_id"],
                kontext_typ=kontext["kontext_typ"]
            )
            kontext["bewertung"] = bewertung
            
            # Bewertung anzeigen
            print(werte_teilen.format_bewertung(bewertung))
            
            # Silky Edge
            se = SilkyEdge(identity.data, zyklus)
            antwort = se.veredeln(rohantwort, bedeutung)
            
            # Erfahrung speichern
            erfahrung = Erfahrung(identity.data, zyklus, werte_teilen)
            erfahrung.speichern(bedeutung, kontext=kontext)
            
            # Rückmeldung
            rueck = Rueckmeldung(identity.data, zyklus, werte_teilen)
            rueck.verarbeite(antwort, kontext=kontext)
            
            # Identität speichern
            Identity.save(identity.data)
            
            # Antwort ausgeben
            print(f"\n{identity.data.get('name', 'URASIL')}: {antwort}")
            
        except KeyboardInterrupt:
            print("\nBeende Session...")
            break
        except Exception as e:
            print(f"\n❌ Fehler: {e}")
            import traceback
            traceback.print_exc()
    
    # Session beenden
    session.end()
    print("\nSession beendet. Auf Wiedersehen!")


if __name__ == "__main__":
    # Prüfen, ob interaktiver Modus gewünscht ist
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive()
    else:
        # Einmalige Ausführung (für Tests)
        main()
