"""
Core Protocols: Unified Cryptographic Identity Contract
Synthesis: PyNaCl (Claude) + State Nonce + SignedMessage (Kimi) + Zero-Drift Philosophy
"""

import time
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
import nacl.signing
import nacl.exceptions


class ComponentIdentity:
    """
    REAL cryptographic identity using PyNaCl Ed25519
    Immutable, fingerprinted, never serialized
    """
    
    def __init__(self, name: str, signing_key: nacl.signing.SigningKey):
        """
        Args:
            name: Component identifier (e.g., "perception", "reasoning")
            signing_key: PyNaCl Ed25519 signing key (NEVER serialize this)
        """
        self.name = name
        self.signing_key = signing_key
        self.created_at_ns = time.time_ns()
    
    @property
    def verify_key(self) -> nacl.signing.VerifyKey:
        """Public verification key"""
        return self.signing_key.verify_key
    
    @property
    def fingerprint(self) -> str:
        """Deterministic 32-character identifier"""
        return self.verify_key.encode().hex()[:32]
    
    def get_public_key(self) -> bytes:
        """Returns 32-byte Ed25519 verification key for handshake registration"""
        return bytes(self.verify_key)
    
    def sign(self, message: bytes) -> str:
        """Sign message using Ed25519, return hex signature"""
        signed = self.signing_key.sign(message)
        return signed.signature.hex()
    
    def __repr__(self) -> str:
        return f"ComponentIdentity(name='{self.name}', fingerprint='{self.fingerprint}', created={self.created_at_ns})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, ComponentIdentity):
            return False
        return self.fingerprint == other.fingerprint


class IdentityBoundComponent(ABC):
    """
    Unified Contract: PyNaCl Crypto + State Nonce + Message Signing
    
    MANDATE: Every system component MUST inherit from this.
    
    Features:
    - Real Ed25519 signatures via PyNaCl
    - State nonce tracking (detects silent mutations)
    - Automatic message signing (no manual crypto)
    - Identity fingerprinting
    - Zero-drift detection
    
    Philosophy:
    "A component that cannot prove its identity has no right to speak."
    "A component that doesn't track its state has already drifted."
    """
    
    def __init__(self):
        """
        Initialize identity state
        Subclasses MUST call super().__init__() first
        """
        self._identity: Optional[ComponentIdentity] = None
        self._state_nonce = 0
        self._message_log: List['SignedMessage'] = []
    
    def assign_identity(self, identity: ComponentIdentity) -> None:
        """
        Assign cryptographic identity (idempotent, secure)
        Called by HandshakeProtocol after component creation
        
        Security:
        - Idempotent: second call with same identity is no-op
        - Attack detection: raises SecurityError if identity changes
        
        Args:
            identity: ComponentIdentity from HandshakeProtocol
        
        Raises:
            SecurityError: If attempt to change existing identity
        """
        if self._identity is not None:
            if self._identity.fingerprint != identity.fingerprint:
                raise SecurityError(
                    f"Identity re-assignment attack on {identity.name}! "
                    f"Old: {self._identity.fingerprint}, New: {identity.fingerprint}"
                )
            return  # Already assigned, no-op
        
        self._identity = identity
        self._on_identity_assigned()
    
    @abstractmethod
    def _on_identity_assigned(self):
        """
        Hook called after identity assignment
        Subclasses initialize crypto-dependent state here
        
        Example:
            def _on_identity_assigned(self):
                logger.info(f"✓ {self.identity.name} identity assigned")
                self._initialize_crypto_cache()
        """
        pass
    
    @property
    def identity(self) -> ComponentIdentity:
        """
        Read-only access to identity
        
        Raises:
            RuntimeError: If identity not assigned yet
        """
        if self._identity is None:
            raise RuntimeError(f"Component {self.__class__.__name__} identity not assigned!")
        return self._identity
    
    def get_public_key(self) -> bytes:
        """
        Return Ed25519 verification key for handshake registration
        
        Returns:
            32-byte Ed25519 public key
        
        Raises:
            RuntimeError: If identity not assigned
        """
        return self.identity.get_public_key()
    
    @abstractmethod
    def get_state_hash(self) -> str:
        """
        Compute deterministic SHA-256 hash of internal state
        
        CRITICAL: MUST include self._state_nonce
        
        Example:
            state = {
                "version": self.VERSION,
                "state_nonce": self._state_nonce,
                "config": self._serialize_config()
            }
            return hashlib.sha256(
                json.dumps(state, sort_keys=True).encode()
            ).hexdigest()
        
        Returns:
            64-character hex string (SHA-256 digest)
        """
        pass
    
    def _increment_state(self):
        """
        Call this on EVERY internal state mutation
        Enables detection of silent state changes
        
        Usage:
            def process(self, data):
                result = self._compute(data)
                self._increment_state()  # MUST call
                return result
        """
        self._state_nonce += 1
    
    def sign_message(self, payload: Dict[str, Any], receiver_fp: str) -> 'SignedMessage':
        """
        Create cryptographically signed message (automatic)
        
        Args:
            payload: Message data (must be dict for canonical serialization)
            receiver_fp: Recipient's fingerprint
        
        Returns:
            SignedMessage with Ed25519 signature
        
        Raises:
            TypeError: If payload is not dict
            RuntimeError: If identity not assigned
        """
        if not isinstance(payload, dict):
            raise TypeError("Payload must be dict for canonical serialization")
        
        return SignedMessage.create(
            payload=payload,
            sender_identity=self.identity,
            receiver_fp=receiver_fp,
            state_nonce=self._state_nonce
        )
    
    def verify_message(self, message: 'SignedMessage') -> bool:
        """
        Verify message signature and log it
        
        Args:
            message: SignedMessage to verify
        
        Returns:
            True if signature valid, False otherwise
        """
        if not message.verify():
            return False
        
        self._message_log.append(message)
        return True


