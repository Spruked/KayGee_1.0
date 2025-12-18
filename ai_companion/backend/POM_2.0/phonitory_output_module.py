# phonitory_output_module.py


import logging
import json
import time
from TTS.api import TTS
from pydub import AudioSegment
from larynx_sim import LarynxSimulator
from POM.formant_filter import FormantFilter
from POM.tongue_artic import TongueArticulator
from POM.lip_control import LipController
from POM.uvula_control import UvulaController

# === Biological Naming ===

class PhonatoryOutputModule:
    """
    Simulates laryngeal phonation and vocal emission using Coqui TTS.
    Maps symbolic payloads into voiced speech with advanced phonatory processing.
    """

    def __init__(self, config_path="voice_config.json"):
        # Setup logging (if not already set)
        logging.basicConfig(level=logging.INFO, filename="synthesis.log")
        self.logger = logging.getLogger(__name__)
        # Load config
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            raise
        self.model_name = config.get("model_name", "tts_models/en/ljspeech/tacotron2-DDC")
        self.gpu = config.get("use_gpu", False)
        try:
            self.tts = TTS(model_name=self.model_name, progress_bar=False, gpu=self.gpu)
        except Exception as e:
            self.logger.error(f"TTS initialization failed: {str(e)}")
            raise
        self.logger.info(f"PhonatoryOutputModule initialized with: {self.model_name}, GPU: {self.gpu}")
        # Pass config to advanced modules if available
        self.larynx = LarynxSimulator(config.get("larynx_params", {}))
        self.formant = FormantFilter(config.get("formant_params", {}))
        self.tongue = TongueArticulator(config.get("tongue_params", {}))
        self.lip = LipController(config.get("lip_params", {}))
        self.uvula = UvulaController(config.get("uvula_params", {}))


    def phonate(self, text: str, out_path=None, pitch_factor=1.0, formant_target=None, articulation=None, nasalization=None):
        """
        Generate voice output from symbolic text, with advanced phonatory hooks.

        Args:
            text (str): Input text to synthesize.
            out_path (str): Path to save the output WAV file (default: timestamped file).
            pitch_factor (float): Multiplier for pitch modulation (default: 1.0).
            formant_target (dict): Formant frequencies (e.g., {"f1": 500, "f2": 1500}).
            articulation (dict): Articulation parameters (e.g., {"vowel": "a"}).
            nasalization (dict): Nasalization parameters (e.g., {"level": 0.5}).

        Returns:
            str: Path to the output WAV file.

        Raises:
            ValueError: If input text or parameters are invalid.
            RuntimeError: If synthesis or audio processing fails.
        """
        # Input validation
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string")
        if out_path is None:
            out_path = f"output_voice_{int(time.time())}.wav"
        if not out_path.endswith(".wav"):
            raise ValueError("Output path must be a .wav file")
        if not isinstance(pitch_factor, (int, float)) or pitch_factor <= 0:
            raise ValueError("Pitch factor must be a positive number")

        try:
            # Synthesize base audio
            self.tts.tts_to_file(text=text, file_path=out_path)
            self.logger.info(f"Base audio synthesized to {out_path}")
            # Load and process audio
            audio_data = AudioSegment.from_wav(out_path)
            # Advanced processing (if implemented)
            if hasattr(self.larynx, 'modulate_pitch'):
                audio_data = self.larynx.modulate_pitch(audio_data, pitch_factor)
            if formant_target and hasattr(self.formant, 'shape_vowel'):
                audio_data = self.formant.shape_vowel(audio_data, formant_target)
            if articulation:
                if hasattr(self.tongue, 'apply_articulation_effects'):
                    audio_data = self.tongue.apply_articulation_effects(audio_data, articulation)
                if hasattr(self.lip, 'apply_lip_effects'):
                    audio_data = self.lip.apply_lip_effects(audio_data, articulation)
            if nasalization and hasattr(self.uvula, 'apply_nasalization_effects'):
                audio_data = self.uvula.apply_nasalization_effects(audio_data, nasalization)
            audio_data.export(out_path, format="wav")
            self.logger.info(f"Voice emitted to {out_path}")
            return out_path
        except Exception as e:
            self.logger.error(f"Phonation failed: {str(e)}")
            raise RuntimeError(f"Phonation failed: {str(e)}")

    def diagnostics(self):
        import TTS
        self.logger.info(f"TTS package version: {getattr(TTS, '__version__', 'unknown')}")
        self.logger.info(f"Available models: {self.tts.list_models()}")
        self.logger.info(f"LarynxSimulator status: {'Initialized' if self.larynx else 'Not initialized'}")
        self.logger.info(f"FormantFilter status: {'Initialized' if self.formant else 'Not initialized'}")
        self.logger.info(f"TongueArticulator status: {'Initialized' if self.tongue else 'Not initialized'}")
        self.logger.info(f"LipController status: {'Initialized' if self.lip else 'Not initialized'}")
        self.logger.info(f"UvulaController status: {'Initialized' if self.uvula else 'Not initialized'}")


# Demo usage with logging
if __name__ == "__main__":
    emitter = PhonatoryOutputModule()
    try:
        out_path = emitter.phonate("This is the Phonatory Output Module speaking for the first time.")
        print(f"Synthesized speech saved to: {out_path}")
    except Exception as e:
        print(f"Error during synthesis: {e}")
    emitter.diagnostics()
    print("Diagnostics logged to synthesis.log.")
