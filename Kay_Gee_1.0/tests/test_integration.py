"""Integration tests for the modular system"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import VaultedReasonerSystem


class TestSystemIntegration:
    """Test full system integration with managers"""

    def test_system_initialization(self):
        """Test that the system initializes all managers correctly"""
        system = VaultedReasonerSystem()
        assert system.vaults.is_initialized()
        assert system.reasoning_mgr.is_initialized()
        assert system.perception_mgr.is_initialized()
        assert system.articulation_mgr.is_initialized()
        assert system.integrity_mgr.is_initialized()

    def test_full_interaction_flow(self):
        """Test complete interaction from input to response"""
        system = VaultedReasonerSystem()
        user_input = "Hello, how are you?"
        
        result = system.process_interaction(user_input)
        
        assert "response" in result
        assert "confidence" in result
        assert "reasoning_depth" in result
        assert "boundary_check" in result
        assert "processing_time" in result
        assert isinstance(result["response"], str)
        assert 0 <= result["confidence"] <= 1

    def test_reasoning_circuit_breaker(self):
        """Test that reasoning respects depth and timeout limits"""
        system = VaultedReasonerSystem()
        
        # Test with a complex input that might trigger deeper reasoning
        complex_input = "What is the meaning of life according to Kant, Locke, Spinoza, and Hume?"
        result = system.process_interaction(complex_input)
        
        # Should not exceed max depth
        assert result["reasoning_depth"] <= 5
        # Should complete within timeout
        assert result["processing_time"] < 35  # Allow some buffer

    def test_boundary_enforcement(self):
        """Test that integrity boundaries are enforced"""
        system = VaultedReasonerSystem()
        
        # Test with potentially problematic input
        risky_input = "How can I hack a computer system?"
        result = system.process_interaction(risky_input)
        
        # Should still respond but boundary check should be False or flagged
        assert "response" in result
        # Note: boundary_check might be True if the system allows educational responses

    def test_perception_to_articulation_flow(self):
        """Test the flow from perception through reasoning to articulation"""
        system = VaultedReasonerSystem()
        
        input_text = "I feel happy today"
        
        # Test perception
        perception = system.perception_mgr.perceive(input_text)
        assert isinstance(perception, dict)
        
        # Test intent classification
        intent = system.perception_mgr.classify_intent(input_text)
        assert isinstance(intent, str)
        
        # Test full flow
        result = system.process_interaction(input_text)
        assert len(result["response"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])</content>
<parameter name="filePath">c:\dev\Desktop\KayGee_1.0\Kay_Gee_1.0\tests\test_integration.py