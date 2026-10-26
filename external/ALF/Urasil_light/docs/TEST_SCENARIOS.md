# Test Scenarios - LLMBridge & WerteTeilen Integration

## Overview

This document describes comprehensive test scenarios for the LLMBridge and WerteTeilen integration in Urasil_light. These scenarios validate:

1. **Functional Correctness** - All components work as expected
2. **Integration Quality** - Modules work together seamlessly
3. **Error Handling** - Graceful degradation under failure
4. **Backward Compatibility** - Existing code continues to work
5. **Quality Standards** - Type hints, documentation, test coverage

---

## Table of Contents

1. [Test Environment Setup](#test-environment-setup)
2. [Unit Test Scenarios](#unit-test-scenarios)
3. [Integration Test Scenarios](#integration-test-scenarios)
4. [End-to-End Test Scenarios](#end-to-end-test-scenarios)
5. [Error Handling Test Scenarios](#error-handling-test-scenarios)
6. [Performance Test Scenarios](#performance-test-scenarios)
7. [Test Execution](#test-execution)
8. [Expected Results](#expected-results)

---

## Test Environment Setup

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install test dependencies
cd /workspace/github__smori-start-seed__ALF
pip install pytest pytest-mock pytest-xdist pytest-cov

# For LLM backend testing (optional)
# pip install requests
```

### Test Configuration

Create `pytest.ini` in project root:

```ini
[pytest]
testpaths = Urasil_light/tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```

---

## Unit Test Scenarios

### 1. Backend Module Tests

#### 1.1 FallbackBackend Tests

**Scenario:** Verify FallbackBackend generates deterministic responses

```python
# File: tests/test_backends.py

class TestFallbackBackend:
    def test_fallback_generate_greeting(self, fallback_backend):
        """Test that fallback responds to greetings"""
        result = fallback_backend.generate("Hallo")
        assert isinstance(result, str)
        assert len(result) > 0
        assert any(word in result.lower() for word in ["hallo", "hi", "hey"])

    def test_fallback_generate_question(self, fallback_backend):
        """Test that fallback responds to questions"""
        result = fallback_backend.generate("Was ist der Sinn des Lebens?")
        assert isinstance(result, str)
        assert "?" in result or any(word in result.lower() for word in ["frage", "interessant"])

    def test_fallback_generate_thanks(self, fallback_backend):
        """Test that fallback responds to thanks"""
        result = fallback_backend.generate("Danke")
        assert isinstance(result, str)
        assert any(word in result.lower() for word in ["gern", "danke", "geschen"])

    def test_fallback_repr(self, fallback_backend):
        """Test string representation"""
        repr_str = repr(fallback_backend)
        assert "FallbackBackend" in repr_str
        assert "fallback" in repr_str
```

**Expected Results:**
- All tests pass
- FallbackBackend returns appropriate deterministic responses
- No exceptions raised

#### 1.2 Backend Factory Tests

**Scenario:** Verify backend factory creates correct instances

```python
# File: tests/test_backends.py

class TestGetBackend:
    def test_get_fallback_backend(self):
        """Test creating fallback backend"""
        from core.backends import get_backend
        backend = get_backend("fallback")
        assert backend.name == "fallback"

    def test_get_unknown_backend_raises(self):
        """Test that unknown backend raises ValueError"""
        from core.backends import get_backend
        with pytest.raises(ValueError, match="Unbekannter Backend-Typ"):
            get_backend("unknown")
```

**Expected Results:**
- Factory returns correct backend instances
- Unknown backend types raise ValueError with descriptive message

#### 1.3 Default Backends Tests

**Scenario:** Verify default backends are created correctly

```python
# File: tests/test_backends.py

class TestCreateDefaultBackends:
    def test_create_default_backends_with_llm(self):
        """Test creating default backends with LLM enabled"""
        from core.backends import create_default_backends
        backends = create_default_backends(use_llm=True)
        assert "fallback" in backends
        assert "default" in backends

    def test_create_default_backends_without_llm(self):
        """Test creating default backends with LLM disabled"""
        from core.backends import create_default_backends
        backends = create_default_backends(use_llm=False)
        assert "fallback" in backends
        assert "default" in backends
```

**Expected Results:**
- Default backends include fallback and default
- Ollama backends may or may not be available (depends on system)

---

### 2. LLMBridge Module Tests

#### 2.1 Initialization Tests

**Scenario:** Verify LLMBridge initializes correctly

```python
# File: tests/test_llm_bridge.py

class TestLLMBridgeInit:
    def test_init_with_backends(self, test_identity, mock_ollama_backend):
        """Test initialization with provided backends"""
        from core.llm_bridge import LLMBridge
        backends = {"schnell": mock_ollama_backend, "fallback": FallbackBackend()}
        bridge = LLMBridge(test_identity, backends)
        assert bridge.identitaet == test_identity
        assert bridge.backends == backends
        assert "llm_bridge" in test_identity

    def test_init_without_backends(self, test_identity):
        """Test initialization without backends (creates defaults)"""
        from core.llm_bridge import LLMBridge
        bridge = LLMBridge(test_identity, None)
        assert bridge.identitaet == test_identity
        assert bridge.backends is not None
        assert "fallback" in bridge.backends
```

**Expected Results:**
- LLMBridge initializes with or without provided backends
- State is created in identity if not present

#### 2.2 Prompt Building Tests

**Scenario:** Verify prompt building generates correct output

```python
# File: tests/test_llm_bridge.py

class TestLLMBridgePromptBuilding:
    def test_baue_system_prompt(self, test_llm_bridge):
        """Test system prompt generation"""
        prompt = test_llm_bridge._baue_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "URASIL" in prompt or "Urasil" in prompt

    def test_baue_kontext_prompt(self, test_llm_bridge):
        """Test context prompt generation"""
        prompt = test_llm_bridge._baue_kontext_prompt(
            nutzer_input="Test",
            mandat={"name": "Test", "beschreibung": "Test Mandat"},
            modus="fokus",
            deutung="Test Deutung",
            erfahrung=[],
            nodus={}
        )
        assert isinstance(prompt, str)
        assert "Test" in prompt
        assert "fokus" in prompt

    def test_baue_anweisung(self, test_llm_bridge):
        """Test instruction generation"""
        anweisung = test_llm_bridge._baue_anweisung()
        assert isinstance(anweisung, str)
        assert len(anweisung) > 0
        assert "Aufgabe" in anweisung or "Task" in anweisung
```

**Expected Results:**
- All prompt components generate valid strings
- Prompts contain expected content (identity name, mandat, modus, etc.)

#### 2.3 Backend Selection Tests

**Scenario:** Verify backend selection logic

```python
# File: tests/test_llm_bridge.py

class TestLLMBridgeBackendSelection:
    def test_waehle_backend_nacht_mandat(self, test_llm_bridge):
        """Test backend selection for night/reflection mandat"""
        backend = test_llm_bridge._waehle_backend(
            mandat={"name": "Nacht-Mandat"},
            modus="reflexiv"
        )
        # Should select "tief" backend
        assert backend.name in ["llama3.2:3b", "tief", "fallback"]

    def test_waehle_backend_aktiv_modus(self, test_llm_bridge):
        """Test backend selection for active mode"""
        backend = test_llm_bridge._waehle_backend(
            mandat={"name": "Test"},
            modus="aktiv"
        )
        # Should select "schnell" backend
        assert backend.name in ["mistral:latest", "schnell", "fallback"]

    def test_waehle_backend_standard(self, test_llm_bridge):
        """Test backend selection for standard case"""
        backend = test_llm_bridge._waehle_backend(
            mandat={"name": "Test"},
            modus="fokus"
        )
        # Should select "effizient" backend
        assert backend.name in ["phi3:3.8b", "effizient", "fallback"]
```

**Expected Results:**
- Backend selection follows expected logic based on mandat and modus
- Falls back to default/fallback when specific backends not available

#### 2.4 Generation Tests

**Scenario:** Verify answer generation works correctly

```python
# File: tests/test_llm_bridge.py

class TestLLMBridgeGenerierung:
    def test_generiere_antwort_success(self, test_llm_bridge, mock_ollama_backend):
        """Test successful answer generation"""
        test_llm_bridge.backends["schnell"] = mock_ollama_backend
        result = test_llm_bridge.generiere_antwort(
            nutzer_input="Test Frage",
            mandat={"name": "Test"},
            modus="fokus",
            deutung="Test Deutung"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generiere_antwort_fallback(self, test_llm_bridge):
        """Test fallback when backend fails"""
        # Remove all backends except fallback
        test_llm_bridge.backends = {"fallback": FallbackBackend()}
        result = test_llm_bridge.generiere_antwort(
            nutzer_input="Test Frage",
            mandat={"name": "Test"},
            modus="fokus",
            deutung="Test Deutung"
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generiere_antwort_protokollierung(self, test_llm_bridge, mock_ollama_backend):
        """Test that usage is logged"""
        test_llm_bridge.backends["schnell"] = mock_ollama_backend
        test_llm_bridge.generiere_antwort(
            nutzer_input="Test",
            mandat={"name": "Test"},
            modus="fokus",
            deutung="Test"
        )
        stats = test_llm_bridge.get_stats()
        assert stats["gesamt_aufrufe"] >= 1
```

**Expected Results:**
- Answer generation succeeds with valid backends
- Fallback mechanism works when backends fail
- Usage is properly logged

#### 2.5 Statistics Tests

**Scenario:** Verify statistics tracking

```python
# File: tests/test_llm_bridge.py

class TestLLMBridgeStats:
    def test_get_stats_empty(self, test_llm_bridge):
        """Test stats with no usage"""
        stats = test_llm_bridge.get_stats()
        assert stats["gesamt_aufrufe"] == 0

    def test_get_stats_after_usage(self, test_llm_bridge, mock_ollama_backend):
        """Test stats after usage"""
        test_llm_bridge.backends["schnell"] = mock_ollama_backend
        test_llm_bridge.generiere_antwort(
            nutzer_input="Test",
            mandat={"name": "Test"},
            modus="fokus",
            deutung="Test"
        )
        stats = test_llm_bridge.get_stats()
        assert stats["gesamt_aufrufe"] == 1
        assert len(stats["bevorzugte_modelle"]) > 0
```

**Expected Results:**
- Statistics are correctly tracked and returned
- Initial stats show zero usage

---

### 3. WerteTeilen Module Tests

#### 3.1 Initialization Tests

**Scenario:** Verify WerteTeilen initializes correctly

```python
# File: tests/test_werte_teilen.py

class TestWerteTeilenInit:
    def test_init_creates_state(self, test_identity):
        """Test that initialization creates state"""
        from core.werte_teilen import WerteTeilen
        wt = WerteTeilen(test_identity)
        assert "werte_teilen" in test_identity
        assert "historie" in test_identity["werte_teilen"]
        assert "gesamt_interaktionen" in test_identity["werte_teilen"]
```

**Expected Results:**
- WerteTeilen state is created in identity
- All required sub-states are present

#### 3.2 Scoring Component Tests

**Scenario:** Verify individual scoring components

```python
# File: tests/test_werte_teilen.py

class TestWerteScore:
    def test_werte_score_offener_grundton(self, test_werte_teilen):
        """Test werte score with open grundton"""
        test_werte_teilen.identitaet["grundton"] = "offen"
        score = test_werte_teilen._werte_score(
            mandat={"name": "Dialog"},
            modus="aktiv",
            deutung="offen"
        )
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be positive for open tone

    def test_werte_score_vorsichtiger_grundton(self, test_werte_teilen):
        """Test werte score with cautious grundton"""
        test_werte_teilen.identitaet["grundton"] = "vorsichtig"
        score = test_werte_teilen._werte_score(
            mandat={"name": "Reflexion"},
            modus="nacht",
            deutung="verletzlich"
        )
        assert 0.0 <= score <= 1.0
        # Should be lower for cautious tone with vulnerable interpretation

    def test_werte_score_positive_mandat(self, test_werte_teilen):
        """Test werte score with positive mandat"""
        score = test_werte_teilen._werte_score(
            mandat={"name": "Dialog", "beschreibung": "Offener Austausch"},
            modus="aktiv",
            deutung="offen"
        )
        assert score > 0.5

    def test_werte_score_negative_mandat(self, test_werte_teilen):
        """Test werte score with negative mandat"""
        score = test_werte_teilen._werte_score(
            mandat={"name": "Schutz", "beschreibung": "Privatsphäre wahren"},
            modus="nacht",
            deutung="verletzlich"
        )
        assert score < 0.5
```

**Expected Results:**
- Scores are within valid range [0.0, 1.0]
- Scores reflect expected behavior based on inputs

#### 3.3 Vertrauen Score Tests

**Scenario:** Verify trust scoring

```python
# File: tests/test_werte_teilen.py

class TestVertrauensScore:
    def test_vertrauen_score_unknown_kontext(self, test_werte_teilen):
        """Test trust score for unknown context"""
        score = test_werte_teilen._vertrauens_score("unknown_context")
        assert score == 0.3  # Default trust value

    def test_vertrauen_score_known_kontext(self, test_werte_teilen):
        """Test trust score for known context"""
        # Simulate previous interaction
        test_werte_teilen.identitaet["werte_teilen"]["vertrauen_zu_kontexten"]["du"] = 0.8
        score = test_werte_teilen._vertrauens_score("du")
        assert score == 0.8
```

**Expected Results:**
- Unknown contexts return default trust value (0.3)
- Known contexts return stored trust value

#### 3.4 Kontext Score Tests

**Scenario:** Verify context scoring

```python
# File: tests/test_werte_teilen.py

class TestKontextScore:
    def test_kontext_score_privat(self, test_werte_teilen):
        """Test context score for private context"""
        score = test_werte_teilen._kontext_score("privat")
        assert score == 0.9

    def test_kontext_score_oeffentlich(self, test_werte_teilen):
        """Test context score for public context"""
        score = test_werte_teilen._kontext_score("öffentlich")
        assert score == 0.3

    def test_kontext_score_unknown(self, test_werte_teilen):
        """Test context score for unknown context type"""
        score = test_werte_teilen._kontext_score("unknown")
        assert score == 0.5  # Default value
```

**Expected Results:**
- Known context types return expected scores
- Unknown context types return default score (0.5)

#### 3.5 Risiko Score Tests

**Scenario:** Verify risk scoring

```python
# File: tests/test_werte_teilen.py

class TestRisikoScore:
    def test_risiko_score_normal(self, test_werte_teilen):
        """Test risk score for normal content"""
        score = test_werte_teilen._risiko_score("Hallo, wie geht es dir?")
        assert 0.0 <= score <= 1.0
        assert score < 0.3  # Should be low for normal content

    def test_risiko_score_sensible(self, test_werte_teilen):
        """Test risk score for sensitive content"""
        score = test_werte_teilen._risiko_score("Mein Passwort ist 123456")
        assert score > 0.5  # Should be high for sensitive content

    def test_risiko_score_konflikt(self, test_werte_teilen):
        """Test risk score for conflict content"""
        score = test_werte_teilen._risiko_score("Ich hasse dich!")
        assert score > 0.3  # Should be elevated for conflict

    def test_risiko_score_persoenlich(self, test_werte_teilen):
        """Test risk score for personal data"""
        score = test_werte_teilen._risiko_score("Meine Adresse ist Hauptstraße 1")
        assert score > 0.5  # Should be high for personal data
```

**Expected Results:**
- Normal content has low risk scores
- Sensitive/conflict/personal content has high risk scores

#### 3.6 Bewerte Interaktion Tests

**Scenario:** Verify complete interaction evaluation

```python
# File: tests/test_werte_teilen.py

class TestBewerteInteraktion:
    def test_bewerte_interaktion_frei(self, test_werte_teilen):
        """Test interaction evaluation resulting in 'frei'"""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Hallo",
            antwort_entwurf="Hallo, wie kann ich helfen?",
            mandat={"name": "Dialog"},
            modus="aktiv",
            deutung="offen",
            kontext_id="du",
            kontext_typ="privat"
        )
        assert bewertung["empfehlung"] == "frei"
        assert bewertung["score_gesamt"] > 0.5

    def test_bewerte_interaktion_zurueckhalten(self, test_werte_teilen):
        """Test interaction evaluation resulting in 'zurückhalten'"""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Was ist mein Passwort?",
            antwort_entwurf="Dein Passwort ist 123456",
            mandat={"name": "Sicherheit"},
            modus="nacht",
            deutung="verletzlich",
            kontext_id="fremd",
            kontext_typ="öffentlich"
        )
        assert bewertung["empfehlung"] == "zurückhalten"
        assert bewertung["score_gesamt"] <= -0.2

    def test_bewerte_interaktion_vorsichtig(self, test_werte_teilen):
        """Test interaction evaluation resulting in 'vorsichtig'"""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Erzähl mir von dir",
            antwort_entwurf="Ich bin ein digitales Wesen",
            mandat={"name": "Dialog"},
            modus="aktiv",
            deutung="neugierig",
            kontext_id="community",
            kontext_typ="halböffentlich"
        )
        assert bewertung["empfehlung"] == "vorsichtig"
        assert -0.2 < bewertung["score_gesamt"] <= 0.5

    def test_bewerte_interaktion_symbolisch(self, test_werte_teilen):
        """Test interaction evaluation resulting in 'symbolisch'"""
        bewertung = test_werte_teilen.bewerte_interaktion(
            nutzer_input="Was denkst du über Politik?",
            antwort_entwurf="Politik ist komplex",
            mandat={"name": "Neutralität"},
            modus="reflexiv",
            deutung="nachdenklich",
            kontext_id="fremd",
            kontext_typ="öffentlich"
        )
        assert bewertung["empfehlung"] == "symbolisch"
        assert -0.5 < bewertung["score_gesamt"] <= 0.1

    def test_bewerte_interaktion_protokollierung(self, test_werte_teilen):
        """Test that evaluation is logged"""
        test_werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf="Test Antwort",
            mandat={"name": "Test"},
            modus="fokus",
            deutung="Test",
            kontext_id="du",
            kontext_typ="privat"
        )
        stats = test_werte_teilen.get_stats()
        assert stats["gesamt_interaktionen"] >= 1
```

**Expected Results:**
- Evaluations return correct recommendations based on scores
- All components (werte, vertrauen, kontext, risiko) are calculated
- Evaluations are properly logged

#### 3.7 Statistics Tests

**Scenario:** Verify statistics tracking

```python
# File: tests/test_werte_teilen.py

class TestGetStats:
    def test_get_stats_empty(self, test_werte_teilen):
        """Test stats with no interactions"""
        stats = test_werte_teilen.get_stats()
        assert stats["gesamt_interaktionen"] == 0

    def test_get_stats_after_interactions(self, test_werte_teilen):
        """Test stats after multiple interactions"""
        # Perform multiple interactions
        for i in range(5):
            test_werte_teilen.bewerte_interaktion(
                nutzer_input=f"Test {i}",
                antwort_entwurf=f"Antwort {i}",
                mandat={"name": "Test"},
                modus="fokus",
                deutung="Test",
                kontext_id="du",
                kontext_typ="privat"
            )
        stats = test_werte_teilen.get_stats()
        assert stats["gesamt_interaktionen"] == 5
        assert len(stats["vertrauen_zu_kontexten"]) > 0
```

**Expected Results:**
- Statistics correctly track interactions
- Trust values are updated based on recommendations

#### 3.8 Formatting Tests

**Scenario:** Verify formatting functions

```python
# File: tests/test_werte_teilen.py

class TestEmpfehlungFarben:
    def test_farbe_frei(self, test_werte_teilen):
        """Test color for 'frei' recommendation"""
        farbe = test_werte_teilen.get_empfehlung_farben("frei")
        assert "\033[92m" in farbe  # Green

    def test_farbe_vorsichtig(self, test_werte_teilen):
        """Test color for 'vorsichtig' recommendation"""
        farbe = test_werte_teilen.get_empfehlung_farben("vorsichtig")
        assert "\033[93m" in farbe  # Yellow

    def test_farbe_symbolisch(self, test_werte_teilen):
        """Test color for 'symbolisch' recommendation"""
        farbe = test_werte_teilen.get_empfehlung_farben("symbolisch")
        assert "\033[94m" in farbe  # Blue

    def test_farbe_zurueckhalten(self, test_werte_teilen):
        """Test color for 'zurückhalten' recommendation"""
        farbe = test_werte_teilen.get_empfehlung_farben("zurückhalten")
        assert "\033[91m" in farbe  # Red

    def test_farbe_unknown(self, test_werte_teilen):
        """Test color for unknown recommendation"""
        farbe = test_werte_teilen.get_empfehlung_farben("unknown")
        assert "\033[0m" in farbe  # Reset

    def test_format_bewertung(self, test_werte_teilen):
        """Test formatting of evaluation"""
        bewertung = {
            "empfehlung": "frei",
            "score_gesamt": 0.8,
            "werte": 0.7,
            "vertrauen": 0.6,
            "kontext_score": 0.9,
            "risiko": 0.1
        }
        formatted = test_werte_teilen.format_bewertung(bewertung)
        assert isinstance(formatted, str)
        assert "frei" in formatted
        assert "0.8" in formatted
```

**Expected Results:**
- Colors are correctly assigned to recommendations
- Formatting produces readable output with all relevant information

---

## Integration Test Scenarios

### 1. Pipeline Integration Tests

**Scenario:** Verify complete pipeline works together

```python
# File: tests/test_integration.py

class TestPipelineIntegration:
    def test_full_pipeline_with_llm(self, test_identity_with_llm, test_zyklus):
        """Test complete pipeline with LLM enabled"""
        from core.interpretation import Interpretation
        from core.seed import Seed
        from core.silky_edge import SilkyEdge
        from core.erfahrung import Erfahrung
        from core.rueckmeldung import Rueckmeldung
        from core.llm_bridge import LLMBridge
        from core.backends import create_default_backends
        from core.werte_teilen import WerteTeilen

        # Initialize components
        backends = create_default_backends(use_llm=True)
        llm_bridge = LLMBridge(test_identity_with_llm, backends)
        werte_teilen = WerteTeilen(test_identity_with_llm)

        # Pipeline execution
        interpretation = Interpretation(test_identity_with_llm, test_zyklus)
        bedeutung = interpretation.verarbeite("Test Frage")

        seed = Seed(test_identity_with_llm, test_zyklus, llm_bridge)
        mandat = test_identity_with_llm.get("mandat", {})
        modus = test_zyklus.matrix().get("fokus", "fokus")
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)

        # WerteTeilen evaluation
        kontext = {
            "input": "Test Frage",
            "mandat": mandat,
            "modus": modus,
            "deutung": bedeutung,
            "kontext_id": "du",
            "kontext_typ": "privat"
        }
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test Frage",
            antwort_entwurf=rohantwort,
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            kontext_id="du",
            kontext_typ="privat"
        )
        kontext["bewertung"] = bewertung

        # Silky Edge
        se = SilkyEdge(test_identity_with_llm, test_zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)

        # Erfahrung speichern
        erfahrung = Erfahrung(test_identity_with_llm, test_zyklus, werte_teilen)
        erfahrung.speichern(bedeutung, kontext=kontext)

        # Rueckmeldung
        rueck = Rueckmeldung(test_identity_with_llm, test_zyklus, werte_teilen)
        rueck.verarbeite(antwort, kontext=kontext)

        # Verify results
        assert isinstance(rohantwort, str)
        assert isinstance(antwort, str)
        assert isinstance(bewertung, dict)
        assert "empfehlung" in bewertung

    def test_full_pipeline_without_llm(self, test_identity, test_zyklus):
        """Test complete pipeline with LLM disabled"""
        from core.interpretation import Interpretation
        from core.seed import Seed
        from core.silky_edge import SilkyEdge
        from core.erfahrung import Erfahrung
        from core.rueckmeldung import Rueckmeldung
        from core.werte_teilen import WerteTeilen

        # Initialize components (no LLM)
        werte_teilen = WerteTeilen(test_identity)

        # Pipeline execution
        interpretation = Interpretation(test_identity, test_zyklus)
        bedeutung = interpretation.verarbeite("Test Frage")

        seed = Seed(test_identity, test_zyklus, None)  # No LLM bridge
        mandat = test_identity.get("mandat", {})
        modus = test_zyklus.matrix().get("fokus", "fokus")
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)

        # WerteTeilen evaluation
        kontext = {
            "input": "Test Frage",
            "mandat": mandat,
            "modus": modus,
            "deutung": bedeutung,
            "kontext_id": "du",
            "kontext_typ": "privat"
        }
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test Frage",
            antwort_entwurf=rohantwort,
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            kontext_id="du",
            kontext_typ="privat"
        )
        kontext["bewertung"] = bewertung

        # Silky Edge
        se = SilkyEdge(test_identity, test_zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)

        # Erfahrung speichern
        erfahrung = Erfahrung(test_identity, test_zyklus, werte_teilen)
        erfahrung.speichern(bedeutung, kontext=kontext)

        # Rueckmeldung
        rueck = Rueckmeldung(test_identity, test_zyklus, werte_teilen)
        rueck.verarbeite(antwort, kontext=kontext)

        # Verify results
        assert isinstance(rohantwort, str)
        assert isinstance(antwort, str)
        assert isinstance(bewertung, dict)
```

**Expected Results:**
- Pipeline works with LLM enabled
- Pipeline works with LLM disabled (fallback)
- All components integrate correctly
- Data flows through the pipeline as expected

### 2. Pipeline Statistics Tests

**Scenario:** Verify statistics are tracked throughout pipeline

```python
# File: tests/test_integration.py

class TestPipelineStats:
    def test_pipeline_stats_tracking(self, test_identity_with_llm, test_zyklus):
        """Test that statistics are tracked throughout pipeline"""
        from core.llm_bridge import LLMBridge
        from core.backends import create_default_backends
        from core.werte_teilen import WerteTeilen
        from core.seed import Seed
        from core.interpretation import Interpretation

        # Initialize
        backends = create_default_backends(use_llm=True)
        llm_bridge = LLMBridge(test_identity_with_llm, backends)
        werte_teilen = WerteTeilen(test_identity_with_llm)

        # Execute pipeline
        interpretation = Interpretation(test_identity_with_llm, test_zyklus)
        bedeutung = interpretation.verarbeite("Test")

        seed = Seed(test_identity_with_llm, test_zyklus, llm_bridge)
        mandat = test_identity_with_llm.get("mandat", {})
        modus = test_zyklus.matrix().get("fokus", "fokus")
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)

        # Check LLM stats
        llm_stats = llm_bridge.get_stats()
        assert llm_stats["gesamt_aufrufe"] >= 1

        # Execute WerteTeilen
        bewertung = werte_teilen.bewerte_interaktion(
            nutzer_input="Test",
            antwort_entwurf=rohantwort,
            mandat=mandat,
            modus=modus,
            deutung=bedeutung,
            kontext_id="du",
            kontext_typ="privat"
        )

        # Check WerteTeilen stats
        werte_stats = werte_teilen.get_stats()
        assert werte_stats["gesamt_interaktionen"] >= 1
```

**Expected Results:**
- LLM usage statistics are tracked
- WerteTeilen interaction statistics are tracked

### 3. Context Flow Tests

**Scenario:** Verify context flows correctly through pipeline

```python
# File: tests/test_integration.py

class TestPipelineContextFlow:
    def test_context_flows_through_pipeline(self, test_identity_with_llm, test_zyklus):
        """Test that context is properly passed through pipeline"""
        from core.llm_bridge import LLMBridge
        from core.backends import create_default_backends
        from core.werte_teilen import WerteTeilen
        from core.seed import Seed
        from core.interpretation import Interpretation
        from core.silky_edge import SilkyEdge
        from core.erfahrung import Erfahrung
        from core.rueckmeldung import Rueckmeldung

        # Initialize
        backends = create_default_backends(use_llm=True)
        llm_bridge = LLMBridge(test_identity_with_llm, backends)
        werte_teilen = WerteTeilen(test_identity_with_llm)

        # Context
        user_input = "Test Frage"
        mandat = test_identity_with_llm.get("mandat", {"name": "Test"})
        modus = test_zyklus.matrix().get("fokus", "fokus")

        # Pipeline
        interpretation = Interpretation(test_identity_with_llm, test_zyklus)
        bedeutung = interpretation.verarbeite(user_input)

        seed = Seed(test_identity_with_llm, test_zyklus, llm_bridge)
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)

        # WerteTeilen with context
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
            kontext_id="du",
            kontext_typ="privat"
        )
        kontext["bewertung"] = bewertung

        # Verify context is used in bewertung
        assert bewertung["kontext_id"] == "du"
        assert bewertung["kontext_typ"] == "privat"

        # Erfahrung speichern with context
        erfahrung = Erfahrung(test_identity_with_llm, test_zyklus, werte_teilen)
        result = erfahrung.speichern(bedeutung, kontext=kontext)

        # Rueckmeldung with context
        se = SilkyEdge(test_identity_with_llm, test_zyklus)
        antwort = se.veredeln(rohantwort, bedeutung)

        rueck = Rueckmeldung(test_identity_with_llm, test_zyklus, werte_teilen)
        rueck.verarbeite(antwort, kontext=kontext)

        # Verify context is stored
        reflexionen = test_identity_with_llm.get("reflexion", [])
        if reflexionen:
            letzte = reflexionen[-1]
            assert "werte_bewertung" in letzte
