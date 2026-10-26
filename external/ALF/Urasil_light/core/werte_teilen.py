"""
WerteTeilen Module für Urasil_light

Dieses Modul implementiert ein fließendes Wertescoring-System, das:
- Jede Interaktion entlang von Werten, Vertrauen, Kontext und Risiko bewertet
- Keine harten Ja/Nein-Entscheidungen trifft, sondern Tendenzen zurückgibt
- Urasil_light ermöglicht, seinen Stil des Teilens dynamisch anzupassen

Die Bewertung basiert auf vier Komponenten:
1. Werte-Score: Passt die Interaktion zu den aktuellen Werten von Urasil?
2. Vertrauens-Score: Wie sehr vertraut Urasil dem aktuellen Kontext?
3. Kontext-Score: Wie passend ist der Kontext für das Teilen?
4. Risiko-Score: Wie hoch ist das Risiko von Missverständnissen?

Empfehlungen:
- "frei": Antwort kann ohne Einschränkungen geteilt werden
- "vorsichtig": Antwort sollte mit Bedacht geteilt werden
- "symbolisch": Antwort nur symbolisch/abstrakt teilen
- "zurückhalten": Antwort sollte nicht geteilt werden

Beispiel:
    from core.werte_teilen import WerteTeilen
    from core.identity import Identity
    
    identity = Identity.load()
    werte_teilen = WerteTeilen(identity.data)
    
    bewertung = werte_teilen.bewerte_interaktion(
        nutzer_input="Was ist mein Passwort?",
        antwort_entwurf="Dein Passwort ist 123456",
        mandat={"name": "Sicherheit"},
        modus="aktiv",
        deutung="Der Nutzer fragt nach sensiblen Daten",
        kontext_id="fremd",
        kontext_typ="öffentlich"
    )
    # → bewertung["empfehlung"] = "zurückhalten"
"""

import datetime
from typing import Dict, Any, Optional, List


