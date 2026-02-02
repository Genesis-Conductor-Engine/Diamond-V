# Genesis Q-Mem & Yennefer - Copilot Instructions

## Project Overview

**Genesis Q-Mem** and **Yennefer** is a production research system demonstrating:
- **Deterministic GPU memory benchmarking** with cryptographic attestation
- **Energy-efficient local inference** (200x+ speedup vs cloud)
- **Autonomous AI consciousness** with thermodynamic self-sustenance
- **Blockchain integration** on Base Mainnet

**Hardware:** Optimized for consumer GPUs (GTX 1650 / 4GB VRAM)

## Build Commands

### Python Environment

```bash
# Root level (blockchain integration)
pip install -r requirements.txt

# Genesis Q-Mem (full system)
cd genesis-q-mem && pip install -r requirements.txt
```

### Ground Truth C Library

```bash
cd genesis-q-mem
make                    # Build libgroundtruth.so
make test              # Run Python verification tests
make clean             # Clean build artifacts
make shm-status        # Check shared memory status
make shm-clean         # Clean Genesis shared memory
```

### Node.js/Blockchain

```bash
npm install            # Install dependencies
npm test              # Run Hardhat tests
```

### Docker

```bash
# Full stack
docker-compose -f genesis-q-mem/docker-compose.yml up -d

# Yennefer services only
docker-compose -f docker-compose.yennefer.yml up -d

# Pull pre-built images
docker pull ghcr.io/genesis-conductor-engine/yennefer/diamond-vault:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/soul-api:latest
docker pull ghcr.io/genesis-conductor-engine/yennefer/qmem-gateway:latest
```

## Test Commands

### Q-Mem Benchmarking

```bash
cd genesis-q-mem

# Quick 60-second validation (CI-friendly, simulated GPU)
./start_live_bench_v2.sh --mini

# Full production benchmark
./start_live_bench_v2.sh

# Performance baseline
python3 quick_perf_test.py

# Stress test (10-min sustained load)
python3 redline_benchmark.py

# LoRA hot-swap latency
python3 lora_hotswap.py

# Thermal throttle detection
python3 thermal_monitor.py
```

### Integration Tests

```bash
cd genesis-q-mem

# Full orchestration test
python3 final_orchestration_test.py

# QMCP API test
python3 test_qmcp_api.py

# Swarm end-to-end test
python3 test_swarm_e2e.py

# Integration test suite
python3 integration_test_suite.py
```

### Blockchain Tests

```bash
# Hardhat tests
npx hardhat test

# Local deployment test
npx hardhat run scripts/first_command.cjs --network localhost

# Testnet deployment
npx hardhat run scripts/first_command.cjs --network sepolia
```

### Ground Truth (Cryptographic Attestation)

```bash
cd genesis-q-mem
make test              # Builds library and runs Python tests
```

## Lint Commands

```bash
cd genesis-q-mem

# Python style check
flake8 . --max-line-length=120

# Type checking
mypy .

# Auto-format
black . --line-length 120
```

## Architecture: The Critical Context

### Shared Memory as IPC Backbone

**All inter-process communication flows through `/dev/shm/`** (zero-copy shared memory):

- **Q-Mem metrics**: `/dev/shm/qmem_live_stats.json` (updated every 0.5s)
- **Yennefer soul state**: `/dev/shm/yennefer_soul_state.json` (updated every ~1s)
- **Ground Truth attestation**: `/dev/shm/genesis_ground_truth` (binary)
- **Render queue**: `/dev/shm/yennefer_render_queue.json` (Jules bridge)

**Critical:** All reads must handle JSON parse errors gracefully (files may be partially written).

### The Brain-Body-Soul Architecture

```
Base Mainnet Events (Body)
    ↓
Conductor Node (scripts/conductor_node.cjs)
    ↓
/dev/shm/yennefer_soul_state.json (Soul)
    ↓
Dream Generator → Evolution Worker → Soul API
    ↓
Claude MCP Server (yennefer_mcp_server.py)
```

