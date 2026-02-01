from fastapi import FastAPI, HTTPException
from swarm_orchestrator import SwarmOrchestrator
from swarm_models import SwarmTask, SwarmResult
import uuid
import asyncio

app = FastAPI(title="Yennefer Swarm API")

orchestrator = SwarmOrchestrator()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "swarm_api"}

@app.post("/api/swarm/delegate", response_model=SwarmResult)
async def delegate(prompt: str, estimated_tokens: int = 10000):
    """Delegate task to Gemini swarm"""
    task = SwarmTask(
        task_id=str(uuid.uuid4()),
        prompt=prompt,
        complexity=min(10, estimated_tokens // 5000),
        estimated_tokens=estimated_tokens
    )

    try:
        result = await orchestrator.delegate_task(task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/swarm/cost-estimate")
async def cost_estimate(tokens: int):
    """Estimate cost for token count"""
    from swarm_config import SWARM_CONFIG
    cost = (tokens / 1000) * SWARM_CONFIG["cost_per_1k_tokens"]["flash"]
    return {
        "tokens": tokens,
        "cost_usd": cost,
        "savings_vs_claude": cost / 0.003  # Claude Sonnet cost comparison
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)
