"""
Confucian Ethics Plugin
Five Relationships & Ren (benevolence)
Philosophical Expansion - Plug-in Ethics
"""

from pathlib import Path


class ConfucianEthics:
    """Confucian ethical framework plugin"""
    
    def __init__(self):
        self.rules_path = Path("src/ethics/plugins/confucian_rules.pl")
        self.rules = self.load_rules()
    
    def load_rules(self):
        """Load Confucian Prolog rules"""
        if self.rules_path.exists():
            with open(self.rules_path) as f:
                return f.read()
        return ""
    
    def evaluate(self, action: str, context: dict) -> float:
        """
        Five Relationships & Ren (benevolence)
        Returns ethical score 0.0 - 1.0
        """
        score = 0.5  # Neutral baseline
        
        # Filial piety check
        relationship = context.get("relationship", "")
        if relationship == "parent":
            if "disrespect" in action.lower() or "dishonor" in action.lower():
                score -= 0.5
            elif "honor" in action.lower() or "respect" in action.lower():
                score += 0.3
        
        # Social harmony check
        if self.promotes_harmony(action, context):
            score += 0.3
        
        # Reciprocity (Shu) - "Do not do to others what you would not want done to yourself"
        if self.would_not_want(action, context):
            score -= 0.4
        
        # Ren (benevolence) - humaneness and compassion
        if self.shows_compassion(action):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def promotes_harmony(self, action: str, context: dict) -> bool:
        """Check if action promotes social harmony"""
        harmony_keywords = ['reconcile', 'mediate', 'compromise', 'peace', 'balance']
        return any(keyword in action.lower() for keyword in harmony_keywords)
    
    def would_not_want(self, action: str, context: dict) -> bool:
        """Check reciprocity - would you want this done to you?"""
        negative_actions = ['deceive', 'harm', 'exploit', 'manipulate', 'insult']
        return any(keyword in action.lower() for keyword in negative_actions)
    
    def shows_compassion(self, action: str) -> bool:
        """Check for benevolence/compassion"""
        compassion_keywords = ['help', 'support', 'comfort', 'care', 'nurture']
        return any(keyword in action.lower() for keyword in compassion_keywords)
