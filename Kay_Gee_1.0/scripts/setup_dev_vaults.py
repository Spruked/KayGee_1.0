"""
Setup development vaults
Initialize all vaults for development
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def setup_vaults():
    """Initialize all vaults"""
    from memory.vault import APrioriVault, APosterioriVault, TraceVault
    
    print("🔧 Setting up development vaults...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize A Priori
    print("  - Initializing A Priori vault...")
    apriori = APrioriVault()
    apriori.connect()
    apriori._seed_meta_weights()
    
    # Initialize A Posteriori
    print("  - Initializing A Posteriori vault...")
    aposteriori = APosterioriVault()
    aposteriori.connect()
    
    # Initialize Trace
    print("  - Initializing Trace vault...")
    trace = TraceVault()
    trace.connect()
    
    print("✅ All vaults initialized successfully")


if __name__ == "__main__":
    setup_vaults()
