from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SwarmTask(BaseModel):
    task_id: str
    prompt: str
    complexity: int  # 1-10 scale
    estimated_tokens: int
    assigned_workers: List[str] = []
    status: str = "pending"  # pending, delegated, completed, failed
    created_at: datetime = datetime.utcnow()

class SwarmResult(BaseModel):
    task_id: str
    output: str
    tokens_used: int
    cost_usd: float
    worker_contributions: dict
    completed_at: datetime
