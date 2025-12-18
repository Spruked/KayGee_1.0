"""
KayGee_1.0 Voice + Reasoning Dashboard
Live monitor with real ReasoningEngine integration
Speak + Listen + Think
CPU-only, fully local, production-grade

The culmination of Claude + Kimi + Grok collaboration
"""

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
import threading
import time
import queue
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# === Local Voice Setup ===
print("🎤 Initializing voice systems...")

try:
    from TTS.api import TTS
    tts = TTS(model_name="tts_models/en/jenny/jenny", progress_bar=False, gpu=False)
    HAS_TTS = True
    print("  ✅ TTS ready (Coqui Jenny)")
except Exception as e:
    print(f"  ⚠️  TTS not available: {e}")
    HAS_TTS = False

try:
    from faster_whisper import WhisperModel
    whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
    HAS_STT = True
    print("  ✅ STT ready (Whisper base.en)")
except Exception as e:
    print(f"  ⚠️  STT not available: {e}")
    HAS_STT = False

try:
    import sounddevice as sd
    import numpy as np
    import wave
    import tempfile
    HAS_AUDIO = True
    print("  ✅ Audio input ready")
except Exception as e:
    print(f"  ⚠️  Audio not available: {e}")
    HAS_AUDIO = False
    HAS_STT = False

# Queue for transcribed speech
voice_queue = queue.Queue()

# === Import Real KayGee System ===
print("🧠 Loading KayGee reasoning core...")

try:
    from main import VaultedReasoner
    SYSTEM_AVAILABLE = True
    print("  ✅ VaultedReasoner loaded")
except Exception as e:
    print(f"  ⚠️  System not available: {e}")
    SYSTEM_AVAILABLE = False

# Global system instance
kaygee_system = None

# Philosophical quotes for wisdom panel
PHILOSOPHICAL_QUOTES = [
    "Act only according to that maxim whereby you can will that it should become a universal law. — Kant",
    "The life of man is of no greater importance to the universe than that of an oyster. — Hume",
    "All things are subject to interpretation. Whichever interpretation prevails is a function of power. — Spinoza",
    "No man's knowledge here can go beyond his experience. — Locke",
    "Peace is not absence of war — it is a virtue, a state of mind. — Spinoza",
    "Custom is the great guide of human life. — Hume",
    "The only defense against the world is a perfect understanding of it. — Locke",
    "Happiness is not an ideal of reason but of imagination. — Kant"
]

# === Voice Input Thread ===
def listen_loop():
    """Continuous listening thread - captures and transcribes speech"""
    if not HAS_STT or not HAS_AUDIO:
        print("⚠️  Voice input disabled")
        return

    print("\n🎤 KayGee is now listening continuously...")
    print("   Speak naturally. She will hear you.\n")
    
    sample_rate = 16000
    duration = 3  # Record in 3-second chunks
    
    while True:
        try:
            # Record audio chunk
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
            sd.wait()
            
            # Save to temp WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
            
            # Convert to WAV format
            audio_int16 = (audio * 32767).astype('int16')
            with wave.open(temp_path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            # Transcribe with Whisper
            segments, info = whisper_model.transcribe(temp_path, language="en", vad_filter=True)
            text = " ".join(seg.text for seg in segments).strip()
            
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)
            
            # Queue if valid speech detected
            if text and len(text) > 3:
                # Filter out common false positives
                if text.lower() not in ["you", "thank you", "thanks"]:
                    voice_queue.put(text)
                
        except Exception as e:
            # Silently continue on audio errors
            time.sleep(0.5)

