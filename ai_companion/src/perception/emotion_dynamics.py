"""
Emotional State Dynamics - Continuous Affect Modeling
Difference Equations + Emotional Inertia (symbolic dynamical system)
"""

from typing import Dict, List
from collections import deque


class EmotionModel:
    def __init__(self):
        self.state = {"valence": 0.0, "arousal": 0.0}  # 2D emotional space
        self.inertia = 0.85  # Emotional state persistence
        self.history = deque(maxlen=10)
        self.trend = "stable"
    
    def update(self, perceptual_features: dict):
        # Map features to emotional perturbation
        perturbation = {
            "valence": self.valence_from_features(perceptual_features),
            "arousal": self.arousal_from_features(perceptual_features)
        }
        
        # Update with inertia
        self.state["valence"] = (self.inertia * self.state["valence"] + 
                                 (1 - self.inertia) * perturbation["valence"])
        self.state["arousal"] = (self.inertia * self.state["arousal"] + 
                                 (1 - self.inertia) * perturbation["arousal"])
        
        # Store in history
        self.history.append(dict(self.state))
        
        # Detect emotional trends (increasing stress, improving mood)
        self.trend = self.calculate_trend()
        
        return self.state
    
    def valence_from_features(self, features):
        """Extract valence from perceptual features"""
        if features.get("user_says_negative_words", 0) > 3:
            return -0.5
        elif features.get("user_says_positive_words", 0) > 3:
            return +0.5
        
        # Use emotion if available
        emotion = features.get('emotion', 'neutral')
        emotion_valence_map = {
            'joy': 0.8,
            'neutral': 0.0,
            'stress': -0.6,
            'sadness': -0.7,
            'anger': -0.5,
            'fear': -0.6,
            'curiosity': 0.3
        }
        
        return emotion_valence_map.get(emotion, 0.0)
    
    def arousal_from_features(self, features):
        """Extract arousal from perceptual features"""
        emotion = features.get('emotion', 'neutral')
        arousal_map = {
            'joy': 0.6,
            'neutral': 0.0,
            'stress': 0.7,
            'sadness': -0.3,
            'anger': 0.8,
            'fear': 0.7,
            'curiosity': 0.5
        }
        return arousal_map.get(emotion, 0.0)
    
    def calculate_trend(self):
        """Detect trend in emotional state"""
        # Simple linear regression on last 10 states
        if len(self.history) < 3:
            return "stable"
        
        history_list = list(self.history)
        slope = (history_list[-1]["valence"] - history_list[0]["valence"]) / len(history_list)
        
        if slope > 0.05:
            return "improving"
        elif slope < -0.05:
            return "declining"
        return "stable"
    
    def get_history(self, window: int = 10) -> List[Dict]:
        """Get recent emotional history"""
        return list(self.history)[-window:]
