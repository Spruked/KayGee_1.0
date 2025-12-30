#!/usr/bin/env python3
"""
Caleon Director Console - Manual control interface for Caleon's voice evolution
"""

import argparse
import json
import os
from POM.caleon_instance import CaleonPOMInstance

def main():
    parser = argparse.ArgumentParser(description="Caleon Director Console")
    parser.add_argument("--setup", action="store_true", help="Initialize Caleon's workspace")
    parser.add_argument("--instance-id", default="caleon_primary", help="Caleon instance ID")
    parser.add_argument("--evolve", action="store_true", help="Trigger voice evolution")
    parser.add_argument("--samples", nargs="*", help="Sample content files for evolution")
    parser.add_argument("--target-performance", type=float, default=0.90, help="Target performance for evolution")
    parser.add_argument("--export-dna", action="store_true", help="Export Caleon's voice DNA")
    parser.add_argument("--output", help="Output file for DNA export")
    parser.add_argument("--restore", help="Restore Caleon from DNA backup file")
    parser.add_argument("--adjust", action="store_true", help="Manually adjust voice parameters")
    parser.add_argument("--voice-id", help="Voice ID to adjust")
    parser.add_argument("--param", help="Parameter to adjust")
    parser.add_argument("--value", type=float, help="New parameter value")
    parser.add_argument("--inspect", action="store_true", help="Inspect Caleon's current state")
    parser.add_argument("--show-voices", action="store_true", help="Show voice registry")
    parser.add_argument("--show-performance", action="store_true", help="Show performance log")
    
    args = parser.parse_args()
    
    if args.setup:
        print(f"🏗️  Setting up Caleon instance: {args.instance_id}")
        caleon = CaleonPOMInstance(args.instance_id)
        print("✅ Setup complete")
    
    elif args.evolve:
        caleon = CaleonPOMInstance(args.instance_id)
        
        if args.samples:
            # Load content from files
            content_samples = []
            for sample_file in args.samples:
                if os.path.exists(sample_file):
                    with open(sample_file, 'r') as f:
                        content_samples.append(f.read())
                else:
                    print(f"⚠️  Sample file not found: {sample_file}")
            
            if content_samples:
                caleon.evolve_voice(content_samples, args.target_performance)
            else:
                print("❌ No valid sample content found")
        else:
            print("❌ No sample content provided. Use --samples to specify content files")
    
    elif args.export_dna:
        caleon = CaleonPOMInstance(args.instance_id)
        dna = caleon.export_voice_dna()
        
        output_file = args.output or f"caleon_dna_{args.instance_id}_{int(__import__('time').time())}.json"
        with open(output_file, 'w') as f:
            json.dump(dna, f, indent=2)
        
        print(f"💾 Caleon's DNA exported to: {output_file}")
    
    elif args.restore:
        if not os.path.exists(args.restore):
            print(f"❌ DNA file not found: {args.restore}")
            return
        
        with open(args.restore, 'r') as f:
            dna = json.load(f)
        
        print(f"🔄 Restoring Caleon from: {args.restore}")
        
        # Create instance and restore state
        caleon = CaleonPOMInstance(dna["instance_id"])
        
        # Restore voice registry
        from POM.caleon_voice_oracle import VoiceSignature
        caleon.oracle.voice_registry = [
            VoiceSignature(**voice_data) for voice_data in dna["voice_registry"]
        ]
        
        # Restore learning params
        learning_params = dna["learning_params"]
        caleon.oracle.learning_rate = learning_params["learning_rate"]
        caleon.oracle.exploration_rate = learning_params["exploration_rate"]
        
        # Save restored state
        caleon.oracle._save_voice_registry()
        
        print("✅ Caleon restored successfully")
    
    elif args.adjust:
        if not args.voice_id or not args.param or args.value is None:
            print("❌ Must specify --voice-id, --param, and --value")
            return
        
        caleon = CaleonPOMInstance(args.instance_id)
        
        # Find the voice
        voice = next((v for v in caleon.oracle.voice_registry if v.signature_id == args.voice_id), None)
        if not voice:
            print(f"❌ Voice not found: {args.voice_id}")
            return
        
        # Adjust parameter
        if hasattr(voice, args.param):
            old_value = getattr(voice, args.param)
            setattr(voice, args.param, args.value)
            print(f"🔧 Adjusted {args.voice_id}.{args.param}: {old_value} → {args.value}")
            
            # Save changes
            caleon.oracle._save_voice_registry()
        else:
            print(f"❌ Parameter not found: {args.param}")
    
    elif args.inspect:
        caleon = CaleonPOMInstance(args.instance_id)
        
        print(f"🔍 Inspecting Caleon Instance: {args.instance_id}")
        print(f"   Voices: {len(caleon.oracle.voice_registry)}")
        print(f"   Evolution events: {len(caleon.evolution_log)}")
        print(f"   Performance logs: {len(caleon.oracle.performance_log)}")
        
        if args.show_voices:
            print("\n🎭 Voice Registry:")
            for voice in caleon.oracle.voice_registry:
                print(f"   • {voice.signature_id}: score={voice.success_score:.3f}, uses={voice.usage_count}")
        
        if args.show_performance:
            print("\n📊 Recent Performance:")
            for log in caleon.oracle.performance_log[-5:]:  # Last 5
                print(f"   • {log['voice_id']}: reward={log['reward']:.3f}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()