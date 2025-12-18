# Vaulted Reasoner: Non-Neural Philosophical AI Companion

A **neuro-symbolic architecture without neural networks** - combining symbolic reasoning, classical machine learning, and philosophical ethics for a transparent, auditable AI companion.

## Architecture Overview

### Core Principles
- **Zero Neural Networks**: Uses scikit-learn (Random Forest, SVM), Prolog, and LSH
- **Zero Drift**: Cryptographic handshakes enforce deterministic state transitions
- **Zero Hallucination**: All outputs traceable to A Priori axioms or A Posteriori cases
- **Philosophical Grounding**: Four philosopher modules (Kant, Locke, Spinoza, Hume)

### System Layers

1. **Memory Vaults**
   - **A Priori Vault**: Immutable philosophical axioms (cryptographically signed)
   - **A Posteriori Vault**: Learned cases from experience (versioned)
   - **Trace Vault**: Append-only ledger of all reasoning (blockchain-like)

2. **Perception Layer**
   - Random Forest classifier for intent recognition
   - SVM for emotion detection
   - Hand-engineered semantic vectors (5-20 dimensions, not 768)

3. **Reasoning Engine**
   - Hybrid scikit-learn + Prolog validation
   - Recursive self-correction with depth limits
   - Master Super KG for multi-philosopher conflict resolution

4. **Learning System**
   - Ripper-inspired rule induction
   - Decision tree → Prolog clause conversion
   - Emergent concept formation (invented predicates)

5. **Articulation Layer**
   - Template-based NLG (SimpleNLG-like)
   - Philosopher-specific semantic graphs
   - Deterministic, auditable speech generation

6. **Handshake Protocol (PAVC)**
   - Ping-ACK-Verify-Commit cryptographic handshakes
   - Ed25519 signatures per component
   - Byzantine fault tolerance with quorum voting

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize vaults (first run only)
python -c "from src.memory.vault import initialize_vaults; initialize_vaults()"
```

## Usage

```bash
# Run main application
python main.py

# Verify system integrity
python verify_system_integrity.py

# Run tests
pytest tests/ -v
```

## Configuration

Edit `.vscode/settings.json` to configure:
- Python interpreter path
- Prolog executable path (`swipl`)
- Linting and formatting options

## Philosophical Modules

- **kant.pl**: Categorical imperative, duty-based ethics
- **locke.pl**: Natural rights (life, liberty, property), empiricism
- **spinoza.pl**: Conatus, determinism, intellectual love
- **hume.pl**: Moral sentiment, utility, custom/habit

## Performance

- **Decision latency**: 50-200ms on Raspberry Pi 5
- **Throughput**: ~100 decisions/second
- **Storage**: ~1GB/year for Trace Vault
- **CPU overhead**: <5% for cryptographic checks

## Security

- All philosophical rules are **cryptographically signed**
- State transitions are **deterministic** and **auditable**
- Drift detection triggers **system halt** (fail-safe)
- No retroactive data modification (append-only logs)

## License

[Your License Here]

## Architecture Comparison

| Feature | Vaulted Reasoner | LLM Companion |
|---------|------------------|---------------|
| Architecture | Symbolic + Statistical | Neural (Transformer) |
| Memory | Exact, unbounded | Approximate, context-limited |
| Ethics | Auditable, rule-based | Opaque, prompt-based |
| Speed | 50-200ms | 500-2000ms |
| Privacy | 100% local | Cloud-dependent |
| Modifiability | Extreme (edit rules) | Limited (prompts) |
| Creativity | None | High |
| Transparency | Complete | None |
