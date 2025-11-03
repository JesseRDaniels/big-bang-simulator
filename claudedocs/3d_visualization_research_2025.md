# 3D Visualization Research for Big Bang Simulator
**Research Date:** November 3, 2025
**Conducted by:** Claude Code (SuperClaude Research Mode)
**Context:** Evaluating 3D visualization alternatives for cosmological structure formation

---

## Executive Summary

After comprehensive analysis of 5 Python 3D visualization libraries, I recommend a **hybrid approach** rather than full 3D rendering for your Big Bang simulator:

**🏆 Primary Recommendation:** Enhanced 2D visualization (multiple slice views)
**🚀 Best 3D Option (if needed):** VisPy (GPU-accelerated, real-time capable)
**⚠️ Full 3D Grid Concern:** 256³ = 17M cells creates rendering challenges, not memory issues

**Key Finding:** Your current 2D visualization is working perfectly. Enhancing it with orthogonal views provides 3D spatial understanding without the complexity and performance costs of true volume rendering.

---

## Library Comparison Matrix

| Library | Performance | Real-Time | Installation | Integration | Scientific | Verdict |
|---------|------------|-----------|--------------|-------------|------------|---------|
| **matplotlib 3D** | ⭐ Poor | ❌ No | ⭐⭐⭐⭐⭐ Trivial | ⭐⭐⭐⭐⭐ Native | ⚠️ Basic | **Avoid** |
| **PyVista** | ⭐⭐⭐ Good | ⚠️ Limited | ⭐⭐⭐⭐ Easy | ⚠️ Separate | ⭐⭐⭐⭐⭐ Excellent | **Good** |
| **VisPy** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Yes | ⭐⭐⭐⭐ Easy | ⚠️ Separate | ⭐⭐⭐⭐⭐ Excellent | **Best 3D** |
| **Mayavi** | ⭐⭐⭐ Good | ⚠️ Limited | ⚠️ Complex | ⚠️ Difficult | ⭐⭐⭐⭐ Good | Legacy |
| **Plotly** | ⭐⭐ Fair | ⚠️ Limited | ⭐⭐⭐⭐ Easy | ⚠️ Separate | ⚠️ Basic | Web-focused |

---

## Detailed Library Analysis

### 1. matplotlib 3D (mplot3d)
**Status:** ❌ **NOT Recommended for Volume Rendering**

#### Capabilities
- Basic 3D scatter, surface, and wireframe plots
- Software-only rendering (CPU-based)
- Limited interactivity (rotation, zoom)
- Part of standard matplotlib installation

#### Performance Characteristics
- **Rotation Speed:** Extremely slow, "laggy" even with 6,500 points
- **Resource Usage:** 1-2 GB RAM, CPU redlining reported
- **Parallelization:** None (single CPU core)
- **Real-time Updates:** Not designed for animations
- **Hardware Acceleration:** None

#### Technical Limitations (2024 Research)
From community consensus:
- "matplotlib is not designed for speedy interactive plotting, especially in 3D"
- "mplot3d is extremely slow because it uses software rendering"
- "When rotating points, only one CPU is used - no parallelization"
- "The plot does not respond correctly to pan controls from the mouse"

#### Use Cases
✅ **Good for:** Static 3D plots, presentation figures, simple demonstrations
❌ **Bad for:** Real-time interaction, large datasets, volume rendering, animations

#### Verdict
**Keep for your current 2D visualization, avoid for any 3D volume rendering.**

---

### 2. PyVista
**Status:** ✅ **Recommended - Best Balance**

#### Capabilities
- Modern Pythonic interface to VTK (Visualization Toolkit)
- Dedicated volume rendering support (`add_volume()`)
- Supports uniform grids, unstructured grids, point clouds
- 3D mesh analysis and manipulation
- Scientific visualization focus

#### Performance Characteristics
- **Rendering Engine:** VTK (C++ with Python bindings)
- **Hardware Acceleration:** GPU-accelerated via VTK
- **Grid Support:** ImageData (uniform), UnstructuredGrid
- **Volume Rendering:** Built-in with transfer functions
- **Community:** 2000+ dependent projects (2024)

#### Installation
```bash
pip install pyvista
```

**Dependencies:** vtk, numpy, matplotlib (for colormaps)
**Installation Complexity:** ⭐⭐⭐⭐ Easy (pure Python + VTK wheels)

