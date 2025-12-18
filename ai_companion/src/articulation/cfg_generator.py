"""
Advanced Natural Language Generation
Context-free grammar + Personalization Lexicon (still symbolic, no LLM)
"""

from typing import Dict, Any


class NLG_Engine:
    def __init__(self, user_lexicon: dict = None):
        # Grammar rules that include placeholders for personalization
        self.grammar = {
            "POLITE_OPENING": ["I understand you're", "I hear you're", "I sense you're"],
            "EMOTION_STATE": ["stressed", "concerned", "uncertain", "worried"],
            "JUSTIFICATION": ["because {reason}, I suggest {action}"],
            "REASON": [
                "it respects your autonomy",
                "it promotes well-being",
                "it aligns with your values",
                "it has worked well before"
            ],
            "POLITE_CLOSING": ["Does that feel right?", "What do you think?", "Does this help?"]
        }
        
        # User-specific synonyms ("stressed" → "overwhelmed")
        self.lexicon = user_lexicon or {}
    
    def generate(self, action: str, reasoning_trace: dict, user_mood: str):
        # Select grammar rule based on philosophical grounding
        philosopher = reasoning_trace.get('dominant_philosopher', 'hume')
        
        if philosopher == 'kant' or 'kantian' in philosopher:
            justification = "it respects your autonomy"
        elif philosopher == 'hume' or 'humean' in philosopher:
            justification = "it will make you feel better"
        elif philosopher == 'locke' or 'lockean' in philosopher:
            justification = "it preserves your freedom"
        elif philosopher == 'spinoza' or 'spinozan' in philosopher:
            justification = "it increases your rational capacity"
        else:
            justification = "it seems appropriate"
        
        # Fill template with user-specific words
        emotion = self.lexicon.get(user_mood, user_mood)
        
        # Select opening randomly
        import random
        opening = random.choice(self.grammar["POLITE_OPENING"])
        closing = random.choice(self.grammar["POLITE_CLOSING"])
        
        sentence = f"{opening} {emotion}. Because {justification}, I suggest {action.replace('_', ' ')}. {closing}"
        
        # Apply prosody based on confidence
        confidence = reasoning_trace.get('confidence', 0.7)
        
        return {
            "text": sentence,
            "prosody": {
                "pitch": "high" if confidence < 0.6 else "normal",
                "rate": "slow" if emotion in ["stressed", "overwhelmed", "anxious"] else "medium",
                "volume": "medium"
            }
        }
