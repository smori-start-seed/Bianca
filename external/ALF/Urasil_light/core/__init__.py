"""
ALF Core Module

This package contains the core components of the ALF (Artificial Life Framework) system.

Security Note:
This module includes a whitelist system to prevent unauthorized code execution.
All modules are verified against the whitelist before loading.

For more information, see:
- docs/WHITELIST.md
- docs/SCREENSAVER.md
- README.md
"""

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class WhitelistSecurityError(Exception):
    """Raised when a module fails whitelist verification."""
    pass


class WhitelistManager:
    """
    Manages whitelist verification for ALF core modules.
    
    This is a lightweight wrapper that integrates with the full WhitelistManager
    from core.whitelist.whitelist for security checks during module loading.
    """
    
    def __init__(self, whitelist_dir: Optional[Path] = None):
        """
        Initialize the whitelist manager.
        
        Args:
            whitelist_dir: Path to whitelist directory. Defaults to data/whitelist
        """
        self.whitelist_dir = whitelist_dir or Path(__file__).parent.parent.parent / "data" / "whitelist"
        self._whitelist_cache: Optional[Dict[str, Any]] = None
        self._enabled = True
        
        # Check if whitelist exists
        if not self._get_current_whitelist():
            # In dev mode, disable whitelist if no file exists
            self._enabled = False
    
    def _get_current_whitelist(self) -> Optional[Dict[str, Any]]:
        """Load the current whitelist from disk."""
        if self._whitelist_cache is not None:
            return self._whitelist_cache
        
        # Get current version
        version_file = self.whitelist_dir / "current_version.txt"
        if not version_file.exists():
            return None
        
        try:
            with open(version_file, "r") as f:
                version = f.read().strip()
        except IOError:
            return None
        
        # Load whitelist file
        whitelist_file = self.whitelist_dir / f"whitelist_{version}.json"
        if not whitelist_file.exists():
            return None
        
        try:
            with open(whitelist_file, "r", encoding="utf-8") as f:
                self._whitelist_cache = json.load(f)
            return self._whitelist_cache
        except (IOError, json.JSONDecodeError):
            return None
    
    def is_enabled(self) -> bool:
        """Check if whitelist security is enabled."""
        return self._enabled
    
    def verify_module(self, module_path: str) -> bool:
        """
        Verify that a module is in the whitelist.
        
        Args:
            module_path: Relative path to the module (e.g., 'core.identity')
            
        Returns:
            True if module is allowed, False otherwise
        """
        if not self._enabled:
            return True  # Dev mode: allow all
        
        whitelist = self._get_current_whitelist()
        if whitelist is None:
            return True
        
        # Normalize path
        normalized_path = module_path.replace(".", "/").replace("\\", "/")
        if normalized_path.endswith(".py"):
            normalized_path = normalized_path[:-3]
        
        # Check all entries
        for entry in whitelist.get("entries", []):
            entry_path = entry.get("file_path", "").replace("\\", "/")
            if entry_path.endswith(".py"):
                entry_path = entry_path[:-3]
            
            if normalized_path == entry_path:
                # Verify hash if available
                if "sha256_hash" in entry:
                    file_path = Path(__file__).parent / module_path.replace(".", "/")
                    if file_path.exists():
                        with open(file_path, "rb") as f:
                            content = f.read()
                        actual_hash = hashlib.sha256(content).hexdigest()
                        if actual_hash != entry["sha256_hash"]:
                            return False
                return True
        
        return False
    
    def verify_file(self, file_path: str) -> bool:
        """
        Verify that a file is in the whitelist.
        
        Args:
            file_path: Path to the file (relative to core directory)
            
        Returns:
            True if file is allowed, False otherwise
        """
        if not self._enabled:
            return True
        
        whitelist = self._get_current_whitelist()
        if whitelist is None:
            return True
        
        normalized_path = file_path.replace("\\", "/")
        if normalized_path.endswith(".py"):
            normalized_path = normalized_path[:-3]
        
        for entry in whitelist.get("entries", []):
            entry_path = entry.get("file_path", "").replace("\\", "/")
            if entry_path.endswith(".py"):
                entry_path = entry_path[:-3]
            
            if normalized_path == entry_path:
                return True
        
        return False


# Global whitelist manager instance
_whitelist_manager = WhitelistManager()


def get_whitelist_manager() -> WhitelistManager:
    """Get the global whitelist manager instance."""
    return _whitelist_manager


def verify_module(module_path: str) -> bool:
    """
    Verify a module against the whitelist.
    
    Args:
        module_path: Module path (e.g., 'core.identity')
        
    Returns:
        True if allowed, False otherwise
    """
    return _whitelist_manager.verify_module(module_path)


