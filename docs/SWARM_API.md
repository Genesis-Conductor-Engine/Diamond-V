# Yennefer Swarm API Documentation

## Overview

The Yennefer Swarm API provides cost-effective AI task delegation through a distributed Gemini 2.0 Flash worker architecture with a Gemini 2.0 Pro supervisor. Save 90% on AI API costs compared to Claude Sonnet.

## Base URL

```
http://localhost:8300
```

Production: `https://api.swarm.yennefer.quest`

## Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "swarm_api"
}
```

### POST /api/swarm/delegate

Delegate a task to the Gemini swarm for parallel execution.

**Parameters:**
- `prompt` (string, required): Task description
- `estimated_tokens` (integer, optional): Expected token usage (default: 10000)

**Response:**
```json
{
  "task_id": "uuid-string",
  "output": "result text from swarm",
  "tokens_used": 12500,
  "cost_usd": 0.00187,
  "worker_contributions": {},
  "completed_at": "2026-01-31T12:34:56.789123"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8300/api/swarm/delegate \
  -G --data-urlencode "prompt=Write a Python function to calculate fibonacci numbers" \
  --data-urlencode "estimated_tokens=5000"
```

### GET /api/swarm/cost-estimate

Estimate the cost of a task before delegation.

**Parameters:**
- `tokens` (integer, required): Token count to estimate

**Response:**
```json
{
  "tokens": 50000,
  "cost_usd": 0.0075,
  "savings_vs_claude": 0.0025
}
```

**Example Request:**
```bash
curl http://localhost:8300/api/swarm/cost-estimate?tokens=50000
```

## Authentication

Currently no authentication required for localhost. Production deployment should implement:

```bash
# Header-based API key
X-API-Key: your_api_key_here

# Or query parameter
?api_key=your_api_key_here
```

## Rate Limits

Based on subscription tier:

| Tier | Monthly Tokens | Max Workers | Priority |
|------|---|---|---|
| Starter | 1M | 3 | Normal |
| Pro | 5M | 5 | High |
| Enterprise | Unlimited | 10 | Critical |

## Cost Comparison

**Gemini 2.0 Flash:** $0.15 per 1M tokens
**Claude Sonnet:** $3.00 per 1M tokens

**Example Savings:**
- 50M tokens/month: $7.50 with Swarm vs $150 with Claude (95% savings)
- 1B tokens/month: $150 with Swarm vs $3,000 with Claude (95% savings)

## Error Handling

All errors return standard HTTP status codes with JSON details:

```json
{
  "error": "Error message describing what went wrong",
  "status_code": 400
}
```

Common errors:

| Status | Message | Solution |
|--------|---------|----------|
| 400 | Missing required prompt parameter | Include prompt in request |
| 429 | Rate limit exceeded | Wait or upgrade plan |
| 500 | Swarm processing failed | Retry or contact support |

## Best Practices

1. **Token Estimation**: Overestimate tokens slightly to avoid quota overages
2. **Batch Operations**: Group small tasks for efficiency
3. **Error Handling**: Implement exponential backoff for retries
4. **Caching**: Cache common results to reduce API calls
5. **Monitoring**: Track cost_usd per task to optimize spending

## Examples

### Python

```python
import requests

response = requests.post(
    "http://localhost:8300/api/swarm/delegate",
    params={
        "prompt": "Generate API documentation for this Python module",
        "estimated_tokens": 20000
    }
)

result = response.json()
print(f"Cost: ${result['cost_usd']:.4f}")
print(f"Output:\n{result['output']}")
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const response = await fetch(
  'http://localhost:8300/api/swarm/delegate?' +
  'prompt=Write%20a%20REST%20API&estimated_tokens=10000',
  { method: 'POST' }
);

const result = await response.json();
console.log(`Cost: $${result.cost_usd.toFixed(4)}`);
```

### cURL

```bash
# Delegate a task
curl -X POST http://localhost:8300/api/swarm/delegate \
  -G --data-urlencode "prompt=Your task here" \
  --data-urlencode "estimated_tokens=10000"

# Get cost estimate
curl http://localhost:8300/api/swarm/cost-estimate?tokens=50000
```

## Webhook Events (Coming Soon)

Once task completes:

```json
{
  "event": "task.completed",
  "data": {
    "task_id": "uuid",
    "cost_usd": 0.00187,
    "tokens_used": 12500
  }
}
```

## Support

- Documentation: https://docs.yennefer.quest/swarm
- Issues: support@yennefer.quest
- Discord: https://discord.gg/yennefer
