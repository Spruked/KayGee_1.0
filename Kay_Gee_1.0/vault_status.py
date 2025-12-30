#!/usr/bin/env python3
"""
Quick status check for Seed Candidate Vault
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import vaults

def main():
    print("🔍 Seed Candidate Vault Status")
    print("="*40)

    # Initialize vault manager
    vm = vaults.VaultManager()
    vm.initialize({})

    # Get summary
    summary = vm.seed_candidate_vault.get_dashboard_summary()

    print(f"Total Candidates: {summary['total_candidates']}")
    print(f"Quarantined: {summary['quarantined']}")
    print(f"Under Review: {summary['under_review']}")
    print(f"Promoted: {summary['promoted']}")
    print(f"Rejected: {summary['rejected']}")
    print(f"Require Review: {summary['requires_review']}")

    # Show candidates requiring review
    if summary['requires_review'] > 0:
        print(f"\n🚨 {summary['requires_review']} candidates require immediate review:")
        requiring_review = vm.seed_candidate_vault.requires_human_review()
        for i, candidate in enumerate(requiring_review[:3], 1):  # Show first 3
            print(f"\n{i}. {candidate.principle[:80]}...")
            print(f"   Resonance: {vm.seed_candidate_vault._calculate_mean_resonance(candidate.resonance_history):.3f}")
            print(f"   Queries: {candidate.query_volume}")

    print("\n🌌 Epistemic discipline maintained - no automatic promotion to Seed vault")

if __name__ == "__main__":
    main()