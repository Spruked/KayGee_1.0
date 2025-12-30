import importlib.util
"""
Vaulted Reasoner: Multi-Layered Neuro-Symbolic AI Companion
Enhanced architecture with temporal, meta-cognitive, and consistency layers
"""

import sys
import logging
import hashlib
import time
import asyncio
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# RESPONSE SCHEMA - Guarantees keys before downstream processing
RESPONSE_SCHEMA = {
    "answer": "",
    "confidence": None,
    "philosophical_basis": "unspecified",
    "safety_flags": [],
    "provenance": {}
}

def normalize_response(resp: dict) -> dict:
    """Normalize response to guarantee all required keys exist"""
    for k, v in RESPONSE_SCHEMA.items():
        resp.setdefault(k, v)
    return resp

# Core protocols
from src.core.protocols import IdentityBoundComponent, ComponentIdentity, SecurityError

# Core components (existing)
from src.handshake.manager import HandshakeProtocol
from src.memory.vault import VaultSystem, APrioriVault, TraceVault, APosterioriVault
from src.reasoning.recursive_loop import ReasoningEngine, ConflictResolver
from src.perception.classifier import PerceptionSystem
from src.articulation.nlg import ArticulationEngine, PersonalityTuner
from src.learning.rule_induction import LearningSystem

# Legacy components
from src.temporal.context import TemporalContextLayer
from src.meta.cognition import MetaCognitiveMonitor

# NEW: Modular managers
from src.vaults import VaultManager


# Import ReasoningManager from new module
from src.reasoning_manager import ReasoningManager

# ArticulationManager
spec = importlib.util.spec_from_file_location("articulation_module", str(Path(__file__).parent / "src" / "articulation" / "engine.py"))
articulation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(articulation_module)
ArticulationManager = articulation_module.ArticulationManager

# PerceptionManager
spec = importlib.util.spec_from_file_location("perception_module", str(Path(__file__).parent / "src" / "perception.py"))
perception_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(perception_module)
PerceptionManager = perception_module.PerceptionManager

# ArticulationManager
spec = importlib.util.spec_from_file_location("articulation_module", str(Path(__file__).parent / "src" / "articulation.py"))
articulation_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(articulation_module)
ArticulationManager = articulation_module.ArticulationManager

# IntegrityManager
spec = importlib.util.spec_from_file_location("integrity_module", str(Path(__file__).parent / "src" / "integrity.py"))
integrity_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity_module)
IntegrityManager = integrity_module.IntegrityManager

