"""
Meta-Cognitive Monitor
System self-awareness and uncertainty tracking
"""

from typing import Dict, Any, List

class MetaCognitiveMonitor:
    """Monitors system reasoning quality and flags concerns"""
    
    def __init__(self):
        self.concerns = []
        self.uncertainty_log = []
    
    def monitor(self, decision_quality: float, reasoning_path: List[str], system_load: float):
        """Monitor a decision's quality"""
        # Flag low confidence
        if decision_quality < 0.5:
            self.concerns.append({
                "type": "low_confidence",
                "value": decision_quality,
                "path": reasoning_path
            })
        
        # Flag high system load
        if system_load > 5.0:
            self.concerns.append({
                "type": "performance_degradation",
                "load": system_load
            })
    
    def has_concerns(self) -> bool:
        """Check if there are active concerns"""
        # Clear old concerns (keep last 10)
        self.concerns = self.concerns[-10:]
        return len(self.concerns) > 3
    
    def get_concerns(self) -> List[Dict[str, Any]]:
        """Get current concerns"""
        return self.concerns
