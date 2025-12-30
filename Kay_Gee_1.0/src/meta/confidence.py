"""
Meta-Reasoning & Confidence Monitoring
Explicit uncertainty detection with escalation paths
"""

from typing import Dict, Tuple, Optional


class MetaReasoner:
    def assess(self, trace):
        """
        Evaluate uncertainty and return action
        Returns: (action_type, response)
          action_type: "CLARIFY", "RECURSE", or "PROCEED"
        """
        penalties = 0
        
        # Check for low similarity
        if trace.get('lsh_similarity', 1.0) < 0.65:
            penalties += 1
        
        # Check for philosopher conflicts
        if len(trace.get('philosopher_conflicts', [])) >= 2:
            penalties += 1
        
        # Check for risky invented terms
        invented_terms = trace.get('invented_terms', [])
        for term in invented_terms:
            if term.startswith(('qua_', 'blu_', 'zee_')) and self.get_term_usage(term) < 7:
                penalties += 1
                break
        
        # Check recursion depth
        if trace.get('depth', 0) > 3:
            penalties += 1
        
        confidence = max(0.1, 1.0 - penalties * 0.2)
        
        if confidence < 0.5:
            question = self.craft_question(trace)
            # In VS Code, would use: vscode.window.show_quick_pick
            print(f"[Meta-Reasoning] Uncertain (confidence {confidence:.2f}): {question}")
            response = "Honesty first"  # Mock response
            return "CLARIFY", response
        elif confidence < 0.75:
            return "RECURSE", None
        
        return "PROCEED", None
    
    def craft_question(self, trace) -> str:
        """Generate clarification question based on trace"""
        if trace.get('philosopher_conflicts'):
            return "Are you prioritizing emotional comfort or strict honesty in this conversation?"
        elif trace.get('low_similarity'):
            return "This situation seems unusual. Can you provide more context?"
        else:
            return "I want to make sure I understand correctly. Can you clarify what's most important to you here?"
    
    def get_term_usage(self, term: str) -> int:
        """Get usage count for invented term"""
        # Mock implementation
        return 5
