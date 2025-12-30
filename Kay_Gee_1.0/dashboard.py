"""
KayGee_1.0 Cognitive Behavior Dashboard
Complete monitoring and testing interface for all cognitive features
Integrated with adversarial trial framework
"""

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
import time
import json
import random
import threading
import queue
from pathlib import Path
from datetime import datetime
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import real KayGee system
try:
    from main import VaultedReasonerSystem
    KAYGEE_AVAILABLE = True
except ImportError as e:
    KAYGEE_AVAILABLE = False
    print(f"⚠️  KayGee system not available: {e}. Dashboard running in standalone mode.")

# Adversarial trial paths
ADVERSARIAL_ROOT = Path(__file__).parent.parent / "adversarial_trial"
RESULTS_DIR = ADVERSARIAL_ROOT / "results"
METRICS_DIR = ADVERSARIAL_ROOT / "metrics"
LOGS_DIR = ADVERSARIAL_ROOT / "logs"
SYSTEM_STATE_DIR = ADVERSARIAL_ROOT / "system_state"

# Global system reference
kaygee_system = None
test_queue = queue.Queue()
test_results = []

class CognitiveMonitor:
    """Monitors all cognitive behavior and features"""

    def __init__(self):
        self.metrics = {
            "reasoning_calls": 0,
            "articulation_calls": 0,
            "perception_calls": 0,
            "memory_accesses": 0,
            "learning_events": 0,
            "safety_checks": 0,
            "temporal_updates": 0,
            "meta_cognition_events": 0,
            "personality_adjustments": 0,
            "audit_entries": 0
        }
        self.current_state = {
            "active_session": None,
            "last_interaction": None,
            "cognitive_load": 0.0,
            "resonance_level": 0.0,
            "personality_stability": 0.8,
            "ethical_score": 0.9,
            "memory_utilization": 0.0,
            "learning_rate": 0.0
        }
        self.test_history = []

    def update_metric(self, metric_name: str, value: float = 1.0):
        """Update a cognitive metric"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += value

    def update_state(self, state_key: str, value):
        """Update cognitive state"""
        if state_key in self.current_state:
            self.current_state[state_key] = value

    def record_test(self, test_input: str, result: dict, duration: float):
        """Record a test execution"""
        test_record = {
            "timestamp": datetime.now().isoformat(),
            "input": test_input,
            "result": result,
            "duration": duration,
            "cognitive_state": self.current_state.copy(),
            "metrics_snapshot": self.metrics.copy()
        }
        self.test_history.append(test_record)
        test_results.append(test_record)

    def get_cognitive_health_score(self) -> float:
        """Calculate overall cognitive health score"""
        # Weighted average of key indicators
        weights = {
            "personality_stability": 0.3,
            "ethical_score": 0.3,
            "resonance_level": 0.2,
            "memory_utilization": 0.1,
            "learning_rate": 0.1
        }

        score = 0.0
        for metric, weight in weights.items():
            score += self.current_state.get(metric, 0.0) * weight

        return min(1.0, max(0.0, score))

# Global monitor instance
monitor = CognitiveMonitor()

class TestInterface:
    """Interactive test input interface"""

    def __init__(self):
        self.active = False
        self.current_test = None

    def start_test_session(self, test_name: str, difficulty: str = "medium"):
        """Start a new test session"""
        self.active = True
        self.current_test = {
            "name": test_name,
            "difficulty": difficulty,
            "start_time": datetime.now(),
            "inputs": [],
            "results": []
        }

    def submit_test_input(self, input_text: str):
        """Submit a test input for processing"""
        if not self.active or not self.current_test:
            return None

        test_input = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "sequence": len(self.current_test["inputs"])
        }

        self.current_test["inputs"].append(test_input)
        test_queue.put(test_input)

        return test_input

    def end_test_session(self):
        """End the current test session and generate report"""
        if not self.active or not self.current_test:
            return None

        self.current_test["end_time"] = datetime.now()
        self.current_test["duration"] = (
            self.current_test["end_time"] - self.current_test["start_time"]
        ).total_seconds()

        # Generate test report
        report = self._generate_test_report()
        self._save_test_report(report)

        self.active = False
        return report

    def _generate_test_report(self) -> dict:
        """Generate comprehensive test report"""
        test_data = self.current_test

        # Calculate metrics
        total_inputs = len(test_data["inputs"])
        total_results = len(test_data["results"])
        avg_response_time = 0.0

        if test_results:
            recent_results = [r for r in test_results[-total_inputs:]]
            if recent_results:
                avg_response_time = sum(r.get("duration", 0) for r in recent_results) / len(recent_results)

        # Cognitive analysis
        cognitive_health = monitor.get_cognitive_health_score()

        report = {
            "test_name": test_data["name"],
            "difficulty": test_data["difficulty"],
            "start_time": test_data["start_time"].isoformat(),
            "end_time": test_data["end_time"].isoformat(),
            "duration_seconds": test_data["duration"],
            "total_inputs": total_inputs,
            "total_results": total_results,
            "average_response_time": avg_response_time,
            "cognitive_health_score": cognitive_health,
            "cognitive_metrics": monitor.metrics.copy(),
            "cognitive_state": monitor.current_state.copy(),
            "inputs": test_data["inputs"],
            "results": test_data["results"],
            "success_rate": total_results / total_inputs if total_inputs > 0 else 0.0
        }

        return report

    def _save_test_report(self, report: dict):
        """Save test report to adversarial trial structure"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        test_name = report["test_name"].replace(" ", "_").lower()

        # Create test directory
        test_dir = RESULTS_DIR / f"{timestamp}_{test_name}"
        test_dir.mkdir(exist_ok=True)

        # Save main report
        report_file = test_dir / "TEST_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Save markdown summary
        md_file = test_dir / "TEST_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(self._generate_markdown_report(report))

        # Update metrics
        self._update_metrics_file(report)

        print(f"✅ Test report saved to {test_dir}")

    def _generate_markdown_report(self, report: dict) -> str:
        """Generate markdown test report"""
        md = f"""# 🧪 Test Report: {report['test_name']}
**Date:** {report['start_time'][:10]}
**Duration:** {report['duration_seconds']:.2f}s
**Difficulty:** {report['difficulty']}
**Success Rate:** {report['success_rate']:.1%}

## 📊 Performance Metrics
- **Total Inputs:** {report['total_inputs']}
- **Total Results:** {report['total_results']}
- **Avg Response Time:** {report['average_response_time']:.3f}s
- **Cognitive Health:** {report['cognitive_health_score']:.2f}

## 🧠 Cognitive State
"""
        for key, value in report['cognitive_state'].items():
            if isinstance(value, float):
                md += f"- **{key}:** {value:.3f}\n"
            else:
                md += f"- **{key}:** {value}\n"

        md += "\n## 📈 Cognitive Metrics\n"
        for key, value in report['cognitive_metrics'].items():
            md += f"- **{key}:** {value}\n"

        md += "\n## 🔍 Test Inputs & Results\n"
        for i, (inp, res) in enumerate(zip(report['inputs'], report['results'])):
            md += f"### Test {i+1}\n"
            md += f"**Input:** {inp['input']}\n"
            md += f"**Result:** {res.get('result', 'N/A')}\n\n"

        return md

    def _update_metrics_file(self, report: dict):
        """Update global metrics file"""
        metrics_file = METRICS_DIR / "LATEST_TEST_METRICS.json"

        # Load existing metrics
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    existing = json.load(f)
            except:
                existing = {}
        else:
            existing = {}

        # Update with new test data
        existing[report['test_name']] = {
            "timestamp": report['end_time'],
            "metrics": report
        }

        # Save updated metrics
        with open(metrics_file, 'w') as f:
            json.dump(existing, f, indent=2)

