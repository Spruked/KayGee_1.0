"""
KayGee runtime voice stack.

Primary path:
- ACPHub orchestration for STT/TTS
- Kokoro default female voice (af_bella)

Fallback path:
- Local Kokoro provider
- Edge TTS backup
- Whisper baseline transcription
"""

from __future__ import annotations

import asyncio
import base64
import importlib
import logging
import os
import shlex
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger("kaygee.voice_stack")


@dataclass
class TTSResult:
    engine: str
    file_path: Path
    mime_type: str


class KokoroProvider:
    """Primary TTS provider. Supports CLI hook + best-effort Python hook."""

    def __init__(self, default_voice: str) -> None:
        self.cli = os.getenv("KOKORO_CLI", "").strip()
        self.default_voice = default_voice

    async def synthesize(self, text: str, output_path: Path, voice: Optional[str] = None) -> TTSResult:
        if self.cli:
            await self._synthesize_with_cli(text, output_path, voice)
            return TTSResult(engine="kokoro", file_path=output_path, mime_type="audio/wav")

        if await self._synthesize_with_python(text, output_path, voice):
            return TTSResult(engine="kokoro", file_path=output_path, mime_type="audio/wav")

        raise RuntimeError("Kokoro provider unavailable. Set KOKORO_CLI or install a supported Kokoro Python package.")

    async def _synthesize_with_cli(self, text: str, output_path: Path, voice: Optional[str]) -> None:
        cmd_template = self.cli
        replacements = {
            "{text}": text,
            "{output}": str(output_path),
            "{voice}": voice or self.default_voice,
        }
        cmd = cmd_template
        for key, value in replacements.items():
            cmd = cmd.replace(key, value)

        parts = shlex.split(cmd)
        proc = await asyncio.create_subprocess_exec(
            *parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Kokoro CLI failed: {stderr.decode(errors='ignore').strip()}")
        if not output_path.exists():
            raise RuntimeError("Kokoro CLI completed but did not produce an output file")

    async def _synthesize_with_python(self, text: str, output_path: Path, voice: Optional[str]) -> bool:
        try:
            import kokoro  # type: ignore
        except Exception:
            return False

        if not hasattr(kokoro, "generate"):
            return False

        loop = asyncio.get_running_loop()

        def _run_generate() -> tuple[np.ndarray, int]:
            generated = kokoro.generate(text=text, voice=voice or self.default_voice)
            if isinstance(generated, tuple) and len(generated) >= 2:
                audio, sample_rate = generated[0], int(generated[1])
            else:
                audio = generated
                sample_rate = 24000
            arr = np.asarray(audio, dtype=np.float32)
            return arr, sample_rate

        audio, sample_rate = await loop.run_in_executor(None, _run_generate)
        _write_float_wav(output_path, audio, sample_rate)
        return True


class EdgeProvider:
    """Backup TTS provider using Microsoft Edge neural voices."""

    async def synthesize(self, text: str, output_path: Path, voice: Optional[str] = None) -> TTSResult:
        try:
            import edge_tts  # type: ignore
        except Exception as exc:
            raise RuntimeError("edge-tts is not installed") from exc

        selected_voice = voice or os.getenv("EDGE_TTS_VOICE", "en-US-AvaNeural")
        communicate = edge_tts.Communicate(text=text, voice=selected_voice)
        await communicate.save(str(output_path))
        if not output_path.exists():
            raise RuntimeError("Edge TTS did not produce an output file")
        return TTSResult(engine="edge-tts", file_path=output_path, mime_type="audio/mp3")


class ACPBridge:
    """
    ACP preprocessing bridge.

    If `ACP_BRIDGE_CMD` is configured, it is executed before transcription.
    The command can use placeholders: {input} and {output}.
    """

    def __init__(self) -> None:
        self.acp_repo = Path(os.getenv("ACP_REPO", r"C:\dev\Desktop\Adaptive_Cochlear_Processor_v1"))
        self.bridge_cmd = os.getenv("ACP_BRIDGE_CMD", "").strip()

    def preprocess(self, input_audio: Path) -> Path:
        if self.bridge_cmd:
            output_audio = input_audio.with_name(f"{input_audio.stem}.acp{input_audio.suffix}")
            cmd = self.bridge_cmd.replace("{input}", str(input_audio)).replace("{output}", str(output_audio))
            completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if completed.returncode != 0:
                raise RuntimeError(f"ACP bridge command failed: {completed.stderr.strip()}")
            if output_audio.exists():
                return output_audio
            return input_audio

        # Default safe behavior when no ACP command is configured: pass-through.
        if self.acp_repo.exists():
            logger.info("ACP repository detected at %s (pass-through mode)", self.acp_repo)
        return input_audio


class ACPHubProvider:
    """Adapter for ACPHub orchestration package."""

    def __init__(self, acp_repo: Path, audio_dir: Path, primary_voice: str) -> None:
        self.acp_repo = acp_repo
        self.audio_dir = audio_dir
        self.primary_voice = primary_voice
        self.hub: Any = None
        self.import_error: str = ""
        self._initialize()

    def _initialize(self) -> None:
        if not self.acp_repo.exists():
            self.import_error = f"ACP repo not found at {self.acp_repo}"
            return

        # Ensure ACP package defaults are aligned with KayGee runtime.
        os.environ.setdefault("ACP_AUDIO_DIR", str(self.audio_dir))
        os.environ.setdefault("ACP_KOKORO_DEFAULT_VOICE", self.primary_voice)
        os.environ.setdefault("ACP_KOKORO_DEFAULT_LANG", "en-us")
        os.environ.setdefault("ACP_EDGE_DEFAULT_VOICE", os.getenv("EDGE_TTS_VOICE", "en-US-AvaNeural"))

        repo_str = str(self.acp_repo)
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)

        try:
            orchestrator = importlib.import_module("router.orchestrator")
            hub_cls = getattr(orchestrator, "ACPHub")
            self.hub = hub_cls()
            logger.info("ACPHub initialized from %s", self.acp_repo)
        except Exception as exc:
            self.hub = None
            self.import_error = str(exc)
            logger.warning("ACPHub initialization failed: %s", exc)

    @property
    def available(self) -> bool:
        return self.hub is not None

    async def synthesize(self, text: str, voice: str) -> TTSResult:
        if not self.available:
            raise RuntimeError(self.import_error or "ACPHub unavailable")

        loop = asyncio.get_running_loop()

        def _run() -> Path:
            audio_path = self.hub.speak(text=text, speaker_id=voice)
            return Path(audio_path)

        path = await loop.run_in_executor(None, _run)
        if path.is_absolute():
            resolved_path = path
        else:
            candidates = [
                (Path.cwd() / path).resolve(),
                (self.audio_dir / path.name).resolve(),
                (self.acp_repo / path).resolve(),
            ]
            resolved_path = next((candidate for candidate in candidates if candidate.exists()), candidates[0])
        if not resolved_path.exists():
            raise RuntimeError(f"ACPHub generated path not found: {resolved_path}")

        mime = "audio/wav" if resolved_path.suffix.lower() == ".wav" else "audio/mpeg"
        return TTSResult(engine="acp-hub", file_path=resolved_path, mime_type=mime)

    def transcribe(self, audio_path: Path, language: Optional[str]) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError(self.import_error or "ACPHub unavailable")

        def _run() -> Dict[str, Any]:
            context: Dict[str, Any] = {"source": "kaygee_voice_stack"}
            if language:
                context["language"] = language
            return self.hub.stt.transcribe(str(audio_path), context)

        raw = _run()
        return {
            "text": (raw.get("transcript") or "").strip(),
            "confidence": float(raw.get("confidence", 0.0) or 0.0),
            "engine": str(raw.get("_source", "acp-hub")),
            "router_result": raw,
        }

    def status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False, "error": self.import_error}
        try:
            return {"available": True, "status": self.hub.get_system_status()}
        except Exception as exc:
            return {"available": True, "status_error": str(exc)}


