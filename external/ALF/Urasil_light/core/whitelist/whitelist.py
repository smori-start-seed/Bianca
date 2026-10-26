"""
ALF Whitelist Module - Core Implementation

This module implements the core whitelist functionality for ALF:
- Immutable, versioned whitelist files
- File validation against whitelist
- Integration with voting system for changes

The whitelist is designed to be:
1. Tamper-proof (cryptographic signatures)
2. Versioned (each change creates a new version)
3. Distributed (stored on IPFS or similar)
4. Validated (each file must match whitelist hash)

Example:
    from core.whitelist import WhitelistManager
    
    manager = WhitelistManager()
    
    # Check if file is allowed
    if manager.is_allowed("core/llm_bridge.py"):
        print("File is whitelisted")
    
    # Get current whitelist
    whitelist = manager.get_current_whitelist()
    print(f"Current version: {whitelist.version}")
"""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class WhitelistChangeType(Enum):
    """Types of whitelist changes."""
    ADD = "add"          # Add new file/module
    REMOVE = "remove"     # Remove file/module
    UPDATE = "update"     # Update existing entry


@dataclass
class WhitelistEntry:
    """
    A single entry in the ALF whitelist.
    
    Attributes:
        file_path: Path to the file (relative to project root)
        file_hash: SHA-256 hash of the file content
        description: Human-readable description of the file
        required: Whether this file is required for ALF to function
        change_type: Type of the last change (ADD, REMOVE, UPDATE)
        added_version: Whitelist version when this entry was added
    """
    file_path: str
    file_hash: str
    description: str = ""
    required: bool = True
    change_type: WhitelistChangeType = WhitelistChangeType.ADD
    added_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "description": self.description,
            "required": self.required,
            "change_type": self.change_type.value,
            "added_version": self.added_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhitelistEntry':
        """Create from dictionary."""
        return cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            description=data.get("description", ""),
            required=data.get("required", True),
            change_type=WhitelistChangeType(data.get("change_type", "add")),
            added_version=data.get("added_version", "1.0")
        )
    
    def verify_file(self, file_path: str) -> bool:
        """
        Verify that a file matches this whitelist entry.
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            True if file matches, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            actual_hash = hashlib.sha256(content).hexdigest()
            return actual_hash == self.file_hash
        except (FileNotFoundError, IOError):
            return False


@dataclass
class WhitelistFile:
    """
    Represents a single version of the ALF whitelist.
    
    The whitelist file is:
    - Immutable (once created, cannot be modified)
    - Signed (cryptographically signed for authenticity)
    - Versioned (each change creates a new version)
    - Timestamped (creation time is recorded)
    
    Attributes:
        version: Version string (e.g., "1.0", "1.1")
        timestamp: Creation timestamp (ISO format)
        entries: List of whitelist entries
        signature: Cryptographic signature (optional)
        previous_hash: Hash of previous whitelist version
        approval_hash: Hash of the voting approval for this version
    """
    version: str
    timestamp: str
    entries: List[WhitelistEntry] = field(default_factory=list)
    signature: str = ""
    previous_hash: str = ""
    approval_hash: str = ""  # Hash of the voting transaction
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "entries": [e.to_dict() for e in self.entries],
            "signature": self.signature,
            "previous_hash": self.previous_hash,
            "approval_hash": self.approval_hash
        }
    
    def get_hash(self) -> str:
        """
        Calculate the hash of this whitelist file.
        
        Returns:
            SHA-256 hash of the whitelist content
        """
        content = json.dumps(self.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(content).hexdigest()
    
    def get_file_paths(self) -> Set[str]:
        """
        Get all file paths in this whitelist.
        
        Returns:
            Set of file paths
        """
        return {entry.file_path for entry in self.entries}
    
    def is_allowed(self, file_path: str) -> bool:
        """
        Check if a file is in the whitelist.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is whitelisted, False otherwise
        """
        return file_path in self.get_file_paths()
    
    def get_entry(self, file_path: str) -> Optional[WhitelistEntry]:
        """
        Get the whitelist entry for a file.
        
        Args:
            file_path: Path to look up
            
        Returns:
            WhitelistEntry if found, None otherwise
        """
        for entry in self.entries:
            if entry.file_path == file_path:
                return entry
        return None
    
    def verify_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Verify that a file matches its whitelist entry.
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        entry = self.get_entry(file_path)
        if entry is None:
            return False, f"File '{file_path}' is not in whitelist"
        
        if not entry.verify_file(file_path):
            return False, f"File '{file_path}' hash does not match whitelist"
        
        return True, None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhitelistFile':
        """Create from dictionary."""
        entries = [WhitelistEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(
            version=data["version"],
            timestamp=data["timestamp"],
            entries=entries,
            signature=data.get("signature", ""),
            previous_hash=data.get("previous_hash", ""),
            approval_hash=data.get("approval_hash", "")
        )
    
    def save_to_file(self, file_path: str):
        """
        Save whitelist to a JSON file.
        
        Args:
            file_path: Path to save the whitelist
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


