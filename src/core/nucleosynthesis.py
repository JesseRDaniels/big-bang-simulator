"""
Big Bang Nucleosynthesis Engine

Models the formation of light elements (H, He, D, Li) in the first ~20 minutes.

Key Physics:
- Neutron-proton equilibrium (n ↔ p + e⁻ + ν̄)
- Deuterium bottleneck (p + n → d + γ)
- Helium-4 formation (d + d → ⁴He)
- Freeze-out when temperature drops below binding energies

Time Window:
- Start: t ~ 10 seconds (T ~ 10⁹ K, kT ~ 0.1 MeV)
- End: t ~ 1200 seconds (T ~ 3×10⁸ K, kT ~ 0.03 MeV)

Expected Abundances:
- Hydrogen (H):  75% by mass
- Helium-4 (⁴He): 25% by mass
- Deuterium (D):  D/H ~ 2.5×10⁻⁵
- Helium-3 (³He): ³He/H ~ 10⁻⁵
- Lithium-7 (⁷Li): ⁷Li/H ~ 10⁻¹⁰
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass
from scipy.integrate import solve_ivp


@dataclass
class NucleosynthesisConstants:
    """Physical constants for nucleosynthesis calculations."""

    # Particle masses (MeV)
    m_n: float = 939.57  # Neutron mass
    m_p: float = 938.27  # Proton mass
    m_e: float = 0.511   # Electron mass
    delta_m: float = 1.293  # Neutron-proton mass difference (m_n - m_p)

    # Neutron lifetime
    tau_n: float = 879.4  # seconds (free neutron decay time)

    # Nuclear binding energies (MeV)
    B_d: float = 2.224    # Deuterium binding energy
    B_He3: float = 7.718  # Helium-3 binding energy
    B_He4: float = 28.296 # Helium-4 binding energy

    # Constants
    k_B: float = 8.617e-11  # Boltzmann constant [MeV/K]
    c: float = 299792458.0  # Speed of light [m/s]

    # Baryon-to-photon ratio (from CMB observations)
    eta: float = 6.1e-10  # Baryon-to-photon ratio


class NucleosynthesisEngine:
    """
    Models Big Bang Nucleosynthesis (BBN).

    Tracks abundances of: n, p, d, ³He, ⁴He
    Simplified reaction network for computational efficiency.
    """

    def __init__(self, constants: NucleosynthesisConstants = None):
        """Initialize nucleosynthesis engine."""
        self.const = constants or NucleosynthesisConstants()

        print("✅ Nucleosynthesis engine initialized")
        print(f"   Neutron lifetime: τ_n = {self.const.tau_n:.1f} s")
        print(f"   n-p mass diff: Δm = {self.const.delta_m:.3f} MeV")
        print(f"   Deuterium binding: B_d = {self.const.B_d:.3f} MeV")

    def neutron_proton_ratio(self, T_MeV: float) -> float:
        """
        Calculate n/p ratio in thermal equilibrium.

        At high temperatures: n/p ≈ 1 (symmetric)
        At low temperatures: n/p ≈ exp(-Δm/kT) (Boltzmann suppression)

        Saha equation:
        n/p = exp(-Δm / kT)

        Args:
            T_MeV: Temperature in MeV

        Returns:
            Neutron-to-proton ratio
        """
        if T_MeV <= 0:
            return 0

        # Boltzmann factor
        ratio = np.exp(-self.const.delta_m / T_MeV)

        return ratio

    def freeze_out_ratio(self, T_freeze_MeV: float = 0.7) -> float:
        """
        Calculate n/p ratio at weak interaction freeze-out.

        Weak interactions (n ↔ p) freeze out at T ~ 0.7 MeV.
        After this, ratio only changes due to neutron decay.

        Args:
            T_freeze_MeV: Freeze-out temperature [MeV]

        Returns:
            Frozen n/p ratio
        """
        return self.neutron_proton_ratio(T_freeze_MeV)

    def neutron_fraction_with_decay(
        self,
        n_p_initial: float,
        time_elapsed: float
    ) -> Tuple[float, float]:
        """
        Calculate neutron/proton fractions accounting for decay.

        After freeze-out, neutrons decay: n → p + e⁻ + ν̄
        n(t) = n(t_freeze) * exp(-t / τ_n)

        Args:
            n_p_initial: Initial n/p ratio at freeze-out
            time_elapsed: Time since freeze-out [seconds]

        Returns:
            (neutron_fraction, proton_fraction)
        """
        # Neutron survival probability
        survival = np.exp(-time_elapsed / self.const.tau_n)

        # Current n/p ratio
        n_p_current = n_p_initial * survival

        # Convert to fractions
        # n/(n+p) and p/(n+p) with n/p = n_p_current
        neutron_frac = n_p_current / (1 + n_p_current)
        proton_frac = 1 / (1 + n_p_current)

        return neutron_frac, proton_frac

    def helium4_mass_fraction(self, neutron_fraction: float) -> float:
        """
        Calculate ⁴He mass fraction (by mass, not number).

        Nearly all neutrons end up in ⁴He (2n + 2p → ⁴He).
        Each ⁴He has mass ~ 4 GeV, uses 2 neutrons.

        Y_He4 = (mass in He4) / (total mass)
              ≈ 2 * X_n  (since each He4 uses 2 neutrons)

        Args:
            neutron_fraction: Neutron mass fraction X_n

        Returns:
            Helium-4 mass fraction Y_He4
        """
        # All neutrons → He4, each He4 has 2 neutrons
        Y_He4 = 2 * neutron_fraction

        return Y_He4

    def hydrogen_mass_fraction(self, helium4_fraction: float) -> float:
        """
        Calculate hydrogen mass fraction.

        All baryons not in He4 remain as H.
        Y_H = 1 - Y_He4

        Args:
            helium4_fraction: He4 mass fraction

        Returns:
            Hydrogen mass fraction
        """
        return 1.0 - helium4_fraction

    def deuterium_abundance(
        self,
        eta: float = None,
        T_final_MeV: float = 0.03
    ) -> float:
        """
        Estimate deuterium-to-hydrogen ratio.

        Deuterium bottleneck breaks when T ~ 0.1 MeV.
        Final abundance depends on baryon-to-photon ratio η.

        Approximate formula:
        D/H ≈ 2.6×10⁻⁵ * (η / 6×10⁻¹⁰)^(-1.6)

        Args:
            eta: Baryon-to-photon ratio
            T_final_MeV: Final temperature [MeV]

        Returns:
            D/H ratio (by number)
        """
        if eta is None:
            eta = self.const.eta

        # Empirical fit from BBN calculations
        D_H_ratio = 2.6e-5 * (eta / 6e-10)**(-1.6)

        return D_H_ratio

    def calculate_abundances(
        self,
        T_freeze_MeV: float = 0.7,
        T_nuc_start_MeV: float = 0.1,
        time_to_nucleosynthesis: float = 300.0
    ) -> Dict[str, float]:
        """
        Calculate final primordial abundances.

        Timeline:
        1. t ~ 1s: Weak interactions freeze (T ~ 0.7 MeV)
        2. t ~ 10-300s: Neutrons decay
        3. t ~ 300s: Deuterium bottleneck breaks (T ~ 0.1 MeV)
        4. t ~ 300-1200s: Rapid fusion to He4

        Args:
            T_freeze_MeV: Freeze-out temperature
            T_nuc_start_MeV: Nucleosynthesis start temperature
            time_to_nucleosynthesis: Time from freeze to BBN start [s]

        Returns:
            Dictionary of mass fractions
        """
        # Step 1: n/p ratio at freeze-out
        n_p_freeze = self.freeze_out_ratio(T_freeze_MeV)

        # Step 2: Neutron decay until nucleosynthesis starts
        X_n, X_p = self.neutron_fraction_with_decay(n_p_freeze, time_to_nucleosynthesis)

        # Step 3: Rapid fusion to He4
        Y_He4 = self.helium4_mass_fraction(X_n)
        Y_H = self.hydrogen_mass_fraction(Y_He4)

        # Step 4: Trace abundances
        D_H = self.deuterium_abundance()

        return {
            'H': Y_H,           # Hydrogen mass fraction
            'He4': Y_He4,       # Helium-4 mass fraction
            'D_H': D_H,         # Deuterium-to-hydrogen ratio
            'n_p_freeze': n_p_freeze,
            'X_n_final': X_n,
            'X_p_final': X_p
        }

    def get_bbn_summary(
        self,
        T_freeze_MeV: float = 0.7,
        time_to_nuc: float = 300.0
    ) -> str:
        """
        Get human-readable BBN summary.

        Args:
            T_freeze_MeV: Freeze-out temperature
            time_to_nuc: Time to nucleosynthesis start

        Returns:
            Formatted summary string
        """
        abundances = self.calculate_abundances(T_freeze_MeV, time_to_nucleosynthesis=time_to_nuc)

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           BIG BANG NUCLEOSYNTHESIS SUMMARY                   ║
╚══════════════════════════════════════════════════════════════╝

📊 PRIMORDIAL ABUNDANCES (by mass):
   • Hydrogen (H):    {abundances['H']*100:5.2f}%
   • Helium-4 (⁴He):  {abundances['He4']*100:5.2f}%
   • Deuterium (D/H): {abundances['D_H']:.2e}

🔬 NUCLEAR PHYSICS:
   • n/p at freeze-out: {abundances['n_p_freeze']:.4f}
   • Final X_n: {abundances['X_n_final']:.4f}
   • Final X_p: {abundances['X_p_final']:.4f}

⏱️  TIMELINE:
   • t ~ 1 s:     Weak interactions freeze (T = {T_freeze_MeV:.1f} MeV)
   • t ~ {time_to_nuc:.0f} s:  Neutron decay phase
   • t ~ 300 s:   Deuterium bottleneck breaks
   • t ~ 1200 s:  Nucleosynthesis complete

📖 OBSERVED VALUES (for comparison):
   • H:  75% ± 1%
   • ⁴He: 25% ± 1%
   • D/H: (2.5 ± 0.3)×10⁻⁵
"""
        return summary