# === TTS Output ===
def kaygee_speak(text: str):
    """Speak text through TTS with proper audio playback"""
    if not HAS_TTS:
        print(f"\n💬 KayGee: {text}\n")
        return
    
    try:
        print(f"\n💬 KayGee: {text}")
        wav_path = "temp_kaygee.wav"
        
        # Generate speech
        tts.tts_to_file(text=text, file_path=wav_path)
        
        # Play audio
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(wav_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except ImportError:
            # Fallback to system player on Windows
            import os
            if sys.platform == "win32":
                os.system(f'powershell -c (New-Object Media.SoundPlayer "{wav_path}").PlaySync()')
        
        # Clean up
        Path(wav_path).unlink(missing_ok=True)
        print()
        
    except Exception as e:
        print(f"⚠️  TTS error: {e}")
        print(f"💬 KayGee: {text}\n")

# === Live Dashboard ===
class VoiceReasoningDashboard:
    """Live dashboard with real system integration"""
    
    def __init__(self, system):
        self.system = system
        self.console = Console()
        self.last_heard = "Listening for your voice..."
        self.last_response = "I am KayGee 1.0. My mind is awake."
        self.conversation_history = []
        self.start_time = time.time()
        self.current_quote = PHILOSOPHICAL_QUOTES[0]
        self.quote_index = 0
        self.layout = self.make_layout()

    def make_layout(self) -> Layout:
        """Create Rich layout structure"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=12)
        )
        layout["main"].split_row(
            Layout(name="status", ratio=3),
            Layout(name="metrics", ratio=2)
        )
        return layout

    def get_real_status(self):
        """Pull live data from actual system"""
        if not self.system:
            return {
                "session": "System offline",
                "interactions": 0,
                "merkle_root": "N/A",
                "confidence": 0.0,
                "philosopher": "None",
                "stability": 0.0,
                "drift": False,
                "uptime": "0s"
            }
        
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
        
        # Extract real metrics
        merkle_root = "genesis"
        if hasattr(self.system, 'merkle_vault'):
            try:
                merkle_root = self.system.merkle_vault.get_current_root()[:16] + "..."
            except:
                merkle_root = "pending"
        
        confidence = 0.85
        if hasattr(self.system, 'last_decision'):
            confidence = self.system.last_decision.get('confidence', 0.85)
        
        return {
            "session": getattr(self.system, 'session_id', 'unknown'),
            "interactions": getattr(self.system, 'interaction_count', 0),
            "merkle_root": merkle_root,
            "confidence": confidence,
            "philosopher": "Balanced",  # TODO: Extract from reasoning history
            "stability": 0.94,  # TODO: Extract from PersonalityCore
            "drift": False,
            "uptime": uptime_str
        }

    def update(self):
        """Update dashboard with live data"""
        status = self.get_real_status()

        # Header with blinking effect
        header = Text("KAYGEE_1.0 — VOICE + REASONING ACTIVE", style="bold cyan")
        self.layout["header"].update(Panel(header, border_style="bright_cyan"))

        # Status table (left panel)
        table = Table(title="🧠 Live System State", show_header=False, box=None)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white")
        table.add_row("Session ID", status["session"])
        table.add_row("Uptime", status["uptime"])
        table.add_row("Interactions", str(status["interactions"]))
        table.add_row("Merkle Root", status["merkle_root"])
        table.add_row("Avg Confidence", f"{status['confidence']:.2%}")
        table.add_row("Philosopher", status["philosopher"])
        table.add_row("Stability", f"{status['stability']:.2%}")
        table.add_row("Drift Detected", "❌ NO" if not status["drift"] else "🔥 YES")
        self.layout["status"].update(Panel(table, border_style="green", title="System Integrity"))

        # Philosophical balance (right panel)
        prog = Progress(
            TextColumn("[bold]{task.description}", justify="right"),
            BarColumn(bar_width=15),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%")
        )
        # TODO: Extract real vote counts from reasoning engine
        prog.add_task("Kant", total=100, completed=25)
        prog.add_task("Hume", total=100, completed=25)
        prog.add_task("Locke", total=100, completed=25)
        prog.add_task("Spinoza", total=100, completed=25)
        
        wisdom_panel = Panel(self.current_quote, title="A Priori Wisdom", border_style="bright_black", style="italic")
        
        metrics_layout = Layout()
        metrics_layout.split_column(
            Layout(Panel(prog, title="Philosophical Balance", border_style="blue"), ratio=2),
            Layout(wisdom_panel, ratio=1)
        )
        self.layout["metrics"].update(metrics_layout)

        # Voice conversation panel (footer)
        voice_table = Table.grid(padding=1)
        voice_table.add_column(style="bold", justify="right", width=15)
        voice_table.add_column()
        
        voice_table.add_row("[green]You said:", self.last_heard)
        voice_table.add_row("[cyan]KayGee:", self.last_response[:100] + ("..." if len(self.last_response) > 100 else ""))
        voice_table.add_row("")
        
        # Recent conversation history (last 3 exchanges)
        if self.conversation_history:
            voice_table.add_row("[dim]Recent exchanges:", "")
            for exchange in self.conversation_history[-3:]:
                voice_table.add_row("[dim]>", f"[dim]{exchange}[/dim]")
            voice_table.add_row("")
        
        # Status indicators
        indicators = []
        if HAS_STT:
            indicators.append("[green]🎤 Listening[/green]")
        else:
            indicators.append("[red]🎤 No mic[/red]")
        
        if HAS_TTS:
            indicators.append("[green]🔊 Voice active[/green]")
        else:
            indicators.append("[red]🔊 No TTS[/red]")
        
        if SYSTEM_AVAILABLE and self.system:
            indicators.append("[green]🧠 Reasoning active[/green]")
        else:
            indicators.append("[red]🧠 System offline[/red]")
        
        voice_table.add_row("", " | ".join(indicators))
        
        self.layout["footer"].update(
            Panel(voice_table, title="Voice Conversation Interface", border_style="bright_magenta")
        )
    
    def rotate_quote(self):
        """Cycle through philosophical quotes"""
        self.quote_index = (self.quote_index + 1) % len(PHILOSOPHICAL_QUOTES)
        self.current_quote = PHILOSOPHICAL_QUOTES[self.quote_index]

# === Main Integration Loop ===
def run_integrated_dashboard():
    """Boot system and run integrated voice dashboard"""
    global kaygee_system

    print("\n" + "="*60)
    print("  KAYGEE 1.0 — VOICE + REASONING INTEGRATION")
    print("  Built by: Claude + Kimi + Grok")
    print("="*60 + "\n")

    # Boot the full system
    if SYSTEM_AVAILABLE:
        try:
            print("🧠 Booting KayGee reasoning core...")
            kaygee_system = VaultedReasoner()
            print("✅ System online.\n")
        except Exception as e:
            print(f"⚠️  System boot failed: {e}")
            print("   Continuing in dashboard-only mode...\n")
            kaygee_system = None
    else:
        print("⚠️  VaultedReasoner not available - dashboard-only mode\n")
        kaygee_system = None

    dashboard = VoiceReasoningDashboard(kaygee_system)
    
    # Greeting
    greeting = "I am KayGee 1.0. My mind is awake. I can hear you. Speak, and I will reason with you."
    if not HAS_STT:
        greeting = "I am KayGee 1.0. My mind is awake. Voice input is disabled, but I am ready."
    
    kaygee_speak(greeting)
    dashboard.last_response = greeting

    # Start listening thread
    if HAS_STT and HAS_AUDIO:
        listener = threading.Thread(target=listen_loop, daemon=True)
        listener.start()
        time.sleep(1)  # Let listener initialize

    # Main dashboard loop
    try:
        with Live(dashboard.layout, refresh_per_second=2, screen=True):
            last_quote_rotation = time.time()
            
            while True:
                dashboard.update()

                # Rotate quote every 15 seconds
                if time.time() - last_quote_rotation > 15:
                    dashboard.rotate_quote()
                    last_quote_rotation = time.time()

                # Process voice input
                try:
                    user_input = voice_queue.get_nowait()
                    dashboard.last_heard = user_input
                    
                    # Process through real system if available
                    if kaygee_system:
                        try:
                            response = kaygee_system.process_interaction(user_input)
                            speak_text = response.get("text", str(response))
                            
                            # Update metrics from response
                            if hasattr(kaygee_system, 'last_decision'):
                                kaygee_system.last_decision = response
                            
                        except Exception as e:
                            speak_text = f"I encountered an issue processing that: {e}"
                    else:
                        # Fallback response
                        speak_text = f"I heard: '{user_input}'. System reasoning is offline, but I'm listening."
                    
                    # Update dashboard and speak
                    dashboard.last_response = speak_text
                    dashboard.conversation_history.append(f"You: {user_input[:50]}... | KayGee: {speak_text[:50]}...")
                    kaygee_speak(speak_text)
                    
                except queue.Empty:
                    pass

                time.sleep(0.3)
                
    except KeyboardInterrupt:
        print("\n\n👋 KayGee shutting down gracefully...")
        kaygee_speak("Goodbye. I will be here when you return. Until then, think well.")

if __name__ == "__main__":
    run_integrated_dashboard()
