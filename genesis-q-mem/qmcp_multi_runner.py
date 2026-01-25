#!/usr/bin/env python3
"""
QMCP MULTI-RUNNER DISPATCHER
Dispatches GPU/CPU jobs to multiple GitHub Actions runners:
  - GPU Runner (Tesla T4) - quantum annealing, seismic tests
  - CPU Orchestrator (96-core) - coordination, data processing
  - Dual Bridge - parallel GPU+CPU for maximum QFLOP yield

Usage:
    python3 qmcp_multi_runner.py --runner gpu --vector quantum --duration 60
    python3 qmcp_multi_runner.py --runner dual --duration 10
    python3 qmcp_multi_runner.py --runner cpu --task orchestrate
"""

import os
import sys
import json
import time
import uuid
import asyncio
import subprocess
import argparse
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

GITHUB_REPO = os.getenv("QMCP_GITHUB_REPO", "Genesis-Conductor-Engine/Yennefer")

# Runner configurations
RUNNERS = {
    "gpu": {
        "workflow": "diamond_node.yml",
        "name": "Tesla T4 GPU",
        "label": "GPU",
        "capabilities": ["quantum", "seismic", "swarm", "cuda"],
        "default_duration": 60
    },
    "gpu-maxpower": {
        "workflow": "gpu-qflop-runner.yml",
        "name": "GPU QFLOP MaxPower",
        "label": "ubuntu-gpu",
        "capabilities": ["qflop", "maxpower", "mining"],
        "default_duration": 60
    },
    "cpu": {
        "workflow": "qflop-dual-bridge.yml",
        "name": "96-Core CPU Orchestrator",
        "label": "ubuntu-latest-m",
        "capabilities": ["orchestrate", "coordinate", "process"],
        "default_duration": 10
    },
    "dual": {
        "workflow": "qflop-dual-bridge.yml",
        "name": "Dual Bridge (GPU + 96-Core CPU)",
        "label": "dual",
        "capabilities": ["bridge", "parallel", "sync"],
        "default_duration": 10
    }
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DISPATCHER] %(levelname)s: %(message)s"
)
logger = logging.getLogger("qmcp.dispatcher")

