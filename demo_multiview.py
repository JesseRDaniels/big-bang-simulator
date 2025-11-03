#!/usr/bin/env python3
"""
Quick Multi-View Demo
Shows what the enhanced 2D multi-view layout looks like without modifying the real simulator.

Run: python demo_multiview.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def generate_demo_data():
    """Generate a 3D density field with some interesting structure."""
    # Create 128x128x128 grid (smaller for demo speed)
    size = 128
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    z = np.linspace(-1, 1, size)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Create some spherical "galaxy clusters" at different positions
    clusters = [
        (0.3, 0.3, 0.3, 0.2),   # (x, y, z, radius)
        (-0.4, -0.3, 0.2, 0.15),
        (0.2, -0.4, -0.3, 0.18),
        (-0.3, 0.4, -0.2, 0.12),
    ]

    # Start with uniform density
    density = np.ones_like(X)

    # Add spherical overdensities (galaxy clusters)
    for cx, cy, cz, radius in clusters:
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2 + (Z - cz)**2)
        density += 2.0 * np.exp(-dist**2 / (2 * radius**2))

    # Add some filamentary structure (cosmic web)
    density += 0.5 * np.sin(3 * X) * np.sin(3 * Y) * np.exp(-Z**2 / 0.5)

    # Add random perturbations
    np.random.seed(42)
    density += 0.1 * np.random.randn(*density.shape)

    return density


class MultiViewDemo:
    def __init__(self, density_field):
        self.density = density_field
        self.size = density_field.shape[0]

        # Initial slice positions
        self.x_pos = self.size // 2
        self.y_pos = self.size // 2
        self.z_pos = self.size // 2

        self.setup_figure()

    def setup_figure(self):
        """Create the multi-view layout."""
        # Create figure
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('🌌 Multi-View Demo - Big Bang Simulator Concept',
                         fontsize=16, fontweight='bold')

        # Create grid layout: 3 rows x 4 columns
        gs = self.fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3,
                                   left=0.05, right=0.98, top=0.93, bottom=0.12)

        # 1. Main XY view (top-down) - LARGE, spans 2x2
        self.ax_xy = self.fig.add_subplot(gs[0:2, 0:2])
        self.ax_xy.set_title('XY View (Top-Down) - Z slice', fontweight='bold', fontsize=12)
        self.ax_xy.set_xlabel('X →')
        self.ax_xy.set_ylabel('Y →')

        # 2. XZ view (side view) - MEDIUM
        self.ax_xz = self.fig.add_subplot(gs[0, 2])
        self.ax_xz.set_title('XZ View (Side)', fontweight='bold', fontsize=10)
        self.ax_xz.set_xlabel('X →')
        self.ax_xz.set_ylabel('Z ↑')

        # 3. YZ view (front view) - MEDIUM
        self.ax_yz = self.fig.add_subplot(gs[1, 2])
        self.ax_yz.set_title('YZ View (Front)', fontweight='bold', fontsize=10)
        self.ax_yz.set_xlabel('Y →')
        self.ax_yz.set_ylabel('Z ↑')

        # 4. Info panel
        self.ax_info = self.fig.add_subplot(gs[0:2, 3])
        self.ax_info.axis('off')
        self.info_text = self.ax_info.text(
            0.05, 0.95, '',
            verticalalignment='top',
            fontfamily='monospace',
            fontsize=9
        )

        # 5. Legend/instructions
        self.ax_legend = self.fig.add_subplot(gs[2, 2:4])
        self.ax_legend.axis('off')
        legend_text = """
🎮 CONTROLS:
• X Slider: Move vertical slice plane (updates XZ view)
• Y Slider: Move horizontal slice plane (updates YZ view)
• Z Slider: Change depth layer (updates XY view)

📊 VIEWS:
• XY (main): Top-down view at current Z depth
• XZ (top right): Side view at current Y position
• YZ (mid right): Front view at current X position

