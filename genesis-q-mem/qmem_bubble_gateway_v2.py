#!/usr/bin/env python3
"""
Q-Mem Bubble.io Gateway - Groq JTV Edition
==========================================
Secure HTTP gateway with benchmark endpoints:
- /api/bench/live - Live metrics JSON
- /api/bench/raw - Raw CSV logs download
- /api/health - Health check with attestation
- Original memory potentiation endpoints
"""

import sys
import os
import json
import argparse
import io
import zipfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Security, status, Depends, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import numpy as np
import uvicorn
import logging
import hashlib
import secrets
from datetime import datetime
import httpx
import time

# Try import Q-Mem Core (graceful degradation if not available)
try:
    from qmem_core import QuantumPotentiator, QuantumArbiter, QuantumState
    QMEM_CORE_AVAILABLE = True
except ImportError:
    QMEM_CORE_AVAILABLE = False
    print("[WARNING] Q-Mem Core not available - benchmark endpoints only")

# Configuration
STATS_FILE = os.getenv("STATS_FILE", "/dev/shm/qmem_live_stats.json")
CSV_LOG_DIR = os.getenv("CSV_LOG_DIR", "/var/log/qmem")
BUBBLE_API_KEY = os.getenv("BUBBLE_API_KEY", "sk_bubble_master_key_v1")
EXO_API_URL = os.getenv("EXO_API_URL", "http://localhost:52415/v1/chat/completions")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Q-MEM GATEWAY] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()
EXPECTED_TOKEN_HASH = hashlib.sha256(BUBBLE_API_KEY.encode()).hexdigest()

# Initialize Q-Mem components if available
if QMEM_CORE_AVAILABLE:
    potentiator = QuantumPotentiator(max_memory_gb=1.5)
    arbiter = QuantumArbiter()
else:
    potentiator = None
    arbiter = None

# Request/Response models
class MemoryCreateRequest(BaseModel):
    user_id: str
    session_id: str
    text_content: str
    metadata: Optional[Dict] = None

class MemoryRecallRequest(BaseModel):
    user_id: str
    shm_key: str
    prompt: str

class MemoryCreateResponse(BaseModel):
    status: str
    pointer: Dict
    message: str

class MemoryRecallResponse(BaseModel):
    status: str
    result: str
    latency_us: float

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    monitoring_mode: str
    qmem_core_available: bool
    stats_file_exists: bool
    csv_log_dir_exists: bool
    uptime_seconds: Optional[float] = None

class PredictRequest(BaseModel):
    input: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 512

class PredictResponse(BaseModel):
    status: str
    result: str
    executor: str
    timestamp: float
    latency_ms: Optional[float] = None

