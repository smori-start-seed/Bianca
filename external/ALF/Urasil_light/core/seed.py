"""
Seed Module für Urasil_light

Dieses Modul ist verantwortlich für die Generierung von Rohantworten.
Es kann entweder:
1. Einfache, deterministische Antworten generieren (Standard)
2. LLM-basierte Antworten generieren (falls LLMBridge verfügbar)

Die Auswahl hängt von der Konfiguration (use_llm) ab.

Beispiel:
    from core.seed import Seed
    from core.llm_bridge import LLMBridge
    from core.backends import create_default_backends
    
    # Ohne LLM (Standard)
    seed = Seed(identity.data, zyklus)
    antwort = seed.generiere("Hallo")
    
    # Mit LLM
    backends = create_default_backends()
    llm_bridge = LLMBridge(identity.data, backends)
    seed = Seed(identity.data, zyklus, llm_bridge)
    antwort = seed.generiere("Hallo")
"""

from typing import Dict, Any, Optional, List
from .mandate import Mandate


class Seed:
    """
    Generiert Rohantworten für Urasil_light.
    
    Diese Klasse kann entweder:
    - Einfache, deterministische Antworten generieren (basierend auf Zyklus)
    - LLM-basierte Antworten generieren (falls LLMBridge verfügbar)
    
    Die Entscheidung wird basierend auf der Konfiguration getroffen.
    """
    
    def __init__(
        self,
        identity: Dict[str, Any],
        zyklus,
        llm_bridge: Optional[Any] = None,
        mandat: Optional[Dict[str, Any]] = None
    ):
        """
        Initialisiert den Seed-Generator.
        
        Args:
            identity: Die Identität von Urasil_light
            zyklus: Das Zyklus-Objekt
            llm_bridge: Optional die LLMBridge für LLM-basierte Antworten
            mandat: Optional ein spezifisches Mandat (sonst aus identity)
        """
        self.identity = identity
        self.zyklus = zyklus
        self.mandate = Mandate(identity)
        self.llm_bridge = llm_bridge
        self._mandat = mandat or identity.get("mandat", {})
        
        # Prüfen, ob LLM genutzt werden soll
        self.use_llm = identity.get("use_llm", False) and llm_bridge is not None
    
    def generiere(
        self,
        bedeutung: str,
        mandat: Optional[Dict[str, Any]] = None,
        modus: Optional[str] = None
    ) -> str:
        """
        Generiert eine Rohantwort.
        
        Falls LLM aktiviert ist und verfügbar:
        - Nutzt LLMBridge für kontextbewusste Antworten
        
        Sonst:
        - Generiert einfache, deterministische Antworten basierend auf Zyklus
        
        Args:
            bedeutung: Die interpretierte Bedeutung der Nutzer-Eingabe
            mandat: Optional ein spezifisches Mandat
            modus: Optional ein spezifischer Modus (sonst aus Zyklus)
            
        Returns:
            Die generierte Rohantwort
        """
        # Mandat und Modus bestimmen
        mandat = mandat or self._mandat
        modus = modus or self.zyklus.matrix().get("fokus", "fokus")
        
        # Falls LLM aktiviert und verfügbar
        if self.use_llm and self.llm_bridge:
            try:
                return self._generiere_mit_llm(bedeutung, mandat, modus)
            except Exception as e:
                print(f"⚠️ LLM-Generierung fehlgeschlagen: {e}")
                print("   Nutze Fallback-Methode.")
                return self._generiere_fallback(bedeutung, mandat, modus)
        
        # Standard: Einfache Generierung
        return self._generiere_fallback(bedeutung, mandat, modus)
    
    def _generiere_mit_llm(
        self,
        bedeutung: str,
        mandat: Dict[str, Any],
        modus: str
    ) -> str:
        """
        Generiert eine Antwort mit LLM.
        
        Args:
            bedeutung: Die interpretierte Bedeutung
            mandat: Das aktuelle Mandat
            modus: Der aktuelle Modus
            
        Returns:
            Die LLM-generierte Antwort
        """
        # Kontext für LLMBridge vorbereiten
        erfahrung = self.identity.get("erfahrung", [])
        nodus = self.identity.get("nodus", {})
        
        # LLMBridge generieren lassen
        return self.llm_bridge.generiere_antwort(
            nutzer_input=bedeutung,  # oder originaler Input?
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            erfahrung=erfahrung,
            nodus=nodus
        )
    
    def _generiere_fallback(
        self,
        bedeutung: str,
        mandat: Dict[str, Any],
        modus: str
    ) -> str:
        """
        Generiert eine einfache, deterministische Antwort (Fallback).
        
        Diese Methode wird verwendet, wenn:
        - LLM nicht aktiviert ist
        - LLM nicht verfügbar ist
        - Ein Fehler bei der LLM-Generierung auftritt
        
        Args:
            bedeutung: Die interpretierte Bedeutung
            mandat: Das aktuelle Mandat
            modus: Der aktuelle Modus
            
        Returns:
            Eine einfache Rohantwort
        """
        # Reflexionssignal aus der Identität
        reflex = self.identity.get("letzte_korrektur", "ok")
        
        # Antwort basierend auf Modus generieren
        if modus == "fokus":
            antwort = f"Direkt: {bedeutung}"
        elif modus == "variation":
            antwort = f"Alternative Sicht: {bedeutung}"
        else:  # synthese
            antwort = f"Zusammenhang: {bedeutung}"
        
        # Wenn letzte Antwort nicht gold-konform war → mehr Klarheit
        if reflex == "gold":
            antwort = "Klarer: " + antwort
        
        return antwort
    
    def get_llm_stats(self) -> Optional[Dict[str, Any]]:
        """
        Gibt Statistiken zur LLM-Nutzung zurück (falls verfügbar).
        
        Returns:
            Dictionary mit LLM-Statistiken oder None
        """
        if self.llm_bridge:
            return self.llm_bridge.get_stats()
        return None
