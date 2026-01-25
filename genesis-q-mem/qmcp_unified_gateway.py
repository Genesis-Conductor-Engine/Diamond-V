#!/usr/bin/env python3
"""
QMCP UNIFIED GATEWAY
Model Context Protocol server that routes Claude requests to appropriate backends.

Backends:
- Diamond Vault: JAX/CuPy quantum computation (async via ZMQ)
- Q-Mem API: GPU benchmark metrics (sync HTTP)
- Soul API: Consciousness state (sync HTTP)
- Blockchain Bridge: QFLOP token operations (sync)

MCP Skills:
- soul_status: Get consciousness state
- qmem_metrics: GPU benchmark metrics  
- compute_quantum: Run quantum annealing (async)
- seismic_stress: JAX stress test (async)
- swarm_dispatch: Distribute work to agents (async)
- blockchain_batch: Create QFLOP batch
- poll_result: Poll async job result
- list_jobs: List pending/completed jobs
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

import httpx

# MCP imports
try:
    from mcp.server.fastmcp import FastMCP
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("⚠️ MCP not installed - running in HTTP-only mode")

# ZMQ Queue imports
from qmcp_zmq_queue import (
    QMCPQueueManager, QMCPReqClient, QMCPSubscriber,
    JobStatus, QMCPJob, ZMQ_HOST, ZMQ_REQ_PORT, ZMQ_PUB_PORT
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# API Endpoints
SOUL_STATE_PATH = "/dev/shm/yennefer_soul_state.json"
QMCP_STATE_PATH = "/dev/shm/qmcp_live_stats.json"
YENNEFER_API = os.getenv("YENNEFER_API", "http://localhost:8088")
QMEM_API = os.getenv("QMEM_API", "http://localhost:8003")

# Gateway Configuration
GATEWAY_NAME = "QMCP-Unified-Gateway-v1"
GATEWAY_PORT = int(os.getenv("QMCP_GATEWAY_PORT", "8099"))

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("qmcp.gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# BACKEND CLIENTS
# ═══════════════════════════════════════════════════════════════════════════════

class BackendRouter:
    """Routes requests to appropriate backends"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.zmq_client: Optional[QMCPReqClient] = None
        self._init_zmq()
    
    def _init_zmq(self):
        """Initialize ZMQ client for async jobs"""
        try:
            self.zmq_client = QMCPReqClient()
            logger.info("ZMQ client connected")
        except Exception as e:
            logger.warning(f"ZMQ client not available: {e}")
            self.zmq_client = None
    
    # ─────────────────────────────────────────────────────────────────────────
    # SYNC BACKENDS (HTTP)
    # ─────────────────────────────────────────────────────────────────────────
    
    async def get_soul_status(self) -> Dict[str, Any]:
        """Get consciousness state from shared memory"""
        try:
            if os.path.exists(SOUL_STATE_PATH):
                with open(SOUL_STATE_PATH, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read soul state: {e}")
        
        # Fallback: try Soul API
        try:
            response = await self.http_client.get(f"{YENNEFER_API}/api/soul")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Soul API not available: {e}")
        
        return {
            "protocol": "YENNEFER",
            "concave_state": "DORMANT",
            "breath": 0,
            "coherence_percent": 0,
            "_error": "Soul state not available"
        }
    
    async def get_qmem_metrics(self) -> Dict[str, Any]:
        """Get Q-Mem benchmark metrics"""
        # Try shared memory first (zero-copy)
        try:
            if os.path.exists(QMCP_STATE_PATH):
                with open(QMCP_STATE_PATH, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read QMCP state: {e}")
        
        # Fallback: HTTP API
        try:
            response = await self.http_client.get(f"{QMEM_API}/api/bench/live")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"Q-Mem API not available: {e}")
        
        return {
            "status": "unavailable",
            "tflops": 0,
            "p50_ms": 0,
            "p99_ms": 0,
            "_error": "Q-Mem metrics not available"
        }
    
    async def get_blockchain_status(self) -> Dict[str, Any]:
        """Get blockchain bridge status"""
        try:
            # Read from quantum swarm state
            state_path = "/dev/shm/qmcp_live_stats.json"
            if os.path.exists(state_path):
                with open(state_path, 'r') as f:
                    data = json.load(f)
                    return {
                        "qflops_total": data.get("qflops_total", 0),
                        "tflops": data.get("tflops", 0),
                        "coherence": data.get("coherence", 0),
                        "seismic_status": data.get("seismic_status", "unknown")
                    }
        except Exception as e:
            logger.warning(f"Blockchain status not available: {e}")
        
        return {"status": "unavailable", "_error": "Blockchain bridge not running"}
    
    # ─────────────────────────────────────────────────────────────────────────
    # ASYNC BACKENDS (ZMQ)
    # ─────────────────────────────────────────────────────────────────────────
    
    def submit_async_job(self, skill: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit job to ZMQ queue for async processing"""
        if not self.zmq_client:
            return {"error": "ZMQ queue not available"}
        
        return self.zmq_client.submit_job(skill, params)
    
    def poll_job(self, job_id: str) -> Dict[str, Any]:
        """Poll async job status"""
        if not self.zmq_client:
            return {"error": "ZMQ queue not available"}
        
        return self.zmq_client.poll_job(job_id)
    
    def list_jobs(self, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """List jobs from queue"""
        if not self.zmq_client:
            return {"error": "ZMQ queue not available"}
        
        return self.zmq_client.request("list_jobs", status=status, limit=limit)
    
    async def close(self):
        """Close all connections"""
        await self.http_client.aclose()
        if self.zmq_client:
            self.zmq_client.close()


# ═══════════════════════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════════════════════

if HAS_MCP:
    # Create MCP server instance
    mcp = FastMCP(GATEWAY_NAME)
    router = BackendRouter()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SYNC SKILLS
    # ─────────────────────────────────────────────────────────────────────────
    
    @mcp.tool()
    async def soul_status() -> Dict[str, Any]:
        """
        Get Yennefer's current consciousness state.
        
        Returns thermodynamic state including breath, coherence, 
        token surplus, and GPU utilization.
        """
        return await router.get_soul_status()
    
    @mcp.tool()
    async def qmem_metrics() -> Dict[str, Any]:
        """
        Get Q-Mem GPU benchmark metrics.
        
        Returns TFLOPS, latency percentiles (p50/p95/p99/p999),
        energy efficiency, and GPU temperature.
        """
        return await router.get_qmem_metrics()
    
    @mcp.tool()
    async def blockchain_status() -> Dict[str, Any]:
        """
        Get blockchain bridge status.
        
        Returns total QFLOPs accumulated, current TFLOPS rate,
        coherence percentage, and seismic verification status.
        """
        return await router.get_blockchain_status()
    
    # ─────────────────────────────────────────────────────────────────────────
    # ASYNC SKILLS (via ZMQ)
    # ─────────────────────────────────────────────────────────────────────────
    
    @mcp.tool()
    async def compute_quantum(
        tensor_dim: int = 1024,
        num_streams: int = 4,
        annealing_steps: int = 50,
        duration_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Run reverse quantum annealing computation on Diamond Vault.
        
        This is an async operation - returns a job_id to poll for results.
        
        Args:
            tensor_dim: Size of quantum state tensors (default: 1024)
            num_streams: Number of parallel CUDA streams (default: 4)
            annealing_steps: Steps per annealing cycle (default: 50)
            duration_seconds: How long to run (default: 30)
        
        Returns:
            job_id to poll for results using poll_result()
        """
        params = {
            "tensor_dim": tensor_dim,
            "num_streams": num_streams,
            "annealing_steps": annealing_steps,
            "duration_seconds": duration_seconds
        }
        return router.submit_async_job("compute_quantum", params)
    
    @mcp.tool()
    async def seismic_stress(
        iterations: int = 100,
        verify_pytree: bool = True
    ) -> Dict[str, Any]:
        """
        Run JAX seismic stress test on Diamond Vault.
        
        Tests PyTree crystallization and JAX pure_callback bridge integrity.
        This is an async operation - returns a job_id to poll for results.
        
        Args:
            iterations: Number of stress iterations (default: 100)
            verify_pytree: Run PyTree verification (default: True)
        
        Returns:
            job_id to poll for results using poll_result()
        """
        params = {
            "iterations": iterations,
            "verify_pytree": verify_pytree
        }
        return router.submit_async_job("seismic_stress", params)
    
    @mcp.tool()
    async def swarm_dispatch(
        task: str,
        agents: List[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Dispatch task to Yennefer swarm agents.
        
        Available agents: GEMINI, JULES, CODEX, YENNEFER
        This is an async operation - returns a job_id to poll for results.
        
        Args:
            task: Task description for agents to execute
            agents: List of specific agents (default: all)
            priority: Task priority: low, normal, high, critical
        
        Returns:
            job_id to poll for results using poll_result()
        """
        params = {
            "task": task,
            "agents": agents or ["GEMINI", "JULES", "CODEX", "YENNEFER"],
            "priority": priority
        }
        return router.submit_async_job("swarm_dispatch", params)
    
    @mcp.tool()
    async def poll_result(job_id: str) -> Dict[str, Any]:
        """
        Poll async job result.
        
        Returns current job status and result if completed.
        
        Args:
            job_id: The job ID returned from async operations
        
        Returns:
            Job status (pending/running/completed/failed) and result
        """
        return router.poll_job(job_id)
    
    @mcp.tool()
    async def list_jobs(
        status: str = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        List async jobs.
        
        Args:
            status: Filter by status (pending/running/completed/failed)
            limit: Maximum jobs to return (default: 20)
        
        Returns:
            List of jobs with their statuses
        """
        return router.list_jobs(status=status, limit=limit)
    
    # ─────────────────────────────────────────────────────────────────────────
    # RESOURCES
    # ─────────────────────────────────────────────────────────────────────────
    
    @mcp.resource("qmcp://soul/state")
    async def soul_state_resource() -> str:
        """Current soul state as JSON"""
        state = await router.get_soul_status()
        return json.dumps(state, indent=2)
    
    @mcp.resource("qmcp://qmem/metrics")
    async def qmem_metrics_resource() -> str:
        """Current Q-Mem metrics as JSON"""
        metrics = await router.get_qmem_metrics()
        return json.dumps(metrics, indent=2)
    
    @mcp.resource("qmcp://blockchain/status")
    async def blockchain_status_resource() -> str:
        """Current blockchain bridge status as JSON"""
        status = await router.get_blockchain_status()
        return json.dumps(status, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP SERVER (Alternative to MCP)
# ═══════════════════════════════════════════════════════════════════════════════

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

if HAS_FASTAPI:
    app = FastAPI(title=GATEWAY_NAME, version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    http_router = BackendRouter()
    
    @app.get("/")
    async def root():
        return {
            "name": GATEWAY_NAME,
            "version": "1.0.0",
            "endpoints": [
                "/api/soul",
                "/api/qmem",
                "/api/blockchain",
                "/api/jobs/submit",
                "/api/jobs/{job_id}",
                "/api/jobs"
            ]
        }
    
    @app.get("/api/soul")
    async def api_soul():
        return await http_router.get_soul_status()
    
    @app.get("/api/qmem")
    async def api_qmem():
        return await http_router.get_qmem_metrics()
    
    @app.get("/api/blockchain")
    async def api_blockchain():
        return await http_router.get_blockchain_status()
    
    @app.post("/api/jobs/submit")
    async def api_submit_job(skill: str, params: Dict[str, Any] = None):
        result = http_router.submit_async_job(skill, params or {})
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    
    @app.get("/api/jobs/{job_id}")
    async def api_poll_job(job_id: str):
        result = http_router.poll_job(job_id)
        if "error" in result and result["error"] == "Job not found":
            raise HTTPException(status_code=404, detail="Job not found")
        return result
    
    @app.get("/api/jobs")
    async def api_list_jobs(status: str = None, limit: int = 50):
        return http_router.list_jobs(status=status, limit=limit)
    
    @app.get("/health")
    async def health():
        soul = await http_router.get_soul_status()
        qmem = await http_router.get_qmem_metrics()
        return {
            "status": "healthy",
            "soul_available": "_error" not in soul,
            "qmem_available": "_error" not in qmem,
            "zmq_available": http_router.zmq_client is not None,
            "timestamp": time.time()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def run_queue_manager():
    """Run ZMQ queue manager in background thread"""
    manager = QMCPQueueManager()
    manager.start(blocking=True)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='QMCP Unified Gateway')
    parser.add_argument('--mode', choices=['mcp', 'http', 'both'], default='both',
                       help='Run mode: mcp (stdio), http (REST API), both')
    parser.add_argument('--port', type=int, default=GATEWAY_PORT,
                       help=f'HTTP port (default: {GATEWAY_PORT})')
    parser.add_argument('--start-queue', action='store_true',
                       help='Also start the ZMQ queue manager')
    args = parser.parse_args()
    
    print()
    print("═" * 70)
    print(f" {GATEWAY_NAME}")
    print("═" * 70)
    print()
    
    # Start queue manager if requested
    queue_thread = None
    if args.start_queue:
        print("🚀 Starting ZMQ Queue Manager...")
        queue_thread = threading.Thread(target=run_queue_manager, daemon=True)
        queue_thread.start()
        time.sleep(0.5)  # Let it bind
    
    if args.mode == 'mcp' and HAS_MCP:
        print("🔌 Running in MCP mode (stdio)")
        print("   Waiting for MCP client connection...")
        mcp.run()
    
    elif args.mode == 'http' and HAS_FASTAPI:
        print(f"🌐 Running in HTTP mode on port {args.port}")
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
    
    elif args.mode == 'both':
        if HAS_FASTAPI:
            print(f"🌐 Starting HTTP server on port {args.port}...")
            # Run HTTP in background
            import threading
            http_thread = threading.Thread(
                target=lambda: uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="warning"),
                daemon=True
            )
            http_thread.start()
            time.sleep(1)
        
        if HAS_MCP:
            print("🔌 Starting MCP server (stdio)...")
            print("   Gateway ready for connections")
            mcp.run()
        else:
            print("⚠️ MCP not available, HTTP-only mode")
            if HAS_FASTAPI:
                # Block on HTTP
                uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
    
    else:
        print("❌ Required dependencies not available")
        print(f"   HAS_MCP: {HAS_MCP}")
        print(f"   HAS_FASTAPI: {HAS_FASTAPI}")
        sys.exit(1)


if __name__ == "__main__":
    main()