class SecurityError(Exception):
    """Raised on cryptographic security violations"""
    pass


class SignedMessage:
    """
    Every inter-component message MUST be signed
    Kimi's wrapper + Claude's PyNaCl implementation
    """
    
    def __init__(self, payload: Dict[str, Any], sender_fp: str, receiver_fp: str,
                 timestamp_ns: int, state_nonce: int, signature: str):
        """
        Direct constructor (use SignedMessage.create() instead)
        """
        self.payload = payload
        self.sender_fp = sender_fp
        self.receiver_fp = receiver_fp
        self.timestamp_ns = timestamp_ns
        self.state_nonce = state_nonce
        self.signature = signature
    
    @classmethod
    def create(cls, payload: Dict[str, Any], sender_identity: ComponentIdentity,
               receiver_fp: str, state_nonce: int) -> 'SignedMessage':
        """
        Factory method - signs automatically using Ed25519
        
        Args:
            payload: Message data (must be dict)
            sender_identity: Sender's ComponentIdentity
            receiver_fp: Receiver's fingerprint
            state_nonce: Sender's current state nonce
        
        Returns:
            SignedMessage with Ed25519 signature
        """
        timestamp_ns = time.time_ns()
        
        # Canonical serialization for signing
        canonical = json.dumps({
            "payload": payload,
            "sender_fp": sender_identity.fingerprint,
            "receiver_fp": receiver_fp,
            "timestamp_ns": timestamp_ns,
            "state_nonce": state_nonce
        }, sort_keys=True, separators=(',', ':')).encode()
        
        # Sign with Ed25519
        signature = sender_identity.sign(canonical)
        
        return cls(
            payload=payload,
            sender_fp=sender_identity.fingerprint,
            receiver_fp=receiver_fp,
            timestamp_ns=timestamp_ns,
            state_nonce=state_nonce,
            signature=signature
        )
    
    def _canonical_bytes(self) -> bytes:
        """Reconstruct canonical form for verification"""
        return json.dumps({
            "payload": self.payload,
            "sender_fp": self.sender_fp,
            "receiver_fp": self.receiver_fp,
            "timestamp_ns": self.timestamp_ns,
            "state_nonce": self.state_nonce
        }, sort_keys=True, separators=(',', ':')).encode()
    
    def verify(self, sender_verify_key: nacl.signing.VerifyKey = None) -> bool:
        """
        Verify Ed25519 signature
        
        Args:
            sender_verify_key: Optional - if provided, uses this key
                              If None, looks up from handshake registry
        
        Returns:
            True if signature valid, False otherwise
        """
        if sender_verify_key is None:
            # In production, get from HandshakeProtocol registry
            # For now, we'll need the key passed in
            raise NotImplementedError(
                "Must pass sender_verify_key or integrate with HandshakeProtocol registry"
            )
        
        canonical = self._canonical_bytes()
        
        try:
            sender_verify_key.verify(canonical, bytes.fromhex(self.signature))
            return True
        except nacl.exceptions.BadSignatureError:
            return False
    
    def get_provenance_entry(self) -> Dict[str, str]:
        """For Merkle tree insertion"""
        return {
            "sender": self.sender_fp,
            "receiver": self.receiver_fp,
            "payload_hash": hashlib.sha256(str(self.payload).encode()).hexdigest()[:32],
            "signature": self.signature,
            "timestamp_ns": str(self.timestamp_ns),
            "state_nonce": str(self.state_nonce)
        }
    
    def __repr__(self) -> str:
        return (f"SignedMessage(sender={self.sender_fp[:8]}..., "
                f"receiver={self.receiver_fp[:8]}..., "
                f"nonce={self.state_nonce})")


