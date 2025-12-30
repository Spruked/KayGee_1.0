"""
Personality Core - Deterministic, non-generative personality modulation
Used ONLY to shape tone and confidence of articulation.
"""

from typing import Dict


class PersonalityCore:
    """Deterministic personality profile for system expression"""

    DEFAULT_TRAITS: Dict[str, float] = {
        "warmth": 0.8,
        "confidence": 0.7,
        "directness": 0.6
    }

    def __init__(self, traits: Dict[str, float] | None = None):
        # Copy defaults to avoid mutation bleed
        self.traits: Dict[str, float] = self.DEFAULT_TRAITS.copy()

        if traits:
            for k, v in traits.items():
                self.set_trait(k, v)

    def get_trait(self, trait_name: str) -> float:
        """Return trait value (0.0–1.0). Unknown traits are neutral."""
        return self.traits.get(trait_name, 0.5)

    def set_trait(self, trait_name: str, value: float):
        """Set a trait with strict bounds enforcement."""
        if not isinstance(value, (int, float)):
            raise TypeError(f"Trait '{trait_name}' must be numeric")

        self.traits[trait_name] = max(0.0, min(1.0, float(value)))

    def adjust_trait(self, trait_name: str, delta: float):
        """Incrementally adjust a trait."""
        current = self.get_trait(trait_name)
        self.set_trait(trait_name, current + delta)

    def snapshot(self) -> Dict[str, float]:
        """Immutable snapshot for audit/logging."""
        return dict(self.traits)

    def apply_to_response(self, response: dict) -> dict:
        """
        Annotate response with personality metadata.
        Does NOT alter reasoning or content.
        """
        response["personality"] = self.snapshot()
        return response
