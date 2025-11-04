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
        # NO precomputation - compute frames on-demand for fast startup

    return universe

@st.cache_data(show_spinner=False)
def get_state_at_time(target_time):
    """
    Get universe state at specific time (cached per time).

    Args:
        target_time: Target time in seconds

    Returns:
        UniverseState at requested time
    """
    # Create temporary universe instance for this computation
    config = load_config()
    temp_universe = Universe(config)

    # Compute to target time
    temp_universe.run_to_time(target_time)

    # Return final state with full density field
    return temp_universe.get_current_state(include_density_field=True)

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

def create_visualization(state, x_pos, y_pos, z_pos, all_times):
    """Create multi-view visualization."""
    # Extract density field from state
    density_field = state.density_field
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

    # Time progress indicator
    ax_time = fig.add_subplot(gs[0, 3])
    ax_time.axis('off')
    current_time_myr = state.time / (1e6 * 365.25 * 24 * 3600)
    max_time_myr = max(all_times) / (1e6 * 365.25 * 24 * 3600)
    progress = current_time_myr / max_time_myr if max_time_myr > 0 else 0

    time_text = f"""
    ⏱️  Cosmic Time Progress

    Current: {current_time_myr:.2f} Myr
    Maximum: {max_time_myr:.2f} Myr
    Progress: {progress*100:.1f}%

    Epoch: {state.epoch}
    """
    ax_time.text(0.1, 0.5, time_text, fontsize=11, verticalalignment='center',
                 fontfamily='monospace')

    # Key Metrics Panel
    ax_metrics = fig.add_subplot(gs[1, 3])
    ax_metrics.axis('off')
    metrics_text = f"""
    📊 Current Metrics

    Temperature:
      {format_temp(state.temperature)}

    Scale Factor:
      a = {state.scale_factor:.3e}

    Hubble Parameter:
      H = {state.hubble:.3e} s⁻¹
    """
    ax_metrics.text(0.1, 0.5, metrics_text, fontsize=11, verticalalignment='center',
                   fontfamily='monospace')

    # Structure Formation Stats
    ax_structure = fig.add_subplot(gs[2, 2:4])
    ax_structure.axis('off')
    structure_text = f"""
    🌌 Structure Formation

    Density Perturbations:
      • RMS: δρ/ρ = {state.density_rms:.3e}
      • Maximum: δρ/ρ = {state.density_max:.3e}
      • Minimum: δρ/ρ = {state.density_min:.3e}

    Status: {'Structures forming' if state.density_max > 0.01 else 'Linear regime'}
    """
    ax_structure.text(0.1, 0.5, structure_text, fontsize=11, verticalalignment='center',
                     fontfamily='monospace')

    plt.tight_layout()
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">🌌 Big Bang Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interactive visualization of cosmic evolution from Planck epoch to structure formation</div>', unsafe_allow_html=True)

    # Initialize universe (fast - no precomputation)
    universe = initialize_universe()

    # Define time points (in seconds) - logarithmic spacing
    # From ~1 second to 50 million years
    num_points = 50
    time_years = np.logspace(np.log10(1/(365.25*24*3600)), np.log10(50e6), num_points)
    time_points = time_years * 365.25 * 24 * 3600  # Convert to seconds

    # Sidebar controls
    st.sidebar.header("⏱️ Time Control")

    time_idx = st.sidebar.slider(
        "Cosmic Time",
        min_value=0,
        max_value=len(time_points) - 1,
        value=0,
        key="time_slider",
        help="Slide to explore different epochs in cosmic history. First load of each time may take 10-30 seconds."
    )

    target_time = time_points[time_idx]

    # Show current time selection
    st.sidebar.markdown(f"**Selected Time:** {format_time(target_time)}")
    st.sidebar.markdown(f"**Time Index:** {time_idx + 1} / {len(time_points)}")

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
    - Use the **Cosmic Time** slider to explore different epochs
    - Adjust **X/Y/Z Position** sliders to navigate through 3D space
    - Watch structure formation evolve!

    **Color scale:**
    - 🔵 Blue = Voids (underdense regions)
    - ⚪ White = Average density
    - 🔴 Red = Overdense structures (future galaxies)

    **Note:** First load of each time point may take a few seconds as the universe evolves to that epoch.
    """)

    # Get state at selected time (cached for performance)
    # Note: First computation for each time point may take 10-30 seconds
    with st.spinner(f"⏳ Computing universe at {format_time(target_time)}... (this may take 10-30 seconds for first load)"):
        state = get_state_at_time(target_time)

    # Debug: Show state object ID to verify it's changing
    if st.sidebar.checkbox("Show Debug Info", value=False):
        st.sidebar.code(f"State ID: {id(state)}\nTime: {state.time:.2e}s\nTemp: {state.temperature:.2e}K")

    # Display current epoch info
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Cosmic Time", format_time(state.time))
    with col2:
        st.metric("Temperature", format_temp(state.temperature))
    with col3:
        st.metric("Scale Factor", f"{state.scale_factor:.3e}")

    # Create and display visualization
    with st.spinner("🎨 Generating visualization..."):
        fig = create_visualization(state, x_pos, y_pos, z_pos, time_points)
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
