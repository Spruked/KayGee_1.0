"""
Unified Protocol Verification Tests
Tests PyNaCl + State Nonce + SignedMessage integration
"""

import sys
import pytest
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.protocols import (
    ComponentIdentity, IdentityBoundComponent, SignedMessage,
    SecurityError, verify_component_contract
)
from src.handshake.manager import HandshakeProtocol
from src.perception.classifier import PerceptionSystem
from src.reasoning.recursive_loop import ReasoningEngine
import nacl.signing


class TestComponentIdentity:
    """Test ComponentIdentity with real PyNaCl"""
    
    def test_create_identity(self):
        """Verify ComponentIdentity creates valid Ed25519 keys"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("test_component", signing_key)
        
        assert identity.name == "test_component"
        assert isinstance(identity.verify_key, nacl.signing.VerifyKey)
        assert len(identity.fingerprint) == 32
        assert len(identity.get_public_key()) == 32
    
    def test_identity_signing(self):
        """Verify identity can sign and signature is verifiable"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("test", signing_key)
        
        message = b"test message"
        signature_hex = identity.sign(message)
        
        # Verify signature
        identity.verify_key.verify(message, bytes.fromhex(signature_hex))
        # If no exception, signature valid ✓
    
    def test_fingerprint_deterministic(self):
        """Verify fingerprint is deterministic for same key"""
        signing_key = nacl.signing.SigningKey.generate()
        identity1 = ComponentIdentity("test", signing_key)
        identity2 = ComponentIdentity("test", signing_key)
        
        assert identity1.fingerprint == identity2.fingerprint


class TestIdentityAssignment:
    """Test identity assignment with attack detection"""
    
    def test_assignment_idempotent(self):
        """Verify assign_identity is idempotent"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        original_fp = perception.identity.fingerprint
        
        # Try to assign new identity
        new_signing_key = nacl.signing.SigningKey.generate()
        new_identity = ComponentIdentity("perception", new_signing_key)
        
        # Should raise SecurityError (identity re-assignment attack)
        with pytest.raises(SecurityError, match="Identity re-assignment attack"):
            perception.assign_identity(new_identity)
        
        # Original identity unchanged
        assert perception.identity.fingerprint == original_fp
    
    def test_identity_not_assigned_error(self):
        """Verify RuntimeError when accessing identity before assignment"""
        
        class TestComponent(IdentityBoundComponent):
            def _on_identity_assigned(self):
                pass
            
            def get_state_hash(self):
                return "hash"
        
        component = TestComponent()
        
        with pytest.raises(RuntimeError, match="identity not assigned"):
            _ = component.identity


class TestStateNonce:
    """Test state nonce tracking"""
    
    def test_state_nonce_increments(self):
        """Verify _increment_state() increases nonce"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        nonce_before = perception._state_nonce
        
        # Process input (should increment nonce)
        perception.process("test input")
        
        nonce_after = perception._state_nonce
        
        assert nonce_after == nonce_before + 1
    
    def test_state_hash_includes_nonce(self):
        """Verify state hash changes when nonce changes"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        hash1 = perception.get_state_hash()
        
        # Increment state
        perception._increment_state()
        
        hash2 = perception.get_state_hash()
        
        assert hash1 != hash2, "State hash must change when nonce increments"
    
    def test_reasoning_state_nonce(self):
        """Verify ReasoningEngine increments nonce on reason()"""
        handshake = HandshakeProtocol()
        reasoning = ReasoningEngine(handshake)
        
        nonce_before = reasoning._state_nonce
        
        # Mock situation for reasoning
        situation = {
            'data': [{
                'situation_vector': [0.5] * 5,
                'action': 'listen_and_empathize',
                'ethical_score': 0.8
            }]
        }
        
        reasoning.reason(situation, "test input", {})
        
        nonce_after = reasoning._state_nonce
        
        assert nonce_after > nonce_before


class TestSignedMessage:
    """Test SignedMessage with real Ed25519 signatures"""
    
    def test_message_creation(self):
        """Verify SignedMessage.create() signs correctly"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("sender", signing_key)
        
        message = SignedMessage.create(
            payload={"data": "test"},
            sender_identity=identity,
            receiver_fp="receiver123",
            state_nonce=5
        )
        
        assert message.sender_fp == identity.fingerprint
        assert message.receiver_fp == "receiver123"
        assert message.state_nonce == 5
        assert len(message.signature) == 128  # 64 bytes hex = 128 chars
    
    def test_message_verification(self):
        """Verify SignedMessage.verify() works with real Ed25519"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("sender", signing_key)
        
        message = SignedMessage.create(
            payload={"data": "test"},
            sender_identity=identity,
            receiver_fp="receiver123",
            state_nonce=5
        )
        
        # Verify with sender's verify key
        assert message.verify(identity.verify_key) is True
    
    def test_message_tampering_detected(self):
        """Verify tampering is detected"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("sender", signing_key)
        
        message = SignedMessage.create(
            payload={"data": "original"},
            sender_identity=identity,
            receiver_fp="receiver123",
            state_nonce=5
        )
        
        # Tamper with payload
        message.payload["data"] = "tampered"
        
        # Verification should fail
        assert message.verify(identity.verify_key) is False
    
    def test_provenance_entry(self):
        """Verify get_provenance_entry() includes all fields"""
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity("sender", signing_key)
        
        message = SignedMessage.create(
            payload={"data": "test"},
            sender_identity=identity,
            receiver_fp="receiver123",
            state_nonce=7
        )
        
        provenance = message.get_provenance_entry()
        
        assert "sender" in provenance
        assert "receiver" in provenance
        assert "payload_hash" in provenance
        assert "signature" in provenance
        assert "state_nonce" in provenance
        assert provenance["state_nonce"] == "7"


