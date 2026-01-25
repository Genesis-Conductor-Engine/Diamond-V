#!/usr/bin/env python3
"""
QMCP DIAMOND WORKER
ZMQ worker that pulls jobs from the queue and executes them on the Diamond Vault
(quantum_swarm_blockchain_bridge.py).

Job Types:
- compute_quantum: Run reverse quantum annealing
- seismic_stress: Run JAX stress test
- swarm_dispatch: Dispatch task to swarm agents

Architecture:
- PULL jobs from ZMQ queue (port 5557)
- Execute on GPU via CuPy/JAX
- Report results via REQ to gateway (port 5555)
"""

import os
import sys
import json
import time
import uuid
import signal
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cupy as cp
import numpy as np

# ZMQ Queue imports
from qmcp_zmq_queue import (
    QMCPWorkerQueue, QMCPResultReporter, QMCPJob,
    ZMQ_HOST, ZMQ_PUSH_PORT, ZMQ_REQ_PORT
)

# Import quantum components
try:
    from quantum_swarm_blockchain_bridge import (
        ReverseQuantumAnnealingEngine, SwarmCoordinator, 
        ThermalManager, SeismicVerification,
        TENSOR_DIM, NUM_STREAMS, OVERCLOCK_FACTOR
    )
    HAS_QUANTUM = True
except ImportError as e:
    print(f"⚠️ Quantum bridge not available: {e}")
    HAS_QUANTUM = False

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

WORKER_ID = os.getenv("QMCP_WORKER_ID", f"diamond-{uuid.uuid4().hex[:8]}")
POLL_TIMEOUT_MS = 5000
MAX_JOB_DURATION = 300  # 5 minutes max per job

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(f"qmcp.worker.{WORKER_ID}")

# ═══════════════════════════════════════════════════════════════════════════════
# JOB HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