#### Performance Benchmarks (from research)
- **Large Dataset Warning:** 13 minutes in PyVista vs 24 seconds in ParaView (7GB dataset)
- **Grid Type Matters:** UniformGrid significantly faster than StructuredGrid
- **GPU vs CPU:** "Using GPU as renderer results in smooth plotting"
- **Real-time Slices:** Limited - identified as weakness in 2024 geophysics research

#### Code Example
```python
import pyvista as pv
import numpy as np

# Create uniform grid from your density field
grid = pv.ImageData(dimensions=(256, 256, 256))
grid.point_data['density'] = density_field.ravel(order='F')

# Create plotter
plotter = pv.Plotter()
plotter.add_volume(
    grid,
    cmap='seismic',  # Your current colormap
    opacity='linear',  # Opacity transfer function
    shade=False
)

# Add camera controls
plotter.camera_position = 'xy'
plotter.show()
```

#### Integration Strategy
- **Separate Window:** PyVista uses VTK render window (not matplotlib)
- **State Sync:** Can share Universe object between matplotlib and PyVista windows
- **Update Pattern:** Call `plotter.update()` when density field changes
- **Event Loop:** Independent from matplotlib Timer

#### User Feedback (2024)
- "PyVista is truly the 3D equivalent of Matplotlib"
- "Using PyVista as a supporting module is really easy for external projects"
- "I became a big fan of PyVista"
- Developer: "I found [Mayavi] cumbersome and not intuitive"

#### Use Cases
✅ **Good for:** Scientific volume rendering, mesh analysis, educational simulations
⚠️ **Consider:** Performance on large grids, separate window requirement

#### Verdict
**Best documented, most Pythonic, good balance of capability and usability. Choose this if you want quality 3D with excellent documentation.**

---

### 3. VisPy
**Status:** ⭐ **Best Performance - GPU-Accelerated**

#### Capabilities
- High-performance OpenGL-based rendering
- Direct GPU access for maximum speed
- Multiple volume rendering methods:
  - **MIP (Maximum Intensity Projection):** Brightest voxels along view ray
  - **Attenuated MIP:** MIP with absorption
  - **Additive:** Voxel colors added along ray
  - **Isosurface:** Surface rendering with lighting
  - **Average:** Average intensity projection
- Real-time interaction with millions of points

#### Performance Characteristics
- **Rendering Engine:** Direct OpenGL (via pyglet/PyQt/GLFW backends)
- **Hardware Acceleration:** ⭐⭐⭐⭐⭐ Full GPU utilization
- **Real-time Capability:** "Millions of points at interactive frame rates"
- **Optimization:** Adjustable ray stepping for quality/speed trade-off

#### Installation
```bash
pip install vispy
```

**Dependencies:** numpy, OpenGL-capable backend (pyglet/PyQt5/PyQt6/PySide2/PySide6)
**Installation Complexity:** ⭐⭐⭐⭐ Easy (but requires OpenGL drivers)

#### Performance Tuning
```python
# Increase step size for better performance
volume = scene.visuals.Volume(
    data,
    relative_step_size=1.5,  # Default 0.8, increase for speed
    method='mip'  # Fast maximum intensity projection
)
```

#### Code Example
```python
import vispy
from vispy import scene
import numpy as np

# Create canvas
canvas = scene.SceneCanvas(keys='interactive', bgcolor='black')
view = canvas.central_widget.add_view()

# Create volume visual
volume = scene.visuals.Volume(
    density_field,  # Your 256x256x256 array
    parent=view.scene,
    cmap='seismic',  # Your current colormap
    method='mip',  # Maximum intensity projection
    relative_step_size=0.8  # Quality vs speed
)

# Setup camera
camera = scene.cameras.TurntableCamera(parent=view.scene, fov=60)
view.camera = camera

# Show
canvas.show()
vispy.app.run()
```

#### Advanced Features
- **Texture Optimization:** 32-bit float data scaled on GPU (no CPU copy)
- **Fast Color Updates:** GPU-side scaling allows dynamic color limits
- **Multiple Backends:** Choice of Qt, glfw, pyglet, SDL2
- **Interactive Controls:** Built-in rotation, zoom, pan

