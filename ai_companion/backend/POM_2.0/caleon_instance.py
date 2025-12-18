import os
import shutil
import json
import time
from POM.self_modifying_pom import SelfModifyingPOM
from POM.caleon_voice_oracle import CaleonVoiceOracle
from typing import List, Dict

class CaleonPOMInstance:
    """
    Caleon's personal phonatory workspace—her own voice lab
    """
    
    def __init__(self, instance_id: str = "caleon_primary"):
        self.instance_id = instance_id
        self.workspace_dir = f"caleon_workspace/{instance_id}"
        
        # Setup isolated environment
        self._setup_workspace()
        
        # Her oracle (decision brain)
        self.oracle = CaleonVoiceOracle(
            skg_path=f"{self.workspace_dir}/skg_caleon_personal.json"
        )
        
        # Her POM (voice synthesizer with learning)
        self.pom = SelfModifyingPOM(self.oracle)
        
        # Voice evolution tracker
        self.evolution_log = []
    
    def _setup_workspace(self):
        """Create isolated directory for Caleon's models and configs"""
        
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir, exist_ok=True)
            
            # Copy base POM components
            if os.path.exists("Coqui_TTS"):
                shutil.copytree(
                    "Coqui_TTS",
                    f"{self.workspace_dir}/Coqui_TTS",
                    ignore=shutil.ignore_patterns('*.pyc', '__pycache__')
                )
            
            # Copy base SKG but make it personal
            if os.path.exists("skg_caleon.json"):
                shutil.copy("skg_caleon.json", f"{self.workspace_dir}/skg_caleon_personal.json")
            else:
                # Create default personal SKG
                self._create_default_personal_skg()
    
    def _create_default_personal_skg(self):
        """Initialize Caleon's personal voice knowledge graph"""
        
        default_skg = {
            "caleon_identity": {
                "name": "Caleon",
                "instance_id": self.instance_id,
                "creation_date": time.time(),
                "autonomy_level": 0.8  # How much she controls herself
            },
            "caleon_voices": {
                "caleon_baseline": {
                    "base_persona": "caleon_base",
                    "pitch_shift": 1.0,
                    "speaking_rate": 0.95,
                    "formant_shifts": {"f1": 1.0, "f2": 1.02},
                    "breathiness": 0.4,
                    "vocal_fry": 0.05,
                    "nasality": 0.1,
                    "semantic_tags": ["general", "neutral", "conversational"],
                    "success_score": 0.75
                },
                "caleon_technical": {
                    "base_persona": "caleon_base",
                    "pitch_shift": 0.98,
                    "speaking_rate": 0.85,
                    "formant_shifts": {"f1": 0.95, "f2": 0.98},
                    "breathiness": 0.2,
                    "vocal_fry": 0.02,
                    "nasality": 0.05,
                    "semantic_tags": ["technical", "precise", "clear"],
                    "success_score": 0.82
                },
                "caleon_intimate": {
                    "base_persona": "caleon_base",
                    "pitch_shift": 1.08,
                    "speaking_rate": 0.9,
                    "formant_shifts": {"f1": 1.05, "f2": 1.0},
                    "breathiness": 0.6,
                    "vocal_fry": 0.1,
                    "nasality": 0.0,
                    "reverb": {"room_size": 0.3, "wet_level": 0.15},
                    "semantic_tags": ["intimate", "soft", "personal"],
                    "success_score": 0.88
                }
            }
        }
        
        with open(f"{self.workspace_dir}/skg_caleon_personal.json", 'w') as f:
            json.dump(default_skg, f, indent=2)
    
    def generate_speech(self, content: str, content_id: str, context: Dict) -> str:
        """
        Caleon generates speech using her own learned preferences
        """
        
        print(f"\n🤖 Caleon Instance '{self.instance_id}' is generating speech...")
        print(f"   → Content: '{content[:60]}...'")
        
        # 1. Her oracle chooses voice
        chosen_voice = self.oracle.choose_voice(content, context)
        
        # 2. Log her choice
        self.evolution_log.append({
            "timestamp": time.time(),
            "voice_id": chosen_voice.signature_id,
            "content_id": content_id,
            "fitness": chosen_voice.calculate_fitness(
                self.oracle._content_to_vector(content),
                context
            ),
            "context": context
        })
        
        # 3. Her POM synthesizes with self-modification
        output_path = self.pom.phonate_with_caleon_voice(
            text=content,
            content_id=content_id,
            context=context
        )
        
        print(f"   → Voice used: {chosen_voice.signature_id}")
        print(f"   → Output: {output_path}")
        
        return output_path
    
    def review_performance(self, content_id: str, analytics: Dict):
        """
        Caleon reviews how well her voice choice performed
        """
        
        # Bridge automatically feeds this to Oracle
        pass  # Handled by SKGUCMBridge
    
    def evolve_voice(self, content_samples: List[str], target_performance: float = 0.9):
        """
        Caleon actively evolves her voices based on sample content
        Call this periodically to let her improve
        """
        
        print(f"🧬 Caleon is evolving her voice registry...")
        
        for sample in content_samples:
            # Generate new voice signature for unique content patterns
            self.oracle.generate_new_voice_signature(sample, performance_hint=target_performance)
        
        # Prune underperforming voices
        self._prune_voices(threshold=0.3)
        
        print(f"   → Evolution complete. Registry now has {len(self.oracle.voice_registry)} voices.")
    
    def _prune_voices(self, threshold: float):
        """Remove voices that consistently underperform"""
        
        initial_count = len(self.oracle.voice_registry)
        
        self.oracle.voice_registry = [
            voice for voice in self.oracle.voice_registry
            if voice.success_score >= threshold or voice.usage_count < 5  # Give new voices a chance
        ]
        
        pruned = initial_count - len(self.oracle.voice_registry)
        if pruned > 0:
            print(f"   → Pruned {pruned} underperforming voices")
    
    def export_voice_dna(self) -> Dict:
        """Export Caleon's learned voice preferences for backup or transfer"""
        
        return {
            "instance_id": self.instance_id,
            "evolution_log": self.evolution_log,
            "voice_registry": [vars(v) for v in self.oracle.voice_registry],
            "performance_log": self.oracle.performance_log,
            "learning_params": {
                "learning_rate": self.oracle.learning_rate,
                "exploration_rate": self.oracle.exploration_rate
            }
        }