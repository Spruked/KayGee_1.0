import json
import numpy as np
import time
import random
import hashlib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class VoiceSignature:
    """A specific voice configuration Caleon can use"""
    signature_id: str
    base_persona: str  # Links to SKG persona
    pitch_shift: float
    speaking_rate: float
    formant_shifts: Dict[str, float]
    breathiness: float = 0.3
    vocal_fry: float = 0.1
    nasality: float = 0.0
    reverb: Optional[Dict[str, float]] = None
    
    # Semantic tags for when to use this voice
    semantic_tags: List[str] = None
    success_score: float = 0.7  # Learned performance metric (0.0-1.0)
    usage_count: int = 0
    last_used: float = 0.0  # timestamp
    
    def __post_init__(self):
        if self.semantic_tags is None:
            self.semantic_tags = []
    
    def calculate_fitness(self, content_vector: np.ndarray, context: Dict) -> float:
        """How well this voice matches the current content"""
        
        # 1. Semantic similarity
        tag_vector = self._vectorize_tags(self.semantic_tags)
        semantic_score = np.dot(content_vector, tag_vector) / (np.linalg.norm(content_vector) * np.linalg.norm(tag_vector))
        
        # 2. Context appropriateness
        context_score = self._score_context_match(context)
        
        # 3. Historical success (weighted by recency)
        recency_weight = np.exp(-(time.time() - self.last_used) / 86400)  # Decay over 24 hours
        success_score = self.success_score * recency_weight
        
        # 4. Exploration bonus (use underutilized voices)
        exploration_bonus = 0.1 / (self.usage_count + 1)
        
        # Combined fitness
        fitness = (
            semantic_score * 0.4 + 
            context_score * 0.3 + 
            success_score * 0.2 + 
            exploration_bonus * 0.1
        )
        
        return fitness
    
    def _vectorize_tags(self, tags: List[str]) -> np.ndarray:
        """Simple word vector (in production, use embeddings)"""
        # Placeholder: use hash-based vectorization
        vector_dim = 50
        vector = np.zeros(vector_dim)
        for tag in tags:
            hash_val = int(hashlib.md5(tag.encode()).hexdigest(), 16)
            for i in range(vector_dim):
                vector[i] += (hash_val >> i) & 1
        return vector / len(tags) if tags else vector
    
    def _score_context_match(self, context: Dict) -> float:
        """Check if voice matches context constraints"""
        score = 1.0
        
        # Example: Don't use heavy reverb in "intimate" contexts
        if context.get("intimacy_level", 0.0) > 0.7 and self.reverb:
            score *= 0.6
        
        # Prefer clear voices for technical content
        if context.get("technical_density", 0.0) > 0.5 and self.nasality > 0.5:
            score *= 0.7
        
        return score

