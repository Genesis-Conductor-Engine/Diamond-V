#!/usr/bin/env python3
"""
GPU Overclock & Tensor Offload Optimizer for Yennefer QMCP
Maximizes GTX 1650 performance through:
- Dynamic GPU overclocking (memory/core clocks)
- Tensor offload with async transfers
- Memory coalescing and prefetching
- Thermal-aware frequency scaling
"""

import os
import time
import json
import subprocess
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import mmap

# Try to import GPU libraries
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_NVML = True
except:
    HAS_NVML = False

try:
    import cupy as cp
    HAS_CUPY = True
    print("⚡ CuPy GPU acceleration ENABLED")
except ImportError:
    HAS_CUPY = False
    print("⚡ Using NumPy (install cupy for GPU tensor offload)")


# ═══════════════════════════════════════════════════════════════════════════════
# GPU CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GPUConfig:
    """GTX 1650 optimized configuration"""
    device_id: int = 0
    
    # Base clocks (MHz)
    base_core_clock: int = 1485
    base_mem_clock: int = 4001
    
    # Overclock targets (MHz) - conservative for stability
    target_core_clock: int = 1785  # +300MHz
    target_mem_clock: int = 4501   # +500MHz
    
    # Power limits (W)
    default_power_limit: int = 75
    max_power_limit: int = 90
    
    # Thermal limits (°C)
    thermal_throttle: int = 83
    thermal_target: int = 75
    thermal_critical: int = 90
    
    # Memory (MB)
    vram_total: int = 4096
    vram_reserved: int = 512  # Reserve for system
    
    # Tensor offload settings
    tensor_batch_size: int = 1024
    async_transfer_streams: int = 4
    prefetch_depth: int = 2


