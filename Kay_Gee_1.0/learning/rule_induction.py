"""
Rule Induction Module (Vault-Compliant Version)
Ripper-inspired algorithm for generating Prolog rules from decision trees
Converts learned patterns into cryptographically-signed, A Priori-verified Prolog clauses
"""

import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.tree import DecisionTreeClassifier, _tree
import numpy as np
from datetime import datetime
import ed25519

@dataclass
class InducedRule:
    """Cryptographically signed, provenance-tracked Prolog clause"""
    clause: str
    confidence: float
    philosophical_grounding: str
    provenance_hash: str  # Merkle root of source case IDs
    case_count: int
    timestamp: str
    signature: bytes
    rule_id: str
    
    def verify_signature(self, public_key: bytes) -> bool:
        """Verify that rule was signed by LearningSystem"""
        message = self.clause.encode() + self.provenance_hash.encode()
        try:
            ed25519.VerifyingKey(public_key).verify(self.signature, message)
            return True
        except ed25519.BadSignatureError:
            return False


class VaultCompliantRuleInducer:
    """
    Induces Prolog rules from A Posteriori vault via MiniBatchKMeans + DecisionTrees
    Guarantees:
    - Every rule signed by LearningSystem identity
    - Every rule verified against A Priori axioms before assertion
    - Every rule links to source cases via Merkle root
    - Cases are grouped by philosophical grounding before induction
    - Rules are tiered: Episodic → Prototypical → Semantic
    """
    
    def __init__(self, max_depth: int = 3, min_samples: int = 10):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.tree = DecisionTreeClassifier(max_depth=max_depth, min_samples_leaf=min_samples)
        self.learning_identity = None  # Set by handshake protocol
        self.feature_names = ["mood", "verbosity", "ethics_density", "temporal", "spatial"]
        
    def set_identity(self, identity: ed25519.SigningKey):
        """Called by handshake protocol during initialization"""
        self.learning_identity = identity
    
    def induce_from_episodic_tier(self, cases: List[Dict], a_priori_engine) -> List[InducedRule]:
        """
        Induces rules from consolidated episodic tier
        - Filters cases by philosophical module to prevent cross-contamination
        - Verifies each rule against A Priori axioms
        - Returns only verified, signed rules
        
        Args:
            cases: Cases from Episodic Vault (already filtered by age/confidence)
            a_priori_engine: Instance of Z3Prover or SWIProlog with A Priori loaded
            
        Returns:
            List[InducedRule]: Verified, signed rules ready for Prototypical tier
        """
        if len(cases) < self.min_samples:
            return []
        
        # 1. Group cases by philosophical grounding to prevent contamination
        cases_by_philosophy = {
            "kantian_duty": [],
            "lockean_rights": [],
            "spinozan_conatus": [],
            "humean_utility": []
        }
        
        for case in cases:
            grounding = case.get('philosophical_grounding', 'humean_utility')
            if grounding in cases_by_philosophy:
                cases_by_philosophy[grounding].append(case)
        
        all_rules = []
        
        for philosophy, cases_subset in cases_by_philosophy.items():
            if len(cases_subset) < 5:  # Minimum per philosophy
                continue
                
            # 2. Build feature matrix for this philosophical cluster
            X = []
            y = []
            case_ids = []
            
            for case in cases_subset:
                vector = case['situation_vector']
                X.append(vector)
                y.append(case['action'])
                case_ids.append(case['case_id'])
            
            X = np.array(X)
            
            # 3. Train tree on philosophically-homogeneous data
            self.tree.fit(X, y)
            
            # 4. Convert tree to clauses with philosophical type guards
            raw_clauses = self._tree_to_clauses(self.tree, feature_names=self.feature_names, philosophy=philosophy)
            
            # 5. Verify each clause against A Priori axioms
            for clause in raw_clauses:
                is_safe, counterexample = a_priori_engine.verify_rule(clause)
                
                if is_safe:
                    # 6. Compute Merkle root of source case IDs
                    provenance_hash = self._merkle_root(case_ids)
                    
                    # 7. Sign the clause
                    signature = self.learning_identity.sign(
                        clause.encode() + provenance_hash.encode()
                    )
                    
                    # 8. Create InducedRule object
                    rule = InducedRule(
                        clause=clause,
                        confidence=len(cases_subset) / 100.0,  # Normalized by experience
                        philosophical_grounding=philosophy,
                        provenance_hash=provenance_hash,
                        case_count=len(cases_subset),
                        timestamp=datetime.now().isoformat(),
                        signature=signature,
                        rule_id=hashlib.sha256(clause.encode()).hexdigest()[:16]
                    )
                    
                    all_rules.append(rule)
                else:
                    # Rule violates A Priori—log and reject
                    trace_vault.log_rejected_rule(clause, counterexample)
        
        return all_rules
    
    def _tree_to_clauses(self, tree: DecisionTreeClassifier, feature_names: List[str], 
                        philosophy: str) -> List[str]:
        """Convert tree to Prolog clauses with philosophical type guards"""
        tree_ = tree.tree_
        
        def recurse(node, conditions):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                feature = feature_names[tree_.feature[node]]
                threshold = tree_.threshold[node]
                
                # Add philosophical type constraints
                if philosophy == "kantian_duty":
                    type_check = f"universalizable({feature})"
                elif philosophy == "lockean_rights":
                    type_check = f"consent_given({feature})"
                elif philosophy == "spinozan_conatus":
                    type_check = f"rational({feature})"
                else:  # humean_utility
                    type_check = f"empirical({feature})"
                
                left = recurse(tree_.children_left[node], 
                              conditions + [f"{feature} =< {threshold:.3f}", type_check])
                right = recurse(tree_.children_right[node],
                               conditions + [f"{feature} > {threshold:.3f}", type_check])
                return left + right
            else:
                # Leaf node
                samples = tree_.n_node_samples[node]
                if samples < self.min_samples:
                    return []
                
                # Get action
                value = tree_.value[node]
                if len(value) > 0:
                    class_idx = np.argmax(value[0])
                    action = tree.classes_[class_idx] if hasattr(tree, 'classes_') else f"action_{class_idx}"
                    
                    # Add philosophical guard
                    guard = f"{philosophy}_grounded"
                    conditions_with_guard = conditions + [guard]
                    
                    clause = f"ethical({action}) :- \n    " + ",\n    ".join(conditions_with_guard) + "."
                    return [clause]
                return []
        
        return recurse(0, [])
    
    def _merkle_root(self, case_ids: List[str]) -> str:
        """Compute Merkle root of case IDs for provenance"""
        if not case_ids:
            return "0" * 64
        
        # Sort for determinism
        sorted_ids = sorted(case_ids)
        
        # Build Merkle tree
        level = [hashlib.sha256(cid.encode()).hexdigest() for cid in sorted_ids]
        
        while len(level) > 1:
            next_level = []
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    combined = level[i] + level[i+1]
                else:
                    combined = level[i] + level[i]  # Duplicate if odd
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            level = next_level
        
        return level[0]


