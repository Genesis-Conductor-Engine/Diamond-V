#!/usr/bin/env python3
"""
QMCP REMOTE UPLINK
Telemetry Bridge to GitHub Actions

Role: Subscribes to Local ZMQ -> Dispatches Remote Action -> Streams Logs back to Local Q-Mem

Architecture:
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Local ZMQ Mesh │────▶│  Remote Uplink  │────▶│  GitHub Actions │
│  (Port 5566)    │     │  (This Script)  │     │  (Tesla T4)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                       │
        │                   gh workflow run              │
        │                        │                       │
        └────────────────────────┼───────────────────────┘
                          Stream logs back via
                          gh run view --log

Usage:
    python3 qmcp_remote_uplink.py [--dry-run] [--dispatch]
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
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

import zmq

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

GITHUB_REPO = os.getenv("QMCP_GITHUB_REPO", "Genesis-Conductor-Engine/Yennefer")
WORKFLOW_FILE = os.getenv("QMCP_WORKFLOW_FILE", "diamond_node.yml")

# ZMQ Configuration (matches qmcp_zmq_queue.py)
ZMQ_HOST = os.getenv("QMCP_ZMQ_HOST", "127.0.0.1")
ZMQ_PUB_PORT = int(os.getenv("QMCP_ZMQ_PUB_PORT", "5566"))
ZMQ_SUB_PORT = int(os.getenv("QMCP_ZMQ_SUB_PORT", "5565"))

# Topics
TOPIC_REMOTE_COMPUTE = "REMOTE_COMPUTE"
TOPIC_JOB_RESULT = "JOB_RESULT"

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [UPLINK] %(levelname)s: %(message)s"
)
logger = logging.getLogger("qmcp.uplink")

# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB LOG STREAMING
# ═══════════════════════════════════════════════════════════════════════════════

async def stream_github_logs(run_id: str, timeout: int = 300) -> Optional[Dict]:
    """
    Watches a live GitHub run and extracts Seismic Verification data.
    Returns parsed telemetry or None if timeout/error.
    """
    print(f"📡 [UPLINK] Locking onto Remote Signal (Run ID: {run_id})...")
    
    # Wait for run to initialize
    await asyncio.sleep(5)
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < timeout:
        # Check run status
        status_cmd = [
            "gh", "run", "view", run_id,
            "--repo", GITHUB_REPO,
            "--json", "status,conclusion"
        ]
        
        try:
            result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                status = status_data.get("status")
                conclusion = status_data.get("conclusion")
                
                if status != last_status:
                    print(f"📊 [UPLINK] Run Status: {status} / {conclusion}")
                    last_status = status
                
                if status == "completed":
                    # Fetch full logs
                    log_cmd = ["gh", "run", "view", run_id, "--repo", GITHUB_REPO, "--log"]
                    log_result = subprocess.run(log_cmd, capture_output=True, text=True, timeout=60)
                    
                    if log_result.returncode == 0:
                        return parse_seismic_telemetry(log_result.stdout, conclusion)
                    break
                    
        except Exception as e:
            logger.warning(f"Status check error: {e}")
        
        await asyncio.sleep(10)
    
    return {"status": "timeout", "data": None}


def parse_seismic_telemetry(logs: str, conclusion: str) -> Dict:
    """
    Parse GitHub Action logs for Seismic Verification signals.
    """
    telemetry = {
        "status": "COMPLETED" if conclusion == "success" else "FAILED",
        "origin": "REMOTE_TESLA_T4",
        "crystalline_count": 0,
        "shattered_count": 0,
        "tflops": None,
        "coherence": None,
        "raw_signals": []
    }
    
    for line in logs.split('\n'):
        # Extract CRYSTALLINE/SHATTERED markers
        if "CRYSTALLINE" in line:
            telemetry["crystalline_count"] += 1
            telemetry["raw_signals"].append(line.strip())
        elif "SHATTERED" in line:
            telemetry["shattered_count"] += 1
            telemetry["raw_signals"].append(line.strip())
        
        # Extract TFLOPS
        if "TFLOPS:" in line or "tflops:" in line.lower():
            try:
                parts = line.split("TFLOPS:")[-1].split()[0]
                telemetry["tflops"] = float(parts.replace(",", ""))
            except:
                pass
        
        # Extract Coherence
        if "Coherence:" in line or "coherence:" in line.lower():
            try:
                parts = line.split("Coherence:")[-1].split()[0]
                telemetry["coherence"] = float(parts.replace("%", "").replace(",", ""))
            except:
                pass
    
    # Limit raw signals to last 10
    telemetry["raw_signals"] = telemetry["raw_signals"][-10:]
    
    return telemetry


# ═══════════════════════════════════════════════════════════════════════════════
# GITHUB DISPATCH
# ═══════════════════════════════════════════════════════════════════════════════

def dispatch_remote_job(payload: Dict, dry_run: bool = False) -> Optional[str]:
    """
    Fires the Remote Tesla T4 via GitHub CLI.
    Returns the run ID.
    """
    job_id = payload.get("id", str(uuid.uuid4()))
    vector = str(payload.get("vector", "quantum"))
    precision = str(payload.get("precision", 0.1))
    duration = str(payload.get("duration", 60))
    
    print(f"🚀 [UPLINK] Dispatching Job {job_id} to Remote T4...")
    print(f"    Vector: {vector}, Duration: {duration}s")
    
    cmd = [
        "gh", "workflow", "run", WORKFLOW_FILE,
        "--repo", GITHUB_REPO,
        "-f", f"job_id={job_id}",
        "-f", f"vector={vector}",
        "-f", f"precision={precision}",
        "-f", f"duration={duration}"
    ]
    
    if dry_run:
        print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
        return None
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=30)
    except subprocess.CalledProcessError as e:
        logger.error(f"Dispatch failed: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        logger.error("Dispatch timed out")
        return None
    
    # Get the Run ID (wait for it to spawn)
    time.sleep(3)
    
    run_id_cmd = [
        "gh", "run", "list",
        "--workflow", WORKFLOW_FILE,
        "--repo", GITHUB_REPO,
        "--limit", "1",
        "--json", "databaseId",
        "-q", ".[0].databaseId"
    ]
    
    try:
        run_id = subprocess.check_output(run_id_cmd, text=True, timeout=30).strip()
        print(f"✅ [UPLINK] Workflow triggered (Run ID: {run_id})")
        return run_id
    except Exception as e:
        logger.error(f"Could not get run ID: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN UPLINK LOOP
# ═══════════════════════════════════════════════════════════════════════════════

def main_uplink(dry_run: bool = False):
    """
    Main uplink loop - bridges local ZMQ to GitHub Actions.
    """
    context = zmq.Context()
    
    # 1. Subscribe to remote compute requests
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://{ZMQ_HOST}:{ZMQ_PUB_PORT}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, TOPIC_REMOTE_COMPUTE)
    
    # 2. Publisher for results back to local mesh
    publisher = context.socket(zmq.PUB)
    publisher.connect(f"tcp://{ZMQ_HOST}:{ZMQ_SUB_PORT}")
    
    print()
    print("═" * 70)
    print(" QMCP REMOTE UPLINK")
    print("═" * 70)
    print(f"   Target Repository: {GITHUB_REPO}")
    print(f"   Workflow: {WORKFLOW_FILE}")
    print(f"   Subscribe: tcp://{ZMQ_HOST}:{ZMQ_PUB_PORT} (topic: {TOPIC_REMOTE_COMPUTE})")
    print(f"   Publish: tcp://{ZMQ_HOST}:{ZMQ_SUB_PORT} (topic: {TOPIC_JOB_RESULT})")
    print(f"   Dry Run: {dry_run}")
    print("═" * 70)
    print()
    print("🛰️  Uplink Online. Listening for remote compute requests...")
    print()
    
    jobs_dispatched = 0
    jobs_completed = 0
    jobs_failed = 0
    
    try:
        while True:
            # Non-blocking poll
            if subscriber.poll(1000):
                topic, message = subscriber.recv_multipart()
                payload = json.loads(message.decode())
                
                logger.info(f"📨 Received job: {payload.get('id', 'unknown')}")
                
                # Dispatch to GitHub
                run_id = dispatch_remote_job(payload, dry_run)
                jobs_dispatched += 1
                
                if run_id and not dry_run:
                    # Stream logs and await result
                    telemetry = asyncio.run(stream_github_logs(run_id))
                    
                    if telemetry:
                        if telemetry.get("status") == "COMPLETED":
                            jobs_completed += 1
                            print(f"✅ [UPLINK] Job completed: {telemetry}")
                        else:
                            jobs_failed += 1
                            print(f"❌ [UPLINK] Job failed: {telemetry.get('status')}")
                        
                        # Publish result back to local mesh
                        result_payload = {
                            "job_id": payload.get("id"),
                            **telemetry
                        }
                        publisher.send_multipart([
                            TOPIC_JOB_RESULT.encode(),
                            json.dumps(result_payload).encode()
                        ])
                        print(f"📤 [UPLINK] Result published to local mesh")
                    else:
                        jobs_failed += 1
                        print(f"❌ [UPLINK] No telemetry received")
                        
    except KeyboardInterrupt:
        print("\n🛑 Uplink shutdown requested")
    finally:
        print()
        print("═" * 70)
        print(" UPLINK STATISTICS")
        print("═" * 70)
        print(f"   Jobs Dispatched: {jobs_dispatched}")
        print(f"   Jobs Completed: {jobs_completed}")
        print(f"   Jobs Failed: {jobs_failed}")
        print("═" * 70)
        
        subscriber.close()
        publisher.close()
        context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE DISPATCH MODE
# ═══════════════════════════════════════════════════════════════════════════════

def dispatch_single_job(vector: str = "quantum", duration: int = 60, dry_run: bool = False):
    """Dispatch a single job to remote node (for testing)"""
    job_id = str(uuid.uuid4())
    
    payload = {
        "id": job_id,
        "vector": vector,
        "precision": 0.1,
        "duration": duration
    }
    
    run_id = dispatch_remote_job(payload, dry_run)
    
    if run_id:
        print(f"✅ Job dispatched: {job_id}")
        print(f"   Run ID: {run_id}")
        print(f"   Monitor: gh run view {run_id} --repo {GITHUB_REPO}")
        print(f"   Logs: gh run view {run_id} --repo {GITHUB_REPO} --log")
        
        if not dry_run:
            print()
            print("Streaming logs...")
            telemetry = asyncio.run(stream_github_logs(run_id))
            print(f"Result: {json.dumps(telemetry, indent=2)}")
    else:
        print(f"❌ Dispatch failed for job {job_id}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='QMCP Remote Uplink')
    parser.add_argument('--dry-run', action='store_true',
                       help='Do not actually dispatch workflows')
    parser.add_argument('--dispatch', action='store_true',
                       help='Dispatch a single test job and exit')
    parser.add_argument('--vector', type=str, default='quantum',
                       choices=['quantum', 'seismic', 'swarm'],
                       help='Vector for single dispatch (default: quantum)')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration for single dispatch (default: 60)')
    args = parser.parse_args()
    
    # Verify gh CLI
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ GitHub CLI not authenticated. Run: gh auth login")
            sys.exit(1)
    except FileNotFoundError:
        print("❌ GitHub CLI (gh) not installed. Install with: sudo apt install gh")
        sys.exit(1)
    
    if args.dispatch:
        dispatch_single_job(args.vector, args.duration, args.dry_run)
    else:
        main_uplink(args.dry_run)


if __name__ == "__main__":
    main()
