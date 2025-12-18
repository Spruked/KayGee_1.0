from typing import Dict, Any
import threading
import time
import numpy as np

class SKGUCMBridge:
    """
    Bidirectional sync between Unified Content Manager and Speaker Knowledge Graph
    """
    
    def __init__(self, skg_manager, ucm_instance):
        self.skg = skg_manager
        self.ucm = ucm_instance
        self.sync_lock = threading.Lock()
        
        # Subscribe to UCM content events
        if hasattr(self.ucm, 'subscribe'):
            self.ucm.subscribe("content_ingested", self._on_content_ingested)
            self.ucm.subscribe("content_published", self._on_content_published)
            self.ucm.subscribe("listener_analytics", self._on_analytics_received)
    
    def _on_content_ingested(self, content_id: str, metadata: Dict):
        """Auto-enrich SKG when UCM receives new content"""
        
        print(f"🌉 UCM→SKG: New content '{content_id}' ingested")
        
        with self.sync_lock:
            # Extract semantic features
            semantic_tags = self._extract_semantic_tags(metadata)
            
            # Create content vector in SKG
            if not hasattr(self.skg, 'content_vectors'):
                self.skg.content_vectors = {}
            
            self.skg.content_vectors[content_id] = {
                "vector": self._vectorize_content(metadata),
                "tags": semantic_tags,
                "timestamp": time.time(),
                "source": metadata.get("source", "unknown")
            }
            
            # If content is tagged for Caleon, notify Oracle
            if "caleon_narration" in metadata.get("tags", []):
                self._prepare_caleon_voice(content_id, metadata)
    
    def _on_content_published(self, content_id: str, publication_data: Dict):
        """Track voice usage when content goes live"""
        
        voice_used = publication_data.get("voice_signature_id")
        if voice_used and "caleon" in voice_used:
            print(f"🌉 Tracking: Caleon used {voice_used} for {content_id}")
            
            # Log in performance queue for later feedback
            if not hasattr(self.skg, 'performance_queue'):
                self.skg.performance_queue = {}
            
            self.skg.performance_queue[content_id] = {
                "voice_id": voice_used,
                "timestamp": time.time(),
                "status": "pending_feedback"
            }
    
    def _on_analytics_received(self, content_id: str, analytics: Dict):
        """Feed listener analytics back to Caleon's Oracle"""
        
        if not hasattr(self.skg, 'performance_queue') or content_id not in self.skg.performance_queue:
            return
        
        print(f"🌉 UCM→SKG: Analytics received for {content_id}")
        
        # Extract engagement metrics
        listener_feedback = {
            "retention_rate": analytics.get("avg_retention", 0.7),
            "engagement_score": analytics.get("engagement", 0.6),
            "completion_rate": analytics.get("completion_rate", 0.5),
            "drop_off_points": analytics.get("drop_off_timestamps", [])
        }
        
        # Calculate performance score
        performance_score = (
            listener_feedback["retention_rate"] * 0.4 +
            listener_feedback["engagement_score"] * 0.3 +
            listener_feedback["completion_rate"] * 0.3
        )
        
        # Send to Oracle for learning
        voice_id = self.skg.performance_queue[content_id]["voice_id"]
        
        # Import here to avoid circular imports
        from POM.caleon_voice_oracle import CaleonVoiceOracle
        oracle = CaleonVoiceOracle()
        oracle.receive_feedback(
            voice_id=voice_id,
            content_hash=content_id,
            performance_score=performance_score,
            listener_feedback=listener_feedback
        )
        
        # Mark as processed
        self.skg.performance_queue[content_id]["status"] = "processed"
    
    def _prepare_caleon_voice(self, content_id: str, metadata: Dict):
        """Pre-select voice signature for upcoming narration"""
        
        from POM.caleon_voice_oracle import CaleonVoiceOracle
        oracle = CaleonVoiceOracle()
        
        # Extract content snippets
        content_preview = metadata.get("preview_text", "")
        
        context = {
            "technical_density": metadata.get("technical_language_score", 0.0),
            "emotional_tone": metadata.get("primary_emotion", "neutral"),
            "audience_intimacy": metadata.get("target_audience", "general"),
            "content_id": content_id
        }
        
        # This will pre-load her choice into the registry
        chosen_voice = oracle.choose_voice(content_preview, context)
        
        # Store choice in UCM for reference
        if hasattr(self.ucm, 'set_content_metadata'):
            self.ucm.set_content_metadata(content_id, {
                "preselected_voice_id": chosen_voice.signature_id,
                "voice_fitness": chosen_voice.calculate_fitness(
                    oracle._content_to_vector(content_preview),
                    context
                )
            })
    
    def _extract_semantic_tags(self, metadata: Dict) -> list:
        """Extract semantic tags from content metadata"""
        
        tags = []
        
        # Extract from title and description
        text = f"{metadata.get('title', '')} {metadata.get('description', '')}"
        
        # Simple tag extraction
        if "technical" in text.lower() or "quantum" in text.lower():
            tags.append("technical")
        if "emotional" in text.lower() or "personal" in text.lower():
            tags.append("emotional")
        if "tutorial" in text.lower() or "guide" in text.lower():
            tags.append("educational")
        
        return tags
    
    def _vectorize_content(self, metadata: Dict) -> np.ndarray:
        """Create a simple vector representation of content"""
        
        # Simple vector based on metadata
        vector = np.zeros(10)
        
        # Length-based features
        text_length = len(metadata.get('description', ''))
        vector[0] = min(text_length / 1000, 1.0)  # Normalized length
        
        # Technical density
        technical_words = ["quantum", "algorithm", "neural", "machine", "learning", "data"]
        tech_count = sum(1 for word in technical_words if word in metadata.get('description', '').lower())
        vector[1] = min(tech_count / 5, 1.0)
        
        # Emotional tone (simplified)
        emotional_words = ["amazing", "wonderful", "terrible", "sad", "exciting"]
        emotion_count = sum(1 for word in emotional_words if word in metadata.get('description', '').lower())
        vector[2] = min(emotion_count / 3, 1.0)
        
        return vector