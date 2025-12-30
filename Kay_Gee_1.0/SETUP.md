# Vaulted Reasoner Setup Guide

## Quick Start

### 1. Install Dependencies

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Initialize Vaults

```powershell
# First-time setup: create all vault databases
python -c "from src.memory.vault import initialize_vaults; initialize_vaults()"
```

Expected output:
```
🔧 Initializing Vaulted Reasoner vaults...
  ✓ A Priori Vault created: data\a_priori_vault.db
  ✓ Checksum: a1b2c3d4e5f6...
  ✓ A Posteriori Vault created: data\a_posteriori_vault.db
  ✓ Trace Vault created: data\trace_vault
✅ All vaults initialized successfully
```

### 3. Verify System Integrity

```powershell
python verify_system_integrity.py
```

Expected output:
```
🔍 VAULTED REASONER INTEGRITY VERIFICATION
============================================================
📋 A Priori Vault Integrity...
   ✅ PASS

📋 Philosopher Module Checksums...
   ✅ PASS

... (all checks)

✅ ALL CHECKS PASSED
System integrity verified.
```

### 4. Run the System

```powershell
python main.py
```

## Architecture Overview

### Component Flow

```
User Input
    ↓
[Perception Layer] ← Random Forest + SVM
    ↓ (PAVC Handshake)
[Memory Vaults] ← A Priori + A Posteriori + Trace
    ↓ (PAVC Handshake)
[Reasoning Engine] ← Prolog + Recursive Logic
    ↓ (PAVC Handshake)
[Articulation Layer] ← Template NLG
    ↓
Response Output
```

### Key Files

#### Philosophical Core (Immutable)
- `src/reasoning/kant.pl` - Categorical imperative, duty-based ethics
- `src/reasoning/locke.pl` - Natural rights, social contract
- `src/reasoning/spinoza.pl` - Conatus, determinism, rationality
- `src/reasoning/hume.pl` - Moral sentiment, utility, custom
- `src/reasoning/master_kg.pl` - Meta-rule conflict resolution

#### Python Modules
- `src/perception/classifier.py` - Intent/emotion detection
- `src/memory/vault.py` - Three-vault memory system
- `src/reasoning/recursive_loop.py` - Ethical reasoning engine
- `src/learning/rule_induction.py` - Prolog rule generation
- `src/articulation/nlg.py` - Template-based speech generation
- `src/handshake/manager.py` - PAVC cryptographic protocol

## Testing

### Run All Tests

```powershell
pytest tests/ -v
```

### Run Specific Test

```powershell
pytest tests/test_handshake.py -v
```

### Test Coverage

```powershell
pytest tests/ --cov=src --cov-report=html
```

## Development Workflow

### 1. Make Changes
Edit any Python or Prolog files as needed.

### 2. Verify Integrity
After changes to philosopher modules:
```powershell
python verify_system_integrity.py
```

### 3. Run Tests
```powershell
pytest tests/ -v
```

### 4. Format Code
```powershell
black src/ tests/ main.py
```

## Configuration

Edit `config.yaml` to adjust:
- Recursion depth limits
- Ethical thresholds
- Consolidation intervals
- Component enable/disable

**WARNING**: Do NOT modify philosophical weights in config. They are immutable in the A Priori Vault.

## Debugging

### Enable Debug Logging

In `main.py`, change:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

### View Transaction Log

```python
from src.handshake.manager import HandshakeProtocol

protocol = HandshakeProtocol()
transactions = protocol.get_transaction_log()
print(transactions)
```

### Inspect Vault Contents

```python
from src.memory.vault import APrioriVault

vault = APrioriVault()
vault.connect()
axioms = vault.query_axioms(philosopher="kant")
print(axioms)
```

## Troubleshooting

### "A Priori Vault integrity compromised"

**Cause**: Philosophical vault has been modified.

**Solution**:
1. Backup current vault: `copy data\a_priori_vault.db data\a_priori_vault.backup.db`
2. Reinitialize: `python -c "from src.memory.vault import initialize_vaults; initialize_vaults()"`
3. Verify: `python verify_system_integrity.py`

### "Handshake timeout"

**Cause**: Component not responding within 500ms.

**Solution**: Increase timeout in `config.yaml`:
```yaml
handshake:
  timeout: 1.0  # Increase to 1 second
```

### "Prolog module not found"

**Cause**: PySwip not installed or SWI-Prolog not in PATH.

**Solution**:
1. Install SWI-Prolog: https://www.swi-prolog.org/Download.html
2. Add to PATH
3. Reinstall pyswip: `pip install pyswip`

## Performance Monitoring

### Check Decision Latency

The system logs decision time for each interaction:
```
[INFO] 📥 Processing: 'I'm feeling stressed'
[INFO] 📤 Response: 'I hear you're stressed...' (120ms)
```

Target: 50-200ms on modern hardware

### Monitor Memory Usage

```powershell
# Windows
Get-Process -Name python | Select-Object WorkingSet

# Expected: ~50-100MB for base system
```

## Security

### Cryptographic Verification

Every component-to-component transfer:
1. **Signed** with Ed25519
2. **Hashed** with SHA-256
3. **Audited** in Trace Vault
4. **Verified** against expected state

### Drift Detection

If any component's state diverges:
```
❌ Component state drift detected!
Manual intervention required.
```

System automatically halts (fail-safe).

## Production Deployment

**WARNING**: This is a development/research system.

For production:
1. Replace mock Prolog bridge with real PySwip
2. Implement proper HSM for key storage
3. Add user authentication
4. Enable TLS for network communication
5. Set up automated backup of vaults
6. Configure log rotation
7. Deploy monitoring/alerting

## Next Steps

1. **Train classifiers**: Collect labeled data for intent/emotion models
2. **Seed A Priori**: Add specific philosophical axioms to vault
3. **Test scenarios**: Create test cases for ethical dilemmas
4. **Tune thresholds**: Adjust ethical score thresholds based on use case
5. **Add TTS**: Integrate with Piper or other TTS engine

## Support

- **Architecture**: See main README.md
- **Philosophy**: See Prolog module comments
- **API**: See docstrings in Python modules

---

**Remember**: This is a **symbolic AI system**. It values **correctness over eloquence**, **transparency over flexibility**, and **auditability over adaptability**.
