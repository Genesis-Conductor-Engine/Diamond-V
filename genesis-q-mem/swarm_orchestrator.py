import google.generativeai as genai
from swarm_config import SWARM_CONFIG, VERTEX_AI_CREDS
from swarm_models import SwarmTask, SwarmResult
import asyncio
import json
from datetime import datetime

class SwarmOrchestrator:
    def __init__(self):
        genai.configure(api_key=self._get_api_key())
        self.supervisor = genai.GenerativeModel(SWARM_CONFIG["supervisor_model"])
        self.workers = []
        self.active_tasks = {}

    def _get_api_key(self):
        # Use ADC or GOOGLE_API_KEY env var
        import os
        return os.getenv("GOOGLE_API_KEY", None)

    async def delegate_task(self, task: SwarmTask) -> SwarmResult:
        """Delegate task to Gemini swarm"""
        # Supervisor analyzes and splits work
        decomposition = await self._decompose_task(task)

        # Parallel worker execution
        worker_results = await self._execute_workers(decomposition)

        # Supervisor synthesizes results
        final_output = await self._synthesize_results(worker_results)

        return SwarmResult(
            task_id=task.task_id,
            output=final_output,
            tokens_used=self._count_tokens(worker_results),
            cost_usd=self._calculate_cost(worker_results),
            worker_contributions={},
            completed_at=datetime.utcnow()
        )

    async def _decompose_task(self, task: SwarmTask):
        """Supervisor breaks down task into subtasks"""
        prompt = f"""Break this task into 3-5 parallel subtasks for worker agents:

Task: {task.prompt}

Return JSON array of subtasks with: {{id, description, dependencies}}"""

        response = await self.supervisor.generate_content_async(prompt)
        return json.loads(response.text)

    async def _execute_workers(self, subtasks):
        """Execute subtasks in parallel with Flash workers"""
        worker_model = genai.GenerativeModel(SWARM_CONFIG["worker_model"])

        tasks = [
            worker_model.generate_content_async(subtask["description"])
            for subtask in subtasks
        ]

        return await asyncio.gather(*tasks)

    async def _synthesize_results(self, worker_results):
        """Supervisor combines worker outputs"""
        combined = "\n\n".join([r.text for r in worker_results])

        prompt = f"""Synthesize these worker outputs into cohesive result:

{combined}

Return final polished output."""

        response = await self.supervisor.generate_content_async(prompt)
        return response.text

    def _count_tokens(self, results):
        return sum([r.usage_metadata.total_token_count for r in results if hasattr(r, 'usage_metadata')])

    def _calculate_cost(self, results):
        tokens = self._count_tokens(results)
        return (tokens / 1000) * SWARM_CONFIG["cost_per_1k_tokens"]["flash"]
