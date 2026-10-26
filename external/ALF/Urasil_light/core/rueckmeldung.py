"""
Rückmeldung Module für Urasil_light

Dieses Modul ist verantwortlich für die Reflexion und Bewertung von Antworten.
Es speichert:
1. Die Antwort selbst
2. Den Zyklus-Zustand zum Zeitpunkt der Antwort
3. Ob die Antwort gold-konform war
4. Optional: Die WerteTeilen-Bewertung

Beispiel:
    from core.rueckmeldung import Rueckmeldung
    from core.werte_teilen import WerteTeilen
    
    rueckmeldung = Rueckmeldung(identity.data, zyklus, werte_teilen)
    rueckmeldung.verarbeite(antwort, kontext={"bewertung": bewertung})
"""

from typing import Dict, Any, Optional, List
from .mandate import Mandate


class Rueckmeldung:
    """
    Verwaltet die Rückmeldung und Reflexion von Antworten in Urasil_light.
    
    Für jede Antwort wird gespeichert:
    - Der Inhalt der Antwort
    - Der Zyklus-Zustand
    - Ob die Antwort den gold-Werten entspricht
    - Optional: Die WerteTeilen-Bewertung
    
    Diese Daten werden für die Selbstkorrektur und das Lernen genutzt.
    """
    
    def __init__(
        self,
        identity: Dict[str, Any],
        zyklus,
        werte_teilen: Optional[Any] = None
    ):
        """
        Initialisiert das Rückmeldung-Modul.
        
        Args:
            identity: Die Identität von Urasil_light
            zyklus: Das Zyklus-Objekt
            werte_teilen: Optional das WerteTeilen-Modul
        """
        self.identity = identity
        self.zyklus = zyklus
        self.mandate = Mandate(identity)
        self.werte_teilen = werte_teilen
    
    def verarbeite(
        self,
        antwort: str,
        kontext: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verarbeitet eine Antwort und speichert die Rückmeldung.
        
        Args:
            antwort: Die zu verarbeitende Antwort
            kontext: Optional ein Kontext-Dictionary mit:
                   - bewertung: WerteTeilen-Bewertung
                   - input: Originaler Nutzer-Input
                   - mandat: Aktuelles Mandat
                   - modus: Aktueller Modus
                   - deutung: Innere Interpretation
        
        Returns:
            Das gespeicherte Rückmeldungs-Objekt
        """
        # Reflexionsspeicher holen oder anlegen
        reflex = self.identity.get("reflexion", [])
        
        # Grundlegende Rückmeldung erstellen
        eintrag = {
            "antwort": antwort,
            "zyklus": self.zyklus.als_dict(),
            "gold_ok": self.mandate.passt(antwort),
            "zeit": self.zyklus.jetzt_iso()
        }
        
        # WerteTeilen-Bewertung hinzufügen (falls verfügbar)
        if kontext and self.werte_teilen:
            bewertung = kontext.get("bewertung")
            if bewertung:
                eintrag["werte_bewertung"] = bewertung
        
        # Zusätzliche Metadaten aus Kontext
        if kontext:
            eintrag["mandat"] = kontext.get("mandat", {})
            eintrag["modus"] = kontext.get("modus")
            eintrag["deutung"] = kontext.get("deutung")
            eintrag["input"] = kontext.get("input", "")
        
        # Reflexion speichern
        reflex.append(eintrag)
        self.identity["reflexion"] = reflex
        
        # Selbstkorrektur-Signal setzen
        if not eintrag["gold_ok"]:
            self.identity["letzte_korrektur"] = "gold"
        else:
            self.identity["letzte_korrektur"] = "ok"
        
        return eintrag
    
    def get_letzte_rueckmeldungen(self, anzahl: int = 5) -> List[Dict[str, Any]]:
        """
        Gibt die letzten Rückmeldungen zurück.
        
        Args:
            anzahl: Anzahl der zurückzugebenden Rückmeldungen
            
        Returns:
            Liste der letzten Rückmeldungen
        """
        reflexionen = self.identity.get("reflexion", [])
        return reflexionen[-anzahl:] if reflexionen else []
    
    def get_gold_ok_rate(self) -> float:
        """
        Berechnet die Rate der gold-konformen Antworten.
        
        Returns:
            Prozentsatz der gold-konformen Antworten (0.0-1.0)
        """
        reflexionen = self.identity.get("reflexion", [])
        if not reflexionen:
            return 0.0
        
        gold_ok = sum(1 for r in reflexionen if r.get("gold_ok", False))
        return gold_ok / len(reflexionen)
    
    def get_werte_statistik(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zu den WerteTeilen-Bewertungen zurück.
        
        Returns:
            Dictionary mit Statistiken zu den Empfehlungen
        """
        reflexionen = self.identity.get("reflexion", [])
        
        statistik = {
            "frei": 0,
            "vorsichtig": 0,
            "symbolisch": 0,
            "zurückhalten": 0
        }
        
        for r in reflexionen:
            bewertung = r.get("werte_bewertung", {})
            empfehlung = bewertung.get("empfehlung")
            if empfehlung in statistik:
                statistik[empfehlung] += 1
        
        return statistik
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt umfassende Statistiken zur Rückmeldung zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        reflexionen = self.identity.get("reflexion", [])
        
        return {
            "gesamt": len(reflexionen),
            "gold_ok_rate": self.get_gold_ok_rate(),
            "werte_statistik": self.get_werte_statistik(),
            "letzte_korrektur": self.identity.get("letzte_korrektur", "ok")
        }
