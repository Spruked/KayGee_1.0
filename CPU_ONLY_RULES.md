# CPU-ONLY REPOSITORY RULES
# =========================
# This repository is configured for CPU-only operation.
# NO NVIDIA/CUDA packages should be installed.

## Enforcement Rules

### 1. PyTorch Installation
**ALWAYS** use CPU-only index:
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. Environment Variables
Set these BEFORE any Python execution:
```bash
export CUDA_VISIBLE_DEVICES=''  # Linux/Mac
$env:CUDA_VISIBLE_DEVICES=''    # Windows PowerShell
```

### 3. Forbidden Packages
The following packages should NEVER be installed:
- torch[cuda]
- torch[cu118]
- torch[cu121]
- nvidia-cudnn
- nvidia-cuda-runtime
- tensorflow-gpu
- Any package with "cuda" or "gpu" in the name

### 4. Verification Script
Run before commits:
```bash
python verify_cpu_only.py
```

### 5. Dependencies
All requirements files must specify CPU-only versions:
```
torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu
```

### 6. Code Standards
All audio/ML modules must check and force CPU mode:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torch
torch.set_num_threads(4)  # Optimize for CPU
assert not torch.cuda.is_available(), "GPU detected - CPU-only mode required"
```

### 7. Performance Expectations
- TTS synthesis: 2-3 seconds per sentence
- Audio transcription: Real-time capable
- Memory usage: 500MB-1GB for models
- CPU threads: 4 (configurable in .env.cpu)

### 8. CI/CD
All automated tests must run in CPU-only mode.
No GPU runners should be configured.

## Rationale
- **Portability**: Works on any machine without GPU
- **Cost**: No expensive GPU hardware needed
- **Simplicity**: No driver/CUDA version conflicts
- **Reproducibility**: Consistent behavior across environments

## Exceptions
NONE. This is a hard rule for this repository.
