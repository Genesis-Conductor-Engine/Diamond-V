# Yennefer Swarm MCP Integration Guide

## Overview

The Yennefer Swarm is integrated with Claude via MCP (Model Context Protocol), enabling cost-effective AI delegation directly from Claude conversations.

## Available MCP Tools

### swarm_delegate

Delegate a complex task to the Gemini 2.0 Flash swarm for parallel processing.

**When to use:** Tasks requiring >10,000 tokens where cost savings matter

**Parameters:**
- `prompt` (string, required): Detailed task description
- `estimated_tokens` (integer, optional): Expected token count (default: 10000)

**Returns:** SwarmResult with output, cost, and metrics

**Example Usage:**

```json
{
  "tool": "swarm_delegate",
  "arguments": {
    "prompt": "Analyze this codebase and generate comprehensive API documentation with examples for each endpoint",
    "estimated_tokens": 50000
  }
}
```

**Response:**
```json
{
  "task_id": "abc-123-def",
  "output": "# API Documentation\n\n## Endpoints\n...",
  "tokens_used": 47532,
  "cost_usd": 0.00712,
  "worker_contributions": {
    "worker_1": "Section 1: Overview",
    "worker_2": "Section 2: Authentication",
    "worker_3": "Section 3: Endpoints"
  },
  "completed_at": "2026-01-31T14:22:10.123456"
}
```

### swarm_cost_estimate

Estimate the cost of task before delegation.

**When to use:** Before delegating large tasks to understand cost impact

**Parameters:**
- `tokens` (integer, required): Expected token count

**Returns:** Cost estimate with savings comparison

**Example Usage:**

```json
{
  "tool": "swarm_cost_estimate",
  "arguments": {
    "tokens": 100000
  }
}
```

**Response:**
```json
{
  "tokens": 100000,
  "cost_usd": 0.015,
  "savings_vs_claude": 2.985
}
```