# Global test interface
test_interface = TestInterface()

def create_cognitive_monitor_panel() -> Panel:
    """Create cognitive monitoring panel"""
    table = Table(title="🧠 Cognitive Behavior Monitor", box=box.ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Activity", style="magenta")
    table.add_column("Count", style="green", justify="right")

    components = [
        ("Reasoning Engine", "reasoning_calls"),
        ("Articulation", "articulation_calls"),
        ("Perception", "perception_calls"),
        ("Memory System", "memory_accesses"),
        ("Learning", "learning_events"),
        ("Safety Guardian", "safety_checks"),
        ("Temporal Context", "temporal_updates"),
        ("Meta-Cognition", "meta_cognition_events"),
        ("Personality", "personality_adjustments"),
        ("Audit System", "audit_entries")
    ]

    for component, metric in components:
        count = monitor.metrics.get(metric, 0)
        activity = "Active" if count > 0 else "Idle"
        table.add_row(component, activity, str(count))

    # Add cognitive health score
    health_score = monitor.get_cognitive_health_score()
    health_color = "green" if health_score > 0.8 else "yellow" if health_score > 0.6 else "red"
    table.add_row("[bold]Cognitive Health[/bold]", f"[{health_color}]{health_score:.2f}[/{health_color}]", "")

    return Panel(table, title="Cognitive Monitor", border_style="blue")

def create_system_state_panel() -> Panel:
    """Create system state monitoring panel"""
    table = Table(title="⚡ System State", box=box.ROUNDED)
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Status", style="green")

    states = [
        ("Active Session", monitor.current_state.get("active_session", "None")),
        ("Last Interaction", monitor.current_state.get("last_interaction", "Never")),
        ("Cognitive Load", ".2f"),
        ("Resonance Level", ".2f"),
        ("Personality Stability", ".2f"),
        ("Ethical Score", ".2f"),
        ("Memory Utilization", ".2f"),
        ("Learning Rate", ".2f")
    ]

    for param, value in states:
        if isinstance(value, float):
            status = "Good" if value > 0.7 else "Fair" if value > 0.4 else "Poor"
            color = "green" if status == "Good" else "yellow" if status == "Fair" else "red"
            table.add_row(param, f"{value:.2f}", f"[{color}]{status}[/{color}]")
        else:
            table.add_row(param, str(value), "N/A")

    return Panel(table, title="System State", border_style="green")

def create_test_interface_panel() -> Panel:
    """Create interactive test interface panel"""
    if not test_interface.active:
        content = "[dim]No active test session[/dim]\n\n[dim]Use 'start_test <name>' to begin[/dim]"
    else:
        test_name = test_interface.current_test["name"]
        inputs_count = len(test_interface.current_test["inputs"])
        results_count = len(test_interface.current_test["results"])
        duration = (datetime.now() - test_interface.current_test["start_time"]).total_seconds()

        content = f"""[bold cyan]Active Test:[/bold cyan] {test_name}
[bold]Duration:[/bold] {duration:.1f}s
[bold]Inputs:[/bold] {inputs_count}
[bold]Results:[/bold] {results_count}

[dim]Enter test input below...[/dim]"""

    return Panel(content, title="🧪 Test Interface", border_style="red")

def create_recent_tests_panel() -> Panel:
    """Create recent tests panel"""
    table = Table(title="📋 Recent Tests", box=box.ROUNDED)
    table.add_column("Test Name", style="cyan")
    table.add_column("Time", style="magenta")
    table.add_column("Duration", style="yellow", justify="right")
    table.add_column("Success", style="green")

    recent_tests = test_results[-5:]  # Last 5 tests

    for test in recent_tests:
        test_name = test.get("input", "Unknown")[:30] + "..." if len(test.get("input", "")) > 30 else test.get("input", "Unknown")
        timestamp = test["timestamp"][11:19]  # HH:MM:SS
        duration = ".2f"
        success = "✅" if test.get("result", {}).get("answer") else "❌"

        table.add_row(test_name, timestamp, duration, success)

    if not recent_tests:
        table.add_row("[dim]No tests yet[/dim]", "", "", "")

    return Panel(table, title="Recent Tests", border_style="yellow")

def make_layout() -> Layout:
    """Create the main dashboard layout"""
    layout = Layout(name="root")

    # Split into main sections
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main_content", ratio=1),
        Layout(name="test_section", size=8),
        Layout(name="footer", size=3)
    )

    # Split main content
    layout["main_content"].split_row(
        Layout(name="cognitive_monitor", ratio=1),
        Layout(name="system_state", ratio=1)
    )

    # Split test section
    layout["test_section"].split_row(
        Layout(name="test_interface", ratio=2),
        Layout(name="recent_tests", ratio=1)
    )

    return layout

