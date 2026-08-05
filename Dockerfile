# Dockerfile — Phase 4: Production
# Packages the AI Customer Support Playbook API into a portable container.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer, so Docker caches this step
# and doesn't reinstall everything just because source code changed)
#
# Install CPU-only PyTorch FIRST, from PyTorch's own CPU-only index. This
# avoids pip pulling the default GPU/CUDA build of torch (several GB of
# NVIDIA libraries we don't need, since this runs on CPU only) when
# sentence-transformers gets installed below.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/

WORKDIR /app/src

EXPOSE 8000

# Run the API with Uvicorn. --host 0.0.0.0 is required so the container
# accepts connections from outside itself, not just localhost.
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]