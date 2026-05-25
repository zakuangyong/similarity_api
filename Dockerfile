FROM python:3.11-slim-bookworm

ARG DEBIAN_MIRROR=http://mirrors.aliyun.com/debian
ARG DEBIAN_SECURITY_MIRROR=http://mirrors.aliyun.com/debian-security
ARG PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ARG PIP_TRUSTED_HOST=mirrors.aliyun.com
ARG TORCH_VERSION=2.8.0+cu128
ARG TORCHVISION_VERSION=0.23.0+cu128
ARG TORCH_INDEX_URL=https://mirrors.aliyun.com/pytorch-wheels/cu128

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST} \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

RUN set -eux; \
    sed -i \
        -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
        -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
        /etc/apt/sources.list.d/debian.sources; \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt constraints-cu128.txt ./
RUN python -m pip config set global.index-url "${PIP_INDEX_URL}" \
    && python -m pip config set global.trusted-host "${PIP_TRUSTED_HOST}" \
    && python -m pip config set global.timeout "120" \
    && python -m pip config set global.retries "10" \
    && python -m pip install --upgrade pip setuptools wheel \
        --index-url "${PIP_INDEX_URL}" \
        --trusted-host "${PIP_TRUSTED_HOST}"

RUN pip install \
        "torch==${TORCH_VERSION}" \
        "torchvision==${TORCHVISION_VERSION}" \
        --index-url "${PIP_INDEX_URL}" \
        --find-links "${TORCH_INDEX_URL}" \
        --trusted-host "${PIP_TRUSTED_HOST}" \
    && python -c "import torch; print('build torch cuda:', torch.version.cuda); assert torch.version.cuda == '12.8', torch.version.cuda"

RUN pip install -r requirements.txt \
        -c constraints-cu128.txt \
        --index-url "${PIP_INDEX_URL}" \
        --find-links "${TORCH_INDEX_URL}" \
        --trusted-host "${PIP_TRUSTED_HOST}" \
    && python -c "import torch; print('final torch cuda:', torch.version.cuda); assert torch.version.cuda == '12.8', torch.version.cuda" \
    && python -m pip check

COPY app.py similarity_pipeline.py ./
COPY configs ./configs
COPY tools ./tools
COPY .streamlit ./.streamlit

RUN mkdir -p /app/models /app/img/front /app/result

EXPOSE 8502

HEALTHCHECK --interval=30s --timeout=8s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8502/_stcore/health', timeout=5)"

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8502", "--server.headless=true", "--server.fileWatcherType=none", "--server.maxUploadSize=200"]