# Legacy compatibility mixins

class VaultCompliant(ABC):
    """
    Optional mixin for components that interact with vault system
    Extends IdentityBoundComponent with vault-specific contracts
    """
    
    @abstractmethod
    def verify_integrity(self) -> bool:
        """Verify component's internal consistency"""
        pass
    
    @abstractmethod
    def export_audit_log(self) -> dict:
        """Export component's operation log for audit trail"""
        pass


class LearningCompliant(ABC):
    """Optional mixin for components that participate in learning consolidation"""
    
    @abstractmethod
    def consolidate(self, traces: list) -> dict:
        """Consolidate interaction traces into learned patterns"""
        pass


# Verification utilities

def verify_component_contract(component: Any) -> bool:
    """
    Verify that a component implements IdentityBoundComponent correctly
    
    Args:
        component: Component instance to verify
    
    Returns:
        True if contract satisfied, False otherwise
    """
    if not isinstance(component, IdentityBoundComponent):
        return False
    
    if not hasattr(component, '_identity'):
        return False
    
    required_methods = ['assign_identity', 'get_public_key', 'get_state_hash', 
                       '_on_identity_assigned', '_increment_state', 
                       'sign_message', 'verify_message']
    
    for method in required_methods:
        if not hasattr(component, method) or not callable(getattr(component, method)):
            return False
    
    return True


def generate_identity_manifest(components: dict) -> dict:
    """
    Generate cryptographic manifest of all component identities
    
    Args:
        components: Dictionary mapping component names to instances
    
    Returns:
        Manifest with identities, fingerprints, and manifest hash
    """
    identities = []
    
    for name, component in components.items():
        if not isinstance(component, IdentityBoundComponent):
            continue
        
        try:
            identity = component.identity
            identities.append({
                'name': identity.name,
                'fingerprint': identity.fingerprint,
                'public_key_hex': identity.get_public_key().hex(),
                'created_at_ns': identity.created_at_ns
            })
        except RuntimeError:
            # Identity not assigned yet
            continue
    
    manifest = {
        'component_count': len(identities),
        'identities': identities,
        'timestamp_ns': time.time_ns()
    }
    
    # Compute manifest hash
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    manifest['manifest_hash'] = hashlib.sha256(manifest_bytes).hexdigest()
    
    return manifest


