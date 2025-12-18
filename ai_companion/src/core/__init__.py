"""Core package initialization"""
from src.core.protocols import (
    ComponentIdentity,
    CryptoIdentifiable,
    VaultCompliant,
    LearningCompliant,
    verify_component_contract,
    generate_identity_manifest
)

__all__ = [
    'ComponentIdentity',
    'CryptoIdentifiable',
    'VaultCompliant',
    'LearningCompliant',
    'verify_component_contract',
    'generate_identity_manifest'
]
