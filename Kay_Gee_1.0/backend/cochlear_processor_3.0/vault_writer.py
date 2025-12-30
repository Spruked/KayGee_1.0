"""
Vault Writer Module for Cochlear Processor
Integrates with KayGee's TraceVault system
"""
import logging
from pathlib import Path
from typing import Dict, Any
import json
import time

logger = logging.getLogger(__name__)

# Try to import KayGee's vault system
try:
    from src.memory.vault import TraceVault
    VAULT_AVAILABLE = True
    logger.info("✅ KayGee TraceVault loaded")
except ImportError:
    VAULT_AVAILABLE = False
    logger.warning("⚠️ KayGee TraceVault not available")

# Global vault instance (lazy loading)
_vault = None

def get_trace_vault():
    """Lazy load the TraceVault"""
    global _vault
    if _vault is None and VAULT_AVAILABLE:
        try:
            _vault = TraceVault()
            logger.info("✅ TraceVault initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TraceVault: {e}")
            _vault = None
    return _vault

def write_vault_record(trace: Dict[str, Any]) -> str:
    """
    Write a trace record to the vault system

    Args:
        trace: The trace data to write

    Returns:
        Merkle root hash of the written block
    """
    vault = get_trace_vault()
    if not vault:
        logger.warning("TraceVault not available, logging trace to console")
        print(f"VAULT RECORD: {json.dumps(trace, indent=2)}")
        return "no_vault"

    try:
        # Add timestamp if not present
        if 'timestamp' not in trace:
            trace['timestamp'] = time.time()

        # Write to vault
        merkle_root = vault.append(trace)
        logger.info(f"✅ Trace written to vault: {merkle_root}")
        return merkle_root

    except Exception as e:
        logger.error(f"Failed to write to vault: {e}")
        return f"error_{str(e)}"

def query_vault_records(filters: Dict[str, Any] = None, limit: int = 10) -> list:
    """
    Query vault records

    Args:
        filters: Optional filters to apply
        limit: Maximum number of records to return

    Returns:
        List of matching vault records
    """
    vault = get_trace_vault()
    if not vault:
        return []

    try:
        return vault.query(filters, limit)
    except Exception as e:
        logger.error(f"Failed to query vault: {e}")
        return []