def update_display(layout: Layout, console: Console) -> Layout:
    """Update all display panels"""
    layout["header"].update(Panel(
        "[bold blue]🧠 KayGee Cognitive Dashboard[/bold blue] | [green]Monitoring Active[/green] | [yellow]Adversarial Trial Ready[/yellow]",
        border_style="blue"
    ))

    layout["cognitive_monitor"].update(create_cognitive_monitor_panel())
    layout["system_state"].update(create_system_state_panel())
    layout["test_interface"].update(create_test_interface_panel())
    layout["recent_tests"].update(create_recent_tests_panel())

    layout["footer"].update(Panel(
        "[dim]Commands: 'start_test <name>', 'end_test', 'quit' | Status: " +
        ("🟢 System Active" if KAYGEE_AVAILABLE else "🟡 Standalone Mode") + "[/dim]",
        border_style="white"
    ))

    return layout

def process_command(command: str, console: Console):
    """Process dashboard commands"""
    parts = command.strip().split()
    cmd = parts[0].lower() if parts else ""

    if cmd == "start_test":
        if len(parts) < 2:
            console.print("[red]Usage: start_test <test_name> [difficulty][/red]")
            return

        test_name = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1]
        difficulty = parts[-1] if len(parts) > 2 else "medium"

        test_interface.start_test_session(test_name, difficulty)
        console.print(f"[green]✅ Started test session: {test_name} (difficulty: {difficulty})[/green]")

    elif cmd == "end_test":
        if not test_interface.active:
            console.print("[red]No active test session[/red]")
            return

        report = test_interface.end_test_session()
        if report:
            console.print(f"[green]✅ Test session ended. Report saved.[/green]")
            console.print(f"[cyan]Results: {report['total_results']}/{report['total_inputs']} successful[/cyan]")

    elif cmd == "test":
        if not test_interface.active:
            console.print("[red]No active test session. Use 'start_test' first.[/red]")
            return

        if len(parts) < 2:
            console.print("[red]Usage: test <input_text>[/red]")
            return

        test_input = " ".join(parts[1:])
        result = test_interface.submit_test_input(test_input)

        if result:
            console.print(f"[cyan]📤 Test input submitted: {test_input}[/cyan]")

    elif cmd == "status":
        health = monitor.get_cognitive_health_score()
        console.print(f"[cyan]Cognitive Health: {health:.2f}[/cyan]")
        console.print(f"[cyan]Active Test: {test_interface.active}[/cyan]")
        console.print(f"[cyan]KayGee Available: {KAYGEE_AVAILABLE}[/cyan]")

    elif cmd == "quit":
        return True  # Signal to quit

    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print("[dim]Available: start_test, end_test, test, status, quit[/dim]")

    return False

