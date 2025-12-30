"""
Vaults Module - SKG Fatigue-Resistant Architecture
Temporal Anchors & Drift Detection
"""

from typing import Dict, Any, List, Optional, Tuple
from src.core.layers import MemoryLayer
from src.memory.vault import VaultSystem, APrioriVault, TraceVault, APosterioriVault
from src.handshake.manager import HandshakeProtocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import asyncio
from collections import defaultdict
import json

# Global edge registry for resonance tracking
edge_registry = {}

@dataclass
class TemporalMetadata:
    ontology_version: str  # Merkle root of active A Priori
    created_at: datetime
    validity_window: Optional[timedelta] = None  # None = eternal
    retirement_date: Optional[datetime] = None
    resonance_score: float = 0.0  # Updated via async job
    turbulence_flags: List[str] = field(default_factory=list)

class VaultEntry:
    def __init__(self, content: Any, source_vault: str,
                 validity_window: Optional[timedelta] = None):
        self.content = content
        self.hash = self._compute_hash()
        self.temporal = TemporalMetadata(
            created_at=datetime.now(),
            validity_window=validity_window,
            ontology_version=self._get_current_ontology_merkle()
        )
        self.source_vault = source_vault  # 'seed', 'a_priori', 'a_posteriori'
        self.access_count = 0
        self.last_accessed = None

    def _compute_hash(self) -> str:
        return hashlib.sha256(str(self.content).encode()).hexdigest()[:16]

    def _get_current_ontology_merkle(self) -> str:
        # Placeholder - will be updated when ontology versioning is implemented
        return "v0_init"

@dataclass
class CandidateRecord:
    """Record for quarantined seed candidates"""
    principle: str
    resonance_history: List[float]
    query_volume: int
    philosopher_weights: Dict[str, float]
    discovery_date: datetime
    status: str  # 'quarantined', 'under_review', 'rejected', 'promoted'
    human_review_notes: Optional[str] = None

