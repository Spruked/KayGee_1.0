# Migration Guide: Implementing CryptoIdentifiable Protocol

## Overview

All system components **MUST** implement the `CryptoIdentifiable` protocol to ensure:
- **Zero-drift detection** via state hashing
- **Cryptographic provenance** for all operations
- **Handshake protocol integration** with verified identities

This guide shows how to retrofit existing components and create new ones correctly.

---

## Why This Protocol Exists

### The Problem
Before the protocol:
```python
# ❌ BAD: Direct identity creation in component
class MyComponent:
    def __init__(self, handshake):
        self.identity = handshake.create_identity("my_component")
    
    def get_public_key(self):
        return self.identity.get_public_key()
```

**Issues:**
1. No contract enforcement (typos in method names go undetected)
2. No state hashing (drift detection impossible)
3. Inconsistent identity patterns across components

### The Solution
With the protocol:
```python
# ✅ GOOD: Implements CryptoIdentifiable contract
class MyComponent(CryptoIdentifiable):
    def __init__(self, handshake):
        self.identity = handshake.create_identity("my_component")
    
    def assign_identity(self, identity: ComponentIdentity) -> None:
        if self.identity is None:
            self.identity = identity
    
    def get_public_key(self) -> bytes:
        if self.identity is None:
            raise RuntimeError("Identity not assigned")
        return self.identity.get_public_key()
    
    def get_state_hash(self) -> str:
        state = {"version": self.VERSION, "config": self.config}
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()
```

**Benefits:**
1. Type checker enforces all three methods exist
2. State hashing enables drift detection
3. Consistent pattern across all components

---

## Step-by-Step Retrofit Guide

### Step 1: Add Imports

```python
# At top of your component file
from src.core.protocols import CryptoIdentifiable, ComponentIdentity
import hashlib
import json
from typing import Optional
```

### Step 2: Inherit from CryptoIdentifiable

```python
# BEFORE
class MyComponent:
    def __init__(self, handshake):
        # ...

# AFTER
class MyComponent(CryptoIdentifiable):
    VERSION = "1.0.0"  # Add version constant
    
    def __init__(self, handshake):
        # ...
```

### Step 3: Update Identity Handling

```python
# BEFORE
def __init__(self, handshake):
    self.identity = handshake.create_identity("my_component")

# AFTER
def __init__(self, handshake):
    self.identity: Optional[ComponentIdentity] = handshake.create_identity("my_component")
```

### Step 4: Implement assign_identity()

```python
def assign_identity(self, identity: ComponentIdentity) -> None:
    """
    Assign cryptographic identity (idempotent)
    Called by orchestrator if centralized identity creation used
    """
    if self.identity is None:
        self.identity = identity
```

**Note:** This method is idempotent. If identity already exists (from `__init__`), second call does nothing.

### Step 5: Update get_public_key()

```python
# BEFORE
def get_public_key(self):
    return self.identity.get_public_key()

# AFTER
def get_public_key(self) -> bytes:
    """Return Ed25519 public key for handshake registration"""
    if self.identity is None:
        raise RuntimeError(f"Identity not assigned to {self.__class__.__name__}")
    return self.identity.get_public_key()
```

**Critical:** Return `bytes`, not `str` or `VerifyKey` object.

### Step 6: Implement get_state_hash()

This is the **most important** method for zero-drift detection.

```python
def get_state_hash(self) -> str:
    """
    Compute deterministic SHA-256 hash of internal state
    Used for drift detection by integrity checker
    """
    state = {
        "component_version": self.VERSION,
        "component_id": self.component_id,
        # Include ALL mutable configuration
        "model_trained": self.model._is_trained,
        "config_hash": self._hash_config(),
        # Use sorted() for lists, sort_keys=True for dicts
        "feature_names": sorted(self.feature_names)
    }
    
    return hashlib.sha256(
        json.dumps(state, sort_keys=True).encode()
    ).hexdigest()
```

**Rules for state_hash:**
- ✅ Include version numbers
- ✅ Include model training status
- ✅ Include configuration parameters
- ✅ Sort all keys and lists
- ❌ Do NOT include timestamps
- ❌ Do NOT include random values
- ❌ Do NOT include identity/keys

