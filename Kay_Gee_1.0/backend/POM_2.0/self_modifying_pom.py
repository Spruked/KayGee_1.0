from typing import Dict, Any
import time

class SelfModifyingPOM:
    """
    Enhanced POM that accepts live parameter modifications
    and logs successful configurations
    """
    
    def __init__(self, caleon_oracle):
        # Don't initialize PhonatoryOutputModule immediately to avoid TTS loading issues
        # super().__init__()
        self.oracle = caleon_oracle
        self.modification_log = []
        self.stability_threshold = 0.95  # When to lock in a config
    
    def phonate_with_caleon_voice(self, text: str, content_id: str, context: Dict) -> str:
        """
        Primary entry: Caleon chooses her voice, then synthesizes
        """
        
        # 1. Caleon chooses her best voice for this content
        voice_signature = self.oracle.choose_voice(text, context)
        
        # 2. Apply voice parameters to POM
        modified_config = self._apply_voice_signature(voice_signature)
        
        # 3. Simulate synthesis with her chosen parameters
        output_path = self._simulate_phonate(
            text=text,
            speaker=voice_signature.base_persona,
            speaker_wav=self._get_caleon_reference_audio(voice_signature),
            **modified_config
        )
        
        # 4. Log the modification
        self.modification_log.append({
            "content_id": content_id,
            "voice_id": voice_signature.signature_id,
            "text_snippet": text[:100],
            "timestamp": time.time(),
            "config_snapshot": modified_config
        })
        
        # 5. If this voice is very successful, consider locking it
        if voice_signature.success_score > self.stability_threshold:
            self._stabilize_voice(voice_signature)
        
        return output_path
    
    def _simulate_phonate(self, text: str, speaker: str, speaker_wav: str, **kwargs) -> str:
        """Simulate phonation for testing Caleon's logic"""
        import hashlib
        import os
        
        # Create a unique filename based on content
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        output_path = f"output_caleon_{content_hash}.wav"
        
        # Simulate synthesis by creating a placeholder file
        # In real implementation, this would call the actual TTS
        print(f"🎵 Simulating synthesis: {text[:50]}... → {output_path}")
        print(f"   Voice config: {kwargs}")
        
        # Create empty file as placeholder
        with open(output_path, 'w') as f:
            f.write(f"# Simulated audio file for: {text[:100]}\n")
            f.write(f"# Speaker: {speaker}\n")
            f.write(f"# Config: {kwargs}\n")
        
        return output_path
    
    def _apply_voice_signature(self, voice) -> Dict:
        """Convert voice signature to POM parameters"""
        
        # Map to POM's expected parameters
        pom_config = {
            "pitch_shift": voice.pitch_shift,
            "speed": voice.speaking_rate,
            "formant_shifts": voice.formant_shifts,
            "phonatory_effects": {
                "breathiness": voice.breathiness,
                "vocal_fry": voice.vocal_fry,
                "nasalization": voice.nasality
            }
        }
        
        # Apply reverb if present
        if voice.reverb:
            pom_config["post_effects"] = {
                "reverb": voice.reverb
            }
        
        return pom_config
    
    def _get_caleon_reference_audio(self, voice) -> str:
        """Find the best reference audio for this voice signature"""
        
        # If voice has custom reference, use it
        if hasattr(voice, 'reference_audio_path'):
            return voice.reference_audio_path
        
        # Otherwise, use base persona reference
        # Assuming SKG has persona info, but for now use default
        return "reference_voice.wav"  # Default reference
    
    def _stabilize_voice(self, voice):
        """Lock in a successful configuration"""
        
        print(f"🔒 Stabilizing voice: {voice.signature_id} (score: {voice.success_score:.3f})")
        
        # Create permanent model cache
        cache_path = f"coqui/voices/stable_{voice.signature_id}.wav"
        
        # Generate a stabilization sample (Caleon's "signature phrase")
        stabilization_text = "This is my voice, stable and true."
        
        self._simulate_phonate(
            text=stabilization_text,
            speaker=voice.base_persona,
            speaker_wav=cache_path,
            **self._apply_voice_signature(voice)
        )
        
        # Mark as stable in registry
        if not hasattr(voice, 'metadata'):
            voice.metadata = {}
        voice.metadata = {"stable_model_path": cache_path, "is_locked": True}
        
        # Reduce future exploration
        self.oracle.exploration_rate *= 0.9
    
    def adjust_voice_realtime(self, text_segment: str, current_config: Dict, feedback_signal: float) -> Dict:
        """
        Mid-narration adjustment based on real-time feedback
        feedback_signal: 0.0-1.0 (listener engagement meter)
        """
        
        # If engagement drops, modify parameters to recapture attention
        if feedback_signal < 0.4:
            print(f"⚠️  Engagement low ({feedback_signal:.2f}), adjusting voice")
            
            # Increase energy and clarity
            adjustment = {
                "pitch_shift": current_config.get("pitch_shift", 1.0) * 1.05,
                "speed": current_config.get("speed", 1.0) * 0.95,  # Slow down slightly
                "phonatory_effects": {
                    **current_config.get("phonatory_effects", {}),
                    "breathiness": 0.1,  # Clearer voice
                    "vocal_fry": 0.05
                }
            }
            
            return adjustment
        
        # If engagement is high, maintain current config
        return current_config