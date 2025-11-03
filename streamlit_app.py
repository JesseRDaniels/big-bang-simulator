"""
Big Bang Simulator - Streamlit Web App
Interactive visualization of cosmic evolution
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for web
import matplotlib.pyplot as plt
from matplotlib import cm
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulation.universe import Universe
import yaml

# Page config
st.set_page_config(
    page_title="Big Bang Simulator",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_config():
    """Load cosmology configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'cosmology_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

@st.cache_resource
def initialize_universe():
    """Initialize universe (cached to avoid recomputation)."""
    config = load_config()
    with st.spinner("🌌 Initializing universe..."):
        universe = Universe(config)

        # Run simulation to populate history
        target_time = 50e6 * 365.25 * 24 * 3600  # 50 million years in seconds
        universe.run_to_time(target_time)

    return universe

def format_time(t_seconds):
    """Convert seconds to readable time format."""
    t_years = t_seconds / (365.25 * 24 * 3600)

    if t_years < 1:
        return f"{t_years*365.25:.1f} days"
    elif t_years < 1000:
        return f"{t_years:.2f} years"
    elif t_years < 1e6:
        return f"{t_years/1000:.2f} kyr"
    elif t_years < 1e9:
        return f"{t_years/1e6:.2f} Myr"
    else:
        return f"{t_years/1e9:.2f} Gyr"

def format_temp(T):
    """Format temperature."""
    if T > 1e9:
        return f"{T/1e9:.2e} GK"
    elif T > 1e6:
        return f"{T/1e6:.2e} MK"
    elif T > 1e3:
        return f"{T/1e3:.2e} kK"
    else:
        return f"{T:.2e} K"

