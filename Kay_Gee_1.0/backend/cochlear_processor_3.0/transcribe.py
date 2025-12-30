"""
ASR Transcription Module using faster-whisper
CPU-ONLY MODE
"""
import logging
from typing import Union
import numpy as np

logger = logging.getLogger(__name__)

# Try to import faster-whisper
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
    logger.info("✅ Faster-whisper loaded")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("⚠️ Faster-whisper not available")

# Global model instance (lazy loading)
_model = None

def get_whisper_model():
    """Lazy load the Whisper model"""
    global _model
    if _model is None and WHISPER_AVAILABLE:
        try:
            # Use CPU-only, small model for speed
            _model = WhisperModel("tiny", device="cpu", compute_type="int8")
            logger.info("✅ Whisper model loaded (tiny, CPU)")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            _model = None
    return _model

def asr_transcribe(audio: Union[str, np.ndarray], language: str = "en") -> str:
    """
    Transcribe audio using faster-whisper

    Args:
        audio: Either a file path (str) or numpy array of audio data
        language: Language code (default: "en")

    Returns:
        Transcribed text
    """
    model = get_whisper_model()
    if not model:
        return "Speech recognition unavailable"

    try:
        if isinstance(audio, str):
            # Audio is a file path
            segments, info = model.transcribe(audio, language=language)
        else:
            # Audio is a numpy array
            segments, info = model.transcribe(audio, language=language)

        # Collect all text segments
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return f"Transcription error: {str(e)}"

def asr_transcribe_with_timestamps(audio: Union[str, np.ndarray], language: str = "en") -> dict:
    """
    Transcribe audio with timestamps

    Returns:
        Dict with 'text' and 'segments' containing timestamped transcription
    """
    model = get_whisper_model()
    if not model:
        return {"text": "Speech recognition unavailable", "segments": []}

    try:
        segments, info = model.transcribe(audio, language=language)

        result = {
            "text": " ".join([segment.text for segment in segments]),
            "segments": [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                for segment in segments
            ]
        }
        return result

    except Exception as e:
        logger.error(f"Transcription with timestamps failed: {e}")
        return {"text": f"Transcription error: {str(e)}", "segments": []}