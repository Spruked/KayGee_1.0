"""
Temporal Context Layer
Tracks session continuity and temporal coherence
"""

from typing import Dict, Any, Optional
import time

class TemporalContextLayer:
    """Maintains temporal context across interactions"""
    
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None
    
    def initialize_session(self, session_id: str):
        """Initialize a new session"""
        self.current_session_id = session_id
        self.sessions[session_id] = {
            "start_time": time.time(),
            "interaction_count": 0,
            "context_stack": [],
            "emotional_state_history": [],
            "personality_stability": 1.0
        }
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve temporal context for session"""
        if session_id not in self.sessions:
            return {
                "is_new_session": True,
                "elapsed_time": 0,
                "personality_stability": 1.0,
                "recent_topics": []
            }
        
        session = self.sessions[session_id]
        return {
            "is_new_session": False,
            "elapsed_time": time.time() - session["start_time"],
            "personality_stability": session["personality_stability"],
            "recent_topics": session["context_stack"][-5:] if session["context_stack"] else []
        }
    
    def update_session_context(self, session_id: str, interaction_marker: str, emotional_residual: str):
        """Update session context after interaction"""
        if session_id in self.sessions:
            self.sessions[session_id]["interaction_count"] += 1
            self.sessions[session_id]["context_stack"].append({
                "marker": interaction_marker,
                "timestamp": time.time(),
                "emotion": emotional_residual
            })
