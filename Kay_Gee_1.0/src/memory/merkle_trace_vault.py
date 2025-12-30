"""
MerkleTraceVault
Append-only interaction ledger with O(log n) inclusion proofs
Pure Python, no external deps beyond hashlib
Integrates with existing TraceVault and SignedMessage provenance
"""

import hashlib
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MerkleProof:
    """JSON-serializable inclusion proof"""
    leaf_hash: str
    proof_hashes: List[str]  # Sibling hashes from leaf to root
    proof_indices: List[int]  # 0 = left, 1 = right
    root: str

class MerkleTraceVault:
    """
    Merkle-accelerated TraceVault
    - Commits Merkle root every COMMIT_INTERVAL entries
    - Generates verifiable inclusion proofs
    - Offline verification possible
    """
    
    COMMIT_INTERVAL = 32  # Rebuild tree every 32 entries (adjustable)

    def __init__(self, path: str = "data/trace_vault.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[Dict[str, Any]] = []
        self.leaf_hashes: List[str] = []
        self.current_root: Optional[str] = None
        self.commit_count = 0
        self._load_existing()

    def _load_existing(self):
        if not self.path.exists():
            return
        with open(self.path, "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    self.entries.append(entry)
                    leaf = self._hash_leaf(entry)
                    self.leaf_hashes.append(leaf)
        if self.leaf_hashes:
            self.current_root = self._build_tree(self.leaf_hashes)[-1]
            self.commit_count = len(self.entries) // self.COMMIT_INTERVAL

    def _hash_leaf(self, entry: Dict[str, Any]) -> str:
        canonical = json.dumps(entry, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _hash_node(self, left: str, right: str) -> str:
        return hashlib.sha256((left + right).encode()).hexdigest()

    def _build_tree(self, leaves: List[str]) -> List[str]:
        """Build full Merkle tree bottom-up, return all nodes (last is root)"""
        if not leaves:
            return ["0" * 64]  # Genesis empty root
        
        tree = leaves[:]
        while len(tree) > 1:
            if len(tree) % 2 == 1:
                tree.append(tree[-1])  # Duplicate last for odd count
            next_level = []
            for i in range(0, len(tree), 2):
                next_level.append(self._hash_node(tree[i], tree[i+1]))
            tree = next_level
        return tree

    def append(self, record: Dict[str, Any]) -> int:
        """Append record and return index"""
        record["index"] = len(self.entries)
        record["timestamp"] = time.time()
        
        # Add provenance from SignedMessage if present
        if "provenance" in record:
            record["provenance"].append({
                "step": "merkle_vault_commit",
                "vault_root": self.current_root or "genesis"
            })
        
        self.entries.append(record)
        
        leaf_hash = self._hash_leaf(record)
        self.leaf_hashes.append(leaf_hash)
        
        index = len(self.entries) - 1
        
        # Commit new root if interval reached
        if len(self.entries) % self.COMMIT_INTERVAL == 0:
            self.current_root = self._build_tree(self.leaf_hashes)[-1]
            self.commit_count += 1
            record["committed_root"] = self.current_root
            logger.info(f"Merkle root committed at entry {index}: {self.current_root[:16]}...")
        
        # Append to disk immediately (append-only)
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        return index

    def get_proof(self, index: int) -> MerkleProof:
        """Generate inclusion proof for entry at index"""
        if index >= len(self.leaf_hashes):
            raise IndexError("Entry not found")
        
        leaf_hash = self.leaf_hashes[index]
        proof_hashes: List[str] = []
        proof_indices: List[int] = []
        
        current_level = self.leaf_hashes[:]
        current_idx = index
        
        while len(current_level) > 1:
            if len(current_level) % 2 == 1:
                current_level.append(current_level[-1])
            
            if current_idx % 2 == 0:
                sibling_idx = current_idx + 1
                proof_indices.append(1)  # sibling is right
            else:
                sibling_idx = current_idx - 1
                proof_indices.append(0)  # sibling is left
            
            proof_hashes.append(current_level[sibling_idx])
            current_idx //= 2
            
            # Build next level
            next_level = []
            for i in range(0, len(current_level), 2):
                next_level.append(self._hash_node(current_level[i], current_level[i+1]))
            current_level = next_level
        
        root = current_level[0] if current_level else "0"*64
        
        return MerkleProof(
            leaf_hash=leaf_hash,
            proof_hashes=proof_hashes,
            proof_indices=proof_indices,
            root=root
        )

    @staticmethod
    def verify_proof(proof: MerkleProof) -> bool:
        """Offline verification of inclusion proof"""
        current = proof.leaf_hash
        for sibling, is_right in zip(proof.proof_hashes, proof.proof_indices):
            if is_right:
                # Sibling is on the right, so: hash(current + sibling)
                current = hashlib.sha256((current + sibling).encode()).hexdigest()
            else:
                # Sibling is on the left, so: hash(sibling + current)
                current = hashlib.sha256((sibling + current).encode()).hexdigest()
        return current == proof.root

    def get_current_root(self) -> str:
        return self.current_root or "0"*64

    def get_entry(self, index: int) -> Dict[str, Any]:
        return self.entries[index]

    def verify_chain(self) -> bool:
        """Full chain verification (recompute all committed roots)"""
        if not self.leaf_hashes:
            return True
        computed_root = self._build_tree(self.leaf_hashes)[-1]
        return computed_root == self.current_root
