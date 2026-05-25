FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ffmpeg \
        git \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

COPY app.py similarity_pipeline.py ./
COPY configs ./configs
COPY tools ./tools
COPY .streamlit ./.streamlit

RUN mkdir -p /app/models /app/img/front /app/result

EXPOSE 8502

HEALTHCHECK --interval=30s --timeout=8s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8502/_stcore/health', timeout=5)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8502", "--server.headless=true", "--server.fileWatcherType=none", "--server.maxUploadSize=200"]
