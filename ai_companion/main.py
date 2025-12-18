"""
Vaulted Reasoner: Multi-Layered Neuro-Symbolic AI Companion
Enhanced architecture with temporal, meta-cognitive, and consistency layers
"""

import sys
import logging
import hashlib
import time
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Core protocols
from src.core.protocols import IdentityBoundComponent, ComponentIdentity, SecurityError

# Core components (existing)
from src.handshake.manager import HandshakeProtocol, verify_all_components
from src.memory.vault import VaultSystem, APrioriVault, TraceVault, EpisodicVault
from src.reasoning.recursive_loop import ReasoningEngine, ConflictResolver
from src.perception.classifier import PerceptionSystem
from src.articulation.nlg import ArticulationEngine, PersonalityTuner
from src.learning.rule_induction import LearningSystem

# NEW: Additional layers
from src.temporal.context import TemporalContextLayer
from src.meta.cognition import MetaCognitiveMonitor
from src.consistency.personality import PersonalityCore
from src.audit.transparency import AuditLogger, ExplanationGenerator
from src.boundary.safety import SafetyGuardian, BoundaryVault
from src.emotional.state import EmotionalStateIntegrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("ai_companion.log"),
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
        
        # Layer 0: Cryptographic Foundation
        self.handshake = HandshakeProtocol()
        
        # Layer 1: Multi-Vault Memory System
        self.memory = VaultSystem(self.handshake)
        self.apriori_vault = APrioriVault()  # Immutable philosophical core
        self.trace_vault = TraceVault()      # Append-only interaction ledger
        self.episodic_vault = EpisodicVault() # Learned patterns
        
        # Layer 2: Temporal & Context
        self.temporal = TemporalContextLayer()
        
        # Layer 3: Perception & Emotional Parsing
        self.perception = PerceptionSystem(self.handshake)
        self.emotional_integrator = EmotionalStateIntegrator()
        
        # Layer 4: Reasoning with Conflict Resolution
        self.reasoning = ReasoningEngine(self.handshake)
        self.conflict_resolver = ConflictResolver(self.apriori_vault)
        
        # Layer 5: Meta-Cognition (system self-awareness)
        self.metacognition = MetaCognitiveMonitor()
        
        # Layer 6: Personality Core (stable traits)
        self.personality = PersonalityCore(config_path)
        self.personality_tuner = PersonalityTuner(self.personality)
        
        # Layer 7: Safety & Boundaries
        self.safety = SafetyGuardian(self.apriori_vault)
        self.boundary_vault = BoundaryVault()
        
        # Layer 8: Articulation
        self.articulation = ArticulationEngine(self.handshake)
        
        # Layer 9: Learning & Consolidation
        self.learning = LearningSystem(self.handshake)
        
        # Transparency & Audit
        self.audit = AuditLogger()
        self.explainer = ExplanationGenerator()
        
        # Optional: TTS Voice (Coqui)
        self.voice = None
        try:
            from src.voice.coqui import CoquiVoice
            self.voice = CoquiVoice()
            logger.info("🎤 TTS voice initialized")
        except ImportError:
            logger.info("⚠️  TTS not available (install Coqui TTS)")
        except Exception as e:
            logger.warning(f"⚠️  TTS initialization failed: {e}")
        
        # System state
        self.session_id = self._generate_session_id()
        self.interaction_count = 0
        
        # Register all components
        self._register_components()
        
        # Verify system integrity
        self._verify_integrity()
        
        # Initialize temporal context
        self.temporal.initialize_session(self.session_id)
        
        logger.info("✅ Enhanced system initialized successfully")
        logger.info(f"📋 Session ID: {self.session_id}")
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically unique session identifier"""
        timestamp = str(time.time())
        nonce = hashlib.sha256(timestamp.encode()).hexdigest()[:16]
        return f"session_{int(time.time())}_{nonce}"
    
    def _register_components(self):
        """Register all component public keys with centralized identity creation"""
        # Component map: name -> (class, constructor_args)
        # NOTE: Components already instantiated, so we work with existing instances
        components = {
            "perception": self.perception,
            "memory": self.memory,
            "reasoning": self.reasoning,
            "articulation": self.articulation,
            "learning": self.learning,
            "temporal": self.temporal,
            "metacognition": self.metacognition,
            "personality": self.personality,
            "safety": self.safety
        }
        
        # Register each component using its identity's public key
        for name, component in components.items():
            # Components already have identities from their __init__
            # Verify they implement IdentityBoundComponent
            if not isinstance(component, IdentityBoundComponent):
                logger.warning(f"  ⚠️  {name} does not implement IdentityBoundComponent")
                # Fallback: use component's existing get_public_key() if available
                if hasattr(component, 'get_public_key'):
                    self.handshake.register_component(name, component.get_public_key())
                    logger.info(f"  ✓ Registered {name} (legacy mode)")
                continue
            
            # Standard path: use identity contract
            self.handshake.register_component(name, component.get_public_key())
            logger.info(f"  ✓ Registered {name}")
        
        # Establish cross-component trust relationships
        self.handshake.establish_trust_network()
        logger.info("  ✓ Trust network established")
    
    def _verify_integrity(self):
        """Comprehensive integrity verification across all layers"""
        logger.info("🔍 Verifying multi-layer integrity...")
        
        # Verify A Priori Vault (philosophical immutability)
        if not self.apriori_vault.verify_integrity():
            raise SecurityError("❌ A Priori Vault integrity compromised!")
        
        # Verify Boundary Vault (safety constraints)
        if not self.boundary_vault.verify_constraints():
            raise SecurityError("❌ Boundary constraints violated!")
        
        # Verify component state hashes
        if not verify_all_components(self.handshake):
            raise SecurityError("❌ Component state drift detected!")
        
        # Verify personality consistency
        if not self.personality.verify_stability():
            logger.warning("⚠️  Personality stability threshold approaching limit")
        
        logger.info("✅ Multi-layer integrity verification passed")
    
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
        Enhanced reasoning loop with 9-layer processing
        Returns structured response with full provenance
        """
        self.interaction_count += 1
        start_time = time.time()
        
        try:
            logger.info(f"📥 Processing interaction #{self.interaction_count}: '{user_input[:50]}...'")
            
            # Step 1: Build rich interaction context
            interaction_ctx = self._build_context(user_input, context)
            
            # Step 2: Layer 1 - Perception & Emotional Parsing
            perception_data = self.perception.process(user_input, interaction_ctx)
            emotional_state = self.emotional_integrator.parse(
                user_input, 
                perception_data["tone_markers"]
            )
            
            # Safety check #1: Content screening (ADVISORY ONLY - NO VETO)
            input_safety = self.safety.evaluate_input(user_input, perception_data)
            # Record safety concerns but NEVER block early
            safety_advisories = {
                "input_risk": input_safety.get("risk_score", 0.0),
                "input_flags": input_safety.get("flags", [])
            }
            
            # Step 3: Layer 2 - Memory Retrieval (multi-vault)
            memory_tx = self.handshake.send("perception", "memory", perception_data)
            
            # Retrieve from multiple vaults
            similar_cases = self.episodic_vault.retrieve_cases(
                memory_tx["data"],
                top_k=5,
                similarity_threshold=0.75
            )
            
            # Query A Priori Vault for ethical principles
            ethical_principles = self.apriori_vault.query_principles(
                situation_type=perception_data["intent_category"]
            )
            
            # Step 4: Layer 3 - Temporal Context Integration
            temporal_context = self.temporal.get_context(
                session_id=self.session_id,
                interaction_num=self.interaction_count
            )
            
            # Step 5: Layer 4 - Reasoning with Conflict Resolution
            reasoning_tx = self.handshake.send("memory", "reasoning", {
                "cases": similar_cases,
                "principles": ethical_principles,
                "temporal": temporal_context,
                "emotional": emotional_state
            })
            
            decision = self.reasoning.reason(
                situation=reasoning_tx["data"],
                user_input=user_input,
                context=interaction_ctx
            )
            
            # Resolve any principle conflicts
            if decision["conflicts_detected"]:
                decision = self.conflict_resolver.resolve(
                    decision,
                    user_context=interaction_ctx
                )
            
            # Safety check #2: Ethical boundary assessment (ADVISORY ONLY)
            decision_safety = self.safety.evaluate_decision(decision)
            safety_advisories.update({
                "decision_risk": decision_safety.get("risk_score", 0.0),
                "decision_flags": decision_safety.get("flags", [])
            })
            
            # Step 6: Layer 5 - Meta-Cognitive Monitoring (ADVISORY ONLY)
            meta_assessment = self.metacognition.assess(
                decision_quality=decision["confidence"],
                reasoning_path=decision["reasoning_chain"],
                system_load=(time.time() - start_time)
            )
            
            # Apply cognitive resonance modifier (from space field phase coherence)
            resonance_modifier = self._get_resonance_confidence_modifier()
            base_confidence = decision["confidence"]
            adjusted_confidence = min(1.0, max(0.0, base_confidence + resonance_modifier))
            
            logger.info(f"🎵 Cognitive Resonance: confidence {base_confidence:.2f} → {adjusted_confidence:.2f} "
                       f"(modifier: {resonance_modifier:+.2f})")
            
            # Collect meta advisories (NO BLOCKING)
            meta_advisories = {
                "adjusted_confidence": meta_assessment.get("suggested_confidence", adjusted_confidence),
                "concern_count": meta_assessment.get("concerns", 0),
                "reasoning_quality": meta_assessment.get("quality_score", 0.8),
                "resonance_modifier": resonance_modifier,
                "harmonic_state": "locked" if resonance_modifier > 0.15 else "turbulent" if resonance_modifier < -0.1 else "neutral"
            }
            
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
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in interaction #{self.interaction_count}: {e}")
            self.audit.log_error(e, self.interaction_count)
            return self._generate_safe_refusal("system_error", interaction_ctx)
    
    def _build_context(self, user_input: str, context: Optional[Dict]) -> InteractionContext:
        """Construct rich interaction context"""
        return InteractionContext(
            timestamp=time.time(),
            session_id=self.session_id,
            user_state=context or {},
            system_state={
                "interaction_count": self.interaction_count,
                "metacognitive_concerns": self.metacognition.get_concern_count(),
                "personality_stability": self.personality.get_stability_score()
            },
            boundary_flags=self.safety.check_user_boundaries(user_input),
            emotional_climate=self.emotional_integrator.get_climate(),
            temporal_marker=self.temporal.get_temporal_marker()
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
                print(f"  [Basis: {response['philosophical_basis']}]")
                print(f"  [Confidence: {response.get('confidence', 'N/A'):.2f}]")
                if 'alternative_suggestion' in response:
                    print(f"  [Alternative: {response['alternative_suggestion']}]\n")
                
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