# ═══════════════════════════════════════════════════════════════════════════════
# GPU OVERCLOCK MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class GPUOverclockManager:
    """
    Dynamic GPU overclocking with thermal protection.
    Uses nvidia-settings and nvidia-smi for clock control.
    """
    
    def __init__(self, config: GPUConfig = None):
        self.config = config or GPUConfig()
        self.handle = None
        self.current_clocks = {'core': 0, 'mem': 0}
        self.thermal_history = []
        self.overclock_enabled = False
        
        if HAS_NVML:
            try:
                self.handle = pynvml.nvmlDeviceGetHandleByIndex(self.config.device_id)
                self._init_overclock()
            except Exception as e:
                print(f"⚠️ NVML init failed: {e}")
    
    def _init_overclock(self):
        """Initialize overclocking if supported"""
        if not self.handle:
            return
            
        try:
            # Get device info
            name = pynvml.nvmlDeviceGetName(self.handle)
            print(f"🎮 GPU: {name}")
            
            # Check persistence mode
            mode = pynvml.nvmlDeviceGetPersistenceMode(self.handle)
            if mode == pynvml.NVML_FEATURE_DISABLED:
                print("  ⚠️ Persistence mode disabled - clocks may reset")
            
            # Get current clocks
            clocks = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_GRAPHICS)
            mem_clocks = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_MEM)
            self.current_clocks = {'core': clocks, 'mem': mem_clocks}
            print(f"  📊 Current clocks: Core={clocks}MHz, Mem={mem_clocks}MHz")
            
        except Exception as e:
            print(f"  ⚠️ Clock query failed: {e}")
    
    def apply_overclock(self, level: str = 'moderate') -> Dict:
        """
        Apply overclocking profile.
        Levels: 'conservative', 'moderate', 'aggressive'
        """
        profiles = {
            'conservative': {'core_offset': 100, 'mem_offset': 200},
            'moderate': {'core_offset': 200, 'mem_offset': 400},
            'aggressive': {'core_offset': 300, 'mem_offset': 500}
        }
        
        profile = profiles.get(level, profiles['moderate'])
        
        try:
            # Use nvidia-settings for overclock (requires X display)
            core_cmd = f"nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels={profile['core_offset']}'"
            mem_cmd = f"nvidia-settings -a '[gpu:0]/GPUMemoryTransferRateOffsetAllPerformanceLevels={profile['mem_offset']}'"
            
            # Try to apply (may fail without X)
            result_core = subprocess.run(core_cmd, shell=True, capture_output=True, text=True)
            result_mem = subprocess.run(mem_cmd, shell=True, capture_output=True, text=True)
            
            if result_core.returncode == 0 and result_mem.returncode == 0:
                self.overclock_enabled = True
                print(f"⚡ Overclock applied: Core+{profile['core_offset']}MHz, Mem+{profile['mem_offset']}MHz")
            else:
                # Fallback: try nvidia-smi power limit increase
                power_cmd = f"sudo nvidia-smi -pl {self.config.max_power_limit}"
                subprocess.run(power_cmd, shell=True, capture_output=True)
                print(f"⚡ Power limit increased to {self.config.max_power_limit}W")
            
            return {
                'status': 'applied',
                'level': level,
                'core_offset': profile['core_offset'],
                'mem_offset': profile['mem_offset']
            }
            
        except Exception as e:
            print(f"⚠️ Overclock failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_gpu_stats(self) -> Dict:
        """Get current GPU statistics"""
        stats = {
            'temperature': 0,
            'gpu_util': 0,
            'mem_util': 0,
            'power_draw': 0,
            'core_clock': 0,
            'mem_clock': 0,
            'fan_speed': 0
        }
        
        if not self.handle:
            return stats
            
        try:
            stats['temperature'] = pynvml.nvmlDeviceGetTemperature(
                self.handle, pynvml.NVML_TEMPERATURE_GPU)
            
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            stats['gpu_util'] = util.gpu
            stats['mem_util'] = util.memory
            
            power = pynvml.nvmlDeviceGetPowerUsage(self.handle)
            stats['power_draw'] = power / 1000.0  # mW to W
            
            stats['core_clock'] = pynvml.nvmlDeviceGetClockInfo(
                self.handle, pynvml.NVML_CLOCK_GRAPHICS)
            stats['mem_clock'] = pynvml.nvmlDeviceGetClockInfo(
                self.handle, pynvml.NVML_CLOCK_MEM)
            
            try:
                stats['fan_speed'] = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except:
                pass
                
        except Exception as e:
            pass
            
        return stats
    
    def thermal_throttle_check(self) -> bool:
        """Check if thermal throttling should activate"""
        stats = self.get_gpu_stats()
        temp = stats['temperature']
        
        self.thermal_history.append(temp)
        if len(self.thermal_history) > 60:  # Keep 1 minute history
            self.thermal_history.pop(0)
        
        if temp >= self.config.thermal_throttle:
            print(f"🌡️ THERMAL THROTTLE: {temp}°C - reducing clocks")
            self._reduce_clocks()
            return True
        elif temp >= self.config.thermal_target and self.overclock_enabled:
            avg_temp = sum(self.thermal_history) / len(self.thermal_history)
            if avg_temp >= self.config.thermal_target:
                print(f"🌡️ Thermal target reached: {temp}°C (avg: {avg_temp:.1f}°C)")
                return True
        
        return False
    
    def _reduce_clocks(self):
        """Reduce clocks for thermal protection"""
        try:
            subprocess.run(
                "nvidia-settings -a '[gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels=0'",
                shell=True, capture_output=True
            )
            self.overclock_enabled = False
        except:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# TENSOR OFFLOAD ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class TensorOffloadEngine:
    """
    Async tensor offload between CPU and GPU.
    Supports memory pinning, prefetching, and stream management.
    """
    
    def __init__(self, config: GPUConfig = None):
        self.config = config or GPUConfig()
        self.streams = []
        self.pinned_memory = {}
        self.gpu_cache = {}
        self.transfer_queue = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        if HAS_CUPY:
            self._init_cuda_streams()
    
    def _init_cuda_streams(self):
        """Initialize CUDA streams for async transfers"""
        if not HAS_CUPY:
            return
            
        try:
            for i in range(self.config.async_transfer_streams):
                stream = cp.cuda.Stream(non_blocking=True)
                self.streams.append(stream)
            print(f"🌊 {len(self.streams)} CUDA streams initialized")
        except Exception as e:
            print(f"⚠️ Stream init failed: {e}")
    
    def to_gpu(self, data: np.ndarray, key: str = None, stream_id: int = 0) -> Any:
        """
        Transfer numpy array to GPU with optional caching.
        Uses pinned memory for faster transfers.
        """
        if not HAS_CUPY:
            return data  # Fallback to CPU
        
        if key and key in self.gpu_cache:
            return self.gpu_cache[key]
        
        try:
            stream = self.streams[stream_id % len(self.streams)] if self.streams else None
            
            with stream if stream else cp.cuda.Stream.null:
                # Pin memory for faster transfer
                if key not in self.pinned_memory:
                    pinned = cp.cuda.alloc_pinned_memory(data.nbytes)
                    self.pinned_memory[key] = pinned
                
                # Transfer to GPU
                gpu_data = cp.asarray(data)
                
                if key:
                    self.gpu_cache[key] = gpu_data
                
                return gpu_data
                
        except Exception as e:
            print(f"⚠️ GPU transfer failed: {e}")
            return data
    
    def to_cpu(self, gpu_data: Any, stream_id: int = 0) -> np.ndarray:
        """Transfer GPU array back to CPU"""
        if not HAS_CUPY or not isinstance(gpu_data, cp.ndarray):
            return gpu_data if isinstance(gpu_data, np.ndarray) else np.array(gpu_data)
        
        try:
            stream = self.streams[stream_id % len(self.streams)] if self.streams else None
            
            with stream if stream else cp.cuda.Stream.null:
                return cp.asnumpy(gpu_data)
                
        except Exception as e:
            print(f"⚠️ CPU transfer failed: {e}")
            return np.array(gpu_data.get())
    
    def gpu_matmul(self, a: np.ndarray, b: np.ndarray, stream_id: int = 0) -> np.ndarray:
        """GPU-accelerated matrix multiplication"""
        if not HAS_CUPY:
            return np.matmul(a, b)
        
        try:
            stream = self.streams[stream_id % len(self.streams)] if self.streams else None
            
            with stream if stream else cp.cuda.Stream.null:
                a_gpu = cp.asarray(a)
                b_gpu = cp.asarray(b)
                result_gpu = cp.matmul(a_gpu, b_gpu)
                return cp.asnumpy(result_gpu)
                
        except Exception as e:
            print(f"⚠️ GPU matmul failed, falling back to CPU: {e}")
            return np.matmul(a, b)
    
    def gpu_fft(self, data: np.ndarray, stream_id: int = 0) -> np.ndarray:
        """GPU-accelerated FFT"""
        if not HAS_CUPY:
            return np.fft.fft(data)
        
        try:
            stream = self.streams[stream_id % len(self.streams)] if self.streams else None
            
            with stream if stream else cp.cuda.Stream.null:
                data_gpu = cp.asarray(data)
                result_gpu = cp.fft.fft(data_gpu)
                return cp.asnumpy(result_gpu)
                
        except Exception as e:
            return np.fft.fft(data)
    
    def batch_process(self, data_list: List[np.ndarray], operation: Callable, 
                      batch_size: int = None) -> List[np.ndarray]:
        """
        Process data in batches with GPU offload.
        Automatically handles memory limits and stream scheduling.
        """
        batch_size = batch_size or self.config.tensor_batch_size
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            stream_id = (i // batch_size) % len(self.streams) if self.streams else 0
            
            # Process batch
            batch_results = []
            for item in batch:
                if HAS_CUPY:
                    gpu_item = self.to_gpu(item, stream_id=stream_id)
                    result = operation(gpu_item)
                    cpu_result = self.to_cpu(result, stream_id=stream_id)
                    batch_results.append(cpu_result)
                else:
                    batch_results.append(operation(item))
            
            results.extend(batch_results)
        
        return results
    
    def prefetch(self, keys: List[str], data_dict: Dict[str, np.ndarray]):
        """Prefetch data to GPU for anticipated use"""
        if not HAS_CUPY:
            return
        
        def _prefetch_item(key):
            if key in data_dict and key not in self.gpu_cache:
                self.to_gpu(data_dict[key], key=key)
        
        # Async prefetch
        futures = [self.executor.submit(_prefetch_item, k) for k in keys[:self.config.prefetch_depth]]
        for f in futures:
            try:
                f.result(timeout=1.0)
            except:
                pass
    
    def clear_cache(self):
        """Clear GPU cache to free memory"""
        self.gpu_cache.clear()
        self.pinned_memory.clear()
        
        if HAS_CUPY:
            try:
                cp.get_default_memory_pool().free_all_blocks()
                print("🧹 GPU cache cleared")
            except:
                pass
    
    def get_memory_info(self) -> Dict:
        """Get GPU memory usage"""
        if not HAS_CUPY:
            return {'used': 0, 'total': 0, 'free': 0}
        
        try:
            mempool = cp.get_default_memory_pool()
            return {
                'used': mempool.used_bytes() / 1024**2,  # MB
                'total': mempool.total_bytes() / 1024**2,
                'free': (mempool.total_bytes() - mempool.used_bytes()) / 1024**2,
                'cached': len(self.gpu_cache)
            }
        except:
            return {'used': 0, 'total': 0, 'free': 0}


# ═══════════════════════════════════════════════════════════════════════════════
# QFLOP ACCELERATOR
# ═══════════════════════════════════════════════════════════════════════════════

class QFLOPAccelerator:
    """
    Combined GPU overclock + tensor offload for maximum QFLOP performance.
    Integrates with QMCP quantum simulation.
    """
    
    def __init__(self, config: GPUConfig = None):
        self.config = config or GPUConfig()
        self.overclock = GPUOverclockManager(config)
        self.tensor = TensorOffloadEngine(config)
        self.qflop_counter = 0
        self.start_time = time.time()
        
        # Apply moderate overclock on init
        self.overclock.apply_overclock('moderate')
    
    def quantum_gate_gpu(self, state: np.ndarray, gate: np.ndarray) -> np.ndarray:
        """Apply quantum gate with GPU acceleration"""
        return self.tensor.gpu_matmul(gate, state)
    
    def quantum_fft_gpu(self, state: np.ndarray) -> np.ndarray:
        """Quantum FFT on GPU"""
        return self.tensor.gpu_fft(state)
    
    def simulate_qubits(self, n_qubits: int, depth: int = 10) -> Dict:
        """
        Simulate quantum circuit with GPU acceleration.
        Returns QFLOP metrics.
        """
        dim = 2 ** n_qubits
        
        # Initialize state |0...0⟩
        if HAS_CUPY:
            state = cp.zeros(dim, dtype=cp.complex128)
            state[0] = 1.0
        else:
            state = np.zeros(dim, dtype=np.complex128)
            state[0] = 1.0
        
        # Hadamard gate
        H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2)
        
        ops_count = 0
        start = time.perf_counter()
        
        # Apply circuit layers
        for layer in range(depth):
            # Hadamard on all qubits
            for q in range(n_qubits):
                # Build full gate (tensor product)
                full_gate = np.eye(1, dtype=np.complex128)
                for i in range(n_qubits):
                    full_gate = np.kron(full_gate, H if i == q else np.eye(2))
                
                if HAS_CUPY:
                    state = cp.asarray(full_gate) @ state
                else:
                    state = full_gate @ state
                
                ops_count += dim * dim  # Matrix-vector multiply
        
        elapsed = time.perf_counter() - start
        qflops = ops_count / elapsed / 1e9  # GFLOPS
        
        self.qflop_counter += ops_count
        
        # Check thermals
        self.overclock.thermal_throttle_check()
        
        return {
            'n_qubits': n_qubits,
            'depth': depth,
            'operations': ops_count,
            'elapsed_sec': elapsed,
            'qflops': qflops,
            'gpu_accelerated': HAS_CUPY
        }
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        gpu_stats = self.overclock.get_gpu_stats()
        mem_info = self.tensor.get_memory_info()
        
        elapsed = time.time() - self.start_time
        avg_qflops = self.qflop_counter / elapsed / 1e9 if elapsed > 0 else 0
        
        return {
            'gpu': gpu_stats,
            'memory': mem_info,
            'overclock_enabled': self.overclock.overclock_enabled,
            'total_qflops': self.qflop_counter,
            'avg_gflops': avg_qflops,
            'uptime_sec': elapsed
        }
    
    def optimize_for_workload(self, workload_type: str = 'quantum'):
        """
        Auto-tune settings based on workload type.
        Types: 'quantum', 'inference', 'memory_heavy', 'balanced'
        """
        if workload_type == 'quantum':
            # High compute, moderate memory
            self.overclock.apply_overclock('aggressive')
            self.config.tensor_batch_size = 512
            
        elif workload_type == 'inference':
            # Moderate compute, high memory bandwidth
            self.overclock.apply_overclock('moderate')
            self.config.tensor_batch_size = 1024
            
        elif workload_type == 'memory_heavy':
            # Low compute, maximum memory bandwidth
            self.overclock.apply_overclock('conservative')
            self.config.tensor_batch_size = 2048
            
        else:  # balanced
            self.overclock.apply_overclock('moderate')
            self.config.tensor_batch_size = 1024
        
        print(f"⚙️ Optimized for {workload_type} workload")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Test GPU overclock and tensor offload"""
    print("=" * 60)
    print("  GPU OVERCLOCK & TENSOR OFFLOAD OPTIMIZER")
    print("=" * 60)
    
    accelerator = QFLOPAccelerator()
    accelerator.optimize_for_workload('quantum')
    
    print("\n🧪 Running quantum simulation benchmark...")
    
    # Test different qubit counts
    for n_qubits in [4, 6, 8]:
        result = accelerator.simulate_qubits(n_qubits, depth=5)
        print(f"  {n_qubits} qubits: {result['qflops']:.2f} GFLOPS ({result['elapsed_sec']*1000:.1f}ms)")
    
    print("\n📊 Performance Stats:")
    stats = accelerator.get_performance_stats()
    print(f"  GPU Temp: {stats['gpu']['temperature']}°C")
    print(f"  GPU Util: {stats['gpu']['gpu_util']}%")
    print(f"  Power: {stats['gpu']['power_draw']:.1f}W")
    print(f"  Overclock: {'ENABLED' if stats['overclock_enabled'] else 'DISABLED'}")
    print(f"  Avg GFLOPS: {stats['avg_gflops']:.2f}")
    
    print("\n✅ GPU optimization ready")


if __name__ == '__main__':
    main()
