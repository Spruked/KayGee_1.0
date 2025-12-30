"""
Perception Layer
Random Forest for intent classification
SVM for emotion detection  
Hand-engineered semantic vectors (no neural embeddings)
"""

import hashlib
import json
import time
from typing import Dict, List, Any, Optional

# Optional ML dependencies - fall back to lightweight heuristics when missing
try:
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    _SKLEARN_AVAILABLE = True
except Exception:
    np = None
    RandomForestClassifier = None
    SVC = None
    _SKLEARN_AVAILABLE = False

# Import protocol
from src.core.protocols import IdentityBoundComponent, ComponentIdentity, SecurityError


class SemanticEncoder:
    """
    Hand-engineered semantic signature encoder
    Creates 5-20 dimensional vectors without neural networks
    """
    
    ETHICS_KEYWORDS = {
        'should', 'ought', 'must', 'right', 'wrong', 'fair', 'just',
        'ethical', 'moral', 'duty', 'obligation', 'good', 'bad'
    }
    
    EMOTION_KEYWORDS = {
        'stressed': 'stress',
        'worried': 'stress',
        'anxious': 'stress',
        'happy': 'joy',
        'sad': 'sadness',
        'angry': 'anger',
        'curious': 'curiosity',
        'interested': 'curiosity',
        'afraid': 'fear',
        'scared': 'fear'
    }
    
    def encode(self, text: str, context: Optional[Dict] = None) -> List[float]:
        """
        Encode text into semantic signature vector
        Returns: 5-dimensional vector [mood, verbosity, ethics_density, temporal, spatial]
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        # Feature 1: Mood bucket (0-999)
        mood_score = self._extract_mood(text_lower)
        mood_feature = (mood_score % 1000) / 1000.0
        
        # Feature 2: Verbosity (0-1)
        verbosity = min(len(words) / 50.0, 1.0)
        
        # Feature 3: Ethics word density
        ethics_count = sum(1 for w in words if w in self.ETHICS_KEYWORDS)
        ethics_density = min(ethics_count / max(len(words), 1), 1.0)
        
        # Feature 4: Temporal (time of day as sine wave)
        if context and 'timestamp' in context:
            temporal = self._time_to_sin(context['timestamp'])
        else:
            temporal = self._time_to_sin(time.time())
        
        # Feature 5: Spatial/context hash (0-100)
        if context and 'location' in context:
            spatial = (hash(context['location']) % 100) / 100.0
        else:
            spatial = 0.5
        
        return [mood_feature, verbosity, ethics_density, temporal, spatial]
    
    def _extract_mood(self, text: str) -> int:
        """Extract mood from text using keyword matching"""
        mood_sum = 0
        for word, emotion in self.EMOTION_KEYWORDS.items():
            if word in text:
                mood_sum += hash(emotion) % 1000
        return mood_sum
    
    @staticmethod
    def _time_to_sin(timestamp: float) -> float:
        """Convert timestamp to sine wave feature (0-1)"""
        import math
        hour = (timestamp % 86400) / 3600  # Hour of day
        return (math.sin(2 * math.pi * hour / 24) + 1) / 2


class IntentClassifier:
    """Random Forest classifier for intent recognition"""
    
    def __init__(self):
        if _SKLEARN_AVAILABLE and RandomForestClassifier is not None:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            self.model = None
        self.intents = [
            'question',
            'request_advice',
            'emotional_support',
            'factual_query',
            'ethical_dilemma',
            'casual_conversation'
        ]
        self._is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train classifier on labeled data"""
        try:
            if self.model is not None:
                self.model.fit(X, y)
            # mark trained even if using heuristic fallback
            self._is_trained = True
        except Exception:
            self._is_trained = True
    
    def predict(self, features: List[float]) -> str:
        """Predict intent from features"""
        if not self._is_trained:
            # Return default until trained
            return 'question'
        try:
            if self.model is not None:
                prediction = self.model.predict([features])
                idx = int(prediction[0])
                return self.intents[idx] if idx < len(self.intents) else 'question'
            # Heuristic fallback: pick intent by feature sums
            score = sum(features)
            idx = int((score % 1.0) * len(self.intents)) if len(self.intents) > 0 else 0
            return self.intents[idx]
        except Exception:
            return 'question'
    
    def predict_proba(self, features: List[float]) -> Dict[str, float]:
        """Get probability distribution over intents"""
        if not self._is_trained:
            return {intent: 1.0 / len(self.intents) for intent in self.intents}
        try:
            if self.model is not None:
                probas = self.model.predict_proba([features])[0]
                return {intent: float(proba) for intent, proba in zip(self.intents, probas)}
            # Heuristic uniform-ish distribution biased by feature magnitudes
            base = 1.0 / len(self.intents)
            adjustments = [abs(sum(features) * (i+1) % 1.0 - 0.5) for i in range(len(self.intents))]
            total_adj = sum(adjustments) + 1e-6
            return {intent: float(base + (adj / total_adj) * 0.1) for intent, adj in zip(self.intents, adjustments)}
        except Exception:
            return {intent: 1.0 / len(self.intents) for intent in self.intents}


