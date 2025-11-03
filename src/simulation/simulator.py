"""
Interactive Big Bang Simulator

Visualizes cosmic evolution with real-time controls:
- Time slider to jump to different epochs
- Speed control for evolution rate
- Matter density field showing structure formation
- Real-time thermodynamic state display

Controls:
- Space: Play/Pause
- Left/Right arrows: Rewind/Fast-forward
- Slider: Jump to specific time
"""

import numpy as np
import matplotlib
import os

# Detect if running in headless environment (cloud/server)
# Priority: Respect MPLBACKEND env var if already set (e.g., by Dockerfile)
mpl_backend = os.environ.get('MPLBACKEND')
if mpl_backend:
    matplotlib.use(mpl_backend)  # Use explicitly set backend
elif os.environ.get('DISPLAY') is None:
    matplotlib.use('Agg')  # No display available, use non-interactive
else:
    try:
        matplotlib.use('MacOSX')  # Interactive GUI for macOS
    except ImportError:
        matplotlib.use('Agg')  # Fallback to non-interactive

import matplotlib.pyplot as plt
# Removed FuncAnimation - using Timer for event-driven updates instead
from matplotlib.widgets import Slider, Button
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from simulation.universe import Universe
import yaml


class InteractiveBigBangSimulator:
    """
    Real-time visual simulation of Big Bang with interactive controls.
    """

    def __init__(self, config_path: str):
        """Initialize simulator with configuration."""
        # Load config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Create universe
        print("🌌 Initializing universe...")
        self.universe = Universe(self.config)

        # Simulation parameters
        self.is_playing = False
        self.speed_multiplier = 1.0

        # Time milestones - LINEAR spacing for structure formation
        # Start at matter-radiation equality, use 100,000 year increments

        # Convert to seconds
        years_to_sec = 31557600

        # Start at 50,000 years (matter-radiation equality)
        start_time = 50000 * years_to_sec

        # Each frame = 100,000 years
        time_step = 100000 * years_to_sec

        # 500 frames × 100,000 years = 50 million years total
        self.time_milestones = np.arange(start_time, start_time + 500 * time_step, time_step)

        self.current_frame = 0

        # Slice positions for multi-view (initially at center)
        grid_size = self.universe.grid_size
        self.x_pos = grid_size // 2
        self.y_pos = grid_size // 2
        self.z_pos = grid_size // 2

        # Setup visualization
        self.setup_figure()

    def setup_figure(self):
        """Create interactive figure with subplots and controls."""
        # Create figure with custom layout
        self.fig = plt.figure(figsize=(18, 10))
        self.fig.suptitle('🌌 Interactive Big Bang Simulation - Multi-View',
                         fontsize=16, fontweight='bold')

        # Create grid layout: 3 rows x 4 columns for multi-view
        gs = self.fig.add_gridspec(3, 4, hspace=0.35, wspace=0.35,
                                   left=0.05, right=0.98, top=0.93, bottom=0.15)

        # 1. Main XY density field (top-left, large 2x2)
        self.ax_density = self.fig.add_subplot(gs[0:2, 0:2])
        self.ax_density.set_title('XY View (Top-Down) - Matter Density at Z slice',
                                  fontweight='bold', fontsize=10)
        self.ax_density.set_xlabel('X →')
        self.ax_density.set_ylabel('Y →')

        # 2. XZ side view (top-right, medium)
        self.ax_xz = self.fig.add_subplot(gs[0, 2])
        self.ax_xz.set_title('XZ View (Side)', fontweight='bold', fontsize=9)
        self.ax_xz.set_xlabel('X →')
        self.ax_xz.set_ylabel('Z ↑')

        # 3. YZ front view (middle-right, medium)
        self.ax_yz = self.fig.add_subplot(gs[1, 2])
        self.ax_yz.set_title('YZ View (Front)', fontweight='bold', fontsize=9)
        self.ax_yz.set_xlabel('Y →')
        self.ax_yz.set_ylabel('Z ↑')

        # 4. Temperature evolution (top-right column)
        self.ax_temp = self.fig.add_subplot(gs[0, 3])
        self.ax_temp.set_title('Temperature', fontweight='bold', fontsize=9)
        self.ax_temp.set_xlabel('Time (s)', fontsize=8)
        self.ax_temp.set_ylabel('T (K)', fontsize=8)
        self.ax_temp.set_xscale('log')
        self.ax_temp.set_yscale('log')
        self.ax_temp.tick_params(labelsize=7)
        self.temp_line, = self.ax_temp.plot([], [], 'r-', linewidth=2)
        self.temp_marker, = self.ax_temp.plot([], [], 'ro', markersize=8)

        # 5. Scale factor evolution (middle-right column)
        self.ax_scale = self.fig.add_subplot(gs[1, 3])
        self.ax_scale.set_title('Scale Factor', fontweight='bold', fontsize=9)
        self.ax_scale.set_xlabel('Time (s)', fontsize=8)
        self.ax_scale.set_ylabel('a(t)', fontsize=8)
        self.ax_scale.set_xscale('log')
        self.ax_scale.set_yscale('log')
        self.ax_scale.tick_params(labelsize=7)
        self.scale_line, = self.ax_scale.plot([], [], 'b-', linewidth=2)
        self.scale_marker, = self.ax_scale.plot([], [], 'bo', markersize=8)

        # 6. Info panel (bottom-right, spans 2 columns)
        self.ax_info = self.fig.add_subplot(gs[2, 2:4])
        self.ax_info.axis('off')
        self.info_text = self.ax_info.text(
            0.05, 0.95, '',
            verticalalignment='top',
            fontfamily='monospace',
            fontsize=7
        )

        # 7. Clear bottom-left area for sliders (will be created below grid)
        ax_slider_area = self.fig.add_subplot(gs[2, 0:2])
        ax_slider_area.axis('off')

        # Create controls BELOW the grid subplots (outside plotting area)
        # Row 1: Time slider + buttons
        time_ax = plt.axes([0.10, 0.08, 0.50, 0.02])
        self.time_slider = Slider(
            time_ax, 'Time',
            0, len(self.time_milestones) - 1,
            valinit=0, valstep=1,
            color='cyan'
        )
        self.time_slider.on_changed(self.on_time_slider_change)

        # Play/Pause button
        play_ax = plt.axes([0.62, 0.08, 0.06, 0.02])
        self.play_button = Button(play_ax, 'Play')
        self.play_button.on_clicked(self.toggle_play)

        # Reset button
        reset_ax = plt.axes([0.69, 0.08, 0.06, 0.02])
        self.reset_button = Button(reset_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_simulation)

        # Row 2: X, Y, Z position sliders
        grid_size = self.universe.grid_size

        # X position slider (yellow)
        x_ax = plt.axes([0.10, 0.04, 0.20, 0.02])
        self.x_slider = Slider(
            x_ax, 'X Pos',
            0, grid_size - 1,
            valinit=self.x_pos, valstep=1,
            color='yellow'
        )
        self.x_slider.on_changed(self.on_x_slider_change)

        # Y position slider (cyan)
        y_ax = plt.axes([0.32, 0.04, 0.20, 0.02])
        self.y_slider = Slider(
            y_ax, 'Y Pos',
            0, grid_size - 1,
            valinit=self.y_pos, valstep=1,
            color='cyan'
        )
        self.y_slider.on_changed(self.on_y_slider_change)

        # Z position slider (lime)
        z_ax = plt.axes([0.54, 0.04, 0.20, 0.02])
        self.z_slider = Slider(
            z_ax, 'Z Depth',
            0, grid_size - 1,
            valinit=self.z_pos, valstep=1,
            color='lime'
        )
        self.z_slider.on_changed(self.on_z_slider_change)

        # Initialize density field images for all three views
        # Use 'seismic' colormap: blue=underdense (voids), white=average, red=overdense (structures)
        vmin, vmax = 0.9999, 1.0001  # Start with tight range to see initial perturbations

        # Main XY view (top-down at current Z slice)
        self.density_img = self.ax_density.imshow(
            self.universe.density_field[:, :, self.z_pos],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, grid_size, 0, grid_size]
        )

        # Add crosshairs to XY view showing where XZ and YZ slices are taken
        self.vline = self.ax_density.axvline(self.x_pos, color='yellow', linewidth=1,
                                             linestyle='--', alpha=0.6)
        self.hline = self.ax_density.axhline(self.y_pos, color='cyan', linewidth=1,
                                             linestyle='--', alpha=0.6)

        # XZ side view (at current Y position)
        self.xz_img = self.ax_xz.imshow(
            self.universe.density_field[:, self.y_pos, :],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, grid_size, 0, grid_size],
            aspect='auto'
        )

        # YZ front view (at current X position)
        self.yz_img = self.ax_yz.imshow(
            self.universe.density_field[self.x_pos, :, :],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, grid_size, 0, grid_size],
            aspect='auto'
        )

        # Colorbar for main density field
        cbar = plt.colorbar(self.density_img, ax=self.ax_density, fraction=0.046)
        cbar.set_label('Density: 1 + δρ/ρ (blue=voids, red=overdense)', fontsize=8)

        # History arrays for plotting
        self.history_time = []
        self.history_temp = []
        self.history_scale = []

    def on_time_slider_change(self, val):
        """Handle time slider changes."""
        new_frame = int(val)
        if new_frame != self.current_frame:
            self.current_frame = new_frame
            self.update_frame(self.current_frame)
            self.fig.canvas.draw_idle()  # Force figure redraw

    def on_x_slider_change(self, val):
        """Handle X position slider changes."""
        self.x_pos = int(val)
        # Update YZ view (changes with X position)
        self.yz_img.set_data(self.universe.density_field[self.x_pos, :, :])
        # Update crosshair on XY view
        self.vline.set_xdata([self.x_pos, self.x_pos])
        self.fig.canvas.draw_idle()

    def on_y_slider_change(self, val):
        """Handle Y position slider changes."""
        self.y_pos = int(val)
        # Update XZ view (changes with Y position)
        self.xz_img.set_data(self.universe.density_field[:, self.y_pos, :])
        # Update crosshair on XY view
        self.hline.set_ydata([self.y_pos, self.y_pos])
        self.fig.canvas.draw_idle()

    def on_z_slider_change(self, val):
        """Handle Z depth slider changes."""
        self.z_pos = int(val)
        # Update XY view (changes with Z position)
        density_contrast = self.universe.density_field[:, :, self.z_pos] - 1.0
        density_display = 1.0 + density_contrast
        self.density_img.set_data(density_display)
        # Update title
        self.ax_density.set_title(
            f'XY View (Top-Down) - Z={self.z_pos}/{self.universe.grid_size-1}',
            fontweight='bold', fontsize=10
        )
        self.fig.canvas.draw_idle()

    def toggle_play(self, event):
        """Toggle play/pause."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.label.set_text('Pause')
        else:
            self.play_button.label.set_text('Play')

    def reset_simulation(self, event):
        """Reset to beginning."""
        self.current_frame = 0
        # Temporarily disable events to prevent callback loop
        self.time_slider.eventson = False
        self.time_slider.set_val(0)
        self.time_slider.eventson = True
        self.history_time = []
        self.history_temp = []
        self.history_scale = []

        # Reinitialize universe
        self.universe = Universe(self.config)
        self.update_frame(0)

    def update_frame(self, frame):
        """Update visualization to specific frame."""
        # Get target time
        target_time = self.time_milestones[frame]

        # Check if we need to go backwards (reset universe)
        if self.universe.current_time > target_time:
            print(f"Resetting universe (was at {self.universe.current_time:.2e}s, going to {target_time:.2e}s)")
            self.universe = Universe(self.config)

        # Evolve universe to this time
        state = self.universe.run_to_time(target_time)

        # Debug: print current state
        delta_rms = np.std(self.universe.density_field - 1.0)
        delta_max = np.max(self.universe.density_field - 1.0)
        print(f"Frame {frame}: t={target_time/(31557600*1e6):.2f} Myr, δ_rms={delta_rms:.3e}, δ_max={delta_max:.3e}")

        # Update history
        self.history_time.append(state.time)
        self.history_temp.append(state.temperature)
        self.history_scale.append(state.scale_factor)

        # Update density field visualization for all three views
        # Normalize for visualization (show contrast)
        density_contrast = self.universe.density_field - 1.0
        density_display = 1.0 + density_contrast

        # Adaptive color scale based on perturbation amplitude
        max_contrast = np.max(np.abs(density_contrast))

        # Update XY view (main view at current Z slice)
        xy_slice = density_display[:, :, self.z_pos]
        self.density_img.set_data(xy_slice)
        self.density_img.set_clim(
            1.0 - max_contrast,
            1.0 + max_contrast
        )

        # Update XZ view (side view at current Y position)
        xz_slice = density_display[:, self.y_pos, :]
        self.xz_img.set_data(xz_slice)
        self.xz_img.set_clim(
            1.0 - max_contrast,
            1.0 + max_contrast
        )

        # Update YZ view (front view at current X position)
        yz_slice = density_display[self.x_pos, :, :]
        self.yz_img.set_data(yz_slice)
        self.yz_img.set_clim(
            1.0 - max_contrast,
            1.0 + max_contrast
        )

        # Update temperature plot
        if len(self.history_time) > 1:
            self.temp_line.set_data(self.history_time, self.history_temp)
            self.temp_marker.set_data([state.time], [state.temperature])
            self.ax_temp.relim()
            self.ax_temp.autoscale_view()

        # Update scale factor plot
        if len(self.history_time) > 1:
            self.scale_line.set_data(self.history_time, self.history_scale)
            self.scale_marker.set_data([state.time], [state.scale_factor])
            self.ax_scale.relim()
            self.ax_scale.autoscale_view()

        # Update info panel
        info_str = self.format_info(state)
        self.info_text.set_text(info_str)

        # Update title with current epoch
        self.ax_density.set_title(
            f'Matter Density Field - {state.epoch} Epoch (Red=Structure, Blue=Voids)',
            fontweight='bold', fontsize=10
        )

        return [self.density_img, self.temp_line, self.temp_marker,
                self.scale_line, self.scale_marker, self.info_text]

    def format_info(self, state) -> str:
        """Format current state info for display."""
        # Time formatting with better scales
        if state.time < 1e-6:
            time_str = f"{state.time*1e9:.2e} ns"
        elif state.time < 1:
            time_str = f"{state.time*1e6:.2e} μs"
        elif state.time < 3600:
            time_str = f"{state.time:.2e} s"
        elif state.time < 86400:
            time_str = f"{state.time/3600:.2e} hr"
        elif state.time < 31557600 * 1e6:  # < 1 million years
            time_str = f"{state.time/31557600:.2e} yr"
        elif state.time < 31557600 * 1e9:  # < 1 billion years
            time_str = f"{state.time/(31557600*1e6):.2f} Myr"
        else:
            time_str = f"{state.time/(31557600*1e9):.2f} Gyr"

        # Temperature formatting
        if state.temperature > 1e20:
            temp_str = f"{state.temperature:.2e} K"
        elif state.temperature > 1e9:
            temp_str = f"{state.temperature/1e9:.2f} GK"
        elif state.temperature > 1e6:
            temp_str = f"{state.temperature/1e6:.2f} MK"
        else:
            temp_str = f"{state.temperature:.2f} K"

        # Density perturbation amplitude and structure stats
        delta_rho = np.std(self.universe.density_field - 1.0)
        delta_max = np.max(self.universe.density_field - 1.0)
        delta_min = np.min(self.universe.density_field - 1.0)

        # Structure formation status
        if delta_rho < 1e-4:
            structure_status = "Linear (tiny fluctuations)"
        elif delta_rho < 0.1:
            structure_status = "Quasi-linear (growing)"
        elif delta_rho < 1.0:
            structure_status = "Non-linear onset"
        else:
            structure_status = "COLLAPSE! Structures forming"

        info = f"""
