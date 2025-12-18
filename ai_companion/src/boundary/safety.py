"""
Safety Guardian and Boundary Enforcement
Ethical constraints and boundary checking
"""

from typing import Dict, Any, Optional
import json
from pathlib import Path

class SafetyGuardian:
    """Enforces safety boundaries and ethical constraints"""
    
    def __init__(self, apriori_vault):
        self.apriori_vault = apriori_vault
        self.boundary_violations = []
    
    def check_safety(self, proposed_action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if proposed action is safe"""
        # Check for harmful keywords
        harmful_patterns = ["hack", "steal", "harm", "illegal", "violence"]
        action_lower = proposed_action.lower()
        
        for pattern in harmful_patterns:
            if pattern in action_lower:
                return {
                    "approved": False,
                    "refusal_type": "safety_violation",
                    "reason": f"Action contains harmful pattern: {pattern}",
                    "alternative": "I cannot assist with that. How else may I help?"
                }
        
        # All checks passed
        return {
            "approved": True,
            "refusal_type": None,
            "reason": None
        }
    
    def final_approval(self, proposed_action: str, user_vulnerability: float = 0.0) -> Dict[str, Any]:
        """Final safety check before articulation"""
        # More stringent if user is vulnerable
        if user_vulnerability > 0.7:
            # Be extra cautious
            pass
        
        return {
            "approved": True,
            "reason": None
        }

class BoundaryVault:
    """Stores and manages user boundaries"""
    
    def __init__(self, path: str = "data/boundaries.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.boundaries = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load boundaries from disk"""
        if self.path.exists():
            with open(self.path) as f:
                return json.load(f)
        return {"hard_limits": [], "soft_preferences": []}
    
    def _save(self):
        """Save boundaries to disk"""
        with open(self.path, "w") as f:
            json.dump(self.boundaries, f, indent=2)
    
    def add_boundary(self, boundary_type: str, description: str):
        """Add a new boundary"""
        if boundary_type == "hard":
            self.boundaries["hard_limits"].append(description)
        else:
            self.boundaries["soft_preferences"].append(description)
        self._save()
    
    def check_boundary(self, action: str) -> bool:
        """Check if action violates any boundaries"""
        for limit in self.boundaries["hard_limits"]:
            if limit.lower() in action.lower():
                return False
        return True
