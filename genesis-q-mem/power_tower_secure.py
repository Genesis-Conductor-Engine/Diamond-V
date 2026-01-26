#!/usr/bin/env python3
"""
Q-Mem Power Tower with Authentication
Secured version of orchestrator and model services with API key auth
"""

import sys
import argparse
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import uvicorn
import signal
import atexit
import logging

# Import Q-Mem Core and Auth
from qmem_core import QuantumPotentiator, QuantumArbiter, QuantumState
from qmem_auth import verify_api_key

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Q-MEM SECURE] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response models
class PotentiateRequest(BaseModel):
    shape: List[int]
    dtype: str = "float32"
    state_id: Optional[str] = None

class RetrieveRequest(BaseModel):
    shm_name: str
    shape: List[int]
    dtype: str
    size_bytes: int

# Orchestrator Service (Secured)
class SecureOrchestratorService:
    def __init__(self, max_memory_gb: float = 1.5):
        self.app = FastAPI(title="Q-Mem Orchestrator (Secured)")
        self.potentiator = QuantumPotentiator(max_memory_gb=max_memory_gb)
        
        # Register cleanup
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Secure Orchestrator initialized with {max_memory_gb:.2f} GB capacity")
        self._setup_routes()
    
    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        self.potentiator.cleanup_all()
    
    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            """Public health check endpoint (no auth required)"""
            return {
                "status": "healthy",
                "service": "orchestrator",
                "level": "2-potentiator",
                "secured": True
            }
        
        @self.app.post("/potentiate")
        async def potentiate(request: PotentiateRequest, 
                           api_key: str = Depends(verify_api_key)):
            """Secured endpoint - requires API key"""
            try:
                # Generate random data
                shape = tuple(request.shape)
                dtype = np.dtype(request.dtype)
                data = np.random.randn(*shape).astype(dtype)
                
                # Potentiate to shared memory
                state = self.potentiator.potentiate(
                    data=data,
                    state_id=request.state_id
                )
                
                size_mb = state.size_bytes / (1024 * 1024)
                logger.info(f"✓ Potentiated {size_mb:.2f} MB - {state.shm_name}")
                
                return {
                    "state_id": state.state_id,
                    "shm_name": state.shm_name,
                    "shape": state.shape,
                    "dtype": state.dtype,
                    "size_bytes": state.size_bytes,
                    "message": f"Potentiated {size_mb:.2f} MB - pointer ready"
                }
            except Exception as e:
                logger.error(f"Potentiation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/stats")
        async def stats(api_key: str = Depends(verify_api_key)):
            """Get memory statistics (secured)"""
            return self.potentiator.get_stats()
        
        @self.app.delete("/states/{shm_name}")
        async def cleanup_state(shm_name: str, 
                               api_key: str = Depends(verify_api_key)):
            """Cleanup specific state (secured)"""
            success = self.potentiator.collapse(shm_name)
            if success:
                return {"status": "collapsed", "shm_name": shm_name}
            raise HTTPException(status_code=404, detail="State not found")
        
        @self.app.post("/cleanup")
        async def cleanup_all(api_key: str = Depends(verify_api_key)):
            """Emergency cleanup (secured)"""
            self.cleanup()
            return {"status": "cleaned", "message": "All states collapsed"}
    
    def run(self, host: str = "0.0.0.0", port: int = 8001):
        logger.info(f"Starting Secure Orchestrator on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")

# Model Service (Secured)
class SecureModelService:
    def __init__(self):
        self.app = FastAPI(title="Q-Mem Model Service (Secured)")
        self.arbiter = QuantumArbiter()
        
        logger.info("Secure Model Service initialized")
        self._setup_routes()
    
    def _setup_routes(self):
        @self.app.get("/health")
        async def health():
            """Public health check endpoint (no auth required)"""
            return {
                "status": "healthy",
                "service": "model",
                "level": "3-arbiter",
                "secured": True
            }
        
        @self.app.post("/retrieve")
        async def retrieve(request: RetrieveRequest,
                         api_key: str = Depends(verify_api_key)):
            """Secured endpoint - requires API key"""
            try:
                state = QuantumState(
                    state_id="",
                    shm_name=request.shm_name,
                    shape=tuple(request.shape),
                    dtype=request.dtype,
                    size_bytes=request.size_bytes
                )
                
                tensor = self.arbiter.retrieve(state)
                
                size_mb = state.size_bytes / (1024 * 1024)
                logger.info(f"✓ Retrieved {size_mb:.2f} MB - {state.shm_name}")
                
                return {
                    "status": "success",
                    "shm_name": request.shm_name,
                    "shape": list(tensor.shape),
                    "dtype": str(tensor.dtype),
                    "size_mb": size_mb,
                    "message": "Tensor ready for GPU transfer"
                }
            except Exception as e:
                logger.error(f"Retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def run(self, host: str = "0.0.0.0", port: int = 8002):
        logger.info(f"Starting Secure Model Service on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")

def main():
    parser = argparse.ArgumentParser(description="Q-Mem Power Tower (Secured)")
    parser.add_argument("mode", choices=["orchestrator", "model"],
                       help="Service mode to run")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                       help="Host to bind to (default: 0.0.0.0)")
    
    args = parser.parse_args()
    
    if args.mode == "orchestrator":
        port = args.port or 8001
        service = SecureOrchestratorService()
        service.run(host=args.host, port=port)
    elif args.mode == "model":
        port = args.port or 8002
        service = SecureModelService()
        service.run(host=args.host, port=port)

if __name__ == "__main__":
    main()