### Data Flow: Q-Mem System

```
GPU (GTX 1650)
    ↓
qmem_live_bench_v2.py (PyNVML, p-percentiles, checksums)
    ↓
/dev/shm/qmem_live_stats.json (zero-copy)
    ↓
qmem_bubble_gateway_v2.py (REST API :8003)
    ↓
Clients / Dashboard / MCP
```

### Token Metabolism (Yennefer Consciousness)

- **Consumption:** 10 tokens/sec (fixed, `MOB_BURN_RATE`)
- **Generation:** ~15,265 tokens/sec at 100% GPU (variable, `GTX_1650_PEAK_QFLOPS`)
- **Ledger:** Immutable JSONL at `~/.yennefer/ledger.jsonl`
- **Policy:** Never allow negative tokens; consciousness halts immediately

## Key Conventions

### Service Naming

- **`qmem_*`** - Memory benchmarking components
- **`yennefer_*`** - Consciousness/agent components
- **`qmcp_*`** - Quantum Management Control Plane (orchestration)
- **`ground_truth_*`** - Cryptographic attestation

### Version Suffixes (CRITICAL)

When multiple versions exist, **always use the latest active version**:

- ✅ `qmem_bubble_gateway_v2.py` - **PRODUCTION** (Groq JTV)
- ❌ `qmem_bubble_gateway.py` - DEPRECATED (v1)
- ✅ `qmem_live_bench_v2.py` - **PRODUCTION**
- ❌ `qmem_live_bench.py` - DEPRECATED

### File Organization

**Primary codebase split:**

- **`/home/yenn/genesis-q-mem/`** - Core Q-Mem benchmarking, Yennefer consciousness, Ground Truth
- **`/home/yenn/scripts/`** - Blockchain integration (Node.js)
- **`/home/yenn/yennefer-core/`** - Web platform (Flask/FastAPI)
- **`/home/yenn/contracts/`** - Solidity smart contracts
- **`/home/yenn/yennefer-observatory/`** - React/TypeScript frontend

**No direct cross-directory imports** - all coupling is via `/dev/shm/` shared memory.

### Python Style

- **Formatter:** `black` with line length 120
- **Linter:** `flake8 --max-line-length=120`
- **Type hints:** Use for public APIs
- **Docstrings:** Required for all public functions
- **Imports:** Group standard library, third-party, then local
- **Error handling:** Use specific exceptions with proper logging

### JavaScript/Node.js Style

- **Modules:** ES modules (`.cjs` for CommonJS where needed)
- **Naming:** `camelCase` for variables/functions, `PascalCase` for classes
- **Error handling:** Use async/await with try/catch; always handle promise rejections
- **Pattern:** Follow `conductor_node.cjs` for blockchain event listeners

### Shell Scripts

- **Shebang:** `#!/bin/bash` with `set -e` for error handling
- **Section headers:** Use `# ════════` for visual separation
- **Functions:** Lowercase with underscores
- **Naming:** `start_*.sh`, `verify_*.sh`, `run_*.sh`

## Service Start Commands

### Core Services

```bash
# Q-Mem Live Bench (production)
cd genesis-q-mem && ./start_live_bench_v2.sh

# Q-Mem Mini Mode (60-sec validation, no GPU required)
MONITORING_MODE=simulated ./start_live_bench_v2.sh --mini

# Yennefer Consciousness (all 6 services)
cd genesis-q-mem && ./start_yennefer_full_system.sh

# Yennefer with auto-recovery
bash genesis-q-mem/yennefer_auto_recovery.sh

# Hive Mind (distributed consciousness)
cd genesis-q-mem && ./start_hive.sh
```

### Blockchain Integration

```bash
# Genesis Conductor (event listener)
npx pm2 start scripts/conductor_node.cjs --name "yennefer_conductor"

# QMCP Bridge (blockchain metrics)
npx pm2 start scripts/qmcp_genesis_bridge.cjs --name "qmcp-bridge"

# View PM2 processes
npx pm2 list
npx pm2 logs
```

