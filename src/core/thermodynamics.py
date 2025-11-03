"""
Thermodynamics Engine for Big Bang Evolution

Tracks temperature evolution and particle physics throughout cosmic history.

Key Physics:
- Temperature evolution: T(t) ∝ a⁻¹ (for radiation-dominated era)
- Stefan-Boltzmann law: ρ_radiation ∝ T⁴
- Particle creation/annihilation at different energy thresholds
- Phase transitions (electroweak, QCD, etc.)

Temperature Epochs:
- Planck: T ~ 10³² K (all forces unified)
- GUT: T ~ 10²⁸ K (strong force separates)
- Electroweak: T ~ 10¹⁵ K (electromagnetic + weak separate)
- QCD: T ~ 10¹² K (quark confinement)
- Nucleosynthesis: T ~ 10⁹ K (nuclear fusion)
- Recombination: T ~ 3000 K (atoms form)
- Today: T ~ 2.7 K (CMB temperature)
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ThermodynamicsConstants:
    """Physical constants for thermodynamics calculations."""

    # Fundamental constants
    k_B: float = 1.380649e-23       # Boltzmann constant [J/K]
    h: float = 6.62607015e-34       # Planck constant [J·s]
    c: float = 299792458.0          # Speed of light [m/s]

    # Conversion factors
    eV_to_K: float = 1.1604518e4    # K per eV
    eV_to_J: float = 1.602176634e-19  # J per eV

    # Stefan-Boltzmann constant (radiation)
    sigma_SB: float = 5.670374419e-8  # W/(m²·K⁴)

    # Radiation constant (energy density)
    # ρ_radiation = a_rad * T⁴ where a_rad = 4σ_SB/c
    a_rad: float = 7.5657e-16       # J/(m³·K⁴)

    # Effective degrees of freedom (g_eff) for different eras
    # Counts number of particle species in thermal equilibrium
    g_eff_today: float = 3.36       # Photons + neutrinos (decoupled)
    g_eff_before_eewk: float = 106.75  # All Standard Model particles


class ThermodynamicsEngine:
    """
    Tracks temperature and particle physics evolution.

    Integrates with Friedmann solver to provide consistent
    thermodynamic history of the universe.
    """

    def __init__(self, constants: ThermodynamicsConstants = None):
        """Initialize thermodynamics engine."""
        self.const = constants or ThermodynamicsConstants()

        # Define particle masses (in eV) - determines when particles annihilate
        self.particle_masses = {
            'electron': 0.511e6,      # 0.511 MeV
            'muon': 105.7e6,          # 105.7 MeV
            'pion': 140e6,            # ~140 MeV
            'proton': 938.3e6,        # 938 MeV
            'tau': 1777e6,            # 1.777 GeV
            'W_boson': 80.4e9,        # 80.4 GeV
            'Z_boson': 91.2e9,        # 91.2 GeV
            'Higgs': 125e9,           # 125 GeV
            'top_quark': 173e9        # 173 GeV
        }

        print("✅ Thermodynamics engine initialized")
        print(f"   Radiation constant: a_rad = {self.const.a_rad:.3e} J/(m³·K⁴)")
        print(f"   Boltzmann constant: k_B = {self.const.k_B:.3e} J/K")

    def temperature_from_scale_factor(
        self,
        a: float,
        T_today: float = 2.725
    ) -> float:
        """
        Calculate temperature at scale factor a.

        For radiation-dominated universe: T ∝ a⁻¹
        T(a) = T_today / a

        Args:
            a: Scale factor (a=1 today)
            T_today: CMB temperature today [K]

        Returns:
            Temperature in Kelvin
        """
        if a <= 0:
            raise ValueError(f"Scale factor must be positive, got {a}")

        return T_today / a

    def scale_factor_from_temperature(
        self,
        T: float,
        T_today: float = 2.725
    ) -> float:
        """
        Calculate scale factor at temperature T.

        Inverse of temperature_from_scale_factor.

        Args:
            T: Temperature [K]
            T_today: CMB temperature today [K]

        Returns:
            Scale factor
        """
        if T <= 0:
            raise ValueError(f"Temperature must be positive, got {T}")

        return T_today / T

    def temperature_to_energy(self, T: float) -> float:
        """
        Convert temperature to characteristic energy.

        E = k_B * T

        Args:
            T: Temperature [K]

        Returns:
            Energy in Joules
        """
        return self.const.k_B * T

    def temperature_to_energy_eV(self, T: float) -> float:
        """
        Convert temperature to energy in eV.

        E [eV] = T [K] / 11605 K/eV

        Args:
            T: Temperature [K]

        Returns:
            Energy in eV
        """
        return T / self.const.eV_to_K

    def radiation_energy_density(self, T: float) -> float:
        """
        Calculate radiation energy density at temperature T.

        Stefan-Boltzmann law: ρ = a_rad * T⁴

        Args:
            T: Temperature [K]

        Returns:
            Energy density in J/m³
        """
        return self.const.a_rad * T**4

    def radiation_energy_density_kg(self, T: float) -> float:
        """
        Convert radiation energy density to mass density.

        Uses E = mc² to convert J/m³ to kg/m³

        Args:
            T: Temperature [K]

        Returns:
            Mass density in kg/m³
        """
        energy_density = self.radiation_energy_density(T)
        return energy_density / self.const.c**2

    def photon_number_density(self, T: float) -> float:
        """
        Calculate number density of photons at temperature T.

        n_γ = 2 * ζ(3) / π² * (k_B*T/ℏc)³
        where ζ(3) ≈ 1.202 (Riemann zeta function)

        Simplified: n_γ ≈ 2.404 * (k_B*T/ℏc)³

        Args:
            T: Temperature [K]

        Returns:
            Number density in m⁻³
        """
        # Characteristic momentum: k_B*T / (ℏ*c)
        hbar = self.const.h / (2 * np.pi)
        characteristic_k = self.const.k_B * T / (hbar * self.const.c)

        # Number density (with ζ(3) ≈ 1.202)
        n_gamma = 2.404 * characteristic_k**3 / np.pi**2

        return n_gamma

    def get_active_particles(self, T: float) -> Dict[str, bool]:
        """
        Determine which particles are in thermal equilibrium at temperature T.

        Particles are "active" when T > m*c²/k_B
        Below this temperature, they annihilate and don't get recreated.

        Args:
            T: Temperature [K]

        Returns:
            Dictionary of particle names and whether they're active
        """
        # Convert temperature to eV
        T_eV = self.temperature_to_energy_eV(T)

        active = {}
        for particle, mass_eV in self.particle_masses.items():
            # Rule of thumb: particles active when kT ~ mc² (within factor ~3)
            threshold = mass_eV / 3.0
            active[particle] = T_eV > threshold

        return active

    def identify_epoch(self, T: float) -> Tuple[str, str]:
        """
        Identify cosmological epoch based on temperature.

        Args:
            T: Temperature [K]

        Returns:
            (epoch_name, description)
        """
        T_eV = self.temperature_to_energy_eV(T)

        # Define epoch boundaries (in eV)
        # Note: T[K] / 11604.5 = E[eV]
        if T_eV > 1e27:  # > 1.2e31 K (Planck scale)
            return ("Planck", "Quantum gravity, all forces unified")
        elif T_eV > 1e23:  # > 1.2e27 K (GUT scale)
            return ("GUT", "Grand unification, inflation may occur")
        elif T_eV > 80e9:  # > 80 GeV ≈ 9e14 K (W/Z boson mass scale)
            return ("Electroweak", "Electroweak symmetry breaking")
        elif T_eV > 150e6:  # > 150 MeV ≈ 1.7e12 K
            return ("QCD", "Quark-hadron transition, confinement")
        elif T_eV > 1e6:  # > 1 MeV ≈ 1.2e10 K
            return ("Lepton", "Neutrino decoupling, e⁺e⁻ annihilation")
        elif T_eV > 0.1e6:  # > 0.1 MeV ≈ 1.2e9 K
            return ("Nucleosynthesis", "Light element formation")
        elif T_eV > 1:  # > 1 eV ≈ 1.2e4 K
            return ("Matter-Radiation Equality", "Matter starts dominating")
        elif T_eV > 0.25:  # > 0.25 eV ≈ 2900 K (recombination ~3000 K)
            return ("Recombination", "Atoms form, CMB released")
        else:
            return ("Matter-Dominated", "Structure formation, galaxies")

    def get_thermodynamic_state(self, a: float, T_today: float = 2.725) -> Dict:
        """
        Get complete thermodynamic state at scale factor a.

        Args:
            a: Scale factor
            T_today: CMB temperature today [K]

        Returns:
            Dictionary with temperature, energy density, active particles, epoch
        """
        T = self.temperature_from_scale_factor(a, T_today)
        T_eV = self.temperature_to_energy_eV(T)
        rho_rad = self.radiation_energy_density(T)
        rho_rad_kg = self.radiation_energy_density_kg(T)
        n_gamma = self.photon_number_density(T)
        active = self.get_active_particles(T)
        epoch_name, epoch_desc = self.identify_epoch(T)

        return {
            'scale_factor': a,
            'temperature_K': T,
            'temperature_eV': T_eV,
            'radiation_energy_density_J_m3': rho_rad,
            'radiation_mass_density_kg_m3': rho_rad_kg,
            'photon_number_density_m3': n_gamma,
            'active_particles': active,
            'epoch': epoch_name,
            'epoch_description': epoch_desc
        }


def demo():
    """Demonstrate thermodynamics engine."""
    print("="*70)
    print("THERMODYNAMICS ENGINE - DEMO")
    print("="*70)

    engine = ThermodynamicsEngine()

    # Test at different scale factors
    print("\n📊 Temperature Evolution:\n")
    print(f"{'Scale Factor':<15} {'Temperature':<15} {'Energy (eV)':<15} {'Epoch':<20}")
    print("-"*70)

    scale_factors = [1e-35, 1e-20, 1e-10, 1e-5, 1e-3, 0.1, 1.0]

    for a in scale_factors:
        state = engine.get_thermodynamic_state(a)
        print(f"{a:<15.2e} {state['temperature_K']:<15.2e} "
              f"{state['temperature_eV']:<15.2e} {state['epoch']:<20}")

    # Detailed state at nucleosynthesis
    print("\n" + "="*70)
    print("NUCLEOSYNTHESIS EPOCH (T ~ 1 MeV)")
    print("="*70)

    # Find scale factor for T = 1 MeV = 1.16e10 K
    T_nuc = 1.16e10  # K
    a_nuc = engine.scale_factor_from_temperature(T_nuc)
    state_nuc = engine.get_thermodynamic_state(a_nuc)

    print(f"\n🌡️  Temperature: {state_nuc['temperature_K']:.3e} K")
    print(f"⚡ Energy: {state_nuc['temperature_eV']:.3e} eV")
    print(f"📏 Scale factor: {state_nuc['scale_factor']:.3e}")
    print(f"🔆 Photon density: {state_nuc['photon_number_density_m3']:.3e} m⁻³")
    print(f"🌊 Radiation density: {state_nuc['radiation_mass_density_kg_m3']:.3e} kg/m³")

    print(f"\n🔬 Active Particles:")
    for particle, active in state_nuc['active_particles'].items():
        status = "✓" if active else "✗"
        print(f"   {status} {particle}")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo()