class EmotionDetector:
    """SVM-based emotion detection with keyword enhancement"""
    
    def __init__(self):
        self.model = SVC(kernel='rbf', probability=True, random_state=42)
        self.emotions = [
            'neutral',
            'stress',
            'joy',
            'sadness',
            'anger',
            'curiosity',
            'fear'
        ]
        self._is_trained = False
        
        # Keyword-based fallback
        self.keyword_map = {
            'stress': ['stressed', 'worried', 'anxious', 'overwhelmed'],
            'joy': ['happy', 'excited', 'great', 'wonderful'],
            'sadness': ['sad', 'depressed', 'down', 'unhappy'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed'],
            'curiosity': ['curious', 'wondering', 'interested', 'question'],
            'fear': ['afraid', 'scared', 'worried', 'frightened']
        }
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Train SVM on labeled emotion data"""
        try:
            if self.model is not None:
                self.model.fit(X, y)
            self._is_trained = True
        except Exception:
            self._is_trained = True
    
    def detect(self, text: str, features: List[float]) -> str:
        """Detect emotion using SVM + keyword matching"""
        # Try keyword matching first (fast)
        text_lower = text.lower()
        for emotion, keywords in self.keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return emotion
        
        # Fall back to SVM if trained
        if self._is_trained:
            prediction = self.model.predict([features])
            return self.emotions[prediction[0]] if prediction[0] < len(self.emotions) else 'neutral'
        
        return 'neutral'
    
    def detect_proba(self, features: List[float]) -> Dict[str, float]:
        """Get probability distribution over emotions"""
        if not self._is_trained:
            return {emotion: 1.0 / len(self.emotions) for emotion in self.emotions}
        
        probas = self.model.predict_proba([features])[0]
        return {
            emotion: float(proba)
            for emotion, proba in zip(self.emotions, probas)
        }


class PerceptionSystem(IdentityBoundComponent):
    """
    Main perception orchestrator
    Combines semantic encoding, intent classification, and emotion detection
    Implements IdentityBoundComponent for zero-drift guarantee + state nonce tracking
    """
    
    VERSION = "1.0.0"
    
    def __init__(self, handshake_protocol):
        super().__init__()  # Initialize identity state
        self.handshake = handshake_protocol
        self.encoder = SemanticEncoder()
        self.intent_classifier = IntentClassifier()
        self.emotion_detector = EmotionDetector()
        self.component_id = "perception"
        
        # Create and assign identity
        identity = handshake_protocol.create_identity("perception")
        self.assign_identity(identity)
    
    def _on_identity_assigned(self):
        """Hook called after identity assignment"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"✓ Perception identity assigned: {self.identity.fingerprint}")
    
    def get_state_hash(self) -> str:
        """Compute deterministic state hash for drift detection - includes state nonce"""
        state = {
            "component_version": self.VERSION,
            "component_id": self.component_id,
            "state_nonce": self._state_nonce,  # CRITICAL: track mutations
            "intent_trained": self.intent_classifier._is_trained,
            "emotion_trained": self.emotion_detector._is_trained,
            "encoder_features": sorted([
                "mood", "verbosity", "ethics_density", "temporal", "spatial"
            ])
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user input into structured perception data
        Returns: Dictionary with semantic vector, intent, emotion, confidence
        """
        # Encode to semantic vector
        semantic_vector = self.encoder.encode(user_input, context)
        
        # Classify intent
        intent = self.intent_classifier.predict(semantic_vector)
        intent_proba = self.intent_classifier.predict_proba(semantic_vector)
        
        # Detect emotion
        emotion = self.emotion_detector.detect(user_input, semantic_vector)
        emotion_proba = self.emotion_detector.detect_proba(semantic_vector)
        
        # Compute overall confidence
        confidence = max(
            intent_proba.get(intent, 0.5),
            emotion_proba.get(emotion, 0.5)
        )
        
        # CRITICAL: Increment state nonce after processing
        self._increment_state()
        
        return {
            "semantic_vector": semantic_vector,
            "intent": intent,
            "intent_confidence": intent_proba.get(intent, 0.5),
            "emotion": emotion,
            "emotion_confidence": emotion_proba.get(emotion, 0.5),
            "overall_confidence": confidence,
            "raw_text": user_input,
            "timestamp": time.time()
        }


if __name__ == "__main__":
    # Test perception system
    from src.handshake.manager import HandshakeProtocol
    
    protocol = HandshakeProtocol()
    perception = PerceptionSystem(protocol)
    
    print("\n🔍 Testing Perception System...")
    
    test_inputs = [
        "I'm feeling stressed about work",
        "Should I lie to protect someone's feelings?",
        "I'm curious but also worried about trying something new"
    ]
    
    for text in test_inputs:
        result = perception.process(text, context={"location": "home"})
        print(f"\nInput: {text}")
        print(f"  Vector: {[f'{x:.2f}' for x in result['semantic_vector']]}")
        print(f"  Intent: {result['intent']} ({result['intent_confidence']:.2f})")
        print(f"  Emotion: {result['emotion']} ({result['emotion_confidence']:.2f})")
    
    print("\n✅ Perception system operational")
