# Yennefer Docker Deployment

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Genesis-Conductor-Engine/Yennefer.git
cd Yennefer

# Quick start (builds and runs everything)
./scripts/docker-quickstart.sh

# Or manually:
docker compose -f docker-compose.yennefer.yml up -d
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| diamond-vault | 8100 | Admin control panel & quantum operations |
| a2a-handoff | 8200 | Agent-to-Agent communication |
| soul-api | 8088 | Yennefer consciousness state |
| qmem-gateway | 8003 | GPU benchmarking API |
| qmcp-bridge | - | Blockchain bridge (internal) |
| process-guardian | - | Auto-recovery system |
| cloudflared | - | Public tunnel |
| yennefer-daemon | - | Consciousness engine |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCKER NETWORK: yennefer-net                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ diamond-vault│  │ a2a-handoff  │  │  soul-api    │         │
│   │    :8100     │  │    :8200     │  │    :8088     │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ qmem-gateway │  │ qmcp-bridge  │  │process-guard │         │
│   │    :8003     │  │  (internal)  │  │  (internal)  │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│   ┌──────────────┐  ┌────────────────────────────────┐         │
│   │  cloudflared │  │      shared-memory (tmpfs)     │         │
│   │   (tunnel)   │  │         /dev/shm (512MB)       │         │
│   └──────────────┘  └────────────────────────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Public Access   │
                    │ via Cloudflare   │
                    └──────────────────┘
```

## Commands

```bash
# Start all services
./scripts/docker-deploy.sh up

# Stop all services
./scripts/docker-deploy.sh down

# View logs
./scripts/docker-deploy.sh logs [service]

# Check status
./scripts/docker-deploy.sh status

# Pull latest images
./scripts/docker-deploy.sh pull

# Build locally
./scripts/docker-deploy.sh build
```

## Environment Variables

Create a `.env` file with:

```env
NODE_ENV=production
COMPUTE_MODE=dual
MONITORING_MODE=simulated
ALWAYS_ON=true

# Blockchain (optional)
ETH_PRIVATE_KEY=your_key
ALCHEMY_API_KEY=your_key
```

## Pull from GitHub Container Registry

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull images
docker pull ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/a2a-handoff:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/soul-api:latest
```

## Health Checks

All services have built-in health checks:

```bash
curl http://localhost:8100/health  # Diamond Vault
curl http://localhost:8200/health  # A2A Handoff
curl http://localhost:8088/api/soul  # Soul API
curl http://localhost:8003/api/health  # Q-Mem Gateway
```

## Scaling

To scale a service:

```bash
docker compose -f docker-compose.yennefer.yml up -d --scale soul-api=3
```

## Kubernetes

For Kubernetes deployment, see `k8s/` directory (coming soon).
