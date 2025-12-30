"""
Perception Module
Handles perception and classification
"""

import hashlib
import json
from typing import Dict, Any
from src.core.layers import PerceptionLayer
from src.perception.classifier import PerceptionSystem


class PerceptionManager(PerceptionLayer):
    """
    Manages perception and intent classification
    """

    def __init__(self):
        super().__init__("PerceptionManager")
        self.system = None

    def _on_identity_assigned(self):
        """Hook called after identity assignment"""
        print(f"✓ PerceptionManager identity assigned: {self.identity.fingerprint}")

    def get_state_hash(self) -> str:
        """Compute deterministic SHA-256 hash of internal state"""
        state = {
            "version": "1.0.0",
            "state_nonce": self._state_nonce,
            "initialized": self._initialized,
            "system_available": self.system is not None
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()

    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            handshake_protocol = config.get("handshake_protocol") if config else None
            self.system = PerceptionSystem(handshake_protocol=handshake_protocol)
            self._initialized = True
            self._increment_state()
            return True
        except Exception as e:
            print(f"Failed to initialize perception: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        classifier_trained = False
        if self.system:
            is_trained_method = getattr(self.system, "is_trained", None)
            if callable(is_trained_method):
                try:
                    classifier_trained = is_trained_method()
                except Exception:
                    classifier_trained = False
        return {
            "perception_initialized": self._initialized,
            "classifier_trained": classifier_trained,
        }

    def shutdown(self) -> None:
        print("PerceptionManager shutting down...")

    def perceive(self, input_data: Any) -> Dict[str, Any]:
        if not self._initialized:
            return {"error": "Perception not initialized"}
        if not self.system:
            return {"error": "PerceptionSystem is not properly initialized"}
        process_input = getattr(self.system, "process_input", None)
        if not callable(process_input):
            return {"error": "PerceptionSystem missing or does not implement 'process_input' method"}
        try:
            result = process_input(input_data)
            if isinstance(result, dict):
                return result
            else:
                return {"error": "process_input did not return a dictionary"}
        except Exception as e:
            return {"error": str(e)}

    def classify_intent(self, text: str) -> str:
        if not self._initialized:
            return "unknown"

        try:
            return self.system.classify_intent(text)
        except Exception as e:
            return "error"
