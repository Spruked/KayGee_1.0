"""
Personality Core
Stable personality traits and consistency tracking
"""

from typing import Dict, Any
import yaml
from pathlib import Path

class PersonalityCore:
    """Maintains stable personality traits"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.traits = self._load_traits()
        self.stability = 1.0
    
    def _load_traits(self) -> Dict[str, float]:
        """Load personality traits from config"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = yaml.safe_load(f)
                    return config.get("personality", {
                        "warmth": 0.8,
                        "openness": 0.7,
                        "conscientiousness": 0.9,
                        "intellectual_humility": 0.85
                    })
            except:
                pass
        
        # Default traits
        return {
            "warmth": 0.8,
            "openness": 0.7,
            "conscientiousness": 0.9,
            "intellectual_humility": 0.85
        }
    
    def get_current_trait(self, trait_name: str, default: float = 0.5) -> float:
        """Get current value of a personality trait"""
        return self.traits.get(trait_name, default)
    
    def get_current_frame(self) -> Dict[str, Any]:
        """Get current personality frame"""
        return {
            "traits": self.traits.copy(),
            "stability": self.stability
        }
