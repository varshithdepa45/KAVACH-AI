# KAVACH AI — backend image. Build context is the repo root.
FROM python:3.11-slim

WORKDIR /app

# Core + offline-friendly optional deps. RAG falls back to pure-python if the
# heavy vector-store libs are absent, so we keep the image lean.
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY demo-data/ /app/demo-data/
COPY generated/ /app/generated/

WORKDIR /app/backend

ENV KAVACH_MODE=airgapped \
    KAVACH_DEMO_DATA=/app/demo-data \
    KAVACH_UPLOADS=/app/demo-data/uploads \
    KAVACH_GENERATED=/app/generated \
    KAVACH_DB=/app/backend/kavach.db \
    PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
