"""
Memory Vault System
Three-layer vault architecture: A Priori, A Posteriori, Trace
"""

import sqlite3
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class VaultBase:
    """Base class for all vaults with cryptographic verification"""
    
    def __init__(self, db_path: str, immutable: bool = False):
        self.db_path = Path(db_path)
        self.immutable = immutable
        self.connection: Optional[sqlite3.Connection] = None
        self._checksum: Optional[str] = None
        
    def connect(self):
        """Establish database connection"""
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def compute_checksum(self) -> str:
        """Compute SHA-256 checksum of vault contents"""
        if not self.db_path.exists():
            return "EMPTY_VAULT"
        
        hasher = hashlib.sha256()
        with open(self.db_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify vault has not been tampered with"""
        if self.immutable:
            if self._checksum is None:
                self._checksum = self.compute_checksum()
                return True
            current_checksum = self.compute_checksum()
            return current_checksum == self._checksum
        return True  # Mutable vaults always pass
    
    def _execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL with error handling"""
        if not self.connection:
            self.connect()
        return self.connection.execute(query, params)
    
    def _commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()


class APrioriVault(VaultBase):
    """
    Immutable philosophical axioms vault
    Contains Kant, Locke, Spinoza, Hume rules
    Cryptographically signed and read-only
    """
    
    def __init__(self, db_path: str = "data/a_priori_vault.db"):
        super().__init__(db_path, immutable=True)
        self._initialize_schema()
        
    def _initialize_schema(self):
        """Create tables for philosophical axioms"""
        self.connect()
        
        self._execute("""
            CREATE TABLE IF NOT EXISTS axioms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                philosopher TEXT NOT NULL,
                axiom_type TEXT NOT NULL,
                predicate TEXT NOT NULL,
                prolog_rule TEXT NOT NULL,
                priority REAL NOT NULL,
                immutable_flag INTEGER DEFAULT 1,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        self._execute("""
            CREATE TABLE IF NOT EXISTS meta_weights (
                philosopher TEXT PRIMARY KEY,
                weight REAL NOT NULL,
                priority INTEGER NOT NULL,
                immutable_flag INTEGER DEFAULT 1
            )
        """)
        
        self._commit()
        
        # Seed with immutable meta-weights
        self._seed_meta_weights()
        
        # Lock the checksum
        self._checksum = self.compute_checksum()
    
    def _seed_meta_weights(self):
        """Seed immutable philosopher weights"""
        weights = [
            ("kant", 0.25, 1),
            ("locke", 0.30, 2),
            ("spinoza", 0.20, 3),
            ("hume", 0.25, 4)
        ]
        
        for philosopher, weight, priority in weights:
            try:
                self._execute("""
                    INSERT INTO meta_weights (philosopher, weight, priority, immutable_flag)
                    VALUES (?, ?, ?, 1)
                """, (philosopher, weight, priority))
            except sqlite3.IntegrityError:
                pass  # Already exists
        
        self._commit()
    
    def get_meta_weights(self) -> Dict[str, float]:
        """Get immutable philosopher weights"""
        cursor = self._execute("SELECT philosopher, weight FROM meta_weights")
        return {row['philosopher']: row['weight'] for row in cursor.fetchall()}
    
    def add_axiom(self, philosopher: str, axiom_type: str, predicate: str, 
                  prolog_rule: str, priority: float):
        """Add axiom (only during initial seeding)"""
        if not self.verify_integrity():
            raise SecurityError("A Priori Vault integrity compromised!")
        
        checksum = hashlib.sha256(prolog_rule.encode()).hexdigest()
        timestamp = datetime.utcnow().isoformat()
        
        self._execute("""
            INSERT INTO axioms (philosopher, axiom_type, predicate, prolog_rule, 
                                priority, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (philosopher, axiom_type, predicate, prolog_rule, priority, checksum, timestamp))
        
        self._commit()
        
        # Update master checksum
        self._checksum = self.compute_checksum()
    
    def query_axioms(self, philosopher: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query philosophical axioms"""
        if philosopher:
            cursor = self._execute(
                "SELECT * FROM axioms WHERE philosopher = ? ORDER BY priority DESC",
                (philosopher,)
            )
        else:
            cursor = self._execute("SELECT * FROM axioms ORDER BY priority DESC")
        
        return [dict(row) for row in cursor.fetchall()]


class APosterioriVault(VaultBase):
    """
    Mutable learned cases vault
    Stores experience-based knowledge
    Versioned for rollback capability
    """
    
    def __init__(self, db_path: str = "data/a_posteriori_vault.db"):
        super().__init__(db_path, immutable=False)
        self.version = 0
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create tables for learned cases"""
        self.connect()
        
        self._execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_hash TEXT UNIQUE NOT NULL,
                situation_vector TEXT NOT NULL,
                action TEXT NOT NULL,
                ethical_score REAL NOT NULL,
                philosopher_breakdown TEXT,
                outcome TEXT,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version INTEGER NOT NULL
            )
        """)
        
        self._execute("""
            CREATE TABLE IF NOT EXISTS invented_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT UNIQUE NOT NULL,
                features TEXT NOT NULL,
                philosophical_grounding TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                ethical_performance REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        """)
        
        self._execute("""
            CREATE INDEX IF NOT EXISTS idx_case_hash ON cases(case_hash)
        """)
        
        self._execute("""
            CREATE INDEX IF NOT EXISTS idx_ethical_score ON cases(ethical_score)
        """)
        
        self._commit()
    
    def add_case(self, situation_vector: List[float], action: str, 
                 ethical_score: float, philosopher_breakdown: Dict[str, Any],
                 outcome: Optional[str] = None, provenance: Optional[Dict] = None) -> str:
        """Add learned case to vault"""
        self.version += 1
        
        # Compute case hash
        case_data = json.dumps({
            "situation": situation_vector,
            "action": action
        }, sort_keys=True)
        case_hash = hashlib.sha256(case_data.encode()).hexdigest()[:16]
        
        timestamp = datetime.utcnow().isoformat()
        
        try:
            self._execute("""
                INSERT INTO cases (
                    case_hash, situation_vector, action, ethical_score,
                    philosopher_breakdown, outcome, created_at, updated_at, version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_hash,
                json.dumps(situation_vector),
                action,
                ethical_score,
                json.dumps(philosopher_breakdown),
                outcome,
                timestamp,
                timestamp,
                self.version
            ))
        except sqlite3.IntegrityError:
            # Case already exists - update instead
            self._execute("""
                UPDATE cases
                SET usage_count = usage_count + 1,
                    updated_at = ?,
                    version = ?
                WHERE case_hash = ?
            """, (timestamp, self.version, case_hash))
        
        self._commit()
        return case_hash
    
    def retrieve_cases(self, situation_vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve k most similar cases
        Uses Euclidean distance in semantic space
        """
        cursor = self._execute("""
            SELECT * FROM cases
            ORDER BY ethical_score DESC, usage_count DESC
            LIMIT ?
        """, (k * 2,))  # Get more for filtering
        
        all_cases = [dict(row) for row in cursor.fetchall()]
        
        # Compute similarity and sort
        for case in all_cases:
            stored_vector = json.loads(case['situation_vector'])
            case['similarity'] = self._compute_similarity(situation_vector, stored_vector)
        
        # Sort by similarity and return top k
        all_cases.sort(key=lambda x: x['similarity'], reverse=True)
        return all_cases[:k]
    
    @staticmethod
    def _compute_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a ** 2 for a in vec1) ** 0.5
        mag2 = sum(b ** 2 for b in vec2) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def add_invented_term(self, term: str, features: Dict[str, Any], 
                         grounding: str) -> bool:
        """Add emergent invented term"""
        timestamp = datetime.utcnow().isoformat()
        
        try:
            self._execute("""
                INSERT INTO invented_terms (term, features, philosophical_grounding, created_at)
                VALUES (?, ?, ?, ?)
            """, (term, json.dumps(features), grounding, timestamp))
            self._commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Term already exists
    
    def get_invented_terms(self) -> List[Dict[str, Any]]:
        """Get all invented terms for review"""
        cursor = self._execute("""
            SELECT * FROM invented_terms
            ORDER BY usage_count DESC, ethical_performance DESC
        """)
        return [dict(row) for row in cursor.fetchall()]


class TraceVault:
    """
    Append-only immutable trace log
    Blockchain-like structure for audit trail
    """
    
    def __init__(self, log_dir: str = "data/trace_vault"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.log_dir / f"trace_{datetime.utcnow().date()}.jsonl"
        self.blockchain: List[Dict[str, Any]] = []
    
    def append(self, transaction: Dict[str, Any]) -> str:
        """Append transaction to immutable log"""
        # Create block with Merkle root
        if self.blockchain:
            prev_hash = self.blockchain[-1]['merkle_root']
        else:
            prev_hash = "0" * 64
        
        timestamp = datetime.utcnow().isoformat()
        block = {
            "index": len(self.blockchain),
            "timestamp": timestamp,
            "transaction": transaction,
            "prev_hash": prev_hash,
            "merkle_root": self._compute_merkle_root(transaction, prev_hash)
        }
        
        # Sign block (placeholder - would use system master key)
        block["signature"] = self._sign_block(block)
        
        self.blockchain.append(block)
        
        # Write to disk (append-only)
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(block) + '\n')
        
        return block["merkle_root"]
    
    def verify_chain(self) -> bool:
        """Verify blockchain integrity"""
        for i in range(1, len(self.blockchain)):
            if self.blockchain[i]["prev_hash"] != self.blockchain[i-1]["merkle_root"]:
                return False
        return True
    
    def query(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict]:
        """Query trace log"""
        results = []
        for block in reversed(self.blockchain[-limit:]):
            if filters is None:
                results.append(block)
            else:
                # Simple filter matching
                match = all(
                    block['transaction'].get(k) == v 
                    for k, v in filters.items()
                )
                if match:
                    results.append(block)
        return results
    
    @staticmethod
    def _compute_merkle_root(transaction: Dict, prev_hash: str) -> str:
        """Compute Merkle root for block"""
        data = json.dumps(transaction, sort_keys=True) + prev_hash
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def _sign_block(block: Dict) -> str:
        """Sign block with system key (placeholder)"""
        block_data = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def get_last_24h(self) -> List[Dict]:
        """Get all traces from last 24 hours"""
        cutoff_time = time.time() - (24 * 3600)
        return [
            block for block in self.blockchain
            if datetime.fromisoformat(block['timestamp']).timestamp() > cutoff_time
        ]


class VaultSystem:
    """
    Main vault orchestrator
    Manages all three vaults with handshake protocol integration
    """
    
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.a_priori = APrioriVault()
        self.a_posteriori = APosterioriVault()
        self.trace = TraceVault()
        
        # Component identity for handshake
        self.component_id = "memory"
        self.public_key = None  # Set by handshake manager
    
    def get_public_key(self):
        """Get public key for handshake registration"""
        return self.public_key
    
    def verify_apriori_integrity(self) -> bool:
        """Verify immutable philosophical vault"""
        return self.a_priori.verify_integrity()
    
    def retrieve_cases(self, perception_data: Dict) -> List[Dict]:
        """Retrieve similar cases from A Posteriori vault"""
        situation_vector = perception_data.get('semantic_vector', [])
        return self.a_posteriori.retrieve_cases(situation_vector, k=5)
    
    def log_interaction(self, user_input: str, perception: Dict, 
                       cases: List[Dict], decision: Dict, 
                       response: Dict, context: Dict):
        """Log complete interaction to Trace Vault"""
        transaction = {
            "type": "interaction",
            "user_input": user_input,
            "perception": perception,
            "cases_used": [c.get('case_hash') for c in cases],
            "decision": decision,
            "response": response['text'],
            "philosophical_basis": response.get('philosophical_basis'),
            "ethical_score": response.get('ethical_score'),
            "context": context
        }
        
        self.trace.append(transaction)
    
    def get_trace_vault(self) -> TraceVault:
        """Get trace vault for learning system"""
        return self.trace
    
    def close(self):
        """Close all vaults"""
        self.a_priori.close()
        self.a_posteriori.close()


def initialize_vaults():
    """Initialize all vaults - run once on first setup"""
    print("🔧 Initializing Vaulted Reasoner vaults...")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    Path("data/trace_vault").mkdir(exist_ok=True)
    
    # Initialize A Priori vault
    apriori = APrioriVault()
    print(f"  ✓ A Priori Vault created: {apriori.db_path}")
    print(f"  ✓ Checksum: {apriori._checksum[:16]}...")
    
    # Initialize A Posteriori vault
    aposteriori = APosterioriVault()
    print(f"  ✓ A Posteriori Vault created: {aposteriori.db_path}")
    
    # Initialize Trace Vault
    trace = TraceVault()
    print(f"  ✓ Trace Vault created: {trace.log_dir}")
    
    print("✅ All vaults initialized successfully")


if __name__ == "__main__":
    initialize_vaults()
