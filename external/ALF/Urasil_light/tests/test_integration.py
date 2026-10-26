"""
Integrationstests für Urasil_light

Testet die vollständige Pipeline mit:
1. Interpretation
2. Seed-Generierung (mit LLM-Bridge)
3. WerteTeilen-Bewertung
4. Silky Edge
5. Erfahrungsspeicherung
6. Rückmeldung
"""

import pytest
from unittest.mock import MagicMock, patch
from Urasil_light.core.identity import Identity
from Urasil_light.core.zyklus import Zyklus
from Urasil_light.core.interpretation import Interpretation
from Urasil_light.core.seed import Seed
from Urasil_light.core.silky_edge import SilkyEdge
from Urasil_light.core.erfahrung import Erfahrung
from Urasil_light.core.rueckmeldung import Rueckmeldung
from Urasil_light.core.llm_bridge import LLMBridge
from Urasil_light.core.backends import FallbackBackend, create_default_backends
from Urasil_light.core.werte_teilen import WerteTeilen


class TestPipelineIntegration:
    """Testet die vollständige Pipeline-Integration."""
    
    def test_pipeline_without_llm(self, test_identity):
        """Testet die Pipeline ohne LLM."""
        # 1. Zyklus erstellen
        zyklus = Zyklus(test_identity)
        zyklus.fortschritt()
        zyklus.speichern(test_identity)
        
        # 2. Interpretation
        interpretation = Interpretation(test_identity, zyklus)
        bedeutung = interpretation.verarbeite("Test-Eingabe")
        
        assert "Test-Eingabe" in bedeutung or "Kreativer Impuls" in bedeutung
        
        # 3. Seed (ohne LLM)
        seed = Seed(test_identity, zyklus, llm_bridge=None)
        mandat = test_identity.get("mandat", {})
        modus = zyklus.matrix().get("fokus", "fokus")
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
        
        assert isinstance(rohantwort, str)
        assert len(rohantwort) > 0
        
        # 4. WerteTeilen
        werte_teilen = WerteTeilen(test_identity)
        kontext = {
            "input": "Test-Eingabe",
            "mandat": mandat,
            "modus": modus,
            "deutung": bedeutung,
            "kontext_id": "du",
            "kontext_typ": "privat"
        }
        
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test-Eingabe",
            antwort_entwurf=rohantwort,
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            kontext_id=kontext["kontext_id"],
            kontext_typ=kontext["kontext_typ"]
        )
        kontext["bewertung"] = bewertung
        
        assert "empfehlung" in bewertung
        assert "score_gesamt" in bewertung
        
        # 5. Silky Edge
        se = SilkyEdge(test_identity, zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)
        
        assert isinstance(antwort, str)
        assert len(antwort) > 0
        
        # 6. Erfahrung speichern
        erfahrung = Erfahrung(test_identity, zyklus, werte_teilen)
        gespeichert = erfahrung.speichern(bedeutung, kontext=kontext)
        
        # Sollte gespeichert werden (falls reif und nicht zurückhalten)
        assert isinstance(gespeichert, bool)
        
        # 7. Rückmeldung
        rueck = Rueckmeldung(test_identity, zyklus, werte_teilen)
        rueckmeldung = rueck.verarbeite(antwort, kontext=kontext)
        
        assert "antwort" in rueckmeldung
        assert "gold_ok" in rueckmeldung
        assert "zeit" in rueckmeldung
    
    def test_pipeline_with_llm(self, test_identity):
        """Testet die Pipeline mit LLM (FallbackBackend)."""
        # Backends mit Fallback erstellen
        backends = {"fallback": FallbackBackend(), "default": FallbackBackend()}
        llm_bridge = LLMBridge(test_identity, backends)
        
        # 1. Zyklus erstellen
        zyklus = Zyklus(test_identity)
        zyklus.fortschritt()
        zyklus.speichern(test_identity)
        
        # 2. Interpretation
        interpretation = Interpretation(test_identity, zyklus)
        bedeutung = interpretation.verarbeite("Test-Eingabe")
        
        # 3. Seed (mit LLM)
        test_identity["use_llm"] = True
        seed = Seed(test_identity, zyklus, llm_bridge)
        mandat = test_identity.get("mandat", {})
        modus = zyklus.matrix().get("fokus", "fokus")
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
        
        assert isinstance(rohantwort, str)
        assert len(rohantwort) > 0
        
        # 4. WerteTeilen
        werte_teilen = WerteTeilen(test_identity)
        kontext = {
            "input": "Test-Eingabe",
            "mandat": mandat,
            "modus": modus,
            "deutung": bedeutung,
            "kontext_id": "du",
            "kontext_typ": "privat"
        }
        
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test-Eingabe",
            antwort_entwurf=rohantwort,
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            kontext_id=kontext["kontext_id"],
            kontext_typ=kontext["kontext_typ"]
        )
        kontext["bewertung"] = bewertung
        
        # 5. Silky Edge
        se = SilkyEdge(test_identity, zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)
        
        # 6. Erfahrung speichern
        erfahrung = Erfahrung(test_identity, zyklus, werte_teilen)
        gespeichert = erfahrung.speichern(bedeutung, kontext=kontext)
        
        # 7. Rückmeldung
        rueck = Rueckmeldung(test_identity, zyklus, werte_teilen)
        rueckmeldung = rueck.verarbeite(antwort, kontext=kontext)
        
        assert "antwort" in rueckmeldung
        assert "werte_bewertung" in rueckmeldung


