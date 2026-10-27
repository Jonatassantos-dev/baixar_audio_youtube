FROM python:3.11-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1
WORKDIR /build

COPY requirement.txt .
RUN python -m pip wheel --wheel-dir=/wheels -r requirement.txt

FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir --no-index --find-links=/wheels -r requirement.txt \
    && rm -rf /wheels

COPY main.py .
COPY src/ ./src/

RUN mkdir -p static/audios static/videos static/transcricao \
    && useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

USER appuser

CMD ["python", "main.py"]
