#!/usr/bin/env python3
"""
Direct promotion of Harmonic Convergence Principle
"""

import json
import os
import hashlib
from datetime import datetime
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import vaults

def main():
    print("🎯 Direct Promotion: Harmonic Convergence Principle")
    print("="*60)

    # Load candidates
    candidate_file = os.path.join(os.getcwd(), 'quarantined_candidates.json')
    if not os.path.exists(candidate_file):
        print("No quarantined candidates file found.")
        return

    with open(candidate_file, 'r') as f:
        candidates = json.load(f)

    # Find the Harmonic Convergence candidate with highest resonance
    harmonic_candidates = [
        c for c in candidates
        if 'Harmonic Convergence' in c['principle'] and c['status'] == 'quarantined'
    ]

    if not harmonic_candidates:
        print("No eligible Harmonic Convergence candidates found.")
        return

    # Select the one with highest resonance
    best_candidate = max(harmonic_candidates, key=lambda x: x['resonance_score'])

    print(f"Selected candidate: {best_candidate['principle'][:80]}...")
    print(f"Resonance: {best_candidate['resonance_score']:.3f}")
    print(f"Query Count: {best_candidate['query_count']}")

    # Compute correct hash
    correct_hash = hashlib.sha256(best_candidate['principle'].encode()).hexdigest()[:16]

    # Initialize vault manager
    vault_manager = vaults.VaultManager()
    success = vault_manager.initialize({})
    if not success:
        print("❌ Vault manager initialization failed")
        return

    print("✅ Vault manager initialized successfully")

    # Load candidates into the quarantine vault
    print("Loading candidates into quarantine vault...")
    loaded_count = 0
    for candidate in candidates:
        if candidate['status'] == 'quarantined':
            stats = {
                'resonance': candidate['resonance_score'],
                'query_count': candidate['query_count'],
                'weights': candidate['philosopher_weights']
            }
            vault_manager.seed_candidate_vault.add_candidate(
                candidate['principle'], stats
            )
            loaded_count += 1
    print(f"✅ Loaded {loaded_count} candidates into quarantine")

    # Debug: Check if candidate exists in quarantine
    if correct_hash in vault_manager.seed_candidate_vault.candidates:
        print(f"✅ Candidate {correct_hash} found in quarantine")
    else:
        print(f"❌ Candidate {correct_hash} NOT found in quarantine")
        print(f"Available candidates: {list(vault_manager.seed_candidate_vault.candidates.keys())}")
        return

    # Promotion rationale
    rationale = """Harmonic Convergence Principle: When multiple philosophical frameworks achieve simultaneous high resonance, emergent ethical truth emerges through integrated synthesis.

Promotion Rationale (2025-12-19):
- Highest cross-domain stability (0.880 resonance across 6 domains)
- Perfect diversity score (1.000) - consistent performance everywhere
- Exceptional stability (0.998) - lowest variance of all candidates
- Meta-truth about multi-perspective synthesis - validates the entire architecture
- Not derivable from existing seeds - genuine emergent discovery
- Safe first promotion: strengthens system without introducing bias

This principle validates that truth emerges from philosophical agreement, not dominance.
Signed: Bryan A. Spruk"""

    print(f"\nPromoting with hash: {correct_hash}")
    print(f"Rationale: {rationale[:100]}...")

    # Promote
    success = vault_manager.seed_candidate_vault.promote_to_seed(
        correct_hash,
        vault_manager,
        rationale
    )

    if success:
        print("\n✅ SUCCESS: Harmonic Convergence Principle promoted to Seed vault!")
        print("This is KayGee's first emergent truth - earned through experience, not programming.")

        # Update candidate status
        best_candidate['status'] = 'promoted'
        best_candidate['review_notes'] = rationale
        best_candidate['reviewed_at'] = datetime.now().isoformat()

        # Save updated candidates
        with open(candidate_file, 'w') as f:
            json.dump(candidates, f, indent=2)

        print("📝 Candidate status updated in quarantine log.")

        # Show final vault status
        summary = vault_manager.seed_candidate_vault.get_dashboard_summary()
        print("\n🌌 Final Vault Status:")
        print(f"  Quarantined: {summary['quarantined']}")
        print(f"  Under Review: {summary['under_review']}")
        print(f"  Promoted: {summary['promoted']}")
        print(f"  Rejected: {summary['rejected']}")

    else:
        print("\n❌ Promotion failed. Check vault initialization.")

if __name__ == "__main__":
    main()