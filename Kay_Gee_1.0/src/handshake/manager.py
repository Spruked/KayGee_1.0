"""
PAVC Handshake Protocol Manager - Hardened Version
Zero-drift enforcement via cryptographic handshakes (Ed25519 + deterministic state chaining)
"""

import hashlib
import time
import secrets
import json
from typing import Dict, Any, Optional

from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

# Use the core ComponentIdentity
from src.core.protocols import ComponentIdentity


class Transaction:
    """Immutable transaction structure"""
    
    def __init__(self, from_comp: str, to_comp: str, data: Any):
        self.tx_id = secrets.token_hex(16)
        self.from_comp = from_comp
        self.to_comp = to_comp
        self.data = data
        self.data_hash = self._hash_data(data)
        self.timestamp = time.time()
        self.nonce = secrets.randbits(64)
        self.signature: Optional[bytes] = None
    
    @staticmethod
    def _hash_data(data: Any) -> str:
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def metadata_for_signing(self) -> bytes:
        """Metadata that gets signed"""
        meta = {
            "tx_id": self.tx_id,
            "from": self.from_comp,
            "to": self.to_comp,
            "data_hash": self.data_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }
        return json.dumps(meta, sort_keys=True).encode('utf-8')


class HandshakeProtocol:
    """PAVC manager with full verification"""
    
    def __init__(self):
        self.identities: Dict[str, ComponentIdentity] = {}
        self.public_keys: Dict[str, VerifyKey] = {}  # Cached VerifyKey objects
        self.state_hashes: Dict[str, str] = {}
    
    def create_identity(self, name: str) -> ComponentIdentity:
        # Generate a new signing key for this component
        signing_key = SigningKey.generate()
        identity = ComponentIdentity(name, signing_key)
        self.identities[name] = identity
        self.public_keys[name] = identity.verify_key
        # Consistent genesis state
        genesis = hashlib.sha256(f"genesis_{name}".encode()).hexdigest()
        self.state_hashes[name] = genesis
        return identity
    
    def initiate_send(self, from_comp: str, to_comp: str, data: Any) -> Transaction:
        """Sender side: create and sign transaction"""
        if from_comp not in self.identities:
            raise ValueError(f"Unknown sender: {from_comp}")
        
        tx = Transaction(from_comp, to_comp, data)
        message = tx.metadata_for_signing()
        # sign() returns hex string, convert to bytes
        tx.signature = bytes.fromhex(self.identities[from_comp].sign(message))
        return tx
    
    def receive_and_commit(self, tx: Transaction) -> Dict[str, Any]:
        """Receiver side: verify and commit"""
        # Verify sender is registered
        if tx.from_comp not in self.public_keys:
            raise SecurityError(f"Unregistered sender: {tx.from_comp}")
        
        # Verify signature
        verify_key = self.public_keys[tx.from_comp]
        message = tx.metadata_for_signing()
        try:
            verify_key.verify(message, tx.signature)
        except BadSignatureError:
            raise SecurityError("Invalid signature")
        
        # Verify data integrity
        if tx.data_hash != Transaction._hash_data(tx.data):
            raise SecurityError("Data tampered")
        
        # Update both components' state deterministically
        self._update_state_hash(tx.from_comp, tx.data_hash)
        self._update_state_hash(tx.to_comp, tx.data_hash)
        
        return {
            "tx_id": tx.tx_id,
            "status": "COMMITTED",
            "data": tx.data,
            "state_from": self.state_hashes[tx.from_comp][:16] + "...",
            "state_to": self.state_hashes[tx.to_comp][:16] + "..."
        }
    
    def _update_state_hash(self, component: str, data_hash: str):
        current = self.state_hashes.get(component, hashlib.sha256(b"genesis").hexdigest())
        new_state = hashlib.sha256(f"{current}:{data_hash}".encode()).hexdigest()
        self.state_hashes[component] = new_state
    
    def get_state_hash(self, component: str) -> Optional[str]:
        return self.state_hashes.get(component)
    
    def verify_no_drift(self, component: str, expected: str) -> bool:
        return self.state_hashes.get(component) == expected


class SecurityError(Exception):
    pass


if __name__ == "__main__":
    protocol = HandshakeProtocol()
    
    perception = protocol.create_identity("perception")
    memory = protocol.create_identity("memory")
    reasoning = protocol.create_identity("reasoning")
    
    print("Testing Hardened PAVC Protocol...\n")
    
    test_data = {"features": {"stress": 0.6, "curiosity": 0.8}, "confidence": 0.82}
    
    # Sender (perception) initiates
    tx = protocol.initiate_send("perception", "memory", test_data)
    
    # Receiver (memory) verifies and commits
    result = protocol.receive_and_commit(tx)
    
    print(f"Transaction {tx.tx_id[:8]}... COMMITTED")
    print(f"Perception state: {protocol.get_state_hash('perception')[:16]}...")
    print(f"Memory state:     {protocol.get_state_hash('memory')[:16]}...")
    
    # Second transaction - state chains
    tx2 = protocol.initiate_send("memory", "reasoning", {"case_id": 42, "action": "suggest_tea"})
    protocol.receive_and_commit(tx2)
    
    print(f"\nAfter second tx → Reasoning state: {protocol.get_state_hash('reasoning')[:16]}...")
    print("\nZero-drift handshake protocol fully operational")