class WhisperBaseline:
    """CPU-first transcription baseline with faster-whisper fallback to whisper."""

    def __init__(self) -> None:
        self._fw_model = None
        self._ow_model = None

    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        text, confidence, backend = self._transcribe_faster_whisper(audio_path, language)
        if text:
            return {
                "text": text,
                "confidence": confidence,
                "engine": backend,
            }

        text, confidence, backend = self._transcribe_openai_whisper(audio_path, language)
        return {
            "text": text,
            "confidence": confidence,
            "engine": backend,
        }

    def _transcribe_faster_whisper(self, audio_path: Path, language: Optional[str]) -> tuple[str, float, str]:
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except Exception:
            return "", 0.0, "none"

        if self._fw_model is None:
            model_name = os.getenv("WHISPER_MODEL", "base")
            self._fw_model = WhisperModel(model_name, device="cpu", compute_type="int8")

        segments, info = self._fw_model.transcribe(str(audio_path), language=language)
        pieces = []
        confs = []
        for seg in segments:
            seg_text = (seg.text or "").strip()
            if seg_text:
                pieces.append(seg_text)
            prob = 1.0 - max(0.0, min(1.0, getattr(seg, "no_speech_prob", 0.5)))
            confs.append(prob)

        if not pieces:
            return "", 0.0, "faster-whisper"

        confidence = float(sum(confs) / len(confs)) if confs else 0.7
        return " ".join(pieces), confidence, f"faster-whisper:{getattr(info, 'language', 'unknown')}"

    def _transcribe_openai_whisper(self, audio_path: Path, language: Optional[str]) -> tuple[str, float, str]:
        try:
            import whisper  # type: ignore
        except Exception:
            return "", 0.0, "none"

        if self._ow_model is None:
            model_name = os.getenv("WHISPER_MODEL", "base")
            self._ow_model = whisper.load_model(model_name, device="cpu")

        result = self._ow_model.transcribe(str(audio_path), language=language)
        text = (result.get("text") or "").strip()
        return text, 0.7 if text else 0.0, "openai-whisper"


