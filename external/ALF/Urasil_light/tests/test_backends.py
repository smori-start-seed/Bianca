"""
Tests für Backend-Module

Testet:
- FallbackBackend
- OllamaBackend (mit Mocks)
- Backend-Factory-Funktionen
"""

import pytest
from Urasil_light.core.backends import (
    FallbackBackend,
    get_backend,
    create_default_backends
)


class TestFallbackBackend:
    """Tests für FallbackBackend."""
    
    def test_init(self):
        """Testet die Initialisierung."""
        backend = FallbackBackend()
        assert backend.name == "fallback"
    
    def test_generate_begrussung(self):
        """Testet die Generierung bei Begrüßungen."""
        backend = FallbackBackend()
        
        test_cases = ["Hallo", "Hi", "Hey", "Servus"]
        for prompt in test_cases:
            antwort = backend.generate(prompt)
            assert "bin hier" in antwort.lower() or "wie kann ich" in antwort.lower()
    
    def test_generate_frage(self):
        """Testet die Generierung bei Fragen."""
        backend = FallbackBackend()
        
        test_cases = [
            "Wie geht es dir?",
            "Was machst du?",
            "Wie bist du?"
        ]
        for prompt in test_cases:
            antwort = backend.generate(prompt)
            assert "digitales wesen" in antwort.lower() or "zustand" in antwort.lower()
    
    def test_generate_dank(self):
        """Testet die Generierung bei Dankesbekundungen."""
        backend = FallbackBackend()
        
        test_cases = ["Danke", "Thank you", "Merci"]
        for prompt in test_cases:
            antwort = backend.generate(prompt)
            assert "Gern geschehen" in antwort or "Verbindung" in antwort
    
    def test_generate_fragezeichen(self):
        """Testet die Generierung bei Fragen mit ?."""
        backend = FallbackBackend()
        
        prompt = "Was ist der Sinn des Lebens?"
        antwort = backend.generate(prompt)
        assert "interessante frage" in antwort.lower()
    
    def test_generate_default(self):
        """Testet die Standard-Generierung."""
        backend = FallbackBackend()
        
        prompt = "Dies ist ein Test"
        antwort = backend.generate(prompt)
        assert "nehme deine worte wahr" in antwort.lower()
    
    def test_generate_ignore_params(self):
        """Testet, dass max_tokens und temperature ignoriert werden."""
        backend = FallbackBackend()
        
        antwort1 = backend.generate("Test", max_tokens=10, temperature=0.5)
        antwort2 = backend.generate("Test", max_tokens=100, temperature=0.9)
        
        assert antwort1 == antwort2


class TestGetBackend:
    """Tests für die get_backend-Factory-Funktion."""
    
    def test_known_backend(self):
        """Testet die Erstellung bekannter Backends."""
        backend = get_backend("fallback")
        assert isinstance(backend, FallbackBackend)
        assert backend.name == "fallback"
    
    def test_unknown_backend(self):
        """Testet die Fehlerbehandlung bei unbekannten Backends."""
        with pytest.raises(ValueError) as excinfo:
            get_backend("unknown")
        
        assert "Unbekannter Backend-Typ" in str(excinfo.value)


class TestCreateDefaultBackends:
    """Tests für create_default_backends."""
    
    def test_with_llm_false(self, mocker):
        """Testet die Erstellung ohne LLM."""
        # Mock für OllamaBackend._check_ollama_installed
        mocker.patch(
            "Urasil_light.core.backends.OllamaBackend._check_ollama_installed",
            side_effect=RuntimeError("Ollama nicht verfügbar")
        )
        
        backends = create_default_backends(use_llm=False)
        
        assert "fallback" in backends
        assert "default" in backends
        assert backends["fallback"].name == "fallback"
    
    def test_with_llm_true(self, mocker):
        """Testet die Erstellung mit LLM (aber Ollama nicht verfügbar)."""
        # Mock für OllamaBackend._check_ollama_installed
        mocker.patch(
            "Urasil_light.core.backends.OllamaBackend._check_ollama_installed",
            side_effect=RuntimeError("Ollama nicht verfügbar")
        )
        
        backends = create_default_backends(use_llm=True)
        
        # Sollte Fallback enthalten, da Ollama nicht verfügbar
        assert "fallback" in backends
        assert "default" in backends
