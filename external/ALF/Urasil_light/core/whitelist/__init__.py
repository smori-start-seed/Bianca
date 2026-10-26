"""
ALF Whitelist Module

This module implements a secure, democratic whitelist system for ALF that:
1. Maintains an immutable list of trusted files/modules
2. Allows changes only through democratic voting
3. Requires physical confirmation for critical changes
4. Prevents unauthorized modifications

The whitelist ensures that only trusted code can run in the ALF network,
protecting against malware, tampering, and other security threats.

Architecture:
    WhitelistManager
    ├── WhitelistFile (immutable, signed, versioned)
    ├── VotingSystem (democratic voting on changes)
    ├── PhysicalConfirmation (TPM, QR codes, community meetings)
    └── Validation (check files against whitelist)

Example:
    from core.whitelist import WhitelistManager
    
    # Initialize whitelist manager
    manager = WhitelistManager()
    
    # Check if a file is allowed
    if manager.is_allowed("core/llm_bridge.py"):
        # File is in whitelist, safe to load
        import_module("core.llm_bridge")
    
    # Propose a change (requires voting)
    manager.propose_change("core/new_module.py", {"reason": "New feature"})
"""

from .whitelist import WhitelistManager, WhitelistFile, WhitelistEntry
from .voting import VotingSystem, Proposal

__all__ = [
    'WhitelistManager', 
    'WhitelistFile', 
    'WhitelistEntry',
    'VotingSystem',
    'Proposal'
]
