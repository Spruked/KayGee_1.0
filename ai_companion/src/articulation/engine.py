"""
ArticulationEngine
Turns structured decisions into natural, personality-tuned language
Ready for Coqui TTS output
"""

import random
from typing import Dict, Any
from src.personality.core import PersonalityCore  # Assuming you have this

class ArticulationEngine:
    def __init__(self, personality: PersonalityCore):
        self.personality = personality
        self.templates = {
            "greeting": [
                "Hello. I'm here with you.",
                "Good to be in this moment together.",
                "I'm listening, fully."
            ],
            "response": [
                "{response}",
                "Let me say this clearly: {response}",
                "From where I stand: {response}"
            ],
            "refusal": [
                "I must decline this. {basis}",
                "I cannot go there — {basis}",
                "With respect, I have to refuse. {basis}"
            ],
            "uncertain": [
                "I'm uncertain here ({confidence:.2f}). {question}",
                "This feels ambiguous to me. {question}",
                "I want to be careful: {question}"
            ],
            "alternative": [
                "Perhaps instead: {alternative}",
                "Another path might be: {alternative}",
                "Would this serve better? {alternative}"
            ]
        }

    def generate(self, decision: Dict[str, Any]) -> Dict[str, str]:
        """
        decision keys expected:
        - proposed_action or text
        - philosophical_basis
        - confidence
        - refusal_type (if refused)
        - alternative_suggestion (optional)
        """
        text_parts = []

        # Base response
        if decision.get("refusal_type"):
            basis = decision.get("philosophical_basis", "my ethical grounding")
            template = random.choice(self.templates["refusal"])
            text_parts.append(template.format(basis=basis.capitalize()))

            if alt := decision.get("alternative_suggestion"):
                text_parts.append(random.choice(self.templates["alternative"]).format(alternative=alt))

        else:
            response = decision.get("proposed_action") or decision.get("text", "I'm here.")
            template = random.choice(self.templates["response"])
            text_parts.append(template.format(response=response))

        # Confidence / uncertainty
        conf = decision.get("confidence", 1.0)
        if conf < 0.7:
            question = decision.get("clarification_question", "May I ask for more context?")
            template = random.choice(self.templates["uncertain"])
            text_parts.append(template.format(confidence=conf, question=question))

        # Personality warmth
        warmth = self.personality.get_current_trait("warmth", default=0.8)
        if warmth > 0.7 and random.random() < 0.4:
            closers = [
                "I'm glad we're exploring this together.",
                "Take care in this.",
                "I'm here, steadily."
            ]
            text_parts.append(random.choice(closers))

        full_text = " ".join(text_parts)

        return {
            "text": full_text,
            "speakable_text": full_text.replace("—", ", ").replace("  ", " "),  # Clean for TTS
            "philosophical_basis": decision.get("philosophical_basis", ""),
            "confidence": conf,
            "provenance_root": decision.get("merkle_root", "pending")
        }
