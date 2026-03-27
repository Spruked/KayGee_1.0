# Bio-Inspired Audio System - Current Architecture

## Runtime Topology

### Hearing Path (Browser/Plugin -> ACPHub -> ACP/Whisper)

1. Audio input arrives as file path or base64.
2. `voice_stack.py` attempts ACPHub STT router first.
3. ACP core runs when available (typically WSL); Whisper baseline is deterministic fallback.
4. Result is exposed via `/plugin/stt`.

### Voice Path (KayGee -> ACPHub -> Kokoro -> Edge Fallback)

1. Text response is generated in KayGee core.
2. `voice_stack.py` attempts ACPHub TTS router first.
3. Primary voice default is Kokoro female `af_bella`.
4. If Kokoro is unavailable/fails, Edge neural TTS is used.
5. Output is served via `/audio/{filename}` and `/plugin/tts`.

## Key Files

- `backend/voice_stack.py` - primary voice/hearing orchestration
- `backend/audio_streaming_bridge.py` - streaming wrapper
- `backend/main.py` - plugin endpoints (`/plugin/tts`, `/plugin/stt`, `/api/audio/diagnostics`)

## Removed

- Legacy voice runtime tree
- Legacy voice dependency path in active backend service

## Design Goals

- CPU-only friendly
- Sidecar/plugin integration with True_Mark
- Swappable model providers through environment configuration
- ACPHub-first routing with Whisper baseline safety
