"""
Audit and Transparency Layer
Logging and explanation generation
"""

from typing import Dict, Any, List
import logging
import json
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class AuditLogger:
    """Comprehensive interaction auditing"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "audit.jsonl"
    
    def log_interaction(self, interaction_data: Dict[str, Any]):
        """Log a complete interaction"""
        entry = {
            "timestamp": time.time(),
            **interaction_data
        }
        
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_error(self, error: Exception, interaction_id: int):
        """Log an error"""
        logger.error(f"Error in interaction {interaction_id}: {error}")
        self.log_interaction({
            "type": "error",
            "interaction_id": interaction_id,
            "error": str(error),
            "error_type": type(error).__name__
        })

class ExplanationGenerator:
    """Generates human-readable explanations"""
    
    def __init__(self):
        pass
    
    def explain_decision(self, decision: Dict[str, Any]) -> str:
        """Generate explanation for a decision"""
        confidence = decision.get("confidence", 0)
        basis = decision.get("philosophical_basis", "unknown")
        
        explanation = f"Decision made with {confidence:.0%} confidence"
        if basis:
            explanation += f", grounded in {basis}"
        
        return explanation
    
    def explain_refusal(self, refusal_type: str, basis: str) -> str:
        """Explain why an action was refused"""
        return f"Action refused ({refusal_type}) based on {basis}"
