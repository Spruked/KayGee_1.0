import time
import numpy as np
from typing import Dict, List, Callable

class RealtimeCorrectionLoop:
    """
    Monitors synthesis output, detects low confidence, and inserts corrections.
    """
    
    def __init__(self, processor):
        self.processor = processor  # Reference to the full processor
        self.correction_buffer = []
        self.confidence_history = []
        self.callback_threshold = 0.5  # Below this, trigger correction
    
    def monitor_and_correct(self, text_stream: str, 
                          on_correction: Callable[[str, str], None],
                          simulate_realtime: bool = True):
        """
        Watches transcription confidence and triggers corrections when needed.
        """
        words = text_stream.split()
        corrected_stream = []
        
        for i, word in enumerate(words):
            # Get confidence from perceptual filter
            confidence = self._get_word_confidence(word, i)
            self.confidence_history.append(confidence)
            
            # Human-like: sometimes we *realize* we misheard
            if confidence < self.callback_threshold and self._should_correct():
                # Try to infer correct word
                perceptual_report = {
                    "dropouts": [],  # No dropouts for correction inference
                    "attention_level": self.processor.perceptual_filter.state.attention_level
                }
                corrected_word, _ = self.processor.cognitive_engine._infer_word(
                    word, i, words[:i+1], perceptual_report
                )
                
                if corrected_word != word:
                    # Insert correction in human-like way
                    correction_phrase = self._generate_correction_phrase(word, corrected_word)
                    
                    if simulate_realtime:
                        # Simulate pause before correction (human catching themselves)
                        time.sleep(0.3)
                    
                    corrected_stream.append(correction_phrase)
                    corrected_stream.append(corrected_word)
                    
                    # Notify upstream (could trigger re-synthesis)
                    on_correction(word, corrected_word)
                    
                    # Reset confidence
                    self.confidence_history.append(0.8)  # Post-correction confidence
                else:
                    corrected_stream.append(word)
            else:
                corrected_stream.append(word)
        
        return " ".join(corrected_stream)
    
    def _should_correct(self) -> bool:
        """Humans don't correct *every* mishearing—only when they notice"""
        # Probability increases with recent low confidence
        recent_confidence = np.mean(self.confidence_history[-5:])
        return np.random.random() < (1 - recent_confidence)
    
    def _generate_correction_phrase(self, wrong: str, right: str) -> str:
        """Human-like correction markers"""
        phrases = [
            f"Sorry, I meant {right}, not {wrong}.",
            f"No, wait—{right}.",
            f"Actually, {right}.",
            f"I'm hearing that as {right}.",
            f"Correction: {right}."
        ]
        return np.random.choice(phrases)
    
    def _get_word_confidence(self, word: str, position: int) -> float:
        """Simulated confidence based on perceptual state"""
        if not hasattr(self, 'perceptual_filter'):
            self.perceptual_filter = self.processor.perceptual_filter
        
        # Simulated: real confidence would come from ASR
        base_confidence = 0.7
        
        # Attention effect
        attention_factor = self.processor.perceptual_filter.state.attention_level
        
        # Dropout penalty
        dropout_penalty = 0.2 if position % 10 == 0 else 0
        
        return max(0.1, base_confidence * attention_factor - dropout_penalty)