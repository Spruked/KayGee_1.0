"""
Hot reload A Posteriori vault without system restart
Learning rules can be reloaded dynamically
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def hot_reload_posteriori():
    """Reload A Posteriori vault without restarting"""
    from memory.vault import APosterioriVault
    
    print("🔄 Hot-reloading A Posteriori vault...")
    
    vault = APosterioriVault()
    vault.connect()
    
    # Re-query all cases
    cases = vault.retrieve_cases([], k=1000)
    
    print(f"✅ Reloaded {len(cases)} cases from A Posteriori vault")
    print("System can continue without restart")
    
    return True


if __name__ == "__main__":
    hot_reload_posteriori()
