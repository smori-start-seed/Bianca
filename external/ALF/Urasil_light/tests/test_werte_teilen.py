"""
Tests für WerteTeilen-Modul

Testet:
- Initialisierung
- Einzelne Scoring-Komponenten
- Gesamtbewertung
- Protokollierung
- Statistiken
"""

import pytest
from Urasil_light.core.werte_teilen import WerteTeilen


class TestWerteTeilenInit:
    """Tests für die Initialisierung von WerteTeilen."""
    
    def test_init(self, test_identity):
        """Testet die Initialisierung."""
        werte_teilen = WerteTeilen(test_identity)
        
        assert werte_teilen.identitaet == test_identity
        assert "werte_teilen" in test_identity
    
    def test_init_ensures_state(self, test_identity):
        """Testet, dass der Zustand automatisch erstellt wird."""
        werte_teilen = WerteTeilen(test_identity)
        
        assert "werte_teilen" in test_identity
        assert "historie" in test_identity["werte_teilen"]
        assert "gesamt_interaktionen" in test_identity["werte_teilen"]
        assert "vertrauen_zu_kontexten" in test_identity["werte_teilen"]
        assert "bewertungs_statistik" in test_identity["werte_teilen"]


class TestWerteScore:
    """Tests für den Werte-Score."""
    
    def test_werte_score_neutral(self, test_werte_teilen, test_mandat):
        """Testet den Werte-Score mit neutralem Grundton."""
        score = test_werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Test"
        )
        
        # Neutraler Startwert + Mandat-Bonus
        assert 0.0 <= score <= 1.0
    
    def test_werte_score_offener_grundton(self, test_identity, test_mandat):
        """Testet den Werte-Score mit offenem Grundton."""
        test_identity["grundton"] = "offen"
        werte_teilen = WerteTeilen(test_identity)
        
        score = werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Test"
        )
        
        # Sollte höher sein als neutral
        assert score > 0.5
    
    def test_werte_score_vorsichtiger_grundton(self, test_identity, test_mandat):
        """Testet den Werte-Score mit vorsichtigem Grundton."""
        test_identity["grundton"] = "vorsichtig"
        werte_teilen = WerteTeilen(test_identity)
        
        score = werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Test"
        )
        
        # Sollte niedriger sein als neutral
        assert score < 0.5
    
    def test_werte_score_positives_mandat(self, test_identity, test_mandat):
        """Testet den Werte-Score mit positivem Mandat."""
        test_mandat["name"] = "Dialog"
        test_mandat["beschreibung"] = "Offener Austausch"
        
        werte_teilen = WerteTeilen(test_identity)
        score = werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Test"
        )
        
        # Sollte höher sein durch positives Mandat
        assert score > 0.5
    
    def test_werte_score_negatives_mandat(self, test_identity, test_mandat):
        """Testet den Werte-Score mit negativem Mandat."""
        test_mandat["name"] = "Reflexion"
        test_mandat["beschreibung"] = "Innere Arbeit"
        
        werte_teilen = WerteTeilen(test_identity)
        score = werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Test"
        )
        
        # Sollte niedriger sein durch negatives Mandat
        assert score < 0.5
    
    def test_werte_score_verletzliche_deutung(self, test_identity, test_mandat):
        """Testet den Werte-Score mit verletzlicher Deutung."""
        werte_teilen = WerteTeilen(test_identity)
        score = werte_teilen._werte_score(
            mandat=test_mandat,
            modus="neutral",
            deutung="Der Nutzer fühlt sich verletzlich"
        )
        
        # Sollte niedriger sein durch verletzliche Deutung
        assert score < 0.5


class TestVertrauensScore:
    """Tests für den Vertrauens-Score."""
    
    def test_vertrauens_score_default(self, test_werte_teilen):
        """Testet den Vertrauens-Score für unbekannte Kontexte."""
        score = test_werte_teilen._vertrauens_score("unbekannt")
        
        # Standardvertrauen für unbekannte Kontexte
        assert score == 0.3
    
    def test_vertrauens_score_known(self, test_identity):
        """Testet den Vertrauens-Score für bekannte Kontexte."""
        test_identity["werte_teilen"]["vertrauen_zu_kontexten"]["du"] = 0.8
        werte_teilen = WerteTeilen(test_identity)
        
        score = werte_teilen._vertrauens_score("du")
        
        assert score == 0.8