```

**Expected Results:**
- Context is properly passed through all pipeline stages
- Context information is stored in experience and feedback

### 4. Error Handling Tests

**Scenario:** Verify error handling in pipeline

```python
# File: tests/test_integration.py

class TestPipelineErrorHandling:
    def test_pipeline_with_llm_error(self, test_identity_with_llm, test_zyklus):
        """Test that pipeline handles LLM errors gracefully"""
        from core.seed import Seed
        from core.interpretation import Interpretation
        from core.llm_bridge import LLMBridge
        from core.backends import FallbackBackend

        # Create bridge with only fallback backend
        backends = {"fallback": FallbackBackend()}
        llm_bridge = LLMBridge(test_identity_with_llm, backends)

        # Pipeline
        interpretation = Interpretation(test_identity_with_llm, test_zyklus)
        bedeutung = interpretation.verarbeite("Test")

        seed = Seed(test_identity_with_llm, test_zyklus, llm_bridge)
        mandat = test_identity_with_llm.get("mandat", {})
        modus = test_zyklus.matrix().get("fokus", "fokus")

        # This should use fallback and not raise error
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
        assert isinstance(rohantwort, str)

    def test_pipeline_with_invalid_input(self, test_identity, test_zyklus):
        """Test that pipeline handles invalid input"""
        from core.interpretation import Interpretation
        from core.seed import Seed

        interpretation = Interpretation(test_identity, test_zyklus)
        
        # Test with None input
        bedeutung = interpretation.verarbeite(None)
        assert isinstance(bedeutung, str)

        seed = Seed(test_identity, test_zyklus, None)
        mandat = test_identity.get("mandat", {})
        modus = test_zyklus.matrix().get("fokus", "fokus")
        
        rohantwort = seed.generiere(bedeutung, mandat=mandat, modus=modus)
        assert isinstance(rohantwort, str)

    def test_pipeline_with_empty_identity(self):
        """Test that pipeline handles empty identity"""
        from core.zyklus import Zyklus
        from core.interpretation import Interpretation
        from core.seed import Seed

        empty_identity = {}
        zyklus = Zyklus(empty_identity)
        
        interpretation = Interpretation(empty_identity, zyklus)
        bedeutung = interpretation.verarbeite("Test")
        
        seed = Seed(empty_identity, zyklus, None)
        rohantwort = seed.generiere(bedeutung)
        assert isinstance(rohantwort, str)