def demo():
    """Demonstrate nucleosynthesis engine."""
    print("="*70)
    print("BIG BANG NUCLEOSYNTHESIS - DEMO")
    print("="*70)

    engine = NucleosynthesisEngine()

    # Test n/p ratio evolution
    print("\n📊 Neutron-Proton Ratio Evolution:\n")
    print(f"{'Temperature (MeV)':<20} {'n/p ratio':<15} {'n fraction':<15}")
    print("-"*50)

    temperatures = [10, 5, 2, 1, 0.7, 0.5, 0.3, 0.1]
    for T in temperatures:
        n_p = engine.neutron_proton_ratio(T)
        n_frac = n_p / (1 + n_p)
        print(f"{T:<20.1f} {n_p:<15.4f} {n_frac:<15.4f}")

    # Calculate final abundances
    print("\n" + "="*70)
    print(engine.get_bbn_summary(T_freeze_MeV=0.7, time_to_nuc=300))
    print("="*70)

    # Sensitivity to freeze-out time
    print("\n🔬 SENSITIVITY TO NEUTRON DECAY TIME:")
    print(f"\n{'Time (s)':<15} {'Y_He4 (%)':<15} {'Y_H (%)':<15}")
    print("-"*45)

    for t in [200, 250, 300, 350, 400]:
        abund = engine.calculate_abundances(time_to_nucleosynthesis=t)
        print(f"{t:<15.0f} {abund['He4']*100:<15.2f} {abund['H']*100:<15.2f}")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo()
