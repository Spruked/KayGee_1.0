
"""
Reasoning Module
Handles reasoning engine with circuit breakers and SKG cascade logic
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from src.core.layers import ReasoningLayer
from src.reasoning.recursive_loop import ReasoningEngine, ConflictResolver


@dataclass
class OntologyVersion:
	"""Tracks ontology evolution and resonance"""
	version_id: str
	created_at: datetime = field(default_factory=datetime.now)
	resonance_score: float = 0.0
	entropy_level: float = 0.0
	active_edges: int = 0
	retired_edges: int = 0
	contradictions_resolved: int = 0

	def update_metrics(self, resonance: float, entropy: float, active: int, retired: int, resolved: int):
		self.resonance_score = resonance
		self.entropy_level = entropy
		self.active_edges = active
		self.retired_edges = retired
		self.contradictions_resolved = resolved


class ResonanceTracker:
	"""Tracks edge resonance through query patterns"""

	def __init__(self):
		self.edge_weights = {}  # edge_id -> resonance_score
		self.query_patterns = {}  # pattern_hash -> success_rate

	def track_traversal(self, edge_id: str, success: bool, context_strength: float = 1.0):
		"""Update resonance based on traversal success"""
		if edge_id not in self.edge_weights:
			self.edge_weights[edge_id] = 0.5  # Start neutral

		# Exponential moving average
		current = self.edge_weights[edge_id]
		if success:
			new_weight = current + (1.0 - current) * 0.1 * context_strength
		else:
			new_weight = current - current * 0.05 * context_strength

		self.edge_weights[edge_id] = max(0.0, min(1.0, new_weight))

	def get_resonance(self, edge_id: str) -> float:
		return self.edge_weights.get(edge_id, 0.5)

	def prune_low_resonance(self, threshold: float = 0.3) -> List[str]:
		"""Return edges below resonance threshold"""
		return [eid for eid, weight in self.edge_weights.items() if weight < threshold]


class ReasoningManager(ReasoningLayer):
	"""
	Manages reasoning with depth limits, timeout guards, and SKG cascade logic
	"""

	def __init__(self):
		super().__init__("ReasoningManager")
		self.engine = None
		self.resolver = None
		self.max_depth = 5
		self.timeout_seconds = 30

		# SKG components
		self.ontology_version = OntologyVersion("1.0.0")
		self.resonance_tracker = ResonanceTracker()

	def initialize(self, config: Dict[str, Any]) -> bool:
		try:
			handshake_protocol = config.get('handshake_protocol')
			self.engine = ReasoningEngine(handshake_protocol)
			self.resolver = ConflictResolver()
			self.max_depth = config.get('max_reasoning_depth', 5)
			self.timeout_seconds = config.get('reasoning_timeout', 30)
			self._initialized = True
			return True
		except Exception as e:
			print(f"Failed to initialize reasoning: {e}")
			return False

	def get_status(self) -> Dict[str, Any]:
		return {
			"reasoning_initialized": self._initialized,
			"max_depth": self.max_depth,
			"timeout_seconds": self.timeout_seconds,
			"circuit_breaker_active": True,
			"ontology_version": self.ontology_version.version_id,
			"current_resonance": self.ontology_version.resonance_score,
			"current_entropy": self.ontology_version.entropy_level,
			"active_edges": self.ontology_version.active_edges
		}

	def shutdown(self) -> None:
		print("ReasoningManager shutting down...")

	def _on_identity_assigned(self):
		"""Hook called after identity assignment"""
		print(f"✓ ReasoningManager identity assigned: {self.identity.name}")

	def get_state_hash(self) -> str:
		"""Compute deterministic SHA-256 hash of internal state"""
		import hashlib
		import json
        
		state = {
			"version": "1.0.0",
			"state_nonce": self._state_nonce,
			"initialized": self._initialized,
			"max_depth": self.max_depth,
			"timeout_seconds": self.timeout_seconds,
			"ontology_version": self.ontology_version.version_id,
			"resonance_score": self.ontology_version.resonance_score,
			"entropy_level": self.ontology_version.entropy_level,
			"active_edges": self.ontology_version.active_edges
		}
		return hashlib.sha256(
			json.dumps(state, sort_keys=True).encode()
		).hexdigest()

	def query(self, context: Dict[str, Any], vault_manager=None) -> Dict[str, Any]:
		"""
		SKG Cascade Query: Truth flows downhill, entropy bubbles up
		"""
		if not self._initialized:
			return {"error": "Reasoning not initialized"}

		start_time = time.time()
		cascade_path = []
		contradictions_found = []

		try:
			# Phase 1: Seed vault lookup (immutable truths)
			seed_result = self._query_seed_vault(context, vault_manager)
			if seed_result.get('confidence', 0) > 0.9:
				cascade_path.append("seed_vault")
				return self._format_cascade_response(seed_result, cascade_path, contradictions_found, start_time)

			# Phase 2: A Priori vault (deductive reasoning)
			apriori_result = self._query_a_priori_vault(context, vault_manager)
			if apriori_result.get('confidence', 0) > 0.8:
				cascade_path.append("a_priori_vault")
				return self._format_cascade_response(apriori_result, cascade_path, contradictions_found, start_time)

			# Phase 3: A Posteriori vault (inductive learning)
			apost_result = self._query_a_posteriori_vault(context, vault_manager)
			cascade_path.append("a_posteriori_vault")

			# Phase 4: Live reasoning with resonance tracking
			if apost_result.get('confidence', 0) < 0.6:
				live_result = self._live_reasoning(context, vault_manager)
				cascade_path.append("live_reasoning")

				# Check for contradictions
				contradictions = self._detect_contradictions([seed_result, apriori_result, apost_result, live_result])
				contradictions_found.extend(contradictions)

				# Select best result based on resonance
				final_result = self._select_by_resonance([apost_result, live_result], context)
			else:
				final_result = apost_result

			return self._format_cascade_response(final_result, cascade_path, contradictions_found, start_time)

		except Exception as e:
			return {"error": str(e), "cascade_path": cascade_path, "time_taken": time.time() - start_time}

	def _query_seed_vault(self, context: Dict[str, Any], vault_manager) -> Dict[str, Any]:
		"""Query immutable seed truths"""
		if not vault_manager:
			return {"confidence": 0.0}

		query = context.get('query', '')
		for entry in vault_manager.seed_vaults.values():
			if query.lower() in entry.content.lower():
				return {
					"result": entry.content,
					"confidence": 0.95,
					"source": "seed_vault",
					"temporal": entry.temporal
				}
		return {"confidence": 0.0}

	def _query_a_priori_vault(self, context: Dict[str, Any], vault_manager) -> Dict[str, Any]:
		"""Query deductive knowledge"""
		if not vault_manager:
			return {"confidence": 0.0}

		query = context.get('query', '')
		best_match = None
		best_confidence = 0.0

		for entry in vault_manager.a_priori_vaults.values():
			if query.lower() in entry.content.lower():
				confidence = entry.temporal.resonance_score
				if confidence > best_confidence:
					best_match = entry
					best_confidence = confidence

		if best_match:
			return {
				"result": best_match.content,
				"confidence": best_confidence,
				"source": "a_priori_vault",
				"temporal": best_match.temporal
			}
		return {"confidence": 0.0}

	def _query_a_posteriori_vault(self, context: Dict[str, Any], vault_manager) -> Dict[str, Any]:
		"""Query inductive knowledge"""
		if not vault_manager:
			return {"confidence": 0.0}

		query = context.get('query', '')
		best_match = None
		best_confidence = 0.0

		for entries in vault_manager.a_posteriori_vault.values():
			for entry in entries:
				if entry.temporal.retirement_date:  # Skip retired
					continue
				if query.lower() in entry.content.lower():
					confidence = entry.temporal.resonance_score
					if confidence > best_confidence:
						best_match = entry
						best_confidence = confidence

		if best_match:
			return {
				"result": best_match.content,
				"confidence": best_confidence,
				"source": "a_posteriori_vault",
				"temporal": best_match.temporal
			}
		return {"confidence": 0.0}

	def _live_reasoning(self, context: Dict[str, Any], vault_manager) -> Dict[str, Any]:
		"""Perform live recursive reasoning"""
		result = self.reason(context)
		if 'error' not in result:
			# Track this as new knowledge
			if vault_manager:
				vault_manager.commit_entry(
					content=result['result'].get('conclusion', ''),
					vault_type='a_posteriori',
					context_hash=context.get('query', ''),
					resonance_score=result['result'].get('confidence', 0.5)
				)
		return result.get('result', {})

	def _detect_contradictions(self, results: List[Dict]) -> List[Dict]:
		"""Find contradictions between results"""
		contradictions = []
		valid_results = [r for r in results if r.get('confidence', 0) > 0.5]

		for i, result_a in enumerate(valid_results):
			for result_b in valid_results[i+1:]:
				if self._semantic_contradicts(result_a, result_b):
					contradictions.append({
						"sources": [result_a.get('source'), result_b.get('source')],
						"conflict": f"Contradiction between {result_a.get('source')} and {result_b.get('source')}"
					})

		return contradictions

	def _semantic_contradicts(self, result_a: Dict, result_b: Dict) -> bool:
		"""Simple contradiction detection - can be enhanced with NLP"""
		# Placeholder: check for direct opposites
		text_a = result_a.get('result', '').lower()
		text_b = result_b.get('result', '').lower()

		opposites = [
			('true', 'false'), ('yes', 'no'), ('correct', 'incorrect'),
			('valid', 'invalid'), ('right', 'wrong')
		]

		for pos, neg in opposites:
			if (pos in text_a and neg in text_b) or (neg in text_a and pos in text_b):
				return True
		return False

	def _select_by_resonance(self, candidates: List[Dict], context: Dict) -> Dict:
		"""Select result with highest resonance"""
		if not candidates:
			return {}

		# Simple selection by confidence for now
		return max(candidates, key=lambda x: x.get('confidence', 0))

	def _format_cascade_response(self, result: Dict, cascade_path: List[str],
							   contradictions: List[Dict], start_time: float) -> Dict[str, Any]:
		"""Format response with cascade metadata"""
		return {
			"result": result,
			"cascade_path": cascade_path,
			"contradictions_found": contradictions,
			"time_taken": time.time() - start_time,
			"ontology_version": self.ontology_version.version_id,
			"resonance_score": result.get('confidence', 0.0)
		}

	def reason(self, context: Dict[str, Any], depth_limit: int = 5) -> Dict[str, Any]:
		if not self._initialized:
			return {"error": "Reasoning not initialized"}

		start_time = time.time()
		current_depth = 0

		try:
			# Circuit breaker: depth limit
			if depth_limit > self.max_depth:
				depth_limit = self.max_depth

			# Circuit breaker: timeout guard
			while current_depth < depth_limit and (time.time() - start_time) < self.timeout_seconds:
				result = self.engine.reason(context)
				if result.get('confidence', 0) > 0.8:  # High confidence, stop
					break
				current_depth += 1

			return {
				"result": result,
				"depth_used": current_depth,
				"time_taken": time.time() - start_time,
				"circuit_breaker_triggered": current_depth >= depth_limit or (time.time() - start_time) >= self.timeout_seconds
			}

		except Exception as e:
			return {"error": str(e), "depth_used": current_depth, "time_taken": time.time() - start_time}

	def resolve_conflict(self, conflicts: list) -> Dict[str, Any]:
		if not self._initialized:
			return {"error": "Reasoning not initialized"}

		try:
			return self.resolver.resolve(conflicts)
		except Exception as e:
			return {"error": str(e)}

	def evaluate(self, input_text: str) -> Optional[Dict[str, Any]]:
		"""
		Evaluate input and return verdict or None
		No mocks, no placeholders, no fallbacks
		"""
		if not self._initialized:
			return None

		try:
			situation = {"input": input_text}
			verdict = self.engine.reason(situation, input_text)
			return verdict
		except Exception as e:
			# No fallback - return None on any error
			print(f"Reasoning failed: {e}")
			return None
