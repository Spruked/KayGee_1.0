"""
KayGee 1.0 - Wiring Verification Script
Tests all endpoints and integrations
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    
    try:
        # Core
        from src.core.protocols import ComponentIdentity, IdentityBoundComponent
        print("  ✅ Core protocols")
        
        # Memory & Merkle
        from src.memory.vault import VaultSystem, APrioriVault, TraceVault
        from src.memory.merkle_trace_vault import MerkleTraceVault, MerkleProof
        print("  ✅ Memory & Merkle vaults")
        
        # Temporal
        from src.temporal.context import TemporalContextLayer
        print("  ✅ Temporal context")
        
        # Meta-cognition
        from src.meta.cognition import MetaCognitiveMonitor
        print("  ✅ Meta-cognition")
        
        # Personality
        from src.consistency.personality import PersonalityCore
        print("  ✅ Personality core")
        
        # Audit
        from src.audit.transparency import AuditLogger, ExplanationGenerator
        print("  ✅ Audit & transparency")
        
        # Safety
        from src.boundary.safety import SafetyGuardian, BoundaryVault
        print("  ✅ Safety guardian")
        
        # Emotional
        from src.emotional.state import EmotionalStateIntegrator
        print("  ✅ Emotional state")
        
        # Perception
        from src.perception.classifier import PerceptionSystem
        print("  ✅ Perception system")
        
        # Reasoning
        from src.reasoning.recursive_loop import ReasoningEngine
        print("  ✅ Reasoning engine")
        
        # Articulation
        from src.articulation.nlg import ArticulationEngine, PersonalityTuner
        print("  ✅ Articulation engine")
        
        # Learning
        from src.learning.rule_induction import LearningSystem
        print("  ✅ Learning system")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}\n")
        return False

def test_merkle_vault():
    """Test Merkle vault functionality"""
    print("🔍 Testing Merkle vault...")
    
    try:
        from src.memory.merkle_trace_vault import MerkleTraceVault
        import os
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Create vault
        vault = MerkleTraceVault(path="data/test_merkle.jsonl")
        
        # Append entries
        for i in range(5):
            vault.append({"test": f"entry_{i}", "data": i})
        
        # Get proof
        proof = vault.get_proof(2)
        
        # Verify proof
        is_valid = MerkleTraceVault.verify_proof(proof)
        
        if is_valid:
            print(f"  ✅ Merkle proofs working")
            print(f"  ✅ Root: {vault.get_current_root()[:16]}...")
            print(f"  ✅ Entries: {len(vault.entries)}")
        else:
            print("  ❌ Proof verification failed")
            print(f"     Leaf: {proof.leaf_hash[:16]}...")
            print(f"     Root: {proof.root[:16]}...")
            print(f"     Proof hashes: {len(proof.proof_hashes)}")
            return False
        
        # Clean up
        Path("data/test_merkle.jsonl").unlink(missing_ok=True)
        
        print("✅ Merkle vault operational!\n")
        return True
        
    except Exception as e:
        print(f"❌ Merkle test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_identity_system():
    """Test cryptographic identity system"""
    print("🔍 Testing identity system...")
    
    try:
        from src.core.protocols import ComponentIdentity, SignedMessage
        import nacl.signing
        
        # Create identity with proper arguments
        signing_key = nacl.signing.SigningKey.generate()
        identity = ComponentIdentity(name="test_component", signing_key=signing_key)
        
        # Sign message
        message = SignedMessage.create(
            sender="test",
            recipient="receiver",
            payload={"test": "data"},
            sender_identity=identity
        )
        
        # Verify signature
        is_valid = message.verify(identity.verify_key)
        
        if is_valid:
            print(f"  ✅ Identity creation")
            print(f"  ✅ Message signing")
            print(f"  ✅ Signature verification")
            print(f"  ✅ Fingerprint: {identity.fingerprint[:16]}...")
        else:
            print("  ❌ Signature verification failed")
            return False
        
        print("✅ Identity system operational!\n")
        return True
        
    except Exception as e:
        print(f"❌ Identity test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False

def test_system_layers():
    """Test all system layers initialize"""
    print("🔍 Testing system layer initialization...")
    
    try:
        # Temporal
        from src.temporal.context import TemporalContextLayer
        temporal = TemporalContextLayer()
        temporal.initialize_session("test_session")
        print("  ✅ Temporal layer")
        
        # Meta-cognition
        from src.meta.cognition import MetaCognitiveMonitor
        meta = MetaCognitiveMonitor()
        meta.monitor(0.8, ["step1", "step2"], 1.5)
        print("  ✅ Meta-cognition layer")
        
        # Personality
        from src.consistency.personality import PersonalityCore
        personality = PersonalityCore()
        warmth = personality.get_current_trait("warmth")
        print(f"  ✅ Personality layer (warmth: {warmth})")
        
        # Safety
        from src.boundary.safety import SafetyGuardian, BoundaryVault
        from src.memory.vault import APrioriVault
        apriori = APrioriVault()
        safety = SafetyGuardian(apriori)
        result = safety.check_safety("help with homework", {})
        print(f"  ✅ Safety layer (approved: {result['approved']})")
        
        # Emotional
        from src.emotional.state import EmotionalStateIntegrator
        emotional = EmotionalStateIntegrator()
        state = emotional.analyze_emotion({"emotion": "happy"})
        print(f"  ✅ Emotional layer (tone: {state['detected_tone']})")
        
        print("✅ All layers operational!\n")
        return True
        
    except Exception as e:
        print(f"❌ Layer test failed: {e}\n")
        return False

def main():
    print("\n" + "="*60)
    print("  KAYGEE 1.0 - WIRING VERIFICATION")
    print("="*60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Identity System", test_identity_system()))
    results.append(("Merkle Vault", test_merkle_vault()))
    results.append(("System Layers", test_system_layers()))
    
    # Summary
    print("="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("  🎉 ALL TESTS PASSED - SYSTEM READY")
    else:
        print("  ⚠️  SOME TESTS FAILED - CHECK LOGS")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