class SeedCandidateVault:
    """
    Quarantine vault for emergent principles
    Prevents automatic promotion to immutable Seed vault
    Requires human review for epistemic credibility
    """

    def __init__(self):
        self.candidates = {}  # hash → CandidateRecord

    def add_candidate(self, principle: str, stats: Dict):
        """Add a candidate principle to quarantine"""
        record = CandidateRecord(
            principle=principle,
            resonance_history=[stats['resonance']],
            query_volume=stats['query_count'],
            philosopher_weights=stats['weights'],
            discovery_date=datetime.now(),
            status='quarantined',
            human_review_notes=None
        )
        candidate_hash = self._hash(principle)
        self.candidates[candidate_hash] = record
        return candidate_hash

    def update_resonance(self, candidate_hash: str, new_resonance: float):
        """Update resonance history for a candidate"""
        if candidate_hash in self.candidates:
            self.candidates[candidate_hash].resonance_history.append(new_resonance)

    def requires_human_review(self) -> List[CandidateRecord]:
        """Return candidates that meet review criteria"""
        return [
            c for c in self.candidates.values()
            if self._calculate_mean_resonance(c.resonance_history) > 0.95
            and c.query_volume > 5000
            and c.status == 'quarantined'
        ]

    def promote_to_seed(self, candidate_hash: str, vault_manager: 'VaultManager',
                        review_notes: str = None) -> bool:
        """Promote candidate to Seed vault after human review"""
        if candidate_hash not in self.candidates:
            return False

        candidate = self.candidates[candidate_hash]

        # Create seed entry
        seed_entry = VaultEntry(
            content=candidate.principle,
            source_vault='seed'
        )

        # Add to seed vault
        vault_manager.seed_vaults[seed_entry.hash] = seed_entry

        # Update candidate status
        candidate.status = 'promoted'
        candidate.human_review_notes = review_notes

        return True

    def reject_candidate(self, candidate_hash: str, review_notes: str = None):
        """Reject candidate after human review"""
        if candidate_hash in self.candidates:
            self.candidates[candidate_hash].status = 'rejected'
            self.candidates[candidate_hash].human_review_notes = review_notes

    def _hash(self, principle: str) -> str:
        """Compute hash for principle"""
        return hashlib.sha256(principle.encode()).hexdigest()[:16]

    def _calculate_mean_resonance(self, history: List[float]) -> float:
        """Calculate mean resonance from history"""
        return sum(history) / len(history) if history else 0.0

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for dashboard display"""
        quarantined = [c for c in self.candidates.values() if c.status == 'quarantined']
        under_review = [c for c in self.candidates.values() if c.status == 'under_review']
        promoted = [c for c in self.candidates.values() if c.status == 'promoted']
        rejected = [c for c in self.candidates.values() if c.status == 'rejected']

        return {
            'total_candidates': len(self.candidates),
            'quarantined': len(quarantined),
            'under_review': len(under_review),
            'promoted': len(promoted),
            'rejected': len(rejected),
            'requires_review': len(self.requires_human_review())
        }

class VaultManager(MemoryLayer):
    """
    SKG Fatigue-Resistant Vault Manager
    Truth Cascade: Seed → A Priori → A Posteriori
    Entropy Flows Upward, Resonance Flows Downward
    """

    def __init__(self):
        super().__init__("VaultManager")
        self.handshake = None
        self.memory = None

        # SKG Architecture vaults
        self.seed_vaults = {}  # {hash: VaultEntry} - IMMUTABLE
        self.a_priori_vaults = {}  # {hash: VaultEntry} - VERSIONED
        self.a_posteriori_vault = defaultdict(list)  # {hash: [VaultEntry]}
        self.ontology_history = []  # Merkle roots with timestamps

        # Candidate quarantine vault - prevents automatic seed promotion
        self.seed_candidate_vault = SeedCandidateVault()

        # Legacy compatibility
        self.apriori_vault = None
        self.trace_vault = None
        self.episodic_vault = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            # Initialize handshake protocol
            self.handshake = HandshakeProtocol()

            # Initialize vault system (legacy)
            self.memory = VaultSystem(self.handshake)
            self.apriori_vault = APrioriVault()
            self.trace_vault = TraceVault()
            # Note: EpisodicVault not implemented yet
            # self.episodic_vault = EpisodicVault()

            # Bootstrap seed vaults with immutable truths
            self._bootstrap_seed_vaults()

            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize vaults: {e}")
            return False

    def _bootstrap_seed_vaults(self):
        """Load immutable seed truths"""
        seed_truths = [
            "The speed of light in vacuum is 299,792,458 m/s",
            "Water freezes at 0°C at sea level",
            "2 + 2 = 4",
            "A triangle has three sides",
            "The Earth orbits the Sun",
            "Gravity attracts objects with mass",
            "Energy cannot be created or destroyed",
            "Every effect has a cause",
            "Contradiction implies falsehood",
            "Identity is reflexive",
            "The whole is greater than the sum of its parts",
            "Change is constant",
            "Consciousness exists",
            "Truth is correspondence to reality",
            "Knowledge requires justification"
        ]

        for truth in seed_truths:
            entry = VaultEntry(content=truth, source_vault='seed')
            self.seed_vaults[entry.hash] = entry

    def commit_entry(self, entry: VaultEntry,
                    check_drift: bool = True) -> Tuple[bool, Optional[Dict]]:
        """
        Returns (is_valid, drift_report)
        Drift detection happens HERE at the vault level
        """
        # Semantic Drift Detection
        if check_drift and entry.source_vault == 'a_posteriori':
            drift_report = self._detect_turbulence(entry)
            if drift_report['severity'] == 'critical':
                entry.temporal.turbulence_flags.append('CONTRADICTION')
                # Don't commit - bubble up for review
                return False, drift_report

        # Append-only for A Posteriori
        self.a_posteriori_vault[entry.hash].append(entry)

        # Resonance initialization
        self._initialize_edge_weight(entry)

        return True, None

    def _detect_turbulence(self, entry: VaultEntry) -> Dict:
        """
        Checks new entry against Seed + A Priori
        Returns severity and conflicting entries
        """
        conflicts = []

        # Check against immutable truths
        for seed_hash, seed_entry in self.seed_vaults.items():
            if self._semantic_contradicts(entry.content, seed_entry.content):
                conflicts.append(('seed', seed_hash, seed_entry.content))

        # Check against A Priori (current version only)
        for ap_hash, ap_entry in self.a_priori_vaults.items():
            if ap_entry.temporal.retirement_date is None:  # Active
                if self._semantic_contradicts(entry.content, ap_entry.content):
                    conflicts.append(('a_priori', ap_hash, ap_entry.content))

        if conflicts:
            return {
                'severity': 'critical',
                'conflicts': conflicts,
                'recommendation': 'REQUIRE_HUMAN_REVIEW'
            }

        # Check for high resonance alignment
        resonance = self._compute_resonance_alignment(entry)
        if resonance > 0.85:
            return {
                'severity': 'harmonic',
                'resonance_boost': resonance,
                'action': 'STRENGTHEN_EDGES'
            }

        return {'severity': 'neutral'}

    def _semantic_contradicts(self, new_fact: str, existing_fact: str) -> bool:
        """
        Placeholder for actual contradiction detection
        Could use LLM consistency check or logical theorem prover
        """
        # Simplified: check for direct negation patterns
        new_lower = new_fact.lower()
        existing_lower = existing_fact.lower()

        contradictions = [
            (existing_lower, f"not {existing_lower}"),
            (existing_lower, f"{existing_lower} is not"),
            (existing_lower, f"{existing_lower} is false"),
            (f"{existing_lower} is true", f"{existing_lower} is false"),
        ]

        return any(neg in new_lower for _, neg in contradictions)

    def _compute_resonance_alignment(self, entry: VaultEntry) -> float:
        """Measure semantic similarity to high-confidence entries"""
        # Placeholder: simple keyword overlap
        high_confidence_entries = [
            e for e in self.seed_vaults.values()
        ] + [
            e for e in self.a_priori_vaults.values()
            if e.temporal.resonance_score > 0.9
        ]

        if not high_confidence_entries:
            return 0.5

        max_resonance = 0.0
        new_words = set(entry.content.lower().split())

        for existing_entry in high_confidence_entries:
            existing_words = set(existing_entry.content.lower().split())
            overlap = len(new_words.intersection(existing_words))
            total = len(new_words.union(existing_words))
            if total > 0:
                resonance = overlap / total
                max_resonance = max(max_resonance, resonance)

        return max_resonance

    def _on_identity_assigned(self):
        """
        Hook called after identity assignment
        Initialize crypto-dependent state for SKG vaults
        """
        print(f"✓ VaultManager identity assigned: {self.identity.fingerprint}")
        # Initialize any crypto-dependent state here if needed
        # For now, just log the assignment

    def get_state_hash(self) -> str:
        """
        Compute deterministic SHA-256 hash of internal state
        Includes state nonce for drift detection
        """
        state = {
            "version": "skg_v1",
            "state_nonce": self._state_nonce,
            "seed_count": len(self.seed_vaults),
            "a_priori_count": len(self.a_priori_vaults),
            "a_posteriori_count": sum(len(entries) for entries in self.a_posteriori_vault.values()),
            "ontology_history_length": len(self.ontology_history),
            "initialized": self._initialized
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()

    def get_status(self) -> Dict[str, Any]:
        # SKG Health metrics
        seed_count = len(self.seed_vaults)
        a_priori_count = len(self.a_priori_vaults)
        a_posteriori_count = sum(len(entries) for entries in self.a_posteriori_vault.values())

        # Legacy compatibility
        return {
            "vaults_initialized": self._initialized,
            "apriori_entries": len(self.apriori_vault.entries) if self.apriori_vault else 0,
            "trace_entries": len(self.trace_vault.entries) if self.trace_vault else 0,
            "episodic_entries": len(self.episodic_vault.entries) if self.episodic_vault else 0,
            # SKG metrics
            "skg_seed_count": seed_count,
            "skg_a_priori_count": a_priori_count,
            "skg_a_posteriori_count": a_posteriori_count,
            "skg_total_nodes": seed_count + a_priori_count + a_posteriori_count
        }

    def shutdown(self) -> None:
        pass
        # Vaults are typically persistent, but log shutdown
        print("VaultManager shutting down...")

    def store(self, key: str, data: Any) -> bool:
        """
        Store data in appropriate SKG vault based on key prefix
        Key prefixes: 'seed:', 'apriori:', 'aposteriori:'
        """
        if not self._initialized:
            return False

        try:
            if key.startswith('seed:'):
                # Seed vault is immutable - only allow if doesn't exist
                if key in self.seed_vaults:
                    return False  # Cannot overwrite seed truths
                entry = VaultEntry(content=data, source_vault='seed')
                self.seed_vaults[key] = entry
                return True

            elif key.startswith('apriori:'):
                entry = VaultEntry(content=data, source_vault='a_priori')
                self.a_priori_vaults[key] = entry
                return True

            elif key.startswith('aposteriori:'):
                entry = VaultEntry(content=data, source_vault='a_posteriori')
                is_valid, _ = self.commit_entry(entry, check_drift=True)
                return is_valid

            else:
                # Default to a posteriori with drift checking
                entry = VaultEntry(content=data, source_vault='a_posteriori')
                is_valid, _ = self.commit_entry(entry, check_drift=True)
                return is_valid

        except Exception as e:
            print(f"Failed to store in vault: {e}")
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data from SKG vaults with cascade lookup
        Priority: Seed → A Priori → A Posteriori
        """
        if not self._initialized:
            return None

        # Check seed vault first (highest priority)
        if key in self.seed_vaults:
            entry = self.seed_vaults[key]
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            return entry.content

        # Check A Priori vault
        if key in self.a_priori_vaults:
            entry = self.a_priori_vaults[key]
            if entry.temporal.retirement_date is None:  # Not retired
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                return entry.content

        # Check A Posteriori vault (most recent entries first)
        if key in self.a_posteriori_vault:
            entries = self.a_posteriori_vault[key]
            if entries:
                # Return most recent non-retired entry
                for entry in reversed(entries):
                    if entry.temporal.retirement_date is None:
                        entry.access_count += 1
                        entry.last_accessed = datetime.now()
                        return entry.content

        return None

    def search_similar(self, query: Any, limit: int = 10) -> list:
        """
        Search for similar entries across all SKG vaults
        Returns list of (key, content, similarity_score) tuples
        """
        if not self._initialized:
            return []

        results = []
        query_str = str(query).lower()
        query_words = set(query_str.split())

        # Search all vaults
        all_entries = []
        all_entries.extend([(k, v, 'seed') for k, v in self.seed_vaults.items()])
        all_entries.extend([(k, v, 'a_priori') for k, v in self.a_priori_vaults.items()])
        all_entries.extend([
            (k, entry, 'a_posteriori')
            for k, entries in self.a_posteriori_vault.items()
            for entry in entries
            if entry.temporal.retirement_date is None  # Only active entries
        ])

        for key, entry, vault_type in all_entries:
            content_str = str(entry.content).lower()
            content_words = set(content_str.split())

            # Calculate Jaccard similarity
            intersection = len(query_words.intersection(content_words))
            union = len(query_words.union(content_words))

            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # Minimum threshold
                    results.append((key, entry.content, similarity))

        # Sort by similarity (descending) and return top results
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:limit]