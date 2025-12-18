#!/usr/bin/env python3
"""
CPU-Only Verification Script
Ensures no GPU/CUDA packages are installed in the environment
"""
import subprocess
import sys

def check_cuda_packages():
    """Check for forbidden CUDA/GPU packages"""
    forbidden_patterns = [
        'cuda',
        'cudnn',
        'nvidia',
        'gpu',
        'cu118',
        'cu121',
        'tensorrt'
    ]
    
    result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
    installed = result.stdout.lower()
    
    violations = []
    for pattern in forbidden_patterns:
        if pattern in installed:
            violations.append(pattern)
    
    return violations

def check_torch_cpu():
    """Verify PyTorch is CPU-only"""
    try:
        import torch
        if torch.cuda.is_available():
            return False, "PyTorch has CUDA support - CPU-only required"
        if torch.version.cuda:
            return False, f"PyTorch built with CUDA {torch.version.cuda}"
        return True, "PyTorch is CPU-only ✓"
    except ImportError:
        return True, "PyTorch not installed"

def check_environment():
    """Check environment variables"""
    import os
    cuda_devices = os.environ.get('CUDA_VISIBLE_DEVICES', None)
    if cuda_devices != '':
        return False, f"CUDA_VISIBLE_DEVICES={cuda_devices} (should be '')"
    return True, "CUDA_VISIBLE_DEVICES='' ✓"

def main():
    print("🔍 Verifying CPU-Only Configuration...\n")
    
    all_pass = True
    
    # Check 1: Forbidden packages
    print("[1/3] Checking for CUDA/GPU packages...")
    violations = check_cuda_packages()
    if violations:
        print(f"    ❌ Found forbidden packages: {', '.join(violations)}")
        all_pass = False
    else:
        print("    ✓ No GPU packages found")
    
    # Check 2: PyTorch
    print("\n[2/3] Checking PyTorch configuration...")
    torch_ok, torch_msg = check_torch_cpu()
    if not torch_ok:
        print(f"    ❌ {torch_msg}")
        all_pass = False
    else:
        print(f"    ✓ {torch_msg}")
    
    # Check 3: Environment
    print("\n[3/3] Checking environment variables...")
    env_ok, env_msg = check_environment()
    if not env_ok:
        print(f"    ❌ {env_msg}")
        all_pass = False
    else:
        print(f"    ✓ {env_msg}")
    
    # Result
    print("\n" + "="*50)
    if all_pass:
        print("✅ CPU-ONLY MODE VERIFIED")
        print("Repository is properly configured for CPU-only operation.")
        return 0
    else:
        print("❌ CPU-ONLY VIOLATIONS DETECTED")
        print("\nFix instructions:")
        print("1. Uninstall GPU packages: pip uninstall torch torchvision torchaudio -y")
        print("2. Install CPU-only: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu")
        print("3. Set environment: export CUDA_VISIBLE_DEVICES=''")
        return 1

if __name__ == '__main__':
    sys.exit(main())