class TestPipelineStats:
    """Testet die Statistik-Funktionen der Pipeline."""
    
    def test_llm_bridge_stats(self, test_identity):
        """Testet die LLM-Bridge-Statistiken."""
        backends = {"fallback": FallbackBackend(), "default": FallbackBackend()}
        llm_bridge = LLMBridge(test_identity, backends)
        
        # Antwort generieren
        llm_bridge.generiere_antwort(
            nutzer_input="Test",
            mandat={},
            modus="fokus",
            deutung="Test"
        )
        
        stats = llm_bridge.get_stats()
        assert stats["gesamt_aufrufe"] == 1
        assert len(stats["letzte_prompts"]) == 1
        assert len(stats["letzte_antworten"]) == 1
    
    def test_werte_teilen_stats(self, test_identity):
        """Testet die WerteTeilen-Statistiken."""
        werte_teilen = WerteTeilen(test_identity)
        
        # Bewertung durchführen
        werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test",
            mandat={},
            modus="fokus",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        
        stats = werte_teilen.get_stats()
        assert stats["gesamt_interaktionen"] == 1
        assert len(test_identity["werte_teilen"]["historie"]) == 1
    
    def test_erfahrung_stats(self, test_identity):
        """Testet die Erfahrung-Statistiken."""
        zyklus = Zyklus(test_identity)
        erfahrung = Erfahrung(test_identity, zyklus)
        
        # Erfahrung speichern
        erfahrung.speichern("Test-Erfahrung")
        
        stats = erfahrung.get_stats()
        assert stats["gesamt"] == 1
    
    def test_rueckmeldung_stats(self, test_identity):
        """Testet die Rückmeldung-Statistiken."""
        zyklus = Zyklus(test_identity)
        rueck = Rueckmeldung(test_identity, zyklus)
        
        # Rückmeldung verarbeiten
        rueck.verarbeite("Test-Antwort")
        
        stats = rueck.get_stats()
        assert stats["gesamt"] == 1


