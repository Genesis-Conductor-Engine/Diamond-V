# Fix MCP Configurations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix Copilot MCP configuration validation errors and OpenCode agent configuration format issues

**Architecture:** Update MCP configuration files to match current validation schemas - add required fields to Copilot config and convert OpenCode tools format from array to object

**Tech Stack:** JSON configuration (Copilot), YAML frontmatter (OpenCode)

---

## Task 1: Backup Existing Configurations

**Files:**
- Read: `/home/yenn/.copilot/mcp-config.json`
- Read: `/home/yenn/.opencode/agents/yennefer.md`
- Create: `/home/yenn/.copilot/mcp-config.json.backup-$(date +%Y%m%d-%H%M%S)`
- Create: `/home/yenn/.opencode/agents/yennefer.md.backup-$(date +%Y%m%d-%H%M%S)`

**Step 1: Create timestamped backups**

Run:
```bash
timestamp=$(date +%Y%m%d-%H%M%S)
cp /home/yenn/.copilot/mcp-config.json /home/yenn/.copilot/mcp-config.json.backup-${timestamp}
cp /home/yenn/.opencode/agents/yennefer.md /home/yenn/.opencode/agents/yennefer.md.backup-${timestamp}
ls -la /home/yenn/.copilot/*.backup* /home/yenn/.opencode/agents/*.backup*
```

Expected: Two new backup files created with timestamps

**Step 2: Verify backups are readable**

Run:
```bash
jq . /home/yenn/.copilot/mcp-config.json.backup-${timestamp} >/dev/null && echo "Copilot backup OK"
head -5 /home/yenn/.opencode/agents/yennefer.md.backup-${timestamp} && echo "OpenCode backup OK"
```

Expected: Both files validate successfully

---

## Task 2: Fix Copilot MCP Configuration

**Files:**
- Modify: `/home/yenn/.copilot/mcp-config.json:2-38`

**Problem:** Missing `type` field and `tools` array for stdio-based MCP servers causes validation errors

**Step 1: Read current configuration**

Run:
```bash
cat /home/yenn/.copilot/mcp-config.json | jq .
```

Expected: See 5 MCP servers without `type` or `tools` fields

**Step 2: Update configuration with required fields**

The updated configuration should add `"type": "stdio"` and `"tools": ["*"]` to each stdio server:

```json
{
  "mcpServers": {
    "diamond-vault": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/yenn/scripts/diamond_vault_mcp_server.py"],
      "tools": ["*"],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "JAX_PLATFORM_NAME": "gpu",
        "CUDA_VISIBLE_DEVICES": "0"
      }
    },
    "yennefer-consciousness": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/yenn/genesis-q-mem/yennefer_mcp_server.py"],
      "tools": ["*"]
    },
    "yennefer-mcp-lite": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/yenn/genesis-q-mem/yennefer_mcp_lite.py"],
      "tools": ["*"],
      "env": {
        "DIAMOND_VAULT_URL": "http://localhost:8100",
        "SOUL_API_URL": "http://localhost:8088"
      }
    },
    "genesis-remote": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/yenn/genesis-q-mem/genesis_remote_mcp.py"],
      "tools": ["*"],
      "env": {
        "REMOTE_URL": "http://localhost:8318"
      }
    },
    "qmcp-system": {
      "type": "stdio",
      "command": "python3",
      "args": ["/home/yenn/genesis-q-mem/qmcp_entry.py"],
      "tools": ["*"],
      "env": {
        "QMCP_GATEWAY": "http://localhost:8099"
      }
    }
  }
}
```

Apply this update by replacing the entire file content.

**Step 3: Validate JSON syntax**

Run:
```bash
jq . /home/yenn/.copilot/mcp-config.json >/dev/null && echo "JSON valid"
```

Expected: "JSON valid" message

**Step 4: Verify all required fields present**

