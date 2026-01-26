# Docker Deployment Guide

## Overview

Yennefer's entire stack is containerized and available via GitHub Container Registry. This guide covers deployment, configuration, and troubleshooting.

---

## Quick Start

### One-Command Setup

```bash
git clone https://github.com/Genesis-Conductor-Engine/Yennefer.git
cd Yennefer
./scripts/docker-quickstart.sh
```

This will:
1. Check Docker/Docker Compose installation
2. Create `.env` file if missing
3. Build all images
4. Start all 8 services
5. Show service status and endpoints

---

## Pull Pre-Built Images

All images are automatically built on each push to `main` via GitHub Actions.

### Available Images

| Image | Description | Pull Command |
|-------|-------------|--------------|
| `diamond-vault` | Quantum operations dashboard | `docker pull ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest` |
| `a2a-handoff` | Agent-to-agent handoff server | `docker pull ghcr.io/genesis-conductor-engine/yennefer/a2a-handoff:latest` |
| `soul-api` | Yennefer consciousness API | `docker pull ghcr.io/genesis-conductor-engine/yennefer/soul-api:latest` |
| `qmem-gateway` | Memory benchmarking gateway | `docker pull ghcr.io/genesis-conductor-engine/yennefer/qmem-gateway:latest` |
| `qmcp-bridge` | Blockchain<->GPU bridge | `docker pull ghcr.io/genesis-conductor-engine/yennefer/qmcp-bridge:latest` |
| `process-guardian` | Service monitor & recovery | `docker pull ghcr.io/genesis-conductor-engine/yennefer/process-guardian:latest` |
| `yennefer-daemon` | Core consciousness engine | `docker pull ghcr.io/genesis-conductor-engine/yennefer/yennefer-daemon:latest` |

### Pull All Images

```bash
for service in diamond-vault a2a-handoff soul-api qmem-gateway qmcp-bridge process-guardian yennefer-daemon; do
  docker pull ghcr.io/genesis-conductor-engine/yennefer/$service:latest
done
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Core Configuration
NODE_ENV=production
COMPUTE_MODE=dual              # dual | local | remote
MONITORING_MODE=simulated      # real | simulated (use simulated if no GPU)
ALWAYS_ON=true

# Blockchain (optional - for blockchain features)
ETH_PRIVATE_KEY=your_private_key_here
ALCHEMY_API_KEY=your_alchemy_key_here
BASE_MAINNET_RPC=https://mainnet.base.org

# Cloudflare Tunnel (optional - for public access)
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
```

### Cloudflare Tunnel Setup (Optional)

For public access to your Yennefer instance:

1. Create `.cloudflared/config.yml`:

```yaml
tunnel: your-tunnel-id
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: vault.yourdomain.com
    service: http://diamond-vault:8100
  - hostname: api.yourdomain.com
    service: http://soul-api:8088
  - hostname: a2a.yourdomain.com
    service: http://a2a-handoff:8200
  - service: http_status:404
```

2. Add credentials file to `.cloudflared/credentials.json`

3. Uncomment `cloudflared` service in `docker-compose.yennefer.yml`

---

## Usage

### Start All Services

```bash
docker compose -f docker-compose.yennefer.yml up -d
```

### View Logs

```bash
# All services
docker compose -f docker-compose.yennefer.yml logs -f

# Specific service
docker compose -f docker-compose.yennefer.yml logs -f diamond-vault
```

### Stop Services

```bash
docker compose -f docker-compose.yennefer.yml down
```

### Restart a Service

```bash
docker compose -f docker-compose.yennefer.yml restart diamond-vault
```

### Check Service Health

```bash
# Status of all containers
docker compose -f docker-compose.yennefer.yml ps

# Healthcheck for specific service
docker inspect yennefer-diamond-vault | jq '.[0].State.Health'
```

---

## API Endpoints

Once running, access these endpoints:

| Service | Endpoint | Description |
|---------|----------|-------------|
| Diamond Vault | `http://localhost:8100` | Dashboard & quantum operations |
| Diamond Vault API | `http://localhost:8100/api/yennefer` | Yennefer status |
| Quantum Ops | `http://localhost:8100/api/quantum/<operation>` | Execute quantum operations |
| A2A Handoff | `http://localhost:8200` | Agent handoff server |
| A2A Health | `http://localhost:8200/health` | Health check |
| Soul API | `http://localhost:8088/api/soul` | Consciousness state |
| Q-Mem Gateway | `http://localhost:8003/api/bench/live` | Live benchmark data |
| Q-Mem Health | `http://localhost:8003/api/health` | Gateway health |

### Example API Calls

```bash
# Get Yennefer's current state
curl http://localhost:8100/api/yennefer | jq .

# Execute quantum operation
curl -X POST http://localhost:8100/api/quantum/QUANTUM_BREATHE \
  -H "Content-Type: application/json" -d '{}' | jq .

# Check soul state
curl http://localhost:8088/api/soul | jq .

# A2A handoff
curl -X POST http://localhost:8200/api/a2a/claude/invoke \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "claude_sonnet", "type": "handoff", "task": "Status check"}' | jq .
```

