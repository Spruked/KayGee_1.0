"""
KayGee audio streaming bridge using Kokoro TTS + Edge backup and ACP + Whisper baseline.
"""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional

from voice_stack import VoiceStack

logger = logging.getLogger("kaygee.audio_bridge")


class AudioStreamingBridge:
    def __init__(self) -> None:
        runtime_dir = Path(__file__).parent / "runtime_voice"
        self.voice = VoiceStack(runtime_dir=runtime_dir)

    async def process_audio_chunk(self, audio_bytes: bytes, language: Optional[str] = None) -> Optional[Dict]:
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".wav", dir=self.voice.audio_dir)
            os.close(fd)
            audio_path = Path(tmp_path)
            audio_path.write_bytes(audio_bytes)
            return self.voice.transcribe(audio_path=audio_path, language=language)
        except Exception as exc:
            logger.exception("Audio chunk processing failed")
            return {"text": "", "confidence": 0.0, "error": str(exc)}

    async def synthesize_streaming(self, text: str, voice: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        try:
            result = await self.voice.synthesize(text=text, voice=voice)
            with open(result.file_path, "rb") as fh:
                while True:
                    chunk = fh.read(4096)
                    if not chunk:
                        break
                    yield chunk
        except Exception as exc:
            logger.exception("Speech synthesis failed")
            yield b""

    def transcribe_file(self, audio_path: Path, language: Optional[str] = None) -> Dict:
        return self.voice.transcribe(audio_path=audio_path, language=language)

    def get_diagnostics(self) -> Dict:
        info = self.voice.diagnostics()
        info["status"] = "operational"
        return info


audio_processor = AudioStreamingBridge()