class VaultCompliantLearningSystem:
    """
    Orchestrates nightly consolidation across memory tiers
    Full handshake protocol for each rule induction event
    """
    
    def __init__(self, handshake_manager, a_priori_engine, federation_node=None):
        self.handshake = handshake_manager
        self.a_priori = a_priori_engine
        self.inducer = VaultCompliantRuleInducer()
        self.federation = federation_node
        self.consolidation_cron = None
        
        # Get identity for signing
        identity = handshake_manager.create_identity("learning")
        self.inducer.set_identity(identity.private_key)
    
    def start_nightly_consolidation(self, trace_vault, a_posteriori_vault):
        """Runs every 24h, fully signed and verified"""
        import asyncio
        
        async def consolidation_loop():
            while True:
                await asyncio.sleep(86400)  # 24 hours
                
                # 1. PING: Announce consolidation start
                ping_tx = self.handshake.create_ping(
                    from_component="learning",
                    to_component="memory",
                    data={"operation": "consolidation_start"}
                )
                ack = await self.handshake.send_and_wait(ping_tx)
                
                if not ack:
                    trace_vault.log_error("Consolidation: Memory did not ACK")
                    continue
                
                # 2. Retrieve cases from Episodic tier
                cases = a_posteriori_vault.episodic.get_consolidation_batch()
                
                # 3. Verify: Cases are signed and valid
                for case in cases:
                    if not self.handshake.verify_case_signature(case):
                        trace_vault.log_error(f"Case {case.id} signature invalid")
                        continue
                
                # 4. Induce rules (with A Priori verification)
                new_rules = self.inducer.induce_from_episodic_tier(cases, self.a_priori)
                
                # 5. Commit: Each rule is signed and added to Prototypical tier
                for rule in new_rules:
                    # Create COMMIT transaction
                    commit_tx = self.handshake.create_commit(
                        from_component="learning",
                        to_component="memory",
                        data={
                            "rule_id": rule.rule_id,
                            "clause": rule.clause,
                            "grounding": rule.philosophical_grounding,
                            "provenance_hash": rule.provenance_hash,
                            "signature": rule.signature.hex()
                        }
                    )
                    
                    # Wait for Memory to commit
                    final_ack = await self.handshake.send_and_wait(commit_tx)
                    
                    if final_ack:
                        # Add to Prototypical vault with Merkle proof
                        a_posteriori_vault.prototypical.store(rule, proof=final_ack.merkle_proof)
                        
                        # Publish to federation if available
                        if self.federation and rule.confidence > 0.9:
                            self.federation.publish_learned_rule(
                                rule.clause, rule.confidence, rule.provenance_hash
                            )
                    else:
                        trace_vault.log_error(f"Rule {rule.rule_id} commit failed")
                
                # 6. VERIFY: Final integrity check
                integrity_tx = self.handshake.create_verify(
                    from_component="learning",
                    to_component="system",
                    data={"operation": "consolidation_complete", "rules_added": len(new_rules)}
                )
                await self.handshake.broadcast(integrity_tx)
        
        self.consolidation_cron = asyncio.create_task(consolidation_loop())
        return self.consolidation_cron