#### Technical Specifications
From official documentation:
- "Leverages computational power of modern GPUs through OpenGL"
- "Display very large datasets" at interactive rates
- Texture format specification enables "faster color limit changes"

#### Integration Strategy
- **Separate Process:** Best run as independent visualization window
- **State Sync:** Use multiprocessing or file-based state sharing
- **Update Pattern:** Reload volume data when density field changes
- **Event Loop:** vispy.app.run() (independent event system)

#### Use Cases
✅ **Good for:** Real-time large datasets, GPU-accelerated rendering, maximum performance
⚠️ **Consider:** Separate event loop, learning curve, OpenGL dependency

#### Verdict
**Choose this if performance and real-time interaction are your top priorities. Best raw capability for large 3D grids.**

---

### 4. Mayavi
**Status:** ⚠️ **Legacy Option - Declining Use**

#### Historical Context
- Mature scientific visualization library (2000s-2010s)
- Built on VTK (like PyVista)
- High-level API for 3D visualization
- Widely used in academic settings

#### Current Status (2024)
Community moving away from Mayavi to PyVista:
- "Mayavi2 commands were difficult to understand"
- "Cumbersome, its documentation lacking"
- "This became even more obvious when I finally found PyVista"

#### Technical Limitations
- **Installation:** Complex dependency chain, Qt binding issues
- **Documentation:** Inconsistent and incomplete
- **Performance:** "Slow for very large datasets"
- **File Formats:** "Doesn't support parallel file formats"
- **API Design:** Less intuitive than PyVista

#### Verdict
**PyVista supersedes Mayavi for new projects. Only use if maintaining legacy code.**

---

### 5. Plotly
**Status:** ⚠️ **Web-Focused, Limited Scientific Use**

#### Capabilities
- Interactive web-based visualizations
- 40+ chart types including 3D scatter, surface, mesh
- JavaScript-based rendering (plotly.js)
- HTML export for presentations
- Jupyter notebook integration

#### Performance Characteristics
- **Rendering:** Browser-based (WebGL if available)
- **Interactivity:** "Basic real-time interactive features" (rotation, zoom)
- **2D Slices:** Does not support real-time slice interaction (2024 limitation)
- **Large Grids:** Performance degrades with 3D volumes

#### Installation
```bash
pip install plotly
```

**Installation Complexity:** ⭐⭐⭐⭐ Very easy

#### Use Cases
✅ **Good for:** Business dashboards, web presentations, interactive reports
❌ **Bad for:** Scientific volume rendering, real-time large datasets

#### Verdict
**Better for presentations than scientific visualization. Not optimized for cosmological density fields.**

---

## Computational Feasibility Analysis

### Memory Requirements

#### Current Implementation (2D)
```
256 × 256 × 8 bytes (float64) = 524,288 bytes = 0.5 MB
```

#### Proposed 3D Implementation
```
256 × 256 × 256 × 8 bytes (float64) = 134,217,728 bytes = 128 MB
256 × 256 × 256 × 4 bytes (float32) = 67,108,864 bytes = 64 MB
```

**Conclusion:** ✅ **Memory is NOT the bottleneck.** 64-128 MB is trivial for modern systems.

### Rendering Performance Bottlenecks

#### The Real Challenge: Rendering Complexity

**Volume Rendering Equation:**
```
17,777,216 voxels × 30 FPS × ray sampling = billions of operations/second
```

**Why matplotlib 3D Fails:**
1. **Software Rendering:** All calculations on CPU
2. **No Parallelization:** Single-threaded
3. **Not Designed for Volumes:** Point/surface rendering only
4. **Memory Transfers:** Inefficient CPU → display path

**Why VisPy/PyVista Succeed:**
1. **GPU Acceleration:** Parallel processing on graphics hardware
2. **Optimized Algorithms:** Hardware-accelerated ray casting
3. **Efficient Transfers:** Direct GPU → display path
4. **Volumetric Focus:** Designed for 3D density fields

#### Performance Comparison (Estimated)

| Operation | matplotlib 3D | PyVista | VisPy |
|-----------|--------------|---------|-------|
| Initial render | 10-30s | 0.5-2s | 0.1-0.5s |
| Rotation (per frame) | 100-500ms | 16-50ms | 16-33ms |
| Update density field | 10-30s | 1-3s | 0.5-1s |
| Sustained FPS | <1 | 15-30 | 30-60 |

