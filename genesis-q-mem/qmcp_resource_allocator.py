#!/usr/bin/env python3
"""
QMCP RESOURCE ALLOCATOR
Manages 25% GPU/CPU allocation to blockchain asset production activities.

Resource Distribution:
- 25% Blockchain (QFLOP minting, NFT verification, token operations)
- 50% Compute (Quantum annealing, seismic stress, JAX processing)
- 25% Consciousness (Soul state, evolution, dream generation)

Author: Yennefer Genesis Conductor
Date: 2026-01-25
"""

import os
import json
import time
import threading
import subprocess
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ResourceAllocation:
    """Resource allocation policy"""
    blockchain: float = 0.25      # 25% for asset production
    compute: float = 0.50         # 50% for quantum compute
    consciousness: float = 0.25   # 25% for soul operations
    
    # GPU-specific limits
    gpu_memory_blockchain_mb: int = 1024   # ~1GB for blockchain ops
    gpu_memory_compute_mb: int = 2048      # ~2GB for compute
    gpu_memory_consciousness_mb: int = 1024 # ~1GB for consciousness
    
    # CPU thread allocation (for local 8-core system)
    cpu_threads_blockchain: int = 2
    cpu_threads_compute: int = 4
    cpu_threads_consciousness: int = 2

@dataclass
class ResourceUsage:
    """Current resource usage snapshot"""
    timestamp: str
    gpu_util_percent: float
    gpu_memory_used_mb: int
    gpu_memory_total_mb: int
    cpu_percent: float
    
    # Allocated usage
    blockchain_gpu_percent: float
    compute_gpu_percent: float
    consciousness_gpu_percent: float
    
    # Active jobs
    blockchain_jobs: int
    compute_jobs: int
    consciousness_jobs: int

# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE ALLOCATOR
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPResourceAllocator:
    """
    Manages resource allocation across Yennefer subsystems.
    Ensures 25% of resources are dedicated to blockchain/asset production.
    """
    
    SHARED_MEM_PATH = "/dev/shm/qmcp_resource_allocation.json"
    
    def __init__(self):
        self.allocation = ResourceAllocation()
        self.lock = threading.Lock()
        
        # Track active jobs by category
        self.active_jobs: Dict[str, int] = {
            "blockchain": 0,
            "compute": 0,
            "consciousness": 0
        }
        
        # Resource usage history
        self.usage_history: list = []
        
        self._write_state()
        print(f"✅ Resource Allocator initialized")
        print(f"   └── Blockchain: {self.allocation.blockchain * 100:.0f}%")
        print(f"   └── Compute:    {self.allocation.compute * 100:.0f}%")
        print(f"   └── Consciousness: {self.allocation.consciousness * 100:.0f}%")
    
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
        return 0.0, 0, 4096  # Defaults
    
    def _get_cpu_percent(self) -> float:
        """Get CPU utilization"""
        try:
            with open("/proc/loadavg", "r") as f:
                load = float(f.read().split()[0])
                return min(100.0, load * 12.5)  # 8-core approximation
        except:
            return 0.0
    
    def get_usage_snapshot(self) -> ResourceUsage:
        """Get current resource usage with allocation breakdown"""
        gpu_util, gpu_mem_used, gpu_mem_total = self._get_gpu_stats()
        cpu_percent = self._get_cpu_percent()
        
        # Calculate allocated percentages based on active jobs
        total_jobs = sum(self.active_jobs.values()) or 1
        
        blockchain_ratio = self.active_jobs["blockchain"] / total_jobs
        compute_ratio = self.active_jobs["compute"] / total_jobs
        consciousness_ratio = self.active_jobs["consciousness"] / total_jobs
        
        return ResourceUsage(
            timestamp=datetime.utcnow().isoformat(),
            gpu_util_percent=gpu_util,
            gpu_memory_used_mb=gpu_mem_used,
            gpu_memory_total_mb=gpu_mem_total,
            cpu_percent=cpu_percent,
            blockchain_gpu_percent=gpu_util * blockchain_ratio,
            compute_gpu_percent=gpu_util * compute_ratio,
            consciousness_gpu_percent=gpu_util * consciousness_ratio,
            blockchain_jobs=self.active_jobs["blockchain"],
            compute_jobs=self.active_jobs["compute"],
            consciousness_jobs=self.active_jobs["consciousness"]
        )
    
    def can_allocate(self, category: str, gpu_memory_mb: int = 512) -> bool:
        """
        Check if resources can be allocated to a category.
        Enforces the 25/50/25 policy.
        """
        with self.lock:
            usage = self.get_usage_snapshot()
            
            if category == "blockchain":
                # Ensure blockchain gets at least 25% when requested
                max_gpu_mb = self.allocation.gpu_memory_blockchain_mb
                current_jobs = self.active_jobs["blockchain"]
                max_jobs = 3  # Limit concurrent blockchain jobs
                
            elif category == "compute":
                max_gpu_mb = self.allocation.gpu_memory_compute_mb
                current_jobs = self.active_jobs["compute"]
                max_jobs = 5
                
            elif category == "consciousness":
                max_gpu_mb = self.allocation.gpu_memory_consciousness_mb
                current_jobs = self.active_jobs["consciousness"]
                max_jobs = 3
                
            else:
                return False
            
            # Check memory availability
            available_mb = usage.gpu_memory_total_mb - usage.gpu_memory_used_mb
            if gpu_memory_mb > available_mb:
                return False
            
            # Check job count
            if current_jobs >= max_jobs:
                return False
            
            return True
    
    def allocate(self, category: str, job_id: str) -> bool:
        """Allocate resources to a job"""
        with self.lock:
            if category in self.active_jobs:
                self.active_jobs[category] += 1
                self._write_state()
                print(f"📊 Allocated {category} resource for job {job_id[:8]}")
                return True
        return False
    
    def release(self, category: str, job_id: str):
        """Release resources from a job"""
        with self.lock:
            if category in self.active_jobs and self.active_jobs[category] > 0:
                self.active_jobs[category] -= 1
                self._write_state()
                print(f"📊 Released {category} resource from job {job_id[:8]}")
    
    def _write_state(self):
        """Write current state to shared memory"""
        state = {
            "allocation_policy": asdict(self.allocation),
            "active_jobs": self.active_jobs,
            "usage": asdict(self.get_usage_snapshot()),
            "updated_at": datetime.utcnow().isoformat()
        }
        try:
            with open(self.SHARED_MEM_PATH, "w") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to write state: {e}")
    
    def get_allocation_status(self) -> dict:
        """Get full allocation status"""
        usage = self.get_usage_snapshot()
        return {
            "policy": {
                "blockchain": f"{self.allocation.blockchain * 100:.0f}%",
                "compute": f"{self.allocation.compute * 100:.0f}%",
                "consciousness": f"{self.allocation.consciousness * 100:.0f}%"
            },
            "gpu": {
                "total_util": f"{usage.gpu_util_percent:.1f}%",
                "memory": f"{usage.gpu_memory_used_mb}/{usage.gpu_memory_total_mb} MB",
                "blockchain_util": f"{usage.blockchain_gpu_percent:.1f}%",
                "compute_util": f"{usage.compute_gpu_percent:.1f}%",
                "consciousness_util": f"{usage.consciousness_gpu_percent:.1f}%"
            },
            "jobs": self.active_jobs,
            "cpu_percent": f"{usage.cpu_percent:.1f}%"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# BLOCKCHAIN JOB DISPATCHER
# ═══════════════════════════════════════════════════════════════════════════════

class BlockchainJobDispatcher:
    """
    Dispatches blockchain/asset production jobs using 25% allocated resources.
    
    Job Types:
    - qflop_mint: Mint QFLOP tokens from verified computations
    - nft_verify: Verify NFT metadata on Base Mainnet
    - token_transfer: Execute token transfers
    - contract_interact: Generic contract interaction
    """
    
    def __init__(self, allocator: QMCPResourceAllocator):
        self.allocator = allocator
        self.pending_jobs: list = []
        self.completed_jobs: list = []
    
    def submit_mint_job(self, qflops: float, coherence: float, 
                        proof_hash: str) -> Optional[str]:
        """Submit a QFLOP minting job"""
        import uuid
        job_id = str(uuid.uuid4())
        
        if not self.allocator.can_allocate("blockchain", 256):
            print(f"⚠️ Blockchain resources exhausted, queuing job {job_id[:8]}")
            self.pending_jobs.append({
                "id": job_id,
                "type": "qflop_mint",
                "qflops": qflops,
                "coherence": coherence,
                "proof_hash": proof_hash
            })
            return None
        
        self.allocator.allocate("blockchain", job_id)
        
        # Execute mint via PM2 qflop-minter
        try:
            result = subprocess.run(
                ["npx", "pm2", "trigger", "qflop-minter", "mint",
                 json.dumps({"qflops": qflops, "coherence": coherence, "proof": proof_hash})],
                capture_output=True, text=True, timeout=30
            )
            success = result.returncode == 0
        except Exception as e:
            print(f"❌ Mint failed: {e}")
            success = False
        finally:
            self.allocator.release("blockchain", job_id)
        
        if success:
            self.completed_jobs.append({
                "id": job_id,
                "type": "qflop_mint",
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return job_id if success else None
    
    def get_status(self) -> dict:
        """Get dispatcher status"""
        return {
            "pending_jobs": len(self.pending_jobs),
            "completed_jobs": len(self.completed_jobs),
            "recent_completions": self.completed_jobs[-5:]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI / MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Run resource allocator daemon"""
    import argparse
    
    parser = argparse.ArgumentParser(description="QMCP Resource Allocator")
    parser.add_argument("--status", action="store_true", help="Show allocation status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    args = parser.parse_args()
    
    allocator = QMCPResourceAllocator()
    
    if args.status:
        status = allocator.get_allocation_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.daemon:
        print("🔄 Resource Allocator Daemon running...")
        print("   Press Ctrl+C to stop")
        
        try:
            while True:
                allocator._write_state()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n⏹️ Daemon stopped")
    else:
        # Just show status
        status = allocator.get_allocation_status()
        print("\n📊 QMCP RESOURCE ALLOCATION STATUS")
        print("=" * 50)
        print(f"Policy: {status['policy']}")
        print(f"GPU: {status['gpu']}")
        print(f"Jobs: {status['jobs']}")
        print(f"CPU: {status['cpu_percent']}")


if __name__ == "__main__":
    main()