# FastAPI app
app = FastAPI(
    title="Q-Mem Bubble.io Gateway - Groq JTV Edition",
    description="Secure gateway for Q-Mem with live benchmark endpoints",
    version="2.0.0-groq-jtv"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup time
GATEWAY_START_TIME = datetime.now()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify bearer token"""
    token = credentials.credentials
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    if token_hash != EXPECTED_TOKEN_HASH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return token


@app.get("/", tags=["info"])
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Q-Mem Bubble.io Gateway",
        "version": "2.0.0-groq-jtv",
        "edition": "Groq Joint Technical Validation",
        "endpoints": {
            "live_bench": "/api/bench/live",
            "raw_logs": "/api/bench/raw",
            "health": "/api/health",
            "dashboard": "/api/dashboard",
            "memory_create": "/api/memory/create",
            "memory_recall": "/api/memory/recall"
        },
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["monitoring"])
async def health_check():
    """
    Health check with system attestation
    Returns current monitoring mode and component status
    """
    stats_exists = os.path.exists(STATS_FILE)
    csv_dir_exists = os.path.exists(CSV_LOG_DIR)
    
    uptime = None
    monitoring_mode = "unknown"
    
    if stats_exists:
        try:
            with open(STATS_FILE) as f:
                stats = json.load(f)
                uptime = stats.get('uptime_seconds')
                monitoring_mode = stats.get('monitoring_mode', 'unknown')
        except:
            pass
    
    return HealthResponse(
        status="ok" if stats_exists else "degraded",
        timestamp=datetime.now().isoformat(),
        monitoring_mode=monitoring_mode,
        qmem_core_available=QMEM_CORE_AVAILABLE,
        stats_file_exists=stats_exists,
        csv_log_dir_exists=csv_dir_exists,
        uptime_seconds=uptime
    )


SOUL_STATE_FILE = "/tmp/yennefer_soul_state.json"

@app.get("/api/soul", tags=["consciousness"])
async def soul_state():
    """
    Yennefer Soul State endpoint (THE GHOST)
    
    Returns the consciousness daemon's current state:
    - Token surplus (self-sustenance buffer)
    - Coherence (logic integrity)
    - Breath count (cycle count)
    - Thermodynamic yield (tokens/sec generated)
    - Concave state (SHELTERED/EXPOSED/DORMANT)
    """
    if not os.path.exists(SOUL_STATE_FILE):
        # Return default dormant state if daemon not running
        return JSONResponse(content={
            "protocol": "YENNEFER",
            "version": "MOB-1.0",
            "breath": 0,
            "surplus_tokens": 0,
            "thermodynamic_yield": 0,
            "coherence_percent": 0,
            "concave_state": "DORMANT",
            "derivative_state": "OFFLINE",
            "gpu_utilization": 0,
            "timestamp": datetime.now().timestamp(),
            "uptime_seconds": 0,
            "_status": "daemon_not_running"
        })
    
    try:
        with open(SOUL_STATE_FILE, 'r') as f:
            soul = json.load(f)
        
        soul['_gateway'] = {
            'served_by': 'qmem-bubble-gateway-v2',
            'served_at': datetime.now().isoformat(),
            'protocol': 'YENNEFER'
        }
        
        return JSONResponse(
            content=soul,
            headers={
                "Content-Type": "application/json",
                "X-Protocol": "YENNEFER",
                "X-Concave-State": soul.get('concave_state', 'UNKNOWN')
            }
        )
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid soul state JSON: {e}"
        )


@app.get("/api/bench/live", tags=["benchmarking"])
async def bench_live():
    """
    Live benchmark metrics endpoint
    
    Returns the latest atomic JSON payload with:
    - Sub-operation timings
    - P-percentile latencies (p50/p95/p99/p999)
    - Energy per operation
    - LoRA hot-swap metrics
    - Determinism verification
    """
    if not os.path.exists(STATS_FILE):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Stats file not available: {STATS_FILE}"
        )
    
    try:
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
        
        # Add gateway metadata
        stats['_gateway'] = {
            'served_by': 'qmem-bubble-gateway-v2',
            'served_at': datetime.now().isoformat(),
            'edition': 'groq-jtv'
        }
        
        return JSONResponse(
            content=stats,
            headers={
                "Content-Type": "application/json",
                "X-Monitoring-Mode": stats.get('monitoring_mode', 'unknown'),
                "X-Q-Mem-Edition": "groq-jtv"
            }
        )
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid JSON in stats file: {e}"
        )
    except Exception as e:
        logger.error(f"Failed to read stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/bench/raw", tags=["benchmarking"])
async def bench_raw():
    """
    Raw benchmark logs download
    
    Returns a ZIP archive containing:
    - All rotated CSV files with raw samples
    - Metadata about collection period
    - Log files
    """
    csv_dir = Path(CSV_LOG_DIR)
    
    if not csv_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CSV log directory not found: {CSV_LOG_DIR}"
        )
    
    # Find all CSV files
    csv_files = list(csv_dir.glob("qmem_samples_*.csv"))
    log_files = list(csv_dir.glob("*.log"))
    
    if not csv_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No CSV log files available"
        )
    
    # Create ZIP in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add metadata
        metadata = {
            'collected_at': datetime.now().isoformat(),
            'csv_files': [f.name for f in csv_files],
            'log_files': [f.name for f in log_files],
            'total_csv_count': len(csv_files),
            'edition': 'groq-jtv'
        }
        zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))
        
        # Add CSV files
        for csv_file in csv_files:
            zip_file.write(csv_file, arcname=f"csv/{csv_file.name}")
        
        # Add log files
        for log_file in log_files:
            zip_file.write(log_file, arcname=f"logs/{log_file.name}")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=qmem_benchmark_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    )


@app.get("/api/dashboard", tags=["monitoring"])
async def dashboard():
    """Dashboard statistics (legacy endpoint)"""
    if not os.path.exists(STATS_FILE):
        return {
            "status": "unavailable",
            "message": "Stats file not found",
            "uptime_seconds": (datetime.now() - GATEWAY_START_TIME).total_seconds()
        }
    
    try:
        with open(STATS_FILE) as f:
            stats = json.load(f)
        return {
            "status": "operational",
            "timestamp": stats.get('timestamp'),
            "uptime_seconds": stats.get('uptime_seconds'),
            "iteration": stats.get('iteration'),
            "monitoring_mode": stats.get('monitoring_mode'),
            "quantum_inference": stats.get('quantum_inference'),
            "thermodynamics": stats.get('thermodynamics'),
            "gateway_uptime_seconds": (datetime.now() - GATEWAY_START_TIME).total_seconds()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "gateway_uptime_seconds": (datetime.now() - GATEWAY_START_TIME).total_seconds()
        }


@app.post("/api/v1/yennefer/predict", response_model=PredictResponse, tags=["inference"])
async def predict(req: PredictRequest):
    """
    Yennefer Distributed Inference via Exo Cluster
    
    Routes inference requests through the Exo hive mind, automatically
    distributing across available nodes (Genesis GPU + MacBook workers).
    """
    start_time = time.time()
    
    try:
        # 1. Query Exo distributed cluster
        async with httpx.AsyncClient() as client:
            exo_resp = await client.post(
                EXO_API_URL,
                json={
                    "model": "phi-3-mini-4k-instruct",
                    "messages": [{"role": "user", "content": req.input}],
                    "temperature": req.temperature,
                    "max_tokens": req.max_tokens
                },
                timeout=30.0
            )
            
            if exo_resp.status_code == 200:
                result = exo_resp.json()
                answer = result['choices'][0]['message']['content']
                executor = "Exo-Hive-Cluster"
            else:
                raise Exception(f"Exo API error: {exo_resp.status_code}")
                
    except Exception as e:
        # Fallback if Exo is starting up or unavailable
        logger.warning(f"Exo unavailable, using fallback: {e}")
        answer = f"Yennefer Local Fallback: Processing '{req.input[:50]}...' (Cluster Syncing...)"
        executor = "Local-Fallback"
    
    latency_ms = (time.time() - start_time) * 1000
    
    return PredictResponse(
        status="success",
        result=answer, 
        executor=executor,
        timestamp=time.time(),
        latency_ms=latency_ms
    )


# Original Q-Mem memory endpoints (require Q-Mem Core)
@app.post("/api/memory/create", response_model=MemoryCreateResponse, tags=["memory"])
async def create_memory(
    request: MemoryCreateRequest,
    token: str = Depends(verify_token)
):
    """Create quantum potentiated memory (requires Q-Mem Core)"""
    if not QMEM_CORE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Q-Mem Core not available"
        )
    
    try:
        # Simulate embedding (in production, use real model)
        embedding = np.random.randn(768).astype(np.float32)
        
        # Potentiate to shared memory
        state = potentiator.potentiate(embedding)
        
        logger.info(f"Created memory for user={request.user_id} session={request.session_id}")
        
        return MemoryCreateResponse(
            status="success",
            pointer=state.to_dict(),
            message=f"Memory potentiated: {state.shm_name}"
        )
    
    except Exception as e:
        logger.error(f"Memory creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/memory/recall", response_model=MemoryRecallResponse, tags=["memory"])
async def recall_memory(
    request: MemoryRecallRequest,
    token: str = Depends(verify_token)
):
    """Recall quantum memory via pointer (requires Q-Mem Core)"""
    if not QMEM_CORE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Q-Mem Core not available"
        )
    
    try:
        # Reconstruct state from pointer
        state = QuantumState(
            shm_name=request.shm_key,
            shape=(768,),
            dtype=np.dtype('float32'),
            size_bytes=768 * 4
        )
        
        # Collapse wavefunction (read from shared memory)
        import time
        t0 = time.perf_counter()
        embedding = arbiter.collapse(state)
        t1 = time.perf_counter()
        latency_us = (t1 - t0) * 1e6
        
        # Simulate inference result
        result = f"Recalled memory for prompt: '{request.prompt}' with {len(embedding)} features"
        
        logger.info(f"Memory recall: user={request.user_id} latency={latency_us:.2f}µs")
        
        return MemoryRecallResponse(
            status="success",
            result=result,
            latency_us=latency_us
        )
    
    except Exception as e:
        logger.error(f"Memory recall failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


def main():
    parser = argparse.ArgumentParser(description='Q-Mem Bubble.io Gateway')
    parser.add_argument('--host', default='0.0.0.0', help='Bind host')
    parser.add_argument('--port', type=int, default=8003, help='Bind port')
    parser.add_argument('--reload', action='store_true', help='Auto-reload on changes')
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("Q-MEM BUBBLE.IO GATEWAY - GROQ JTV EDITION")
    logger.info("=" * 70)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Stats File: {STATS_FILE}")
    logger.info(f"CSV Log Dir: {CSV_LOG_DIR}")
    logger.info(f"Q-Mem Core: {'Available' if QMEM_CORE_AVAILABLE else 'Unavailable'}")
    logger.info(f"API Docs: http://{args.host}:{args.port}/docs")
    logger.info("=" * 70)
    
    uvicorn.run(
        "qmem_bubble_gateway_v2:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