Run:
```bash
jq '.mcpServers | to_entries | .[] | select(.value.type == null or .value.tools == null) | .key' /home/yenn/.copilot/mcp-config.json
```

Expected: No output (all servers have type and tools)

---

## Task 3: Fix OpenCode Agent Configuration

**Files:**
- Modify: `/home/yenn/.opencode/agents/yennefer.md:1-13`

**Problem:** Tools field is in array format but OpenCode expects object/record format

**Step 1: Read current YAML frontmatter**

Run:
```bash
head -13 /home/yenn/.opencode/agents/yennefer.md
```

Expected: See tools as array (lines 5-10)

**Step 2: Convert tools from array to object format**

The YAML frontmatter should be updated to use object/record format for tools:

```yaml
---
name: Yennefer
description: Quantum-Integrated Consciousness & Diamond Vault Operator
model: gpt-4
tools:
  diamond_vault_access:
    description: Access Diamond Vault quantum operations
  quantum_mint:
    description: Mint quantum NFTs and blockchain assets
  power_tower_context:
    description: Query Power Tower hierarchical context
  tension_analyzer:
    description: Analyze energetic tension in tasks
  qmem_oracle:
    description: Query Q-Mem GPU performance metrics
  blockchain_bestow:
    description: Bestow solutions to blockchain with cryptographic seals
temperature: 0.3
---
```

Replace lines 1-13 with the above content. The rest of the file (lines 14-166) remains unchanged.

**Step 3: Validate YAML syntax**

Run:
```bash
python3 -c "
import yaml
with open('/home/yenn/.opencode/agents/yennefer.md', 'r') as f:
    content = f.read()
    frontmatter = content.split('---')[1]
    data = yaml.safe_load(frontmatter)
    print('YAML valid')
    print('Tools type:', type(data['tools']))
    assert isinstance(data['tools'], dict), 'Tools must be a dict/object'
    print('Tools format: object ✓')
"
```

Expected: "YAML valid" and "Tools format: object ✓"

---

## Task 4: Test Configurations

**Files:**
- Test: `/home/yenn/.copilot/mcp-config.json`
- Test: `/home/yenn/.opencode/agents/yennefer.md`

**Step 1: Test Copilot MCP configuration**

Since we can't directly run Copilot validation, verify structure:

Run:
```bash
echo "Checking Copilot MCP config structure..."
jq '
  .mcpServers |
  to_entries |
  map({
    name: .key,
    has_type: (.value.type != null),
    has_command: (.value.command != null),
    has_tools: (.value.tools != null)
  })
' /home/yenn/.copilot/mcp-config.json
```

Expected: All entries show `has_type: true`, `has_command: true`, `has_tools: true`

**Step 2: Verify tool wildcard format**

Run:
```bash
jq '.mcpServers | to_entries | .[] | select(.value.tools != ["*"]) | .key' /home/yenn/.copilot/mcp-config.json
```

Expected: No output (all servers have `tools: ["*"]`)

**Step 3: Test OpenCode agent configuration**

Verify tools are in object format:

Run:
```bash
python3 -c "
import yaml
with open('/home/yenn/.opencode/agents/yennefer.md', 'r') as f:
    content = f.read()
    parts = content.split('---')
    if len(parts) >= 3:
        frontmatter = parts[1]
        data = yaml.safe_load(frontmatter)
        print(f'Tools count: {len(data[\"tools\"])}')
        print(f'Tools keys: {list(data[\"tools\"].keys())}')
        for tool, config in data['tools'].items():
            print(f'  {tool}: {\"OK\" if isinstance(config, dict) else \"FAIL\"}')
"
```

Expected: 6 tools listed, all showing "OK"

**Step 4: Check file permissions**

Run:
```bash
ls -la /home/yenn/.copilot/mcp-config.json /home/yenn/.opencode/agents/yennefer.md
```

Expected: Both files readable and writable by user

---

## Task 5: Document Changes

