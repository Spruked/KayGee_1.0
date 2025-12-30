# Installation Guide - CPU-Only Audio System

## Quick Install (CPU-Only)

```powershell
# Navigate to backend
cd c:\dev\Desktop\KayGee_1.0\Kay_Gee_1.0\backend

# Install CPU-only PyTorch first (prevents CUDA download)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install audio dependencies
pip install -r requirements_audio_cpu.txt

# Verify CPU mode
python -c "import torch; print(f'PyTorch CPU-only: {not torch.cuda.is_available()}')"
```

## What's Installed

**Cochlear Processor (CPU):**
- numpy, scipy, librosa
- soundfile, audioread
- Human-like hearing with SKG learning

**POM Voice (CPU):**
- Coqui TTS (CPU version)
- PyTorch CPU-only
- Articulatory vocal tract simulation

**No CUDA/GPU packages installed** ✅

## Performance Notes

- **TTS synthesis**: ~2-3 seconds per sentence on modern CPU
- **Audio transcription**: Real-time capable with Whisper base model
- **Memory usage**: ~500MB-1GB for models
- **Optimization**: Uses 4 CPU threads by default

## Troubleshooting

If you see CUDA errors:
```powershell
# Uninstall any GPU packages
pip uninstall torch torchvision torchaudio -y

# Reinstall CPU-only
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

Verify no GPU packages:
```powershell
pip list | Select-String -Pattern "cuda|cudnn|nvidia"
# Should return empty
```