def create_visualization(universe, frame_idx, x_pos, y_pos, z_pos):
    """Create multi-view visualization."""
    # Get state at this frame
    if frame_idx >= len(universe.history):
        frame_idx = len(universe.history) - 1

    state = universe.history[frame_idx]

    # Get current density field
    universe.current_time = state.time
    density_field = universe.density_field
    delta = density_field - 1.0  # Density contrast

    # Create figure with multi-view layout
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

    # Color settings
    cmap = cm.seismic
    vmin, vmax = -0.3, 0.3

    # Main XY view (top-down)
    ax_xy = fig.add_subplot(gs[0:2, 0:2])
    im_xy = ax_xy.imshow(delta[:, :, z_pos].T,
                         origin='lower', cmap=cmap, vmin=vmin, vmax=vmax,
                         extent=[0, 1, 0, 1])
    ax_xy.axvline(x_pos/delta.shape[0], color='yellow', linewidth=1,
                  linestyle='--', alpha=0.6, label='X slice')
    ax_xy.axhline(y_pos/delta.shape[1], color='cyan', linewidth=1,
                  linestyle='--', alpha=0.6, label='Y slice')
    ax_xy.set_title(f"XY View (z={z_pos})", fontsize=12, fontweight='bold')
    ax_xy.set_xlabel("X")
    ax_xy.set_ylabel("Y")
    plt.colorbar(im_xy, ax=ax_xy, label='δρ/ρ', fraction=0.046)

    # XZ side view
    ax_xz = fig.add_subplot(gs[0, 2])
    im_xz = ax_xz.imshow(delta[:, y_pos, :].T,
                         origin='lower', cmap=cmap, vmin=vmin, vmax=vmax,
                         extent=[0, 1, 0, 1])
    ax_xz.set_title(f"XZ View (y={y_pos})", fontsize=10)
    ax_xz.set_xlabel("X")
    ax_xz.set_ylabel("Z")

    # YZ front view
    ax_yz = fig.add_subplot(gs[1, 2])
    im_yz = ax_yz.imshow(delta[x_pos, :, :].T,
                         origin='lower', cmap=cmap, vmin=vmin, vmax=vmax,
                         extent=[0, 1, 0, 1])
    ax_yz.set_title(f"YZ View (x={x_pos})", fontsize=10)
    ax_yz.set_xlabel("Y")
    ax_yz.set_ylabel("Z")

    # Info panel
    ax_info = fig.add_subplot(gs[2, 0:2])
    ax_info.axis('off')

    info_text = f"""
    Time: {format_time(state.time)}
    Scale Factor: a = {state.scale_factor:.6e}
    Temperature: T = {format_temp(state.temperature)}
    Hubble Parameter: H = {state.hubble:.3e} s⁻¹

    Matter Density: ρₘ = {state.rho_matter:.3e} kg/m³
    Radiation Density: ρᵣ = {state.rho_radiation:.3e} kg/m³
    Dark Energy: ρΛ = {state.rho_dark_energy:.3e} kg/m³

    Density Contrast: δρ/ρ (rms) = {state.density_rms:.3e}
    Max Overdensity: δρ/ρ (max) = {state.density_max:.3e}
    Min Underdensity: δρ/ρ (min) = {state.density_min:.3e}
    """

    ax_info.text(0.1, 0.5, info_text, fontsize=10, verticalalignment='center',
                 fontfamily='monospace')

    # Temperature evolution plot
    ax_temp = fig.add_subplot(gs[0, 3])
    times = [s.time / (1e6 * 365.25 * 24 * 3600) for s in universe.history]  # Myr
    temps = [s.temperature for s in universe.history]
    ax_temp.semilogy(times, temps, 'b-', linewidth=2)
    ax_temp.axvline(state.time / (1e6 * 365.25 * 24 * 3600),
                   color='r', linestyle='--', label='Current')
    ax_temp.set_xlabel("Time (Myr)")
    ax_temp.set_ylabel("Temperature (K)")
    ax_temp.set_title("Temperature Evolution", fontsize=10)
    ax_temp.grid(True, alpha=0.3)
    ax_temp.legend()

    # Scale factor evolution plot
    ax_scale = fig.add_subplot(gs[1, 3])
    scales = [s.scale_factor for s in universe.history]
    ax_scale.semilogy(times, scales, 'g-', linewidth=2)
    ax_scale.axvline(state.time / (1e6 * 365.25 * 24 * 3600),
                    color='r', linestyle='--', label='Current')
    ax_scale.set_xlabel("Time (Myr)")
    ax_scale.set_ylabel("Scale Factor a(t)")
    ax_scale.set_title("Expansion History", fontsize=10)
    ax_scale.grid(True, alpha=0.3)
    ax_scale.legend()

    # Density growth plot
    ax_growth = fig.add_subplot(gs[2, 2:4])
    rms_values = [s.density_rms for s in universe.history if s.density_rms is not None]
    max_values = [s.density_max for s in universe.history if s.density_max is not None]
    times_density = times[:len(rms_values)]

    ax_growth.plot(times_density, rms_values, 'b-', linewidth=2, label='RMS')
    ax_growth.plot(times_density, max_values, 'r-', linewidth=2, label='Max')
    if frame_idx < len(rms_values):
        ax_growth.axvline(times_density[frame_idx], color='orange',
                         linestyle='--', label='Current')
    ax_growth.set_xlabel("Time (Myr)")
    ax_growth.set_ylabel("Density Contrast")
    ax_growth.set_title("Structure Formation", fontsize=10)
    ax_growth.grid(True, alpha=0.3)
    ax_growth.legend()

    plt.tight_layout()
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">🌌 Big Bang Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interactive visualization of cosmic evolution from Planck epoch to structure formation</div>', unsafe_allow_html=True)

    # Initialize universe
    universe = initialize_universe()

    # Sidebar controls
    st.sidebar.header("⏱️ Time Control")

    max_frame = len(universe.history) - 1
    frame_idx = st.sidebar.slider(
        "Time Frame",
        min_value=0,
        max_value=max_frame,
        value=0,
        help="Slide to explore different epochs in cosmic history"
    )

    st.sidebar.header("📍 Position Control")

    grid_size = universe.density_field.shape[0]

    x_pos = st.sidebar.slider(
        "X Position",
        min_value=0,
        max_value=grid_size - 1,
        value=grid_size // 2,
        help="X-axis slice position"
    )

    y_pos = st.sidebar.slider(
        "Y Position",
        min_value=0,
        max_value=grid_size - 1,
        value=grid_size // 2,
        help="Y-axis slice position"
    )

    z_pos = st.sidebar.slider(
        "Z Position",
        min_value=0,
        max_value=grid_size - 1,
        value=grid_size // 2,
        help="Z-axis slice position"
    )

    # Info box
    st.sidebar.info("""
    **How to use:**
    - Use the **Time Frame** slider to explore different epochs
    - Adjust **X/Y/Z Position** sliders to navigate through 3D space
    - Watch structure formation in real-time!

    **Color scale:**
    - 🔵 Blue = Voids (underdense regions)
    - ⚪ White = Average density
    - 🔴 Red = Overdense structures (future galaxies)
    """)

    # Display current epoch info
    if frame_idx < len(universe.history):
        state = universe.history[frame_idx]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Cosmic Time", format_time(state.time))
        with col2:
            st.metric("Temperature", format_temp(state.temperature))
        with col3:
            st.metric("Scale Factor", f"{state.scale_factor:.3e}")

    # Create and display visualization
    with st.spinner("🎨 Generating visualization..."):
        fig = create_visualization(universe, frame_idx, x_pos, y_pos, z_pos)
        st.pyplot(fig)
        plt.close(fig)  # Clean up to save memory

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Built with Python, NumPy, SciPy, Matplotlib, and Streamlit |
        Based on ΛCDM cosmology with Friedmann equations
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
