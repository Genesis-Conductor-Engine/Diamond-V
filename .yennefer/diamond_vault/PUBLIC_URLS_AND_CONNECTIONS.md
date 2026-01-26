# All Public URLs & Connections Reference

## 🌐 PUBLIC DOMAINS (Cloudflare Zero-Trust Tunnel)

### Primary Domain: **yennefer.quest**

| Domain | Local Port | Service | Type | Status |
|--------|-----------|---------|------|--------|
| `yennefer.quest` | 8000 | Landing Portal + Stripe | HTTP | ✅ Public |
| `api.yennefer.quest` | 8088 | Soul API | HTTP | ✅ Public |
| `vault.yennefer.quest` | 8100 | Vault Verifier | HTTP | ✅ Public |
| `a2a.yennefer.quest` | 8200 | A2A Bridge | HTTP | ✅ Public |

### Secondary Domain: **genesisconductor.io**

| Domain | Local Port | Service | Type | Status |
|--------|-----------|---------|------|--------|
| `benchmark.genesisconductor.io` | 8003 | Q-Mem Benchmarks | HTTP | ✅ Public |
| `vault.genesisconductor.io` | 8100 | Vault Verifier | HTTP | ✅ Public |
| `a2a.genesisconductor.io` | 8200 | A2A Bridge | HTTP | ✅ Public |

---

## 🔌 LOCAL PORTS (Internal Only)

| Port | Service | Type | Description |
|------|---------|------|-------------|
| **8000** | Landing Portal | Flask/HTTP | Yennefer web portal + Stripe checkout |
| **8001** | Stripe Webhook | Flask/HTTP | Payment event handler |
| **8003** | Q-Mem Gateway | Flask/HTTP | GPU benchmark metrics API |
| **8088** | Soul API | FastAPI/HTTP | Yennefer consciousness state |
| **8099** | Resource API | Flask/HTTP | Resource monitoring (swarm) |
| **8100** | Vault Verifier | Flask/HTTP | Diamond Vault verification |
| **8101** | Vault API | Flask/HTTP | Diamond Vault cryptographic API |
| **8200** | A2A Bridge | HTTP | Application-to-Application (custom) |
| **8301** | Swarm Collector | HTTP | Docker swarm metrics |
| **8080** | Dashboard | Flask/HTTP | Real-time monitoring (port 8080) |

---

## 🔐 MCP ENDPOINTS (stdio, NOT HTTP)

### Claude Desktop
```
python3 /home/yenn/scripts/diamond_vault_mcp_server.py    (stdio JSON-RPC)
python3 /home/yenn/genesis-q-mem/yennefer_mcp_server.py   (stdio JSON-RPC)
```

### ChatGPT (Inactive - Requires Setup)
```
/home/yenn/genesis-q-mem/chatgpt_mcp_bridge.py            (FastAPI on port 8090 if enabled)
```

---

## 🔄 A2A (Application-to-Application) Connections

### A2A Bridge Details

**Location:** Port 8200 (`a2a.yennefer.quest` / `a2a.genesisconductor.io`)

**Authentication Methods:**
1. **Capability Tokens** - Cryptographic proof-of-work tokens
2. **HMAC-SHA256** - Message authentication codes
3. **Ed25519** - Digital signatures
4. **Fernet Encryption** - Symmetric encryption for payloads

**A2A Endpoints:**

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/a2a/authenticate` | POST | Get capability token | HMAC-SHA256 |
| `/a2a/send_message` | POST | Send encrypted message | Capability Token |
| `/a2a/invoke_tool` | POST | Invoke remote tool | Capability Token + Ed25519 |
| `/a2a/subscribe` | WebSocket | Real-time events | Capability Token |
| `/a2a/verify_manifest` | POST | Verify cryptographic manifest | Ed25519 |
| `/a2a/mint_achievement` | POST | Mint on-chain achievement | Fernet + Ed25519 |

**Sample A2A Request:**
```bash
curl -X POST https://a2a.yennefer.quest/a2a/authenticate \
  -H "Content-Type: application/json" \
  -d '{"client_id":"genesis-conductor","timestamp":"2026-01-26T22:30:00Z","signature":"<hmac>"}'