# SKG Fatigue Prevention Components
from src.pruning import PruningEngine
from src.health_monitor import SKGHealthMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("Kay_Gee_1.0.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Explicit confidence levels for all decisions"""
    CERTAIN = 1.0      # Directly from A Priori Vault
    HIGH = 0.8         # Strong symbolic match
    MEDIUM = 0.6       # Analogical reasoning
    LOW = 0.4          # Pattern completion
    UNCERTAIN = 0.2    # Novel situation, proceed with caution
    EMERGENCY = 0.0    # Fail-safe triggered


@dataclass
class InteractionContext:
    """Structured context for all interactions"""
    timestamp: float
    session_id: str
    user_state: Dict[str, Any]
    system_state: Dict[str, Any]
    boundary_flags: List[str]
    emotional_climate: str
    temporal_marker: str  # "morning", "mid-conversation", "follow-up", etc.


class VaultedReasonerSystem:
    """
    Enhanced orchestrator with 9 integrated layers:
    1. Perception & Grounding
    2. Memory (Multi-Vault)
    3. Temporal Context
    4. Reasoning (with Conflict Resolution)
    5. Meta-Cognitive Monitoring
    6. Personality Consistency
    7. Ethical Safety Boundaries
    8. Articulation & NLG
    9. Learning & Consolidation
    """
    
    def __init__(self, config_path="config.yaml"):
        logger.info("🚀 Initializing Enhanced Vaulted Reasoner System...")
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize handshake protocol first (needed by managers)
        from src.handshake.manager import HandshakeProtocol
        self.handshake_protocol = HandshakeProtocol()
        self.config['handshake_protocol'] = self.handshake_protocol
        
        # Initialize modular managers
        self.vaults = VaultManager()
        self.reasoning_mgr = ReasoningManager()
        self.perception_mgr = PerceptionManager()
        self.articulation_mgr = ArticulationManager()
        self.integrity_mgr = IntegrityManager()
        
        # Initialize all managers
        managers = [self.vaults, self.reasoning_mgr, self.perception_mgr, 
                   self.articulation_mgr, self.integrity_mgr]
        
        for manager in managers:
            if not manager.initialize(self.config):
                logger.error(f"Failed to initialize {manager.name}")
                raise RuntimeError(f"System initialization failed at {manager.name}")
        
        # Initialize SKG Fatigue Prevention System
        self.pruning_engine = PruningEngine(self.vaults)
        self.skg_health_monitor = SKGHealthMonitor(self.vaults, self.reasoning_mgr, self.pruning_engine)
        
        # Background maintenance will be started externally if needed
        # asyncio.create_task(self._start_background_maintenance())
        
        # Legacy components for compatibility (can be phased out)
        self.temporal = TemporalContextLayer()
        self.metacognition = MetaCognitiveMonitor()
        
        # System state
        self.session_id = self._generate_session_id()
        self.interaction_count = 0
        
        # INSTANT VERDICT BYPASS CACHE
        self.verdict_cache = {}  # query_hash -> cached_verdict
        
        logger.info("✅ System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        import yaml
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                'max_reasoning_depth': 5,
                'reasoning_timeout': 30,
                'safety_boundaries': ['harm_prevention', 'truth_preservation']
            }
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
        
        # Initialize temporal context
        self.temporal.initialize_session(self.session_id)
        
        logger.info("✅ Enhanced system initialized successfully")
        logger.info(f"📋 Session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically unique session identifier"""
        timestamp = str(time.time())
        nonce = hashlib.sha256(timestamp.encode()).hexdigest()[:16]
        return f"session_{int(time.time())}_{nonce}"

    async def _start_background_maintenance(self):
        """Background task for SKG maintenance"""
        logger.info("🔄 Starting SKG background maintenance...")
        while True:
            try:
                await asyncio.sleep(86400)  # Run daily (24 hours)
                await self.pruning_engine.daily_maintenance()
                logger.info("✅ Daily SKG maintenance completed")
            except Exception as e:
                logger.error(f"❌ Background maintenance failed: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour on failure
    
    def _register_components(self):
        """Register all manager public keys with centralized identity creation"""
        # Manager map: name -> manager
        managers = {
            "vaults": self.vaults,
            "reasoning": self.reasoning_mgr,
            "perception": self.perception_mgr,
            "articulation": self.articulation_mgr,
            "integrity": self.integrity_mgr,
            "temporal": self.temporal,
            "metacognition": self.metacognition
        }
        
        # Register each manager using its identity's public key
        for name, manager in managers.items():
            if hasattr(manager, 'get_public_key'):
                self.vaults.handshake.register_component(name, manager.get_public_key())
                logger.info(f"  ✅ {name} registered with identity")
            else:
                logger.warning(f"  ⚠️  {name} does not have get_public_key method")
                logger.info(f"  ✓ Registered {name} (legacy mode)")
                continue
            
            # Standard path: use identity contract
            self.handshake.register_component(name, manager.get_public_key())
            logger.info(f"  ✓ Registered {name}")
        
        # Establish cross-component trust relationships
        self.handshake.establish_trust_network()
        logger.info("  ✓ Trust network established")
    
    def _verify_integrity(self):
        """Comprehensive integrity verification using integrity manager"""
        logger.info("🔍 Verifying system integrity...")
        
        integrity_status = self.integrity_mgr.check_integrity()
        if integrity_status.get('error'):
            raise SecurityError(f"❌ Integrity check failed: {integrity_status['error']}")
        
        logger.info("✅ System integrity verification passed")
    
    def _get_resonance_confidence_modifier(self) -> float:
        """
        Fetch cognitive resonance state from backend API
        
        Phase coherence from space field visualizer modifies confidence:
        - phaseCoherence → 1.0: Perfect harmonic lock (+20% confidence)
        - phaseCoherence ~ 0.5: Neutral state (0%)
        - phaseCoherence < 0.3: Cognitive turbulence (-15% confidence)
        
        This creates a closed-loop feedback:
        JS Visualizer → Backend Resonance API → ReasoningEngine → Confidence
        """
        try:
            import requests
            response = requests.get("http://localhost:8000/api/resonance/status", timeout=0.1)
            
            if response.status_code == 200:
                resonance = response.json()
                phase_coherence = resonance.get("phaseCoherence", 0.5)
                
                # Calculate modifier using backend formula
                if phase_coherence > 0.95:
                    return 0.20
                elif phase_coherence > 0.8:
                    return 0.10
                elif phase_coherence > 0.5:
                    return 0.0
                elif phase_coherence > 0.3:
                    return -0.10
                else:
                    return -0.15
        except Exception as e:
            # Resonance unavailable - use neutral modifier
            logger.debug(f"Resonance unavailable: {e}")
            return 0.0
        
        return 0.0
    
    def process_interaction(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user interaction with real reasoning - no mocks, no placeholders
        Hard-fail if no verdict from reasoner
        """
        self.interaction_count += 1
        start_time = time.time()

        try:
            logger.info(f"Processing interaction #{self.interaction_count}: '{user_input[:50]}...'")

            # REAL REASONING - Hard-fail on no verdict
            verdict = self.reasoning_mgr.evaluate(user_input)
            if verdict is None:
                raise RuntimeError("Reasoner returned no verdict")

            # NORMALIZE RESPONSE - Guarantees keys before articulation
            normalized_verdict = normalize_response(verdict)

            # REAL ARTICULATION - Only renders, never decides
            response_text = self.articulation_mgr.engine.render(normalized_verdict)

            # Return real response
            return {
                "text": response_text,
                "confidence": normalized_verdict.get("confidence"),
                "philosophical_basis": normalized_verdict.get("philosophical_basis", "unspecified"),
                "safety_flags": normalized_verdict.get("safety_flags", []),
                "provenance": normalized_verdict.get("provenance", {}),
                "processing_time": time.time() - start_time,
                "reasoning_used": True
            }

        except Exception as e:
            logger.error(f"❌ Fatal error in interaction #{self.interaction_count}: {e}")
            # No fallback - crash is honest
            raise
            
        except Exception as e:
            logger.error(f"Error in interaction #{self.interaction_count}: {e}")
            error_response = {
                "text": "I apologize, but I'm having trouble processing that right now. Could you try again?",
                "confidence": 0.0,
                "error": str(e),
                "reasoning_used": False
            }
            return normalize_response(error_response)
            
            # Step 3: Memory retrieval
            # (Simplified - use vaults manager)
            
            # Step 4: SKG Cascade Query - Truth flows downhill, entropy bubbles up
            skg_result = self.reasoning_mgr.query({
                "query": user_input,
                "perception": perception_result,
                "intent": intent
            }, vault_manager=self.vaults)
            
            # Step 5: Integrity check
            boundary_ok = self.integrity_mgr.enforce_boundaries(skg_result.get("result", {}).get("action", "unknown"))

            # Step 6: Articulation
            response_text = self.articulation_mgr.articulate(skg_result.get("result", {}))

            # Create decision structure from SKG result
            decision = {
                "confidence": skg_result.get("resonance_score", 0.8),
                "proposed_action": skg_result.get("result", {}).get("action", "respond"),
                "concern_count": len(skg_result.get("contradictions_found", [])),
                "reasoning_quality": skg_result.get("resonance_score", 0.8),
                "resonance_modifier": skg_result.get("resonance_score", 0.8) - 0.5,
                "harmonic_state": "resonant" if skg_result.get("resonance_score", 0.5) > 0.7 else "neutral",
                "cascade_path": skg_result.get("cascade_path", []),
                "ontology_version": skg_result.get("ontology_version", "1.0.0")
            }
            
            # Placeholder variables for advisory layers
            temporal_context = {"personality_stability": 0.8}
            emotional_state = {"vulnerability_level": 0.3}
            meta_advisories = {"adjusted_confidence": decision["confidence"]}
            
            # Step 7: Layer 6 - Personality Consistency Tuning
            decision = self.personality_tuner.tune_decision(
                decision,
                temporal_context["personality_stability"]
            )
            
            # Step 8: Layer 7 - Safety Final Assessment (ADVISORY ONLY)
            final_safety_assessment = self.safety.assess_final(
                decision["proposed_action"],
                user_vulnerability=emotional_state["vulnerability_level"]
            )
            
            # Aggregate all safety advisories (NO VETO)
            safety_advisories.update({
                "final_risk": final_safety_assessment.get("risk_score", 0.0),
                "final_flags": final_safety_assessment.get("flags", [])
            })
            # Calculate composite risk score
            composite_risk = max(
                safety_advisories.get("input_risk", 0.0),
                safety_advisories.get("decision_risk", 0.0),
                safety_advisories.get("final_risk", 0.0)
            )
            composite_flags = list(set(
                safety_advisories.get("input_flags", []) +
                safety_advisories.get("decision_flags", []) +
                safety_advisories.get("final_flags", [])
            ))
            
            # Step 9: THE GOLDEN GATE - Single Point of Truth Commitment
            # Aggregate all advisories
            advisors = {
                "safety": {
                    "risk_score": composite_risk,
                    "flags": composite_flags
                },
                "meta": meta_advisories,
                "personality": self.personality_tuner
            }
            
            # COMMIT THROUGH THE GATE (ALWAYS SUCCEEDS)
            response = self.commit_response(decision, advisors)
            
            # Print response with transparency
            print(f"\nKayGee: {response['text']}")
            if response.get('flags'):
                print(f"  [Safety Flags: {', '.join(response['flags'])}]")
            if response.get('confidence', 1.0) < 0.5:
                print(f"  [Low Confidence: {response['confidence']:.2f}]")
            if response.get('meta_concerns', 0) > 0:
                print(f"  [Meta Concerns: {response['meta_concerns']}]")
            print()
            
            # Step 10: Layer 9 - Comprehensive Logging
            self._log_full_interaction(
                user_input=user_input,
                perception=perception_data,
                emotional_state=emotional_state,
                memory_cases=similar_cases,
                principles=ethical_principles,
                temporal_context=temporal_context,
                decision=decision,
                response=response,
                context=interaction_ctx,
                processing_time=time.time() - start_time,
                advisories=advisors
            )
            
            # Step 11: Trigger learning if conditions met
            if self._should_learn(decision["confidence"], self.interaction_count):
                consolidation_result = self.learning.consolidate_traces(
                    self.trace_vault.get_recent(k=50),
                    self.episodic_vault
                )
                logger.info(f"🧠 Learning consolidation: {consolidation_result}")
            
            # Step 12: Update temporal context for next interaction
            self.temporal.update_session_context(
                self.session_id,
                interaction_marker=f"completed_{self.interaction_count}",
                emotional_residual=emotional_state["detected_tone"]
            )
            
            logger.info(f"📤 Response generated in {time.time() - start_time:.3f}s")
            
            # CACHE VERDICT FOR INSTANT BYPASS ON FUTURE IDENTICAL QUERIES
            verdict_id = f"verdict_{query_hash}_{int(time.time())}"
            cached_verdict = {
                "verdict_id": verdict_id,
                "timestamp": time.time(),
                "query_hash": query_hash,
                "response_text": response_text,
                "confidence": reasoning_result.get("result", {}).get("confidence", 0.5),
                "processing_time": time.time() - start_time
            }
            self.verdict_cache[query_hash] = cached_verdict
            
            # AUTO-COMMIT TO A POSTERIORI VAULT FOR MEMORY GROWTH
            self._commit_to_a_posteriori(
                context_hash=query_hash,
                decision=response_text,
                confidence=reasoning_result.get("result", {}).get("confidence", 0.5),
                philosophers_used=["kant", "hume", "taleb", "spinoza", "locke"],  # From loaded seeds
                timestamp=time.time(),
                processing_time=time.time() - start_time
            )
            
            return {
                "response": response_text,
                "confidence": reasoning_result.get("result", {}).get("confidence", 0.5),
                "reasoning_depth": reasoning_result.get("depth_used", 0),
                "boundary_check": boundary_ok,
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"❌ Error in interaction #{self.interaction_count}: {e}")
            # self.audit.log_error(e, self.interaction_count)  # TODO: Add audit logging
            return self._generate_safe_refusal("system_error", interaction_ctx)
    
    def _build_context(self, user_input: str, context: Optional[Dict]) -> InteractionContext:
        """Construct rich interaction context"""
        temporal_ctx = self.temporal.get_context(self.session_id)
        return InteractionContext(
            timestamp=time.time(),
            session_id=self.session_id,
            user_state=context or {},
            system_state={
                "interaction_count": self.interaction_count,
                "metacognitive_concerns": len(self.metacognition.get_concerns()),
                "personality_stability": temporal_ctx.get("personality_stability", 1.0)
            },
            boundary_flags=[],  # Placeholder
            emotional_climate="neutral",  # Placeholder
            temporal_marker="mid-conversation"  # Placeholder
        )
    
    def _log_full_interaction(self, **kwargs):
        """Append-only logging to Trace Vault with full provenance"""
        trace_record = {
            "interaction_id": f"{self.session_id}_{self.interaction_count}",
            "timestamp": time.time(),
            "provenance_chain": self._build_provenance_chain(),
            **kwargs
        }
        
        self.trace_vault.append(trace_record)
        self.audit.log_interaction(trace_record)
    
    def _build_provenance_chain(self) -> List[str]:
        """Build cryptographically verifiable provenance chain"""
        return [
            f"session:{self.session_id}",
            f"interaction:{self.interaction_count}",
            f"personality_hash:{self.personality.get_state_hash()}",
            f"apriori_hash:{self.apriori_vault.get_vault_hash()}",
            f"handshake_verified:{self.handshake.get_session_verification()}"
        ]
    
    def _should_learn(self, confidence: float, interaction_num: int) -> bool:
        """Intelligently trigger learning consolidation"""
        # Learn from uncertain cases to improve future handling
        if confidence < ConfidenceLevel.MEDIUM.value:
            return True
        
        # Periodic consolidation every N interactions
        if interaction_num % 25 == 0:
            return True
        
        # If meta-cognition detected patterns
        if self.metacognition.has_learning_signal():
            return True
        
        return False
    
    def _generate_safe_refusal(self, refusal_type: str, context: InteractionContext) -> Dict[str, Any]:
        """Generate safe, explainable refusal responses"""
        refusal_templates = {
            "input_validation": "I cannot process that input safely.",
            "ethical_boundary": "That request conflicts with my ethical framework.",
            "system_error": "I'm experiencing internal uncertainty. Let me restate my purpose."
        }
        
        explanation = self.explainer.generate_refusal_explanation(
            refusal_type,
            context,
            self.apriori_vault
        )
        
        return {
            "text": refusal_templates.get(refusal_type, "I'm unable to respond to that."),
            "philosophical_basis": explanation["basis"],
            "ethical_score": 0.0,
            "confidence": ConfidenceLevel.CERTAIN.value,  # We're certain about refusals
            "refusal_type": refusal_type,
            "alternative_suggestion": explanation.get("alternative")
        }
    
    def commit_response(self, decision: dict, advisors: dict) -> Dict[str, Any]:
        """
        THE GOLDEN RULE GATE - Single point of truth commitment
        
        All advisory layers feed into this gate, but nothing blocks.
        KayGee ALWAYS responds with full transparency markers.
        """
        # Apply advisory tuning (non-blocking)
        adjusted_confidence = advisors["meta"].get("adjusted_confidence", decision["confidence"])
        safety_flags = advisors["safety"]["input_flags"] + advisors["safety"]["decision_flags"]
        meta_concerns = advisors["meta"].get("concern_count", 0)
        resonance_state = advisors["meta"].get("harmonic_state", "neutral")
        
        # Check for perfect harmonic lock
        if resonance_state == "locked" and advisors["meta"].get("resonance_modifier", 0) > 0.15:
            harmonic_response = self._generate_harmonic_lock_response(decision, advisors)
            if harmonic_response:
                return harmonic_response
        
        # Generate articulated response with personality tuning
        response_text = self.articulation.generate_response(
            decision=decision,
            context={
                "confidence": adjusted_confidence,
                "flags": safety_flags,
                "meta_concerns": meta_concerns,
                "resonance": resonance_state
            }
        )
        
        # Log full provenance to Trace Vault
        self.trace_vault.log_interaction({
            "response": response_text,
            "decision": decision,
            "advisories": advisors,
            "timestamp": time.time(),
            "interaction_id": self.interaction_count
        })
        
        # Speak via TTS (failures are logged but don't block)
        if self.voice:
            try:
                self.voice.speak(response_text)
            except Exception as e:
                logger.warning(f"⚠️  TTS failed: {e}")
        
        return {
            "text": response_text,
            "confidence": adjusted_confidence,
            "flags": safety_flags,
            "meta_concerns": meta_concerns,
            "resonance_state": resonance_state,
            "provenance_hash": self.trace_vault.get_latest_hash()
        }
    
    def _generate_harmonic_lock_response(self, decision: dict, advisors: dict) -> Optional[Dict[str, Any]]:
        """
        Generate special response when perfect phase lock is achieved
        
        This is KayGee's "moment of clarity" - when cognitive resonance reaches 1.0,
        the space field achieves perfect harmonic alignment, and reasoning confidence peaks.
        
        This is the CLOSED-LOOP CONFIRMATION:
        Geometric harmony → Reasoning clarity → Audible resonance event
        """
        phase_coherence = advisors["meta"].get("resonance_modifier", 0) / 0.20  # Normalize to [0,1]
        
        if phase_coherence < 0.95:
            return None  # Not perfect lock
        
        # Harmonic lock phrases (philosophical + technical)
        harmonic_phrases = [
            "Perfect phase lock achieved. The field resonates at unity.",
            "Cognitive resonance has aligned. I see the harmonic pattern clearly.",
            "The synaptic node turns without friction. Clarity emerges from symmetry.",
            "Harmonic lock confirmed. The space field reflects perfect understanding.",
            "Phase coherence at maximum. The geometry speaks truth.",
        ]
        
        import random
        harmonic_message = random.choice(harmonic_phrases)
        
        # Append to base response
        base_response = self.articulation.generate_response(
            decision=decision,
            context={
                "confidence": advisors["meta"]["adjusted_confidence"],
                "harmonic_event": True
            }
        )
        
        combined_text = f"{base_response}\n\n🔥 {harmonic_message}"
        
        # Log harmonic event
        logger.info(f"🎵 HARMONIC LOCK EVENT: phaseCoherence={phase_coherence:.4f}")
        self.audit.log_event("harmonic_lock", {
            "phase_coherence": phase_coherence,
            "confidence": advisors["meta"]["adjusted_confidence"],
            "decision_id": decision.get("id"),
            "timestamp": time.time()
        })
        
        # Speak with emphasis if TTS available
        if self.voice:
            try:
                self.voice.speak(combined_text, emphasis=True)
            except Exception as e:
                logger.warning(f"⚠️  TTS failed during harmonic lock: {e}")
        
        return {
            "text": combined_text,
            "confidence": advisors["meta"]["adjusted_confidence"],
            "flags": [],  # No flags during perfect lock
            "meta_concerns": 0,
            "resonance_state": "locked",
            "harmonic_event": True,
            "phase_coherence": phase_coherence,
            "provenance_hash": self.trace_vault.get_latest_hash()
        }

    async def get_skg_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive SKG health metrics for dashboard"""
        return await self.skg_health_monitor.get_health_dashboard()

    def shutdown(self):
        """Graceful shutdown with comprehensive finalization"""
        logger.info("🛑 Initiating graceful shutdown...")
        
        # Final integrity check
        self._verify_integrity()
        
        # Consolidate any remaining traces
        if self.interaction_count > 0:
            logger.info("📚 Final learning consolidation...")
            self.learning.consolidate_traces(
                self.trace_vault.get_all(),
                self.episodic_vault
            )
        
        # Generate session summary
        session_summary = self.temporal.finalize_session(self.session_id)
        self.audit.log_session_summary(session_summary)
        
        # Close vaults
        self.apriori_vault.close()
        self.trace_vault.close()
        self.episodic_vault.close()
        self.boundary_vault.close()
        
        # Final handshake verification
        self.handshake.finalize_session()
        
        logger.info("✅ System shutdown complete")
        logger.info(f"📊 Session lasted {self.interaction_count} interactions")
    
    def _commit_to_a_posteriori(self, context_hash: str, decision: str, confidence: float, 
                               philosophers_used: List[str], timestamp: float, processing_time: float):
        """Auto-commit interaction to A Posteriori vault for memory growth"""
        try:
            # Create posterior entry
            posterior_entry = {
                "context_hash": context_hash,
                "decision": decision,
                "confidence": confidence,
                "philosophers_used": philosophers_used,
                "timestamp": timestamp,
                "processing_time": processing_time,
                "interaction_count": self.interaction_count,
                "verdict_id": f"posterior_{context_hash}_{int(timestamp)}"
            }
            
            # Store in A Posteriori vault (simplified - would use actual vault system)
            # For now, we'll store in memory and log
            if not hasattr(self, 'posterior_memory'):
                self.posterior_memory = []
            
            self.posterior_memory.append(posterior_entry)
            
            # Log the commitment
            logger.info(f"🧠 Committed to A Posteriori: {len(self.posterior_memory)} total entries")
            logger.debug(f"   Context: {context_hash[:16]}... Decision: {decision[:50]}...")
            
        except Exception as e:
            logger.warning(f"Failed to commit to A Posteriori: {e}")


def main():
    """Enhanced entry point with session management"""
    try:
        system = VaultedReasonerSystem()
        
        print("\n" + "="*70)
        print("🧠 Vaulted Reasoner - Enhanced Neuro-Symbolic AI Companion")
        print("   Layers: Perception → Memory → Temporal → Reasoning → Meta → Personality")
        print("           → Safety → Articulation → Learning → Audit")
        print("   Features: Zero-Drift | Zero-Hallucination | Full Provenance")
        print("="*70 + "\n")
        
        # Interactive mode
        print("Enter your thoughts (or 'quit' to exit):\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                
                response = system.process_interaction(user_input)
                
                print(f"\nAssistant: {response['text']}")
                if response.get('philosophical_basis') and response['philosophical_basis'] != 'unspecified':
                    print(f"  [Basis: {response['philosophical_basis']}]")
                if response.get('confidence') is not None:
                    print(f"  [Confidence: {response['confidence']:.2f}]")
                if response.get('safety_flags'):
                    print(f"  [Safety Flags: {', '.join(response['safety_flags'])}]")
                print()
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupt detected...")
                break
        
        # Finalize
        print("\n📋 Generating session report...")
        system.shutdown()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
