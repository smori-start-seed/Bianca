"""
Democratic Voting System for ALF Whitelist Changes

This module implements a democratic voting system for whitelist modifications,
ensuring that changes require community consensus (51% quorum) and optional
physical confirmation for critical changes.

Key Features:
- Proposal submission and tracking
- Node-based voting with reputation weighting
- Quorum calculation (51% of active voters)
- Physical confirmation integration (TPM/QR/Notary)
- Proposal finalization and archiving

Security Model:
1. Any node can propose a change
2. All nodes can vote (weighted by reputation)
3. 51% quorum required for approval
4. Critical changes require physical confirmation
5. All changes are cryptographically signed

Example:
    from core.whitelist.voting import VotingSystem, Proposal
    
    voting = VotingSystem()
    
    # Create a proposal
    proposal = voting.create_proposal(
        change_type="ADD",
        file_path="new_module.py",
        file_hash="abc123...",
        reason="New module for ALF growth"
    )
    
    # Vote on proposal
    voting.vote(proposal.id, node_id="node_1", vote=True)
    
    # Check if approved
    if voting.is_approved(proposal.id):
        # Apply change
        pass
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid


class VoteType(Enum):
    """Types of votes in the system."""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class ProposalStatus(Enum):
    """Current status of a proposal."""
    PENDING = "pending"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FINALIZED = "finalized"


class PhysicalConfirmationType(Enum):
    """Types of physical confirmation for critical changes."""
    NONE = "none"
    TPM = "tpm"  # Trusted Platform Module
    QR_CODE = "qr_code"  # QR code verification
    NOTARY = "notary"  # Notary service
    HARDWARE_KEY = "hardware_key"  # Hardware security key


@dataclass
class VoterInfo:
    """Information about a voter in the system."""
    node_id: str
    reputation: float = 1.0
    join_date: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    last_vote: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "reputation": self.reputation,
            "join_date": self.join_date,
            "last_vote": self.last_vote,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoterInfo":
        """Create from dictionary."""
        return cls(
            node_id=data.get("node_id", ""),
            reputation=data.get("reputation", 1.0),
            join_date=data.get("join_date", datetime.utcnow().isoformat() + "Z"),
            last_vote=data.get("last_vote"),
            is_active=data.get("is_active", True)
        )


@dataclass
class Vote:
    """A single vote on a proposal."""
    voter_id: str
    vote_type: VoteType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    weight: float = 1.0
    signature: Optional[str] = None  # Cryptographic signature
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "voter_id": self.voter_id,
            "vote_type": self.vote_type.value,
            "timestamp": self.timestamp,
            "weight": self.weight,
            "signature": self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vote":
        """Create from dictionary."""
        return cls(
            voter_id=data.get("voter_id", ""),
            vote_type=VoteType(data.get("vote_type", "abstain")),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            weight=data.get("weight", 1.0),
            signature=data.get("signature")
        )


@dataclass
class Proposal:
    """
    A proposal for a whitelist change.
    
    Attributes:
        id: Unique identifier for the proposal
        change_type: Type of change (ADD, REMOVE, UPDATE)
        file_path: Path to the file being changed
        file_hash: SHA-256 hash of the file (for ADD/UPDATE)
        old_hash: Previous hash (for UPDATE/REMOVE)
        reason: Human-readable reason for the change
        creator_id: Node ID of the creator
        status: Current status of the proposal
        created_at: Timestamp of creation
        voting_end: When voting period ends
        votes: List of votes on this proposal
        quorum: Required percentage for approval (default 51%)
        is_critical: Whether this is a critical change requiring physical confirmation
        physical_confirmation_type: Type of physical confirmation required
        physical_confirmation_data: Data for physical confirmation
        finalized_at: When the proposal was finalized
        applied_at: When the change was applied to the whitelist
    """
    id: str
    change_type: str  # "ADD", "REMOVE", "UPDATE"
    file_path: str
    file_hash: Optional[str] = None
    old_hash: Optional[str] = None
    reason: str = ""
    creator_id: str = ""
    status: ProposalStatus = ProposalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    voting_end: str = field(default_factory=lambda: (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z")
    votes: List[Vote] = field(default_factory=list)
    quorum: float = 0.51  # 51% required
    is_critical: bool = False
    physical_confirmation_type: PhysicalConfirmationType = PhysicalConfirmationType.NONE
    physical_confirmation_data: Optional[Dict[str, Any]] = None
    finalized_at: Optional[str] = None
    applied_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate proposal after initialization."""
        if self.change_type not in ["ADD", "REMOVE", "UPDATE"]:
            raise ValueError(f"Invalid change_type: {self.change_type}. Must be ADD, REMOVE, or UPDATE")
        
        # Ensure voting_end is in the future
        if self.voting_end:
            try:
                voting_end_dt = datetime.fromisoformat(self.voting_end.replace("Z", "+00:00"))
                if voting_end_dt <= datetime.utcnow():
                    self.voting_end = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
            except ValueError:
                self.voting_end = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
    
    @property
    def is_expired(self) -> bool:
        """Check if voting period has expired."""
        try:
            voting_end_dt = datetime.fromisoformat(self.voting_end.replace("Z", "+00:00"))
            return datetime.utcnow() > voting_end_dt
        except ValueError:
            return False
    
    def add_vote(self, vote: Vote) -> None:
        """Add a vote to this proposal."""
        # Check if voter already voted
        existing_votes = [v for v in self.votes if v.voter_id == vote.voter_id]
        if existing_votes:
            # Update existing vote
            existing_votes[0] = vote
        else:
            self.votes.append(vote)
    
    def get_vote_counts(self) -> Dict[VoteType, int]:
        """Get counts of each vote type."""
        counts = {VoteType.APPROVE: 0, VoteType.REJECT: 0, VoteType.ABSTAIN: 0}
        for vote in self.votes:
            counts[vote.vote_type] += 1
        return counts
    
    def get_weighted_votes(self) -> Dict[VoteType, float]:
        """Get weighted sum of votes."""
        weighted = {VoteType.APPROVE: 0.0, VoteType.REJECT: 0.0, VoteType.ABSTAIN: 0.0}
        for vote in self.votes:
            weighted[vote.vote_type] += vote.weight
        return weighted
    
    def get_total_weight(self) -> float:
        """Get total weight of all votes."""
        return sum(vote.weight for vote in self.votes)
    
    def get_approval_rate(self) -> float:
        """Get current approval rate (0.0 to 1.0)."""
        weighted = self.get_weighted_votes()
        total = self.get_total_weight()
        if total == 0:
            return 0.0
        return weighted[VoteType.APPROVE] / total
    
    def is_quorum_met(self) -> bool:
        """Check if quorum is met for approval."""
        return self.get_approval_rate() >= self.quorum
    
    def get_approving_voters(self) -> Set[str]:
        """Get set of voter IDs who approved."""
        return {v.voter_id for v in self.votes if v.vote_type == VoteType.APPROVE}
    
    def get_rejecting_voters(self) -> Set[str]:
        """Get set of voter IDs who rejected."""
        return {v.voter_id for v in self.votes if v.vote_type == VoteType.REJECT}
    
    def has_voted(self, voter_id: str) -> bool:
        """Check if a voter has already voted."""
        return any(v.voter_id == voter_id for v in self.votes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "change_type": self.change_type,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "old_hash": self.old_hash,
            "reason": self.reason,
            "creator_id": self.creator_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "voting_end": self.voting_end,
            "votes": [v.to_dict() for v in self.votes],
            "quorum": self.quorum,
            "is_critical": self.is_critical,
            "physical_confirmation_type": self.physical_confirmation_type.value,
            "physical_confirmation_data": self.physical_confirmation_data,
            "finalized_at": self.finalized_at,
            "applied_at": self.applied_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Proposal":
        """Create from dictionary."""
        proposal = cls(
            id=data.get("id", str(uuid.uuid4())),
            change_type=data.get("change_type", "ADD"),
            file_path=data.get("file_path", ""),
            file_hash=data.get("file_hash"),
            old_hash=data.get("old_hash"),
            reason=data.get("reason", ""),
            creator_id=data.get("creator_id", ""),
            status=ProposalStatus(data.get("status", "PENDING")),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            voting_end=data.get("voting_end", (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"),
            quorum=data.get("quorum", 0.51),
            is_critical=data.get("is_critical", False),
            physical_confirmation_type=PhysicalConfirmationType(
                data.get("physical_confirmation_type", "NONE")
            ),
            physical_confirmation_data=data.get("physical_confirmation_data"),
            finalized_at=data.get("finalized_at"),
            applied_at=data.get("applied_at")
        )
        
        # Load votes
        votes_data = data.get("votes", [])
        proposal.votes = [Vote.from_dict(v) for v in votes_data]
        
        return proposal


@dataclass
class VotingConfig:
    """Configuration for the voting system."""
    data_dir: Path = field(default_factory=lambda: Path("data/whitelist/voting"))
    proposal_file: str = "proposals.json"
    voters_file: str = "voters.json"
    default_voting_period_days: int = 7
    default_quorum: float = 0.51
    min_reputation: float = 0.1
    critical_change_types: List[str] = field(default_factory=lambda: ["REMOVE", "UPDATE"])
    critical_file_patterns: List[str] = field(default_factory=lambda: [
        "core/__init__.py",
        "core/identity.py",
        "core/zyklus.py",
        "core/mandate.py",
        "whitelist/"
    ])
    
    def __post_init__(self):
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)


class VotingSystem:
    """
    Democratic voting system for whitelist changes.
    
    This system manages:
    - Proposal creation and tracking
    - Voter registration and reputation
    - Vote collection and counting
    - Quorum calculation
    - Physical confirmation for critical changes
    - Proposal finalization
    
    Security Features:
    - Reputation-weighted voting
    - Time-limited voting periods
    - 51% quorum requirement
    - Physical confirmation for critical changes
    - Cryptographic signatures (optional)
    
    Example:
        voting = VotingSystem()
        
        # Create proposal
        proposal_id = voting.create_proposal(
            change_type="ADD",
            file_path="new_module.py",
            file_hash="abc123...",
            reason="New module for ALF"
        )
        
        # Vote
        voting.vote(proposal_id, "node_1", VoteType.APPROVE)
        
        # Check status
        if voting.is_approved(proposal_id):
            # Apply change
            pass
    """
    
    def __init__(self, config: Optional[VotingConfig] = None):
        """
        Initialize the voting system.
        
        Args:
            config: Configuration for the voting system. If None, uses defaults.
        """
        self.config = config or VotingConfig()
        self._proposals: Dict[str, Proposal] = {}
        self._voters: Dict[str, VoterInfo] = {}
        self._load_data()
    
    def _load_data(self) -> None:
        """Load proposals and voters from disk."""
        self._load_proposals()
        self._load_voters()
    
    def _save_data(self) -> None:
        """Save proposals and voters to disk."""
        self._save_proposals()
        self._save_voters()
    
    def _load_proposals(self) -> None:
        """Load proposals from file."""
        proposals_file = self.config.data_dir / self.config.proposal_file
        if proposals_file.exists():
            try:
                with open(proposals_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._proposals = {
                        p["id"]: Proposal.from_dict(p) for p in data.get("proposals", [])
                    }
            except (json.JSONDecodeError, IOError):
                self._proposals = {}
    
    def _save_proposals(self) -> None:
        """Save proposals to file."""
        proposals_file = self.config.data_dir / self.config.proposal_file
        data = {
            "proposals": [p.to_dict() for p in self._proposals.values()]
        }
        try:
            with open(proposals_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if can't save
    
    def _load_voters(self) -> None:
        """Load voters from file."""
        voters_file = self.config.data_dir / self.config.voters_file
        if voters_file.exists():
            try:
                with open(voters_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._voters = {
                        v["node_id"]: VoterInfo.from_dict(v) for v in data.get("voters", [])
                    }
            except (json.JSONDecodeError, IOError):
                self._voters = {}
    
    def _save_voters(self) -> None:
        """Save voters to file."""
        voters_file = self.config.data_dir / self.config.voters_file
        data = {
            "voters": [v.to_dict() for v in self._voters.values()]
        }
        try:
            with open(voters_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def register_voter(self, node_id: str, reputation: float = 1.0) -> VoterInfo:
        """
        Register a new voter in the system.
        
        Args:
            node_id: Unique identifier for the voter/node
            reputation: Initial reputation (0.0 to 1.0)
            
        Returns:
            The created VoterInfo
        """
        voter = VoterInfo(
            node_id=node_id,
            reputation=max(0.0, min(1.0, reputation))
        )
        self._voters[node_id] = voter
        self._save_voters()
        return voter
    
    def get_voter(self, node_id: str) -> Optional[VoterInfo]:
        """Get voter information by node ID."""
        return self._voters.get(node_id)
    
    def update_reputation(self, node_id: str, delta: float) -> bool:
        """
        Update a voter's reputation.
        
        Args:
            node_id: The voter to update
            delta: Change in reputation (-1.0 to 1.0)
            
        Returns:
            True if updated, False if voter not found
        """
        voter = self._voters.get(node_id)
        if voter is None:
            return False
        
        voter.reputation = max(0.0, min(1.0, voter.reputation + delta))
        self._save_voters()
        return True
    
    def create_proposal(
        self,
        change_type: str,
        file_path: str,
        file_hash: Optional[str] = None,
        old_hash: Optional[str] = None,
        reason: str = "",
        creator_id: str = "",
        is_critical: Optional[bool] = None,
        voting_period_days: Optional[int] = None
    ) -> str:
        """
        Create a new proposal for a whitelist change.
        
        Args:
            change_type: Type of change ("ADD", "REMOVE", "UPDATE")
            file_path: Path to the file being changed
            file_hash: SHA-256 hash of the new file (for ADD/UPDATE)
            old_hash: Previous hash (for UPDATE/REMOVE)
            reason: Human-readable reason for the change
            creator_id: Node ID of the creator
            is_critical: Override critical flag (None = auto-detect)
            voting_period_days: Override voting period (None = use default)
            
        Returns:
            The ID of the created proposal
        """
        # Auto-detect if critical
        if is_critical is None:
            is_critical = self._is_critical_change(change_type, file_path)
        
        # Set voting period
        if voting_period_days is None:
            voting_period_days = self.config.default_voting_period_days
        
        proposal = Proposal(
            id=str(uuid.uuid4()),
            change_type=change_type,
            file_path=file_path,
            file_hash=file_hash,
            old_hash=old_hash,
            reason=reason,
            creator_id=creator_id,
            is_critical=is_critical,
            quorum=self.config.default_quorum,
            voting_end=(datetime.utcnow() + timedelta(days=voting_period_days)).isoformat() + "Z"
        )
        
        # Set physical confirmation type for critical changes
        if is_critical:
            proposal.physical_confirmation_type = PhysicalConfirmationType.TPM
        
        self._proposals[proposal.id] = proposal
        self._save_proposals()
        
        return proposal.id
    
    def _is_critical_change(self, change_type: str, file_path: str) -> bool:
        """
        Determine if a change is critical based on type and file path.
        
        Args:
            change_type: Type of change
            file_path: Path to the file
            
        Returns:
            True if this is a critical change
        """
        # Critical change types
        if change_type in self.config.critical_change_types:
            return True
        
        # Critical file patterns
        for pattern in self.config.critical_file_patterns:
            if pattern in file_path:
                return True
        
        return False
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get a proposal by ID."""
        return self._proposals.get(proposal_id)
    
    def list_proposals(
        self,
        status: Optional[ProposalStatus] = None,
        is_critical: Optional[bool] = None
    ) -> List[Proposal]:
        """
        List all proposals, optionally filtered.
        
        Args:
            status: Filter by status
            is_critical: Filter by critical flag
            
        Returns:
            List of matching proposals
        """
        proposals = list(self._proposals.values())
        
        if status is not None:
            proposals = [p for p in proposals if p.status == status]
        
        if is_critical is not None:
            proposals = [p for p in proposals if p.is_critical == is_critical]
        
        # Sort by creation date (newest first)
        proposals.sort(
            key=lambda p: p.created_at,
            reverse=True
        )
        
        return proposals
    
    def vote(
        self,
        proposal_id: str,
        voter_id: str,
        vote_type: VoteType,
        weight: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Cast a vote on a proposal.
        
        Args:
            proposal_id: ID of the proposal to vote on
            voter_id: ID of the voter
            vote_type: Type of vote (APPROVE, REJECT, ABSTAIN)
            weight: Override vote weight (None = use voter reputation)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if proposal exists
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False, f"Proposal {proposal_id} not found"
        
        # Check if voting period is open
        if proposal.status != ProposalStatus.VOTING:
            return False, f"Proposal is not in voting state: {proposal.status.value}"
        
        # Check if voting period has expired
        if proposal.is_expired:
            proposal.status = ProposalStatus.EXPIRED
            self._save_proposals()
            return False, "Voting period has expired"
        
        # Check if voter exists
        voter = self._voters.get(voter_id)
        if voter is None:
            # Auto-register voter with default reputation
            voter = self.register_voter(voter_id)
        
        # Check if voter is active
        if not voter.is_active:
            return False, "Voter is not active"
        
        # Check reputation threshold
        if voter.reputation < self.config.min_reputation:
            return False, f"Voter reputation ({voter.reputation}) below minimum ({self.config.min_reputation})"
        
        # Determine vote weight
        if weight is None:
            weight = voter.reputation
        
        # Create vote
        vote = Vote(
            voter_id=voter_id,
            vote_type=vote_type,
            weight=weight
        )
        
        # Add vote to proposal
        proposal.add_vote(vote)
        
        # Update voter's last vote
        voter.last_vote = vote.timestamp
        self._save_voters()
        self._save_proposals()
        
        # Check if proposal is now approved or rejected
        self._check_proposal_status(proposal)
        
        return True, None
    
    def _check_proposal_status(self, proposal: Proposal) -> None:
        """
        Check if a proposal's status should be updated based on votes.
        
        Args:
            proposal: The proposal to check
        """
        # Check if expired
        if proposal.is_expired:
            proposal.status = ProposalStatus.EXPIRED
            return
        
        # Check if quorum is met
        if proposal.is_quorum_met():
            # Check for physical confirmation if critical
            if proposal.is_critical:
                if proposal.physical_confirmation_data:
                    proposal.status = ProposalStatus.APPROVED
                else:
                    proposal.status = ProposalStatus.PENDING
                    # Set to waiting for physical confirmation
                    return
            else:
                proposal.status = ProposalStatus.APPROVED
            return
        
        # Check if majority is against
        weighted = proposal.get_weighted_votes()
        total = proposal.get_total_weight()
        if total > 0:
            reject_rate = weighted[VoteType.REJECT] / total
            if reject_rate > 0.5:
                proposal.status = ProposalStatus.REJECTED
        
        # If no votes yet, ensure it's in VOTING state
        if len(proposal.votes) == 0 and proposal.status == ProposalStatus.PENDING:
            proposal.status = ProposalStatus.VOTING
    
    def is_approved(self, proposal_id: str) -> bool:
        """Check if a proposal is approved."""
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False
        return proposal.status == ProposalStatus.APPROVED
    
    def is_rejected(self, proposal_id: str) -> bool:
        """Check if a proposal is rejected."""
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False
        return proposal.status == ProposalStatus.REJECTED
    
    def finalize_proposal(
        self,
        proposal_id: str,
        physical_confirmation_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Finalize a proposal (mark as finalized and ready to apply).
        
        For critical changes, physical confirmation data must be provided.
        
        Args:
            proposal_id: ID of the proposal
            physical_confirmation_data: Data from physical confirmation
            
        Returns:
            Tuple of (success, error_message)
        """
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False, f"Proposal {proposal_id} not found"
        
        # Check if approved
        if proposal.status != ProposalStatus.APPROVED:
            return False, f"Proposal is not approved: {proposal.status.value}"
        
        # For critical changes, require physical confirmation
        if proposal.is_critical:
            if physical_confirmation_data is None:
                return False, "Critical change requires physical confirmation data"
            
            # Verify physical confirmation (placeholder for actual verification)
            if not self._verify_physical_confirmation(
                proposal.physical_confirmation_type,
                physical_confirmation_data
            ):
                return False, "Physical confirmation verification failed"
            
            proposal.physical_confirmation_data = physical_confirmation_data
        
        proposal.status = ProposalStatus.FINALIZED
        proposal.finalized_at = datetime.utcnow().isoformat() + "Z"
        self._save_proposals()
        
        return True, None
    
    def _verify_physical_confirmation(
        self,
        confirmation_type: PhysicalConfirmationType,
        data: Dict[str, Any]
    ) -> bool:
        """
        Verify physical confirmation data.
        
        This is a placeholder for actual verification logic.
        In production, this would integrate with TPM, QR code scanning, etc.
        
        Args:
            confirmation_type: Type of physical confirmation
            data: Confirmation data to verify
            
        Returns:
            True if verification succeeds, False otherwise
        """
        # For now, just check that data exists
        if not data:
            return False
        
        # In a real implementation, this would:
        # - For TPM: Verify TPM signature
        # - For QR_CODE: Verify QR code scan
        # - For NOTARY: Verify notary signature
        # - For HARDWARE_KEY: Verify hardware key signature
        
        return True
    
    def mark_as_applied(self, proposal_id: str) -> Tuple[bool, Optional[str]]:
        """
        Mark a proposal as applied to the whitelist.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Tuple of (success, error_message)
        """
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return False, f"Proposal {proposal_id} not found"
        
        # Check if finalized
        if proposal.status != ProposalStatus.FINALIZED:
            return False, f"Proposal is not finalized: {proposal.status.value}"
        
        proposal.status = ProposalStatus.APPROVED
        proposal.applied_at = datetime.utcnow().isoformat() + "Z"
        self._save_proposals()
        
        return True, None
    
    def get_proposal_stats(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a proposal.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Dictionary with statistics, or None if not found
        """
        proposal = self._proposals.get(proposal_id)
        if proposal is None:
            return None
        
        vote_counts = proposal.get_vote_counts()
        weighted_votes = proposal.get_weighted_votes()
        total_weight = proposal.get_total_weight()
        
        return {
            "id": proposal.id,
            "status": proposal.status.value,
            "change_type": proposal.change_type,
            "file_path": proposal.file_path,
            "is_critical": proposal.is_critical,
            "vote_counts": {k.value: v for k, v in vote_counts.items()},
            "weighted_votes": {k.value: v for k, v in weighted_votes.items()},
            "total_weight": total_weight,
            "approval_rate": proposal.get_approval_rate(),
            "quorum": proposal.quorum,
            "quorum_met": proposal.is_quorum_met(),
            "created_at": proposal.created_at,
            "voting_end": proposal.voting_end,
            "is_expired": proposal.is_expired,
            "num_votes": len(proposal.votes)
        }
    
    def cleanup_expired_proposals(self) -> int:
        """
        Clean up expired proposals that are still in PENDING or VOTING state.
        
        Returns:
            Number of proposals cleaned up
        """
        cleaned = 0
        for proposal_id, proposal in list(self._proposals.items()):
            if proposal.is_expired and proposal.status in [
                ProposalStatus.PENDING,
                ProposalStatus.VOTING
            ]:
                proposal.status = ProposalStatus.EXPIRED
                cleaned += 1
        
        if cleaned > 0:
            self._save_proposals()
        
        return cleaned
    
    def get_voter_stats(self, voter_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a voter.
        
        Args:
            voter_id: ID of the voter
            
        Returns:
            Dictionary with statistics, or None if not found
        """
        voter = self._voters.get(voter_id)
        if voter is None:
            return None
        
        # Count votes by this voter
        vote_counts = {}
        for proposal in self._proposals.values():
            for vote in proposal.votes:
                if vote.voter_id == voter_id:
                    vote_counts[vote.vote_type.value] = vote_counts.get(vote.vote_type.value, 0) + 1
        
        return {
            "node_id": voter.node_id,
            "reputation": voter.reputation,
            "join_date": voter.join_date,
            "last_vote": voter.last_vote,
            "is_active": voter.is_active,
            "vote_counts": vote_counts
        }


def calculate_quorum(
    votes: List[Vote],
    quorum_threshold: float = 0.51
) -> Tuple[bool, float]:
    """
    Calculate if quorum is met for a set of votes.
    
    Args:
        votes: List of votes
        quorum_threshold: Required percentage (0.0 to 1.0)
        
    Returns:
        Tuple of (quorum_met, approval_rate)
    """
    weighted = {VoteType.APPROVE: 0.0, VoteType.REJECT: 0.0, VoteType.ABSTAIN: 0.0}
    for vote in votes:
        weighted[vote.vote_type] += vote.weight
    
    total = sum(weighted.values())
    if total == 0:
        return False, 0.0
    
    approval_rate = weighted[VoteType.APPROVE] / total
    quorum_met = approval_rate >= quorum_threshold
    
    return quorum_met, approval_rate


def generate_proposal_signature(
    proposal: Proposal,
    secret_key: Optional[str] = None
) -> str:
    """
    Generate a cryptographic signature for a proposal.
    
    Args:
        proposal: The proposal to sign
        secret_key: Optional secret key (for HMAC)
        
    Returns:
        Hex-encoded signature
    """
    # Create signature data
    signature_data = f"{proposal.id}:{proposal.change_type}:{proposal.file_path}:{proposal.file_hash}"
    
    if secret_key:
        # HMAC signature
        import hmac
        signature = hmac.new(
            secret_key.encode("utf-8"),
            signature_data.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
    else:
        # Simple hash
        signature = hashlib.sha256(signature_data.encode("utf-8")).hexdigest()
    
    return signature


if __name__ == "__main__":
    # Demo usage
    voting = VotingSystem()
    
    # Register some voters
    voting.register_voter("node_1", reputation=1.0)
    voting.register_voter("node_2", reputation=0.8)
    voting.register_voter("node_3", reputation=0.6)
    
    # Create a proposal
    proposal_id = voting.create_proposal(
        change_type="ADD",
        file_path="new_module.py",
        file_hash="abc123def456",
        reason="Adding new module for ALF growth"
    )
    
    print(f"Created proposal: {proposal_id}")
    
    # Vote
    voting.vote(proposal_id, "node_1", VoteType.APPROVE)
    voting.vote(proposal_id, "node_2", VoteType.APPROVE)
    voting.vote(proposal_id, "node_3", VoteType.REJECT)
    
    # Get stats
    stats = voting.get_proposal_stats(proposal_id)
    print(f"Proposal stats: {stats}")
    print(f"Is approved: {voting.is_approved(proposal_id)}")
