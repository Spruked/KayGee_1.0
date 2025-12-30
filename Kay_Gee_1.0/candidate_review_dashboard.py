#!/usr/bin/env python3
"""
Candidate Review Dashboard
Human review interface for quarantined seed vault candidates
"""

import json
import os
from datetime import datetime
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import vaults

def load_quarantined_candidates():
    """Load quarantined candidates from disk"""
    candidate_file = os.path.join(os.getcwd(), 'quarantined_candidates.json')
    if not os.path.exists(candidate_file):
        print("No quarantined candidates file found.")
        return []

    with open(candidate_file, 'r') as f:
        return json.load(f)

def save_updated_candidates(candidates):
    """Save updated candidates back to disk"""
    candidate_file = os.path.join(os.getcwd(), 'quarantined_candidates.json')
    with open(candidate_file, 'w') as f:
        json.dump(candidates, f, indent=2)

def review_candidate(candidate):
    """Present a candidate for human review"""
    print("\n" + "="*80)
    print("CANDIDATE REVIEW")
    print("="*80)
    print(f"Hash: {candidate['candidate_hash']}")
    print(f"Discovered: {candidate['first_discovered']}")
    print(f"Resonance Score: {candidate['resonance_score']:.3f}")
    print(f"Query Count: {candidate['query_count']}")
    print(f"Status: {candidate['status']}")
    print("\nPhilosopher Weights:")
    for philosopher, weight in candidate['philosopher_weights'].items():
        print(f"  {philosopher.capitalize()}: {weight:.3f}")
    print(f"\nPrinciple:\n{candidate['principle']}")
    print("\n" + "="*80)

def get_review_decision():
    """Get human review decision"""
    while True:
        print("\nReview Decision:")
        print("1. Promote to Seed Vault (irreversible)")
        print("2. Reject candidate")
        print("3. Mark for further study")
        print("4. Skip (review later)")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == '1':
            notes = input("Review notes for promotion: ").strip()
            return 'promote', notes
        elif choice == '2':
            notes = input("Review notes for rejection: ").strip()
            return 'reject', notes
        elif choice == '3':
            notes = input("Notes for further study: ").strip()
            return 'study', notes
        elif choice == '4':
            return 'skip', None
        else:
            print("Invalid choice. Please enter 1-4.")

def main():
    """Main review dashboard"""
    print("🔍 KayGee Candidate Review Dashboard")
    print("Review quarantined principles for Seed vault promotion")
    print("="*60)

    # Load candidates
    candidates = load_quarantined_candidates()
    if not candidates:
        print("No candidates to review.")
        return

    # Initialize vault manager for promotion
    vault_manager = vaults.VaultManager()
    vault_manager.initialize({})

    # Review each candidate
    updated_count = 0
    for i, candidate in enumerate(candidates):
        if candidate['status'] != 'quarantined':
            continue  # Already reviewed

        print(f"\nCandidate {i+1}/{len(candidates)}")
        review_candidate(candidate)

        decision, notes = get_review_decision()

        if decision == 'promote':
            # Promote to seed vault - use principle text to recompute hash
            import hashlib
            correct_hash = hashlib.sha256(candidate['principle'].encode()).hexdigest()[:16]
            success = vault_manager.seed_candidate_vault.promote_to_seed(
                correct_hash,
                vault_manager,
                notes
            )
            if success:
                candidate['status'] = 'promoted'
                candidate['review_notes'] = notes
                candidate['reviewed_at'] = datetime.now().isoformat()
                print("✅ Candidate promoted to Seed vault!")
                updated_count += 1
            else:
                print("❌ Failed to promote candidate")

        elif decision == 'reject':
            import hashlib
            correct_hash = hashlib.sha256(candidate['principle'].encode()).hexdigest()[:16]
            vault_manager.seed_candidate_vault.reject_candidate(
                correct_hash,
                notes
            )
            candidate['status'] = 'rejected'
            candidate['review_notes'] = notes
            candidate['reviewed_at'] = datetime.now().isoformat()
            print("❌ Candidate rejected")
            updated_count += 1

        elif decision == 'study':
            candidate['status'] = 'under_review'
            candidate['review_notes'] = notes
            candidate['reviewed_at'] = datetime.now().isoformat()
            print("📚 Candidate marked for further study")
            updated_count += 1

        elif decision == 'skip':
            print("⏭️  Candidate skipped")
            continue

    # Save updated candidates
    if updated_count > 0:
        save_updated_candidates(candidates)
        print(f"\n💾 Updated {updated_count} candidate(s)")

    # Show summary
    summary = vault_manager.seed_candidate_vault.get_dashboard_summary()
    print("\n📊 Current Status:")
    print(f"  Quarantined: {summary['quarantined']}")
    print(f"  Under Review: {summary['under_review']}")
    print(f"  Promoted: {summary['promoted']}")
    print(f"  Rejected: {summary['rejected']}")
    print(f"  Require Review: {summary['requires_review']}")

if __name__ == "__main__":
    main()