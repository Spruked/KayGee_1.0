# Installation Guide - CPU-Only Audio Stack (Kokoro + ACP)

## Quick Install

```powershell
cd c:\dev\Desktop\KayGee_1.0\Kay_Gee_1.0\backend
pip install -r requirements_audio_cpu.txt
```

## Active Voice/Hearing Stack

- **TTS router primary:** ACPHub (`router/orchestrator.py`)
- **TTS default voice:** Kokoro female `af_bella`
- **TTS local fallback:** Kokoro (via `KOKORO_CLI` or compatible Kokoro Python package)
- **TTS backup:** Edge neural voices (`edge-tts`)
- **STT router primary:** ACPHub (ACP when available, Whisper fallback)
- **ASR local baseline:** Whisper on CPU (`faster-whisper`)

## Optional Runtime Configuration

```powershell
# Kokoro CLI template (supports placeholders)
$env:KOKORO_CLI = "kokoro --text \"{text}\" --output \"{output}\" --voice \"{voice}\""

# ACP source of truth
$env:ACP_REPO = "C:\dev\Desktop\Adaptive_Cochlear_Processor_v1"

# Lock KayGee's default Kokoro voice
$env:KG_PRIMARY_KOKORO_VOICE = "af_bella"

# Optional ACP preprocessing command
$env:ACP_BRIDGE_CMD = "python C:\dev\Desktop\Adaptive_Cochlear_Processor_v1\bridge.py --input {input} --output {output}"

# Whisper model
$env:WHISPER_MODEL = "base"
```

## Verification

```powershell
python -c "from voice_stack import VoiceStack; from pathlib import Path; print(VoiceStack(Path('runtime_voice')).diagnostics())"
```

## Notes

- Legacy voice modules were removed from backend runtime.
- This stack is ACPHub-first with deterministic local fallbacks.
- Voice override is disabled by default; set `KG_ALLOW_VOICE_OVERRIDE=1` only if needed.
