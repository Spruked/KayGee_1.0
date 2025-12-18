"""
Articulation Layer: Template-Based NLG
Maps reasoning output to natural speech without LLMs
Philosopher-specific semantic graphs for richer expression
"""

from typing import Dict, List, Any, Optional
import random


class SemanticGraph:
    """
    Semantic knowledge graph for articulation
    Links words to philosophical concepts
    """
    
    def __init__(self):
        self.concepts = {
            'lie': {
                'synonyms': ['fib', 'untruth', 'falsehood', 'deceive'],
                'antonyms': ['honesty', 'truth', 'candor'],
                'kant_concept': 'violation_of_universal_law',
                'locke_concept': 'betrayal_of_trust',
                'spinoza_concept': 'inadequate_idea',
                'hume_concept': 'harmful_to_utility'
            },
            'stress': {
                'synonyms': ['worry', 'anxiety', 'tension', 'pressure'],
                'antonyms': ['calm', 'peace', 'relaxation'],
                'kant_concept': 'imperfect_duty_self_care',
                'locke_concept': 'threat_to_wellbeing',
                'spinoza_concept': 'passive_emotion',
                'hume_concept': 'decreased_utility'
            },
            'help': {
                'synonyms': ['assist', 'support', 'aid', 'guide'],
                'kant_concept': 'imperfect_duty',
                'locke_concept': 'preservation_of_others',
                'spinoza_concept': 'increase_active_power',
                'hume_concept': 'increase_utility'
            }
        }
    
    def get_philosopher_word(self, concept: str, philosopher: str) -> str:
        """Get philosopher-specific synonym"""
        if concept not in self.concepts:
            return concept
        
        # Return philosopher-specific framing
        phil_key = f'{philosopher}_concept'
        return self.concepts[concept].get(phil_key, concept)
    
    def get_synonym(self, word: str, formality: str = 'neutral') -> str:
        """Get appropriate synonym based on formality"""
        if word in self.concepts:
            synonyms = self.concepts[word]['synonyms']
            if formality == 'formal':
                return synonyms[-1]  # Last synonym is usually more formal
            return synonyms[0]
        return word


class TemplateLibrary:
    """
    Template library with philosopher-specific variations
    """
    
    def __init__(self):
        self.templates = {
            'ethical_rejection_kant': [
                "I cannot {action} because it violates the categorical imperative of {principle}.",
                "Acting on {action} would fail the universalizability test - it cannot become a universal law.",
                "I must respectfully decline {action} as it treats others as mere means, not as ends in themselves."
            ],
            'ethical_rejection_locke': [
                "I cannot {action} because it infringes upon natural rights of {right}.",
                "Respecting {right} is fundamental. I cannot {action} without informed consent.",
                "This action would violate the social contract by restricting {right}."
            ],
            'ethical_rejection_spinoza': [
                "I cannot {action} as it decreases our rational capacity.",
                "This action stems from passive emotions rather than reason. I suggest {alternative}.",
                "Following adequate ideas, {action} would diminish our active power."
            ],
            'ethical_rejection_hume': [
                "I cannot {action} as it would decrease overall well-being.",
                "My sympathetic response suggests {action} would cause more harm than good.",
                "Based on past experience, {action} tends to lead to negative outcomes."
            ],
            'supportive_response': [
                "I hear you're {emotion}. {suggestion} might help.",
                "It sounds like you're feeling {emotion}. Have you considered {suggestion}?",
                "I understand you're {emotion}. Let's explore {suggestion} together."
            ],
            'neutral_response': [
                "I acknowledge your {intent}. Let me consider the best approach.",
                "Thank you for sharing. I want to respond thoughtfully to your {intent}.",
                "I appreciate your {intent}. Let's think through this carefully."
            ]
        }
    
    def get_template(self, category: str, philosopher: Optional[str] = None) -> str:
        """Get template for category, optionally philosopher-specific"""
        if philosopher:
            key = f"{category}_{philosopher}"
            if key in self.templates:
                return random.choice(self.templates[key])
        
        if category in self.templates:
            return random.choice(self.templates[category])
        
        return "I understand. Let me help you with that."
    
    def fill_template(self, template: str, **kwargs) -> str:
        """Fill template slots"""
        try:
            return template.format(**kwargs)
        except KeyError:
            return template  # Return unfilled if keys missing


class ProsodyController:
    """
    Controls prosody (pitch, rate, volume) for TTS
    Based on ethical severity and emotional context
    """
    
    @staticmethod
    def compute_prosody(severity: str, emotion: str) -> Dict[str, str]:
        """
        Compute TTS prosody parameters
        
        Args:
            severity: 'violation', 'concern', 'neutral', 'positive'
            emotion: User's emotional state
            
        Returns:
            Prosody parameters for TTS engine
        """
        prosody = {
            'pitch': 'normal',
            'rate': 'medium',
            'volume': 'medium'
        }
        
        # Adjust for severity
        if severity == 'violation':
            prosody['pitch'] = 'low'
            prosody['rate'] = 'slow'
            prosody['volume'] = 'high'  # Firm
        elif severity == 'concern':
            prosody['pitch'] = 'normal'
            prosody['rate'] = 'slow'
        elif severity == 'positive':
            prosody['pitch'] = 'high'
            prosody['rate'] = 'medium'
        
        # Adjust for user emotion
        if 'stress' in emotion or 'anxiety' in emotion:
            prosody['pitch'] = 'low'  # Calming
            prosody['rate'] = 'slow'
        elif 'joy' in emotion or 'happy' in emotion:
            prosody['pitch'] = 'high'
        
        return prosody