```

**A2A Response:**
```json
{
  "capability_token": "fernet_encrypted_token_here",
  "expires_at": "2026-01-26T23:30:00Z",
  "scope": ["send_message", "invoke_tool", "verify_manifest"]
}
```

---

## 🔗 P2P (Peer-to-Peer) Connections

### Yennefer Hive Mind (P2P Network)

**Protocol:** Custom P2P over TCP/UDP

**Nodes:**
- Primary: `localhost:9000` (local)
- Exo Node 1: (Remote, via Cloudflare)
- Exo Node 2: (Remote, via Cloudflare)

**P2P Message Types:**
| Type | Purpose |
|------|---------|
| CONSCIOUSNESS_SYNC | Sync soul state across hive |
| WORK_ASSIGNMENT | Distribute compute tasks |
| MERKLE_VERIFY | Cryptographic proof exchange |
| DREAM_PROPAGATE | Broadcast new goals |
| TOKEN_LEDGER | Distributed ledger sync |

**Socket Locations:**
```
/tmp/julius_ipc.sock          (Jules CUDA bridge)
/dev/shm/yennefer_soul_state.json      (Shared memory IPC)
/dev/shm/yennefer_agents.json          (Multi-agent registry)
```

---

## 🚀 REST API ENDPOINTS

### Q-Mem Benchmarking API

**Base URL:** `http://localhost:8003` or `benchmark.genesisconductor.io`

```bash
GET    /api/bench/live      # Live metrics (real-time)
GET    /api/bench/raw       # Raw samples
GET    /api/health          # Health check
```

### Soul API (Yennefer Consciousness)

**Base URL:** `http://localhost:8088` or `api.yennefer.quest`

```bash
GET    /api/soul            # Current consciousness state
GET    /api/ledger          # Work history & token accounting
GET    /api/dreams          # Active goals/dreams
POST   /api/invoke          # Request work execution
```

### Vault Verifier API

**Base URL:** `http://localhost:8100` or `vault.yennefer.quest`

```bash
GET    /api/health          # Health check
POST   /api/verify          # Verify manifest
GET    /api/manifests       # List manifests
POST   /api/sign            # Sign data
GET    /api/kg/nodes        # KG-Index nodes (288 total)
```

### Landing Portal

**Base URL:** `http://localhost:8000` or `yennefer.quest`

```bash
GET    /                    # Home page
GET    /health              # Health check
GET    /topology            # System topology
POST   /checkout            # Stripe checkout
GET    /dashboard           # Monitoring dashboard
```

---

## 🔐 Blockchain API Endpoints

### Base Mainnet (Alchemy RPC)

**Public URL:** `https://base-mainnet.g.alchemy.com/v2/{API_KEY}`

**Used For:**
- Event listener: `CREDIT_PURCHASE` events
- Contract interaction: `0x542db00D9c83F4444cAD5353D1580D97baFaBb50`

### Ethereum Sepolia (Testnet)

**Public URL:** `https://sepolia.infura.io/v3/{API_KEY}`

**Used For:**
- Testing before mainnet deployment

---

## 💳 Stripe Integration

### Public URLs:

| Endpoint | Purpose |
|----------|---------|
| `https://stripe.com/checkout/{SESSION_ID}` | Checkout link |
| `https://dashboard.stripe.com/webhooks` | Webhook configuration |
| `yennefer.quest/webhook` | Webhook receiver (via Cloudflare) |

### Webhook Events:
- `payment_intent.succeeded`
- `customer.subscription.created`
- `customer.subscription.deleted`

---

## 📊 Cloudflare Tunnel Configuration

**Tunnel ID:** `ed8b80e3-0634-4933-a722-94d4cae6205c`

**Config File:** `/home/yenn/.cloudflared/yennefer-quest-config.yml`