class VoiceStack:
    def __init__(self, runtime_dir: Path) -> None:
        self.runtime_dir = runtime_dir
        self.audio_dir = runtime_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        primary_voice = os.getenv("KG_PRIMARY_KOKORO_VOICE", os.getenv("ACP_KOKORO_DEFAULT_VOICE", "af_bella")).strip()
        self.primary_voice = primary_voice or "af_bella"
        self.allow_voice_override = os.getenv("KG_ALLOW_VOICE_OVERRIDE", "0").strip() == "1"
        self.acp_repo = Path(os.getenv("ACP_REPO", r"C:\dev\Desktop\Adaptive_Cochlear_Processor_v1"))

        self.kokoro = KokoroProvider(default_voice=self.primary_voice)
        self.edge = EdgeProvider()
        self.acp = ACPBridge()
        self.whisper = WhisperBaseline()
        self.acp_hub = ACPHubProvider(acp_repo=self.acp_repo, audio_dir=self.audio_dir, primary_voice=self.primary_voice)

    def _resolved_voice(self, voice: Optional[str]) -> str:
        if self.allow_voice_override and voice:
            return voice
        return self.primary_voice

    async def synthesize(self, text: str, voice: Optional[str] = None) -> TTSResult:
        stem = f"kg_{int(asyncio.get_running_loop().time() * 1000)}"
        wav_path = self.audio_dir / f"{stem}.wav"
        selected_voice = self._resolved_voice(voice)

        if self.acp_hub.available:
            try:
                return await self.acp_hub.synthesize(text=text, voice=selected_voice)
            except Exception as acp_err:
                logger.warning("ACPHub synthesis failed, using local fallback path: %s", acp_err)

        try:
            return await self.kokoro.synthesize(text=text, output_path=wav_path, voice=selected_voice)
        except Exception as kokoro_err:
            logger.warning("Kokoro synthesis failed, using Edge backup: %s", kokoro_err)
            mp3_path = self.audio_dir / f"{stem}.mp3"
            return await self.edge.synthesize(text=text, output_path=mp3_path, voice=None)

    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> Dict[str, Any]:
        if self.acp_hub.available:
            try:
                result = self.acp_hub.transcribe(audio_path=audio_path, language=language)
                result["acp_audio_path"] = str(audio_path)
                return result
            except Exception as acp_err:
                logger.warning("ACPHub transcription failed, using local fallback path: %s", acp_err)

        acp_audio = self.acp.preprocess(audio_path)
        local = self.whisper.transcribe(acp_audio, language=language)
        local["acp_audio_path"] = str(acp_audio)
        return local

    def decode_base64_audio(self, audio_base64: str, suffix: str = ".wav") -> Path:
        raw = base64.b64decode(audio_base64)
        fd, tmp_path = tempfile.mkstemp(suffix=suffix, dir=self.audio_dir)
        os.close(fd)
        path = Path(tmp_path)
        path.write_bytes(raw)
        return path

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "runtime_dir": str(self.runtime_dir),
            "audio_dir": str(self.audio_dir),
            "primary_voice": self.primary_voice,
            "allow_voice_override": self.allow_voice_override,
            "kokoro_cli_configured": bool(self.kokoro.cli),
            "acp_repo": str(self.acp.acp_repo),
            "acp_repo_exists": self.acp.acp_repo.exists(),
            "acp_bridge_cmd_configured": bool(self.acp.bridge_cmd),
            "acp_hub": self.acp_hub.status(),
            "whisper_model": os.getenv("WHISPER_MODEL", "base"),
        }


def _write_float_wav(path: Path, audio: np.ndarray, sample_rate: int) -> None:
    clipped = np.clip(audio, -1.0, 1.0)
    pcm16 = (clipped * 32767.0).astype(np.int16)

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm16.tobytes())
