"""
SKG Health Monitor - Dashboard Integration
Real-time monitoring of knowledge graph health and fatigue indicators
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from statistics import mean, stdev

logger = logging.getLogger(__name__)

class SKGHealthMonitor:
    """Monitors SKG health metrics for dashboard display"""

    def __init__(self, vault_manager, reasoning_manager, pruning_engine):
        self.vault_manager = vault_manager
        self.reasoning_manager = reasoning_manager
        self.pruning_engine = pruning_engine

        # Health metrics cache
        self.last_update = None
        self.health_snapshot = {}

        # Alert thresholds
        self.entropy_alert_threshold = 0.15
        self.resonance_alert_threshold = 0.4
        self.contradiction_alert_threshold = 5

    async def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health metrics for dashboard"""
        if not self._is_cache_valid():
            await self._update_health_snapshot()

        return {
            "timestamp": self.last_update.isoformat(),
            "overall_health": self._calculate_overall_health(),
            "metrics": self.health_snapshot,
            "alerts": self._generate_alerts(),
            "recommendations": self._generate_recommendations()
        }

    def _is_cache_valid(self) -> bool:
        """Check if cached metrics are still valid"""
        if not self.last_update:
            return False
        return (datetime.now() - self.last_update) < timedelta(minutes=5)

    async def _update_health_snapshot(self):
        """Update all health metrics"""
        try:
            self.health_snapshot = {
                "vault_health": await self._get_vault_health(),
                "reasoning_health": await self._get_reasoning_health(),
                "pruning_health": await self._get_pruning_health(),
                "temporal_health": await self._get_temporal_health(),
                "resonance_health": await self._get_resonance_health()
            }
            self.last_update = datetime.now()
            logger.debug("Updated SKG health snapshot")

        except Exception as e:
            logger.error(f"Failed to update health snapshot: {e}")
            self.health_snapshot = {"error": str(e)}

    async def _get_vault_health(self) -> Dict[str, Any]:
        """Vault population and integrity metrics"""
        seed_count = len(self.vault_manager.seed_vault)
        apriori_count = len(self.vault_manager.a_priori_vault)
        apost_count = sum(len(entries) for entries in self.vault_manager.a_posteriori_vault.values())

        # Active vs retired in a posteriori
        active_apost = 0
        retired_apost = 0
        for entries in self.vault_manager.a_posteriori_vault.values():
            for entry in entries:
                if entry.temporal.retirement_date:
                    retired_apost += 1
                else:
                    active_apost += 1

        return {
            "seed_vault_entries": seed_count,
            "a_priori_entries": apriori_count,
            "a_posteriori_active": active_apost,
            "a_posteriori_retired": retired_apost,
            "total_entries": seed_count + apriori_count + active_apost + retired_apost,
            "retirement_rate": retired_apost / max(1, active_apost + retired_apost)
        }

    async def _get_reasoning_health(self) -> Dict[str, Any]:
        """Reasoning performance and cascade metrics"""
        ontology = self.reasoning_manager.ontology_version

        return {
            "ontology_version": ontology.version_id,
            "resonance_score": ontology.resonance_score,
            "entropy_level": ontology.entropy_level,
            "active_edges": ontology.active_edges,
            "retired_edges": ontology.retired_edges,
            "contradictions_resolved": ontology.contradictions_resolved,
            "edge_retirement_rate": ontology.retired_edges / max(1, ontology.active_edges + ontology.retired_edges)
        }

    async def _get_pruning_health(self) -> Dict[str, Any]:
        """Pruning effectiveness metrics"""
        try:
            entropy = await self.pruning_engine._calculate_entropy()
            return {
                "current_entropy": entropy,
                "entropy_trend": "stable",  # Would track over time
                "last_pruning_run": "recent",  # Would track actual timestamps
                "maintenance_status": "active"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _get_temporal_health(self) -> Dict[str, Any]:
        """Temporal integrity and drift detection"""
        now = datetime.now()
        recent_entries = 0
        old_entries = 0
        drifting_entries = 0

        # Check temporal health across all vaults
        for vault_name, vault in [
            ("seed", self.vault_manager.seed_vault),
            ("apriori", self.vault_manager.a_priori_vault)
        ]:
            for entry in vault:
                age_days = (now - entry.temporal.created_at).days
                if age_days < 30:
                    recent_entries += 1
                elif age_days > 365:
                    old_entries += 1

                if "TURBULENCE" in entry.temporal.turbulence_flags:
                    drifting_entries += 1

        # A posteriori vault
        for entries in self.vault_manager.a_posteriori_vault.values():
            for entry in entries:
                if entry.temporal.retirement_date:
                    continue
                age_days = (now - entry.temporal.created_at).days
                if age_days < 30:
                    recent_entries += 1
                elif age_days > 365:
                    old_entries += 1

                if "TURBULENCE" in entry.temporal.turbulence_flags:
                    drifting_entries += 1

        return {
            "recent_entries": recent_entries,
            "legacy_entries": old_entries,
            "drifting_entries": drifting_entries,
            "temporal_integrity": 1.0 - (drifting_entries / max(1, recent_entries + old_entries))
        }

    async def _get_resonance_health(self) -> Dict[str, Any]:
        """Resonance distribution and edge health"""
        tracker = self.reasoning_manager.resonance_tracker

        if not tracker.edge_weights:
            return {"average_resonance": 0.5, "resonance_variance": 0.0, "healthy_edges": 0}

        resonances = list(tracker.edge_weights.values())
        avg_resonance = mean(resonances)
        variance = stdev(resonances) if len(resonances) > 1 else 0.0
        healthy_edges = len([r for r in resonances if r > 0.6])

        return {
            "average_resonance": avg_resonance,
            "resonance_variance": variance,
            "healthy_edges": healthy_edges,
            "total_edges": len(resonances),
            "resonance_distribution": {
                "high": len([r for r in resonances if r > 0.8]),
                "medium": len([r for r in resonances if 0.5 <= r <= 0.8]),
                "low": len([r for r in resonances if r < 0.5])
            }
        }

    def _calculate_overall_health(self) -> float:
        """Calculate overall system health score (0-1)"""
        if not self.health_snapshot:
            return 0.0

        scores = []

        # Vault health (30%)
        vault = self.health_snapshot.get("vault_health", {})
        if vault:
            retirement_rate = vault.get("retirement_rate", 0)
            vault_score = 1.0 - min(retirement_rate * 2, 1.0)  # Penalize high retirement
            scores.append(vault_score * 0.3)

        # Reasoning health (25%)
        reasoning = self.health_snapshot.get("reasoning_health", {})
        if reasoning:
            resonance = reasoning.get("resonance_score", 0.5)
            entropy = reasoning.get("entropy_level", 0)
            reasoning_score = (resonance + (1.0 - entropy)) / 2
            scores.append(reasoning_score * 0.25)

        # Temporal health (20%)
        temporal = self.health_snapshot.get("temporal_health", {})
        if temporal:
            integrity = temporal.get("temporal_integrity", 1.0)
            scores.append(integrity * 0.2)

        # Resonance health (15%)
        resonance = self.health_snapshot.get("resonance_health", {})
        if resonance:
            avg_resonance = resonance.get("average_resonance", 0.5)
            scores.append(avg_resonance * 0.15)

        # Pruning health (10%)
        pruning = self.health_snapshot.get("pruning_health", {})
        if pruning:
            entropy = pruning.get("current_entropy", 0)
            pruning_score = 1.0 - min(entropy * 2, 1.0)
            scores.append(pruning_score * 0.1)

        return sum(scores) if scores else 0.0

    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Generate active alerts based on thresholds"""
        alerts = []

        if not self.health_snapshot:
            return alerts

        # Entropy alert
        pruning = self.health_snapshot.get("pruning_health", {})
        entropy = pruning.get("current_entropy", 0)
        if entropy > self.entropy_alert_threshold:
            alerts.append({
                "level": "warning",
                "type": "entropy",
                "message": f"High entropy detected: {entropy:.3f}",
                "action": "Review contradictions and consider ontology refresh"
            })

        # Resonance alert
        resonance = self.health_snapshot.get("resonance_health", {})
        avg_resonance = resonance.get("average_resonance", 1.0)
        if avg_resonance < self.resonance_alert_threshold:
            alerts.append({
                "level": "warning",
                "type": "resonance",
                "message": f"Low average resonance: {avg_resonance:.3f}",
                "action": "Review edge pruning and query patterns"
            })

        # Contradiction alert
        reasoning = self.health_snapshot.get("reasoning_health", {})
        contradictions = reasoning.get("contradictions_resolved", 0)
        if contradictions > self.contradiction_alert_threshold:
            alerts.append({
                "level": "critical",
                "type": "contradictions",
                "message": f"High contradiction count: {contradictions}",
                "action": "Immediate human review required"
            })

        return alerts

    def _generate_recommendations(self) -> List[str]:
        """Generate maintenance recommendations"""
        recommendations = []

        health = self._calculate_overall_health()

        if health < 0.5:
            recommendations.append("🩺 Schedule comprehensive SKG health review")
        elif health < 0.7:
            recommendations.append("🔧 Consider targeted pruning and resonance analysis")

        # Specific recommendations based on metrics
        temporal = self.health_snapshot.get("temporal_health", {})
        if temporal.get("drifting_entries", 0) > 10:
            recommendations.append("🕐 Review temporal drift patterns")

        resonance = self.health_snapshot.get("resonance_health", {})
        low_resonance = resonance.get("resonance_distribution", {}).get("low", 0)
        if low_resonance > 20:
            recommendations.append("📉 Prune low-resonance edges")

        return recommendations