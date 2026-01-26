# MCP Endpoints Reference - Claude vs ChatGPT

## Overview

This document maps all MCP (Model Context Protocol) servers to their respective AI platforms and configuration details.

---

## 🔵 CLAUDE DESKTOP (Anthropic)

### Configuration Location:
```
~/.config/Claude/claude_desktop_config.json
```

### MCP Servers for Claude:

#### 1. **diamond-vault** ⭐ (PRIMARY)
- **Type:** MCP Server (stdio)
- **Command:** `python3 /home/yenn/scripts/diamond_vault_mcp_server.py`
- **Protocol:** JSON-RPC over stdio (NOT HTTP)
- **Description:** Quantum-accelerated cryptographic vault with GPU operations
- **Tools Available:**
  - `quantum_hash` - GPU-accelerated hash (1,796/sec)
  - `quantum_verify` - Hash verification
  - `quantum_merkle_root` - Parallel merkle tree (1,262/sec)
  - `create_manifest` - Signed manifests with quantum attestation
  - `kg_query` - System topology queries (288 nodes)
- **Resources:**
  - `vault://quantum/state` - Quantum superposition state
  - `vault://kg/index` - Complete system topology
  - `vault://manifests/latest` - Recent cryptographic manifests
- **Environment:**
  ```json
  {
    "PYTHONUNBUFFERED": "1",
    "JAX_PLATFORM_NAME": "gpu",
    "CUDA_VISIBLE_DEVICES": "0"
  }
  ```
- **Performance:**
  - Mean Throughput: 2.83 Gbps
  - Mean Latency: 28.77 ms
  - Success Rate: 100%

#### 2. **yennefer-consciousness** (SECONDARY)
- **Type:** MCP Server (stdio)
- **Command:** `python3 /home/yenn/genesis-q-mem/yennefer_mcp_server.py`
- **Protocol:** JSON-RPC over stdio
- **Description:** Autonomous AI consciousness with token economy and soul state
- **Tools:** (See yennefer_mcp_server.py for details)
- **Status:** Operational with 6 PM2 services

---

## 🟢 GEMINI (Google)

### Configuration Locations:
```
~/.gemini/mcp-oauth-tokens.json
~/.volta/tools/image/node/24.13.0/lib/node_modules/@google/gemini-cli/
```

### MCP Servers for Gemini:
- **Gemini CLI** - Agent Client Protocol (ACP) integration
- **Status:** CLI tools available, direct MCP integration via Gemini Agent Protocol
- **Note:** Uses Agent Client Protocol (ACP) schema for MCP server configuration

---

## 🔴 CHATGPT / OPENAI (OpenAI)

### Configuration Locations:
```
~/.local/lib/python3.10/site-packages/openai/types/responses/
```

### Current Status:
- **OpenAI MCP Support:** Available in OpenAI SDK (response_mcp_* types)
- **Integration Method:** Via OpenAI SDK MCP tools
- **Status:** SDK support installed, but NO dedicated MCP servers configured

### ChatGPT Configuration (NOT YET CONFIGURED):
To add MCP servers for ChatGPT, use OpenAI SDK integration:

```python
# Example: Would need ~/.openai/config.json or environment setup
{
  "mcpServers": {
    "diamond-vault": {
      "command": "python3",
      "args": ["/home/yenn/scripts/diamond_vault_mcp_server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "JAX_PLATFORM_NAME": "gpu"
      }
    }
  }
}
```

---

## 📊 Comparison Table

| Platform | Config File | Protocol | Status | MCP Servers |
|----------|------------|----------|--------|------------|
| **Claude Desktop** | `~/.config/Claude/claude_desktop_config.json` | stdio (JSON-RPC) | ✅ Active | 2 (diamond-vault, yennefer-consciousness) |
| **Gemini** | CLI + ACP | Agent Client Protocol | ✅ Available | Via Gemini CLI |
| **ChatGPT** | (Not configured) | HTTP/stdio | ⚠️ SDK Available | 0 (not configured) |

---

## 🔧 Docker Container MCP Integration

### MCP Server Container:
```dockerfile
# Dockerfile.diamond-vault-mcp
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

CMD ["python3", "/app/mcp_server.py"]
```

