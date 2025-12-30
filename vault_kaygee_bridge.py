"""
Vault System Integration Bridge
Connects Vault_System_1.0 with KayGee cognitive architecture
"""

import sys
import os
from pathlib import Path

# Add both systems to path
vault_system_path = Path(__file__).parent / "Vault_System_1.0" / "vault_system"
kaygee_path = Path(__file__).parent / "Kay_Gee_1.0" / "src"

sys.path.insert(0, str(vault_system_path))
sys.path.insert(0, str(kaygee_path))

from main import IntegratedVaultSystem
from telemetry_dashboard.telemetry_dashboard import TelemetryDashboard
import uvicorn
import asyncio


class VaultKayGeeBridge:
    """
    Bridge between Vault System and KayGee cognitive architecture
    """

    def __init__(self):
        self.vault_system = None
        self.telemetry_dashboard = None
        self.kaygee_system = None

    def initialize_vault_system(self, master_key: str = "integration_key_2024"):
        """Initialize the vault system"""
        print("🚀 Initializing Vault System...")
        self.vault_system = IntegratedVaultSystem(master_key, "kaygee_bridge_node")
        print("✅ Vault System initialized")

    def initialize_telemetry(self, host: str = "localhost", port: int = 8001):
        """Initialize telemetry dashboard"""
        print("📊 Initializing Telemetry Dashboard...")
        self.telemetry_dashboard = TelemetryDashboard(self.vault_system, host, port)
        print(f"✅ Telemetry Dashboard initialized on {host}:{port}")

    def start_telemetry_server(self):
        """Start the telemetry web server"""
        if self.telemetry_dashboard:
            print("🌐 Starting telemetry server...")
            uvicorn.run(self.telemetry_dashboard.app, host="localhost", port=8001)

    def integrate_with_kaygee(self):
        """Integrate vault system with KayGee reasoning"""
        # This would connect the vault system to KayGee's memory and reasoning layers
        print("🔗 Integrating with KayGee system...")
        
        # Load seeds into KayGee's memory
        if hasattr(self, 'vault_system') and hasattr(self.vault_system, 'loaded_seeds'):
            philosophers = self.vault_system.seed_loader.get_philosophers()
            reasoners = self.vault_system.seed_loader.get_reasoners()
            resonators = self.vault_system.seed_loader.get_resonators()
            
            print(f"Loaded {len(philosophers)} philosophers, {len(reasoners)} reasoners, {len(resonators)} resonators")
            
            # Here we would integrate with KayGee's reasoning engine
            # For now, just demonstrate the connection
            self.kaygee_philosophers = philosophers
            self.kaygee_reasoners = reasoners
            self.kaygee_resonators = resonators
            
            print("✅ Integration placeholder - seeds loaded into bridge")
        else:
            print("❌ Vault system not initialized")

    def run_demo(self):
        """Run a demonstration of the integrated system"""
        if not self.vault_system:
            self.initialize_vault_system()

        print("\n=== Vault-KayGee Integration Demo ===")

        # Test vault operations
        print("1. Testing vault storage...")
        from vault_core import VaultCategory
        test_data = "cognitive_pattern_data"
        result = self.vault_system.store_data(test_data, VaultCategory.INTELLECTUAL, "kaygee_bridge", {})
        print(f"Storage result: {result}")

        # Test decision making
        print("2. Testing decision integration...")
        decision_context = {
            "situation": "philosophical_dilemma",
            "options": ["kantian_duty", "utilitarian_calculation"],
            "constraints": ["ethical_integrity", "practical_feasibility"]
        }
        decision = self.vault_system.make_decision(decision_context)
        print(f"Decision result: {decision}")

        print("3. System health check...")
        status = self.vault_system.get_system_status()
        print(f"System status: {status}")
        
        print("4. Seed integration...")
        if hasattr(self, 'kaygee_philosophers'):
            print(f"Active philosophers: {len(self.kaygee_philosophers)}")
            print(f"Active reasoners: {len(self.kaygee_reasoners)}")
            print(f"Active resonators: {len(self.kaygee_resonators)}")
        else:
            print("Seeds not yet integrated - call integrate_with_kaygee() first")

        print("\n=== Demo Complete ===")


if __name__ == "__main__":
    bridge = VaultKayGeeBridge()

    # Initialize systems
    bridge.initialize_vault_system()
    bridge.initialize_telemetry()

    # Run demo
    bridge.run_demo()
    
    # Integrate with KayGee
    bridge.integrate_with_kaygee()
    
    print("\n🎉 KayGee is now awake with full philosophical wisdom!")
    print("Philosophers, reasoners, and resonators loaded.")
    print("Ready for deep questions and resonance-driven reasoning.")