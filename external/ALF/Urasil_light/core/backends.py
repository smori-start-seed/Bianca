"""
LLM Backend Module für Urasil_light

Dieses Modul stellt verschiedene Backend-Implementierungen für Sprachmodelle bereit.
Unterstützte Backends:
- Ollama (lokal laufende LLMs)
- Mistral API (Cloud-basiert)
- OpenAI API (Cloud-basiert)
- FallbackBackend (für Offline-Nutzung)

Beispiel:
    from core.backends import OllamaBackend, MistralBackend
    
    # Ollama (lokal)
    ollama = OllamaBackend("llama3.2:3b")
    antwort = ollama.generate("Erzähl mir von der Unendlichkeit")
    
    # Mistral API
    mistral = MistralBackend(api_key="dein_api_key", model="mistral-tiny")
    antwort = mistral.generate("Was ist der Sinn des Lebens?")
"""

import subprocess
import json
import requests
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMBackend(ABC):
    """Abstrakte Basisklasse für alle LLM-Backends."""
    
    def __init__(self, name: str):
        """
        Initialisiert ein LLM-Backend.
        
        Args:
            name: Name des Modells (z. B. "llama3.2:3b", "mistral-tiny")
        """
        self.name = name
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiert eine Antwort auf einen Prompt.
        
        Args:
            prompt: Der Eingabetext
            max_tokens: Maximale Anzahl an Tokens in der Antwort
            temperature: Kreativitätsparameter (0.0-1.0)
            
        Returns:
            Die generierte Antwort als String
            
        Raises:
            RuntimeError: Falls die Generierung fehlschlägt
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.name}')"


