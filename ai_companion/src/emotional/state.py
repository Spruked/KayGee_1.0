"""
Emotional State Integrator
Tracks and analyzes emotional context
"""

from typing import Dict, Any

class EmotionalStateIntegrator:
    """Integrates emotional analysis into reasoning"""
    
    def __init__(self):
        self.emotional_history = []
    
    def analyze_emotion(self, perception_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze emotional content from perception"""
        # Extract emotion from perception if available
        detected_emotion = perception_data.get("emotion", "neutral")
        
        # Simple vulnerability scoring
        vulnerable_emotions = ["sad", "anxious", "distressed", "angry"]
        vulnerability = 0.7 if detected_emotion in vulnerable_emotions else 0.2
        
        emotional_state = {
            "detected_tone": detected_emotion,
            "vulnerability_level": vulnerability,
            "requires_empathy": vulnerability > 0.5
        }
        
        # Track history
        self.emotional_history.append(emotional_state)
        if len(self.emotional_history) > 100:
            self.emotional_history = self.emotional_history[-100:]
        
        return emotional_state