# ═══════════════════════════════════════════════════════════════════════════════
# DISPATCHER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class MultiRunnerDispatcher:
    """Dispatches jobs to multiple GitHub Actions runners"""
    
    def __init__(self, repo: str = GITHUB_REPO):
        self.repo = repo
        self.active_runs: Dict[str, Dict] = {}
    
    def dispatch_gpu(self, vector: str = "quantum", duration: int = 60, 
                     precision: float = 0.1) -> Optional[str]:
        """Dispatch to GPU runner (Tesla T4)"""
        job_id = str(uuid.uuid4())
        
        cmd = [
            "gh", "workflow", "run", "diamond_node.yml",
            "--repo", self.repo,
            "-f", f"job_id={job_id}",
            "-f", f"vector={vector}",
            "-f", f"precision={precision}",
            "-f", f"duration={duration}"
        ]
        
        logger.info(f"🚀 Dispatching GPU job: {job_id} (vector={vector})")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            run_id = self._get_latest_run_id("diamond_node.yml")
            
            self.active_runs[job_id] = {
                "runner": "gpu",
                "run_id": run_id,
                "vector": vector,
                "started": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ GPU job dispatched (Run ID: {run_id})")
            return run_id
        except Exception as e:
            logger.error(f"❌ GPU dispatch failed: {e}")
            return None
    
    def dispatch_maxpower(self, duration: int = 60, power_mode: str = "maxpower",
                          mint_tokens: bool = True) -> Optional[str]:
        """Dispatch to GPU QFLOP MaxPower runner"""
        cmd = [
            "gh", "workflow", "run", "gpu-qflop-runner.yml",
            "--repo", self.repo,
            "-f", f"duration_minutes={duration}",
            "-f", f"power_mode={power_mode}",
            "-f", f"mint_tokens={str(mint_tokens).lower()}"
        ]
        
        logger.info(f"⚡ Dispatching MaxPower job (duration={duration}min, mode={power_mode})")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            run_id = self._get_latest_run_id("gpu-qflop-runner.yml")
            
            job_id = f"maxpower-{run_id}"
            self.active_runs[job_id] = {
                "runner": "gpu-maxpower",
                "run_id": run_id,
                "power_mode": power_mode,
                "started": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ MaxPower job dispatched (Run ID: {run_id})")
            return run_id
        except Exception as e:
            logger.error(f"❌ MaxPower dispatch failed: {e}")
            return None
    
    def dispatch_dual_bridge(self, duration: int = 10, 
                             power_mode: str = "maxpower") -> Optional[str]:
        """Dispatch to Dual Bridge (96-core CPU + GPU parallel)"""
        cmd = [
            "gh", "workflow", "run", "qflop-dual-bridge.yml",
            "--repo", self.repo,
            "-f", f"duration_minutes={duration}",
            "-f", f"power_mode={power_mode}"
        ]
        
        logger.info(f"🔀 Dispatching Dual Bridge (duration={duration}min)")
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            run_id = self._get_latest_run_id("qflop-dual-bridge.yml")
            
            job_id = f"dual-{run_id}"
            self.active_runs[job_id] = {
                "runner": "dual",
                "run_id": run_id,
                "power_mode": power_mode,
                "started": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Dual Bridge dispatched (Run ID: {run_id})")
            return run_id
        except Exception as e:
            logger.error(f"❌ Dual Bridge dispatch failed: {e}")
            return None
    
    def _get_latest_run_id(self, workflow: str) -> Optional[str]:
        """Get the latest run ID for a workflow"""
        time.sleep(3)  # Wait for run to spawn
        
        cmd = [
            "gh", "run", "list",
            "--workflow", workflow,
            "--repo", self.repo,
            "--limit", "1",
            "--json", "databaseId",
            "-q", ".[0].databaseId"
        ]
        
        try:
            result = subprocess.check_output(cmd, text=True, timeout=30)
            return result.strip()
        except:
            return None
    
    def get_run_status(self, run_id: str) -> Dict:
        """Get status of a workflow run"""
        cmd = [
            "gh", "run", "view", run_id,
            "--repo", self.repo,
            "--json", "status,conclusion,jobs"
        ]
        
        try:
            result = subprocess.check_output(cmd, text=True, timeout=30)
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
    
    def stream_logs(self, run_id: str, tail: int = 50) -> str:
        """Stream logs from a workflow run"""
        cmd = [
            "gh", "run", "view", run_id,
            "--repo", self.repo,
            "--log"
        ]
        
        try:
            result = subprocess.check_output(cmd, text=True, timeout=60)
            lines = result.split('\n')
            return '\n'.join(lines[-tail:])
        except Exception as e:
            return f"Error: {e}"
    
    def list_runners(self) -> None:
        """Display available runners"""
        print()
        print("═" * 70)
        print(" AVAILABLE RUNNERS")
        print("═" * 70)
        
        for key, config in RUNNERS.items():
            print(f"\n  {key}:")
            print(f"    Name: {config['name']}")
            print(f"    Workflow: {config['workflow']}")
            print(f"    Label: {config['label']}")
            print(f"    Capabilities: {', '.join(config['capabilities'])}")
        
        print()
        print("═" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# ZMQ INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

def connect_to_mesh(dispatcher: MultiRunnerDispatcher):
    """Connect dispatcher to local ZMQ mesh for automatic job routing"""
    try:
        import zmq
    except ImportError:
        logger.warning("ZMQ not available - running in standalone mode")
        return
    
    ZMQ_PUB_PORT = int(os.getenv("QMCP_ZMQ_PUB_PORT", "5566"))
    ZMQ_SUB_PORT = int(os.getenv("QMCP_ZMQ_SUB_PORT", "5565"))
    
    context = zmq.Context()
    
    # Subscribe to remote compute requests
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://127.0.0.1:{ZMQ_PUB_PORT}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "REMOTE_COMPUTE")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "GPU_DISPATCH")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "DUAL_DISPATCH")
    
    # Publisher for results
    publisher = context.socket(zmq.PUB)
    publisher.connect(f"tcp://127.0.0.1:{ZMQ_SUB_PORT}")
    
    logger.info(f"🔌 Connected to ZMQ mesh (SUB:{ZMQ_PUB_PORT}, PUB:{ZMQ_SUB_PORT})")
    
    while True:
        try:
            if subscriber.poll(1000):
                topic, message = subscriber.recv_multipart()
                topic_str = topic.decode()
                payload = json.loads(message.decode())
                
                logger.info(f"📨 Received: {topic_str} - {payload.get('id', 'unknown')}")
                
                run_id = None
                
                if topic_str == "GPU_DISPATCH" or payload.get("runner") == "gpu":
                    run_id = dispatcher.dispatch_gpu(
                        vector=payload.get("vector", "quantum"),
                        duration=payload.get("duration", 60)
                    )
                elif topic_str == "DUAL_DISPATCH" or payload.get("runner") == "dual":
                    run_id = dispatcher.dispatch_dual_bridge(
                        duration=payload.get("duration", 10)
                    )
                elif payload.get("runner") == "maxpower":
                    run_id = dispatcher.dispatch_maxpower(
                        duration=payload.get("duration", 60)
                    )
                else:
                    # Default to GPU
                    run_id = dispatcher.dispatch_gpu(
                        vector=payload.get("vector", "quantum"),
                        duration=payload.get("duration", 60)
                    )
                
                # Publish result
                result = {
                    "job_id": payload.get("id"),
                    "run_id": run_id,
                    "status": "dispatched" if run_id else "failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
                publisher.send_multipart([
                    b"JOB_DISPATCHED",
                    json.dumps(result).encode()
                ])
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Mesh error: {e}")
    
    subscriber.close()
    publisher.close()
    context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='QMCP Multi-Runner Dispatcher')
    parser.add_argument('--runner', type=str, default='gpu',
                       choices=['gpu', 'gpu-maxpower', 'dual', 'cpu'],
                       help='Runner to dispatch to')
    parser.add_argument('--vector', type=str, default='quantum',
                       choices=['quantum', 'seismic', 'swarm'],
                       help='Compute vector (for GPU runner)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration in seconds (GPU) or minutes (others)')
    parser.add_argument('--power-mode', type=str, default='maxpower',
                       choices=['maxpower', 'balanced', 'efficient'],
                       help='Power mode for GPU runners')
    parser.add_argument('--list', action='store_true',
                       help='List available runners')
    parser.add_argument('--mesh', action='store_true',
                       help='Connect to ZMQ mesh and auto-route jobs')
    parser.add_argument('--status', type=str, metavar='RUN_ID',
                       help='Get status of a workflow run')
    parser.add_argument('--logs', type=str, metavar='RUN_ID',
                       help='Stream logs from a workflow run')
    
    args = parser.parse_args()
    
    dispatcher = MultiRunnerDispatcher()
    
    if args.list:
        dispatcher.list_runners()
        return
    
    if args.status:
        status = dispatcher.get_run_status(args.status)
        print(json.dumps(status, indent=2))
        return
    
    if args.logs:
        logs = dispatcher.stream_logs(args.logs)
        print(logs)
        return
    
    if args.mesh:
        print()
        print("═" * 70)
        print(" QMCP MULTI-RUNNER DISPATCHER (Mesh Mode)")
        print("═" * 70)
        print(f"   Repository: {GITHUB_REPO}")
        print(f"   Listening for: REMOTE_COMPUTE, GPU_DISPATCH, DUAL_DISPATCH")
        print("═" * 70)
        print()
        connect_to_mesh(dispatcher)
        return
    
    # Single dispatch mode
    print()
    print("═" * 70)
    print(f" DISPATCHING TO: {RUNNERS[args.runner]['name']}")
    print("═" * 70)
    
    run_id = None
    
    if args.runner == 'gpu':
        run_id = dispatcher.dispatch_gpu(
            vector=args.vector,
            duration=args.duration
        )
    elif args.runner == 'gpu-maxpower':
        run_id = dispatcher.dispatch_maxpower(
            duration=args.duration,
            power_mode=args.power_mode
        )
    elif args.runner in ['dual', 'cpu']:
        run_id = dispatcher.dispatch_dual_bridge(
            duration=args.duration,
            power_mode=args.power_mode
        )
    
    if run_id:
        print()
        print(f"  ✅ Dispatched successfully")
        print(f"  Run ID: {run_id}")
        print(f"  Monitor: gh run view {run_id} --repo {GITHUB_REPO}")
        print(f"  Logs: gh run view {run_id} --repo {GITHUB_REPO} --log")
    else:
        print(f"  ❌ Dispatch failed")
    
    print()
    print("═" * 70)


if __name__ == "__main__":
    main()
