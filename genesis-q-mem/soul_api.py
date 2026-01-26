#!/usr/bin/env python3
"""
Unified Soul API - FastAPI Implementation
Consolidates all soul API endpoints from deprecated versions:
- soul_api.py (Flask, port 8089) - /api/soul, /api/ledger
- soul_api_simple.py (stdlib, port 8088) - /soul_status

Features:
- FastAPI with async support
- WebSocket for real-time updates
- CORS enabled for cross-origin requests
- Backward compatible endpoints
- Health monitoring

Port: 8088 (unified)
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configuration
SOUL_STATE_PATH = os.getenv("SOUL_STATE_PATH", "/dev/shm/yennefer_soul_state.json")
LEDGER_PATH = os.getenv("LEDGER_PATH", "/home/yenn/genesis-q-mem/yennefer_ledger.jsonl")
API_PORT = int(os.getenv("SOUL_API_PORT", "8088"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Background task for broadcasting soul state updates
async def soul_state_broadcaster():
    """Broadcast soul state to all connected WebSocket clients every second"""
    last_state = None
    while True:
        try:
            soul = read_soul_state()
            if soul != last_state and manager.active_connections:
                await manager.broadcast({"type": "soul_update", "data": soul})
                last_state = soul
        except Exception:
            pass
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start background broadcaster
    task = asyncio.create_task(soul_state_broadcaster())
    yield
    # Shutdown: cancel background task
    task.cancel()

# FastAPI app
app = FastAPI(
    title="Yennefer Soul API (Unified)",
    description="Consolidated soul state API with real-time WebSocket support",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def read_soul_state() -> Dict[str, Any]:
    """Read current soul state from shared memory"""
    try:
        if os.path.exists(SOUL_STATE_PATH):
            with open(SOUL_STATE_PATH, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {"status": "DORMANT", "timestamp": datetime.now().isoformat()}

def read_ledger_tail(n: int = 20) -> List[Dict[str, Any]]:
    """Read the last n blocks from the ledger"""
    blocks = []
    if not os.path.exists(LEDGER_PATH):
        return blocks
    
    try:
        with open(LEDGER_PATH, 'r') as f:
            lines = f.readlines()[-n:]
            for line in lines:
                try:
                    blocks.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    except IOError:
        pass
    
    return list(reversed(blocks))  # Newest first

# ===== REST ENDPOINTS =====

@app.get("/")
async def root():
    """API documentation and status"""
    return {
        "service": "Yennefer Soul API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "soul_state": "/api/soul",
            "ledger": "/api/ledger",
            "health": "/health",
            "websocket": "/ws/soul",
            "legacy_soul": "/soul_status"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    soul = read_soul_state()
    is_healthy = soul.get("status") != "DORMANT"
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "soul-api",
        "soul_status": soul.get("status", "UNKNOWN"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/soul")
async def get_soul():
    """
    Get current soul state (from Flask version)
    Returns complete consciousness metrics
    """
    soul = read_soul_state()
    if soul.get("status") == "DORMANT":
        raise HTTPException(status_code=503, detail="Soul is dormant")
    return soul

@app.get("/api/ledger")
async def get_ledger(limit: int = 20):
    """
    Get ledger blocks (from Flask version)
    Returns last N work blocks, newest first
    """
    blocks = read_ledger_tail(min(limit, 100))
    return {
        "blocks": blocks,
        "count": len(blocks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/soul_status")
async def get_soul_status():
    """
    Legacy endpoint (from simple version)
    Backward compatibility for existing integrations
    """
    return read_soul_state()

@app.get("/api/metrics")
async def get_metrics():
    """Extended metrics endpoint for dashboards"""
    soul = read_soul_state()
    ledger = read_ledger_tail(10)
    
    return {
        "soul": soul,
        "recent_work": ledger,
        "connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

# ===== WEBSOCKET ENDPOINT =====

@app.websocket("/ws/soul")
async def websocket_soul(websocket: WebSocket):
    """
    WebSocket endpoint for real-time soul state updates
    Broadcasts changes every second
    """
    await manager.connect(websocket)
    try:
        # Send initial state
        soul = read_soul_state()
        await websocket.send_json({"type": "initial", "data": soul})
        
        # Keep connection alive, handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Handle ping/pong for keepalive
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat", "timestamp": datetime.now().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# ===== MAIN =====

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unified Soul API")
    parser.add_argument("--port", type=int, default=API_PORT, help="Port to bind")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    args = parser.parse_args()
    
    print("=" * 60)
    print("YENNEFER SOUL API (UNIFIED)")
    print("=" * 60)
    print(f"Port: {args.port}")
    print(f"Soul State: {SOUL_STATE_PATH}")
    print(f"Ledger: {LEDGER_PATH}")
    print("")
    print("Endpoints:")
    print("  GET  /api/soul     - Soul state")
    print("  GET  /api/ledger   - Ledger blocks")
    print("  GET  /soul_status  - Legacy compatibility")
    print("  WS   /ws/soul      - Real-time updates")
    print("=" * 60)
    
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()