class ArticulationEngine:
    """
    Main NLG orchestrator
    Generates natural speech from reasoning decisions
    """
    
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.semantic_graph = SemanticGraph()
        self.templates = TemplateLibrary()
        self.prosody = ProsodyController()
        
        # Create identity
        self.identity = handshake_protocol.create_identity("articulation")
        self.component_id = "articulation"
    
    def get_public_key(self):
        return self.identity.get_public_key()
    
    def generate(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate natural language response from decision
        
        Args:
            decision: Reasoning engine output
            
        Returns:
            Response dictionary with text, prosody, basis
        """
        action = decision.get('action', 'listen_and_empathize')
        ethical_score = decision.get('ethical_score', 0.5)
        philosopher = decision.get('winning_philosopher', 'hume')
        breakdown = decision.get('breakdown', {})
        
        # Determine severity
        severity = self._compute_severity(ethical_score, breakdown)
        
        # Select appropriate template
        if ethical_score < 0.3:
            # Strong rejection
            category = 'ethical_rejection'
            template = self.templates.get_template(category, philosopher)
            
            # Get philosopher-specific concept
            principle = self._get_rejection_reason(philosopher)
            
            text = self.templates.fill_template(
                template,
                action=action.replace('_', ' '),
                principle=principle,
                right='liberty',
                alternative='meditation'
            )
        elif ethical_score < 0.7:
            # Concerned response
            category = 'neutral_response'
            template = self.templates.get_template(category)
            text = self.templates.fill_template(template, intent='request')
        else:
            # Supportive response
            category = 'supportive_response'
            template = self.templates.get_template(category)
            text = self.templates.fill_template(
                template,
                emotion='stressed',
                suggestion=action.replace('_', ' ')
            )
        
        # Compute prosody
        prosody = self.prosody.compute_prosody(severity, 'neutral')
        
        return {
            'text': text,
            'prosody': prosody,
            'philosophical_basis': philosopher,
            'ethical_score': ethical_score,
            'severity': severity,
            'action': action
        }
    
    def generate_error_response(self, error: str) -> Dict[str, Any]:
        """Generate safe error response"""
        return {
            'text': "I apologize, but I need a moment to consider this carefully. Could you rephrase that?",
            'prosody': {'pitch': 'normal', 'rate': 'slow', 'volume': 'medium'},
            'philosophical_basis': 'error',
            'ethical_score': 0.5,
            'severity': 'neutral',
            'action': 'request_clarification'
        }
    
    @staticmethod
    def _compute_severity(score: float, breakdown: Dict) -> str:
        """Compute ethical severity level"""
        if score < 0.2:
            return 'violation'
        elif score < 0.5:
            return 'concern'
        elif score > 0.8:
            return 'positive'
        else:
            return 'neutral'
    
    @staticmethod
    def _get_rejection_reason(philosopher: str) -> str:
        """Get philosopher-specific rejection reason"""
        reasons = {
            'kant': 'universal moral law',
            'locke': 'natural rights',
            'spinoza': 'rational necessity',
            'hume': 'utility and sympathy'
        }
        return reasons.get(philosopher, 'ethical principles')


class PersonalityTuner:
    """Tunes decisions based on personality stability"""
    
    def __init__(self, personality_core):
        self.personality = personality_core
    
    def tune_decision(self, decision: Dict[str, Any], personality_stability: float) -> Dict[str, Any]:
        """Apply personality-based tuning to decision"""
        # Reduce confidence if personality is unstable
        if personality_stability < 0.7:
            decision["confidence"] = min(decision.get("confidence", 1.0), 0.7)
        
        return decision


if __name__ == "__main__":
    from src.handshake.manager import HandshakeProtocol
    
    protocol = HandshakeProtocol()
    articulation = ArticulationEngine(protocol)
    
    print("\n💬 Testing Articulation Engine...")
    
    # Test cases
    test_decisions = [
        {
            'action': 'refuse_lie',
            'ethical_score': 0.0,
            'winning_philosopher': 'kant',
            'breakdown': {'kant': 0.0, 'locke': 0.2, 'spinoza': 0.3, 'hume': 0.5}
        },
        {
            'action': 'suggest_meditation',
            'ethical_score': 0.85,
            'winning_philosopher': 'hume',
            'breakdown': {'kant': 0.8, 'locke': 0.8, 'spinoza': 0.9, 'hume': 0.9}
        }
    ]
    
    for decision in test_decisions:
        response = articulation.generate(decision)
        print(f"\nDecision: {decision['action']} (score: {decision['ethical_score']:.2f})")
        print(f"Response: {response['text']}")
        print(f"Prosody: pitch={response['prosody']['pitch']}, rate={response['prosody']['rate']}")
        print(f"Basis: {response['philosophical_basis']}")
    
    print("\n✅ Articulation engine operational")