*Estimates based on 256³ grid with moderate complexity*

### Data Transfer Considerations

#### CPU → GPU Bandwidth
- **256³ float32:** 64 MB per transfer
- **PCIe 3.0:** ~12 GB/s bandwidth
- **Transfer time:** ~5ms (negligible)

#### Update Strategies
1. **Full Update:** Upload entire 256³ grid (64 MB) - acceptable for occasional updates
2. **Partial Update:** Upload changed regions only - complex, often not supported
3. **Texture Streaming:** Advanced GPUs support fast texture updates

**Conclusion:** Data transfer is manageable. Rendering complexity is the bottleneck.

---

## Recommended Implementation Strategies

### Strategy 1: Enhanced 2D (Recommended)
**Effort:** ⭐⭐ Low (2-3 hours)
**Risk:** ⭐ Very Low
**Value:** ⭐⭐⭐⭐ High

#### Approach: Multiple Orthogonal Views

Add three synchronized 2D slice views:
1. **XY Plane (current):** Top-down view of structure
2. **XZ Plane:** Side view showing vertical structure
3. **YZ Plane:** Front view showing depth structure

#### Implementation
```python
# Modify setup_figure() in simulator.py

# Current: 1 large density plot
# New: 3 smaller density plots + 1 3D position indicator

gs = self.fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

# XY view (top-down)
self.ax_xy = self.fig.add_subplot(gs[0:2, 0:2])
self.img_xy = self.ax_xy.imshow(density_field[:, :, z_slice], ...)

# XZ view (side)
self.ax_xz = self.fig.add_subplot(gs[0, 2])
self.img_xz = self.ax_xz.imshow(density_field[:, y_slice, :], ...)

# YZ view (front)
self.ax_yz = self.fig.add_subplot(gs[1, 2])
self.img_yz = self.ax_yz.imshow(density_field[x_slice, :, :], ...)

# 3D schematic (shows slice positions)
self.ax_3d_indicator = self.fig.add_subplot(gs[0:2, 3])
```

#### Advantages
- ✅ No new dependencies
- ✅ Uses your proven event-driven architecture
- ✅ Provides 3D spatial understanding
- ✅ Low computational cost
- ✅ Works on all systems (no GPU requirement)

#### Enhancements
- **Crosshairs:** Show slice intersection lines
- **Synchronized Zoom:** Pan/zoom linked across views
- **Density Contours:** Add contour lines at key density thresholds
- **Projection View:** Add maximum/average intensity projections

#### Code Estimate
~150 lines of additional code in `simulator.py`

---

### Strategy 2: VisPy Volume Rendering (Advanced)
**Effort:** ⭐⭐⭐⭐ High (1-2 days)
**Risk:** ⭐⭐⭐ Medium
**Value:** ⭐⭐⭐⭐⭐ Excellent (if you need true 3D)

#### Approach: Dual-Window System

**Window 1 (matplotlib):** Controls, plots, info panel (existing)
**Window 2 (VisPy):** 3D volume rendering synchronized with Window 1

#### Implementation Outline

**File: `src/visualization/volume_renderer.py`** (new file)
```python
import vispy
from vispy import scene
import numpy as np

class VolumeRenderer:
    def __init__(self, density_field):
        # Create canvas
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            bgcolor='black',
            size=(800, 600)
        )

        # Create view
        self.view = self.canvas.central_widget.add_view()

        # Create volume visual
        self.volume = scene.visuals.Volume(
            density_field,
            parent=self.view.scene,
            cmap='seismic',
            method='mip',  # or 'additive', 'iso', 'average'
            relative_step_size=1.0
        )

        # Setup camera
        self.camera = scene.cameras.TurntableCamera(
            parent=self.view.scene,
            fov=60,
            distance=400
        )
        self.view.camera = self.camera

    def update_density(self, new_density_field):
        """Update the volume data"""
        self.volume.set_data(new_density_field)

    def show(self):
        self.canvas.show()
        return self.canvas
```

**Modify `simulator.py`:**
```python
from visualization.volume_renderer import VolumeRenderer

class InteractiveBigBangSimulator:
    def __init__(self, config_path):
        # ... existing init ...

        # Create 3D renderer
        self.volume_renderer = VolumeRenderer(
            self.universe.density_field
        )

    def update_frame(self, frame):
        # ... existing update ...

        # Update 3D visualization
        self.volume_renderer.update_density(
            self.universe.density_field
        )
```

