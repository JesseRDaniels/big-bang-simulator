#!/usr/bin/env python3
"""
Test Friedmann Equation Solver

Tests the expansion of the universe from Planck time to present.
Validates density evolution and key cosmological milestones.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from core.friedmann import FriedmannSolver, CosmologicalParameters


def test_initialization():
    """Test solver initialization and parameter validation."""
    print("="*70)
    print("TEST 1: Initialization")
    print("="*70)

    params = CosmologicalParameters()
    solver = FriedmannSolver(params)

    # Check density parameters sum to 1 (within cosmological precision)
    total = params.Omega_m0 + params.Omega_r0 + params.Omega_lambda0 + params.Omega_k0
    assert abs(total - 1.0) < 1e-3, f"Density parameters sum to {total}, not 1!"

    print("✅ Initialization passed\n")
    return solver


def test_density_evolution(solver):
    """Test that densities scale correctly with scale factor."""
    print("="*70)
    print("TEST 2: Density Evolution")
    print("="*70)

    # Test at different scale factors
    a_values = [0.001, 0.01, 0.1, 1.0, 10.0]

    print("\nScale Factor | Matter Density | Radiation Density | Dark Energy")
    print("-"*70)

    for a in a_values:
        rho_m = solver.density_matter(a)
        rho_r = solver.density_radiation(a)
        rho_lambda = solver.density_dark_energy(a)

        print(f"{a:12.3f} | {rho_m:13.3e} | {rho_r:17.3e} | {rho_lambda:11.3e}")

    # Validate scaling laws
    # At smaller a, density is higher (∝ a⁻³), so rho(a1) / rho(a2) = (a2/a1)³
    a1, a2 = 0.1, 1.0
    rho_m1 = solver.density_matter(a1)
    rho_m2 = solver.density_matter(a2)
    expected_ratio = (a2/a1)**3  # Ratio should be (1.0/0.1)³ = 1000
    actual_ratio = rho_m1 / rho_m2

    print(f"\n🔍 Matter density scaling (a⁻³):")
    print(f"   Expected ratio: {expected_ratio:.1f}")
    print(f"   Actual ratio: {actual_ratio:.1f}")
    assert abs(expected_ratio - actual_ratio) / expected_ratio < 0.01, "Matter scaling wrong!"
    print("   ✅ Scales correctly as a⁻³")

    rho_r1 = solver.density_radiation(a1)
    rho_r2 = solver.density_radiation(a2)
    expected_ratio = (a2/a1)**4  # Ratio should be (1.0/0.1)⁴ = 10000
    actual_ratio = rho_r1 / rho_r2

    print(f"\n🔍 Radiation density scaling (a⁻⁴):")
    print(f"   Expected ratio: {expected_ratio:.1f}")
    print(f"   Actual ratio: {actual_ratio:.1f}")
    assert abs(expected_ratio - actual_ratio) / expected_ratio < 0.01, "Radiation scaling wrong!"
    print("   ✅ Scales correctly as a⁻⁴")

    print("\n✅ Density evolution passed\n")


def test_matter_radiation_equality(solver):
    """Test calculation of matter-radiation equality."""
    print("="*70)
    print("TEST 3: Matter-Radiation Equality")
    print("="*70)

    a_eq, t_eq = solver.find_matter_radiation_equality()

    print(f"\n📊 Equality conditions:")
    print(f"   Scale factor: a_eq = {a_eq:.3e}")
    print(f"   Time: t_eq = {t_eq:.3e} s")
    print(f"   Time: t_eq = {t_eq/31557600:.0f} years")

    # Validate that densities are actually equal
    rho_m_eq = solver.density_matter(a_eq)
    rho_r_eq = solver.density_radiation(a_eq)

    print(f"\n🔍 Density check at equality:")
    print(f"   Matter: {rho_m_eq:.3e} kg/m³")
    print(f"   Radiation: {rho_r_eq:.3e} kg/m³")
    print(f"   Ratio: {rho_m_eq/rho_r_eq:.6f}")

    assert abs(rho_m_eq - rho_r_eq) / rho_m_eq < 0.01, "Densities not equal!"
    print("   ✅ Densities are equal")

    # Expected: ~50,000-100,000 years (observational constraint with approximation tolerance)
    assert 1e12 < t_eq < 5e12, f"Equality time {t_eq} outside expected range!"
    print("   ✅ Equality time within expected range (order of magnitude correct)")

    print("\n✅ Matter-radiation equality test passed\n")


def test_friedmann_solution(solver):
    """Test full solution from Planck time to present."""
    print("="*70)
    print("TEST 4: Full Friedmann Solution")
    print("="*70)

    # Solve from Planck epoch to 1 billion years
    t_planck = 5.391e-44  # seconds
    t_end = 1e9 * 31557600  # 1 billion years in seconds
    a_initial = 1e-35  # Planck-scale size

    solution = solver.solve(
        t_start=t_planck,
        t_end=t_end,
        a_initial=a_initial,
        max_step=1e13  # Large steps for efficiency
    )

    assert solution['success'], "Solver failed!"
    print(f"\n✅ Solution computed: {len(solution['time'])} timesteps")

    # Validate solution
    is_valid = solver.validate_solution()
    assert is_valid, "Validation failed!"

    print("\n✅ Full solution test passed\n")

    return solution


def visualize_solution(solver, solution):
    """Create plots of the solution."""
    print("="*70)
    print("VISUALIZATION")
    print("="*70)

    t = solution['time']
    a = solution['scale_factor']
    H = solution['hubble']
    densities = solution['densities']

    # Convert time to years for plotting
    t_years = t / 31557600

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Scale factor evolution
    ax = axes[0, 0]
    ax.loglog(t_years, a, 'b-', linewidth=2)
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_ylabel('Scale Factor a(t)', fontsize=11)
    ax.set_title('Universe Expansion', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Mark matter-radiation equality
    a_eq, t_eq = solver.find_matter_radiation_equality()
    ax.axvline(t_eq/31557600, color='red', linestyle='--', alpha=0.5, label='Matter-Rad Equality')
    ax.legend()

    # 2. Hubble parameter
    ax = axes[0, 1]
    ax.loglog(t_years, H, 'r-', linewidth=2)
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_ylabel('Hubble Parameter H(t) [s⁻¹]', fontsize=11)
    ax.set_title('Expansion Rate', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # 3. Density evolution
    ax = axes[1, 0]
    ax.loglog(t_years, densities['matter'], 'r-', linewidth=2, label='Matter', alpha=0.8)
    ax.loglog(t_years, densities['radiation'], 'orange', linewidth=2, label='Radiation', alpha=0.8)
    ax.loglog(t_years, densities['dark_energy'], 'c-', linewidth=2, label='Dark Energy', alpha=0.8)
    ax.loglog(t_years, densities['total'], 'k--', linewidth=1, label='Total', alpha=0.5)
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_ylabel('Density [kg/m³]', fontsize=11)
    ax.set_title('Energy Density Evolution', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Density fractions
    ax = axes[1, 1]
    total = densities['total']
    omega_m = densities['matter'] / total
    omega_r = densities['radiation'] / total
    omega_lambda = densities['dark_energy'] / total

    ax.semilogx(t_years, omega_m, 'r-', linewidth=2, label='Ωₘ (Matter)')
    ax.semilogx(t_years, omega_r, 'orange', linewidth=2, label='Ωᵣ (Radiation)')
    ax.semilogx(t_years, omega_lambda, 'c-', linewidth=2, label='ΩΛ (Dark Energy)')
    ax.set_xlabel('Time (years)', fontsize=11)
    ax.set_ylabel('Density Fraction', fontsize=11)
    ax.set_title('Universe Composition', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Add epoch markers
    epochs = {
        'Planck': 1.7e-36,
        'Nucleosynthesis': 3.8e-6,
        'Equality': t_eq/31557600,
        'Recombination': 3.8e5
    }

    for name, time in epochs.items():
        if t_years[0] < time < t_years[-1]:
            ax.axvline(time, color='gray', linestyle=':', alpha=0.3)

    plt.suptitle('🌌 Big Bang Evolution - Friedmann Equations', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Save figure
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'friedmann_expansion.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n📊 Plots saved to: {output_file}")

    plt.show()


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🌌 FRIEDMANN EQUATION SOLVER - COMPREHENSIVE TEST")
    print("="*70 + "\n")

    # Run tests in sequence
    solver = test_initialization()
    test_density_evolution(solver)
    test_matter_radiation_equality(solver)
    solution = test_friedmann_solution(solver)

    # Visualize
    visualize_solution(solver, solution)

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\n🎉 The Friedmann solver is working correctly!")
    print("   - Densities evolve as ρₘ ∝ a⁻³, ρᵣ ∝ a⁻⁴")
    print("   - Matter-radiation equality at ~50,000 years")
    print("   - Universe expansion follows ΛCDM model")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
