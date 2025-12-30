"""
KayGee_1.0 Voice Dashboard
Live monitor + Speak + Listen (CPU-only, local)
"""

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
import threading
import time
import queue
import json
import random
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local TTS (Coqui) - replaced by audio bridge
try:
    from backend.audio_streaming_bridge import audio_processor
    HAS_AUDIO_BRIDGE = True
    print("✅ Audio streaming bridge loaded")
except Exception as e:
    print(f"Audio bridge not available: {e}")
    HAS_AUDIO_BRIDGE = False
    # Fallback to direct TTS
    try:
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False, gpu=False)
        HAS_TTS = True
    except Exception as e:
        print(f"Coqui TTS not available: {e}")
        HAS_TTS = False

# Local Speech Recognition (faster-whisper) - now in audio bridge
HAS_STT = HAS_AUDIO_BRIDGE

# Try to import the real KayGee system
try:
    from main import VaultedReasonerSystem
    HAS_KAYGEE = True
except Exception as e:
    print(f"KayGee system not available: {e}")
    HAS_KAYGEE = False

# Queue for voice input
voice_queue = queue.Queue()

def listen_loop():
    """Background thread: records and transcribes when you speak"""
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        print("Missing dependencies for voice input. Install: pip install sounddevice numpy")
        return

    print("\n🎤 KayGee is listening... Speak now (or Ctrl+C to stop dashboard)")
    
    sample_rate = 16000
    duration = 3  # Record in 3-second chunks
    
    while True:
        try:
            # Record audio
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            # Convert to bytes for audio bridge
            audio_bytes = (audio * 32767).astype('int16').tobytes()
            
            if HAS_AUDIO_BRIDGE:
                # Use audio bridge for transcription
                result = audio_processor.process_audio_chunk(audio_bytes)
                text = result.get('transcript', '')
                confidence = result.get('confidence', 0.0)
                
                if text and len(text) > 3 and confidence > 0.5:
                    print(f"\n🎧 You said: {text} (confidence: {confidence:.2f})")
                    voice_queue.put(text)
            else:
                print("Audio bridge not available for transcription")
                
        except Exception as e:
            print(f"Listening error: {e}")
            time.sleep(1)

# Mock system data (used when real system not available)
def get_status():
    return {
        "session": "sess_20251218_voice",
        "interactions": 42,
        "root": "a1b2c3...f9e0",
        "drift": False,
        "confidence": round(random.uniform(0.7, 1.0), 2),
        "philosopher": random.choice(["Kant", "Hume", "Locke", "Spinoza"]),
        "stability": round(random.uniform(0.88, 0.99), 2)
    }

quotes = [
    "The life of man is of no greater importance than that of an oyster. — Hume",
    "Act only according to that maxim whereby you can will it universal. — Kant",
    "Peace is not absence of war — it is a virtue. — Spinoza",
    "Knowledge is power. — Locke"
]