#### Synchronization Strategy

**Option A: Shared State (Simple)**
- Both windows reference same Universe object
- Updates propagate automatically

**Option B: Event System (Robust)**
```python
from threading import Event

class SharedState:
    def __init__(self):
        self.density_field = None
        self.updated = Event()

    def update(self, new_field):
        self.density_field = new_field
        self.updated.set()
```

#### Event Loop Integration

**Challenge:** matplotlib and VisPy both want control of event loop

**Solution 1: Separate Processes**
```python
import multiprocessing as mp

def run_vispy_window(shared_memory):
    # VisPy window in separate process
    renderer = VolumeRenderer(...)
    vispy.app.run()

# Main process: matplotlib window
p = mp.Process(target=run_vispy_window, args=(shared_mem,))
p.start()
plt.show()  # matplotlib event loop
```

**Solution 2: Threading**
```python
import threading

def vispy_thread():
    renderer = VolumeRenderer(...)
    vispy.app.run()

t = threading.Thread(target=vispy_thread, daemon=True)
t.start()
plt.show()  # Main thread for matplotlib
```

#### Advantages
- ✅ True 3D visualization
- ✅ GPU-accelerated (60 FPS possible)
- ✅ Real-time rotation/interaction
- ✅ Multiple rendering methods (MIP, iso, additive)

#### Challenges
- ⚠️ Separate event loops require coordination
- ⚠️ OpenGL dependency (system requirement)
- ⚠️ Learning curve for VisPy API
- ⚠️ Debugging complexity with multiple windows

#### Code Estimate
~300-500 lines (new file + modifications)

---

### Strategy 3: PyVista Volume Rendering (Balanced)
**Effort:** ⭐⭐⭐ Medium (4-6 hours)
**Risk:** ⭐⭐ Low-Medium
**Value:** ⭐⭐⭐⭐ High

#### Approach: Similar to VisPy but with better documentation

**File: `src/visualization/pyvista_renderer.py`**
```python
import pyvista as pv
import numpy as np

class PyVistaRenderer:
    def __init__(self, density_field):
        # Create ImageData (uniform grid)
        self.grid = pv.ImageData(dimensions=(256, 256, 256))
        self.grid.point_data['density'] = density_field.ravel(order='F')

        # Create plotter
        self.plotter = pv.Plotter(off_screen=False)
        self.volume = self.plotter.add_volume(
            self.grid,
            cmap='seismic',
            opacity='linear',
            shade=False
        )

        # Set camera
        self.plotter.camera_position = 'iso'

    def update_density(self, new_density_field):
        """Update volume data"""
        self.grid.point_data['density'] = new_density_field.ravel(order='F')
        self.plotter.update()

    def show(self):
        self.plotter.show(auto_close=False)
```

#### Integration Pattern
Same as VisPy: separate window, shared state

#### Advantages over VisPy
- ✅ Better documentation (2000+ examples)
- ✅ More Pythonic API
- ✅ Large community support
- ✅ SciPy 2024 tutorial available

#### Disadvantages vs VisPy
- ⚠️ Slower rendering (VTK overhead)
- ⚠️ Reports of 10x+ slower than native tools

#### Code Estimate
~250-400 lines (similar to VisPy approach)

---

## Alternative Enhancements (Without 3D)

### Option A: Animated Slice Sweep
**Effort:** ⭐ Very Low (1 hour)

Add a depth slider that sweeps through Z-planes:
```python
# Add Z-slice slider
z_slider_ax = plt.axes([0.15, 0.03, 0.55, 0.02])
self.z_slider = Slider(z_slider_ax, 'Z Depth', 0, 255, valinit=128)

def update_z_slice(val):
    z = int(val)
    self.density_img.set_data(self.universe.density_field[:, :, z])
    self.fig.canvas.draw_idle()

self.z_slider.on_changed(update_z_slice)
```

Shows 3D structure by animating through depth layers.

### Option B: Projection Views
**Effort:** ⭐⭐ Low (2 hours)

Add maximum/average intensity projections:
```python
# Maximum intensity projection (XY plane)
mip_xy = np.max(density_field, axis=2)

# Average intensity projection
aip_xy = np.mean(density_field, axis=2)
```