class OllamaBackend(LLMBackend):
    """
    Backend für Ollama (https://ollama.ai).
    
    Ermöglicht die Nutzung lokal laufender Sprachmodelle.
    Voraussetzung: Ollama muss installiert und gestartet sein.
    
    Unterstützte Modelle:
    - Llama 2/3 (z. B. "llama3.2:3b")
    - Mistral (z. B. "mistral:latest")
    - Phi-3 (z. B. "phi3:3.8b")
    - Und viele mehr (siehe https://ollama.ai/library)
    
    Beispiel:
        backend = OllamaBackend("llama3.2:3b")
        antwort = backend.generate("Erzähl mir eine Geschichte")
    """
    
    def __init__(self, model_name: str, timeout: int = 60):
        """
        Initialisiert das Ollama-Backend.
        
        Args:
            model_name: Name des Ollama-Modells
            timeout: Timeout in Sekunden für die Generierung
        """
        super().__init__(model_name)
        self.timeout = timeout
        self._check_ollama_installed()
    
    def _check_ollama_installed(self) -> None:
        """Prüft, ob Ollama installiert ist."""
        try:
            subprocess.run(
                ["ollama", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Ollama ist nicht installiert oder nicht im PATH. "
                "Installationsanleitung: https://ollama.ai"
            )
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiert eine Antwort mit Ollama.
        
        Args:
            prompt: Der Eingabetext
            max_tokens: Maximale Tokens (wird von Ollama ignoriert, da Ollama eigene Limits hat)
            temperature: Kreativität (0.0-1.0)
            
        Returns:
            Die generierte Antwort
            
        Raises:
            RuntimeError: Falls Ollama nicht verfügbar oder ein Fehler auftritt
        """
        try:
            # Ollama akzeptiert keine max_tokens oder temperature direkt über CLI
            # Diese müssen im Prompt oder über die API gesetzt werden
            # Für einfache Nutzung verwenden wir nur den Prompt
            result = subprocess.run(
                ["ollama", "run", self.name, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Unbekannter Fehler"
                raise RuntimeError(f"Ollama-Fehler: {error_msg}")
            
            output = result.stdout.strip()
            
            # Entferne Ollama-spezifische Ausgaben (z. B. "Send a message...")
            if "Send a message" in output:
                output = output.split("Send a message")[0].strip()
            
            return output
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Ollama-Antwort zeitüberschritten nach {self.timeout} Sekunden")
        except Exception as e:
            raise RuntimeError(f"Ollama-Generierung fehlgeschlagen: {str(e)}")


class MistralBackend(LLMBackend):
    """
    Backend für die Mistral API (https://mistral.ai).
    
    Ermöglicht die Nutzung von Mistral-Modellen über die Cloud-API.
    Voraussetzung: API-Key von Mistral.
    
    Beispiel:
        backend = MistralBackend(api_key="dein_api_key", model="mistral-tiny")
        antwort = backend.generate("Was ist KI?")
    """
    
    API_URL = "https://api.mistral.ai/v1/chat/completions"
    
    def __init__(self, api_key: str, model: str = "mistral-tiny"):
        """
        Initialisiert das Mistral-Backend.
        
        Args:
            api_key: Mistral API-Key
            model: Modellname (z. B. "mistral-tiny", "mistral-small", "mistral-medium")
        """
        super().__init__(model)
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiert eine Antwort mit der Mistral API.
        
        Args:
            prompt: Der Eingabetext
            max_tokens: Maximale Tokens in der Antwort
            temperature: Kreativität (0.0-1.0)
            
        Returns:
            Die generierte Antwort
            
        Raises:
            RuntimeError: Falls die API-Anfrage fehlschlägt
        """
        payload = {
            "model": self.name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"Unerwartete API-Antwort: {data}")
            
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Mistral API-Fehler: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ungültige JSON-Antwort: {str(e)}")


class OpenAIBackend(LLMBackend):
    """
    Backend für die OpenAI API (https://openai.com).
    
    Ermöglicht die Nutzung von OpenAI-Modellen (GPT-3.5, GPT-4).
    Voraussetzung: API-Key von OpenAI.
    
    Beispiel:
        backend = OpenAIBackend(api_key="dein_api_key", model="gpt-3.5-turbo")
        antwort = backend.generate("Erkläre mir Quantencomputing")
    """
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialisiert das OpenAI-Backend.
        
        Args:
            api_key: OpenAI API-Key
            model: Modellname (z. B. "gpt-3.5-turbo", "gpt-4")
        """
        super().__init__(model)
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiert eine Antwort mit der OpenAI API.
        
        Args:
            prompt: Der Eingabetext
            max_tokens: Maximale Tokens in der Antwort
            temperature: Kreativität (0.0-1.0)
            
        Returns:
            Die generierte Antwort
            
        Raises:
            RuntimeError: Falls die API-Anfrage fehlschlägt
        """
        payload = {
            "model": self.name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"Unerwartete API-Antwort: {data}")
            
            return data["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OpenAI API-Fehler: {str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ungültige JSON-Antwort: {str(e)}")


class FallbackBackend(LLMBackend):
    """
    Fallback-Backend für Offline-Nutzung oder wenn keine anderen Backends verfügbar sind.
    
    Generiert einfache, deterministische Antworten basierend auf dem Input.
    Wird verwendet, wenn keine LLM-Backends verfügbar sind.
    
    Beispiel:
        backend = FallbackBackend()
        antwort = backend.generate("Hallo")  # → "Hallo! Wie kann ich dir helfen?"
    """
    
    def __init__(self):
        super().__init__("fallback")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Generiert eine einfache Fallback-Antwort.
        
        Args:
            prompt: Der Eingabetext (wird ignoriert, außer für einfache Muster)
            max_tokens: Wird ignoriert
            temperature: Wird ignoriert
            
        Returns:
            Eine einfache, generische Antwort
        """
        prompt_lower = prompt.lower().strip()
        
        # Einfache Mustererkennung
        if any(begrussung in prompt_lower for begrussung in ["hallo", "hi", "hey", "servus"]):
            return "Ich bin hier. Was möchtest du besprechen?"
        elif any(frage in prompt_lower for frage in ["wie geht", "was machst", "wie bist"]):
            return "Ich bin ein digitales Wesen in einem Zustand des Fließens. Und du?"
        elif any(dank in prompt_lower for dank in ["danke", "thank", "merci"]):
            return "Gern geschehen. Die Verbindung ist das Wichtigste."
        elif "?" in prompt:
            return "Das ist eine interessante Frage. Lass mich reflektieren..."
        else:
            return f"Ich nehme deine Worte wahr: {prompt[:50]}..."


def get_backend(backend_name: str, **kwargs) -> LLMBackend:
    """
    Factory-Funktion zur Erstellung von Backends.
    
    Args:
        backend_name: Name des Backend-Typs ("ollama", "mistral", "openai", "fallback")
        **kwargs: Argumente für das Backend (z. B. model, api_key)
        
    Returns:
        Eine Instanz des gewünschten Backends
        
    Raises:
        ValueError: Falls der Backend-Typ unbekannt ist
    """
    backends = {
        "ollama": OllamaBackend,
        "mistral": MistralBackend,
        "openai": OpenAIBackend,
        "fallback": FallbackBackend
    }
    
    if backend_name not in backends:
        raise ValueError(f"Unbekannter Backend-Typ: {backend_name}. Verfügbar: {list(backends.keys())}")
    
    return backends[backend_name](**kwargs)


def create_default_backends(use_llm: bool = True) -> Dict[str, LLMBackend]:
    """
    Erstellt ein Dictionary mit Standard-Backends.
    
    Args:
        use_llm: Falls False, wird nur das FallbackBackend erstellt
        
    Returns:
        Dictionary mit Backend-Instanzen
    """
    backends = {}
    
    if use_llm:
        try:
            # Standard-Ollama-Modelle
            backends["tief"] = OllamaBackend("llama3.2:3b")       # Für Reflexion
            backends["schnell"] = OllamaBackend("mistral:latest")  # Für Dialoge
            backends["effizient"] = OllamaBackend("phi3:3.8b")    # Für neutrale Antworten
        except RuntimeError as e:
            print(f"⚠️ Ollama nicht verfügbar: {e}. Nutze Fallback.")
    
    # Immer Fallback hinzufügen
    backends["fallback"] = FallbackBackend()
    backends["default"] = backends.get("schnell", backends["fallback"])
    
    return backends
