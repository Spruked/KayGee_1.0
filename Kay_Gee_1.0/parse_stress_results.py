#!/usr/bin/env python3
"""
Parse and display stress test results
"""

import json

def main():
    with open('stress_test_results.json', 'r') as f:
        data = json.load(f)

    print('🔬 STRESS TEST RESULTS SUMMARY')
    print('='*50)
    print(f'Domains tested: {len(data["test_config"]["domains"])}')
    print(f'Iterations: {data["test_config"]["iterations"]}')
    print(f'Candidates tested: {len(data["candidates"])}')
    print()

    for i, candidate in enumerate(data['candidates'], 1):
        principle = candidate['principle'][:60] + '...' if len(candidate['principle']) > 60 else candidate['principle']
        print(f'Candidate {i}: {principle}')
        print(f'  Overall Resonance: {candidate["overall_resonance"]:.3f}')
        print(f'  Stability: {candidate["resonance_stability"]:.3f}')
        print(f'  Diversity: {candidate["domain_diversity_score"]:.3f}')
        print(f'  Original Resonance: {candidate["original_resonance"]:.3f}')

        # Domain breakdown
        print('  Domain Performance:')
        for domain, results in candidate['domain_results'].items():
            print(f'    {domain}: {results["avg_resonance"]:.3f} (std: {results["resonance_std"]:.3f})')
        print()

if __name__ == "__main__":
    main()