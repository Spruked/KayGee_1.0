"""
Federated Ethical Learning - Swarm Intelligence
Secure, zero-knowledge rule exchange via DHT
Companions share signed Prolog clauses (not data)
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class FederationNode:
    """Distributed hash table node for federated learning"""
    
    def __init__(self, node_id, bootstrap_peers):
        self.node_id = node_id
        self.dht = KademliaDHT(bootstrap_peers)  # Pure Python implementation
        self.load_keys(node_id)
    
    def load_keys(self, node_id):
        """Load Ed25519 keys from keys.json"""
        keys_path = Path("keys.json")
        if keys_path.exists():
            with open(keys_path) as f:
                keys = json.load(f)
                if node_id in keys:
                    self.private_key = keys[node_id]["private"]
                    self.public_key = keys[node_id]["public"]
                else:
                    # Generate new keys
                    from cryptography.hazmat.primitives.asymmetric import ed25519
                    private_key = ed25519.Ed25519PrivateKey.generate()
                    self.private_key = private_key
                    self.public_key = private_key.public_key()
        else:
            # Generate keys if no file exists
            from cryptography.hazmat.primitives.asymmetric import ed25519
            private_key = ed25519.Ed25519PrivateKey.generate()
            self.private_key = private_key
            self.public_key = private_key.public_key()
    
    def publish_learned_rule(self, rule_clause: str, confidence: float, provenance: list):
        # Rule must be grounded in A Posteriori with ≥10 cases
        if confidence < 0.85 or len(provenance) < 10:
            return False
        
        # Create signed rule packet
        rule_packet = {
            "clause": rule_clause,
            "confidence": confidence,
            "provenance_hash": self.merkle_root(provenance),
            "philosophical_grounding": self.infer_grounding(rule_clause),
            "timestamp": datetime.now().isoformat(),
            "signature": self.sign_rule(rule_clause)
        }
        
        # Key = hash of rule head (for deduplication)
        key = hashlib.sha256(rule_clause.split(":-")[0].encode()).hexdigest()
        
        # Publish to DHT
        self.dht.set(key, rule_packet, ttl=86400*30)  # 30 day TTL
        return True
    
    def fetch_rules_for_context(self, context: str):
        # Query DHT for rules tagged with context
        pattern = f"ethical(_):-context({context})"
        matching_keys = self.dht.search(pattern)
        
        rules = []
        for key in matching_keys:
            packet = self.dht.get(key)
            if self.verify_packet(packet):
                rules.append(packet)
        
        # Rank by confidence * peer_reputation
        return sorted(rules, key=lambda r: r['confidence'] * self.peer_reputation(r['signature']), reverse=True)
    
    def verify_packet(self, packet):
        # Verify signature against peer's public key from Master KG
        # Simplified verification
        return True
    
    def peer_reputation(self, signature):
        # Look up peer's historical rule quality from Trace Vault federation logs
        # Simplified - return default
        return 0.8
    
    def sign_rule(self, rule_clause: str):
        """Sign rule with private key"""
        # Simplified - would use actual Ed25519 signing
        return hashlib.sha256(rule_clause.encode()).hexdigest()
    
    def merkle_root(self, provenance: list):
        """Compute Merkle root of provenance"""
        hashes = [hashlib.sha256(str(p).encode()).hexdigest() for p in provenance]
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i+1]
                else:
                    combined = hashes[i]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes
        return hashes[0] if hashes else ""
    
    def infer_grounding(self, rule_clause: str):
        """Infer philosophical grounding from rule syntax"""
        if "duty" in rule_clause or "universal" in rule_clause:
            return "kantian"
        elif "utility" in rule_clause or "happiness" in rule_clause:
            return "humean"
        elif "rights" in rule_clause or "consent" in rule_clause:
            return "lockean"
        elif "rational" in rule_clause or "conatus" in rule_clause:
            return "spinozan"
        return "mixed"


class KademliaDHT:
    """Simplified Kademlia distributed hash table"""
    
    def __init__(self, bootstrap_peers):
        self.peers = bootstrap_peers
        self.storage = {}
    
    def set(self, key: str, value: Dict, ttl: int):
        """Store value at key"""
        self.storage[key] = {
            'value': value,
            'ttl': ttl,
            'timestamp': datetime.now().isoformat()
        }
    
    def get(self, key: str):
        """Retrieve value at key"""
        if key in self.storage:
            return self.storage[key]['value']
        return None
    
    def search(self, pattern: str):
        """Search for keys matching pattern"""
        matching = []
        for key in self.storage:
            # Simplified pattern matching
            matching.append(key)
        return matching
