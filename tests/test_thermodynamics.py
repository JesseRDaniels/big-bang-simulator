#!/usr/bin/env python3
"""
Test Thermodynamics Engine

Validates temperature evolution, radiation density, and epoch transitions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from core.thermodynamics import ThermodynamicsEngine, ThermodynamicsConstants


def test_initialization():
    """Test engine initialization."""
    print("="*70)
    print("TEST 1: Initialization")
    print("="*70)

    engine = ThermodynamicsEngine()
    assert engine.const.k_B > 0, "Boltzmann constant invalid"
    assert engine.const.a_rad > 0, "Radiation constant invalid"

    print("✅ Initialization passed\n")
    return engine


def test_temperature_scaling(engine):
    """Test that temperature scales as a⁻¹."""
    print("="*70)
    print("TEST 2: Temperature Scaling (T ∝ a⁻¹)")
    print("="*70)

    T_today = 2.725  # CMB temperature

    # Test at different scale factors
    test_cases = [
        (1.0, T_today),           # Today
        (0.1, T_today * 10),      # 10x hotter when 10x smaller
        (0.01, T_today * 100),    # 100x hotter
        (2.0, T_today / 2),       # 2x cooler when 2x bigger
    ]

    print(f"\n{'Scale Factor':<15} {'Expected T (K)':<15} {'Actual T (K)':<15} {'Error %':<10}")
    print("-"*70)

    for a, expected_T in test_cases:
        actual_T = engine.temperature_from_scale_factor(a, T_today)
        error = abs(actual_T - expected_T) / expected_T * 100

        print(f"{a:<15.2f} {expected_T:<15.3f} {actual_T:<15.3f} {error:<10.6f}")

        assert error < 0.001, f"Temperature scaling wrong at a={a}"

    print("\n✅ Temperature scales correctly as a⁻¹\n")


def test_radiation_density(engine):
    """Test Stefan-Boltzmann law: ρ ∝ T⁴."""
    print("="*70)
    print("TEST 3: Radiation Energy Density (ρ ∝ T⁴)")
    print("="*70)

    # Test doubling temperature quadruples density
    T1 = 1000  # K
    T2 = 2000  # K (2x hotter)

    rho1 = engine.radiation_energy_density(T1)
    rho2 = engine.radiation_energy_density(T2)

    expected_ratio = (T2 / T1)**4  # Should be 16
    actual_ratio = rho2 / rho1

    print(f"\n🔍 Density scaling test:")
    print(f"   T1 = {T1} K → ρ1 = {rho1:.3e} J/m³")
    print(f"   T2 = {T2} K → ρ2 = {rho2:.3e} J/m³")
    print(f"   Expected ratio (T2/T1)⁴: {expected_ratio:.1f}")
    print(f"   Actual ratio: {actual_ratio:.1f}")

    assert abs(expected_ratio - actual_ratio) / expected_ratio < 0.001, "T⁴ scaling wrong!"
    print("   ✅ Density scales as T⁴")

    # Validate against Stefan-Boltzmann constant
    T_test = 2.725  # CMB temperature today
    rho_cmb = engine.radiation_energy_density(T_test)
    expected_rho = engine.const.a_rad * T_test**4

    print(f"\n🔍 Stefan-Boltzmann validation:")
    print(f"   T_CMB = {T_test} K")
    print(f"   Computed ρ = {rho_cmb:.3e} J/m³")
    print(f"   Expected ρ = {expected_rho:.3e} J/m³")

    assert abs(rho_cmb - expected_rho) / expected_rho < 1e-10, "SB constant wrong!"
    print("   ✅ Stefan-Boltzmann law correct")

    print("\n✅ Radiation density test passed\n")


def test_epoch_identification(engine):
    """Test epoch classification at different temperatures."""
    print("="*70)
    print("TEST 4: Epoch Identification")
    print("="*70)

    # Known epoch boundaries (physically accurate temperatures)
    test_epochs = [
        (1e32, "Planck"),          # > 1.2e31 K
        (1e28, "GUT"),             # > 1.2e27 K
        (1e15, "Electroweak"),     # > 9e14 K (W/Z mass)
        (2e12, "QCD"),             # > 1.7e12 K (150 MeV)
        (1e10, "Nucleosynthesis"), # > 1.2e9 K (0.1 MeV)
        (3000, "Recombination"),   # > 3000 K (0.26 eV)
        (2.725, "Matter-Dominated") # Today
    ]

    print(f"\n{'Temperature (K)':<20} {'Expected Epoch':<25} {'Actual Epoch':<25} {'Match':<10}")
    print("-"*90)

    for T, expected_epoch in test_epochs:
        actual_epoch, description = engine.identify_epoch(T)
        match = "✓" if expected_epoch == actual_epoch else "✗"

        print(f"{T:<20.2e} {expected_epoch:<25} {actual_epoch:<25} {match:<10}")

        assert expected_epoch == actual_epoch, f"Epoch wrong at T={T}"

    print("\n✅ Epoch identification test passed\n")


def test_particle_activation(engine):
    """Test particle creation/annihilation thresholds."""
    print("="*70)
    print("TEST 5: Particle Activation")
    print("="*70)

    # Test at different temperatures
    # Note: Particles active when kT > m/3 (thermal creation)
    test_cases = [
        (1e15, ["top_quark", "Higgs", "W_boson", "Z_boson"]),  # Electroweak: kT ~ 86 GeV
        (2e12, ["pion"]),  # QCD: kT ~ 172 MeV (pion: 140 MeV / 3 = 47 MeV threshold)
        (1e10, ["electron"]),  # Nucleosynthesis: kT ~ 0.86 MeV (electron: 0.511 / 3 = 0.17 MeV threshold)
        (1e9, []),  # Below electron threshold
    ]

    print("\nParticle activation at different temperatures:\n")

    for T, should_be_active in test_cases:
        state = engine.get_thermodynamic_state(engine.scale_factor_from_temperature(T))
        active_particles = state['active_particles']

        print(f"T = {T:.2e} K ({state['temperature_eV']:.2e} eV) - {state['epoch']}")
        print(f"   Active particles: ", end="")
        active_list = [p for p, active in active_particles.items() if active]
        print(", ".join(active_list) if active_list else "none")

        # Verify expected particles are active
        for particle in should_be_active:
            assert active_particles.get(particle, False), \
                f"{particle} should be active at T={T}"

    print("\n✅ Particle activation test passed\n")


def test_complete_state(engine):
    """Test getting complete thermodynamic state."""
    print("="*70)
    print("TEST 6: Complete Thermodynamic State")
    print("="*70)

    # Get state at nucleosynthesis
    T_nuc = 1.16e10  # K (1 MeV)
    a_nuc = engine.scale_factor_from_temperature(T_nuc)
    state = engine.get_thermodynamic_state(a_nuc)

    print(f"\n🌡️  Nucleosynthesis Epoch:")
    print(f"   Scale factor: {state['scale_factor']:.3e}")
    print(f"   Temperature: {state['temperature_K']:.3e} K")
    print(f"   Energy: {state['temperature_eV']:.3e} eV")
    print(f"   Epoch: {state['epoch']} - {state['epoch_description']}")
    print(f"   Radiation density: {state['radiation_mass_density_kg_m3']:.3e} kg/m³")
    print(f"   Photon density: {state['photon_number_density_m3']:.3e} m⁻³")

    # Validate key properties
    assert state['epoch'] == "Nucleosynthesis", "Wrong epoch!"
    assert 1e9 < state['temperature_K'] < 1e11, "Temperature out of range!"
    assert state['photon_number_density_m3'] > 0, "Photon density invalid!"

    print("\n✅ Complete state test passed\n")


def test_cmb_today(engine):
    """Test CMB properties today."""
    print("="*70)
    print("TEST 7: CMB Today")
    print("="*70)

    state = engine.get_thermodynamic_state(a=1.0, T_today=2.725)

    print(f"\n🌌 Universe Today:")
    print(f"   Temperature: {state['temperature_K']:.3f} K")
    print(f"   Photon density: {state['photon_number_density_m3']:.3e} m⁻³")
    print(f"   Radiation density: {state['radiation_mass_density_kg_m3']:.3e} kg/m³")
    print(f"   Epoch: {state['epoch']}")

    # CMB photon density should be ~4.1×10⁸ m⁻³
    expected_n_gamma = 4.1e8
    actual_n_gamma = state['photon_number_density_m3']
    error = abs(actual_n_gamma - expected_n_gamma) / expected_n_gamma

    print(f"\n🔍 CMB photon density check:")
    print(f"   Expected: {expected_n_gamma:.2e} m⁻³")
    print(f"   Actual: {actual_n_gamma:.2e} m⁻³")
    print(f"   Error: {error*100:.1f}%")

    assert error < 0.1, "CMB photon density wrong!"
    print("   ✅ CMB properties correct")

    print("\n✅ CMB test passed\n")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🌡️  THERMODYNAMICS ENGINE - COMPREHENSIVE TEST")
    print("="*70 + "\n")

    engine = test_initialization()
    test_temperature_scaling(engine)
    test_radiation_density(engine)
    test_epoch_identification(engine)
    test_particle_activation(engine)
    test_complete_state(engine)
    test_cmb_today(engine)

    print("\n" + "="*70)
    print("✅ ALL THERMODYNAMICS TESTS PASSED!")
    print("="*70)
    print("\n🎉 The thermodynamics engine is working correctly!")
    print("   - Temperature scales as T ∝ a⁻¹")
    print("   - Radiation density follows ρ ∝ T⁴")
    print("   - Epochs correctly identified")
    print("   - Particle physics thresholds accurate")
    print("   - CMB properties validated")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
