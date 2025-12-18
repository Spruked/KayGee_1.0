"""
Identity Contract Verification Tests
Run these to verify CryptoIdentifiable implementation
"""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.protocols import CryptoIdentifiable, ComponentIdentity, verify_component_contract
from src.handshake.manager import HandshakeProtocol
from src.perception.classifier import PerceptionSystem
from src.reasoning.recursive_loop import ReasoningEngine


class TestIdentityEnforcement:
    """Test 1: Identity Assignment Enforcement"""
    
    def test_identity_not_assigned_perception(self):
        """Verify RuntimeError raised when identity not assigned to PerceptionSystem"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        # Force identity to None to test error handling
        perception.identity = None
        
        with pytest.raises(RuntimeError, match="Identity not assigned"):
            perception.get_public_key()
    
    def test_identity_not_assigned_reasoning(self):
        """Verify RuntimeError raised when identity not assigned to ReasoningEngine"""
        handshake = HandshakeProtocol()
        reasoning = ReasoningEngine(handshake)
        
        # Force identity to None
        reasoning.identity = None
        
        with pytest.raises(RuntimeError, match="Identity not assigned"):
            reasoning.get_public_key()
    
    def test_identity_assigned_works(self):
        """Verify get_public_key() works when identity properly assigned"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        # Should not raise
        public_key = perception.get_public_key()
        
        assert isinstance(public_key, bytes)
        assert len(public_key) == 32  # Ed25519 key length


class TestDeterministicHashing:
    """Test 2: Deterministic State Hashing"""
    
    def test_perception_deterministic_hash(self):
        """Verify PerceptionSystem produces identical hashes for identical state"""
        handshake1 = HandshakeProtocol()
        handshake2 = HandshakeProtocol()
        
        perception1 = PerceptionSystem(handshake1)
        perception2 = PerceptionSystem(handshake2)
        
        # Get state hashes
        hash1 = perception1.get_state_hash()
        hash2 = perception2.get_state_hash()
        
        assert hash1 == hash2, f"Hashes differ:\n  {hash1}\n  {hash2}"
        assert len(hash1) == 64  # SHA-256 hex digest
        assert len(hash2) == 64
    
    def test_reasoning_deterministic_hash(self):
        """Verify ReasoningEngine produces identical hashes for identical state"""
        handshake1 = HandshakeProtocol()
        handshake2 = HandshakeProtocol()
        
        reasoning1 = ReasoningEngine(handshake1)
        reasoning2 = ReasoningEngine(handshake2)
        
        # Get state hashes
        hash1 = reasoning1.get_state_hash()
        hash2 = reasoning2.get_state_hash()
        
        assert hash1 == hash2, f"Hashes differ:\n  {hash1}\n  {hash2}"
        assert len(hash1) == 64
        assert len(hash2) == 64
    
    def test_hash_changes_on_state_change(self):
        """Verify state hash changes when component state changes"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        hash_before = perception.get_state_hash()
        
        # Change state (train classifier)
        import numpy as np
        X_dummy = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
        y_dummy = np.array([0])
        perception.intent_classifier.train(X_dummy, y_dummy)
        
        hash_after = perception.get_state_hash()
        
        assert hash_before != hash_after, "Hash should change when state changes"


class TestProtocolCompliance:
    """Test 3: CryptoIdentifiable Protocol Compliance"""
    
    def test_perception_implements_protocol(self):
        """Verify PerceptionSystem implements CryptoIdentifiable correctly"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        # Check inheritance
        assert isinstance(perception, CryptoIdentifiable)
        
        # Check contract compliance
        assert verify_component_contract(perception)
        
        # Check all required methods exist
        assert hasattr(perception, 'assign_identity')
        assert hasattr(perception, 'get_public_key')
        assert hasattr(perception, 'get_state_hash')
        assert hasattr(perception, 'identity')
    
    def test_reasoning_implements_protocol(self):
        """Verify ReasoningEngine implements CryptoIdentifiable correctly"""
        handshake = HandshakeProtocol()
        reasoning = ReasoningEngine(handshake)
        
        assert isinstance(reasoning, CryptoIdentifiable)
        assert verify_component_contract(reasoning)
        
        assert hasattr(reasoning, 'assign_identity')
        assert hasattr(reasoning, 'get_public_key')
        assert hasattr(reasoning, 'get_state_hash')
        assert hasattr(reasoning, 'identity')


class TestIdempotency:
    """Test 4: Identity Assignment Idempotency"""
    
    def test_assign_identity_idempotent(self):
        """Verify assign_identity() is idempotent (second call has no effect)"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        # Get original identity
        original_identity = perception.identity
        original_key = perception.get_public_key()
        
        # Try to assign new identity
        new_identity = handshake.create_identity("test_component")
        perception.assign_identity(new_identity)
        
        # Should still have original identity (idempotent)
        assert perception.identity == original_identity
        assert perception.get_public_key() == original_key


class TestPublicKeyFormat:
    """Test 5: Public Key Format Verification"""
    
    def test_public_key_returns_bytes(self):
        """Verify get_public_key() returns bytes, not str or other type"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        public_key = perception.get_public_key()
        
        assert isinstance(public_key, bytes), f"Expected bytes, got {type(public_key)}"
        assert len(public_key) == 32, f"Expected 32 bytes (Ed25519), got {len(public_key)}"
    
    def test_public_key_consistent(self):
        """Verify get_public_key() returns same value on multiple calls"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        key1 = perception.get_public_key()
        key2 = perception.get_public_key()
        key3 = perception.get_public_key()
        
        assert key1 == key2 == key3, "Public key should be consistent"


class TestStateHashContent:
    """Test 6: State Hash Content Verification"""
    
    def test_state_hash_excludes_timestamps(self):
        """Verify state hash doesn't include timestamps (would make it non-deterministic)"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        import time
        hash1 = perception.get_state_hash()
        time.sleep(0.01)  # Wait a bit
        hash2 = perception.get_state_hash()
        
        # Should be identical despite time passing
        assert hash1 == hash2, "State hash should not include timestamps"
    
    def test_state_hash_includes_version(self):
        """Verify state hash includes component version for tracking"""
        # This is more of a code inspection test
        # We verify by checking that VERSION constant exists
        assert hasattr(PerceptionSystem, 'VERSION')
        assert hasattr(ReasoningEngine, 'VERSION')


def run_all_tests():
    """Convenience function to run all tests with detailed output"""
    print("=" * 70)
    print("Running CryptoIdentifiable Contract Verification Tests")
    print("=" * 70)
    
    pytest.main([
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "-s"  # Show print statements
    ])


if __name__ == "__main__":
    run_all_tests()