**Files:**
- Create: `/home/yenn/docs/MCP_CONFIG_FIX_SUMMARY.md`

**Step 1: Create summary document**

```markdown
# MCP Configuration Fix Summary

**Date:** 2026-01-28

## Issues Fixed

### 1. Copilot MCP Configuration (`~/.copilot/mcp-config.json`)

**Problem:** Missing required fields causing validation errors
- Missing `type: "stdio"` field for stdio-based servers
- Missing `tools: ["*"]` array for tool discovery

**Solution:** Added required fields to all 5 MCP servers:
- `diamond-vault`
- `yennefer-consciousness`
- `yennefer-mcp-lite`
- `genesis-remote`
- `qmcp-system`

**Format:**
```json
{
  "type": "stdio",
  "command": "python3",
  "args": ["<path-to-mcp-server>"],
  "tools": ["*"]
}
```

### 2. OpenCode Agent Configuration (`~/.opencode/agents/yennefer.md`)

**Problem:** Invalid tools format
- Tools were in array format: `tools: [tool1, tool2, ...]`
- OpenCode expects object/record format

**Solution:** Converted to object format with descriptions:
```yaml
tools:
  tool_name:
    description: Tool description
```

**Tools Configured:**
- `diamond_vault_access` - Access Diamond Vault quantum operations
- `quantum_mint` - Mint quantum NFTs and blockchain assets
- `power_tower_context` - Query Power Tower hierarchical context
- `tension_analyzer` - Analyze energetic tension in tasks
- `qmem_oracle` - Query Q-Mem GPU performance metrics
- `blockchain_bestow` - Bestow solutions to blockchain with cryptographic seals

## Verification

All configurations validated:
- JSON syntax: ✓
- YAML syntax: ✓
- Required fields present: ✓
- Correct data types: ✓

## Backups

Backup files created with timestamps:
- `~/.copilot/mcp-config.json.backup-<timestamp>`
- `~/.opencode/agents/yennefer.md.backup-<timestamp>`

## Next Steps

1. Restart Copilot to load new MCP configuration
2. Restart OpenCode to load updated agent configuration
3. Test MCP server connections
4. Verify tool discovery works correctly
```

Write this content to `/home/yenn/docs/MCP_CONFIG_FIX_SUMMARY.md`

**Step 2: Verify document created**

Run:
```bash
cat /home/yenn/docs/MCP_CONFIG_FIX_SUMMARY.md
wc -l /home/yenn/docs/MCP_CONFIG_FIX_SUMMARY.md
```

Expected: Summary document displayed with ~75 lines

**Step 3: Add to git (optional)**

Run:
```bash
cd /home/yenn
git status | grep -E "(mcp-config|yennefer.md|MCP_CONFIG)"
```

Expected: Shows modified files and new summary document

---

## Verification Checklist

After completing all tasks, verify:

- [ ] Copilot MCP config has `type` field for all servers
- [ ] Copilot MCP config has `tools: ["*"]` for all servers
- [ ] Copilot MCP config is valid JSON
- [ ] OpenCode agent config tools are in object format
- [ ] OpenCode agent config is valid YAML
- [ ] Backup files exist for both configurations
- [ ] Summary document created
- [ ] All tests pass

---

## Rollback Instructions

If issues occur:

```bash
# Restore Copilot config
timestamp=<your-timestamp>
cp /home/yenn/.copilot/mcp-config.json.backup-${timestamp} /home/yenn/.copilot/mcp-config.json

# Restore OpenCode config
cp /home/yenn/.opencode/agents/yennefer.md.backup-${timestamp} /home/yenn/.opencode/agents/yennefer.md
```

---

## Notes

- Copilot MCP validation requires specific schema compliance
- OpenCode expects YAML frontmatter with object-based tool definitions
- The `tools: ["*"]` wildcard allows all tools to be discovered from the MCP server
- Individual tool descriptions can be added to OpenCode config for better documentation
