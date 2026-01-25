#!/usr/bin/env python3
"""
QMCP BLOCKCHAIN-DUAL BRIDGE INTEGRATOR
Pairs 25% local blockchain allocation with remote Dual Bridge resources.

This creates a unified pipeline:
  LOCAL (25%) ←→ DUAL BRIDGE (96-core + T4)
  
Flow:
1. Local blockchain jobs use 25% allocated GPU/CPU
2. When local capacity exhausted → overflow to Dual Bridge
3. QFLOP minting results sync back via ZMQ
4. Asset production runs continuously on both local + remote

Author: Yennefer Genesis Conductor
Date: 2026-01-25
"""

import os
import sys
import json
import time
import uuid
import asyncio
import threading
import subprocess
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import zmq
    HAS_ZMQ = True
except ImportError:
    HAS_ZMQ = False
    print("⚠️ ZMQ not available - running in standalone mode")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

GITHUB_REPO = os.getenv("QMCP_GITHUB_REPO", "Genesis-Conductor-Engine/Yennefer")
SHARED_MEM_PATH = "/dev/shm/qmcp_blockchain_bridge.json"
ALLOCATION_PATH = "/dev/shm/qmcp_resource_allocation.json"

# ZMQ Ports
ZMQ_SUB_PORT = 5565
ZMQ_PUB_PORT = 5566
ZMQ_PUSH_PORT = 5567

# Allocation policy
BLOCKCHAIN_ALLOCATION = 0.25  # 25%
LOCAL_GPU_RESERVED_MB = 1024  # 1GB for blockchain
REMOTE_OVERFLOW_THRESHOLD = 0.80  # 80% local usage triggers remote

class JobType(Enum):
    QFLOP_MINT = "qflop_mint"
    NFT_VERIFY = "nft_verify"
    SEISMIC_BLOCKCHAIN = "seismic_blockchain"
    TOKEN_BRIDGE = "token_bridge"
    DUAL_COMPUTE = "dual_compute"

class JobTarget(Enum):
    LOCAL = "local"
    REMOTE_GPU = "remote_gpu"
    REMOTE_DUAL = "remote_dual"
    AUTO = "auto"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class BlockchainJob:
    """A blockchain/asset production job"""
    id: str
    type: JobType
    target: JobTarget
    payload: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict] = None
    run_id: Optional[str] = None  # GitHub Actions run ID if remote