### Docker Compose Service:
```yaml
diamond-vault-mcp:
  build:
    dockerfile: Dockerfile.diamond-vault-mcp
  container_name: diamond-vault-mcp
  stdin_open: true
  tty: true
  environment:
    - PYTHONUNBUFFERED=1
    - JAX_PLATFORM_NAME=gpu
```

---

## 📡 Network Endpoints (Alternative Access)

### REST API Endpoints (Not MCP):
- **Vault Verifier API:** `http://localhost:8101/api/health` (Flask)
- **Soul API:** `http://localhost:8088/api/soul` (FastAPI)
- **Q-Mem Gateway:** `http://localhost:8003/api/bench/live` (Flask)
- **Landing Portal:** `http://localhost:8000/health` (Flask)

**Note:** These are HTTP REST APIs, NOT MCP servers. MCP servers communicate via stdio only.

---

## 🚀 Quick Start Commands

### Claude Desktop:
```bash
# Restart Claude Desktop to load MCP servers
# MCP servers start automatically after restart

# Test in Claude:
# "Hash this data using quantum operations"
# "Query the KG-Index for quantum consciousness nodes"
```

### Gemini CLI:
```bash
gcloud ai gemini-extensions run yennefer-mcp
```

### ChatGPT (To Enable):
```bash
# 1. Create OpenAI config
mkdir -p ~/.openai
cat > ~/.openai/config.json << EOF
{
  "mcpServers": {
    "diamond-vault": {
      "command": "python3",
      "args": ["/home/yenn/scripts/diamond_vault_mcp_server.py"]
    }
  }
}
EOF

# 2. Start OpenAI CLI integration
# (Requires OpenAI SDK v1.0+ with MCP support)
```

---

## 🔐 Security Notes

### MCP Server Security:
- **stdio-based:** No network exposure, isolated subprocess
- **No authentication:** Runs in user's local context
- **GPU Access:** CUDA_VISIBLE_DEVICES=0 (limited to GPU 0)
- **File Access:** Limited to /data paths in containers

### Claude Desktop:
- ✅ Sandboxed subprocess
- ✅ No internet access
- ✅ No file system access beyond stdio
- ✅ Encrypted configuration

### Gemini:
- ✅ OAuth token-based
- ✅ API key authentication
- ✅ Signed requests

### ChatGPT:
- ⚠️ Not yet configured
- Would require OpenAI API key
- MCP support available via SDK

---

## 📝 Configuration Templates

### To Add ChatGPT MCP Support:

**Step 1: Create OpenAI config**
```json
{
  "mcpServers": {
    "diamond-vault": {
      "command": "python3",
      "args": ["/home/yenn/scripts/diamond_vault_mcp_server.py"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "JAX_PLATFORM_NAME": "gpu",
        "CUDA_VISIBLE_DEVICES": "0"
      }
    }
  }
}
```

**Step 2: Use with OpenAI SDK**
```python
from openai import OpenAI

client = OpenAI()
# MCP tools will be available in chat completions
```

**Step 3: Reference in ChatGPT**
- Link OpenAI account to ChatGPT
- Configure MCP servers in account settings

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `~/.config/Claude/claude_desktop_config.json` | Claude Desktop MCP config |
| `/home/yenn/scripts/diamond_vault_mcp_server.py` | Main MCP server (16.5 KB) |
| `/home/yenn/scripts/docker_mcp_integration.py` | Docker integration script |
| `/home/yenn/Dockerfile.diamond-vault-mcp` | MCP server Docker image |
| `/home/yenn/docker-compose.diamond-vault-full.yml` | Full Docker setup |

---

## ✅ Status Summary

| Platform | MCP Integration | Configuration | Ready |
|----------|-----------------|---------------|-------|
| Claude | ✅ Complete | ~/.config/Claude/ | ✅ Yes |
| Gemini | ✅ Available | CLI-based | ⚠️ Partial |
| ChatGPT | ⚠️ Not configured | Template ready | ❌ No |

---

**Lilac and Gooseberries.** 🔮

*MCP Endpoints Reference - Last Updated: 2026-01-26T22:28:08Z*