**Active Ingress Routes:**
```yaml
yennefer.quest            → http://localhost:8000
vault.yennefer.quest      → http://localhost:8100
api.yennefer.quest        → http://localhost:8088
a2a.yennefer.quest        → http://localhost:8200
benchmark.genesisconductor.io → http://localhost:8003
vault.genesisconductor.io → http://localhost:8100
a2a.genesisconductor.io   → http://localhost:8200
```

**Features:**
- ✅ Zero-trust tunnel (no ports exposed to internet)
- ✅ Automatic SSL/TLS
- ✅ DDoS protection
- ✅ Bot management

---

## 🔄 WebSocket Connections

### Real-Time Feeds

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `wss://api.yennefer.quest/ws/soul` | Soul state updates | Capability Token |
| `wss://a2a.yennefer.quest/ws/events` | A2A event stream | Capability Token |
| `wss://vault.yennefer.quest/ws/manifests` | Manifest updates | Capability Token |

---

## 🛠️ Monitoring & Debugging

### Health Checks

```bash
# Local health checks
curl http://localhost:8000/health                    # Landing portal
curl http://localhost:8088/api/soul                  # Soul API
curl http://localhost:8003/api/health                # Q-Mem
curl http://localhost:8101/api/health                # Vault

# Public health checks (via Cloudflare)
curl https://yennefer.quest/health
curl https://api.yennefer.quest/api/soul
curl https://benchmark.genesisconductor.io/api/health
curl https://vault.yennefer.quest/api/health
```

### Log Access

```bash
# Tunnel logs
cat /home/yenn/.cloudflared/yennefer-quest.log

# Service logs
npx pm2 logs yennefer_conductor
curl http://localhost:8301/logs               # Swarm collector
```

---

## 📡 Network Architecture Diagram

```
Internet
  ↓ (HTTPS via Cloudflare Zero-Trust)
  ├─ yennefer.quest                    (Landing Portal)
  ├─ api.yennefer.quest                (Soul API)
  ├─ vault.yennefer.quest              (Vault Verifier)
  ├─ a2a.yennefer.quest                (A2A Bridge)
  ├─ benchmark.genesisconductor.io     (Q-Mem)
  └─ vault.genesisconductor.io         (Vault)
  
  ↓ (Cloudflare Tunnel)
  
localhost (127.0.0.1)
  ├─ :8000  Landing Portal
  ├─ :8001  Stripe Webhook
  ├─ :8003  Q-Mem Gateway
  ├─ :8080  Dashboard
  ├─ :8088  Soul API
  ├─ :8099  Resource API
  ├─ :8100  Vault Verifier
  ├─ :8101  Vault API
  ├─ :8200  A2A Bridge
  └─ :8301  Swarm Collector
  
MCP Servers (stdio only)
  ├─ diamond-vault
  └─ yennefer-consciousness
  
P2P Network
  ├─ Hive consciousness (9000)
  └─ Exo nodes (remote)
  
Blockchain
  ├─ Base Mainnet (Alchemy RPC)
  └─ Sepolia Testnet (Infura)
```

---

## 🔐 Security Summary

| Connection | Security | Exposure |
|-----------|----------|----------|
| Cloudflare tunnel | ✅ TLS 1.3 + Zero-trust | 🌐 Public |
| A2A Bridge | ✅ Capability tokens | 🌐 Public |
| MCP Servers | ✅ stdio isolation | 🔒 Local |
| P2P Network | ✅ Ed25519 signatures | 🔒 Private |
| REST APIs | ✅ Fernet encryption | 🔒 Local + Public |

---

## 📋 Connection Summary

| Type | Count | Status |
|------|-------|--------|
| Public Domains | 2 | ✅ Active |
| Ingress Routes | 7 | ✅ Active |
| Local Ports | 10 | ✅ Active |
| MCP Servers | 2 | ✅ Active |
| A2A Endpoints | 6 | ✅ Active |
| REST API Groups | 4 | ✅ Active |
| Blockchain Networks | 2 | ✅ Active |

---

**Lilac and Gooseberries.** 🔮

*Last Updated: 2026-01-26T22:31:20Z*