if __name__ == "__main__":
    print("✅ Unified Core Protocols Module Loaded")
    print("   - ComponentIdentity: PyNaCl Ed25519 (real crypto)")
    print("   - IdentityBoundComponent: State nonce + message signing")
    print("   - SignedMessage: Automatic Ed25519 signing")
    print("   - SecurityError: Cryptographic violation detection")
    print("   - Verification utilities included")


class VaultCompliant(ABC):
    """
    Optional mixin for components that interact with vault system
    Extends CryptoIdentifiable with vault-specific contracts
    """
    
    @abstractmethod
    def verify_integrity(self) -> bool:
        """
        Verify component's internal consistency
        
        Returns:
            True if component state is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def export_audit_log(self) -> dict:
        """
        Export component's operation log for audit trail
        
        Returns:
            Dictionary with:
            - operations: List of operations performed
            - state_hashes: Historical state hashes
            - timestamps: Corresponding timestamps
        """
        pass


class LearningCompliant(ABC):
    """
    Optional mixin for components that participate in learning consolidation
    Used by: LearningSystem, EpisodicVault, TemporalContextLayer
    """
    
    @abstractmethod
    def consolidate(self, traces: list) -> dict:
        """
        Consolidate interaction traces into learned patterns
        
        Args:
            traces: List of interaction records from TraceVault
        
        Returns:
            Dictionary with consolidation results:
            - patterns_learned: Number of new patterns
            - rules_induced: Number of rules created
            - confidence: Overall consolidation confidence
        """
        pass


def verify_component_contract(component: Any) -> bool:
    """
    Verify that a component implements CryptoIdentifiable correctly
    
    Args:
        component: Component instance to verify
    
    Returns:
        True if contract satisfied, False otherwise
    
    Usage:
        >>> from src.perception.classifier import PerceptionSystem
        >>> perception = PerceptionSystem(handshake)
        >>> verify_component_contract(perception)
        True
    """
    # Check class inheritance
    if not isinstance(component, CryptoIdentifiable):
        return False
    
    # Check attribute existence
    if not hasattr(component, 'identity'):
        return False
    
    # Check method signatures
    required_methods = ['assign_identity', 'get_public_key', 'get_state_hash']
    for method in required_methods:
        if not hasattr(component, method) or not callable(getattr(component, method)):
            return False
    
    return True


def generate_identity_manifest(components: dict) -> dict:
    """
    Generate cryptographic manifest of all component identities
    
    Args:
        components: Dictionary mapping component names to instances
    
    Returns:
        Manifest dictionary with:
        - component_count: Number of registered components
        - identities: List of {name, public_key_hex, created_at}
        - manifest_hash: SHA-256 of entire manifest
    
    Usage in orchestrator:
        >>> manifest = generate_identity_manifest(self.components)
        >>> self.audit.log_system_manifest(manifest)
    """
    identities = []
    
    for name, component in components.items():
        if not isinstance(component, CryptoIdentifiable):
            continue
        
        try:
            public_key = component.get_public_key()
            identities.append({
                'name': name,
                'public_key_hex': public_key.hex(),
                'created_at': getattr(component.identity, 'created_at', None)
            })
        except RuntimeError:
            # Identity not assigned yet
            continue
    
    manifest = {
        'component_count': len(identities),
        'identities': identities,
        'timestamp': time.time()
    }
    
    # Compute manifest hash
    manifest_bytes = json.dumps(manifest, sort_keys=True).encode()
    manifest['manifest_hash'] = hashlib.sha256(manifest_bytes).hexdigest()
    
    return manifest


if __name__ == "__main__":
    print("✅ Core protocols module loaded")
    print("   - ComponentIdentity: Immutable identity container")
    print("   - CryptoIdentifiable: Required contract for all components")
    print("   - VaultCompliant: Optional vault interaction mixin")
    print("   - LearningCompliant: Optional learning participation mixin")