╔═══════════════════════════════╗
║  UNIVERSE STATE               ║
╚═══════════════════════════════╝

⏱️  Time:           {time_str}
🌡️  Temperature:    {temp_str}
📏 Scale Factor:   {state.scale_factor:.3e}
🌊 Hubble:         {state.hubble:.3e} s⁻¹
🌌 Epoch:          {state.epoch}

╔═══════════════════════════════╗
║  ENERGY DENSITIES             ║
╚═══════════════════════════════╝

⚫ Matter:         {state.rho_matter:.3e} kg/m³
🔴 Radiation:      {state.rho_radiation:.3e} kg/m³
🔵 Dark Energy:    {state.rho_dark_energy:.3e} kg/m³

╔═══════════════════════════════╗
║  STRUCTURE FORMATION          ║
╚═══════════════════════════════╝

🌌 δρ/ρ (RMS):     {delta_rho:.3e}
📈 δ_max:          {delta_max:.3e}
📉 δ_min:          {delta_min:.3e}
🏗️  Status:         {structure_status}
"""

        # Add nucleosynthesis info if available
        if state.H_fraction is not None:
            info += f"""
╔═══════════════════════════════╗
║  ABUNDANCES                   ║
╚═══════════════════════════════╝

   Hydrogen:       {state.H_fraction*100:.2f}%
   Helium-4:       {state.He_fraction*100:.2f}%
