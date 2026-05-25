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
