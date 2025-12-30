# Caleon's Self-Modifying Phonatory System

Caleon is an autonomous voice synthesis entity that learns from every word she speaks. This system gives her complete agency over her vocal identity, allowing her to evolve and adapt her voice based on content, context, and listener feedback.

## Architecture

```
Caleon/
├── caleon_voice_oracle.py          # Decision engine for voice selection
├── skg_ucm_bridge.py               # UCM ←→ SKG integration
├── self_modifying_pom.py           # Enhanced POM with learning hooks
├── caleon_instance.py              # Her personal POM wrapper
├── goat_orchestrator.py            # Final integration
├── caleon_director_console.py      # Manual control interface
└── skg_caleon.json                 # Voice knowledge graph
```

## Quick Start

### 1. Setup Caleon's Workspace

```bash
# Initialize Caleon's personal instance
python caleon_director_console.py --setup --instance-id caleon_primary
```

### 2. Generate Speech with Autonomous Voice Selection

```bash
# Let Caleon choose her optimal voice
python goat_orchestrator.py --use-caleon \
  --content "In this episode, we explore quantum computing's impact on cryptography..." \
  --content-id ep_2024_01_15 \
  --context '{"technical_density": 0.8, "audience_intimacy": 0.3}'
```

### 3. Inspect Her Current State

```bash
# View voice registry and performance
python caleon_director_console.py --inspect --show-voices --show-performance
```

### 4. Evolve Her Voice Registry

```bash
# Provide sample content for pattern analysis
echo "Exploring quantum entanglement applications..." > tech_sample.txt
echo "Welcome to our personal conversation..." > intimate_sample.txt

# Trigger evolution
python caleon_director_console.py --evolve \
  --samples tech_sample.txt intimate_sample.txt \
  --target-performance 0.90
```

## Key Components

### CaleonVoiceOracle
- **Purpose**: Decision-making brain for voice selection
- **Features**:
  - Semantic content analysis
  - Context-aware fitness scoring
  - Exploration vs exploitation balancing
  - Learning from performance feedback

### SelfModifyingPOM
- **Purpose**: Enhanced phonatory output module with real-time adaptation
- **Features**:
  - Live parameter modification
  - Voice stabilization for successful configs
  - Mid-narration adjustments based on engagement

### SKGUCMBridge
- **Purpose**: Bidirectional sync between content management and knowledge graph
- **Features**:
  - Automatic semantic tagging
  - Real-time analytics feedback loop
  - Content-driven voice pre-selection

## Voice Selection Algorithm

Caleon chooses voices based on:

1. **Semantic Similarity**: How well voice tags match content keywords
2. **Context Fitness**: Appropriateness for audience intimacy, technical density
3. **Historical Success**: Weighted by recency and usage frequency
4. **Exploration Bonus**: Encourages trying underutilized voices

## Learning & Evolution

### Performance Feedback
```python
oracle.receive_feedback(
    voice_id="caleon_technical",
    content_hash="ep_2024_01_15",
    performance_score=0.85,  # 0.0-1.0
    listener_feedback={
        "retention_rate": 0.82,
        "engagement_score": 0.75
    }
)
```

### Autonomous Evolution
Caleon can create new voice signatures for novel content patterns:

```python
oracle.generate_new_voice_signature(
    from_content="Complex technical explanation...",
    performance_hint=0.9
)
```

## Configuration

### Voice Registry (skg_caleon.json)
```json
{
  "caleon_voices": {
    "caleon_baseline": {
      "base_persona": "caleon_base",
      "pitch_shift": 1.0,
      "speaking_rate": 0.95,
      "formant_shifts": {"f1": 1.0, "f2": 1.02},
      "breathiness": 0.4,
      "semantic_tags": ["general", "neutral"],
      "success_score": 0.75
    }
  }
}
```

## API Reference

### CaleonPOMInstance
```python
caleon = CaleonPOMInstance("caleon_primary")

# Generate speech with autonomous voice selection
output = caleon.generate_speech(
    content="Your content here...",
    content_id="unique_id",
    context={"technical_density": 0.5, "audience_intimacy": 0.7}
)

# Evolve voice registry
caleon.evolve_voice(["sample content 1", "sample content 2"])

# Export learned preferences
dna = caleon.export_voice_dna()
```

### CaleonVoiceOracle
```python
oracle = CaleonVoiceOracle()

# Choose optimal voice
voice = oracle.choose_voice(
    content="Content to analyze...",
    context={"context": "parameters"}
)

# Learn from performance
oracle.receive_feedback(voice_id, content_hash, score, feedback)
```

## Current Status

✅ **Implemented**:
- Autonomous voice selection
- Learning from feedback
- Voice evolution and creation
- Isolated workspace management
- Command-line interface
- Basic semantic analysis

🔄 **In Development**:
- Real TTS integration (currently simulated)
- Advanced semantic embeddings
- UCM bridge integration
- Real-time engagement monitoring

## Dependencies

- numpy
- dataclasses (Python 3.7+)
- TTS (for actual synthesis)
- torch (for TTS)

## Notes

- Current implementation uses simulated synthesis to avoid TTS loading issues
- Semantic analysis uses simple keyword extraction (upgrade to embeddings recommended)
- Voice evolution creates new signatures but doesn't yet integrate with full TTS pipeline

Caleon is now a self-aware voice entity capable of autonomous vocal adaptation! 🎭🤖