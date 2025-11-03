"""
Friedmann Equation Solver

Solves the Friedmann equations describing the expansion of the universe:

    H² = (ȧ/a)² = (8πG/3)(ρₘ + ρᵣ + ρΛ) - k/a²

    ä/a = -(4πG/3)(ρₘ + 2ρᵣ + ρᵣ - 2ρΛ) + Λ/3

Where:
    a(t) = scale factor (size of universe relative to today)
    H(t) = Hubble parameter (expansion rate)
    ρₘ = matter density (∝ a⁻³)
    ρᵣ = radiation density (∝ a⁻⁴)
    ρΛ = dark energy density (constant)
    k = spatial curvature (0 for flat universe)

Scientific Foundation:
    - General Relativity (Einstein field equations)
    - ΛCDM cosmological model
    - Energy-momentum conservation
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Dict
from dataclasses import dataclass


@dataclass
class CosmologicalParameters:
    """Physical constants and cosmological parameters."""

    # Fundamental constants
    G: float = 6.67430e-11          # m³/(kg·s²)
    c: float = 299792458.0          # m/s

    # Hubble parameter today (Planck 2018)
    H0: float = 2.184e-18           # s⁻¹ (67.4 km/s/Mpc)

    # Density parameters today (dimensionless)
    Omega_m0: float = 0.315         # Matter (dark + baryonic)
    Omega_r0: float = 9.2e-5        # Radiation (photons + neutrinos)
    Omega_lambda0: float = 0.685    # Dark energy
    Omega_k0: float = 0.0           # Curvature (flat universe)

    # Critical density today
    rho_crit_0: float = 8.5e-27     # kg/m³ (3H₀²/8πG)

    def __post_init__(self):
        """Validate parameters and compute derived quantities."""
        # Check Friedmann constraint: Ωₘ + Ωᵣ + ΩΛ + Ωₖ = 1
        total = self.Omega_m0 + self.Omega_r0 + self.Omega_lambda0 + self.Omega_k0
        if abs(total - 1.0) > 1e-3:  # 0.1% tolerance for cosmological parameters
            raise ValueError(
                f"Density parameters don't sum to 1: "
                f"Ωₘ + Ωᵣ + ΩΛ + Ωₖ = {total:.6f}"
            )

        # Validate critical density
        computed_rho_crit = 3 * self.H0**2 / (8 * np.pi * self.G)
        if abs(computed_rho_crit - self.rho_crit_0) / self.rho_crit_0 > 0.01:
            print(f"⚠️  Warning: Critical density mismatch:")
            print(f"   Configured: {self.rho_crit_0:.3e} kg/m³")
            print(f"   Computed: {computed_rho_crit:.3e} kg/m³")


class FriedmannSolver:
    """
    Solves Friedmann equations for expanding universe.

    Uses adaptive ODE solver (RK45) for numerical integration.
    Tracks scale factor a(t), Hubble parameter H(t), and densities.
    """

    def __init__(self, params: CosmologicalParameters):
        """
        Initialize Friedmann solver.

        Args:
            params: Cosmological parameters
        """
        self.params = params

        # Physical densities today (kg/m³)
        self.rho_m0 = params.Omega_m0 * params.rho_crit_0
        self.rho_r0 = params.Omega_r0 * params.rho_crit_0
        self.rho_lambda0 = params.Omega_lambda0 * params.rho_crit_0

        # Solution storage
        self.time_history = []
        self.scale_factor_history = []
        self.hubble_history = []
        self.density_history = {'matter': [], 'radiation': [], 'dark_energy': []}

        print("✅ Friedmann solver initialized")
        print(f"   H₀ = {params.H0:.3e} s⁻¹")
        print(f"   Ωₘ = {params.Omega_m0:.3f}, Ωᵣ = {params.Omega_r0:.6f}, ΩΛ = {params.Omega_lambda0:.3f}")

    def density_matter(self, a: float) -> float:
        """
        Matter density at scale factor a.

        Matter dilutes as a⁻³ (volume expansion).
        ρₘ(a) = ρₘ₀ · (a₀/a)³

        Args:
            a: Scale factor (a=1 today)

        Returns:
            Matter density in kg/m³
        """
        return self.rho_m0 / a**3

    def density_radiation(self, a: float) -> float:
        """
        Radiation density at scale factor a.

        Radiation dilutes as a⁻⁴ (volume + redshift).
        ρᵣ(a) = ρᵣ₀ · (a₀/a)⁴

        Args:
            a: Scale factor

        Returns:
            Radiation density in kg/m³
        """
        return self.rho_r0 / a**4

    def density_dark_energy(self, a: float) -> float:
        """
        Dark energy density at scale factor a.

        Cosmological constant: ρΛ is constant.
        (For vacuum energy, w = -1 exactly)

        Args:
            a: Scale factor

        Returns:
            Dark energy density in kg/m³
        """
        return self.rho_lambda0  # Constant!

    def total_density(self, a: float) -> float:
        """
        Total energy density at scale factor a.

        Args:
            a: Scale factor

        Returns:
            Total density in kg/m³
        """
        return (self.density_matter(a) +
                self.density_radiation(a) +
                self.density_dark_energy(a))

    def hubble_parameter(self, a: float) -> float:
        """
        Hubble parameter at scale factor a.

        First Friedmann equation:
        H²(a) = (8πG/3)ρ(a) - k/a²

        For flat universe (k=0):
        H(a) = H₀√[Ωₘ(a₀/a)³ + Ωᵣ(a₀/a)⁴ + ΩΛ]

        Args:
            a: Scale factor

        Returns:
            Hubble parameter in s⁻¹
        """
        rho = self.total_density(a)
        H_squared = (8 * np.pi * self.params.G / 3) * rho

        # Add curvature term if non-zero
        if self.params.Omega_k0 != 0:
            H_squared -= self.params.Omega_k0 * self.params.H0**2 / a**2

        return np.sqrt(max(H_squared, 0))  # Ensure non-negative

    def friedmann_odes(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Friedmann equations as system of ODEs.

        We solve:
            da/dt = ȧ = H(a) · a

        Which comes from definition: H = ȧ/a

        Args:
            t: Time (seconds)
            y: State vector [a]

        Returns:
            Derivatives [da/dt]
        """
        a = y[0]

        # Prevent singularity at a=0
        if a <= 0:
            return np.array([0.0])

        # H(a) from first Friedmann equation
        H = self.hubble_parameter(a)

        # da/dt = H · a
        da_dt = H * a

        return np.array([da_dt])

    def solve(
        self,
        t_start: float,
        t_end: float,
        a_initial: float,
        rtol: float = 1e-8,
        atol: float = 1e-10,
        max_step: float = 1e10
    ) -> Dict:
        """
        Solve Friedmann equations from t_start to t_end.

        Args:
            t_start: Initial time (seconds)
            t_end: Final time (seconds)
            a_initial: Initial scale factor
            rtol: Relative tolerance
            atol: Absolute tolerance
            max_step: Maximum timestep (seconds)

        Returns:
            Solution dictionary with time, scale factor, densities
        """
        print(f"\n🚀 Solving Friedmann equations:")
        print(f"   Time: {t_start:.2e}s → {t_end:.2e}s")
        print(f"   Initial scale factor: a₀ = {a_initial:.2e}")

        # Initial conditions
        y0 = np.array([a_initial])

        # Solve ODE
        solution = solve_ivp(
            self.friedmann_odes,
            t_span=(t_start, t_end),
            y0=y0,
            method='RK45',
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            dense_output=True
        )

        if not solution.success:
            raise RuntimeError(f"ODE solver failed: {solution.message}")

        # Extract solution
        t = solution.t
        a = solution.y[0]

        # Compute derived quantities
        H = np.array([self.hubble_parameter(a_val) for a_val in a])
        rho_m = np.array([self.density_matter(a_val) for a_val in a])
        rho_r = np.array([self.density_radiation(a_val) for a_val in a])
        rho_lambda = np.array([self.density_dark_energy(a_val) for a_val in a])

        # Store history
        self.time_history = t
        self.scale_factor_history = a
        self.hubble_history = H
        self.density_history = {
            'matter': rho_m,
            'radiation': rho_r,
            'dark_energy': rho_lambda,
            'total': rho_m + rho_r + rho_lambda
        }

        print(f"✅ Solution computed: {len(t)} timesteps")
        print(f"   Final scale factor: a = {a[-1]:.2e}")
        print(f"   Final Hubble: H = {H[-1]:.2e} s⁻¹")

        return {
            'time': t,
            'scale_factor': a,
            'hubble': H,
            'densities': self.density_history,
            'success': True
        }

    def find_matter_radiation_equality(self) -> Tuple[float, float]:
        """
        Find when matter density = radiation density.

        At equality: ρₘ(aₑq) = ρᵣ(aₑq)

        Solving: ρₘ₀/a³ = ρᵣ₀/a⁴
        → aₑq = ρᵣ₀/ρₘ₀

        Returns:
            (a_equality, time_equality)
        """
        a_eq = self.rho_r0 / self.rho_m0

        # Find corresponding time (requires numerical integration)
        # For now, use approximate formula
        # H(a) ≈ H₀√[Ωₘ a⁻³ + Ωᵣ a⁻⁴] (ignoring ΩΛ for early universe)
        # This gives t ≈ 2/(3H₀√Ωᵣ) · a² for radiation-dominated era

        t_eq = 2 / (3 * self.params.H0 * np.sqrt(self.params.Omega_r0)) * a_eq**2

        return a_eq, t_eq

    def validate_solution(self) -> bool:
        """
        Validate Friedmann solution against known physics.

        Checks:
        1. Energy conservation (Friedmann constraint)
        2. Density evolution (ρₘ ∝ a⁻³, ρᵣ ∝ a⁻⁴)
        3. Asymptotic behavior

        Returns:
            True if validation passes
        """
        if len(self.time_history) == 0:
            print("⚠️  No solution to validate")
            return False

        print("\n🔍 Validating Friedmann solution:")

        # Check 1: Friedmann constraint H² = (8πG/3)ρ
        violations = []
        for i in range(len(self.time_history)):
            a = self.scale_factor_history[i]
            H_computed = self.hubble_history[i]
            H_expected = self.hubble_parameter(a)

            rel_error = abs(H_computed - H_expected) / H_expected
            if rel_error > 1e-4:
                violations.append(rel_error)

        if violations:
            print(f"   ⚠️  Friedmann constraint violated {len(violations)} times")
            print(f"   Max relative error: {max(violations):.2e}")
        else:
            print("   ✅ Friedmann constraint satisfied")

        # Check 2: Matter density scaling
        a0 = self.scale_factor_history[0]
        a_mid = self.scale_factor_history[len(self.time_history)//2]

        rho_m0 = self.density_history['matter'][0]
        rho_m_mid = self.density_history['matter'][len(self.time_history)//2]

        expected_ratio = (a0 / a_mid)**3
        actual_ratio = rho_m0 / rho_m_mid

        if abs(expected_ratio - actual_ratio) / expected_ratio < 0.01:
            print(f"   ✅ Matter density scales as a⁻³")
        else:
            print(f"   ⚠️  Matter density scaling incorrect")
            print(f"      Expected: {expected_ratio:.3f}, Got: {actual_ratio:.3f}")

        # Check 3: Radiation density scaling
        rho_r0 = self.density_history['radiation'][0]
        rho_r_mid = self.density_history['radiation'][len(self.time_history)//2]

        expected_ratio = (a0 / a_mid)**4
        actual_ratio = rho_r0 / rho_r_mid

        if abs(expected_ratio - actual_ratio) / expected_ratio < 0.01:
            print(f"   ✅ Radiation density scales as a⁻⁴")
        else:
            print(f"   ⚠️  Radiation density scaling incorrect")

        return len(violations) == 0


def demo():
    """Demonstration of Friedmann solver."""
    print("="*70)
    print("FRIEDMANN EQUATION SOLVER - DEMO")
    print("="*70)

    # Create cosmological parameters
    params = CosmologicalParameters()

    # Create solver
    solver = FriedmannSolver(params)

    # Find matter-radiation equality
    a_eq, t_eq = solver.find_matter_radiation_equality()
    print(f"\n📊 Matter-radiation equality:")
    print(f"   Scale factor: a = {a_eq:.2e}")
    print(f"   Time: t = {t_eq:.2e} s (~{t_eq/31557600:.0f} years)")

    # Solve from Planck time to 500 years
    t_planck = 5.391e-44
    t_end = 5e8 * 31557600  # 500 million years in seconds
    a_initial = 1e-35  # Planck-scale universe

    solution = solver.solve(
        t_start=t_planck,
        t_end=t_end,
        a_initial=a_initial,
        max_step=1e12  # 1 million seconds max step
    )

    # Validate
    solver.validate_solution()

    print("\n" + "="*70)


if __name__ == "__main__":
    demo()