@dataclass
class BridgeState:
    """Current state of the blockchain-dual bridge"""
    local_jobs: int = 0
    remote_jobs: int = 0
    local_gpu_util: float = 0.0
    local_gpu_memory_mb: int = 0
    remote_runs_active: int = 0
    total_qflops_minted: float = 0.0
    total_jobs_completed: int = 0
    overflow_to_remote: bool = False
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN-DUAL BRIDGE INTEGRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainDualBridgeIntegrator:
    """
    Integrates 25% local blockchain allocation with remote Dual Bridge.
    
    Capabilities:
    - Routes blockchain jobs to local or remote based on capacity
    - Maintains 25% allocation policy
    - Syncs QFLOP minting between local and remote
    - Tracks asset production across both environments
    """
    
    def __init__(self, auto_overflow: bool = True):
        self.auto_overflow = auto_overflow
        self.state = BridgeState()
        self.pending_jobs: List[BlockchainJob] = []
        self.active_jobs: Dict[str, BlockchainJob] = {}
        self.completed_jobs: List[BlockchainJob] = []
        self.lock = threading.Lock()
        
        # ZMQ connections (lazy init)
        self.zmq_context: Optional[zmq.Context] = None
        self.zmq_publisher: Optional[zmq.Socket] = None
        self.zmq_subscriber: Optional[zmq.Socket] = None
        
        self._write_state()
        print(f"✅ Blockchain-Dual Bridge Integrator initialized")
        print(f"   └── Local allocation: {BLOCKCHAIN_ALLOCATION * 100:.0f}%")
        print(f"   └── Reserved GPU memory: {LOCAL_GPU_RESERVED_MB} MB")
        print(f"   └── Overflow threshold: {REMOTE_OVERFLOW_THRESHOLD * 100:.0f}%")
        print(f"   └── Auto-overflow: {auto_overflow}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # GPU MONITORING
    # ─────────────────────────────────────────────────────────────────────────
    
    def _get_gpu_stats(self) -> tuple:
        """Get current GPU utilization and memory"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", 
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(", ")
                return float(parts[0]), int(parts[1]), int(parts[2])
        except:
            pass
        return 0.0, 0, 4096
    
    def _update_state(self):
        """Update bridge state from current metrics"""
        gpu_util, gpu_mem_used, gpu_mem_total = self._get_gpu_stats()
        
        self.state.local_gpu_util = gpu_util
        self.state.local_gpu_memory_mb = gpu_mem_used
        self.state.local_jobs = len([j for j in self.active_jobs.values() 
                                     if j.target == JobTarget.LOCAL])
        self.state.remote_jobs = len([j for j in self.active_jobs.values() 
                                      if j.target in [JobTarget.REMOTE_GPU, JobTarget.REMOTE_DUAL]])
        
        # Check if we should overflow to remote
        local_capacity_used = gpu_util / 100.0
        blockchain_util = local_capacity_used * BLOCKCHAIN_ALLOCATION
        self.state.overflow_to_remote = blockchain_util >= (REMOTE_OVERFLOW_THRESHOLD * BLOCKCHAIN_ALLOCATION)
        
        self.state.last_updated = datetime.utcnow().isoformat()
    
    # ─────────────────────────────────────────────────────────────────────────
    # JOB ROUTING
    # ─────────────────────────────────────────────────────────────────────────
    
    def _determine_target(self, job_type: JobType) -> JobTarget:
        """Determine optimal target for a job based on current state"""
        self._update_state()
        
        # Heavy compute jobs → prefer remote dual bridge
        if job_type in [JobType.SEISMIC_BLOCKCHAIN, JobType.DUAL_COMPUTE]:
            return JobTarget.REMOTE_DUAL
        
        # Check local capacity
        if self.state.overflow_to_remote and self.auto_overflow:
            # Local at capacity → overflow to remote
            if job_type == JobType.QFLOP_MINT:
                return JobTarget.REMOTE_GPU  # GPU minting
            else:
                return JobTarget.REMOTE_DUAL
        
        # Default to local if capacity available
        return JobTarget.LOCAL
    
    # ─────────────────────────────────────────────────────────────────────────
    # LOCAL EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    
    def _execute_local(self, job: BlockchainJob) -> bool:
        """Execute a job on local resources"""
        job.started_at = datetime.utcnow().isoformat()
        job.status = "running"
        
        try:
            if job.type == JobType.QFLOP_MINT:
                # Trigger local minter
                result = subprocess.run(
                    ["npx", "pm2", "trigger", "qflop-minter", "mint",
                     json.dumps(job.payload)],
                    capture_output=True, text=True, timeout=60
                )
                success = result.returncode == 0
                job.result = {"output": result.stdout, "local": True}
                
            elif job.type == JobType.TOKEN_BRIDGE:
                # Use eth-bridge
                result = subprocess.run(
                    ["npx", "pm2", "trigger", "eth-bridge", "transfer",
                     json.dumps(job.payload)],
                    capture_output=True, text=True, timeout=60
                )
                success = result.returncode == 0
                job.result = {"output": result.stdout, "local": True}
                
            else:
                # Generic local execution
                print(f"📍 Executing {job.type.value} locally...")
                time.sleep(1)  # Placeholder
                success = True
                job.result = {"status": "completed", "local": True}
            
            if success:
                job.status = "completed"
                job.completed_at = datetime.utcnow().isoformat()
                self.state.total_jobs_completed += 1
                return True
            else:
                job.status = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Local execution failed: {e}")
            job.status = "failed"
            job.result = {"error": str(e)}
            return False
    
    # ─────────────────────────────────────────────────────────────────────────
    # REMOTE EXECUTION (DUAL BRIDGE)
    # ─────────────────────────────────────────────────────────────────────────
    
    def _dispatch_remote(self, job: BlockchainJob) -> bool:
        """Dispatch a job to remote Dual Bridge"""
        job.started_at = datetime.utcnow().isoformat()
        job.status = "dispatched"
        
        try:
            if job.target == JobTarget.REMOTE_DUAL:
                # qflop-dual-bridge.yml only accepts duration_minutes and power_mode
                workflow = "qflop-dual-bridge.yml"
                inputs = [
                    "-f", f"duration_minutes={job.payload.get('duration', 10)}",
                    "-f", f"power_mode={job.payload.get('power_mode', 'maxpower')}"
                ]
            else:  # REMOTE_GPU
                # diamond_node.yml accepts job_id, vector, duration, precision
                workflow = "diamond_node.yml"
                inputs = [
                    "-f", f"job_id={job.id}",
                    "-f", f"vector={job.payload.get('vector', 'blockchain')}",
                    "-f", f"duration={job.payload.get('duration', 60)}",
                    "-f", f"precision={job.payload.get('precision', 0.1)}"
                ]
            
            cmd = ["gh", "workflow", "run", workflow, "--repo", GITHUB_REPO] + inputs
            
            print(f"🚀 Dispatching to remote: {workflow}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Get run ID
                time.sleep(3)
                run_id_cmd = [
                    "gh", "run", "list", "--workflow", workflow,
                    "--repo", GITHUB_REPO, "--limit", "1",
                    "--json", "databaseId", "-q", ".[0].databaseId"
                ]
                run_id_result = subprocess.run(run_id_cmd, capture_output=True, text=True, timeout=15)
                job.run_id = run_id_result.stdout.strip()
                
                job.status = "remote_running"
                self.state.remote_runs_active += 1
                print(f"✅ Remote job dispatched (Run ID: {job.run_id})")
                return True
            else:
                print(f"❌ Remote dispatch failed: {result.stderr}")
                job.status = "failed"
                return False
                
        except Exception as e:
            print(f"❌ Remote dispatch error: {e}")
            job.status = "failed"
            job.result = {"error": str(e)}
            return False
    
    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────────────────────────────────
    
    def submit_job(self, job_type: JobType, payload: Dict[str, Any],
                   target: JobTarget = JobTarget.AUTO) -> str:
        """
        Submit a blockchain/asset production job.
        Returns job ID.
        """
        job_id = str(uuid.uuid4())
        
        # Auto-determine target if needed
        actual_target = target if target != JobTarget.AUTO else self._determine_target(job_type)
        
        job = BlockchainJob(
            id=job_id,
            type=job_type,
            target=actual_target,
            payload=payload
        )
        
        with self.lock:
            self.active_jobs[job_id] = job
        
        print(f"📋 Job submitted: {job_id[:8]} | Type: {job_type.value} | Target: {actual_target.value}")
        
        # Execute based on target
        if actual_target == JobTarget.LOCAL:
            success = self._execute_local(job)
        else:
            success = self._dispatch_remote(job)
        
        # Move to completed if done
        if job.status in ["completed", "failed"]:
            with self.lock:
                self.completed_jobs.append(job)
                del self.active_jobs[job_id]
        
        self._write_state()
        return job_id
    
    def submit_qflop_mint(self, qflops: float, coherence: float, 
                          proof_hash: str, force_remote: bool = False) -> str:
        """Submit a QFLOP minting job"""
        target = JobTarget.REMOTE_DUAL if force_remote else JobTarget.AUTO
        return self.submit_job(
            JobType.QFLOP_MINT,
            {"qflops": qflops, "coherence": coherence, "proof": proof_hash},
            target
        )
    
    def submit_dual_compute(self, duration: int = 10, 
                            power_mode: str = "maxpower") -> str:
        """Submit a dual bridge compute job"""
        return self.submit_job(
            JobType.DUAL_COMPUTE,
            {"duration": duration, "power_mode": power_mode},
            JobTarget.REMOTE_DUAL
        )
    
    def submit_seismic_blockchain(self, vector: str = "seismic",
                                   duration: int = 30) -> str:
        """Submit a seismic blockchain verification job"""
        return self.submit_job(
            JobType.SEISMIC_BLOCKCHAIN,
            {"vector": vector, "duration": duration},
            JobTarget.REMOTE_DUAL
        )
    
    def get_status(self) -> Dict:
        """Get full bridge status"""
        self._update_state()
        return {
            "state": asdict(self.state),
            "allocation": {
                "blockchain_percent": f"{BLOCKCHAIN_ALLOCATION * 100:.0f}%",
                "gpu_reserved_mb": LOCAL_GPU_RESERVED_MB,
                "overflow_threshold": f"{REMOTE_OVERFLOW_THRESHOLD * 100:.0f}%"
            },
            "jobs": {
                "pending": len(self.pending_jobs),
                "active": len(self.active_jobs),
                "completed": len(self.completed_jobs),
                "active_details": [
                    {"id": j.id[:8], "type": j.type.value, "target": j.target.value, "status": j.status}
                    for j in self.active_jobs.values()
                ]
            },
            "remote": {
                "active_runs": self.state.remote_runs_active,
                "overflow_active": self.state.overflow_to_remote
            }
        }
    
    def check_remote_jobs(self):
        """Check status of remote jobs and update state"""
        remote_jobs = [j for j in self.active_jobs.values() 
                       if j.target in [JobTarget.REMOTE_GPU, JobTarget.REMOTE_DUAL]
                       and j.run_id]
        
        for job in remote_jobs:
            try:
                result = subprocess.run(
                    ["gh", "run", "view", job.run_id, "--repo", GITHUB_REPO,
                     "--json", "status,conclusion"],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    status = json.loads(result.stdout)
                    if status.get("status") == "completed":
                        job.status = "completed" if status.get("conclusion") == "success" else "failed"
                        job.completed_at = datetime.utcnow().isoformat()
                        self.state.remote_runs_active -= 1
                        self.state.total_jobs_completed += 1
                        
                        with self.lock:
                            self.completed_jobs.append(job)
                            del self.active_jobs[job.id]
                        
                        print(f"✅ Remote job {job.id[:8]} completed: {job.status}")
            except:
                pass
        
        self._write_state()
    
    def _write_state(self):
        """Write current state to shared memory"""
        try:
            status = self.get_status()
            with open(SHARED_MEM_PATH, "w") as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to write state: {e}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # ZMQ MESH INTEGRATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def connect_to_mesh(self):
        """Connect to ZMQ mesh for job routing"""
        if not HAS_ZMQ:
            print("⚠️ ZMQ not available")
            return
        
        self.zmq_context = zmq.Context()
        
        # Subscribe to blockchain job requests
        self.zmq_subscriber = self.zmq_context.socket(zmq.SUB)
        self.zmq_subscriber.connect(f"tcp://localhost:{ZMQ_SUB_PORT}")
        self.zmq_subscriber.setsockopt_string(zmq.SUBSCRIBE, "BLOCKCHAIN_JOB")
        self.zmq_subscriber.setsockopt_string(zmq.SUBSCRIBE, "DUAL_BRIDGE_JOB")
        self.zmq_subscriber.setsockopt_string(zmq.SUBSCRIBE, "QFLOP_MINT")
        
        # Publisher for results
        self.zmq_publisher = self.zmq_context.socket(zmq.PUB)
        self.zmq_publisher.connect(f"tcp://localhost:{ZMQ_PUB_PORT}")
        
        print(f"🔗 Connected to ZMQ mesh (SUB:{ZMQ_SUB_PORT}, PUB:{ZMQ_PUB_PORT})")
    
    def run_mesh_loop(self):
        """Run the mesh integration loop"""
        if not self.zmq_subscriber:
            self.connect_to_mesh()
        
        if not self.zmq_subscriber:
            print("❌ Cannot run mesh loop without ZMQ")
            return
        
        print("🔄 Blockchain-Dual Bridge mesh loop running...")
        
        while True:
            try:
                if self.zmq_subscriber.poll(1000):  # 1 second timeout
                    msg = self.zmq_subscriber.recv_multipart()
                    topic = msg[0].decode()
                    payload = json.loads(msg[1].decode())
                    
                    print(f"📥 Received {topic}: {payload.get('id', 'unknown')[:8]}")
                    
                    if topic == "QFLOP_MINT":
                        job_id = self.submit_qflop_mint(
                            payload.get("qflops", 1.0),
                            payload.get("coherence", 0.99),
                            payload.get("proof", "")
                        )
                    elif topic == "DUAL_BRIDGE_JOB":
                        job_id = self.submit_dual_compute(
                            payload.get("duration", 10),
                            payload.get("power_mode", "maxpower")
                        )
                    else:
                        job_id = self.submit_job(
                            JobType.DUAL_COMPUTE,
                            payload,
                            JobTarget.AUTO
                        )
                    
                    # Publish result
                    self.zmq_publisher.send_multipart([
                        b"JOB_SUBMITTED",
                        json.dumps({"job_id": job_id, "topic": topic}).encode()
                    ])
                
                # Periodically check remote jobs
                self.check_remote_jobs()
                
            except KeyboardInterrupt:
                print("\n⏹️ Mesh loop stopped")
                break
            except Exception as e:
                print(f"⚠️ Mesh loop error: {e}")
                time.sleep(1)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI / MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="QMCP Blockchain-Dual Bridge Integrator")
    parser.add_argument("--status", action="store_true", help="Show bridge status")
    parser.add_argument("--mesh", action="store_true", help="Run mesh integration loop")
    parser.add_argument("--submit", choices=["qflop", "dual", "seismic"], 
                        help="Submit a test job")
    parser.add_argument("--duration", type=int, default=10, help="Job duration (minutes)")
    parser.add_argument("--force-remote", action="store_true", 
                        help="Force job to remote runner")
    args = parser.parse_args()
    
    bridge = BlockchainDualBridgeIntegrator(auto_overflow=True)
    
    if args.status:
        status = bridge.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.submit:
        if args.submit == "qflop":
            job_id = bridge.submit_qflop_mint(
                qflops=1.5,
                coherence=0.99,
                proof_hash=f"proof_{int(time.time())}",
                force_remote=args.force_remote
            )
        elif args.submit == "dual":
            job_id = bridge.submit_dual_compute(args.duration)
        elif args.submit == "seismic":
            job_id = bridge.submit_seismic_blockchain(duration=args.duration * 60)
        
        print(f"\n📋 Job submitted: {job_id}")
        print(json.dumps(bridge.get_status(), indent=2))
        return
    
    if args.mesh:
        bridge.run_mesh_loop()
        return
    
    # Default: show status
    status = bridge.get_status()
    print("\n🔗 BLOCKCHAIN-DUAL BRIDGE STATUS")
    print("=" * 60)
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
