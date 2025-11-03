# Big Bang Simulator - Project Handoff

**Date**: 2025-11-03
**GitHub Repo**: https://github.com/JesseRDaniels/big-bang-simulator
**Railway URL**: https://big-bang-simulator-production.up.railway.app
**Railway Project ID**: 09824444-b1c5-4131-88a9-6972222c19b4

---

## 🚀 Quick Start on Laptop

```bash
# Clone the repository
git clone https://github.com/JesseRDaniels/big-bang-simulator.git
cd big-bang-simulator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Link to Railway (requires Railway CLI)
brew install railway  # if not installed
railway login
railway link  # Select: big-bang-simulator → production

# View current deployment logs
railway logs --service big-bang-simulator

# Test locally
streamlit run streamlit_app.py --server.port 8501
# Open browser to http://localhost:8501

# Make changes and deploy
git add .
git commit -m "Your changes"
git push origin main
railway up --service big-bang-simulator
```

---

## Current Status

### ✅ What's Working
- **Local Development**: Streamlit runs perfectly at http://localhost:8501
  - Multi-view 3D visualization (XY, XZ, YZ slices)
  - Interactive time slider (0-50 million years)
  - Real-time cosmology metrics
  - All physics engines working (Friedmann, thermodynamics, nucleosynthesis)

### ❌ Current Issue - Latest Build Logs (2025-11-03 21:53 UTC)
- **Railway Deployment**: Streamlit starts successfully but container stops immediately after

**Actual Logs**:
```
Starting Container

Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.

  You can now view your Streamlit app in your browser.

  URL: http://0.0.0.0:8501

Stopping Container
  Stopping...
```

**Analysis**:
- ✅ Streamlit server starts successfully (no errors)
- ❌ Container stops immediately with no error message
- ❓ No crash, no exception, no memory error - just clean stop

**Possible Causes**:
1. **Health check failing**: Dockerfile has health check on `/_stcore/health` but maybe timing issue?
2. **Streamlit exits after startup**: Maybe missing `--server.runOnSave=false`?
3. **Railway timeout**: Container not becoming "healthy" fast enough?
4. **Port binding issue**: Railway expects different port behavior?

## Project Structure

```
big-bang-simulator/
├── streamlit_app.py          # Main web interface (304 lines)
├── src/
│   └── simulation/
│       ├── simulator.py       # Batch script (not used for web)
│       ├── universe.py        # Core physics engine
│       ├── friedmann.py       # Expansion dynamics
│       ├── thermodynamics.py  # Temperature evolution
│       └── nucleosynthesis.py # Element formation
├── config/
│   └── cosmology_config.yaml  # Universe parameters
├── Dockerfile                 # Railway deployment config
├── railway.toml              # Railway settings
└── requirements.txt          # Python dependencies
```

## Key Files & Changes

### streamlit_app.py (lines 58-67)
```python
@st.cache_resource
def initialize_universe():
    """Initialize universe (cached to avoid recomputation)."""
    config = load_config()
    with st.spinner("🌌 Initializing universe..."):
        universe = Universe(config)
        # Run simulation to populate history
        target_time = 50e6 * 365.25 * 24 * 3600  # 50 million years
        universe.run_to_time(target_time)
    return universe
```

### Dockerfile (line 36)
```dockerfile
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### railway.toml
```toml
[deploy]
memoryGB = 2  # Allocated 2GB for universe initialization
```

## Recent Changes

1. **Commit f9a097a**: Force Railway rebuild with cache-busting comment
   - Railway was caching old Docker image
   - Added build version to force fresh build
   - Result: Streamlit now starts (progress!)

2. **Commit d002676**: Add Streamlit web interface
   - Created full interactive web app
   - Multi-view visualization with sliders
   - Real-time metrics display

3. **Commit 7406f61**: Fix matplotlib backend detection
   - Fixed MPLBACKEND env var priority
   - Prevents MacOSX import errors on Railway

## Next Steps to Debug

### Check Crash Logs
```bash
cd ~/Desktop/big-bang-simulator
railway logs --service big-bang-simulator | tail -100
```

Look for:
- Memory errors (OOM killed)
- Python exceptions during Universe initialization
- Streamlit-specific errors

### Possible Fixes

**Option A**: Reduce memory usage during initialization
```python
# In streamlit_app.py, line 64
target_time = 10e6 * 365.25 * 24 * 3600  # Reduce to 10 Myr instead of 50
```

**Option B**: Lazy initialization (don't precompute)
```python
# Only compute frames on-demand, not all upfront
universe.run_to_time(target_time)  # Remove this line
# Compute frame only when user requests it
```

**Option C**: Start with "Hello World" Streamlit
- Deploy minimal app to verify Railway works
- Then add complexity incrementally

## Railway CLI Setup

On laptop, install Railway CLI:
```bash
# Install
brew install railway

# Login
railway login

# Link to project
cd ~/Desktop/big-bang-simulator
railway link
# Select project: big-bang-simulator
# Select environment: production

# View logs
railway logs --service big-bang-simulator

# Deploy changes
git commit -am "Your changes"
railway up --service big-bang-simulator
```

## Testing Locally

```bash
cd ~/Desktop/big-bang-simulator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run streamlit_app.py --server.port 8501

# Open browser to http://localhost:8501
```

## Questions for Next Session

1. **Approach**: Debug full simulator OR start with minimal Hello World?
2. **Memory**: Is 2GB enough for 50 Myr simulation?
3. **Strategy**: Lazy loading vs precomputation?

## Contact Info

- Railway Project: https://railway.com/project/09824444-b1c5-4131-88a9-6972222c19b4
- Railway Logs: `railway logs --service big-bang-simulator`
- Local Test: http://localhost:8501

---

**Summary**: Streamlit web interface works perfectly locally. Railway deployment starts Streamlit but crashes immediately. Need to check crash logs to identify if it's memory, initialization, or config issue.
