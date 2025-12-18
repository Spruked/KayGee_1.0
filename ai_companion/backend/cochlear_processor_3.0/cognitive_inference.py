import difflib
from collections import deque
from typing import Dict, List, Tuple, Optional

class CognitiveInferenceEngine:
    """
    Models human context-based error recovery and "phoneme guessing".
    """
    
    def __init__(self):
        self.context_window = deque(maxlen=50)  # Last 50 words for context
        self.confidence_threshold = 0.6  # Below this, trigger inference
        
        # Language model for gap-filling (simplified; use GPT-style in production)
        self.phoneme_prediction_model = self._load_phoneme_model()
        
    def process_with_inference(self, transcript: str, confidence_scores: List[float], 
                               perceptual_report: Dict) -> Tuple[str, List[Dict]]:
        """
        Takes low-confidence transcript, returns inferred version + correction log.
        """
        words = transcript.split()
        corrected_words = []
        corrections = []
        
        for i, (word, conf) in enumerate(zip(words, confidence_scores)):
            if conf < self.confidence_threshold:
                # "Misheard" word—let's try to correct it
                corrected_word, inference_sources = self._infer_word(word, i, words, perceptual_report)
                
                if corrected_word != word:
                    corrections.append({
                        "original": word,
                        "inferred": corrected_word,
                        "confidence_before": conf,
                        "confidence_after": self._estimate_confidence(corrected_word),
                        "sources": inference_sources,
                        "position": i
                    })
                
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
            
            # Update context window
            self.context_window.append(corrected_words[-1])
        
        return " ".join(corrected_words), corrections
    
    def _infer_word(self, misheard: str, position: int, words: List[str], 
                    perceptual_report: Dict) -> Tuple[str, Dict]:
        """
        Human-like reasoning: What word *probably* fits here?
        """
        sources = {}
        
        # 1. Phonetic similarity (sounds-like)
        phonetic_candidates = self._phonetic_neighbors(misheard)
        if phonetic_candidates:
            sources["phonetic"] = phonetic_candidates
        
        # 2. Contextual prediction (n-gram probability)
        context = " ".join(self.context_window)
        context_pred = self._contextual_prediction(context, position)
        if context_pred:
            sources["context"] = context_pred
        
        # 3. Semantic coherence (topic model)
        topic_pred = self._semantic_coherence(words)
        if topic_pred:
            sources["semantic"] = topic_pred
        
        # 4. Perceptual hint (what was *actually* heard?)
        if perceptual_report["dropouts"]:
            sources["dropout_hint"] = "missing_phonemes"
        
        # Choose best inference
        if len(sources) >= 2:
            # Cross-validate: pick word that appears in multiple sources
            inferred = self._cross_validate(sources)
        elif sources:
            # Single source: use best guess
            source_type, candidates = list(sources.items())[0]
            inferred = candidates[0] if isinstance(candidates, list) else candidates
        else:
            # No inference possible: keep original
            inferred = misheard
        
        return inferred, sources
    
    def _phonetic_neighbors(self, word: str, max_distance: int = 2) -> List[str]:
        """Words within Levenshtein distance of 2 (sounds-like)"""
        # In production: use phoneme embedding database
        common_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "I"]
        return [w for w in common_words if difflib.SequenceMatcher(None, word, w).ratio() > 0.7]
    
    def _contextual_prediction(self, context: str, position: int) -> Optional[str]:
        """Predict next word based on preceding context"""
        # Simple n-gram model
        if context.endswith("to"):
            return "be"
        elif context.endswith("I"):
            return "am"
        # Add more patterns...
        return None
    
    def _semantic_coherence(self, words: List[str]) -> Optional[str]:
        """Check topic consistency"""
        # If recent words are about technology, "AI" is more likely than "aye"
        if any(tech in words for tech in ["machine", "learning", "computer", "algorithm"]):
            if "aye" in words:
                return "AI"
        return None
    
    def _cross_validate(self, sources: Dict) -> str:
        """Pick word that appears in multiple inference sources"""
        all_candidates = []
        for candidates in sources.values():
            if isinstance(candidates, list):
                all_candidates.extend(candidates)
            else:
                all_candidates.append(candidates)
        
        # Return most frequent candidate
        from collections import Counter
        counts = Counter(all_candidates)
        return counts.most_common(1)[0][0]
    
    def _estimate_confidence(self, word: str) -> float:
        """Estimated confidence after inference (0.0-1.0)"""
        # Base confidence + bonus for multi-source validation
        base = 0.7
        return min(1.0, base + (len(self.context_window) / 50) * 0.2)
    
    def _load_phoneme_model(self):
        """Placeholder for phoneme prediction model"""
        return None