🎯 CROSSHAIRS:
• Lines on XY view show where XZ and YZ slices are taken
• Intersection shows the 3D position being examined
        """
        self.ax_legend.text(0.05, 0.95, legend_text,
                           verticalalignment='top',
                           fontfamily='monospace',
                           fontsize=8)

        # Initialize images with seismic colormap (like your real simulator)
        vmin, vmax = 0.5, 3.0  # Density range for demo

        # XY view
        self.img_xy = self.ax_xy.imshow(
            self.density[:, :, self.z_pos],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, self.size, 0, self.size]
        )

        # Add crosshairs on XY view
        self.vline = self.ax_xy.axvline(self.x_pos, color='yellow', linewidth=1,
                                        linestyle='--', alpha=0.7, label='X slice')
        self.hline = self.ax_xy.axhline(self.y_pos, color='cyan', linewidth=1,
                                        linestyle='--', alpha=0.7, label='Y slice')
        self.ax_xy.legend(loc='upper right', fontsize=8)

        # XZ view
        self.img_xz = self.ax_xz.imshow(
            self.density[:, self.y_pos, :],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, self.size, 0, self.size],
            aspect='auto'
        )

        # YZ view
        self.img_yz = self.ax_yz.imshow(
            self.density[self.x_pos, :, :],
            cmap='seismic',
            interpolation='bilinear',
            origin='lower',
            vmin=vmin, vmax=vmax,
            extent=[0, self.size, 0, self.size],
            aspect='auto'
        )

        # Add colorbars
        cbar_xy = plt.colorbar(self.img_xy, ax=self.ax_xy, fraction=0.046)
        cbar_xy.set_label('Density (blue=low, red=high)', fontsize=8)

        # Create sliders
        # X position slider
        ax_x = plt.axes([0.15, 0.06, 0.25, 0.02])
        self.slider_x = Slider(ax_x, 'X Position', 0, self.size-1,
                               valinit=self.x_pos, valstep=1, color='yellow')
        self.slider_x.on_changed(self.update_x)

        # Y position slider
        ax_y = plt.axes([0.15, 0.03, 0.25, 0.02])
        self.slider_y = Slider(ax_y, 'Y Position', 0, self.size-1,
                               valinit=self.y_pos, valstep=1, color='cyan')
        self.slider_y.on_changed(self.update_y)

        # Z position slider
        ax_z = plt.axes([0.50, 0.06, 0.25, 0.02])
        self.slider_z = Slider(ax_z, 'Z Depth', 0, self.size-1,
                               valinit=self.z_pos, valstep=1, color='lime')
        self.slider_z.on_changed(self.update_z)

        # Update info
        self.update_info()

    def update_x(self, val):
        """Update X slice position."""
        self.x_pos = int(val)

        # Update YZ view (changes with X position)
        self.img_yz.set_data(self.density[self.x_pos, :, :])

        # Update crosshair on XY view
        self.vline.set_xdata([self.x_pos, self.x_pos])

        # Update info
        self.update_info()

        self.fig.canvas.draw_idle()

    def update_y(self, val):
        """Update Y slice position."""
        self.y_pos = int(val)

        # Update XZ view (changes with Y position)
        self.img_xz.set_data(self.density[:, self.y_pos, :])

        # Update crosshair on XY view
        self.hline.set_ydata([self.y_pos, self.y_pos])

        # Update info
        self.update_info()

        self.fig.canvas.draw_idle()

    def update_z(self, val):
        """Update Z slice position."""
        self.z_pos = int(val)

        # Update XY view (changes with Z position)
        self.img_xy.set_data(self.density[:, :, self.z_pos])

        # Update info
        self.update_info()

        self.fig.canvas.draw_idle()

    def update_info(self):
        """Update info panel."""
        # Get density at current position
        density_at_point = self.density[self.x_pos, self.y_pos, self.z_pos]

        # Get statistics for current XY slice
        xy_slice = self.density[:, :, self.z_pos]
        mean_density = np.mean(xy_slice)
        max_density = np.max(xy_slice)
        min_density = np.min(xy_slice)

        info = f"""
╔═══════════════════════════╗
║  3D POSITION              ║
╚═══════════════════════════╝

📍 X Position:    {self.x_pos:3d} / {self.size-1}
📍 Y Position:    {self.y_pos:3d} / {self.size-1}
📍 Z Depth:       {self.z_pos:3d} / {self.size-1}

╔═══════════════════════════╗
║  DENSITY INFO             ║
╚═══════════════════════════╝

🎯 At (X,Y,Z):    {density_at_point:.3f}
📊 XY Slice Mean: {mean_density:.3f}
📈 XY Slice Max:  {max_density:.3f}
📉 XY Slice Min:  {min_density:.3f}

╔═══════════════════════════╗
║  WHAT YOU'RE SEEING       ║
╚═══════════════════════════╝

🔴 Red regions:   Overdense
                 (matter clumps)
⚪ White regions:  Average density
🔵 Blue regions:  Underdense
                 (cosmic voids)

Yellow crosshair: X slice plane
Cyan crosshair:   Y slice plane
Intersection:     3D focus point
        """

        self.info_text.set_text(info)

    def show(self):
        """Display the figure."""
        plt.show()


def main():
    print("🌌 Generating demo 3D density field...")
    print("   (This simulates cosmic structure formation)")

    # Generate demo data
    density = generate_demo_data()

    print(f"✅ Created {density.shape} density field")
    print(f"   Density range: {density.min():.2f} to {density.max():.2f}")
    print()
    print("🎮 Opening multi-view demo window...")
    print()
    print("Try moving the sliders to explore the 3D structure!")
    print("Notice how:")
    print("  • Moving X slider updates the YZ view")
    print("  • Moving Y slider updates the XZ view")
    print("  • Moving Z slider changes the XY view depth")
    print()

    # Create and show demo
    demo = MultiViewDemo(density)
    demo.show()


if __name__ == "__main__":
    main()