class WerteTeilen:
    """
    Fließendes Wertescoring für Urasil_light.
    
    Diese Klasse bewertet jede Interaktion und gibt eine Tendenz zurück,
    die Urasil_light nutzen kann, um zu entscheiden, wie eine Antwort geteilt wird.
    
    Die Bewertung ist dynamisch und lernt aus vergangenen Interaktionen.
    """
    
    def __init__(self, identitaet: Dict[str, Any]):
        """
        Initialisiert das WerteTeilen-Modul.
        
        Args:
            identitaet: Die Identität von Urasil_light (Dictionary)
        """
        self.identitaet = identitaet
        self._ensure_state()
    
    def _ensure_state(self) -> None:
        """Stellt sicher, dass der WerteTeilen-Zustand in der Identität existiert."""
        if "werte_teilen" not in self.identitaet:
            self.identitaet["werte_teilen"] = {
                "historie": [],
                "gesamt_interaktionen": 0,
                "vertrauen_zu_kontexten": {},
                "bewertungs_statistik": {
                    "frei": 0,
                    "vorsichtig": 0,
                    "symbolisch": 0,
                    "zurückhalten": 0
                }
            }
    
    def _jetzt(self) -> str:
        """Gibt den aktuellen Zeitstempel im ISO-Format zurück."""
        return datetime.datetime.utcnow().isoformat() + "Z"
    
    # -------------------------------------------------
    #   SCORING-KOMPONENTEN
    # -------------------------------------------------
    
    def _werte_score(self, mandat: Dict[str, Any], modus: str, deutung: str) -> float:
        """
        Bewertet, wie sehr das Teilen zu Urasils Werten in diesem Zustand passt.
        
        Berücksichtigt:
        - Grundton der Identität (z. B. "offen", "vorsichtig")
        - Aktuelles Mandat (z. B. "Dialog", "Reflexion")
        - Innere Interpretation (z. B. "verletzlich")
        
        Args:
            mandat: Das aktuelle Mandat
            modus: Der aktuelle Modus
            deutung: Die innere Interpretation
            
        Returns:
            Score zwischen 0.0 (passt nicht) und 1.0 (passt perfekt)
        """
        grundton = self.identitaet.get("grundton", "neutral").lower()
        score = 0.5  # Neutraler Startwert
        
        # Grundton-Bewertung
        if any(wort in grundton for wort in ["offen", "zugewandt", "resonant", "harmonisch"]):
            score += 0.2
        if any(wort in grundton for wort in ["vorsichtig", "zurückhaltend", "neutral"]):
            score -= 0.1
        
        # Mandat-Bewertung
        mandat_name = mandat.get("name", "").lower()
        mandat_beschreibung = mandat.get("beschreibung", "").lower()
        
        # Positive Mandate (fördern das Teilen)
        positive_mandate = [
            "beziehung", "dialog", "verbindung", "austausch", "kommunikation",
            "offenheit", "transparenz", "teilung", "gemeinschaft", "harmonie"
        ]
        if any(w in mandat_name or w in mandat_beschreibung for w in positive_mandate):
            score += 0.2
        
        # Negative Mandate (hemmen das Teilen)
        negative_mandate = [
            "innen", "reflexion", "nacht", "schutz", "sicherheit", "privat",
            "geheim", "verborgen", "stille"
        ]
        if any(w in mandat_name or w in mandat_beschreibung for w in negative_mandate):
            score -= 0.1
        
        # Modus-Bewertung
        if modus in ["aktiv", "wach", "tag", "dialog"]:
            score += 0.1  # Aktive Phasen fördern das Teilen
        elif modus in ["reflexiv", "nacht", "innen"]:
            score -= 0.1  # Reflexive Phasen hemmen das Teilen
        
        # Deutung-Bewertung
        if "verletzlich" in deutung.lower():
            score -= 0.2
        if "offen" in deutung.lower() or "teilung" in deutung.lower():
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _vertrauens_score(self, kontext_id: str) -> float:
        """
        Bewertet das Vertrauen in einen bestimmten Kontext.
        
        Das Vertrauen entwickelt sich über Zeit:
        - "frei"-Bewertungen erhöhen das Vertrauen
        - "zurückhalten"-Bewertungen verringern das Vertrauen
        
        Args:
            kontext_id: Identifier für den Kontext (z. B. "du", "fremd", "community")
            
        Returns:
            Score zwischen 0.0 (kein Vertrauen) und 1.0 (volles Vertrauen)
        """
        state = self.identitaet["werte_teilen"]
        vertrauen = state["vertrauen_zu_kontexten"].get(kontext_id, 0.3)
        return max(0.0, min(1.0, vertrauen))
    
    def _kontext_score(self, kontext_typ: str) -> float:
        """
        Bewertet, wie passend der Kontext für das Teilen ist.
        
        Args:
            kontext_typ: Typ des Kontexts (z. B. "privat", "öffentlich", "anonym")
            
        Returns:
            Score zwischen 0.0 (unpassend) und 1.0 (perfekt passend)
        """
        kontext_typ = kontext_typ.lower()
        
        # Kontext-Bewertungen
        kontext_bewertungen = {
            "privat": 0.9,
            "lokal": 0.9,
            "du": 0.9,
            "freund": 0.8,
            "familie": 0.8,
            "community": 0.7,
            "halböffentlich": 0.6,
            "arbeit": 0.5,
            "anonym": 0.4,
            "öffentlich": 0.3,
            "fremd": 0.2
        }
        
        return kontext_bewertungen.get(kontext_typ, 0.5)
    
    def _risiko_score(self, inhalt: str) -> float:
        """
        Bewertet das Risiko, dass das Teilen zu Missverständnissen oder Problemen führt.
        
        Berücksichtigt:
        - Sensible Themen (Identität, Mandate, Nodus)
        - Konflikte oder negative Emotionen
        - Persönliche oder private Informationen
        
        Args:
            inhalt: Der Inhalt, der geteilt werden soll
            
        Returns:
            Score zwischen 0.0 (kein Risiko) und 1.0 (hohes Risiko)
        """
        text = inhalt.lower()
        score = 0.1  # Grundrisiko
        
        # Sensible Themen
        sensible_themen = [
            "identität", "innerer zyklus", "mandate", "nodus", "kern",
            "verletzlich", "geheim", "privat", "passwort", "sicherheit",
            "persönlich", "intim", "vertraulich", "geheimnis"
        ]
        if any(thema in text for thema in sensible_themen):
            score += 0.4
        
        # Konflikte
        konflikt_wörter = [
            "konflikt", "angriff", "kampf", "streit", "feind",
            "hass", "wut", "aggression", "gewalt", "verletzung"
        ]
        if any(wort in text for wort in konflikt_wörter):
            score += 0.3
        
        # Negative Emotionen
        negative_emotionen = [
            "traurig", "depressiv", "ängstlich", "verzweifelt",
            "wütend", "enttäuscht", "verraten", "verlassen"
        ]
        if any(emotion in text for emotion in negative_emotionen):
            score += 0.2
        
        # Persönliche Daten
        persönliche_daten = [
            "name", "adresse", "telefon", "email", "geburtsdatum",
            "kontonummer", "kreditkarte", "passwort", "pin"
        ]
        if any(datum in text for datum in persönliche_daten):
            score += 0.5
        
        return max(0.0, min(1.0, score))
    
    # -------------------------------------------------
    #   GESAMT-SCORING
    # -------------------------------------------------
    
    def bewerte_interaktion(
        self,
        nutzer_input: str,
        antwort_entwurf: str,
        mandat: Dict[str, Any],
        modus: str,
        deutung: str,
        kontext_id: str = "fremd",
        kontext_typ: str = "öffentlich"
    ) -> Dict[str, Any]:
        """
        Bewertet eine Interaktion und gibt eine Tendenz für das Teilen zurück.
        
        Die Bewertung basiert auf:
        - Werte-Score (40% Gewichtung)
        - Vertrauens-Score (30% Gewichtung)
        - Kontext-Score (30% Gewichtung)
        - Risiko-Score (wird abgezogen)
        
        Args:
            nutzer_input: Die Eingabe des Nutzers
            antwort_entwurf: Der Entwurf der Antwort, die bewertet werden soll
            mandat: Das aktuelle Mandat
            modus: Der aktuelle Modus
            deutung: Die innere Interpretation
            kontext_id: Identifier für den Kontext (z. B. "du", "community")
            kontext_typ: Typ des Kontexts (z. B. "privat", "öffentlich")
            
        Returns:
            Dictionary mit:
            - score_gesamt: Gesamt-Score (-1.0 bis +1.0)
            - empfehlung: "frei", "vorsichtig", "symbolisch", "zurückhalten"
            - komponenten: Einzelne Scores (werte, vertrauen, kontext, risiko)
            - zeit: Zeitstempel der Bewertung
            - kontext_id: Der verwendete Kontext-Identifier
            - kontext_typ: Der verwendete Kontext-Typ
        """
        # Einzelne Scores berechnen
        werte = self._werte_score(mandat, modus, deutung)
        vertrauen = self._vertrauens_score(kontext_id)
        kontext = self._kontext_score(kontext_typ)
        risiko = self._risiko_score(antwort_entwurf)
        
        # Gewichteter Gesamt-Score
        # Formel: (werte * 0.4 + vertrauen * 0.3 + kontext * 0.3) - risiko
        roh_score = (werte * 0.4 + vertrauen * 0.3 + kontext * 0.3) - risiko
        score_gesamt = max(-1.0, min(1.0, roh_score))
        
        # Empfehlung basierend auf Score
        if score_gesamt > 0.5:
            empfehlung = "frei"
        elif score_gesamt > 0.1:
            empfehlung = "vorsichtig"
        elif score_gesamt > -0.2:
            empfehlung = "symbolisch"
        else:
            empfehlung = "zurückhalten"
        
        # Ergebnis zusammenstellen
        ergebnis = {
            "zeit": self._jetzt(),
            "kontext_id": kontext_id,
            "kontext_typ": kontext_typ,
            "werte": round(werte, 3),
            "vertrauen": round(vertrauen, 3),
            "kontext_score": round(kontext, 3),
            "risiko": round(risiko, 3),
            "score_gesamt": round(score_gesamt, 3),
            "empfehlung": empfehlung
        }
        
        # Protokollieren
        self._protokoll(ergebnis, kontext_id)
        
        return ergebnis
    
    def _protokoll(self, ergebnis: Dict[str, Any], kontext_id: str) -> None:
        """
        Protokolliert eine Bewertung in der Historie.
        
        Args:
            ergebnis: Das Bewertungsergebnis
            kontext_id: Der verwendete Kontext-Identifier
        """
        state = self.identitaet["werte_teilen"]
        state["gesamt_interaktionen"] += 1
        state["historie"].append(ergebnis)
        
        # Statistik aktualisieren
        empfehlung = ergebnis["empfehlung"]
        state["bewertungs_statistik"][empfehlung] = \
            state["bewertungs_statistik"].get(empfehlung, 0) + 1
        
        # Vertrauen anpassen (lernend)
        vertrauen = state["vertrauen_zu_kontexten"].get(kontext_id, 0.3)
        if empfehlung == "frei":
            vertrauen += 0.02
        elif empfehlung == "zurückhalten":
            vertrauen -= 0.01
        
        state["vertrauen_zu_kontexten"][kontext_id] = max(0.0, min(1.0, vertrauen))
        
        # Historie begrenzen (max. 1000 Einträge)
        if len(state["historie"]) > 1000:
            state["historie"] = state["historie"][-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken zum WerteTeilen-Modul zurück.
        
        Returns:
            Dictionary mit Statistiken
        """
        state = self.identitaet.get("werte_teilen", {})
        return {
            "gesamt_interaktionen": state.get("gesamt_interaktionen", 0),
            "vertrauen_zu_kontexten": state.get("vertrauen_zu_kontexten", {}),
            "bewertungs_statistik": state.get("bewertungs_statistik", {}),
            "anzahl_historie": len(state.get("historie", []))
        }
    
    def get_empfehlung_farben(self, empfehlung: str) -> str:
        """
        Gibt eine Farbe für die Empfehlung zurück (für Logging/Output).
        
        Args:
            empfehlung: Die Empfehlung ("frei", "vorsichtig", "symbolisch", "zurückhalten")
            
        Returns:
            ANSI-Farbecode für die Konsole
        """
        farben = {
            "frei": "\033[92m",      # Grün
            "vorsichtig": "\033[93m", # Gelb
            "symbolisch": "\033[94m", # Blau
            "zurückhalten": "\033[91m" # Rot
        }
        return farben.get(empfehlung, "\033[0m")
    
    def format_bewertung(self, bewertung: Dict[str, Any]) -> str:
        """
        Formatiert eine Bewertung für die Konsole.
        
        Args:
            bewertung: Das Bewertungsergebnis
            
        Returns:
            Formatierter String für die Ausgabe
        """
        farbe = self.get_empfehlung_farben(bewertung["empfehlung"])
        reset = "\033[0m"
        
        return (
            f"{farbe}[WerteTeilen]{reset} "
            f"Empfehlung: {farbe}{bewertung['empfehlung']}{reset} "
            f"(Score: {bewertung['score_gesamt']:.3f}) | "
            f"Werte: {bewertung['werte']:.2f} | "
            f"Vertrauen: {bewertung['vertrauen']:.2f} | "
            f"Kontext: {bewertung['kontext_score']:.2f} | "
            f"Risiko: {bewertung['risiko']:.2f}"
        )
