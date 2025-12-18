"""
Context-Adaptive Philosophical Blending
Dynamic weighting based on detected context
"""

from typing import Dict, List, Tuple


class ContextBlender:
    PROFILES = {
        "medical": {"kantian_duty": 0.65, "humean_utility": 0.20, "lockean_rights": 0.10, "spinozan_conatus": 0.05},
        "legal":   {"lockean_rights": 0.60, "kantian_duty": 0.30, "humean_utility": 0.08, "spinozan_conatus": 0.02},
        "social":  {"humean_utility": 0.55, "spinozan_conatus": 0.20, "kantian_duty": 0.15, "lockean_rights": 0.10},
        "creative":{"spinozan_conatus": 0.50, "humean_utility": 0.30, "kantian_duty": 0.15, "lockean_rights": 0.05},
        "default": {"kantian_duty": 0.30, "lockean_rights": 0.25, "spinozan_conatus": 0.20, "humean_utility": 0.25},
    }

    def blend(self, detected_context: str, individual_scores: dict) -> Tuple[float, str]:
        """
        Blend philosopher scores based on context
        Returns: (final_score, dominant_philosopher)
        """
        profile = self.PROFILES.get(detected_context, self.PROFILES["default"])
        
        # Map philosopher keys
        score_mapping = {
            "kantian_duty": individual_scores.get("kant", 0.5),
            "lockean_rights": individual_scores.get("locke", 0.5),
            "spinozan_conatus": individual_scores.get("spinoza", 0.5),
            "humean_utility": individual_scores.get("hume", 0.5)
        }
        
        score = sum(score_mapping[p] * w for p, w in profile.items())
        dominant = max(profile, key=profile.get)
        
        # Log to trace vault
        print(f"[Context Blend] Context: {detected_context}, Dominant: {dominant}, Score: {score:.2f}")
        
        return score, dominant
    
    def select_profile(self, context_tags: List[str]):
        """Select best matching profile from tags"""
        for tag in context_tags:
            if tag in self.PROFILES:
                return self.PROFILES[tag]
        return self.PROFILES["default"]
