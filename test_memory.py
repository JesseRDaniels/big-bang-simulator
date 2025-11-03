#!/usr/bin/env python3
"""
Quick memory usage test for Big Bang Simulator.
Tests memory consumption with optimized settings.
"""

import sys
import os
sys.path.insert(0, 'src')

import psutil
import numpy as np
from simulation.universe import Universe
import yaml


def get_memory_mb():
    """Get current process memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def main():
    print("=" * 70)
    print("BIG BANG SIMULATOR - MEMORY USAGE TEST")
    print("=" * 70)

    # Load config
    with open('config/cosmology_config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    grid_size = config.get('structure', {}).get('grid_size', 256)

    print(f"\n📊 Configuration:")
    print(f"   Grid size: {grid_size}³ = {grid_size**3:,} elements")
    print(f"   Memory per field: {grid_size**3 * 8 / 1024 / 1024:.1f} MB")
    print(f"   Expected total: ~{grid_size**3 * 8 / 1024 / 1024 * 3:.1f} MB (3 arrays + overhead)")

    # Measure baseline
    mem_start = get_memory_mb()
    print(f"\n💾 Memory at start: {mem_start:.1f} MB")

    # Create universe
    print("\n🌌 Creating universe...")
    universe = Universe(config)
    mem_after_init = get_memory_mb()
    print(f"   Memory after init: {mem_after_init:.1f} MB (+{mem_after_init - mem_start:.1f} MB)")

    # Run a few frames
    print("\n⏱️  Running simulation for 10 frames...")

    years_to_sec = 31557600
    start_time = 50000 * years_to_sec
    time_step = 100000 * years_to_sec

    for i in range(10):
        target_time = start_time + i * time_step
        universe.run_to_time(target_time)

        if i % 3 == 0:
            mem_now = get_memory_mb()
            print(f"   Frame {i}: {mem_now:.1f} MB (+{mem_now - mem_start:.1f} MB)")

    # Final memory check
    mem_final = get_memory_mb()
    history_size = len(universe.history)

    print(f"\n✅ Simulation complete!")
    print(f"   Final memory: {mem_final:.1f} MB")
    print(f"   Total increase: {mem_final - mem_start:.1f} MB")
    print(f"   History entries: {history_size}")
    print(f"   Memory per history entry: {(mem_final - mem_after_init) / max(history_size, 1):.2f} MB")

    # Memory efficiency check
    if mem_final < 500:
        print(f"\n🎉 EXCELLENT! Memory usage under 500 MB")
    elif mem_final < 2000:
        print(f"\n✅ GOOD! Memory usage under 2 GB")
    elif mem_final < 8000:
        print(f"\n⚠️  WARNING! Memory usage {mem_final/1024:.1f} GB - May crash on low-memory systems")
    else:
        print(f"\n🚨 CRITICAL! Memory usage {mem_final/1024:.1f} GB - Will likely crash")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("Installing psutil for memory monitoring...")
        os.system("pip install psutil")
        import psutil

    main()
