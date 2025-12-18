"""
Generate development keys for handshake protocol
Run once: python scripts/setup_dev_keys.py
"""

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import json
from pathlib import Path


def generate_dev_keys():
    """Generate Ed25519 keypairs for each component"""
    keys = {}
    components = ["perception", "memory", "reasoning", "learning", "articulation"]
    
    for component in components:
        # Generate private key
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Serialize keys
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        keys[component] = {
            "private": private_bytes.hex(),
            "public": public_bytes.hex()
        }
    
    # Save to keys.json
    keys_path = Path("keys.json")
    with open(keys_path, "w") as f:
        json.dump(keys, f, indent=2)
    
    print(f"✓ Generated development keys: {keys_path}")
    print("⚠️  IMPORTANT: Add keys.json to .gitignore immediately!")
    print("⚠️  These are development-only keys. Use HSM for production.")
    
    return keys


if __name__ == "__main__":
    generate_dev_keys()
