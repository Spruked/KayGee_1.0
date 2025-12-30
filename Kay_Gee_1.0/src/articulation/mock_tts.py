"""
Mock TTS - Prints to console instead of speaking
For development without audio hardware
"""


class MockTTS:
    """Prints to console instead of speaking"""
    
    def synthesize(self, text, prosody):
        print(f"[TTS] {text} (pitch: {prosody['pitch']}, rate: {prosody['rate']})")
        return True  # Simulates success
