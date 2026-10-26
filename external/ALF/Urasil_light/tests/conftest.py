"""
Pytest Configuration für Urasil_light

Dieses Modul enthält Fixtures und Konfigurationen für die Tests.
"""

import pytest
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any


# Pfade
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Add project root to Python path for imports
sys.path.insert(0, str(PROJECT_ROOT.parent))


@pytest.fixture
def test_identity() -> Dict[str, Any]:
    """Erstellt eine Test-Identität."""
    return {
        "name": "TEST_URASIL",
        "version": 1,
        "grundton": "neutral",
        "use_llm": False,  # Standardmäßig ohne LLM für Tests
        "zyklus": {"sonne": 0, "mond": 0, "tag": 0},
        "mandate": [],
        "erfahrung": [],
        "reflexion": [],
        "nodus": {},
        "werte": ["Klarheit", "Integrität", "Resonanz", "Tiefe"]
    }


@pytest.fixture
def test_identity_with_llm() -> Dict[str, Any]:
    """Erstellt eine Test-Identität mit LLM-Aktivierung."""
    identity = test_identity()
    identity["use_llm"] = True
    return identity


@pytest.fixture
def test_zyklus(test_identity) -> Any:
    """Erstellt ein Zyklus-Objekt für Tests."""
    from Urasil_light.core.zyklus import Zyklus
    return Zyklus(test_identity)


@pytest.fixture
def test_mandat(test_identity) -> Dict[str, Any]:
    """Erstellt ein Test-Mandat."""
    return {
        "name": "Test-Mandat",
        "beschreibung": "Ein Mandat für Tests"
    }


@pytest.fixture
def mock_ollama_backend(mocker):
    """Mockt das OllamaBackend für Tests."""
    from Urasil_light.core.backends import OllamaBackend
    
    # Mock für subprocess.run
    mock_run = mocker.patch(
        "subprocess.run",
        return_value=mocker.MagicMock(
            stdout=b"Test-Antwort",
            stderr=b"",
            returncode=0
        )
    )
    
    # Mock für _check_ollama_installed
    mocker.patch.object(OllamaBackend, "_check_ollama_installed", return_value=None)
    
    return OllamaBackend("test-model")


@pytest.fixture
def mock_fallback_backend():
    """Erstellt ein FallbackBackend für Tests."""
    from Urasil_light.core.backends import FallbackBackend
    return FallbackBackend()


@pytest.fixture
def test_llm_bridge(test_identity, mock_fallback_backend):
    """Erstellt eine LLMBridge mit Fallback-Backend für Tests."""
    from Urasil_light.core.llm_bridge import LLMBridge
    
    backends = {"fallback": mock_fallback_backend, "default": mock_fallback_backend}
    return LLMBridge(test_identity, backends)


@pytest.fixture
def test_werte_teilen(test_identity):
    """Erstellt ein WerteTeilen-Objekt für Tests."""
    from Urasil_light.core.werte_teilen import WerteTeilen
    return WerteTeilen(test_identity)


@pytest.fixture
def test_seed(test_identity, test_zyklus, test_llm_bridge):
    """Erstellt ein Seed-Objekt für Tests."""
    from Urasil_light.core.seed import Seed
    return Seed(test_identity, test_zyklus, test_llm_bridge)


@pytest.fixture
def test_erfahrung(test_identity, test_zyklus):
    """Erstellt ein Erfahrung-Objekt für Tests."""
    from Urasil_light.core.erfahrung import Erfahrung
    return Erfahrung(test_identity, test_zyklus)


@pytest.fixture
def test_rueckmeldung(test_identity, test_zyklus):
    """Erstellt ein Rueckmeldung-Objekt für Tests."""
    from Urasil_light.core.rueckmeldung import Rueckmeldung
    return Rueckmeldung(test_identity, test_zyklus)


# Autouse-Fixture für Test-Datenverzeichnis
@pytest.fixture(autouse=True, scope="session")
def setup_test_data_dir(tmp_path_factory):
    """Erstellt ein temporäres Datenverzeichnis für Tests."""
    # Erstelle temporäres data-Verzeichnis
    test_data_dir = tmp_path_factory.mktemp("test_data")
    
    # Erstelle Test-Dateien
    gold_path = test_data_dir / "gold.txt"
    gold_path.write_text("Klarheit\nIntegrität\nResonanz\nTiefe\n")
    
    ininity_path = test_data_dir / "Ininity.txt"
    ininity_path.write_text("Reife\nWeisheit\nVerständnis\n")
    
    # Setze Umgebungsvariable für Tests
    os.environ["URASIL_TEST_MODE"] = "1"
    
    yield test_data_dir
    
    # Cleanup
    del os.environ["URASIL_TEST_MODE"]
