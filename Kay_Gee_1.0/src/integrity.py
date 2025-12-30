"""
Integrity Module
Handles integrity checks and safety boundaries
"""

import hashlib
import json
from typing import Dict, Any
from src.core.layers import IntegrityLayer
from src.boundary.safety import SafetyGuardian, BoundaryVault
from src.audit.transparency import AuditLogger


class IntegrityManager(IntegrityLayer):
    """
    Manages integrity and safety
    """

    def __init__(self):
        super().__init__("IntegrityManager")
        self.guardian = None
        self.boundary_vault = None
        self.audit_logger = None

    def _on_identity_assigned(self):
        """Hook called after identity assignment"""
        print(f"✓ IntegrityManager identity assigned: {self.identity.fingerprint}")

    def get_state_hash(self) -> str:
        """Compute deterministic SHA-256 hash of internal state"""
        state = {
            "version": "1.0.0",
            "state_nonce": self._state_nonce,
            "initialized": self._initialized,
            "boundaries_count": len(self.boundary_vault.boundaries) if self.boundary_vault else 0,
            "audit_entries_count": len(self.audit_logger.entries) if self.audit_logger else 0
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()

    def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            self.guardian = SafetyGuardian()
            self.boundary_vault = BoundaryVault()
            self.audit_logger = AuditLogger()
            self._initialized = True
            self._increment_state()
            return True
        except Exception as e:
            print(f"Failed to initialize integrity: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "integrity_initialized": self._initialized,
            "boundaries_active": len(self.boundary_vault.boundaries) if self.boundary_vault else 0,
            "audit_entries": len(self.audit_logger.entries) if self.audit_logger else 0,
        }

    def shutdown(self) -> None:
        print("IntegrityManager shutting down...")

    def check_integrity(self) -> Dict[str, Any]:
        if not self._initialized:
            return {"error": "Integrity not initialized"}

        try:
            return self.guardian.perform_integrity_check()
        except Exception as e:
            return {"error": str(e)}

    def enforce_boundaries(self, action: str) -> bool:
        if not self._initialized:
            return False

        try:
            return self.guardian.check_boundary(action)
        except Exception as e:
            return False