def verify_file(file_path: str) -> bool:
    """
    Verify a file against the whitelist.
    
    Args:
        file_path: File path (relative to core directory)
        
    Returns:
        True if allowed, False otherwise
    """
    return _whitelist_manager.verify_file(file_path)


# Security check for module loading
def _check_module_security(module_name: str) -> bool:
    """
    Internal function to check if a module can be loaded.
    
    Args:
        module_name: Full module name (e.g., 'Urasil_light.core.identity')
        
    Returns:
        True if module is allowed
    """
    # Skip check for built-in modules
    if module_name.startswith("Urasil_light.core"):
        # Extract relative path
        rel_path = module_name.replace("Urasil_light.core.", "")
        return verify_module(rel_path)
    
    # Allow all other modules (they're not part of core)
    return True


# Monkey-patch importlib to add whitelist checks
original_import_module = importlib.import_module

def secure_import_module(name: str, package: Optional[str] = None) -> Any:
    """
    Secure version of import_module that checks whitelist.
    
    Args:
        name: Module name
        package: Package name
        
    Returns:
        Imported module
        
    Raises:
        WhitelistSecurityError: If module is not in whitelist
    """
    # Skip check for standard library and non-ALF modules
    if not name.startswith("Urasil_light"):
        return original_import_module(name, package)
    
    # Check whitelist
    if not _check_module_security(name):
        raise WhitelistSecurityError(
            f"Module '{name}' is not in the whitelist and cannot be loaded. "
            f"To add it, create a proposal through the voting system."
        )
    
    return original_import_module(name, package)


# Only enable security checks if whitelist is enabled
if _whitelist_manager.is_enabled():
    importlib.import_module = secure_import_module


# Re-export all core modules for backward compatibility
from .identity import Identity
from .zyklus import Zyklus
from .mandate import Mandate
from .interpretation import Interpretation
from .seed import Seed
from .erfahrung import Erfahrung
from .rueckmeldung import Rueckmeldung
from .silky_edge import SilkyEdge
from .frequency import Frequency
from .trend import Trend
from .simulation import Simulation
from .profile import Profile
from .session_manager import SessionManager
from .alf_bridge import ALFBridge
from .alf_bridge2 import ALFBridge2
from .ininity import Ininity

# New modules
from .llm_bridge import LLMBridge
from .backends import (
    LLMBackend,
    FallbackBackend,
    OllamaBackend,
    MistralBackend,
    OpenAIBackend,
    create_default_backends
)
from .werte_teilen import WerteTeilen

# Screensaver module
from .screensaver import ALFScreensaver
from .screensaver.screensaver import (
    ScreensaverMode,
    ResourceLimits,
    ScreensaverConfig,
    IdleDetector,
    ResourceManager,
    ALFVisualizer
)

# Whitelist module
from .whitelist.whitelist import (
    WhitelistManager as FullWhitelistManager,
    WhitelistFile,
    WhitelistEntry,
    WhitelistChangeType
)
from .whitelist.voting import (
    VotingSystem,
    VotingConfig,
    Proposal,
    ProposalStatus,
    Vote,
    VoteType,
    VoterInfo,
    PhysicalConfirmationType,
    calculate_quorum,
    generate_proposal_signature
)


__all__ = [
    # Original modules
    "Identity",
    "Zyklus",
    "Mandate",
    "Interpretation",
    "Seed",
    "Erfahrung",
    "Rueckmeldung",
    "SilkyEdge",
    "Frequency",
    "Trend",
    "Simulation",
    "Profile",
    "SessionManager",
    "ALFBridge",
    "ALFBridge2",
    "Ininity",
    # New LLM modules
    "LLMBridge",
    "LLMBackend",
    "FallbackBackend",
    "OllamaBackend",
    "MistralBackend",
    "OpenAIBackend",
    "create_default_backends",
    "WerteTeilen",
    # Screensaver modules
    "ALFScreensaver",
    "ScreensaverMode",
    "ResourceLimits",
    "ScreensaverConfig",
    "IdleDetector",
    "ResourceManager",
    "ALFVisualizer",
    # Whitelist modules
    "FullWhitelistManager",
    "WhitelistFile",
    "WhitelistEntry",
    "WhitelistChangeType",
    "VotingSystem",
    "VotingConfig",
    "Proposal",
    "ProposalStatus",
    "Vote",
    "VoteType",
    "VoterInfo",
    "PhysicalConfirmationType",
    "calculate_quorum",
    "generate_proposal_signature",
    # Security
    "WhitelistSecurityError",
    "get_whitelist_manager",
    "verify_module",
    "verify_file",
]
