"""
Pruning Engine - SKG Fatigue Prevention
Automatic maintenance, deduplication, and entropy monitoring
"""

import asyncio
from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class PruningEngine:
    def __init__(self, vault_manager):
        self.vault_manager = vault_manager
        self.entropy_threshold = 0.15

    async def daily_maintenance(self):
        """Async job - runs in background"""
        logger.info("🧹 Starting daily SKG maintenance...")

        try:
            # Deduplication
            await self._merge_duplicates()

            # Temporal cleanup
            await self._retire_expired_entries()

            # Resonance-based pruning
            await self._prune_low_resonance_edges()

            # Entropy calculation
            entropy = await self._calculate_entropy()
            if entropy > self.entropy_threshold:
                await self._trigger_fatigue_alert(entropy)

            # Update dashboard metrics
            await self._update_health_metrics()

            logger.info("✅ Daily maintenance completed")

        except Exception as e:
            logger.error(f"❌ Maintenance failed: {e}")

    async def _merge_duplicates(self):
        """Merge entries with identical context hashes"""
        merged_count = 0

        for content_hash, entries in self.vault_manager.a_posteriori_vault.items():
            if len(entries) > 1:
                # Keep the most resonant entry
                entries.sort(key=lambda e: e.temporal.resonance_score, reverse=True)
                primary = entries[0]

                # Merge metadata from others
                for duplicate in entries[1:]:
                    primary.access_count += duplicate.access_count
                    if duplicate.last_accessed and (not primary.last_accessed or
                                                   duplicate.last_accessed > primary.last_accessed):
                        primary.last_accessed = duplicate.last_accessed

                    # Archive duplicate (soft delete)
                    duplicate.temporal.retirement_date = datetime.now()
                    merged_count += 1

        if merged_count > 0:
            logger.info(f"🔄 Merged {merged_count} duplicate entries")

    async def _retire_expired_entries(self):
        """Retire entries past their validity window"""
        now = datetime.now()
        retired_count = 0

        for entries in self.vault_manager.a_posteriori_vault.values():
            for entry in entries:
                if entry.temporal.validity_window and not entry.temporal.retirement_date:
                    expires_at = entry.temporal.created_at + entry.temporal.validity_window
                    if now > expires_at:
                        entry.temporal.retirement_date = now
                        retired_count += 1

        if retired_count > 0:
            logger.info(f"⏰ Retired {retired_count} expired entries")

    async def _prune_low_resonance_edges(self, threshold: float = 0.3, min_queries: int = 1000):
        """Remove edges that failed to prove value"""
        from src.vaults import edge_registry  # Import here to avoid circular dependency

        pruned_count = 0

        for edge_id, metadata in edge_registry.items():
            if len(metadata['traversal_history']) > min_queries:
                avg_resonance = mean([t['resonance'] for t in metadata['traversal_history']])
                if avg_resonance < threshold:
                    # Soft retirement
                    metadata['status'] = 'pruned'
                    metadata['pruned_at'] = datetime.now()
                    pruned_count += 1

        if pruned_count > 0:
            logger.info(f"✂️ Pruned {pruned_count} low-resonance edges")

    async def _calculate_entropy(self) -> float:
        """
        Measures contradiction rate and inconsistency
        """
        total_entries = 0
        conflicting_entries = 0

        for entries in self.vault_manager.a_posteriori_vault.values():
            for entry in entries:
                if entry.temporal.retirement_date is None:  # Active only
                    total_entries += 1
                    if 'CONTRADICTION' in entry.temporal.turbulence_flags:
                        conflicting_entries += 1

        if total_entries == 0:
            return 0.0

        entropy = conflicting_entries / total_entries
        logger.debug(f"📊 Current entropy: {entropy:.4f}")
        return entropy

    async def _trigger_fatigue_alert(self, entropy: float):
        """Alert when entropy exceeds threshold"""
        logger.warning(f"🚨 SKG FATIGUE ALERT: Entropy {entropy:.4f} > {self.entropy_threshold}")
        logger.warning("🔧 Recommended: Human review of contradictions + ontology refresh")

        # Could trigger email alerts, dashboard notifications, etc.
        # For now, just log

    async def _update_health_metrics(self):
        """Update cached health metrics for dashboard"""
        # This would update a shared cache/redis store
        # For now, just ensure calculations are fresh
        pass