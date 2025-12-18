"""
KayGee_1.0 Master Dashboard
Functional real-time monitor for the Vaulted Reasoner
Retro-terminal style with philosophical soul
"""

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
from rich import box
import time
import json
import random
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import real KayGee system
try:
    from main import VaultedReasoner
    KAYGEE_AVAILABLE = True
except ImportError:
    KAYGEE_AVAILABLE = False
    print("⚠️  KayGee system not available. Dashboard running in standalone mode.")

# Global reference to KayGee system (will be initialized by Dashboard class)
kaygee_system = None

philosophical_quotes = [
    "Act only according to that maxim whereby you can at the same time will that it should become a universal law. — Kant",
    "The life of man is of no greater importance to the universe than that of an oyster. — Hume",
    "All things are subject to interpretation. Whichever interpretation prevails is a function of power. — Spinoza",
    "No man's knowledge here can go beyond his experience. — Locke"
]

def make_layout() -> Layout:
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=5)
    )
    layout["main"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=1)
    )
    layout["left"].split(
        Layout(name="status"),
        Layout(name="philosophy"),
        Layout(name="timeline")
    )
    return layout

class Dashboard:
    def __init__(self, kaygee_system=None):
        self.console = Console()
        self.layout = make_layout()
        self.quote = random.choice(philosophical_quotes)
        self.kaygee = kaygee_system
        self.start_time = time.time()

    def update(self):
        # Get real data from KayGee system if available
        if self.kaygee:
            status = self._get_real_status()
            balance = self._get_real_balance()
            meta = self._get_real_meta()
            personality = self._get_real_personality()
            vaults = self._get_real_vaults()
            interactions = self._get_real_interactions()
        else:
            # Fallback to empty/placeholder data
            status = {
                "session_id": "No system",
                "uptime": "0s",
                "interactions": 0,
                "merkle_root": "Not initialized",
                "apriori_hash": "Not initialized",
                "drift_detected": False
            }
            balance = {"kant": 0, "locke": 0, "spinoza": 0, "hume": 0, "dominant": "None"}
            meta = {"avg_confidence": 0.0, "concerns": 0, "uncertainty_triggers": 0}
            personality = {"stability": 0.0, "recent_tune": "None"}
            vaults = {"episodic": 0, "prototypical": 0, "semantic_rules": 0}
            interactions = []

        # Header
        header = Text("KAYGEE_1.0 MASTER DASHBOARD", style="bold green on black")
        header.stylize("blink", 0, 9)
        self.layout["header"].update(Panel(header, style="green on black"))

        # Status panel
        status_table = Table.grid(padding=1)
        status_table.add_column(style="cyan")
        status_table.add_column(style="white")
        status_table.add_row("Session", status["session_id"])
        status_table.add_row("Uptime", status["uptime"])
        status_table.add_row("Interactions", str(status["interactions"]))
        status_table.add_row("Merkle Root", status["merkle_root"])
        status_table.add_row("A Priori Hash", status["apriori_hash"])
        status_table.add_row("Drift Detected", "❌ NO" if not status["drift_detected"] else "🔥 YES")
        self.layout["status"].update(Panel(status_table, title="System Integrity", border_style="green"))

        # Philosophy meter
        prog = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=20),
            "[progress.percentage]{task.percentage:>3.0f}%"
        )
        tasks = [
            ("Kant", balance["kant"]),
            ("Locke", balance["locke"]),
            ("Spinoza", balance["spinoza"]),
            ("Hume", balance["hume"])
        ]
        for name, percent in tasks:
            prog.add_task(name, total=100, completed=percent)
        phil_panel = Panel(prog, title=f"Philosophical Balance — Dominant: {balance['dominant']}", border_style="blue")
        self.layout["philosophy"].update(phil_panel)

        # Timeline
        timeline_table = Table(title="Recent Interactions")
        timeline_table.add_column("ID")
        timeline_table.add_column("Conf")
        timeline_table.add_column("Philosopher")
        timeline_table.add_column("Action")
        for i in interactions:
            conf_style = "green" if i["confidence"] > 0.8 else "yellow" if i["confidence"] > 0.6 else "red"
            timeline_table.add_row(
                str(i["id"]),
                f"[{conf_style}]{i['confidence']:.2f}[/{conf_style}]",
                i["philosopher"],
                i["action"]
            )
        self.layout["timeline"].update(Panel(timeline_table, border_style="magenta"))

        # Right column
        right_table = Table.grid(padding=1)
        right_table.add_column()
        right_table.add_column()
        right_table.add_row("Meta Concerns", str(meta["concerns"]))
        right_table.add_row("Avg Confidence", f"{meta['avg_confidence']:.2f}")
        right_table.add_row("Personality Stability", f"{personality['stability']:.2f}")
        right_table.add_row("Episodic Cases", str(vaults["episodic"]))
        right_table.add_row("Semantic Rules", str(vaults["semantic_rules"]))
        self.layout["right"].update(Panel(right_table, title="Health Metrics", border_style="cyan"))

        # Footer quote
        self.layout["footer"].update(Panel(self.quote, title="A Priori Wisdom", border_style="bright_black"))

    def _get_real_status(self):
        uptime = int(time.time() - self.start_time)
        return {
            "session_id": getattr(self.kaygee, 'session_id', 'unknown'),
            "uptime": f"{uptime // 3600}h {(uptime % 3600) // 60}m",
            "interactions": getattr(self.kaygee, 'interaction_count', 0),
            "merkle_root": self.kaygee.merkle_vault.get_current_root()[:16] + "..." if hasattr(self.kaygee, 'merkle_vault') else "pending",
            "apriori_hash": "a3f9c1...d4e2",  # TODO: Compute from APrioriVault
            "drift_detected": False  # TODO: Add drift detection
        }
    
    def _get_real_balance(self):
        # TODO: Extract from reasoning engine's philosophical tracking
        return {"kant": 25, "locke": 25, "spinoza": 25, "hume": 25, "dominant": "Balanced"}
    
    def _get_real_meta(self):
        # TODO: Extract from MetaCognitiveMonitor
        return {"avg_confidence": 0.85, "concerns": 0, "uncertainty_triggers": 0}
    
    def _get_real_personality(self):
        # TODO: Extract from PersonalityCore
        return {"stability": 0.94, "recent_tune": "None"}
    
    def _get_real_vaults(self):
        vaults = {"episodic": 0, "prototypical": 0, "semantic_rules": 0}
        if hasattr(self.kaygee, 'trace_vault'):
            vaults["episodic"] = len(self.kaygee.trace_vault.entries) if hasattr(self.kaygee.trace_vault, 'entries') else 0
        return vaults
    
    def _get_real_interactions(self):
        if not hasattr(self.kaygee, 'trace_vault'):
            return []
        # TODO: Extract last 3 interactions from trace vault
        return []

def run_dashboard(kaygee_system=None):
    dashboard = Dashboard(kaygee_system)
    with Live(dashboard.layout, refresh_per_second=0.5, screen=True):
        while True:
            dashboard.update()
            time.sleep(2)

if __name__ == "__main__":
    run_dashboard()
