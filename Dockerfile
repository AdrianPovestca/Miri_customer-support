# Dockerfile — Phase 4: Production
# Packages the AI Customer Support Playbook API into a portable container.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer, so Docker caches this step
# and doesn't reinstall everything just because source code changed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/
COPY knowledge_base/ ./knowledge_base/

WORKDIR /app/src

EXPOSE 8000

# Run the API with Uvicorn. --host 0.0.0.0 is required so the container
# accepts connections from outside itself, not just localhost.
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]