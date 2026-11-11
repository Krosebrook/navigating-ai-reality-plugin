# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
COPY requirements.txt ./
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --upgrade pip && /opt/venv/bin/pip install -r requirements.txt "uvicorn[standard]>=0.30.0"

FROM python:3.11-slim AS runner
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    REALITY_LENS_STATELESS_SPEC=2025-11

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser skills ./skills
COPY --chown=appuser:appuser reality_lens_http_app.py ./reality_lens_http_app.py

USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/health', timeout=2)"

CMD ["sh", "-c", "uvicorn reality_lens_http_app:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
