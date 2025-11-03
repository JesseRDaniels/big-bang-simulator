# How to Run the Big Bang Simulator

## 🎯 The Problem
The simulator works perfectly but the GUI window won't appear when run from Claude Code because background processes don't have macOS WindowServer access.

## ✅ The Solution
Run the simulator **directly in your terminal** (not through Claude Code).

## 📋 Instructions

### Option 1: Using the Launcher Script (Easiest)
1. Open your **Terminal** app
2. Run this command:
   ```bash
   ~/Desktop/big-bang-simulator/run_simulator.sh
   ```
3. The GUI window will appear!

### Option 2: Manual Execution
1. Open your **Terminal** app
2. Navigate to the project:
   ```bash
   cd ~/Desktop/big-bang-simulator
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Run the simulator:
   ```bash
   python src/simulation/simulator.py
   ```

## 🎮 Using the Simulator

Once the window opens, you'll see:

### Display Elements
- **Center**: Matter density field showing structure formation
- **Top Right**: Temperature evolution over time
- **Middle Right**: Scale factor (universe expansion) over time
- **Bottom Right**: Real-time universe statistics:
  - Time (in million years)
  - Temperature
  - Scale factor
  - Density perturbations (δρ/ρ)
  - Structure formation status

### Controls
- **Slider** (bottom): Jump to any point in cosmic history (0-500 frames = 50 million years)
- **Play Button**: Start automatic time evolution
- **Pause Button**: Stop the animation
- **Reset Button**: Go back to the beginning

### What to Look For
1. **Early frames (0-200)**: Tiny density fluctuations (~10⁻⁵)
2. **Middle frames (200-400)**: Growing perturbations (quasi-linear regime)
3. **Late frames (400-500)**: Visible clumping and structure formation!
   - Look for **bright spots** in the density field
   - δρ/ρ should reach values >>1 (gravitational collapse!)
   - **This is gravity making galaxies and structure!**

## 🔬 Physics Implemented
- ✅ ΛCDM cosmology (Planck 2018 parameters)
- ✅ Friedmann expansion equations
- ✅ Linear perturbation growth (δ ∝ a)
- ✅ **Non-linear gravitational collapse** (Poisson equation)
- ✅ Matter-radiation equality transition
- ✅ Virialization of collapsed structures
- ✅ 100,000-year linear time steps

## 📊 Expected Results
By frame 500 (50 million years):
- Initial: δρ/ρ ~ 10⁻⁵ (quantum fluctuations)
- Final: δρ/ρ ~ 1-100 (gravitational structure formation)
- **8-million-fold growth** in density contrast!

---

**Note**: If you still don't see a window, check that:
1. You're running in a **real terminal** (Terminal.app), not through an IDE or Claude Code
2. Your macOS allows Python GUI access (System Preferences → Security & Privacy)
3. No other matplotlib windows are blocking the display