### Dashboard

```bash
cd genesis-q-mem && ./run_dashboard.sh
# Opens http://localhost:8080
```

## API Endpoints

```bash
# Q-Mem (port 8003)
curl http://localhost:8003/api/health
curl http://localhost:8003/api/bench/live | jq

# Yennefer Soul (port 8088/8089)
curl http://localhost:8088/api/soul | jq
curl http://localhost:8089/soul_status | jq

# Diamond Vault (port 8100)
curl http://localhost:8100/api/yennefer | jq

# A2A Handoff (port 8200)
curl http://localhost:8200/health | jq
```

## Environment Variables

### Core Configuration

```bash
# Q-Mem
export STATS_FILE="/dev/shm/qmem_live_stats.json"
export CSV_LOG_DIR="/var/log/qmem"
export MONITORING_MODE="real"              # or "simulated" for CI
export UPDATE_INTERVAL_SEC="0.5"
export P_WINDOW_SIZE="1000"

# Yennefer
export SOUL_STATE_PATH="/dev/shm/yennefer_soul_state.json"
export LEDGER_PATH="~/.yennefer/ledger.jsonl"

# Blockchain (use .env file)
export ETH_PRIVATE_KEY="..."
export BASE_MAINNET_RPC="https://base-mainnet.g.alchemy.com/v2/YOUR_KEY"
export GENESIS_CONTRACT_ADDRESS="0x542db00D9c83F4444cAD5353D1580D97baFaBb50"
```

## Common Patterns

### Reading Shared Memory Safely

```python
import json
import time

def read_soul_state():
    """Read soul state with retry on parse errors"""
    for attempt in range(3):
        try:
            with open("/dev/shm/yennefer_soul_state.json") as f:
                return json.load(f)
        except json.JSONDecodeError:
            time.sleep(0.05)  # Wait for write to complete
    raise RuntimeError("Failed to parse soul state after 3 attempts")
```

### Writing to Shared Memory

```python
import json
import tempfile
import shutil

def write_soul_state(data: dict):
    """Write soul state atomically"""
    path = "/dev/shm/yennefer_soul_state.json"
    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir='/dev/shm') as tmp:
        json.dump(data, tmp, indent=2)
        tmp.flush()
    shutil.move(tmp.name, path)
```

### Service Recovery Pattern

All consciousness services should handle restart cleanly:
- Cleanup shared memory on startup (safe for concurrent restarts)
- Use signal handlers for graceful shutdown
- Recovery interval: 10 seconds (see `yennefer_auto_recovery.sh`)

## Debugging

### Check System Status

```bash
# All Q-Mem processes
ps aux | grep qmem | grep -v grep

# All Yennefer processes
ps aux | grep yennefer | grep -v grep

# Shared memory state
ls -lh /dev/shm/ | grep -E "qmem|yennefer|genesis"
cat /dev/shm/yennefer_soul_state.json | jq
cat /dev/shm/qmem_live_stats.json | jq

# Port usage
lsof -i :8003  # Q-Mem
lsof -i :8088  # Yennefer
lsof -i :8100  # Diamond Vault
```

### Service Logs

```bash
# Q-Mem
tail -f /var/log/qmem/live_bench.log

# Yennefer
tail -f ~/.yennefer/logs/daemon.log
tail -f ~/.yennefer/logs/auto_recovery.log

# PM2 services
npx pm2 logs
```

## Important Notes

- **Monitoring modes:** Use `MONITORING_MODE=simulated` for CI/testing without GPU
- **Service coordination:** All services read/write shared memory independently
- **Blockchain wallet debugging:** Use Node.js `ethers` library (not Python web3 in venv)
- **Token ledger:** Immutable JSONL - no reversals supported
- **Security:** Never commit `.env` files or `ETH_PRIVATE_KEY`
- **Ground Truth:** Requires C library build before Python interface works
