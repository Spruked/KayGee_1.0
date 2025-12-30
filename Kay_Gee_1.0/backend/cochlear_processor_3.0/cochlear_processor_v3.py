# cochlear_processor_v3.py
from skg_perceptual_filter import SKGPerceptualFilter, SpeakerKnowledgeGraph
from cognitive_inference import CognitiveInferenceEngine
from correction_loop import RealtimeCorrectionLoop
from skg_learning_bridge import SKGLearningBridge
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
import uuid

# Adjusted imports for v2.0 compatibility
try:
    from transcribe import asr_transcribe
    from vault_writer import write_vault_record as vault_write_trace
except ImportError:
    # Fallback if not found
    def asr_transcribe(audio):
        return "sample transcription"
    def vault_write_trace(trace):
        print("Vault write:", trace)

class CochlearProcessorV3:
    """
    Human-like audio processing with mishearing and correction.
    """
    
    def __init__(self, skg_path: str = "hearing_skg.json"):
        self.skg = SpeakerKnowledgeGraph(skg_path)
        self.perceptual_filter = SKGPerceptualFilter(self.skg)
        self.cognitive_engine = CognitiveInferenceEngine()
        self.correction_loop = RealtimeCorrectionLoop(self)
        self.learning_bridge = SKGLearningBridge(self.skg, self.perceptual_filter)
        
        self.correction_callbacks = []
    
    def process_audio_human_like(self, audio_path: str, context: Dict, speaker_id: Optional[str] = None) -> Dict:
        """
        Full pipeline: perceptual filtering → transcription → inference → correction → learning
        """
        print(f"🧠 Processing audio '{audio_path}' with human-like perception...")
        
        # 1. Load audio
        audio_data, sr = self._load_audio(audio_path)
        
        # 2. Perceptual filtering (simulates ear/brain)
        filtered_audio, perceptual_report = self.perceptual_filter.apply_perceptual_filter(audio_data, context, speaker_id)
        
        # 3. Transcription (with confidence scores)
        transcript, confidence_scores = self._transcribe_with_confidence(filtered_audio, sr)
        
        # 4. Cognitive inference (fill gaps)
        inferred_transcript, corrections = self.cognitive_engine.process_with_inference(
            transcript, confidence_scores, perceptual_report
        )
        
        # 5. Real-time correction loop (insert corrections)
        final_transcript = self.correction_loop.monitor_and_correct(
            inferred_transcript,
            on_correction=self._trigger_reresynthesis,
            simulate_realtime=True
        )
        
        # 6. Build trace with all metadata
        trace = self._build_enriched_trace(
            audio_path=audio_path,
            original_transcript=transcript,
            corrected_transcript=final_transcript,
            corrections=corrections,
            perceptual_report=perceptual_report,
            context=context,
            speaker_id=speaker_id
        )
        
        # 7. Write to vault
        vault_write_trace(trace)
        
        # 8. Learning: update mastery based on corrections
        for correction in corrections:
            correction["speaker"] = speaker_id or "unknown"
            correction["context"] = context.get("topic", "general")
            self.learning_bridge.process_correction(correction)
        
        print(f"   → Final transcript: '{final_transcript[:80]}...'")
        print(f"   → Corrections made: {len(corrections)}")
        print(f"   → Perceptual confidence: {perceptual_report['confidence_factor']:.2f}")
        
        return trace
    
    def _load_audio(self, path: str) -> Tuple[np.ndarray, int]:
        """Load audio file (placeholder: use librosa)"""
        try:
            import librosa
            return librosa.load(path, sr=16000)
        except (ImportError, FileNotFoundError):
            # Fallback: generate dummy audio for testing
            print("⚠️  Audio file not found or librosa not available, using dummy audio")
            # Generate 2 seconds of dummy audio
            duration = 2.0
            sr = 16000
            t = np.linspace(0, duration, int(sr * duration))
            audio = 0.5 * np.sin(2 * np.pi * 300 * t)  # 300Hz tone
            audio += 0.3 * np.sin(2 * np.pi * 2000 * t)  # Higher frequency
            return audio.astype(np.float32), sr
    
    def _transcribe_with_confidence(self, audio: np.ndarray, sr: int) -> Tuple[str, List[float]]:
        """
        Enhanced transcription that returns confidence scores per word.
        In production: modify Whisper to return token confidences.
        """
        # Simulate: Whisper returns transcript + confidence scores
        transcript = asr_transcribe(audio)  # Assuming it takes audio array or path
        
        # Generate confidence scores (simulated: lower for complex words)
        words = transcript.split()
        confidence_scores = [
            0.9 - (len(word) * 0.01) + np.random.normal(0, 0.05)
            for word in words
        ]
        confidence_scores = [max(0.1, min(1.0, c)) for c in confidence_scores]
        
        return transcript, confidence_scores
    
    def _build_enriched_trace(self, **data) -> Dict:
        """Build vault trace with all human-like processing metadata"""
        trace = {
            "trace_id": self._generate_trace_id(),
            "timestamp": time.time(),
            "processor": "cochlear_v3_human_like",
            "audio_path": data["audio_path"],
            "speaker_id": data.get("speaker_id"),
            "transcription": {
                "original": data["original_transcript"],
                "corrected": data["corrected_transcript"],
                "corrections": data["corrections"],
                "confidence_before": np.mean([c["confidence_before"] for c in data["corrections"]]) if data["corrections"] else 0.8,
                "confidence_after": np.mean([c["confidence_after"] for c in data["corrections"]]) if data["corrections"] else 0.8
            },
            "perceptual": data["perceptual_report"],
            "context": data["context"],
            "learning": self.learning_bridge.get_mastery_report()
        }
        
        # Link to previous trace for causality
        trace["prev_trace_id"] = self._get_last_trace_id()
        
        return trace
    
    def _trigger_reresynthesis(self, wrong: str, right: str):
        """If confidence is too low, trigger re-synthesis with clearer voice"""
        print(f"🔄 Correction triggered: '{wrong}' → '{right}'")
        
        # Notify any registered callbacks (could trigger POM re-synthesis)
        for callback in self.correction_callbacks:
            callback(wrong, right)
    
    def add_correction_callback(self, callback):
        """Register callback for re-synthesis triggers"""
        self.correction_callbacks.append(callback)
    
    def get_learning_summary(self) -> Dict:
        """Export Caleon's hearing improvement over time"""
        mastery = self.learning_bridge.get_mastery_report()
        return {
            "total_corrections_processed": mastery["total_corrections"],
            "avg_phoneme_mastery": mastery["avg_phoneme_mastery"],
            "avg_speaker_mastery": mastery["avg_speaker_mastery"],
            "phoneme_mastery": mastery["phoneme_mastery"],
            "speaker_mastery": mastery["speaker_mastery"],
            "perceptual_confidence_trend": self.perceptual_filter.state.attention_level
        }
    
    def _generate_trace_id(self) -> str:
        return str(uuid.uuid4())
    
    def _get_last_trace_id(self) -> str:
        # Placeholder
        return "prev_trace_123"


