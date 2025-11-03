"""
Universe State Manager

Integrates all physics engines:
- Friedmann expansion
- Thermodynamics
- Nucleosynthesis
- Matter density perturbations

Manages complete cosmic evolution from Big Bang to structure formation.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.friedmann import FriedmannSolver, CosmologicalParameters
from core.thermodynamics import ThermodynamicsEngine
from core.nucleosynthesis import NucleosynthesisEngine


@dataclass
class UniverseState:
    """Snapshot of universe at a given time."""
    time: float              # seconds
    scale_factor: float     # dimensionless
    temperature: float       # Kelvin
    hubble: float           # s⁻¹
    epoch: str              # Epoch name

    # Densities
    rho_matter: float       # kg/m³
    rho_radiation: float    # kg/m³
    rho_dark_energy: float  # kg/m³

    # Abundances (if nucleosynthesis occurred)
    H_fraction: Optional[float] = None
    He_fraction: Optional[float] = None

    # Matter perturbations - STATISTICS ONLY (not full field to save memory)
    density_rms: Optional[float] = None      # RMS of density perturbations
    density_max: Optional[float] = None      # Max density contrast
    density_min: Optional[float] = None      # Min density contrast

    # Full field only stored for current state (not in history)
    density_field: Optional[np.ndarray] = None


class Universe:
    """
    Complete universe simulation.

    Manages cosmic evolution from Planck time to structure formation.
    """

    def __init__(self, config: dict):
        """Initialize universe with configuration."""
        self.config = config

        # Initialize physics engines
        print("🌌 Initializing Universe...")
        self.cosmo_params = CosmologicalParameters()
        self.friedmann = FriedmannSolver(self.cosmo_params)
        self.thermo = ThermodynamicsEngine()
        self.bbn = NucleosynthesisEngine()

        # Current state
        self.current_time = config['simulation']['start_time']
        self.current_scale_factor = config['initial_conditions']['scale_factor']

        # History
        self.history = []

        # Matter density field (for structure formation visualization)
        self.grid_size = config.get('structure', {}).get('grid_size', 256)
        self.initialize_density_field()

        print(f"✅ Universe initialized")
        print(f"   Grid size: {self.grid_size}x{self.grid_size}x{self.grid_size}")
        print(f"   Start time: {self.current_time:.2e} s")

    def initialize_density_field(self):
        """
        Initialize matter density field with quantum fluctuations.

        Seeds from inflation: δρ/ρ ~ 10⁻⁵ (Gaussian random field)
        These grow via gravitational instability.
        """
        # Base density (uniform) - NOW 3D!
        self.density_field = np.ones((self.grid_size, self.grid_size, self.grid_size))

        # Add primordial perturbations (from inflation)
        # δρ/ρ ~ 10⁻⁵ at recombination
        amplitude = 1e-5

        # Generate Gaussian random field (power spectrum P(k) ∝ k^n, n≈1)
        # Simplified: just Gaussian noise at multiple scales
        for scale in [1, 2, 4, 8, 16]:
            # Generate noise at this scale
            noise_size = self.grid_size // scale
            noise = np.random.normal(0, amplitude, (noise_size, noise_size, noise_size))

            # Upsample to full 3D grid using repeat
            noise_full = np.repeat(np.repeat(np.repeat(noise, scale, axis=0), scale, axis=1), scale, axis=2)

            # Add to density field
            self.density_field += noise_full

            # Smaller amplitude for smaller scales (rough approximation)
            amplitude *= 0.7

        print(f"   Density fluctuations: δρ/ρ ~ {np.std(self.density_field - 1):.2e}")

    def get_current_state(self, include_density_field: bool = True) -> UniverseState:
        """
        Get complete state at current time.

        Args:
            include_density_field: If True, includes full 3D density field (for visualization).
                                  If False, only includes statistics (for history storage).
        """
        # Thermodynamic state
        thermo_state = self.thermo.get_thermodynamic_state(
            self.current_scale_factor
        )

        # Densities from Friedmann
        rho_m = self.friedmann.density_matter(self.current_scale_factor)
        rho_r = self.friedmann.density_radiation(self.current_scale_factor)
        rho_lambda = self.friedmann.density_dark_energy(self.current_scale_factor)

        # Nucleosynthesis (if in that epoch)
        H_frac, He_frac = None, None
        if 10 < self.current_time < 1200:  # BBN window
            abundances = self.bbn.calculate_abundances(
                time_to_nucleosynthesis=self.current_time - 1
            )
            H_frac = abundances['H']
            He_frac = abundances['He4']

        # Calculate density field statistics (always)
        delta = self.density_field - 1.0
        density_rms = np.std(delta)
        density_max = np.max(delta)
        density_min = np.min(delta)

        return UniverseState(
            time=self.current_time,
            scale_factor=self.current_scale_factor,
            temperature=thermo_state['temperature_K'],
            hubble=self.friedmann.hubble_parameter(self.current_scale_factor),
            epoch=thermo_state['epoch'],
            rho_matter=rho_m,
            rho_radiation=rho_r,
            rho_dark_energy=rho_lambda,
            H_fraction=H_frac,
            He_fraction=He_frac,
            density_rms=density_rms,
            density_max=density_max,
            density_min=density_min,
            density_field=self.density_field.copy() if include_density_field else None
        )

    def step(self, dt: float):
        """
        Advance universe by timestep dt.

        Args:
            dt: Timestep in seconds
        """
        # Update scale factor using Hubble parameter
        H = self.friedmann.hubble_parameter(self.current_scale_factor)
        da_dt = H * self.current_scale_factor

        self.current_scale_factor += da_dt * dt
        self.current_time += dt

        # Grow density perturbations (simplified growth)
        # δ ∝ a in matter-dominated era
        # δ ∝ a² in radiation-dominated era
        growth_rate = self.get_perturbation_growth_rate()
        self.density_field = 1 + (self.density_field - 1) * (1 + growth_rate * dt)

        # Apply gravitational collapse in non-linear regime
        delta_mean = np.mean(np.abs(self.density_field - 1.0))
        if delta_mean > 0.1:
            self.apply_gravitational_collapse(dt)

    def get_perturbation_growth_rate(self) -> float:
        """
        Calculate density perturbation growth rate with non-linear effects.

        Physics:
        - Linear regime (δ << 1): δ ∝ a (matter-dom) or δ ∝ a² (radiation-dom)
        - Non-linear regime (δ > 1): Gravitational collapse accelerates
        - Zel'dovich approximation for quasi-linear regime (0.1 < δ < 1)

        Returns:
            Growth rate per unit time
        """
        rho_m = self.friedmann.density_matter(self.current_scale_factor)
        rho_r = self.friedmann.density_radiation(self.current_scale_factor)

        # Fraction in matter
        f_matter = rho_m / (rho_m + rho_r + 1e-100)

        H = self.friedmann.hubble_parameter(self.current_scale_factor)

        # Linear growth rate
        if f_matter > 0.5:
            # Matter-dominated: δ ∝ a
            base_growth = H
        else:
            # Radiation-dominated: slower growth
            base_growth = 0.1 * H

        # Non-linear enhancement based on local overdensity
        # Average perturbation amplitude
        delta_mean = np.mean(np.abs(self.density_field - 1.0))

        if delta_mean > 1.0:
            # Non-linear regime: collapse accelerates
            # Growth rate increases dramatically: δ ∝ exp(H*t) in collapsing regions
            nonlinear_boost = 2.0 + delta_mean  # Accelerated collapse
            return base_growth * nonlinear_boost
        elif delta_mean > 0.1:
            # Quasi-linear regime: Zel'dovich approximation
            # Growth slightly faster than linear
            zel_boost = 1.0 + 2.0 * delta_mean  # Smooth transition
            return base_growth * zel_boost
        else:
            # Linear regime
            return base_growth

    def apply_gravitational_collapse(self, dt: float):
        """
        Apply gravitational collapse in non-linear regime.

        Physics:
        - Overdense regions (δ > 0) attract more matter
        - Underdense regions (δ < 0) lose matter
        - Simulates Jeans instability and local collapse

        Uses a simple diffusion-like model where matter flows
        from low to high density regions.
        """
        from scipy.ndimage import laplace, gaussian_filter

        # Calculate overdensity: δ = (ρ - ρ_mean) / ρ_mean
        delta = self.density_field - 1.0

        # Only apply collapse if in matter-dominated era (after equality)
        rho_m = self.friedmann.density_matter(self.current_scale_factor)
        rho_r = self.friedmann.density_radiation(self.current_scale_factor)
        f_matter = rho_m / (rho_m + rho_r + 1e-100)

        if f_matter < 0.5:
            # Still radiation-dominated, no collapse yet
            return

        # Gravitational potential approximation: ∇²φ ∝ δ (Poisson equation)
        # Use Laplacian as proxy for gravitational attraction
        gravitational_force = laplace(delta)

        # Collapse strength (increases with time in matter-dominated era)
        # After equality, collapse becomes significant
        collapse_strength = 0.1 * (f_matter - 0.5) * dt * 1e-16

        # Matter flows down potential wells (toward high density)
        # This creates the "gravitational clumping" effect
        density_change = collapse_strength * gravitational_force

        # Apply collapse with stability limit
        max_change = 0.01  # Prevent numerical instability
        density_change = np.clip(density_change, -max_change, max_change)

        self.density_field += density_change

        # Apply smoothing to represent dark matter halos
        # In non-linear regime, structures virialize (settle into equilibrium)
        delta_max = np.max(np.abs(delta))
        if delta_max > 1.0:
            # Smooth high-density regions to represent virialized halos
            smoothing_scale = 0.5  # Sigma for Gaussian filter
            delta_smoothed = gaussian_filter(delta, sigma=smoothing_scale)

            # Blend: keep high-frequency structure but smooth peaks
            blend_factor = min((delta_max - 1.0) / 2.0, 0.3)
            delta_blended = (1 - blend_factor) * delta + blend_factor * delta_smoothed

            self.density_field = 1.0 + delta_blended

        # Enforce physical bounds (density must be positive)
        self.density_field = np.maximum(self.density_field, 0.01)

    def run_to_time(self, target_time: float, callback=None):
        """
        Evolve universe to target time.

        Args:
            target_time: Time to evolve to [seconds]
            callback: Optional function called each step
        """
        # Adaptive timestep (logarithmic for extreme time scales)
        while self.current_time < target_time:
            # Timestep: 1% of current time (logarithmic stepping)
            # Use tiny minimum for early universe (Planck scale)
            dt = max(self.current_time * 0.01, self.current_time * 1e-6)
            dt = min(dt, target_time - self.current_time)

            self.step(dt)

            # Record state periodically (every 10% increase in time)
            # DON'T store full density field in history (saves memory!)
            if len(self.history) == 0 or \
               self.current_time / self.history[-1].time > 1.1:
                state = self.get_current_state(include_density_field=False)
                self.history.append(state)

                if callback:
                    # Callback gets full state with density field
                    full_state = self.get_current_state(include_density_field=True)
                    callback(full_state)

        # Final state (with full density field for visualization)
        state = self.get_current_state(include_density_field=True)
        return state


def demo():
    """Quick demo of universe evolution."""
    import yaml

    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..',
        'config', 'cosmology_config.yaml'
    )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override for quick demo
    config['structure'] = {'grid_size': 128}

    universe = Universe(config)

    print("\n" + "="*70)
    print("UNIVERSE EVOLUTION - DEMO")
    print("="*70)

    # Evolve to key epochs
    epochs = [
        (1, "Weak freeze-out"),
        (100, "Before BBN"),
        (300, "During BBN"),
        (1200, "After BBN"),
        (1e5, "Matter-radiation equality"),
        (1e13, "Recombination")
    ]

    for target_time, description in epochs:
        state = universe.run_to_time(target_time)

        print(f"\n⏱️  t = {state.time:.2e} s - {description}")
        print(f"   T = {state.temperature:.2e} K")
        print(f"   a = {state.scale_factor:.2e}")
        print(f"   Epoch: {state.epoch}")

        if state.H_fraction:
            print(f"   H: {state.H_fraction*100:.1f}%, He: {state.He_fraction*100:.1f}%")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo()
