# Big Bang Simulator - Docker Container
# Optimized for Railway and Google Cloud Run
# Build: 2025-11-03-v3 (Lazy loading - fast startup)

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

# Expose Streamlit port (Railway will override with $PORT)
EXPOSE 8501

# No health check - app starts instantly with lazy loading
# Railway will monitor HTTP responses directly

# Default command: run Streamlit app
# Use Railway's PORT environment variable (fallback to 8501)
# Must use shell form with explicit /bin/sh for variable expansion
CMD ["/bin/sh", "-c", "streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true"]
