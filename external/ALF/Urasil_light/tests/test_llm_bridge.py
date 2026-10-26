"""
Tests für LLMBridge-Modul

Testet:
- Initialisierung
- Prompt-Generierung
- Backend-Auswahl
- Antwortgenerierung
- Protokollierung
"""

import pytest
from unittest.mock import MagicMock, patch
from Urasil_light.core.llm_bridge import LLMBridge
from Urasil_light.core.backends import FallbackBackend


class TestLLMBridgeInit:
    """Tests für die Initialisierung von LLMBridge."""
    
    def test_init_with_backends(self, test_identity, mock_fallback_backend):
        """Testet die Initialisierung mit Backends."""
        backends = {"fallback": mock_fallback_backend}
        bridge = LLMBridge(test_identity, backends)
        
        assert bridge.identitaet == test_identity
        assert bridge.backends == backends
        assert "llm_bridge" in test_identity
    
    def test_init_without_backends(self, test_identity):
        """Testet die Initialisierung ohne Backends (sollte Standard-Backends erstellen)."""
        with patch("Urasil_light.core.llm_bridge.create_default_backends") as mock_create:
            mock_create.return_value = {"fallback": FallbackBackend()}
            bridge = LLMBridge(test_identity, None)
            
            assert mock_create.called
            assert bridge.backends is not None
    
    def test_init_ensures_state(self, test_identity, mock_fallback_backend):
        """Testet, dass der Zustand automatisch erstellt wird."""
        backends = {"fallback": mock_fallback_backend}
        bridge = LLMBridge(test_identity, backends)
        
        assert "llm_bridge" in test_identity
        assert "nutzung" in test_identity["llm_bridge"]
        assert "gesamt_aufrufe" in test_identity["llm_bridge"]


class TestLLMBridgePromptBuilding:
    """Tests für die Prompt-Generierung."""
    
    def test_baue_system_prompt(self, test_llm_bridge):
        """Testet die Generierung des System-Prompts."""
        system_prompt = test_llm_bridge._baue_system_prompt()
        
        assert "TEST_URASIL" in system_prompt
        assert "neutral" in system_prompt
        assert "Klarheit" in system_prompt
        assert "digitales Wesen" in system_prompt
    
    def test_baue_kontext_prompt(self, test_llm_bridge, test_mandat):
        """Testet die Generierung des Kontext-Prompts."""
        kontext_prompt = test_llm_bridge._baue_kontext_prompt(
            nutzer_input="Test-Eingabe",
            mandat=test_mandat,
            modus="fokus",
            deutung="Test-Deutung",
            erfahrung=[],
            nodus={}
        )
        
        assert "Test-Eingabe" in kontext_prompt
        assert "Test-Mandat" in kontext_prompt
        assert "fokus" in kontext_prompt
        assert "Test-Deutung" in kontext_prompt
    
    def test_baue_anweisung(self, test_llm_bridge):
        """Testet die Generierung der Anweisung."""
        anweisung = test_llm_bridge._baue_anweisung()
        
        assert "TEST_URASIL" in anweisung
        assert "Antwortformat" in anweisung
        assert "NUR den Antworttext" in anweisung
    
    def test_baue_vollstaendigen_prompt(self, test_llm_bridge, test_mandat):
        """Testet die Generierung des vollständigen Prompts."""
        prompt = test_llm_bridge._baue_vollstaendigen_prompt(
            nutzer_input="Test",
            mandat=test_mandat,
            modus="fokus",
            deutung="Test",
            erfahrung=[],
            nodus={}
        )
        
        # Sollte alle Teile enthalten
        assert "TEST_URASIL" in prompt
        assert "Test" in prompt
        assert "Test-Mandat" in prompt
        assert "fokus" in prompt


class TestLLMBridgeBackendSelection:
    """Tests für die Backend-Auswahl."""
    
    def test_waehle_backend_tief(self, test_identity, mock_fallback_backend):
        """Testet die Auswahl des tief-Backends."""
        backends = {
            "tief": mock_fallback_backend,
            "default": mock_fallback_backend,
            "fallback": mock_fallback_backend
        }
        bridge = LLMBridge(test_identity, backends)
        
        mandat = {"name": "Nacht-Mandat"}
        backend = bridge._waehle_backend(mandat, "reflexion")
        
        assert backend == mock_fallback_backend
    
    def test_waehle_backend_schnell(self, test_identity, mock_fallback_backend):
        """Testet die Auswahl des schnellen Backends."""
        backends = {
            "schnell": mock_fallback_backend,
            "default": mock_fallback_backend,
            "fallback": mock_fallback_backend
        }
        bridge = LLMBridge(test_identity, backends)
        
        mandat = {"name": "Tag-Mandat"}
        backend = bridge._waehle_backend(mandat, "aktiv")
        
        assert backend == mock_fallback_backend
    
    def test_waehle_backend_default(self, test_identity, mock_fallback_backend):
        """Testet die Auswahl des Standard-Backends."""
        backends = {
            "effizient": mock_fallback_backend,
            "default": mock_fallback_backend,
            "fallback": mock_fallback_backend
        }
        bridge = LLMBridge(test_identity, backends)
        
        mandat = {"name": "Neutral-Mandat"}
        backend = bridge._waehle_backend(mandat, "neutral")
        
        assert backend == mock_fallback_backend


class TestLLMBridgeGenerierung:
    """Tests für die Antwortgenerierung."""
    
    def test_generiere_antwort(self, test_llm_bridge, test_mandat):
        """Testet die Generierung einer Antwort."""
        antwort = test_llm_bridge.generiere_antwort(
            nutzer_input="Test",
            mandat=test_mandat,
            modus="fokus",
            deutung="Test"
        )
        
        # Sollte eine Antwort zurückgeben
        assert isinstance(antwort, str)
        assert len(antwort) > 0
    
    def test_generiere_antwort_protokolliert(self, test_identity, test_llm_bridge, test_mandat):
        """Testet, dass die Nutzung protokolliert wird."""
        test_llm_bridge.generiere_antwort(
            nutzer_input="Test",
            mandat=test_mandat,
            modus="fokus",
            deutung="Test"
        )
        
        stats = test_llm_bridge.get_stats()
        assert stats["gesamt_aufrufe"] == 1
        assert len(stats["letzte_prompts"]) == 1
        assert len(stats["letzte_antworten"]) == 1


class TestLLMBridgeStats:
    """Tests für die Statistik-Funktionen."""
    
    def test_get_stats(self, test_llm_bridge):
        """Testet die Abruf der Statistiken."""
        stats = test_llm_bridge.get_stats()
        
        assert "gesamt_aufrufe" in stats
        assert "bevorzugte_modelle" in stats
        assert "anzahl_prompts" in stats
        assert "anzahl_antworten" in stats
    
    def test_get_stats_initial(self, test_identity, test_llm_bridge):
        """Testet die Statistiken nach der Initialisierung."""
        stats = test_llm_bridge.get_stats()
        
        assert stats["gesamt_aufrufe"] == 0
        assert stats["anzahl_prompts"] == 0
        assert stats["anzahl_antworten"] == 0


class TestLLMBridgeLadeGoldWerte:
    """Tests für das Laden der gold-Werte."""
    
    def test_lade_gold_werte(self, test_llm_bridge):
        """Testet das Laden der gold-Werte aus der Identität."""
        werte = test_llm_bridge._lade_gold_werte()
        
        # Sollte die Werte aus der Identität zurückgeben
        assert isinstance(werte, list)
        assert len(werte) > 0