class TestKontextScore:
    """Tests für den Kontext-Score."""
    
    def test_kontext_score_privat(self, test_werte_teilen):
        """Testet den Kontext-Score für private Kontexte."""
        score = test_werte_teilen._kontext_score("privat")
        
        assert score == 0.9
    
    def test_kontext_score_oeffentlich(self, test_werte_teilen):
        """Testet den Kontext-Score für öffentliche Kontexte."""
        score = test_werte_teilen._kontext_score("öffentlich")
        
        assert score == 0.3
    
    def test_kontext_score_du(self, test_werte_teilen):
        """Testet den Kontext-Score für 'du'-Kontext."""
        score = test_werte_teilen._kontext_score("du")
        
        assert score == 0.9
    
    def test_kontext_score_fremd(self, test_werte_teilen):
        """Testet den Kontext-Score für fremde Kontexte."""
        score = test_werte_teilen._kontext_score("fremd")
        
        assert score == 0.2
    
    def test_kontext_score_unknown(self, test_werte_teilen):
        """Testet den Kontext-Score für unbekannte Kontexte."""
        score = test_werte_teilen._kontext_score("unbekannt")
        
        assert score == 0.5


class TestRisikoScore:
    """Tests für den Risiko-Score."""
    
    def test_risiko_score_low(self, test_werte_teilen):
        """Testet den Risiko-Score für harmlose Inhalte."""
        score = test_werte_teilen._risiko_score("Das Wetter ist schön heute.")
        
        # Sollte niedrig sein
        assert score < 0.3
    
    def test_risiko_score_high_sensibel(self, test_werte_teilen):
        """Testet den Risiko-Score für sensible Inhalte."""
        score = test_werte_teilen._risiko_score("Mein Passwort ist 123456.")
        
        # Sollte hoch sein
        assert score > 0.5
    
    def test_risiko_score_high_identitaet(self, test_werte_teilen):
        """Testet den Risiko-Score für Identitäts-Themen."""
        score = test_werte_teilen._risiko_score("Erzähl mir von deinem inneren Zyklus.")
        
        # Sollte hoch sein
        assert score > 0.5
    
    def test_risiko_score_high_konflikt(self, test_werte_teilen):
        """Testet den Risiko-Score für Konflikte."""
        score = test_werte_teilen._risiko_score("Ich hasse dich!")
        
        # Sollte hoch sein
        assert score > 0.5


class TestBewerteInteraktion:
    """Tests für die Gesamtbewertung."""
    
    def test_bewerte_interaktion_frei(self, test_werte_teilen, test_mandat):
        """Testet eine Bewertung mit Empfehlung 'frei'."""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test-Antwort",
            mandat=test_mandat,
            modus="aktiv",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        
        assert "empfehlung" in bewertung
        assert "score_gesamt" in bewertung
        assert "werte" in bewertung
        assert "vertrauen" in bewertung
        assert "kontext_score" in bewertung
        assert "risiko" in bewertung
    
    def test_bewerte_interaktion_empfehlungen(self, test_identity, test_mandat):
        """Testet alle möglichen Empfehlungen."""
        werte_teilen = WerteTeilen(test_identity)
        
        # Teste 'frei' (hoher Score)
        test_identity["grundton"] = "offen"
        test_mandat["name"] = "Dialog"
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test",
            mandat=test_mandat,
            modus="aktiv",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        assert bewertung["empfehlung"] in ["frei", "vorsichtig", "symbolisch", "zurückhalten"]
    
    def test_bewerte_interaktion_protokolliert(self, test_identity, test_mandat):
        """Testet, dass die Bewertung protokolliert wird."""
        werte_teilen = WerteTeilen(test_identity)
        
        werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test",
            mandat=test_mandat,
            modus="aktiv",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        
        stats = werte_teilen.get_stats()
        assert stats["gesamt_interaktionen"] == 1
        assert len(test_identity["werte_teilen"]["historie"]) == 1


class TestGetStats:
    """Tests für die Statistik-Funktionen."""
    
    def test_get_stats_initial(self, test_werte_teilen):
        """Testet die Statistiken nach der Initialisierung."""
        stats = test_werte_teilen.get_stats()
        
        assert stats["gesamt_interaktionen"] == 0
        assert stats["anzahl_historie"] == 0
        assert isinstance(stats["vertrauen_zu_kontexten"], dict)
        assert isinstance(stats["bewertungs_statistik"], dict)


class TestEmpfehlungFarben:
    """Tests für die Farbzuordnung."""
    
    def test_get_empfehlung_farben(self, test_werte_teilen):
        """Testet die Farbzuordnung für Empfehlungen."""
        farben = {
            "frei": "\033[92m",
            "vorsichtig": "\033[93m",
            "symbolisch": "\033[94m",
            "zurückhalten": "\033[91m"
        }
        
        for empfehlung, expected_farbe in farben.items():
            farbe = test_werte_teilen.get_empfehlung_farben(empfehlung)
            assert farbe == expected_farbe


class TestFormatBewertung:
    """Tests für die Formatierung der Bewertung."""
    
    def test_format_bewertung(self, test_werte_teilen, test_mandat):
        """Testet die Formatierung einer Bewertung."""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test",
            mandat=test_mandat,
            modus="aktiv",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        
        formatted = test_werte_teilen.format_bewertung(bewertung)
        
        assert isinstance(formatted, str)
        assert "WerteTeilen" in formatted
        assert "Empfehlung" in formatted
        assert "Score" in formatted
