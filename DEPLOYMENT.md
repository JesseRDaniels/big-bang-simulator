# Deployment Guide - Big Bang Simulator

## Memory Optimizations Applied ✅

The simulator has been optimized for cloud deployment:

- **Grid size**: 64³ (2 MB per field) - down from 256³ (134 MB)
- **History storage**: Statistics only (~0.02 MB per entry) - not full 3D arrays
- **Total memory**: ~100-200 MB for full simulation
- **Suitable for**: 512 MB - 1 GB RAM instances

## Option 1: Railway Deployment 🚂

Railway is the **easiest** option for quick deployment.

### Prerequisites
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login
```

### Deploy Steps
```bash
cd ~/Desktop/big-bang-simulator

# Initialize Railway project
railway init

# Link to your Railway account
railway link

# Deploy
railway up

# View logs
railway logs

# Open dashboard
railway open
```

### Railway Configuration
- **Memory**: 1 GB (512 MB minimum)
- **Cost**: ~$5-10/month for hobby plan
- **Auto-deploy**: Push to main branch auto-deploys
- **Persistent storage**: Use volumes if saving outputs

### Railway Environment Variables
Set these in Railway dashboard:
```
MPLBACKEND=Agg
PYTHONUNBUFFERED=1
```

## Option 2: Google Cloud Run ☁️

Cloud Run is **pay-per-use** - only charged when running.

### Prerequisites
```bash
# Install gcloud CLI (if not already installed)
# Download from: https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Deploy Steps

#### Method A: One-Command Deploy (Easiest)
```bash
cd ~/Desktop/big-bang-simulator

# Build and deploy in one command
gcloud run deploy big-bang-simulator \
  --source . \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --no-allow-unauthenticated
```

#### Method B: Container Registry (More Control)
```bash
# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Set project ID
PROJECT_ID=$(gcloud config get-value project)

# Build container
docker build -t gcr.io/$PROJECT_ID/big-bang-simulator:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/big-bang-simulator:latest

# Deploy to Cloud Run
gcloud run deploy big-bang-simulator \
  --image gcr.io/$PROJECT_ID/big-bang-simulator:latest \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 3600 \
  --max-instances 1 \
  --no-allow-unauthenticated
```

### Cloud Run Configuration
- **Memory**: 1 GB
- **CPU**: 1 vCPU
- **Timeout**: 3600s (1 hour)
- **Cost**: ~$0.05-0.20 per run (pay-per-use)
- **Scaling**: Auto-scales to 0 when not in use (no idle costs!)

### View Logs
```bash
# Stream logs in real-time
gcloud run logs tail big-bang-simulator --region us-central1

# View in Cloud Console
gcloud run services describe big-bang-simulator --region us-central1
```

## Option 3: Google Compute Engine VM

For **persistent compute** with more control.

### Create VM
```bash
# Create compute instance (1 GB RAM)
gcloud compute instances create big-bang-simulator \
  --machine-type=e2-small \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --zone=us-central1-a

# SSH into instance
gcloud compute ssh big-bang-simulator --zone=us-central1-a
```

### Setup on VM
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv git

# Clone/copy your project
git clone <your-repo> big-bang-simulator
cd big-bang-simulator

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run simulator
python src/simulation/simulator.py
```

### GCE Configuration
- **Machine type**: e2-small (2 vCPU, 2 GB RAM)
- **Cost**: ~$13/month (always on)
- **Suitable for**: Long-running simulations, development

## Comparison

| Feature | Railway | Cloud Run | Compute Engine |
|---------|---------|-----------|----------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | ~$5-10/mo | $0.05-0.20/run | ~$13/mo |
| **Setup Time** | 2 minutes | 5 minutes | 10 minutes |
| **Auto-scaling** | ✅ | ✅ | ❌ |
| **Pay-per-use** | ❌ | ✅ | ❌ |
| **Persistent** | ✅ | ❌ | ✅ |

## Recommendation

**For quick testing**: Use Railway (easiest, fastest)
**For production**: Use Cloud Run (cheapest, auto-scales)
**For development**: Use Compute Engine (most control)

## Saving Outputs

### Railway
```bash
# Add volume in Railway dashboard
# Mount at /app/output
# Access via Railway CLI: railway run ls output/
```

### Cloud Run
```bash
# Use Cloud Storage for outputs
# Add to requirements.txt: google-cloud-storage
# Save outputs to GCS bucket
```

### Compute Engine
```bash
# Direct file system access
# Copy outputs via gcloud:
gcloud compute scp big-bang-simulator:~/output/* ./local-output/
```

## Monitoring

### Railway
```bash
railway logs --tail
```

### Google Cloud
```bash
# Cloud Run
gcloud run logs tail big-bang-simulator --region us-central1

# Compute Engine
gcloud compute ssh big-bang-simulator --command "tail -f simulation.log"
```

## Troubleshooting

### Out of Memory
- Reduce grid size in config: `structure.grid_size: 32`
- Increase memory: `--memory 2Gi`

### Timeout
- Increase timeout: `--timeout 7200` (Cloud Run max: 3600s)
- Use Compute Engine for longer runs

### Build Failures
```bash
# Test Docker locally first
docker build -t big-bang-sim:test .
docker run --rm big-bang-sim:test
```

## Next Steps

1. Choose your platform (Railway recommended for simplicity)
2. Follow the deploy steps above
3. Monitor logs for successful run
4. Access outputs via platform-specific methods
5. Scale up memory/CPU if needed

## Cost Estimates

**Railway**: $5-10/month (hobby plan)
**Cloud Run**: $0.05-0.20 per simulation run (1 hour)
**Compute Engine**: $13/month (e2-small, always on)

For occasional use (few times per week): **Cloud Run is cheapest**
For frequent use (daily): **Railway is simplest**
For 24/7 access: **Compute Engine is best**
