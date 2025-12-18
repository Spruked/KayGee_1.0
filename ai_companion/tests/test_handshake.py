"""Unit tests for PAVC handshake protocol"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.handshake.manager import HandshakeProtocol, ComponentIdentity, Transaction, SecurityError


class TestComponentIdentity:
    """Test cryptographic identity creation"""
    
    def test_identity_creation(self):
        identity = ComponentIdentity("test_component")
        assert identity.name == "test_component"
        assert identity.public_key_hex is not None
        assert len(identity.public_key_hex) > 0
    
    def test_signing(self):
        identity = ComponentIdentity("test")
        data = b"test data"
        signature = identity.sign(data)
        assert signature is not None
        assert len(signature) > 0


class TestTransaction:
    """Test transaction creation"""
    
    def test_transaction_creation(self):
        tx = Transaction("component_a", "component_b", {"test": "data"})
        assert tx.from_component == "component_a"
        assert tx.to_component == "component_b"
        assert tx.data_hash is not None
        assert tx.nonce > 0
    
    def test_transaction_serialization(self):
        tx = Transaction("a", "b", {"key": "value"})
        tx_dict = tx.to_dict()
        assert "tx_id" in tx_dict
        assert "data_hash" in tx_dict
        assert tx_dict["from"] == "a"
        assert tx_dict["to"] == "b"


class TestHandshakeProtocol:
    """Test PAVC handshake protocol"""
    
    def test_protocol_initialization(self):
        protocol = HandshakeProtocol()
        assert protocol.timeout == 0.5
        assert len(protocol.components) == 0
    
    def test_component_registration(self):
        protocol = HandshakeProtocol()
        identity = protocol.create_identity("test_comp")
        
        assert "test_comp" in protocol.components
        assert "test_comp" in protocol.public_keys
        assert "test_comp" in protocol.state_hashes
    
    def test_successful_handshake(self):
        protocol = HandshakeProtocol()
        protocol.create_identity("comp_a")
        protocol.create_identity("comp_b")
        
        result = protocol.send("comp_a", "comp_b", {"test": "data"})
        
        assert result["status"] == "COMMITTED"
        assert result["data"] == {"test": "data"}
        assert "tx_id" in result
    
    def test_state_hash_update(self):
        protocol = HandshakeProtocol()
        protocol.create_identity("comp")
        
        initial_hash = protocol.get_state_hash("comp")
        
        # Send transaction
        protocol.send("comp", "comp", {"data": "test"})
        
        new_hash = protocol.get_state_hash("comp")
        
        # State should have changed
        assert initial_hash != new_hash
    
    def test_drift_detection(self):
        protocol = HandshakeProtocol()
        protocol.create_identity("comp")
        
        correct_hash = protocol.get_state_hash("comp")
        
        # Verify with correct hash
        assert protocol.verify_no_drift("comp", correct_hash) is True
        
        # Verify with wrong hash
        assert protocol.verify_no_drift("comp", "wrong_hash") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