class VoiceDashboard:
    def __init__(self):
        self.console = Console()
        self.status = get_status()
        self.last_spoken = "I'm ready. Speak to me."
        self.last_heard = "Listening..."
        
        # Initialize real KayGee system if available
        self.kaygee = None
        if HAS_KAYGEE:
            try:
                self.kaygee = VaultedReasoner()
                print("✅ KayGee system initialized")
            except Exception as e:
                print(f"⚠️  KayGee initialization failed: {e}")

    def speak(self, text):
        """Speak text through audio bridge or fallback TTS"""
        print(f"\n💬 KayGee speaking: {text}")
        
        if HAS_AUDIO_BRIDGE:
            try:
                # Use audio bridge for synthesis
                import asyncio
                async def synthesize():
                    audio_chunks = []
                    async for chunk in audio_processor.synthesize_streaming(text):
                        audio_chunks.append(chunk)
                    return b''.join(audio_chunks)
                
                # Run async synthesis
                audio_data = asyncio.run(synthesize())
                
                # Save and play
                wav = "temp_kaygee.wav"
                with open(wav, 'wb') as f:
                    f.write(audio_data)
                
                # Play audio
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(wav)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except ImportError:
                    # Fallback to system player
                    import os
                    if sys.platform == "win32":
                        os.system(f"start /min {wav}")
                    elif sys.platform == "darwin":
                        os.system(f"afplay {wav}")
                    else:
                        os.system(f"aplay {wav}")
                    time.sleep(2)
                
                # Clean up
                Path(wav).unlink(missing_ok=True)
                self.last_spoken = text
                
            except Exception as e:
                print(f"⚠️  Audio bridge synthesis error: {e}")
                print(f"KayGee says: {text}")
        else:
            # Fallback to direct TTS
            if not HAS_TTS:
                print(f"KayGee says: {text}")
                return
            
            try:
                wav = "temp_kaygee.wav"
                tts.tts_to_file(text=text, file_path=wav)
                
                # Play audio (same as above)
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(wav)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                except ImportError:
                    import os
                    if sys.platform == "win32":
                        os.system(f"start /min {wav}")
                    elif sys.platform == "darwin":
                        os.system(f"afplay {wav}")
                    else:
                        os.system(f"aplay {wav}")
                    time.sleep(2)
                
                self.last_spoken = text
                Path(wav).unlink(missing_ok=True)
                
            except Exception as e:
                print(f"⚠️  TTS error: {e}")
                print(f"KayGee says: {text}")

    def process_user_input(self, user_text):
        """Process user input through real KayGee system or generate mock response"""
        if self.kaygee:
            try:
                # Real system interaction
                response = self.kaygee.process_interaction(user_text)
                response_text = response.get('text', str(response))
                
                # Update status from real system
                if hasattr(self.kaygee, 'trace_vault'):
                    self.status["interactions"] = len(self.kaygee.trace_vault.entries)
                if hasattr(self.kaygee, 'merkle_vault'):
                    root = self.kaygee.merkle_vault.get_current_root()
                    self.status["root"] = root[:16] + "..."
                
                return response_text
            except Exception as e:
                print(f"⚠️  KayGee processing error: {e}")
                return f"I heard you say '{user_text}', but I encountered an issue processing it."
        else:
            # Mock response
            responses = [
                f"You said: '{user_text}'. I heard you clearly.",
                f"Interesting perspective on '{user_text}'. Let me consider that.",
                f"I understand you're telling me about '{user_text}'. Tell me more.",
                f"That's a thoughtful statement: '{user_text}'. What brings that up?"
            ]
            return random.choice(responses)

    def make_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="voice", size=8)
        )
        layout["body"].split_row(
            Layout(name="metrics"),
            Layout(name="quote")
        )
        return layout

    def update(self, layout):
        status = self.status if not self.kaygee else self.get_real_status()

        # Header
        system_status = "VOICE ACTIVE" if HAS_TTS and HAS_STT else "VOICE PARTIAL"
        header = Text(f"KAYGEE_1.0 — {system_status}", style="bold cyan")
        layout["header"].update(Panel(header, border_style="bright_blue"))

        # Metrics
        table = Table(title="Live System")
        table.add_column("Metric")
        table.add_column("Value", style="green")
        table.add_row("Session", status["session"])
        table.add_row("Interactions", str(status["interactions"]))
        table.add_row("Merkle Root", status["root"][:16] + "...")
        table.add_row("Confidence", f"{status['confidence']:.2f}")
        table.add_row("Philosopher", status["philosopher"])
        table.add_row("Stability", f"{status['stability']:.2f}")
        table.add_row("Drift", "❌ NO" if not status["drift"] else "🔥 YES")
        layout["metrics"].update(Panel(table, border_style="blue"))

        # Quote
        quote = random.choice(quotes)
        layout["quote"].update(Panel(quote, title="A Priori Wisdom", border_style="magenta"))

        # Voice Panel
        voice_panel = Table.grid(padding=1)
        voice_panel.add_row("[bold green]Last heard:[/] ", self.last_heard)
        voice_panel.add_row("[bold cyan]Last spoken:[/] ", self.last_spoken)
        voice_panel.add_row("")
        
        if HAS_STT:
            voice_panel.add_row("[yellow]🎤 Speak now — KayGee is listening...[/]")
        else:
            voice_panel.add_row("[red]⚠️  Voice input disabled (install faster-whisper)[/]")
        
        if not HAS_TTS:
            voice_panel.add_row("[red]⚠️  Voice output disabled (install TTS)[/]")
            
        layout["voice"].update(Panel(voice_panel, title="Voice Interface", border_style="bright_white"))

    def get_real_status(self):
        """Get status from real KayGee system"""
        try:
            return {
                "session": self.kaygee.session_id if hasattr(self.kaygee, 'session_id') else "unknown",
                "interactions": self.kaygee.interaction_count if hasattr(self.kaygee, 'interaction_count') else 0,
                "root": self.kaygee.merkle_vault.get_current_root()[:16] + "..." if hasattr(self.kaygee, 'merkle_vault') else "pending",
                "drift": False,
                "confidence": 0.85,
                "philosopher": "Kant",
                "stability": 0.94
            }
        except:
            return self.status

def run_voice_dashboard():
    if not HAS_TTS and not HAS_STT:
        print("⚠️  Install TTS and faster-whisper for full voice functionality:")
        print("    pip install TTS faster-whisper pygame sounddevice numpy")
        print("\nRunning in text-only mode...")

    dashboard = VoiceDashboard()
    layout = dashboard.make_layout()

    # Start listening thread
    if HAS_STT:
        listener = threading.Thread(target=listen_loop, daemon=True)
        listener.start()
        time.sleep(1)  # Let listener initialize

    # Initial greeting
    greeting = "I am KayGee 1.0. I can hear you now. Speak, and I will respond."
    if not HAS_STT:
        greeting = "I am KayGee 1.0. Voice input is disabled, but I'm ready to process text."
    
    dashboard.speak(greeting)

    try:
        with Live(layout, refresh_per_second=1, screen=True):
            while True:
                dashboard.update(layout)

                # Check for voice input
                try:
                    user_text = voice_queue.get_nowait()
                    dashboard.last_heard = user_text
                    
                    # Process through real KayGee system
                    response_text = dashboard.process_user_input(user_text)
                    dashboard.speak(response_text)
                    
                except queue.Empty:
                    pass

                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n\n👋 KayGee shutting down gracefully...")
        dashboard.speak("Goodbye. I'll be here when you return.")

if __name__ == "__main__":
    run_voice_dashboard()