class TestComponentIntegration:
    """Test component signing and verification"""
    
    def test_component_sign_message(self):
        """Verify component can sign messages"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        message = perception.sign_message(
            payload={"tone": "stressed", "intent": "support"},
            receiver_fp="memory_fp_abc"
        )
        
        assert isinstance(message, SignedMessage)
        assert message.sender_fp == perception.identity.fingerprint
        assert message.state_nonce == perception._state_nonce
    
    def test_component_verify_message(self):
        """Verify component can verify received messages"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        reasoning = ReasoningEngine(handshake)
        
        # Perception sends message
        message = perception.sign_message(
            payload={"data": "perception_result"},
            receiver_fp=reasoning.identity.fingerprint
        )
        
        # Reasoning verifies (needs sender's verify key)
        # In production, HandshakeProtocol would provide this
        assert message.verify(perception.identity.verify_key) is True


class TestProtocolCompliance:
    """Test verify_component_contract()"""
    
    def test_perception_compliant(self):
        """Verify PerceptionSystem implements protocol correctly"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        assert isinstance(perception, IdentityBoundComponent)
        assert verify_component_contract(perception)
    
    def test_reasoning_compliant(self):
        """Verify ReasoningEngine implements protocol correctly"""
        handshake = HandshakeProtocol()
        reasoning = ReasoningEngine(handshake)
        
        assert isinstance(reasoning, IdentityBoundComponent)
        assert verify_component_contract(reasoning)


class TestDeterministicHashing:
    """Test deterministic state hashing"""
    
    def test_perception_deterministic(self):
        """Verify PerceptionSystem hash deterministic with same state"""
        handshake1 = HandshakeProtocol()
        handshake2 = HandshakeProtocol()
        
        perception1 = PerceptionSystem(handshake1)
        perception2 = PerceptionSystem(handshake2)
        
        # Reset nonces to same value
        perception1._state_nonce = 0
        perception2._state_nonce = 0
        
        hash1 = perception1.get_state_hash()
        hash2 = perception2.get_state_hash()
        
        assert hash1 == hash2
    
    def test_hash_excludes_timestamp(self):
        """Verify hash doesn't include timestamps"""
        handshake = HandshakeProtocol()
        perception = PerceptionSystem(handshake)
        
        hash1 = perception.get_state_hash()
        time.sleep(0.01)
        hash2 = perception.get_state_hash()
        
        assert hash1 == hash2  # Should be identical despite time passing


def run_all_tests():
    """Run all unified protocol tests"""
    print("=" * 70)
    print("Running Unified Protocol Verification Tests")
    print("PyNaCl + State Nonce + SignedMessage")
    print("=" * 70)
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])


if __name__ == "__main__":
    run_all_tests()
