# Server Deployment

This project uses Docker Compose with an Nginx reverse proxy.

External port:

```bash
http://SERVER_IP:53380
```

## Directory layout on server

Keep these directories next to `docker-compose.yml`:

```text
models/   model files, mounted read-only
img/      gallery images and uploads
result/   generated outputs
configs/  model and weight config
```

The front gallery should be placed in:

```text
img/front/
```

## Start

CPU/default:

```bash
docker compose up -d --build
```

GPU:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

The GPU mode requires NVIDIA Driver and NVIDIA Container Toolkit on the server.

## Build mirrors

The Docker build defaults to Aliyun mirrors:

- Debian APT: `http://mirrors.aliyun.com/debian`
- Debian security: `http://mirrors.aliyun.com/debian-security`
- PyPI: `https://mirrors.aliyun.com/pypi/simple`

To use Tsinghua mirrors instead:

```bash
DEBIAN_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/debian \
DEBIAN_SECURITY_MIRROR=https://mirrors.tuna.tsinghua.edu.cn/debian-security \
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

To use USTC mirrors:

```bash
DEBIAN_MIRROR=https://mirrors.ustc.edu.cn/debian \
DEBIAN_SECURITY_MIRROR=https://mirrors.ustc.edu.cn/debian-security \
PIP_INDEX_URL=https://mirrors.ustc.edu.cn/pypi/simple \
PIP_TRUSTED_HOST=mirrors.ustc.edu.cn \
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

## Operations

```bash
docker compose ps
docker compose logs -f car-similarity-app
docker compose restart
docker compose down
```

## Notes

- Nginx listens on host port `53380` and proxies to Streamlit on container port `8502`.
- `models`, `img`, and `result` are not baked into the image. They are mounted from the host.
- Increase `client_max_body_size` in `deploy/nginx/default.conf` if uploads exceed 250 MB.