Intelligently collapses 3D → 2D showing structure.

### Option C: Contour Overlays
**Effort:** ⭐ Very Low (1 hour)

Add density threshold contours:
```python
# Add contours at specific density levels
contour_levels = [1.0, 1.1, 1.5, 2.0]
self.ax_density.contour(
    density_field[:, :, z_mid],
    levels=contour_levels,
    colors='yellow',
    linewidths=1
)
```

Shows 3D structure through level sets.

### Option D: Enhanced Colormap
**Effort:** ⭐ Very Low (30 minutes)

Multi-scale colormap for better feature detection:
```python
from matplotlib.colors import LinearSegmentedColormap

# Custom colormap: blue (voids) → white (average) → yellow (dense) → red (very dense)
colors = ['#0000ff', '#ffffff', '#ffff00', '#ff0000']
n_bins = 256
cmap = LinearSegmentedColormap.from_list('cosmic', colors, N=n_bins)
```

---

## Recommendations by Use Case

### For Education/Presentation
**Recommendation:** Enhanced 2D (Strategy 1)
- Multiple slice views provide spatial understanding
- No installation complexity for students
- Works on all hardware
- Professional appearance

### For Research/Publication
**Recommendation:** PyVista (Strategy 3)
- Scientifically accepted tool
- Publication-quality rendering
- Extensive documentation for reproducibility
- Industry standard (VTK backend)

### For Performance/Real-time
**Recommendation:** VisPy (Strategy 2)
- Maximum GPU utilization
- Supports large datasets at interactive framerates
- Best for live demonstrations
- Future-proof for larger simulations

### For Quick Improvement
**Recommendation:** Contour Overlays + Z-Slice Slider (Alternatives A+C)
- Minimal code changes
- Immediate visual improvement
- Zero new dependencies
- 2-3 hours total effort

---

## Implementation Priority Ranking

### Priority 1: Low-Hanging Fruit (Do First)
1. **Z-Slice Slider** (1 hour) - massive value for minimal effort
2. **Contour Overlays** (1 hour) - shows structure formation clearly
3. **Improved Colormap** (30 min) - better visual contrast

**Total:** ~2.5 hours, significant improvement, zero risk

### Priority 2: Enhanced 2D (If More Time)
4. **Orthogonal Views** (3 hours) - true 3D understanding
5. **Synchronized Controls** (2 hours) - professional polish

**Total:** +5 hours, professional-quality visualization

### Priority 3: True 3D (If Performance Critical)
6. **VisPy Integration** (1-2 days) - if you need GPU-accelerated 3D
7. **PyVista Integration** (4-6 hours) - if you want easier path to 3D

**Total:** Significant effort, evaluate need first

---

## Technical Specifications Summary

### System Requirements Comparison

| Library | CPU | RAM | GPU | OpenGL | Python | Platform |
|---------|-----|-----|-----|--------|--------|----------|
| matplotlib 3D | ⭐ | 2+ GB | No | No | 3.9+ | All |
| PyVista | ⭐⭐ | 512 MB | Recommended | Via VTK | 3.9+ | All |
| VisPy | ⭐ | 256 MB | Required | 2.1+ | 3.8+ | All |
| Mayavi | ⭐⭐ | 512 MB | Recommended | Via VTK | 3.8+ | All† |
| Plotly | ⭐ | 256 MB | Browser | WebGL | 3.7+ | All |

†Mayavi has Qt binding issues on some systems

### Your Current System Compatibility

✅ **Compatible:** All libraries
✅ **GPU Available:** macOS with Metal → OpenGL support
✅ **Performance:** M-series Mac excellent for GPU rendering

---

## Conclusion

**Final Recommendation:** Start with Enhanced 2D (Strategy 1)

### Reasoning:
1. **Working Foundation:** Your current 2D visualization is stable after fixing the event-driven architecture
2. **Quick Wins:** Z-slice slider + contours = 2 hours, massive improvement
3. **Low Risk:** No new dependencies, no complex integration
4. **Future-Proof:** Can always add 3D later if needed

### Migration Path:
**Phase 1 (Week 1):** Enhanced 2D with multiple views
**Phase 2 (Week 2):** Evaluate if 3D still needed
**Phase 3 (If yes):** Prototype VisPy or PyVista

