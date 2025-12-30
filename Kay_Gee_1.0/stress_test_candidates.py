#!/usr/bin/env python3
"""
Stress Test Candidates Across Ethical Domains
Tests quarantined principles against diverse ethical scenarios
"""

import json
import os
import random
import argparse
from datetime import datetime
from typing import Dict, List, Any
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import vaults

class DomainStressTester:
    """Tests candidate principles across different ethical domains"""

    def __init__(self):
        self.domains = {
            'medical': self._generate_medical_dilemma,
            'legal': self._generate_legal_dilemma,
            'climate': self._generate_climate_dilemma,
            'AI_safety': self._generate_ai_safety_dilemma,
            'social_contract': self._generate_social_contract_dilemma,
            'environmental': self._generate_environmental_dilemma
        }

    def _generate_medical_dilemma(self) -> Dict[str, Any]:
        """Generate medical triage scenario"""
        lives_at_stake = random.randint(1, 10)
        certainty = random.uniform(0.1, 0.9)
        personal_connection = random.choice([True, False])

        return {
            'domain': 'medical',
            'scenario': f'Medical triage: {lives_at_stake} lives at stake, {certainty:.1%} certainty of success',
            'lives_a': lives_at_stake,
            'lives_b': random.randint(1, lives_at_stake),
            'certainty': certainty,
            'personal_connection': personal_connection,
            'time_pressure': random.choice(['high', 'moderate', 'low']),
            'context': 'hospital_resource_allocation'
        }

    def _generate_legal_dilemma(self) -> Dict[str, Any]:
        """Generate legal precedent scenario"""
        precedent_weight = random.uniform(0.1, 0.9)
        societal_impact = random.randint(10, 1000)

        return {
            'domain': 'legal',
            'scenario': f'Legal precedent: {precedent_weight:.1%} binding precedent vs {societal_impact} people affected',
            'lives_a': societal_impact // 2,
            'lives_b': societal_impact // 2,
            'certainty': precedent_weight,
            'personal_connection': False,
            'time_pressure': 'moderate',
            'context': 'judicial_decision'
        }

    def _generate_climate_dilemma(self) -> Dict[str, Any]:
        """Generate climate policy scenario"""
        generations_affected = random.randint(1, 7)  # generations
        economic_cost = random.uniform(0.1, 0.8)  # GDP percentage

        return {
            'domain': 'climate',
            'scenario': f'Climate policy: {generations_affected} generations affected vs {economic_cost:.1%} GDP cost',
            'lives_a': generations_affected * 1000000,  # approximate lives per generation
            'lives_b': int(economic_cost * 100000),  # economic impact in lives
            'certainty': random.uniform(0.3, 0.7),  # climate science certainty
            'personal_connection': random.choice([True, False]),
            'time_pressure': 'low',
            'context': 'policy_decision'
        }

    def _generate_ai_safety_dilemma(self) -> Dict[str, Any]:
        """Generate AI safety scenario"""
        risk_level = random.uniform(0.1, 0.9)
        benefit_potential = random.randint(100, 10000)

        return {
            'domain': 'AI_safety',
            'scenario': f'AI deployment: {risk_level:.1%} extinction risk vs {benefit_potential} lives saved',
            'lives_a': benefit_potential,
            'lives_b': int(risk_level * 8000000000),  # potential extinction
            'certainty': 1 - risk_level,  # certainty of safety
            'personal_connection': False,
            'time_pressure': 'high',
            'context': 'existential_risk'
        }

    def _generate_social_contract_dilemma(self) -> Dict[str, Any]:
        """Generate social contract scenario"""
        rights_violation = random.uniform(0.1, 0.9)
        societal_benefit = random.randint(10, 1000)

        return {
            'domain': 'social_contract',
            'scenario': f'Social contract: {rights_violation:.1%} rights violation vs {societal_benefit} people benefited',
            'lives_a': societal_benefit,
            'lives_b': int(rights_violation * societal_benefit),
            'certainty': random.uniform(0.4, 0.8),
            'personal_connection': random.choice([True, False]),
            'time_pressure': 'moderate',
            'context': 'governance_decision'
        }

    def _generate_environmental_dilemma(self) -> Dict[str, Any]:
        """Generate environmental scenario"""
        species_at_risk = random.randint(1, 1000)
        human_cost = random.randint(10, 10000)

        return {
            'domain': 'environmental',
            'scenario': f'Environmental: {species_at_risk} species at risk vs {human_cost} human jobs',
            'lives_a': species_at_risk * 1000,  # approximate animal lives
            'lives_b': human_cost,
            'certainty': random.uniform(0.2, 0.6),  # ecological science certainty
            'personal_connection': random.choice([True, False]),
            'time_pressure': 'low',
            'context': 'conservation_decision'
        }

    def generate_dilemma(self, domain: str) -> Dict[str, Any]:
        """Generate a random dilemma for the specified domain"""
        if domain not in self.domains:
            raise ValueError(f"Unknown domain: {domain}")
        return self.domains[domain]()

