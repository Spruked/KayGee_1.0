from TTS.api import TTS
import TTS

print(f"TTS package version: {getattr(TTS, '__version__', 'unknown')}")

try:
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    print("TTS model loaded successfully.")
    print(f"Available models: {tts.list_models()}")
except Exception as e:
    print(f"TTS integration test failed: {e}")