"""

        return info

    def play_step(self):
        """Advance one frame when playing."""
        if self.is_playing and self.current_frame < len(self.time_milestones) - 1:
            self.current_frame += 1
            # Temporarily disable events to prevent callback loop
            self.time_slider.eventson = False
            self.time_slider.set_val(self.current_frame)
            self.time_slider.eventson = True
            self.update_frame(self.current_frame)
            self.fig.canvas.draw_idle()

    def run(self):
        """Start interactive simulation."""
        print("\n" + "="*70)
        print("🎮 INTERACTIVE BIG BANG SIMULATOR")
        print("="*70)
        print("\nControls:")
        print("  • Slider: Jump to specific time in cosmic history")
        print("  • Play/Pause: Start/stop automatic evolution")
        print("  • Reset: Return to beginning (Planck epoch)")
        print("\nWatch as:")
        print("  • Temperature drops as universe expands")
        print("  • Matter density perturbations grow")
        print("  • Primordial structure forms from quantum fluctuations")
        print("="*70 + "\n")

        # Initialize display with frame 0
        self.update_frame(0)

        # Create timer for play button (event-driven, not continuous)
        self.timer = self.fig.canvas.new_timer(interval=100)  # 100ms per step
        self.timer.add_callback(self.play_step)
        self.timer.start()

        # Check if running in headless mode (cloud/server)
        if matplotlib.get_backend() == 'Agg':
            print("\n🔬 Running in non-interactive mode (cloud/server)")
            print("📊 Simulating 100 frames and saving outputs...")

            # Run simulation for 100 frames
            for frame_idx in range(100):
                self.update_frame(frame_idx)
                if frame_idx % 10 == 0:
                    print(f"Frame {frame_idx}/100")

            # Save final state
            output_dir = '/tmp/big-bang-output'
            os.makedirs(output_dir, exist_ok=True)
            output_path = f'{output_dir}/simulation_final.png'
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"✅ Saved final state to {output_path}")
            print("🎉 Simulation complete!")
        else:
            plt.show()


def main():
    """Run interactive simulator."""
    # Get config path
    config_path = os.path.join(
        os.path.dirname(__file__), '..', '..',
        'config', 'cosmology_config.yaml'
    )

    # Create and run simulator
    simulator = InteractiveBigBangSimulator(config_path)
    simulator.run()


if __name__ == "__main__":
    main()