class DiamondWorker:
    """Diamond Vault worker that executes quantum computation jobs"""
    
    def __init__(self, worker_id: str = WORKER_ID):
        self.worker_id = worker_id
        self.running = False
        
        # Initialize GPU resources (lazy)
        self.engine: Optional[ReverseQuantumAnnealingEngine] = None
        self.swarm: Optional[SwarmCoordinator] = None
        self.thermal: Optional[ThermalManager] = None
        self.seismic: Optional[SeismicVerification] = None
        
        # ZMQ connections
        self.job_queue: Optional[QMCPWorkerQueue] = None
        self.reporter: Optional[QMCPResultReporter] = None
        
        # Statistics
        self.jobs_completed = 0
        self.jobs_failed = 0
        self.total_qflops = 0
        self.start_time = time.time()
        
        # Register job handlers
        self.handlers: Dict[str, callable] = {
            "compute_quantum": self._handle_compute_quantum,
            "seismic_stress": self._handle_seismic_stress,
            "swarm_dispatch": self._handle_swarm_dispatch,
            "test_skill": self._handle_test_skill,
        }
        
        logger.info(f"Diamond Worker initialized: {worker_id}")
    
    def _init_quantum_resources(self, tensor_dim: int = TENSOR_DIM, num_streams: int = NUM_STREAMS):
        """Lazy initialization of quantum resources"""
        if not HAS_QUANTUM:
            raise RuntimeError("Quantum bridge not available")
        
        if self.engine is None:
            logger.info("Initializing quantum resources...")
            self.thermal = ThermalManager()
            self.seismic = SeismicVerification()
            self.engine = ReverseQuantumAnnealingEngine(
                tensor_dim=tensor_dim,
                num_streams=num_streams
            )
            self.swarm = SwarmCoordinator(self.engine)
            logger.info("Quantum resources ready")
    
    # ─────────────────────────────────────────────────────────────────────────
    # JOB HANDLERS
    # ─────────────────────────────────────────────────────────────────────────
    
    def _handle_compute_quantum(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute reverse quantum annealing"""
        tensor_dim = params.get("tensor_dim", TENSOR_DIM)
        num_streams = params.get("num_streams", NUM_STREAMS)
        duration_seconds = params.get("duration_seconds", 30)
        
        self._init_quantum_resources(tensor_dim, num_streams)
        
        start_time = time.time()
        iterations = 0
        coherence_history = []
        
        end_time = start_time + min(duration_seconds, MAX_JOB_DURATION)
        
        while time.time() < end_time:
            # Run annealing cycle
            results = self.swarm.distribute_work()
            iterations += 1
            coherence_history.append(results['coherence'])
            
            # Thermal management
            self.thermal.get_gpu_temperature()
            throttle = self.thermal.get_throttle_factor()
            
            if throttle < 0.8:
                time.sleep(0.1)  # Cool down
        
        elapsed = time.time() - start_time
        total_qflops = self.engine.total_qflops
        tflops = total_qflops / elapsed / 1e12
        
        self.total_qflops += total_qflops
        
        return {
            "status": "completed",
            "duration_seconds": elapsed,
            "iterations": iterations,
            "total_qflops": total_qflops,
            "tflops": tflops,
            "tflops_overclocked": tflops * OVERCLOCK_FACTOR,
            "avg_coherence": np.mean(coherence_history),
            "thermal": self.thermal.get_stats(),
            "worker_id": self.worker_id
        }
    
    def _handle_seismic_stress(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JAX seismic stress test"""
        iterations = params.get("iterations", 100)
        verify_pytree = params.get("verify_pytree", True)
        
        self._init_quantum_resources()
        
        start_time = time.time()
        results = []
        
        # Run seismic verification
        if verify_pytree:
            seismic_result = self.seismic.run_pytree_crystallization_test()
            results.append({
                "test": "pytree_crystallization",
                "status": seismic_result["status"],
                "coherence": seismic_result.get("coherence", 0)
            })
        
        # Run stress iterations
        for i in range(iterations):
            # Create random PyTree-like structure
            state = {
                "layer_1": cp.random.randn(256, 256).astype(cp.float32),
                "layer_2": cp.random.randn(256).astype(cp.float32),
                "iteration": i
            }
            
            # Stress operation: matrix multiply
            result = cp.dot(state["layer_1"], state["layer_1"].T)
            checksum = float(cp.sum(result).get())
            
            if i % 20 == 0:
                results.append({
                    "iteration": i,
                    "checksum": checksum,
                    "temp": self.thermal.get_gpu_temperature()
                })
        
        elapsed = time.time() - start_time
        
        return {
            "status": "completed",
            "duration_seconds": elapsed,
            "iterations": iterations,
            "pytree_verified": verify_pytree,
            "seismic_tests_passed": self.seismic.tests_passed,
            "seismic_tests_failed": self.seismic.tests_failed,
            "samples": results[:10],  # Return first 10 samples
            "thermal": self.thermal.get_stats(),
            "worker_id": self.worker_id
        }
    
    def _handle_swarm_dispatch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task to swarm agents"""
        task = params.get("task", "default_task")
        agents = params.get("agents", ["GEMINI", "JULES", "CODEX", "YENNEFER"])
        priority = params.get("priority", "normal")
        
        self._init_quantum_resources()
        
        start_time = time.time()
        
        # Execute one round of swarm work
        results = self.swarm.distribute_work()
        
        # Get agent statistics
        agent_stats = []
        for agent in self.swarm.agents:
            if agent.agent_id in agents:
                agent_stats.append({
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "qflops_generated": agent.qflops_generated,
                    "tasks_completed": agent.tasks_completed
                })
        
        elapsed = time.time() - start_time
        
        return {
            "status": "completed",
            "task": task,
            "priority": priority,
            "duration_seconds": elapsed,
            "agents_dispatched": len(agent_stats),
            "agent_stats": agent_stats,
            "consensus": self.swarm.consensus,
            "coherence": results['coherence'],
            "energy": results['energy'],
            "qflops": results['qflops'],
            "worker_id": self.worker_id
        }
    
    def _handle_test_skill(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simple test skill for validation"""
        return {
            "status": "completed",
            "echo": params,
            "worker_id": self.worker_id,
            "timestamp": time.time()
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────────────────────────────────
    
    def connect(self, host: str = ZMQ_HOST):
        """Connect to ZMQ queue"""
        logger.info(f"Connecting to ZMQ queue at {host}...")
        self.job_queue = QMCPWorkerQueue(host=host)
        self.reporter = QMCPResultReporter(host=host)
        logger.info("ZMQ connections established")
    
    def process_job(self, job: QMCPJob) -> None:
        """Process a single job"""
        logger.info(f"Processing job {job.job_id} ({job.skill})")
        
        # Report started
        try:
            self.reporter.report_started(job.job_id, self.worker_id)
        except Exception as e:
            logger.warning(f"Failed to report job started: {e}")
        
        # Execute handler
        handler = self.handlers.get(job.skill)
        if not handler:
            error = f"Unknown skill: {job.skill}"
            logger.error(error)
            try:
                self.reporter.report_failed(job.job_id, error)
            except:
                pass
            self.jobs_failed += 1
            return
        
        try:
            result = handler(job.params)
            self.reporter.report_completed(job.job_id, result)
            self.jobs_completed += 1
            logger.info(f"Job {job.job_id} completed successfully")
        except Exception as e:
            error = str(e)
            logger.error(f"Job {job.job_id} failed: {error}")
            try:
                self.reporter.report_failed(job.job_id, error)
            except:
                pass
            self.jobs_failed += 1
    
    def run(self, host: str = ZMQ_HOST):
        """Main worker loop"""
        self.connect(host)
        self.running = True
        
        print()
        print("═" * 70)
        print(f" QMCP DIAMOND WORKER: {self.worker_id}")
        print("═" * 70)
        print(f"   Host: {host}")
        print(f"   Job queue port: {ZMQ_PUSH_PORT}")
        print(f"   Reporter port: {ZMQ_REQ_PORT}")
        print(f"   Skills: {list(self.handlers.keys())}")
        print("═" * 70)
        print()
        print("⏳ Waiting for jobs...")
        
        while self.running:
            try:
                job = self.job_queue.pull_job(timeout_ms=POLL_TIMEOUT_MS)
                if job:
                    self.process_job(job)
                else:
                    # No job, print periodic status
                    pass
            except KeyboardInterrupt:
                logger.info("Received interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                time.sleep(1)
        
        self._print_stats()
        self.close()
    
    def _print_stats(self):
        """Print worker statistics"""
        elapsed = time.time() - self.start_time
        print()
        print("═" * 70)
        print(" WORKER STATISTICS")
        print("═" * 70)
        print(f"   Worker ID: {self.worker_id}")
        print(f"   Uptime: {elapsed:.1f}s")
        print(f"   Jobs completed: {self.jobs_completed}")
        print(f"   Jobs failed: {self.jobs_failed}")
        print(f"   Total QFLOPs: {self.total_qflops:,.0f}")
        print("═" * 70)
    
    def stop(self):
        """Stop the worker"""
        self.running = False
    
    def close(self):
        """Close connections"""
        if self.job_queue:
            self.job_queue.close()
        if self.reporter:
            self.reporter.close()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='QMCP Diamond Worker')
    parser.add_argument('--host', default=ZMQ_HOST,
                       help=f'ZMQ queue host (default: {ZMQ_HOST})')
    parser.add_argument('--worker-id', default=None,
                       help='Worker ID (default: auto-generated)')
    args = parser.parse_args()
    
    worker_id = args.worker_id or WORKER_ID
    worker = DiamondWorker(worker_id=worker_id)
    
    # Handle signals
    def signal_handler(sig, frame):
        print("\n🛑 Shutdown signal received")
        worker.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    worker.run(host=args.host)


if __name__ == "__main__":
    main()