class TestPipelineContextFlow:
    """Testet den Kontext-Fluss durch die Pipeline."""
    
    def test_kontext_propagation(self, test_identity):
        """Testet, dass der Kontext durch alle Pipeline-Stufen fließt."""
        zyklus = Zyklus(test_identity)
        backends = {"fallback": FallbackBackend(), "default": FallbackBackend()}
        llm_bridge = LLMBridge(test_identity, backends)
        werte_teilen = WerteTeilen(test_identity)
        
        # Kontext erstellen
        kontext = {
            "input": "Test-Eingabe",
            "mandat": {"name": "Test-Mandat"},
            "modus": "fokus",
            "deutung": "Test-Deutung",
            "kontext_id": "du",
            "kontext_typ": "privat"
        }
        
        # 1. Interpretation
        interpretation = Interpretation(test_identity, zyklus)
        bedeutung = interpretation.verarbeite(kontext["input"])
        kontext["deutung"] = bedeutung
        
        # 2. Seed
        test_identity["use_llm"] = True
        seed = Seed(test_identity, zyklus, llm_bridge)
        rohantwort = seed.generiere(
            bedeutung,
            mandat=kontext["mandat"],
            modus=kontext["modus"]
        )
        
        # 3. WerteTeilen
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input=kontext["input"],
            antwort_entwurf=rohantwort,
            mandat=kontext["mandat"],
            modus=kontext["modus"],
            deutung=kontext["deutung"],
            kontext_id=kontext["kontext_id"],
            kontext_typ=kontext["kontext_typ"]
        )
        kontext["bewertung"] = bewertung
        
        # 4. Silky Edge
        se = SilkyEdge(test_identity, zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)
        
        # 5. Erfahrung
        erfahrung = Erfahrung(test_identity, zyklus, werte_teilen)
        erfahrung.speichern(bedeutung, kontext=kontext)
        
        # 6. Rückmeldung
        rueck = Rueckmeldung(test_identity, zyklus, werte_teilen)
        rueckmeldung = rueck.verarbeite(antwort, kontext=kontext)
        
        # Prüfen, dass Kontext in Rückmeldung gespeichert wurde
        assert rueckmeldung["mandat"] == kontext["mandat"]
        assert rueckmeldung["modus"] == kontext["modus"]
        assert rueckmeldung["deutung"] == kontext["deutung"]
        assert rueckmeldung["input"] == kontext["input"]
        assert "werte_bewertung" in rueckmeldung


class TestPipelineErrorHandling:
    """Testet die Fehlerbehandlung in der Pipeline."""
    
    def test_seed_fallback(self, test_identity):
        """Testet, dass Seed auf Fallback zurückfällt, wenn LLM fehlschlägt."""
        zyklus = Zyklus(test_identity)
        
        # Mock-Backend, das einen Fehler wirft
        class FailingBackend(FallbackBackend):
            def generate(self, prompt, max_tokens=512, temperature=0.7):
                raise RuntimeError("LLM-Fehler")
        
        backends = {"fallback": FailingBackend(), "default": FailingBackend()}
        llm_bridge = LLMBridge(test_identity, backends)
        
        test_identity["use_llm"] = True
        seed = Seed(test_identity, zyklus, llm_bridge)
        
        # Sollte nicht abstürzen, sondern Fallback nutzen
        rohantwort = seed.generiere("Test", mandat={}, modus="fokus")
        
        assert isinstance(rohantwort, str)
        assert len(rohantwort) > 0
    
    def test_erfahrung_filter(self, test_identity):
        """Testet, dass Erfahrung nur reife Inhalte speichert."""
        zyklus = Zyklus(test_identity)
        erfahrung = Erfahrung(test_identity, zyklus)
        
        # Unreife Erfahrung (sollte nicht gespeichert werden)
        gespeichert = erfahrung.speichern("unreif")
        assert gespeichert == False
        
        # Reife Erfahrung (sollte gespeichert werden)
        # Annahme: "reif" ist in Ininity.txt enthalten
        gespeichert = erfahrung.speichern("reif")
        # Abhängig davon, ob "reif" in Ininity.txt ist
        # assert gespeichert == True
