FROM python:3.12-slim

WORKDIR /app
COPY game_tracker.py ui.py platforms.py taobao.py taobao_core.py /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV GT_BIND=0.0.0.0 \
    GT_PORT=8766 \
    GT_DATA_DIR=/app/data \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/data
VOLUME ["/app/data"]
EXPOSE 8766

CMD ["python3", "/app/game_tracker.py"]