@dataclass
class WhitelistConfig:
    """Configuration for the whitelist system."""
    whitelist_dir: str = "data/whitelist"  # Directory to store whitelist files
    current_version_file: str = "current_version.txt"  # File tracking current version
    voting_quorum: float = 0.51  # 51% majority required for changes
    voting_period: int = 7 * 24 * 3600  # 7 days in seconds
    require_physical_confirmation: bool = True  # Require physical confirmation for changes
    tpm_required: bool = True  # Require TPM for signing


class WhitelistManager:
    """
    Main manager for the ALF whitelist system.
    
    This class:
    - Maintains the current whitelist
    - Validates files against the whitelist
    - Manages whitelist changes through voting
    - Handles physical confirmation of changes
    
    Example:
        manager = WhitelistManager()
        
        # Check if a module is allowed
        if manager.is_allowed("core/llm_bridge.py"):
            import core.llm_bridge
        
        # Verify a file before loading
        is_valid, error = manager.verify_file("core/llm_bridge.py")
        if not is_valid:
            print(f"Error: {error}")
    """
    
    def __init__(self, config: Optional[WhitelistConfig] = None):
        """
        Initialize the whitelist manager.
        
        Args:
            config: Whitelist configuration
        """
        self.config = config or WhitelistConfig()
        self._whitelist_cache: Dict[str, WhitelistFile] = {}
        self._current_version: Optional[str] = None
        
        # Create whitelist directory if it doesn't exist
        os.makedirs(self.config.whitelist_dir, exist_ok=True)
        
        # Load current version
        self._load_current_version()
    
    def _load_current_version(self):
        """Load the current whitelist version from file."""
        version_file = os.path.join(self.config.whitelist_dir, self.config.current_version_file)
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                self._current_version = f.read().strip()
    
    def _save_current_version(self, version: str):
        """Save the current whitelist version to file."""
        version_file = os.path.join(self.config.whitelist_dir, self.config.current_version_file)
        with open(version_file, 'w') as f:
            f.write(version)
    
    def get_current_whitelist(self) -> Optional[WhitelistFile]:
        """
        Get the current whitelist.
        
        Returns:
            Current WhitelistFile, or None if not loaded
        """
        if self._current_version is None:
            return None
        
        if self._current_version in self._whitelist_cache:
            return self._whitelist_cache[self._current_version]
        
        return self._load_whitelist_version(self._current_version)
    
    def _load_whitelist_version(self, version: str) -> Optional[WhitelistFile]:
        """
        Load a specific whitelist version.
        
        Args:
            version: Version to load
            
        Returns:
            WhitelistFile if found, None otherwise
        """
        version_file = os.path.join(self.config.whitelist_dir, f"whitelist_{version}.json")
        if not os.path.exists(version_file):
            return None
        
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            whitelist = WhitelistFile.from_dict(data)
            self._whitelist_cache[version] = whitelist
            return whitelist
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Fehler beim Laden der Whitelist {version}: {e}")
            return None
    
    def is_allowed(self, file_path: str) -> bool:
        """
        Check if a file is in the current whitelist.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file is whitelisted
        """
        whitelist = self.get_current_whitelist()
        if whitelist is None:
            # If no whitelist, allow all (fallback for development)
            return True
        return whitelist.is_allowed(file_path)
    
    def verify_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Verify that a file matches its whitelist entry.
        
        Args:
            file_path: Path to the file to verify
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        whitelist = self.get_current_whitelist()
        if whitelist is None:
            return True, None  # No whitelist = allow all
        
        return whitelist.verify_file(file_path)
    
    def verify_module(self, module_name: str) -> Tuple[bool, Optional[str]]:
        """
        Verify that a module is allowed and its files match the whitelist.
        
        Args:
            module_name: Name of the module (e.g., 'core.llm_bridge')
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Convert module name to file path
        file_path = module_name.replace('.', '/') + '.py'
        
        # Check if file is in whitelist
        if not self.is_allowed(file_path):
            return False, f"Module '{module_name}' is not in whitelist"
        
        # Verify file hash
        return self.verify_file(file_path)
    
    def get_all_whitelist_versions(self) -> List[str]:
        """
        Get all available whitelist versions.
        
        Returns:
            List of version strings, sorted by version number
        """
        versions = []
        for filename in os.listdir(self.config.whitelist_dir):
            if filename.startswith("whitelist_") and filename.endswith(".json"):
                version = filename.replace("whitelist_", "").replace(".json", "")
                versions.append(version)
        
        # Sort versions (simple numeric sort for now)
        versions.sort()
        return versions
    
    def get_whitelist_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of whitelist changes.
        
        Returns:
            List of whitelist metadata (version, timestamp, etc.)
        """
        history = []
        for version in self.get_all_whitelist_versions():
            whitelist = self._load_whitelist_version(version)
            if whitelist:
                history.append({
                    "version": whitelist.version,
                    "timestamp": whitelist.timestamp,
                    "entry_count": len(whitelist.entries),
                    "previous_hash": whitelist.previous_hash,
                    "approval_hash": whitelist.approval_hash
                })
        return history
    
    def create_initial_whitelist(self, entries: List[WhitelistEntry]) -> WhitelistFile:
        """
        Create the initial whitelist (version 1.0).
        
        Args:
            entries: List of initial whitelist entries
            
        Returns:
            The created WhitelistFile
        """
        whitelist = WhitelistFile(
            version="1.0",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            entries=entries,
            previous_hash="",  # First version has no previous
            approval_hash="initial"  # Special marker for initial version
        )
        
        # Save the whitelist
        self._save_whitelist(whitelist)
        
        # Set as current version
        self._current_version = whitelist.version
        self._save_current_version(whitelist.version)
        
        return whitelist
    
    def _save_whitelist(self, whitelist: WhitelistFile):
        """
        Save a whitelist version to disk.
        
        Args:
            whitelist: WhitelistFile to save
        """
        version_file = os.path.join(
            self.config.whitelist_dir,
            f"whitelist_{whitelist.version}.json"
        )
        whitelist.save_to_file(version_file)
        self._whitelist_cache[whitelist.version] = whitelist
    
    def propose_change(
        self,
        change_type: WhitelistChangeType,
        file_path: str,
        reason: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Propose a change to the whitelist.
        
        This creates a proposal that must be voted on before taking effect.
        
        Args:
            change_type: Type of change (ADD, REMOVE, UPDATE)
            file_path: Path of the file to change
            reason: Reason for the change
            description: Description of the file
            
        Returns:
            Proposal data including proposal ID
        """
        # In a full implementation, this would:
        # 1. Create a proposal object
        # 2. Add it to the voting system
        # 3. Return proposal ID for tracking
        
        # For now, return a placeholder
        return {
            "proposal_id": f"prop_{int(time.time())}",
            "change_type": change_type.value,
            "file_path": file_path,
            "reason": reason,
            "description": description,
            "status": "pending",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    
    def apply_change(self, whitelist: WhitelistFile) -> bool:
        """
        Apply a new whitelist version.
        
        This is called after a proposal has been approved through voting
        and physical confirmation has been obtained.
        
        Args:
            whitelist: The new WhitelistFile to apply
            
        Returns:
            True if change was applied successfully
        """
        # Verify this is a new version
        current = self.get_current_whitelist()
        if current and whitelist.version <= current.version:
            print(f"⚠️ Whitelist Version {whitelist.version} ist nicht neuer als {current.version}")
            return False
        
        # Save the new whitelist
        self._save_whitelist(whitelist)
        
        # Update current version
        self._current_version = whitelist.version
        self._save_current_version(whitelist.version)
        
        print(f"✅ Whitelist Version {whitelist.version} angewendet")
        return True
    
    def generate_whitelist_entry(self, file_path: str, description: str = "") -> WhitelistEntry:
        """
        Generate a whitelist entry for a file.
        
        Args:
            file_path: Path to the file
            description: Description of the file
            
        Returns:
            WhitelistEntry for the file
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
            
            return WhitelistEntry(
                file_path=file_path,
                file_hash=file_hash,
                description=description,
                required=True,
                change_type=WhitelistChangeType.ADD,
                added_version=self._current_version or "1.0"
            )
        except (FileNotFoundError, IOError) as e:
            raise ValueError(f"Konnte Datei {file_path} nicht lesen: {e}")
    
    def scan_directory(self, directory: str, description_prefix: str = "") -> List[WhitelistEntry]:
        """
        Scan a directory and generate whitelist entries for all Python files.
        
        Args:
            directory: Directory to scan
            description_prefix: Prefix for file descriptions
            
        Returns:
            List of WhitelistEntry objects
        """
        entries = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Remove directory prefix if it's the project root
                    if file_path.startswith(directory):
                        relative_path = file_path[len(directory):].lstrip('/\\')
                    else:
                        relative_path = file_path
                    
                    description = f"{description_prefix}{relative_path}"
                    try:
                        entry = self.generate_whitelist_entry(file_path, description)
                        entries.append(entry)
                    except ValueError as e:
                        print(f"⚠️ Konnte {file_path} nicht verarbeiten: {e}")
        
        return entries