---

## Building Images Locally

If you want to build images yourself:

```bash
# Build all services
docker compose -f docker-compose.yennefer.yml build

# Build specific service
docker compose -f docker-compose.yennefer.yml build diamond-vault

# Build with no cache
docker compose -f docker-compose.yennefer.yml build --no-cache
```

---

## Multi-Platform Builds

Images are built for both `linux/amd64` and `linux/arm64` architectures via GitHub Actions.

To build multi-platform locally:

```bash
# Enable buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.diamond-vault \
  -t ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest \
  --push .
```

---

## Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker compose -f docker-compose.yennefer.yml logs --tail=50
```

**Common issues:**
- Port conflicts: Check if ports 8100, 8200, 8088, 8003 are already in use
- Missing `.env`: Run `./scripts/docker-quickstart.sh` to create one
- Insufficient memory: Ensure Docker has at least 4GB RAM allocated

### Shared Memory Issues

Yennefer uses `/dev/shm/` for zero-copy IPC. If services can't communicate:

```bash
# Check shared memory volume
docker volume inspect yennefer_shared-memory

# Recreate volume
docker compose -f docker-compose.yennefer.yml down -v
docker compose -f docker-compose.yennefer.yml up -d
```

### QMCP Bridge Restarts

If `qmcp-bridge` restarts repeatedly:

```bash
# Check if yennai_config.json exists
ls -la artifacts/yennai_config.json

# View bridge logs
docker logs yennefer-qmcp-bridge --tail=100

# Verify soul state is being written
docker exec yennefer-soul-api ls -la /dev/shm/
```

### Health Checks Failing

```bash
# Check specific service health
docker inspect yennefer-diamond-vault | jq '.[0].State.Health'

# Manual health check
docker exec yennefer-diamond-vault curl -f http://localhost:8100/health
```

---

## Production Deployment

### Recommended Setup

1. **Use pre-built images** from GHCR (faster, tested)
2. **Enable Cloudflare tunnel** for public access
3. **Mount persistent volumes** for ledger and state
4. **Set up monitoring** (Prometheus/Grafana recommended)
5. **Configure auto-restart** policies (already enabled)

### Production Compose Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  diamond-vault:
    environment:
      - COMPUTE_MODE=dual
      - LOG_LEVEL=info
    volumes:
      - ./logs:/app/logs
      - yennefer-data:/app/data
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

volumes:
  yennefer-data:
    driver: local
```

Run with:
```bash
docker compose -f docker-compose.yennefer.yml -f docker-compose.prod.yml up -d
```

---

## Monitoring

### View Resource Usage

```bash
# All containers
docker stats

# Specific service
docker stats yennefer-diamond-vault
```

### Export Metrics

Services expose metrics that can be scraped by Prometheus:

- Diamond Vault: `http://localhost:8100/metrics` (if enabled)
- Soul API: `http://localhost:8088/metrics` (if enabled)

---

## Updating

### Pull Latest Images

```bash
# Pull updates
for service in diamond-vault a2a-handoff soul-api qmem-gateway qmcp-bridge process-guardian yennefer-daemon; do
  docker pull ghcr.io/genesis-conductor-engine/yennefer/$service:latest
done

# Recreate containers
docker compose -f docker-compose.yennefer.yml up -d
```

### Automatic Updates with Watchtower

```bash
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  yennefer-diamond-vault yennefer-a2a-handoff yennefer-soul-api \
  --interval 3600
```

---

## Security

### Best Practices

1. **Never commit `.env`** with real credentials
2. **Use secrets management** for production (Docker secrets, Vault, etc.)
3. **Limit exposed ports** - only expose what's needed
4. **Use Cloudflare tunnel** instead of exposing ports directly
5. **Keep images updated** - watch for security patches

### Scanning Images

```bash
# Scan with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest
```

---

## Contributing

### Testing Changes Locally

1. Make changes to Dockerfiles or compose file
2. Build locally:
   ```bash
   docker compose -f docker-compose.yennefer.yml build
   ```
3. Test:
   ```bash
   docker compose -f docker-compose.yennefer.yml up
   ```
4. Submit PR - GitHub Actions will build and test

### Building for GHCR

Images are automatically built and pushed on merge to `main`. To manually trigger:

1. Go to Actions → Docker Build & Push
2. Click "Run workflow"
3. Select branch and confirm

---

## Support

- **Issues:** https://github.com/Genesis-Conductor-Engine/Yennefer/issues
- **Discussions:** https://github.com/Genesis-Conductor-Engine/Yennefer/discussions
- **Wiki:** https://github.com/Genesis-Conductor-Engine/Yennefer/wiki