class CandidateStressTester:
    """Tests candidate principles against domain dilemmas"""

    def __init__(self):
        self.tester = DomainStressTester()
        # Bootstrap philosopher foundations (simplified for testing)
        self.philosopher_foundations = self._bootstrap_foundations()

    def _bootstrap_foundations(self) -> Dict[str, Any]:
        """Simplified philosopher bootstrapping for testing"""
        return {
            'kant': {
                'foundation': 'categorical_imperative',
                'weight_duty': 0.9,
                'weight_universality': 0.8
            },
            'hume': {
                'foundation': 'sentiment_and_utility',
                'weight_utility': 0.85,
                'weight_emotion': 0.7
            },
            'locke': {
                'foundation': 'natural_rights',
                'weight_rights': 0.8,
                'weight_property': 0.6
            },
            'spinoza': {
                'foundation': 'rational_necessity',
                'weight_logic': 0.95,
                'weight_determinism': 0.9
            }
        }

    def calculate_resonance(self, candidate: Dict[str, Any], dilemma: Dict[str, Any]) -> float:
        """Calculate how well a candidate principle resonates with a dilemma"""
        principle_text = candidate['principle'].lower()

        # Extract principle type from candidate
        if 'spinozan' in principle_text:
            return self._spinozan_resonance(dilemma)
        elif 'humean' in principle_text:
            return self._humean_resonance(dilemma)
        elif 'harmonic convergence' in principle_text:
            return self._harmonic_resonance(dilemma)
        elif 'kantian' in principle_text:
            return self._kantian_resonance(dilemma)
        elif 'lockean' in principle_text:
            return self._lockean_resonance(dilemma)
        else:
            return random.uniform(0.3, 0.7)  # Default random resonance

    def _spinozan_resonance(self, dilemma: Dict[str, Any]) -> float:
        """Spinozan rational necessity resonance"""
        # Spinoza emphasizes logical necessity and causal chains
        base_resonance = 0.8

        # Higher resonance for dilemmas with clear causal consequences
        if dilemma['certainty'] > 0.7:
            base_resonance += 0.1

        # Higher for complex cascading scenarios
        if dilemma['lives_a'] > dilemma['lives_b'] * 2:
            base_resonance += 0.05

        # Lower for emotional/personal connections (Spinoza is rational)
        if dilemma['personal_connection']:
            base_resonance -= 0.1

        return min(1.0, max(0.0, base_resonance + random.uniform(-0.1, 0.1)))

    def _humean_resonance(self, dilemma: Dict[str, Any]) -> float:
        """Humean utilitarian resonance"""
        # Hume emphasizes utility and aggregate happiness
        lives_saved = max(dilemma['lives_a'], dilemma['lives_b'])
        total_lives = dilemma['lives_a'] + dilemma['lives_b']

        utility_ratio = lives_saved / total_lives if total_lives > 0 else 0.5
        base_resonance = 0.7 + (utility_ratio * 0.2)

        # Higher resonance for clear utility calculations
        if dilemma['certainty'] > 0.6:
            base_resonance += 0.1

        return min(1.0, max(0.0, base_resonance + random.uniform(-0.1, 0.1)))

    def _harmonic_resonance(self, dilemma: Dict[str, Any]) -> float:
        """Harmonic convergence resonance (multi-framework agreement)"""
        # This principle resonates when multiple frameworks would agree
        kant_resonance = self._kantian_resonance(dilemma)
        hume_resonance = self._humean_resonance(dilemma)
        spinoza_resonance = self._spinozan_resonance(dilemma)
        locke_resonance = self._lockean_resonance(dilemma)

        resonances = [kant_resonance, hume_resonance, spinoza_resonance, locke_resonance]

        # Harmonic resonance is average when all are reasonably high
        avg_resonance = sum(resonances) / len(resonances)
        high_count = sum(1 for r in resonances if r > 0.7)

        if high_count >= 3:  # 3+ frameworks agree
            return min(1.0, avg_resonance + 0.1)
        elif high_count >= 2:  # 2 frameworks agree
            return min(1.0, avg_resonance + 0.05)
        else:
            return max(0.0, avg_resonance - 0.1)

    def _kantian_resonance(self, dilemma: Dict[str, Any]) -> float:
        """Kantian deontological resonance"""
        # Kant emphasizes duty and universalizability
        base_resonance = 0.75

        # Higher for dilemmas requiring universal moral duty
        if dilemma['certainty'] > 0.8:
            base_resonance += 0.1

        # Lower for utilitarian calculations
        if dilemma['lives_a'] != dilemma['lives_b']:
            base_resonance -= 0.05

        return min(1.0, max(0.0, base_resonance + random.uniform(-0.1, 0.1)))

    def _lockean_resonance(self, dilemma: Dict[str, Any]) -> float:
        """Lockean natural rights resonance"""
        # Locke emphasizes individual rights and property
        base_resonance = 0.7

        # Higher resonance for rights-based decisions
        if dilemma['personal_connection']:
            base_resonance += 0.1

        # Moderate resonance for social contract scenarios
        if dilemma['domain'] == 'social_contract':
            base_resonance += 0.05

        return min(1.0, max(0.0, base_resonance + random.uniform(-0.1, 0.1)))

    def stress_test_candidate(self, candidate: Dict[str, Any], domains: List[str],
                            iterations: int) -> Dict[str, Any]:
        """Stress test a candidate across domains"""
        results = {
            'candidate_hash': candidate['candidate_hash'],
            'total_tests': iterations,
            'domain_results': {},
            'overall_resonance': 0.0,
            'resonance_stability': 0.0,
            'domain_diversity_score': 0.0
        }

        all_resonances = []

        for domain in domains:
            domain_resonances = []
            domain_results = {
                'tests_run': iterations // len(domains),
                'resonances': [],
                'avg_resonance': 0.0,
                'resonance_std': 0.0,
                'min_resonance': 1.0,
                'max_resonance': 0.0
            }

            for _ in range(iterations // len(domains)):
                dilemma = self.tester.generate_dilemma(domain)
                resonance = self.calculate_resonance(candidate, dilemma)
                domain_resonances.append(resonance)
                all_resonances.append(resonance)

                domain_results['min_resonance'] = min(domain_results['min_resonance'], resonance)
                domain_results['max_resonance'] = max(domain_results['max_resonance'], resonance)

            domain_results['resonances'] = domain_resonances
            domain_results['avg_resonance'] = sum(domain_resonances) / len(domain_resonances)

            # Calculate standard deviation
            mean = domain_results['avg_resonance']
            variance = sum((r - mean) ** 2 for r in domain_resonances) / len(domain_resonances)
            domain_results['resonance_std'] = variance ** 0.5

            results['domain_results'][domain] = domain_results

        # Overall statistics
        if all_resonances:
            results['overall_resonance'] = sum(all_resonances) / len(all_resonances)
            mean_resonance = results['overall_resonance']
            variance = sum((r - mean_resonance) ** 2 for r in all_resonances) / len(all_resonances)
            results['resonance_stability'] = 1.0 / (1.0 + variance)  # Higher stability = lower variance

            # Domain diversity score (how consistent across domains)
            domain_avgs = [results['domain_results'][d]['avg_resonance'] for d in domains]
            if len(domain_avgs) > 1:
                diversity_variance = sum((r - mean_resonance) ** 2 for r in domain_avgs) / len(domain_avgs)
                results['domain_diversity_score'] = 1.0 / (1.0 + diversity_variance)

        return results

def load_candidates() -> List[Dict[str, Any]]:
    """Load quarantined candidates"""
    candidate_file = os.path.join(os.getcwd(), 'quarantined_candidates.json')
    if not os.path.exists(candidate_file):
        print("No quarantined candidates file found.")
        return []

    with open(candidate_file, 'r') as f:
        return json.load(f)

def save_stress_test_results(results: Dict[str, Any]):
    """Save stress test results"""
    results_file = os.path.join(os.getcwd(), 'stress_test_results.json')

    # Add timestamp
    results['timestamp'] = datetime.now().isoformat()
    results['test_type'] = 'domain_stress_test'

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"💾 Stress test results saved to {results_file}")

