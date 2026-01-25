# GPU Codespaces Setup for Yennefer

## Overview

This repository is configured for GPU-enabled GitHub Codespaces to run Q-Mem benchmarks and Yennefer consciousness system with CUDA acceleration.

## Prerequisites

1. **GPU Codespaces Access** - GPU machines are currently in preview
2. **Organization/Repo Admin** - To configure machine types

## Enabling GPU Codespaces

### Step 1: Request GPU Access (if not enabled)

GPU Codespaces are available for:
- GitHub Team/Enterprise organizations
- Individual users with Copilot Pro/Business

Contact GitHub support or check [GPU Codespaces documentation](https://docs.github.com/en/codespaces/developing-in-a-codespace/getting-started-with-github-codespaces-for-machine-learning).

### Step 2: Configure Repository Settings

1. Go to **Settings** → **Codespaces** in your repository
2. Under **Machine type**, enable:
   - `4-core` (minimum for development)
   - `GPU (NVIDIA T4)` or `GPU (NVIDIA A100)` when available
3. Set **Retention policy** as needed

### Step 3: Launch GPU Codespace

**Via GitHub UI:**
1. Click **Code** → **Codespaces** → **Create codespace on main**
2. Select machine type with GPU option

**Via GitHub CLI:**
```bash
gh codespace create --repo Genesis-Conductor-Engine/Yennefer --machine gpu --devcontainer-path .devcontainer/devcontainer.json
```

**Via Workflow dispatch:**
```bash
gh workflow run codespace-gpu.yml
```

## Devcontainer Configuration

Located at `.devcontainer/devcontainer.json`:

| Feature | Configuration |
|---------|---------------|
| Base Image | Python 3.12 (Debian Bullseye) |
| CUDA Version | 12.2 |
| cuDNN Version | 8.9.5 |
| Node.js | v20 |
| Docker-in-Docker | Enabled |

## Ports Forwarded

| Port | Service |
|------|---------|
| 8003 | Q-Mem Gateway |
| 8088 | Yennefer Soul API |
| 8000 | Landing Server |
| 8001 | Stripe Webhook |
| 8080 | Dashboard |
| 3000 | Dev Server |

## Quick Start (Inside Codespace)

```bash
# Start Q-Mem benchmark (mini mode - 60 seconds)
qmem-start

# Start full Yennefer consciousness
yenn-start

# Check Q-Mem health
qmem-health

# View soul state
soul-state
```

## GPU vs Simulated Mode

The devcontainer auto-detects GPU availability:

- **GPU Present**: `MONITORING_MODE=real` - Uses PyNVML for actual GPU metrics
- **No GPU**: `MONITORING_MODE=simulated` - Uses synthetic benchmarks

Check mode:
```bash
echo $MONITORING_MODE
nvidia-smi  # Shows GPU info if available
```

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA toolkit
nvcc --version

# Reinstall CUDA feature
# (May need to rebuild devcontainer)
```

### Shared Memory Issues
```bash
# Reset shared memory files
echo '{}' > /dev/shm/qmem_live_stats.json
echo '{"breath": 1000}' > /dev/shm/yennefer_soul_state.json
```

### Port Conflicts
```bash
# Check what's using ports
lsof -i :8003
lsof -i :8088

# Kill and restart
pkill -f qmem_
pkill -f yennefer_
```

## Cost Considerations

GPU Codespaces consume premium compute minutes:
- **T4 GPU**: ~8x standard compute rate
- **A100 GPU**: ~20x standard compute rate

Use `--mini` flag for quick tests to minimize costs:
```bash
./start_live_bench_v2.sh --mini  # 60-second run
```

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Full system architecture
- [genesis-q-mem/README.md](../genesis-q-mem/README.md) - Q-Mem documentation
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