---

## Complete Before/After Examples

### Example 1: PerceptionSystem

#### BEFORE (Legacy)
```python
class PerceptionSystem:
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.encoder = SemanticEncoder()
        self.identity = handshake_protocol.create_identity("perception")
    
    def get_public_key(self):
        return self.identity.get_public_key()
```

#### AFTER (CryptoIdentifiable)
```python
from src.core.protocols import CryptoIdentifiable, ComponentIdentity

class PerceptionSystem(CryptoIdentifiable):
    VERSION = "1.0.0"
    
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.encoder = SemanticEncoder()
        self.identity: Optional[ComponentIdentity] = handshake_protocol.create_identity("perception")
        self.component_id = "perception"
    
    def assign_identity(self, identity: ComponentIdentity) -> None:
        if self.identity is None:
            self.identity = identity
    
    def get_public_key(self) -> bytes:
        if self.identity is None:
            raise RuntimeError("Identity not assigned to PerceptionSystem")
        return self.identity.get_public_key()
    
    def get_state_hash(self) -> str:
        state = {
            "component_version": self.VERSION,
            "component_id": self.component_id,
            "intent_trained": self.intent_classifier._is_trained,
            "emotion_trained": self.emotion_detector._is_trained,
            "encoder_features": sorted(["mood", "verbosity", "ethics_density"])
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()
```

### Example 2: ReasoningEngine

#### BEFORE (Legacy)
```python
class ReasoningEngine:
    MAX_RECURSION_DEPTH = 5
    
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.prolog = PrologBridge()
        self.identity = handshake_protocol.create_identity("reasoning")
    
    def get_public_key(self):
        return self.identity.get_public_key()
```

#### AFTER (CryptoIdentifiable)
```python
from src.core.protocols import CryptoIdentifiable, ComponentIdentity

class ReasoningEngine(CryptoIdentifiable):
    VERSION = "1.0.0"
    MAX_RECURSION_DEPTH = 5
    MIN_ETHICAL_THRESHOLD = 0.7
    
    def __init__(self, handshake_protocol):
        self.handshake = handshake_protocol
        self.prolog = PrologBridge()
        self.score_predictor = EthicsScorePredictor()
        self._load_philosophical_modules()
        self.identity: Optional[ComponentIdentity] = handshake_protocol.create_identity("reasoning")
        self.component_id = "reasoning"
    
    def assign_identity(self, identity: ComponentIdentity) -> None:
        if self.identity is None:
            self.identity = identity
    
    def get_public_key(self) -> bytes:
        if self.identity is None:
            raise RuntimeError("Identity not assigned to ReasoningEngine")
        return self.identity.get_public_key()
    
    def get_state_hash(self) -> str:
        state = {
            "component_version": self.VERSION,
            "component_id": self.component_id,
            "max_recursion_depth": self.MAX_RECURSION_DEPTH,
            "min_ethical_threshold": self.MIN_ETHICAL_THRESHOLD,
            "score_predictor_trained": self.score_predictor._is_trained,
            "prolog_modules": sorted(self.prolog.loaded_modules)
        }
        return hashlib.sha256(
            json.dumps(state, sort_keys=True).encode()
        ).hexdigest()
```

---

## Testing Your Implementation

### Unit Test Template

```python
import pytest
from src.core.protocols import CryptoIdentifiable, verify_component_contract
from src.handshake.manager import HandshakeProtocol

def test_component_implements_protocol():
    """Verify component implements CryptoIdentifiable correctly"""
    handshake = HandshakeProtocol()
    component = MyComponent(handshake)
    
    # Check inheritance
    assert isinstance(component, CryptoIdentifiable)
    
    # Check contract compliance
    assert verify_component_contract(component)
    
    # Test methods
    assert component.identity is not None
    public_key = component.get_public_key()
    assert isinstance(public_key, bytes)
    assert len(public_key) == 32  # Ed25519 key length
    
    state_hash = component.get_state_hash()
    assert isinstance(state_hash, str)
    assert len(state_hash) == 64  # SHA-256 hex digest
    
    # Test idempotency of assign_identity
    new_identity = handshake.create_identity("test_component")
    component.assign_identity(new_identity)
    # Should not change existing identity

def test_state_hash_determinism():
    """Verify state hash is deterministic"""
    handshake = HandshakeProtocol()
    component1 = MyComponent(handshake)
    component2 = MyComponent(handshake)
    
    # Same initial state should produce same hash
    hash1 = component1.get_state_hash()
    hash2 = component2.get_state_hash()
    
    assert hash1 == hash2

def test_identity_not_assigned_error():
    """Verify RuntimeError raised if identity not assigned"""
    handshake = HandshakeProtocol()
    component = MyComponent(handshake)
    component.identity = None  # Simulate missing identity
    
    with pytest.raises(RuntimeError, match="Identity not assigned"):
        component.get_public_key()
```

