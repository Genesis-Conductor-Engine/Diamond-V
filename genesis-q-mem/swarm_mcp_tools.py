import requests

SWARM_API_URL = "http://localhost:8300"

def swarm_delegate_tool(prompt: str, estimated_tokens: int = 10000):
    """
    Delegate complex task to Gemini swarm (cost-effective for >10k token tasks)

    Args:
        prompt: Task description
        estimated_tokens: Expected token usage

    Returns:
        SwarmResult with output and cost metrics
    """
    response = requests.post(
        f"{SWARM_API_URL}/api/swarm/delegate",
        params={"prompt": prompt, "estimated_tokens": estimated_tokens}
    )
    response.raise_for_status()
    return response.json()

def swarm_cost_estimate_tool(tokens: int):
    """Get cost estimate for swarm delegation"""
    response = requests.get(
        f"{SWARM_API_URL}/api/swarm/cost-estimate",
        params={"tokens": tokens}
    )
    response.raise_for_status()
    return response.json()

MCP_TOOLS = [
    {
        "name": "swarm_delegate",
        "description": "Delegate complex task to cost-effective Gemini 2.0 Flash swarm (90% cheaper than Claude for bulk operations)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "estimated_tokens": {"type": "integer", "default": 10000}
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "swarm_cost_estimate",
        "description": "Estimate cost savings for swarm delegation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tokens": {"type": "integer"}
            },
            "required": ["tokens"]
        }
    }
]