## MCP Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yennefer-swarm": {
      "command": "python3",
      "args": ["/home/yenn/genesis-q-mem/yennefer_mcp_lite.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Claude Code

MCP is automatically configured if `yennefer_mcp_lite.py` is running.

## Usage Examples

### Example 1: Code Review

**Claude Prompt:**
> Please use the swarm tool to review this Python codebase and identify security issues, performance bottlenecks, and code quality improvements.

**What happens:**
1. Claude recognizes swarm_delegate is appropriate for large analysis
2. Claude calls swarm_delegate with codebase content
3. Gemini workers analyze different sections in parallel
4. Pro supervisor synthesizes findings
5. Claude receives analysis at 90% cost savings

### Example 2: Cost Estimation

**Claude Prompt:**
> Before you generate comprehensive documentation for our API, estimate the cost using the swarm tool.

**What happens:**
1. Claude calls swarm_cost_estimate with expected token count
2. Claude receives cost: ~$0.015 via Swarm vs $0.30 via Claude
3. Claude confirms with you: "This task will cost $0.015 with Swarm. Proceed?"
4. Upon approval, Claude delegates to swarm_delegate

### Example 3: Bulk Data Processing

**Claude Prompt:**
> Process these 100 customer feedback records and generate a summary report for each, then synthesize trends.

**What happens:**
1. Claude splits work: workers process 20 records each
2. Workers generate summaries in parallel (5x speed)
3. Pro supervisor identifies cross-record trends
4. Result: Same quality, 5x faster, 90% cheaper

## Advanced Configuration

### Custom Worker Count

Modify `genesis-q-mem/swarm_config.py`:

```python
SWARM_CONFIG = {
    "max_workers": 7,  # Default: 5
    # ... other config
}
```

### Token Counting

Claude automatically estimates tokens. For precise counts:

```python
# In your code
estimated_tokens = len(task.split()) * 1.3  # Rough estimate
response = await swarm_delegate_tool(prompt, estimated_tokens)
```

### Fallback Strategy

If swarm API is unavailable, Claude falls back to direct Claude processing:

```python
try:
    result = await swarm_delegate_tool(prompt, tokens)
except Exception:
    # Fallback: Use Claude directly (more expensive)
    result = await claude_direct(prompt)
```

## Cost Optimization Tips

### 1. Batch Similar Tasks
Instead of:
```
Delegate task A ($0.015)
Delegate task B ($0.012)
Delegate task C ($0.018)
Total: $0.045
```

Do:
```
Delegate all three in one prompt ($0.020)
Total: $0.020 (56% savings)
```

### 2. Use for Large Tasks Only

Swarm overhead only pays off for >10k token tasks:
- Task <5k tokens: Use Claude directly
- Task 5-10k tokens: Use swarm if repeating
- Task >10k tokens: Always use swarm

### 3. Monitor Cost_USD

Every swarm response includes `cost_usd`. Track this:

```python
total_cost = 0
for result in results:
    total_cost += result['cost_usd']
    print(f"Task cost: ${result['cost_usd']:.4f}")
print(f"Total: ${total_cost:.4f}")
```

### 4. Cache Results

For repeated tasks, cache swarm outputs:

```python
# On first request
result = swarm_delegate_tool("Analyze this codebase", 50000)
cache[codebase_hash] = result

# On subsequent requests
if codebase_hash in cache:
    return cache[codebase_hash]  # Free!
```

## Integration Patterns

### Pattern 1: Smart Delegation

```
User asks Claude a question
    ↓
Claude evaluates token count
    ↓
If >10k tokens and complex analysis:
    → Use swarm_delegate (90% savings)
Else:
    → Process directly
    ↓
Return result
```

### Pattern 2: Cost-Aware Streaming

```
User asks for long document
    ↓
Claude previews first section directly
    ↓
Claude: "Full generation will cost $0.15 via Swarm vs $3 direct. Use swarm?"
    ↓
User confirms
    ↓
Claude delegates rest to swarm
    ↓
Stream combined result
```

### Pattern 3: Parallel Research

```
User asks: "Research X, Y, and Z"
    ↓
Claude delegates each to separate swarm worker
    ↓
3 workers research in parallel (5x speed)
    ↓
Pro supervisor synthesizes findings
    ↓
Return unified report
```

## Monitoring & Debugging

### Check Swarm Status

```python
import requests

response = requests.get("http://localhost:8300/health")
if response.status_code == 200:
    print("Swarm API healthy")
else:
    print("Swarm API unavailable - falling back to direct Claude")
```

### View MCP Logs

```bash
# Terminal 1: Start MCP with verbose logging
python3 /home/yenn/genesis-q-mem/yennefer_mcp_lite.py

# Terminal 2: View logs
tail -f /tmp/yennefer_mcp.log
```

### Test Tool Directly

```bash
# Test swarm_delegate
python3 -c "
from swarm_mcp_tools import swarm_delegate_tool
result = swarm_delegate_tool('Test prompt', 5000)
print(result)
"
```

## Performance Expectations

| Metric | Swarm | Direct Claude |
|--------|-------|---|
| Latency (50k tokens) | 8-12s | 4-6s |
| Cost | $0.0075 | $0.15 |
| Parallelism | 5 workers | 1 instance |
| Output Quality | Same | - |

For tasks >100k tokens, swarm typically becomes faster due to parallelization.

## Troubleshooting

### Issue: "Tool not found: swarm_delegate"

**Solution:** Ensure MCP server is running:
```bash
ps aux | grep yennefer_mcp_lite
# If not running:
python3 /home/yenn/genesis-q-mem/yennefer_mcp_lite.py &
```

### Issue: "Connection refused: localhost:8300"

**Solution:** Start swarm API:
```bash
cd /home/yenn/genesis-q-mem
python3 swarm_api.py &
```

### Issue: High latency on swarm_delegate

**Solution:** Check Gemini API status:
```bash
curl -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent
```

## Advanced: Custom Swarm Prompts

Modify supervisor/worker prompts in `swarm_orchestrator.py`:

```python
async def _decompose_task(self, task: SwarmTask):
    """Custom decomposition logic"""
    prompt = f"""
    [Your custom instructions]
    Break this task into subtasks:
    {task.prompt}
    """
    # ...
```

## Support & Resources

- **API Docs:** `/home/yenn/docs/SWARM_API.md`
- **Cost Calculator:** https://swarm.yennefer.quest/calculator
- **Status Page:** https://status.yennefer.quest
- **Discord:** https://discord.gg/yennefer-swarm
