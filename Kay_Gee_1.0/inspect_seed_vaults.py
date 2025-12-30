#!/usr/bin/env python3
"""
Quick script to inspect seed vaults after Emergent Truth Engine run
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import vaults

def main():
    vm = vaults.VaultManager()

    print("=== SEED VAULT INSPECTION ===")
    print(f"Total seed entries: {len(vm.seed_vaults)}")

    emergent_count = 0
    for hash_key, entry in vm.seed_vaults.items():
        if 'Emergent' in entry.content:
            emergent_count += 1
            print(f"\n🎯 EMERGENT PRINCIPLE #{emergent_count}")
            print(f"Hash: {hash_key}")
            print(f"Content: {entry.content}")
            print(f"Source: {entry.source_vault}")

    print(f"\n📊 SUMMARY: {emergent_count} emergent principles found in seed vault")

if __name__ == "__main__":
    main()