---

## Common Pitfalls

### ❌ Pitfall 1: Non-Deterministic State Hash
```python
# BAD: Includes timestamp
def get_state_hash(self):
    state = {
        "version": self.VERSION,
        "timestamp": time.time()  # ❌ Changes every call!
    }
    return hashlib.sha256(json.dumps(state).encode()).hexdigest()
```

### ✅ Fix: Remove Non-Deterministic Values
```python
# GOOD: Only includes stable state
def get_state_hash(self):
    state = {
        "version": self.VERSION,
        "config_hash": self._stable_config_hash()
    }
    return hashlib.sha256(
        json.dumps(state, sort_keys=True).encode()
    ).hexdigest()
```

### ❌ Pitfall 2: Returning Wrong Type from get_public_key()
```python
# BAD: Returns string
def get_public_key(self):
    return str(self.identity.public_key)  # ❌ Wrong type!
```

### ✅ Fix: Return bytes
```python
# GOOD: Returns bytes
def get_public_key(self) -> bytes:
    return self.identity.get_public_key()
```

### ❌ Pitfall 3: Mutable State Not Included in Hash
```python
# BAD: Missing important state
def get_state_hash(self):
    state = {"version": self.VERSION}  # ❌ Where's the model state?
    return hashlib.sha256(json.dumps(state).encode()).hexdigest()
```

### ✅ Fix: Include All Mutable Configuration
```python
# GOOD: Includes all state that could drift
def get_state_hash(self):
    state = {
        "version": self.VERSION,
        "model_trained": self.model._is_trained,
        "hyperparameters": self.model.get_params(),
        "feature_count": len(self.features)
    }
    return hashlib.sha256(
        json.dumps(state, sort_keys=True).encode()
    ).hexdigest()
```

---

## Verification Checklist

Before committing your component:

- [ ] Component inherits from `CryptoIdentifiable`
- [ ] All three abstract methods implemented (`assign_identity`, `get_public_key`, `get_state_hash`)
- [ ] `get_public_key()` returns `bytes`, not `str`
- [ ] `get_public_key()` raises `RuntimeError` if identity is None
- [ ] `get_state_hash()` is deterministic (no timestamps, no random values)
- [ ] `get_state_hash()` includes all mutable configuration
- [ ] `get_state_hash()` uses `sort_keys=True` in `json.dumps()`
- [ ] `assign_identity()` is idempotent
- [ ] Unit tests verify contract compliance
- [ ] Unit tests verify state hash determinism

---

## Next Steps

1. **Retrofit remaining components:**
   - `ArticulationEngine`
   - `LearningSystem`
   - `TemporalContextLayer`
   - `MetaCognitiveMonitor`
   - `PersonalityCore`
   - `SafetyGuardian`

2. **Update vault implementations:**
   - Implement `VaultCompliant` mixin
   - Add `verify_integrity()` and `export_audit_log()`

3. **Enable automated drift detection:**
   - Schedule periodic state hash checks
   - Alert on unexpected hash changes
   - Log hash deltas to audit trail

---

## Questions?

If component behavior is unclear:
1. Check [src/core/protocols.py](src/core/protocols.py) for detailed docstrings
2. Review [src/perception/classifier.py](src/perception/classifier.py) (complete example)
3. Review [src/reasoning/recursive_loop.py](src/reasoning/recursive_loop.py) (complete example)

**Remember:** No shortcuts. Every component must implement this contract. Zero-drift guarantee depends on it.