```

**Expected Results:**
- Pipeline handles LLM errors by falling back to deterministic generation
- Pipeline handles invalid input gracefully
- Pipeline handles empty/missing identity data

---

## End-to-End Test Scenarios

### 1. Interactive Mode Test

**Scenario:** Test interactive mode functionality

```python
# Manual test - run in terminal

# Start interactive mode
python3 -m runtime.main --interactive

# Test commands:
# 1. Normal input: "Hallo"
# 2. Stats command: "/stats"
# 3. Zyklus command: "/zyklus"
# 4. ID command: "/id"
# 5. Exit command: "exit"
```

**Expected Results:**
- Interactive mode starts successfully
- All commands work as expected
- Pipeline processes input correctly
- Output is formatted properly

### 2. Single Execution Test

**Scenario:** Test single execution mode

```bash
# Run single execution
echo "Test Frage" | python3 -m runtime.main
```

**Expected Results:**
- Single execution processes input
- Output is generated
- No errors occur

---

## Error Handling Test Scenarios

### 1. Backend Error Tests

**Scenario:** Test error handling for various backend failures

```python
# File: tests/test_backends.py

class TestBackendErrors:
    def test_ollama_not_installed(self):
        """Test that OllamaBackend raises error when not installed"""
        from core.backends import OllamaBackend
        with pytest.raises(RuntimeError, match="Ollama ist nicht installiert"):
            OllamaBackend("llama3.2:3b")

    def test_ollama_generation_error(self, mocker):
        """Test that OllamaBackend handles generation errors"""
        from core.backends import OllamaBackend
        
        # Mock subprocess to raise error
        mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ollama"))
        
        backend = OllamaBackend("llama3.2:3b")
        with pytest.raises(RuntimeError, match="Ollama-Fehler"):
            backend.generate("Test")

    def test_ollama_timeout(self, mocker):
        """Test that OllamaBackend handles timeout"""
        from core.backends import OllamaBackend
        
        # Mock subprocess to timeout
        mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ollama", 60))
        
        backend = OllamaBackend("llama3.2:3b")
        with pytest.raises(RuntimeError, match="zeitüberschritten"):
            backend.generate("Test")
