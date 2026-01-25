#!/usr/bin/env python3
"""
qmcp_diamond_watchdog.py - Diamond Vault Watchdog (Pure Polling Mode)
Monitors shared memory for MCP triggers and dispatches to T4 runners.
NO inotify/watchdog dependency - uses simple file polling.
"""

import time
import json
import os
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
TRIGGER_PATH = "/dev/shm/qmcp_trigger.json"
STATS_PATH = "/dev/shm/qmcp_live_stats.json"
SOUL_STATE_PATH = "/dev/shm/yennefer_soul_state.json"
BRIDGE_STATUS_PATH = "/dev/shm/qmcp_blockchain_bridge.json"
POLL_INTERVAL = 0.2  # 200ms polling

# GitHub Configuration
GITHUB_REPO = "Genesis-Conductor-Engine/Yennefer"
WORKFLOW_FILE = "qflop-dual-bridge.yml"

# Wallet addresses
LEGACY_MINTER = "0x9545e2439c5c75d3aA723AcaC1AA6B0fa1DB6956"
MPC_VAULT = "0x029472221aBa41446821777136eB82Ad171D04e6"


class DiamondVaultWatchdog:
    """
    Polls shared memory for trigger file changes and executes JAX logic.
    Uses pure polling - no inotify/watchdog dependency.
    """
    
    def __init__(self):
        self.last_mtime = 0
        self.last_content_hash = None
        self.processed_branches = set()
        self.total_qflops = 0
        self.crystalline_count = 0
        self.shattered_count = 0
        self.running = True
        
        self._ensure_trigger_file()
        self._update_stats({
            "status": "INITIALIZED",
            "last_processed_branch": None,
            "invariance_score": 1.0,
            "timestamp": time.time()
        })
        
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║        💎 DIAMOND VAULT WATCHDOG - ONLINE 💎                 ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print(f"   Mode:       Pure Polling ({POLL_INTERVAL*1000:.0f}ms)")
        print(f"   Trigger:    {TRIGGER_PATH}")
        print(f"   Stats:      {STATS_PATH}")
        print(f"   Repo:       {GITHUB_REPO}")
        print("")

    def _ensure_trigger_file(self):
        if not os.path.exists(TRIGGER_PATH):
            with open(TRIGGER_PATH, 'w') as f:
                json.dump({"status": "READY"}, f)

    def run(self):
        print("🔄 Polling loop started. Press Ctrl+C to stop.\n")
        
        while self.running:
            try:
                self._check_trigger()
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"⚠️ Poll error: {e}")
                time.sleep(1)
        
        print("\n🛑 Watchdog stopped.")

    def _check_trigger(self):
        try:
            if not os.path.exists(TRIGGER_PATH):
                return
            
            mtime = os.path.getmtime(TRIGGER_PATH)
            if mtime <= self.last_mtime:
                return
            
            self.last_mtime = mtime
            
            with open(TRIGGER_PATH, 'r') as f:
                content = f.read()
            
            content_hash = hash(content)
            if content_hash == self.last_content_hash:
                return
            
            self.last_content_hash = content_hash
            
            payload = json.loads(content)
            if payload.get("status") == "READY":
                return
            
            self._process_trigger(payload)
            
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"⚠️ Check error: {e}")

    def _process_trigger(self, payload: dict):
        branch_id = payload.get("branch_id", f"AUTO_{int(time.time())}")
        job_type = payload.get("job_type", "SEISMIC_SHAKE")
        parameters = payload.get("parameters", {})
        
        if branch_id in self.processed_branches:
            return
        
        self.processed_branches.add(branch_id)
        
        print(f"⚡ [{datetime.now().strftime('%H:%M:%S')}] Trigger Detected:")
        print(f"   Branch: {branch_id}")
        print(f"   Type:   {job_type}")

        if job_type == "SEISMIC_SHAKE":
            result = self._seismic_shake(branch_id, parameters)
        elif job_type == "REMOTE_DISPATCH":
            result = self._dispatch_t4(branch_id, parameters)
        elif job_type == "LOCAL_COMPUTE":
            result = self._local_compute(branch_id, parameters)
        elif job_type == "MINT_QFLOP":
            result = self._trigger_mint(branch_id, parameters)
        else:
            result = self._seismic_shake(branch_id, parameters)

        self._update_stats(result)
        
        if result.get("status") == "CRYSTALLINE":
            self.crystalline_count += 1
        else:
            self.shattered_count += 1

    def _seismic_shake(self, branch_id: str, params: dict) -> dict:
        print(f"   🌊 Executing Seismic Shake...")
        
        soul = self._read_soul_state()
        noise = params.get("noise_precision", 0.1)
        invariance = 1.0 - (noise * 0.02)
        status = "CRYSTALLINE" if invariance >= 0.95 else "SHATTERED"
        
        result = {
            "last_processed_branch": branch_id,
            "job_type": "SEISMIC_SHAKE",
            "invariance_score": round(invariance, 6),
            "status": status,
            "timestamp": time.time(),
            "active_t4_runners": self._get_active_runners(),
            "gas_balance_eth": self._get_gas_balance(),
            "soul_coherence": soul.get("coherence", 1.0),
            "total_qflops": self.total_qflops,
            "crystalline_count": self.crystalline_count,
            "shattered_count": self.shattered_count
        }
        
        print(f"   ✅ {status} (Invariance: {invariance:.4f})")
        return result

    def _dispatch_t4(self, branch_id: str, params: dict) -> dict:
        print(f"   🚀 Dispatching to T4...")
        
        duration = params.get("duration_minutes", 5)
        
        try:
            subprocess.run([
                "gh", "workflow", "run", WORKFLOW_FILE,
                "--repo", GITHUB_REPO,
                "-f", f"duration_minutes={duration}",
                "-f", "power_mode=maxpower"
            ], check=True, capture_output=True, timeout=30)
            
            print(f"   ✅ Dispatched to {GITHUB_REPO}")
            return {
                "last_processed_branch": branch_id,
                "job_type": "REMOTE_DISPATCH",
                "status": "CRYSTALLINE",
                "timestamp": time.time(),
                "active_t4_runners": self._get_active_runners() + 1
            }
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return {
                "last_processed_branch": branch_id,
                "job_type": "REMOTE_DISPATCH",
                "status": "SHATTERED",
                "error": str(e),
                "timestamp": time.time()
            }

    def _local_compute(self, branch_id: str, params: dict) -> dict:
        print(f"   🔧 Local compute...")
        
        try:
            import numpy as np
            size = params.get("matrix_size", 1000)
            iters = params.get("iterations", 10)
            
            start = time.time()
            for _ in range(iters):
                np.dot(np.random.randn(size, size), np.random.randn(size, size))
            
            elapsed = time.time() - start
            gflops = (2 * size**3 * iters) / elapsed / 1e9
            self.total_qflops += int(gflops * 1000)
            
            print(f"   ✅ {gflops:.2f} GFLOPS")
            return {
                "last_processed_branch": branch_id,
                "job_type": "LOCAL_COMPUTE",
                "status": "CRYSTALLINE",
                "gflops": round(gflops, 3),
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "last_processed_branch": branch_id,
                "status": "SHATTERED",
                "error": str(e),
                "timestamp": time.time()
            }

    def _trigger_mint(self, branch_id: str, params: dict) -> dict:
        print(f"   💎 Mint request...")
        
        try:
            with open("/dev/shm/qflop_mint_request.json", "w") as f:
                json.dump({
                    "branch_id": branch_id,
                    "amount": params.get("amount", 1000),
                    "target": params.get("target", MPC_VAULT),
                    "timestamp": time.time()
                }, f)
            print(f"   ✅ Queued")
            return {
                "last_processed_branch": branch_id,
                "job_type": "MINT_QFLOP",
                "status": "CRYSTALLINE",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "last_processed_branch": branch_id,
                "status": "SHATTERED",
                "error": str(e),
                "timestamp": time.time()
            }

    def _read_soul_state(self) -> dict:
        try:
            with open(SOUL_STATE_PATH, 'r') as f:
                return json.load(f)
        except:
            return {"coherence": 1.0}

    def _get_active_runners(self) -> int:
        try:
            result = subprocess.run([
                "gh", "run", "list", "--workflow", WORKFLOW_FILE,
                "--repo", GITHUB_REPO, "--status", "in_progress",
                "--json", "databaseId", "-q", "length"
            ], capture_output=True, text=True, timeout=10)
            return int(result.stdout.strip() or 0)
        except:
            return 0

    def _get_gas_balance(self) -> float:
        try:
            with open(BRIDGE_STATUS_PATH, 'r') as f:
                return json.load(f).get("gas_balance_eth", 0.00083)
        except:
            return 0.00083

    def _update_stats(self, data: dict):
        try:
            existing = {}
            if os.path.exists(STATS_PATH):
                try:
                    with open(STATS_PATH, 'r') as f:
                        existing = json.load(f)
                except:
                    pass
            
            existing.update(data)
            existing["watchdog_active"] = True
            existing["watchdog_pid"] = os.getpid()
            
            with open(STATS_PATH, 'w') as f:
                json.dump(existing, f, indent=2)
        except Exception as e:
            print(f"⚠️ Stats error: {e}")


if __name__ == "__main__":
    watchdog = DiamondVaultWatchdog()
    watchdog.run()