class CaleonVoiceOracle:
    """Caleon's decision-making system for voice selection"""
    
    def __init__(self, skg_path: str = "skg_caleon.json"):
        self.skg_path = skg_path
        self.voice_registry = self._load_voice_registry()
        self.content_embedding_cache = {}
        
        # Learning parameters
        self.learning_rate = 0.1
        self.exploration_rate = 0.15  # 15% chance to try random voice
        
        # Performance tracking
        self.performance_log = []
    
    def _load_voice_registry(self) -> List[VoiceSignature]:
        """Load Caleon's available voices from SKG"""
        
        try:
            with open(self.skg_path, 'r') as f:
                skg = json.load(f)
        except FileNotFoundError:
            # Create default SKG if not exists
            skg = {"caleon_voices": {}}
        
        voices = []
        for voice_id, config in skg.get("caleon_voices", {}).items():
            voice = VoiceSignature(
                signature_id=voice_id,
                base_persona=config["base_persona"],
                pitch_shift=config.get("pitch_shift", 1.0),
                speaking_rate=config.get("speaking_rate", 1.0),
                formant_shifts=config.get("formant_shifts", {}),
                breathiness=config.get("breathiness", 0.3),
                vocal_fry=config.get("vocal_fry", 0.1),
                nasality=config.get("nasality", 0.0),
                reverb=config.get("reverb"),
                semantic_tags=config.get("semantic_tags", []),
                success_score=config.get("success_score", 0.7),
                usage_count=config.get("usage_count", 0),
                last_used=config.get("last_used", 0.0)
            )
            voices.append(voice)
        
        return voices
    
    def choose_voice(self, content: str, context: Dict) -> VoiceSignature:
        """
        Caleon selects her best voice for this content
        """
        print(f"🎭 Caleon Oracle: Choosing voice for '{content[:50]}...'")
        
        # 1. Vectorize content for semantic matching
        content_vector = self._content_to_vector(content)
        
        # 2. Calculate fitness for each voice
        fitness_scores = [
            (voice, voice.calculate_fitness(content_vector, context))
            for voice in self.voice_registry
        ]
        
        # 3. Add exploration noise (epsilon-greedy)
        if random.random() < self.exploration_rate:
            # Explore: choose random but weighted toward less-used voices
            weights = [1 / (v.usage_count + 1) for v, _ in fitness_scores]
            chosen_voice = random.choices(
                [v for v, _ in fitness_scores],
                weights=weights,
                k=1
            )[0]
            print(f"   → Exploring new voice: {chosen_voice.signature_id}")
        else:
            # Exploit: choose best fitness
            chosen_voice = max(fitness_scores, key=lambda x: x[1])[0]
            print(f"   → Best fit: {chosen_voice.signature_id} (fitness: {max(f for _, f in fitness_scores):.3f})")
        
        # 4. Increment usage and update last_used
        chosen_voice.usage_count += 1
        chosen_voice.last_used = time.time()
        
        # 5. Save updated registry
        self._save_voice_registry()
        
        return chosen_voice
    
    def _content_to_vector(self, text: str) -> np.ndarray:
        """Convert text to semantic vector"""
        
        # Simple TF-IDF style vectorization
        # In production: use sentence-transformers or similar
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.content_embedding_cache:
            return self.content_embedding_cache[cache_key]
        
        # Extract keywords as proxy for semantics
        keywords = self._extract_keywords(text)
        vector = self._vectorize_tags(keywords)
        
        self.content_embedding_cache[cache_key] = vector
        return vector
    
    def _vectorize_tags(self, tags: List[str]) -> np.ndarray:
        """Simple word vector (in production, use embeddings)"""
        # Placeholder: use hash-based vectorization
        vector_dim = 50
        vector = np.zeros(vector_dim)
        for tag in tags:
            hash_val = int(hashlib.md5(tag.encode()).hexdigest(), 16)
            for i in range(vector_dim):
                vector[i] += (hash_val >> i) & 1
        return vector / len(tags) if tags else vector
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key semantic terms"""
        
        # Simple keyword extraction without spacy for now
        # Remove stopwords, keep nouns/verbs
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "shall"}
        words = text.lower().split()
        keywords = [
            word for word in words
            if len(word) > 3 and word not in stopwords
        ]
        
        return keywords[:20]  # Top 20
    
    def receive_feedback(self, voice_id: str, content_hash: str, performance_score: float, listener_feedback: Optional[Dict] = None):
        """
        Caleon learns from performance
        performance_score: 0.0-1.0 (how well the voice worked)
        listener_feedback: Optional metadata from UCM/Analytics
        """
        
        voice = next((v for v in self.voice_registry if v.signature_id == voice_id), None)
        if not voice:
            return
        
        # Calculate reward
        reward = performance_score
        
        # Adjust based on listener retention (if available)
        if listener_feedback:
            retention = listener_feedback.get("retention_rate", 0.7)
            engagement = listener_feedback.get("engagement_score", 0.6)
            reward = (reward + retention + engagement) / 3
        
        # Update success score (moving average)
        voice.success_score = (voice.success_score * 0.9) + (reward * 0.1)
        
        # Log for pattern analysis
        self.performance_log.append({
            "voice_id": voice_id,
            "content_hash": content_hash,
            "reward": reward,
            "timestamp": time.time(),
            "semantic_tags": voice.semantic_tags
        })
        
        # Update semantic tags based on successful content
        if reward > 0.8:
            self._reinforce_semantic_tags(voice, content_hash)
        elif reward < 0.3:
            self._punish_semantic_tags(voice, content_hash)
        
        print(f"📊 Caleon learned: {voice_id} → success_score: {voice.success_score:.3f}")
        
        self._save_voice_registry()
    
    def _reinforce_semantic_tags(self, voice: VoiceSignature, content_hash: str):
        """Add relevant tags from successful content"""
        
        # In production: analyze content_hash to extract new tags
        # For now: slightly increase usage count bias
        voice.usage_count = max(0, voice.usage_count - 1)  # Make it more likely to be chosen
    
    def _punish_semantic_tags(self, voice: VoiceSignature, content_hash: str):
        """Reduce fitness for similar future content"""
        
        # Increase usage count (making it less likely to be explored)
        voice.usage_count += 2
    
    def _save_voice_registry(self):
        """Persist learned weights back to SKG"""
        
        try:
            with open(self.skg_path, 'r') as f:
                skg = json.load(f)
        except FileNotFoundError:
            skg = {}
        
        skg["caleon_voices"] = {
            voice.signature_id: {
                **asdict(voice),
                "semantic_tags": list(voice.semantic_tags) if voice.semantic_tags else []
            }
            for voice in self.voice_registry
        }
        
        with open(self.skg_path, 'w') as f:
            json.dump(skg, f, indent=2)
    
    def generate_new_voice_signature(self, from_content: str, performance_hint: float) -> str:
        """
        Caleon creates a new voice signature based on novel content
        This is autonomous voice evolution
        """
        
        print(f"🔬 Caleon evolving: Creating new voice from content pattern")
        
        # 1. Analyze content for unique features
        content_analysis = self._analyze_content_signature(from_content)
        
        # 2. Derive voice parameters from content
        new_voice_config = self._derive_voice_from_content(content_analysis, performance_hint)
        
        # 3. Create unique ID
        voice_id = f"c_{hashlib.md5(from_content.encode()).hexdigest()[:8]}"
        
        # 4. Add to registry
        new_voice = VoiceSignature(
            signature_id=voice_id,
            base_persona="caleon_base",
            **new_voice_config
        )
        
        self.voice_registry.append(new_voice)
        self._save_voice_registry()
        
        print(f"   → New voice created: {voice_id}")
        print(f"   → Semantic tags: {new_voice.semantic_tags}")
        
        return voice_id
    
    def _analyze_content_signature(self, text: str) -> Dict:
        """Extract content's 'voice fingerprint'"""
        
        # Analyze lexical density, sentiment, complexity
        words = text.split()
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        # Sentiment (simplified)
        positive_words = ["good", "great", "amazing", "wonderful", "love"]
        negative_words = ["bad", "terrible", "awful", "hate", "sad"]
        sentiment = sum(1 for w in words if w.lower() in positive_words) - sum(1 for w in words if w.lower() in negative_words)
        
        # Complexity (unique words / total words)
        unique_ratio = len(set(words)) / len(words) if words else 0
        
        return {
            "avg_word_length": avg_word_length,
            "sentiment": sentiment,
            "complexity": unique_ratio,
            "length": len(text)
        }
    
    def _derive_voice_from_content(self, analysis: Dict, hint: float) -> Dict:
        """Map content features to voice parameters"""
        
        config = {}
        
        # Sentiment → pitch
        if analysis["sentiment"] > 2:
            config["pitch_shift"] = 1.05  # Happier = slightly higher
        elif analysis["sentiment"] < -2:
            config["pitch_shift"] = 0.95  # Sadder = lower
        else:
            config["pitch_shift"] = 1.0
        
        # Complexity → speaking rate
        if analysis["complexity"] > 0.7:
            config["speaking_rate"] = 0.9  # Complex = slower
        else:
            config["speaking_rate"] = 1.0
        
        # Word length → formant shifts (longer words = rounder vowels)
        if analysis["avg_word_length"] > 6:
            config["formant_shifts"] = {"f1": 1.05, "f2": 0.95}  # More resonant
        
        # Success hint → confidence
        config["success_score"] = hint
        
        # Auto-tags from content
        config["semantic_tags"] = self._extract_keywords(str(analysis))
        
        return config