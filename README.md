# Big Bang Simulator

Scientifically accurate simulation of the Big Bang and early universe evolution, from Planck time to structure formation.

## Architecture

### Phase 1: Friedmann Expansion (CURRENT)
- **Core**: Friedmann equation solver for expanding universe
- **Physics**: General relativity, matter/radiation/dark energy evolution
- **Time Scale**: Planck time (10⁻⁴³s) → Matter-radiation equality (50,000 years)
- **Output**: Scale factor a(t), Hubble parameter H(t), density evolution

### Phase 2: Thermodynamics Engine
- **Core**: Temperature evolution, particle creation/annihilation
- **Physics**: Statistical mechanics, Standard Model particles
- **Epochs**: Quark-gluon plasma, hadronization, nucleosynthesis, recombination
- **Output**: Temperature T(t), particle abundances

### Phase 3: Big Bang Nucleosynthesis
- **Core**: Nuclear reaction network (p + n → d + γ, etc.)
- **Physics**: Nuclear physics, weak interactions
- **Time**: 10 seconds → 20 minutes
- **Output**: Primordial abundances (H, He, D, Li)

### Phase 4: Structure Formation
- **Core**: Density perturbation evolution
- **Physics**: Jeans instability, dark matter clustering
- **Time**: Recombination → Galaxy formation
- **Output**: Matter power spectrum, CMB fluctuations

## Scientific Foundation

### Fundamental Constants (26 parameters)
- Speed of light: c = 299,792,458 m/s
- Gravitational constant: G = 6.674×10⁻¹¹ m³/(kg·s²)
- Planck constant: ℏ = 1.055×10⁻³⁴ J·s
- Standard Model: 19 particle masses, 4 coupling constants, 3 mixing angles

### Cosmological Parameters
- Hubble constant: H₀ = 67.4 km/s/Mpc
- Matter density: Ωₘ = 0.315
- Dark energy: ΩΛ = 0.685
- Baryon density: Ωᵦ = 0.049

### Initial Conditions (Planck Epoch)
- Time: t₀ = 5.391×10⁻⁴⁴ s
- Temperature: T₀ = 1.4×10³² K
- Energy density: ρ₀ = 5.16×10⁹⁶ kg/m³
- Scale factor: a₀ = 10⁻³⁵ m (arbitrary normalization)

## Comparison to Life Simulator

| Aspect | Life Simulator | Big Bang Simulator |
|--------|----------------|-------------------|
| **Fundamental Laws** | Fick's law, ATP metabolism | Friedmann equations, thermodynamics |
| **Parameters** | ~26 biological constants | 26+ fundamental constants |
| **Timestep** | 0.02 seconds | 10⁻⁴⁴ seconds (Planck) |
| **Stability** | D·Δt/Δx² < 0.5 | Courant condition |
| **Emergence** | Evolution, complexity | Structure formation, galaxies |
| **Conservation** | Energy (ATP) | Energy-momentum tensor |

Both simulators solve differential equations describing how simple rules create complex emergent phenomena.

## Quick Start

```bash
cd ~/Desktop/big-bang-simulator
python3 -m venv venv
source venv/bin/activate
pip install numpy scipy matplotlib pyyaml

# Test Friedmann expansion
python tests/test_friedmann_expansion.py

# Run full simulation
python src/simulation/simulator.py
```

## What You'll See

**Friedmann Expansion Test**:
- Scale factor a(t) growing from Planck size to present universe
- Hubble parameter H(t) decreasing as expansion slows
- Matter, radiation, dark energy density evolution
- Transitions: radiation-dominated → matter-dominated → dark energy-dominated

**Full Simulation**:
- Temperature cooling from 10³² K to 3 K
- Particle creation/annihilation events
- Nucleosynthesis producing primordial elements
- Structure formation from quantum fluctuations

## Files

```
big-bang-simulator/
├── config/
│   └── cosmology_config.yaml      # All physical constants
├── src/
│   ├── core/
│   │   ├── friedmann.py           # Friedmann equation solver
│   │   ├── thermodynamics.py      # Temperature & particle physics
│   │   └── nucleosynthesis.py     # Nuclear reactions
│   └── simulation/
│       ├── universe.py            # Universe state manager
│       └── simulator.py           # Main engine + visualization
├── tests/
│   ├── test_friedmann_expansion.py
│   └── test_nucleosynthesis.py
└── output/
    └── metrics/                   # Simulation data
```

## Scientific Validation

Each component validated against:
- **Friedmann**: ΛCDM model predictions, Planck satellite data
- **Thermodynamics**: Particle Data Group tables
- **Nucleosynthesis**: Observed primordial abundances
- **Structure**: CMB power spectrum (WMAP/Planck)

## Memory Optimizations ⚡

**Optimized for local and cloud deployment:**
- Grid size: 64³ (~2 MB per field) - configurable in config
- History storage: Statistics only, not full 3D arrays
- Total memory: ~100-200 MB for full simulation
- Suitable for: 512 MB - 1 GB RAM instances

## Cloud Deployment ☁️

Deploy to Railway or Google Cloud Run:
```bash
# Railway (easiest)
railway init
railway up

# Google Cloud Run (pay-per-use)
gcloud run deploy big-bang-simulator --source .
```

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.**

## Next Steps

1. ✅ Phase 1: Friedmann expansion
2. ⏳ Phase 2: Thermodynamics
3. ⏳ Phase 3: Nucleosynthesis
4. ⏳ Phase 4: Structure formation
5. ⏳ Inflation extension
6. ⏳ 3D visualization

---

**Built with the same philosophy as the Life Simulator**: Start simple, test incrementally, maintain scientific accuracy.