### Success Metrics:
✅ Can clearly see structure formation in 3D space
✅ Interactive exploration at >30 FPS
✅ Works on standard hardware
✅ Minimal maintenance burden

---

## References & Sources

### Primary Research Sources (2024-2025):
1. PyVista Official Documentation - https://docs.pyvista.org/
2. VisPy Official Documentation - https://vispy.org/
3. matplotlib 3D Performance Issues - GitHub Issues #9301, Stack Overflow
4. PyVista Performance Benchmarks - GitHub Discussions #1697
5. SciVis Libraries Comparison - PyViz Documentation
6. Volume Rendering Techniques - yt Project Documentation
7. Scientific Python Visualization - SciPy 2024 Conference

### Key Papers:
- Sullivan & Kaszynski (2019): "PyVista: 3D plotting and mesh analysis through a streamlined interface for VTK"
- Li et al. (2025): "CIGVis: An open-source Python tool for real-time interactive [visualization]"

### Community Feedback:
- Stack Overflow: "Alternative to Mayavi for scientific 3d plotting" (1000+ views)
- PyVista GitHub Discussions: User migration stories from Mayavi
- matplotlib GitHub Issues: 3D performance limitations

---

**Research Completed:** November 3, 2025
**Next Steps:** Choose implementation strategy and proceed with enhancement

---

## Appendix A: Quick Start Code Snippets

### Enhanced 2D: Z-Slice Explorer
```python
# Add to simulator.py setup_figure()

# Z-slice slider
z_ax = plt.axes([0.15, 0.035, 0.55, 0.015])
self.z_slider = Slider(z_ax, 'Z Depth', 0, 255, valinit=128, valstep=1)

def on_z_change(val):
    z = int(val)
    # Update density view to show this Z-slice
    self.density_img.set_data(self.universe.density_field[:, :, z])
    self.ax_density.set_title(f'XY Slice at Z={z}')
    self.fig.canvas.draw_idle()

self.z_slider.on_changed(on_z_change)
```

### VisPy: Minimal Example
```python
import vispy.scene as scene
from vispy import app

# Canvas
canvas = scene.SceneCanvas(keys='interactive', bgcolor='black')
view = canvas.central_widget.add_view()

# Volume
volume = scene.visuals.Volume(
    density_field,  # 256x256x256 numpy array
    parent=view.scene,
    cmap='seismic',
    method='mip'
)

# Camera
view.camera = scene.TurntableCamera(fov=60, distance=400)

canvas.show()
app.run()
```

### PyVista: Minimal Example
```python
import pyvista as pv

# Create grid
grid = pv.ImageData(dimensions=(256, 256, 256))
grid.point_data['density'] = density_field.ravel(order='F')

# Plot
plotter = pv.Plotter()
plotter.add_volume(grid, cmap='seismic', opacity='linear')
plotter.show()
```

---

## Appendix B: Performance Optimization Tips

### For matplotlib 2D (Current System):
```python
# 1. Use blitting for faster updates
self.density_img.set_data(new_data)  # Fast
# vs
self.ax_density.clear()  # Slow - recreates everything

# 2. Reduce resolution for real-time
downsampled = density_field[::2, ::2]  # 128x128 instead of 256x256

# 3. Update only when changed
if self.current_frame != self.last_rendered_frame:
    self.update_display()
    self.last_rendered_frame = self.current_frame
```

### For VisPy:
```python
# 1. Increase step size for speed
volume = scene.visuals.Volume(
    data,
    relative_step_size=1.5  # Default 0.8, higher = faster
)

# 2. Use float32 instead of float64
density_field_32 = density_field.astype(np.float32)  # Half the memory

# 3. Enable texture optimization
volume.method = 'mip'  # Faster than 'iso' or 'additive'
```

### For PyVista:
```python
# 1. Use ImageData (fastest)
grid = pv.ImageData()  # Uniform grid
# vs
grid = pv.StructuredGrid()  # Slower for regular grids

# 2. Limit scalar range updates
plotter.add_volume(grid, clim=[0.9, 1.1])  # Fixed range = faster

# 3. Reduce quality for interaction
plotter.iren.interactor.SetDesiredUpdateRate(30)  # FPS target
```

---

**End of Report**
