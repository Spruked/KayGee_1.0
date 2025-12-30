"""
Articulation Module
Handles natural language generation and personality tuning
"""

import hashlib
import json
from typing import Dict, Any
from src.core.layers import ArticulationLayer
from src.articulation.nlg import ArticulationEngine, PersonalityTuner


class ArticulationManager(ArticulationLayer):
    """
    Manages articulation and NLG
    """

    def __init__(self):
        super().__init__("ArticulationManager")
        self.engine = None
        self.tuner = None

    def _on_identity_assigned(self):
        """Hook called after identity assignment"""
        print(f"✓ ArticulationManager identity assigned: {self.identity.fingerprint}")

    def get_state_hash(self) -> str:
        """Compute deterministic SHA-256 hash of internal state"""
        state = {
            "version": "1.0.0",
            "state_nonce": self._state_nonce,
            "initialized": self._initialized,
            "current_personality": self.tuner.current_personality if self.tuner else "default"
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()

    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            handshake_protocol = config.get("handshake_protocol")
            self.engine = ArticulationEngine(handshake_protocol)
            self.tuner = PersonalityTuner()
            self._initialized = True
            self._increment_state()
            return True
        except Exception as e:
            print(f"Failed to initialize articulation: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "articulation_initialized": self._initialized,
            "current_personality": self.tuner.current_personality if self.tuner else "default",
        }

    def shutdown(self) -> None:
        print("ArticulationManager shutting down...")

    def articulate(self, reasoning_result: Dict[str, Any]) -> str:
        if not self._initialized:
            return "System not ready for articulation."

        try:
            # Convert reasoning result to decision format expected by ArticulationEngine
            decision = {
                'action': reasoning_result.get('action', 'respond'),
                'ethical_score': reasoning_result.get('ethical_score', 0.5),
                'winning_philosopher': reasoning_result.get('philosopher', 'hume'),
                'breakdown': reasoning_result.get('breakdown', {})
            }
            response = self.engine.generate(decision)
            return response.get('text', 'I need a moment to think about that.')
        except Exception as e:
            return f"Articulation error: {str(e)}"

    def tune_personality(self, philosopher: str) -> None:
        if not self._initialized:
            return

        try:
            self.tuner.set_personality(philosopher)
        except Exception as e:
            print(f"Failed to tune personality: {e}")
