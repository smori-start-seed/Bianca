"""
Erfahrung Module für Urasil_light

Dieses Modul ist verantwortlich für das Speichern von Erfahrungen.
Es implementiert einen Wertefilter, der sicherstellt, dass nur:
1. Reife Erfahrungen (Ininity-Filter)
2. Wertekonforme Erfahrungen (WerteTeilen-Filter)

gespeichert werden.

Beispiel:
    from core.erfahrung import Erfahrung
    from core.werte_teilen import WerteTeilen
    
    erfahrung = Erfahrung(identity.data, zyklus)
    erfahrung.speichern("Eine tiefe Erkenntnis", kontext={"bewertung": {"empfehlung": "frei"}})
"""

from typing import Dict, Any, Optional, List
from .ininity import Ininity


class Erfahrung:
    """
    Verwaltet das Speichern von Erfahrungen in Urasil_light.
    
    Erfahrungen werden nur gespeichert, wenn sie:
    1. Reif sind (Ininity-Filter)
    2. Wertekonform sind (WerteTeilen-Filter, falls verfügbar)
    
    Dies stellt sicher, dass die Identität nur mit qualitativ hochwertigen
    Erfahrungen angereichert wird.
    """
    
    def __init__(
        self,
        identity: Dict[str, Any],
        zyklus,
        werte_teilen: Optional[Any] = None
    ):
        """
        Initialisiert das Erfahrung-Modul.
        
        Args:
            identity: Die Identität von Urasil_light
            zyklus: Das Zyklus-Objekt
            werte_teilen: Optional das WerteTeilen-Modul für dynamische Bewertung
        """
        self.identity = identity
        self.zyklus = zyklus
        self.ininity = Ininity()
        self.werte_teilen = werte_teilen
    
    def speichern(
        self,
        bedeutung: str,
        kontext: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Speichert eine Erfahrung, falls sie die Filter passiert.
        
        Filter:
        1. Ininity-Filter: Ist die Erfahrung reif?
        2. WerteTeilen-Filter: Soll die Erfahrung geteilt werden?
        
        Args:
            bedeutung: Die zu speichernde Erfahrung
            kontext: Optional ein Kontext-Dictionary mit:
                   - bewertung: WerteTeilen-Bewertung
                   - input: Originaler Nutzer-Input
                   - mandat: Aktuelles Mandat
                   - modus: Aktueller Modus
                   - deutung: Innere Interpretation
                   - kontext_id: Kontext-Identifier
                   - kontext_typ: Kontext-Typ
        
        Returns:
            True, wenn die Erfahrung gespeichert wurde, sonst False
        """
        # 1. Ininity-Filter: Ist die Erfahrung reif?
        if not self.ininity.ist_reif(bedeutung):
            return False
        
        # 2. WerteTeilen-Filter: Soll die Erfahrung geteilt werden?
        if self.werte_teilen and kontext:
            bewertung = kontext.get("bewertung")
            if bewertung and bewertung.get("empfehlung") == "zurückhalten":
                return False
        
        # Erfahrung speichern
        erf = self.identity.get("erfahrung", [])
        
        eintrag = {
            "zeit": self.zyklus.jetzt_iso(),
            "inhalt": bedeutung,
            "kategorie": "erfahrung",
            "gewicht": 1.0
        }
        
        # Zusätzliche Metadaten aus Kontext
        if kontext:
            eintrag["mandat"] = kontext.get("mandat", {})
            eintrag["modus"] = kontext.get("modus")
            eintrag["werte_bewertung"] = kontext.get("bewertung")
        
        erf.append(eintrag)
        self.identity["erfahrung"] = erf
        
        return True
    
    def get_letzte_erfahrungen(self, anzahl: int = 5) -> List[Dict[str, Any]]:
        """
        Gibt die letzten Erfahrungen zurück.
        
        Args:
            anzahl: Anzahl der zurückzugebenden Erfahrungen
            
        Returns:
            Liste der letzten Erfahrungen
        """
        erfahrungen = self.identity.get("erfahrung", [])
        return erfahrungen[-anzahl:] if erfahrungen else []
    
    def get_erfahrungen_by_kategorie(self, kategorie: str) -> List[Dict[str, Any]]:
        """
        Gibt alle Erfahrungen einer bestimmten Kategorie zurück.
        
        Args:
            kategorie: Die Kategorie (z. B. "erfahrung", "mandat", "modus")
            
        Returns:
            Liste der Erfahrungen dieser Kategorie
        """
        erfahrungen = self.identity.get("erfahrung", [])
        return [e for e in erfahrungen if e.get("kategorie") == kategorie]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zu den Erfahrungen zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        erfahrungen = self.identity.get("erfahrung", [])
        
        return {
            "gesamt": len(erfahrungen),
            "kategorien": self._zaehle_kategorien(erfahrungen)
        }
    
    def _zaehle_kategorien(self, erfahrungen: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Zählt die Erfahrungen nach Kategorien.
        
        Args:
            erfahrungen: Liste der Erfahrungen
            
        Returns:
            Dictionary mit Kategorie → Anzahl
        """
        kategorien = {}
        for e in erfahrungen:
            kat = e.get("kategorie", "unbekannt")
            kategorien[kat] = kategorien.get(kat, 0) + 1
        return kategorien