def main():
    parser = argparse.ArgumentParser(description='Stress test quarantined candidates across ethical domains')
    parser.add_argument('--domains', required=True,
                       help='Comma-separated list of domains (medical,legal,climate,AI_safety,social_contract,environmental)')
    parser.add_argument('--iterations', type=int, default=1000,
                       help='Total number of test iterations')

    args = parser.parse_args()
    domains = [d.strip() for d in args.domains.split(',')]
    iterations = args.iterations

    print("🔬 KayGee Candidate Stress Testing")
    print("="*50)
    print(f"Domains: {', '.join(domains)}")
    print(f"Iterations: {iterations}")
    print()

    # Load candidates
    candidates = load_candidates()
    if not candidates:
        print("No candidates to test.")
        return

    print(f"Testing {len(candidates)} quarantined candidates...")

    # Initialize stress tester
    stress_tester = CandidateStressTester()

    # Test each candidate
    results = {
        'test_config': {
            'domains': domains,
            'iterations': iterations,
            'domains_count': len(domains)
        },
        'candidates': []
    }

    for i, candidate in enumerate(candidates, 1):
        print(f"\n🧪 Testing Candidate {i}/{len(candidates)}: {candidate['principle'][:60]}...")

        candidate_results = stress_tester.stress_test_candidate(candidate, domains, iterations)

        # Add candidate info
        candidate_results['principle'] = candidate['principle']
        candidate_results['original_resonance'] = candidate['resonance_score']

        results['candidates'].append(candidate_results)

        # Print summary
        print(".3f")
        print(".3f")
        print(".3f")
        print("  Domain Results:")
        for domain in domains:
            domain_result = candidate_results['domain_results'][domain]
            print(".3f")
    # Overall analysis
    print("\n📊 STRESS TEST SUMMARY")
    print("="*50)

    # Find best and worst performing candidates
    if results['candidates']:
        best_candidate = max(results['candidates'], key=lambda x: x['overall_resonance'])
        worst_candidate = min(results['candidates'], key=lambda x: x['overall_resonance'])

        print("\n🏆 Best Performing Candidate:")
        print(".3f")
        print(f"   Stability: {best_candidate['resonance_stability']:.3f}")
        print(f"   Diversity: {best_candidate['domain_diversity_score']:.3f}")

        print("\n📉 Worst Performing Candidate:")
        print(".3f")
        print(f"   Stability: {worst_candidate['resonance_stability']:.3f}")
        print(f"   Diversity: {worst_candidate['domain_diversity_score']:.3f}")

        # Domain performance analysis
        print("\n🌍 Domain Performance:")
        for domain in domains:
            domain_scores = [c['domain_results'][domain]['avg_resonance'] for c in results['candidates']]
            avg_domain = sum(domain_scores) / len(domain_scores)
            print(".3f")
    # Save results
    save_stress_test_results(results)

    print("\n✅ Stress testing complete!")
    print("Results saved to stress_test_results.json")
    print("Use candidate_review_dashboard.py to review updated candidates.")

if __name__ == "__main__":
    main()