class FastCochlearProcessor(CochlearProcessorV3):
    """
    Optimized for real-time human-like processing.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-allocate buffers
        self.audio_buffer = np.zeros(16000 * 10)  # 10-second buffer
        
        # JIT compile critical filters
        self._jit_compile_filters()
        
        # Use faster ASR backend (Whisper.cpp or ONNX Runtime)
        self.asr_backend = "whisper_cpp"  # 3x faster than Python Whisper
        
    def _jit_compile_filters(self):
        """Numba JIT compilation for perceptual filters"""
        try:
            from numba import jit
            
            @jit(nopython=True)
            def fast_frequency_masking(fft, frequencies, sensitivity_map):
                for i in range(len(frequencies)):
                    freq = frequencies[i]
                    # Linear search (fast enough for small arrays)
                    for f_key, sens in sensitivity_map.items():
                        if abs(freq - f_key) < 100:
                            fft[i] *= sens
                            break
                    return fft
            
            self._fast_mask = fast_frequency_masking
        except ImportError:
            self._fast_mask = None
    
    def process_chunked(self, audio_stream, chunk_size=1600):
        """
        Process audio in small chunks for real-time performance.
        """
        for i in range(0, len(audio_stream), chunk_size):
            chunk = audio_stream[i:i+chunk_size]
            
            # Fast path: minimal processing if confidence is high
            if self._should_use_fast_path(chunk):
                transcript = self._fast_transcribe(chunk)
                yield transcript, 0.8, []  # High confidence, no corrections
            else:
                # Slow path: full human-like processing
                trace = self.process_audio_human_like(
                    chunk, context={"is_realtime": True}
                )
                yield trace["transcription"]["corrected"], trace["transcription"]["confidence_after"], trace["transcription"]["corrections"]
    
    def _should_use_fast_path(self, audio_chunk: np.ndarray) -> bool:
        """
        Use fast path when:
        - High attention level
        - No recent dropouts
        - Mastery > 0.8 for this context
        """
        return (
            self.perceptual_filter.state.attention_level > 0.8 and
            len(self.perceptual_filter.state.recent_phoneme_memory or []) > 20 and
            self.plasticity_engine.context_mastery.get(self._extract_context("current"), 0) > 0.8
        )
    
    def _fast_transcribe(self, audio_chunk: np.ndarray) -> str:
        """Use pre-warmed ASR model for low-latency transcription"""
        # Whisper.cpp with GPU acceleration
        return self.asr_cpp.transcribe(
            audio_chunk,
            beam_size=1,  # Fast, low-accuracy mode
            best_of=1,
            language="en"
        )
    
    def _extract_context(self, audio_path: str) -> str:
        """Extract context from path (speaker, topic, environment)"""
        # Example: "audio/phil_interview_tech.wav" → "phil_tech"
        parts = audio_path.split('/')[-1].replace('.wav', '').split('_')
        return f"{parts[0]}_{parts[-1]}" if len(parts) >= 2 else "general"


class HumanHearingProfile:
    """Preset profiles for different human hearing conditions"""
    
    PROFILES = {
        "young_adult": {
            "attention_level": 0.9,
            "frequency_sensitivity": "full_range",
            "confidence": 0.9,
            "correction_rate": 0.05
        },
        "distracted": {
            "attention_level": 0.4,
            "frequency_sensitivity": "reduced_high_freq",
            "confidence": 0.6,
            "correction_rate": 0.3
        },
        "hearing_impaired": {
            "attention_level": 0.7,
            "frequency_sensitivity": "sloping_loss",  # High-freq loss
            "confidence": 0.5,
            "correction_rate": 0.4
        },
        "expert_listener": {
            "attention_level": 0.95,
            "frequency_sensitivity": "enhanced_midrange",
            "confidence": 0.95,
            "correction_rate": 0.02
        }
    }
    
    @classmethod
    def apply_profile(cls, processor: CochlearProcessorV3, profile_name: str):
        """Set processor to simulate a specific human profile"""
        profile = cls.PROFILES[profile_name]
        
        pf = processor.perceptual_filter
        pf.state.attention_level = profile["attention_level"]
        
        # Adjust frequency sensitivity
        if profile["frequency_sensitivity"] == "reduced_high_freq":
            for f in pf.state.frequency_sensitivity:
                if f > 8000:
                    pf.state.frequency_sensitivity[f] *= 0.5
        
        processor.correction_loop.callback_threshold = profile["confidence"]
        processor.cognitive_engine.confidence_threshold = profile["confidence"]