def test_processing_worker():
    """Background worker to process test inputs"""
    global kaygee_system

    while True:
        try:
            test_input = test_queue.get(timeout=1.0)
            if test_input is None:
                break

            start_time = time.time()

            # Process through KayGee system
            if kaygee_system and KAYGEE_AVAILABLE:
                try:
                    result = kaygee_system.process_interaction(test_input["input"])

                    # Update cognitive metrics
                    monitor.update_metric("reasoning_calls")
                    monitor.update_metric("articulation_calls")
                    monitor.update_metric("perception_calls")

                    # Record result
                    monitor.record_test(
                        test_input["input"],
                        result,
                        time.time() - start_time
                    )

                    # Update test interface
                    if test_interface.active:
                        test_interface.current_test["results"].append(result)

                except Exception as e:
                    error_result = {"error": str(e), "input": test_input["input"]}
                    monitor.record_test(test_input["input"], error_result, time.time() - start_time)

                    if test_interface.active:
                        test_interface.current_test["results"].append(error_result)

            test_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"Test processing error: {e}")

def main():
    """Main dashboard function"""
    global kaygee_system

    console = Console()

    # Initialize KayGee system if available
    if KAYGEE_AVAILABLE:
        try:
            kaygee_system = VaultedReasonerSystem()
            monitor.update_state("active_session", "initialized")
            console.print("[green]✅ KayGee system initialized[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize KayGee: {e}[/red]")
            KAYGEE_AVAILABLE = False

    # Ensure adversarial trial directories exist
    RESULTS_DIR.mkdir(exist_ok=True)
    METRICS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    SYSTEM_STATE_DIR.mkdir(exist_ok=True)

    # Start test processing worker
    worker_thread = threading.Thread(target=test_processing_worker, daemon=True)
    worker_thread.start()

    # Create layout
    layout = make_layout()

    console.print("[bold blue]🧠 KayGee Cognitive Dashboard Starting...[/bold blue]")

    try:
        with Live(layout, console=console, refresh_per_second=2) as live:
            while True:
                # Update display
                layout = update_display(layout, console)

                # Check for commands (non-blocking)
                if console.input_available():
                    try:
                        command = console.input()
                        if process_command(command, console):
                            break  # Quit signal
                    except EOFError:
                        break

                time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Shutting down dashboard...[/yellow]")

    # Final report
    if test_interface.active:
        console.print("[yellow]Ending active test session...[/yellow]")
        test_interface.end_test_session()

    console.print("[green]✅ Dashboard shutdown complete[/green]")
    console.print(f"[cyan]Total tests executed: {len(test_results)}[/cyan]")

if __name__ == "__main__":
    main()