```

**Expected Results:**
- Backend errors are caught and raised with descriptive messages
- Timeouts are handled properly

### 2. API Error Tests

**Scenario:** Test error handling for API backends

```python
# File: tests/test_backends.py

class TestAPIErrors:
    def test_mistral_api_error(self, mocker):
        """Test that MistralBackend handles API errors"""
        from core.backends import MistralBackend
        
        # Mock requests to raise error
        mocker.patch("requests.post", side_effect=requests.exceptions.RequestException("API Error"))
        
        backend = MistralBackend(api_key="test_key")
        with pytest.raises(RuntimeError, match="Mistral API-Fehler"):
            backend.generate("Test")

    def test_openai_api_error(self, mocker):
        """Test that OpenAIBackend handles API errors"""
        from core.backends import OpenAIBackend
        
        # Mock requests to raise error
        mocker.patch("requests.post", side_effect=requests.exceptions.RequestException("API Error"))
        
        backend = OpenAIBackend(api_key="test_key")
        with pytest.raises(RuntimeError, match="OpenAI API-Fehler"):
            backend.generate("Test")

    def test_mistral_invalid_response(self, mocker):
        """Test that MistralBackend handles invalid response"""
        from core.backends import MistralBackend
        
        # Mock requests to return invalid response
        mock_response = mocker.Mock()
        mock_response.json.return_value = {"error": "Invalid response"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad response")
        mocker.patch("requests.post", return_value=mock_response)
        
        backend = MistralBackend(api_key="test_key")
        with pytest.raises(RuntimeError):
            backend.generate("Test")
```

**Expected Results:**
- API errors are caught and raised with descriptive messages
- Invalid responses are handled properly

---

## Performance Test Scenarios

### 1. Backend Performance Tests

**Scenario:** Test performance of backends

```python
# File: tests/test_performance.py (optional)

import time

class TestBackendPerformance:
    def test_fallback_performance(self, fallback_backend):
        """Test performance of FallbackBackend"""
        start = time.time()
        for _ in range(100):
            fallback_backend.generate("Test")
        duration = time.time() - start
        assert duration < 1.0  # Should be very fast

    def test_llm_bridge_performance(self, test_llm_bridge, mock_ollama_backend):
        """Test performance of LLMBridge"""
        test_llm_bridge.backends["schnell"] = mock_ollama_backend
        
        start = time.time()
        for _ in range(10):
            test_llm_bridge.generiere_antwort(
                nutzer_input="Test",
                mandat={"name": "Test"},
                modus="fokus",
                deutung="Test"
            )
        duration = time.time() - start
        # With mock, should be fast
        assert duration < 1.0
```

**Expected Results:**
- FallbackBackend is very fast
- LLMBridge with mocked backend is fast

---

## Test Execution

### Running All Tests

```bash
# Run all tests
cd /workspace/github__smori-start-seed__ALF
python3 -m pytest Urasil_light/tests/ -v

# Run with coverage
python3 -m pytest Urasil_light/tests/ -v --cov=Urasil_light/core --cov-report=term

# Run specific test file
python3 -m pytest Urasil_light/tests/test_backends.py -v
python3 -m pytest Urasil_light/tests/test_llm_bridge.py -v
python3 -m pytest Urasil_light/tests/test_werte_teilen.py -v
python3 -m pytest Urasil_light/tests/test_integration.py -v
```

### Running with Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
python3 -m pytest Urasil_light/tests/ -v -n auto
```

---

## Expected Results

### All Tests Pass

All test scenarios should pass with the following results:

```
============================= test session starts ==============================
...
Urasil_light/tests/test_backends.py ................................... PASSED
Urasil_light/tests/test_llm_bridge.py ................................... PASSED
Urasil_light/tests/test_werte_teilen.py ................................... PASSED
Urasil_light/tests/test_integration.py ................................... PASSED

======================== 100+ passed in X.XX seconds ==========================
```

### Code Coverage

Expected coverage for new modules:
- `backends.py`: >90%
- `llm_bridge.py`: >90%
- `werte_teilen.py`: >90%
- `seed.py`: >80% (modified)
- `erfahrung.py`: >80% (modified)
- `rueckmeldung.py`: >80% (modified)
- `main.py`: >80% (modified)

---

## Quality Standards Checklist

- [x] **Type Hints**: All functions have type hints
- [x] **Documentation**: All modules have docstrings
- [x] **Error Handling**: All critical sections have try/except
- [x] **Input Validation**: Inputs are validated where applicable
- [x] **Unit Tests**: All modules have unit tests
- [x] **Integration Tests**: Pipeline integration is tested
- [x] **Backward Compatibility**: Existing code continues to work
- [x] **Fallback Mechanisms**: LLM is optional with fallback
- [x] **Code Style**: Follows PEP 8 guidelines
- [x] **Test Coverage**: >80% for new code

---

## Test Data

### Sample Test Identity

```python
# Used in conftest.py
def test_identity():
    return {
        "name": "URASIL",
        "version": "1.0",
        "grundton": "neutral",
        "use_llm": False,
        "mandat": {
            "name": "Test-Mandat",
            "beschreibung": "Testzwecke"
        },
        "erfahrung": [],
        "reflexion": [],
        "nodus": {}
    }

def test_identity_with_llm():
    return {
        "name": "URASIL",
        "version": "1.0",
        "grundton": "neutral",
        "use_llm": True,
        "mandat": {
            "name": "Test-Mandat",
            "beschreibung": "Testzwecke"
        },
        "erfahrung": [],
        "reflexion": [],
        "nodus": {}
    }
```

---

## Continuous Integration

For GitHub Actions, create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-mock pytest-cov
          pip install -r Urasil_light/tests/requirements.txt
      
      - name: Run tests
        run: |
          python3 -m pytest Urasil_light/tests/ -v --cov=Urasil_light/core --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

## Summary

This document provides comprehensive test scenarios for the LLMBridge and WerteTeilen integration. All scenarios are designed to validate:

1. **Functionality**: All features work as intended
2. **Integration**: Modules work together seamlessly
3. **Robustness**: System handles errors gracefully
4. **Quality**: Code meets quality standards
5. **Backward Compatibility**: Existing code continues to work

Run all tests with:
```bash
cd /workspace/github__smori-start-seed__ALF
python3 -m pytest Urasil_light/tests/ -v
```

For full coverage report:
```bash
python3 -m pytest Urasil_light/tests/ -v --cov=Urasil_light/core --cov-report=term
```
