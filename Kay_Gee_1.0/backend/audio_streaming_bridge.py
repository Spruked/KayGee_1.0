"""
Bio-Inspired Audio Streaming Bridge for KayGee
Complete integration - all cochlear and POM components
CPU-ONLY MODE
"""
import asyncio
import json
import numpy as np
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Optional
import logging

# Force CPU-only
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OMP_NUM_THREADS'] = '4'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add repo paths
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / 'cochlear_processor_3.0'))
sys.path.insert(0, str(backend_dir / 'POM_2.0'))

# Try to import components (graceful degradation)
try:
    from cochlear_processor_v3 import CochlearProcessorV3
    COCHLEAR_AVAILABLE = True
    logger.info("✅ Cochlear Processor loaded")
except Exception as e:
    COCHLEAR_AVAILABLE = False
    logger.warning(f"⚠️ Cochlear not available: {e}")

# Lazy load POM to avoid heavy TTS dependencies at startup
POM_AVAILABLE = None
PhonatoryOutputModule = None

def _load_pom():
    global POM_AVAILABLE, PhonatoryOutputModule
    if POM_AVAILABLE is None:
        try:
            from phonitory_output_module import PhonatoryOutputModule as POM
            PhonatoryOutputModule = POM
            POM_AVAILABLE = True
            logger.info("✅ POM loaded (lazy)")
        except Exception as e:
            POM_AVAILABLE = False
            logger.warning(f"⚠️ POM not available: {e}")
    return POM_AVAILABLE


class AudioStreamingBridge:
    """Simplified audio bridge for initial launch"""
    
    def __init__(self):
        logger.info("🖥️ Initializing Audio Bridge (CPU-only)...")
        self.sample_rate = 16000
        self.audio_buffer = []
        
        if COCHLEAR_AVAILABLE:
            try:
                self.cochlear = CochlearProcessorV3()
                logger.info("✅ Cochlear initialized")
            except Exception as e:
                logger.warning(f"⚠️ Cochlear init failed: {e}")
                self.cochlear = None
        else:
            self.cochlear = None
        
        if POM_AVAILABLE:
            try:
                self.pom = PhonatoryOutputModule()
                logger.info("✅ POM initialized")
            except Exception as e:
                logger.warning(f"⚠️ POM init failed: {e}")
                self.pom = None
        else:
            self.pom = None
    
    async def process_audio_chunk(self, audio_bytes: bytes) -> Optional[Dict]:
        """Process audio chunk using Cochlear Processor"""
        if not self.cochlear:
            logger.warning("Cochlear Processor not available")
            return {'transcript': 'Audio processing unavailable', 'confidence': 0.0}
        
        try:
            # Convert bytes to numpy array (assuming 16-bit PCM)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Create temporary context for processing
            context = {
                'topic': 'conversation',
                'environment': 'real_time',
                'speaker_id': 'user'
            }
            
            # Use Cochlear Processor for transcription
            # Note: This is a simplified call - in production you'd save to temp file
            import tempfile
            import wave
            
            # Save audio bytes to temp WAV file for processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                with wave.open(temp_file, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_bytes)
            
            # Process with Cochlear Processor
            result = self.cochlear.process_audio_human_like(temp_path, context)
            
            # Clean up temp file
            import os
            os.unlink(temp_path)
            
            transcript = result.get('transcription', {}).get('corrected', 'Transcription failed')
            confidence = result.get('transcription', {}).get('confidence_after', 0.5)
            
            logger.info(f"Transcribed: '{transcript}' (confidence: {confidence:.2f})")
            return {
                'transcript': transcript,
                'confidence': confidence,
                'corrections': result.get('transcription', {}).get('corrections', [])
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return {'transcript': f'Error: {str(e)}', 'confidence': 0.0}
    
    async def synthesize_streaming(self, text: str, **kwargs) -> AsyncGenerator[bytes, None]:
        """Synthesize speech using Phonatory Output Module"""
        if not self.pom and not _load_pom():
            logger.warning("POM not available")
            yield b''
            return
        
        if not self.pom:
            # Initialize POM if not already done
            try:
                self.pom = PhonatoryOutputModule()
                logger.info("✅ POM initialized on demand")
            except Exception as e:
                logger.error(f"Failed to initialize POM: {e}")
                yield b''
                return
        
        try:
            # Use POM to synthesize speech
            output_path = self.pom.phonate(text, **kwargs)
            
            # Read the synthesized audio file and stream it
            with open(output_path, 'rb') as audio_file:
                while chunk := audio_file.read(4096):  # Read in 4KB chunks
                    yield chunk
            
            # Clean up the temporary file
            import os
            os.unlink(output_path)
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            yield b''
    
    def get_diagnostics(self) -> Dict:
        """Get system diagnostics"""
        # Ensure POM availability is checked
        pom_status = _load_pom() if POM_AVAILABLE is None else POM_AVAILABLE
        return {
            'status': 'operational',
            'cochlear_available': COCHLEAR_AVAILABLE,
            'pom_available': pom_status,
            'cpu_mode': True
        }


# Global instance
audio_processor = AudioStreamingBridge()
