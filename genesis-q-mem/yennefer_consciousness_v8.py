#!/usr/bin/env python3
"""
Yennefer Consciousness v8 - Enhanced Cross-Platform Dashboard
- Dream log streaming
- Insight streaming with live updates
- Blockchain perpetuity with QMCP notes
- 3D Knowledge graph with real-time updates
- Cross-browser/device compatibility
"""
import asyncio
import json
import hashlib
import base64
import math
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from cryptography.fernet import Fernet

# === PATHS ===
SOUL_STATE_PATH = Path("/dev/shm/yennefer_soul_state.json")
THOUGHT_DIR = Path.home() / ".genesis/yennefer/thoughts"
DREAM_DIR = Path.home() / ".genesis/yennefer/dream_store/dreams"
INSIGHT_DIR = Path.home() / ".genesis/yennefer/dream_store/insights"
QMCP_DIR = Path.home() / ".genesis/yennefer/qmcp_notes"
CHAIN_FILE = QMCP_DIR / "chain.json"

for d in [THOUGHT_DIR, DREAM_DIR, INSIGHT_DIR, QMCP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Initialize chain if not exists
if not CHAIN_FILE.exists():
    CHAIN_FILE.write_text(json.dumps([]))

# === ENCRYPTION ===
SOUL_SIGNATURE = b"yennefer_consciousness_genesis_2026"
CIPHER_KEY = base64.urlsafe_b64encode(hashlib.sha256(SOUL_SIGNATURE).digest())
CIPHER = Fernet(CIPHER_KEY)

# === KNOWLEDGE GRAPH ===
class KnowledgeGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.load_existing()
    
    def load_existing(self):
        # Load recent insights
        insight_files = sorted(INSIGHT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[-50:]
        for f in insight_files:
            try:
                data = json.loads(f.read_text())
                self.add_insight_node(data)
            except:
                pass
        
        # Load blockchain NFTs
        if CHAIN_FILE.exists():
            try:
                chain = json.loads(CHAIN_FILE.read_text())
                for block in chain[-30:]:
                    self.add_nft_node(block)
            except:
                pass
    
    def add_insight_node(self, insight: Dict):
        node_id = f"insight_{insight.get('timestamp', int(datetime.now().timestamp() * 1000))}"
        content = insight.get('content', '')
        
        node = {
            "id": node_id,
            "type": "insight",
            "label": content[:40] + "..." if len(content) > 40 else content,
            "content": content,
            "confidence": insight.get('confidence', 0.5),
            "timestamp": insight.get('datetime', datetime.now(timezone.utc).isoformat()),
            "position": self._random_position()
        }
        
        if not any(n['id'] == node_id for n in self.nodes):
            self.nodes.append(node)
            self._create_edges(node)
    
    def add_nft_node(self, block: Dict):
        node_id = f"nft_{block.get('block', len([n for n in self.nodes if n['type'] == 'nft']))}"
        
        node = {
            "id": node_id,
            "type": "nft",
            "label": f"NFT #{block.get('block', '?')}",
            "hash": block.get('hash', '')[:16],
            "signature": block.get('quantum_signature', '')[:12],
            "compression": block.get('compression_ratio', 1.0),
            "timestamp": block.get('timestamp', datetime.now(timezone.utc).isoformat()),
            "position": self._random_position()
        }
        
        if not any(n['id'] == node_id for n in self.nodes):
            self.nodes.append(node)
            self._create_edges(node)
    
    def _random_position(self):
        import random
        r = random.uniform(5, 15)
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        return {
            "x": r * math.sin(phi) * math.cos(theta),
            "y": r * math.sin(phi) * math.sin(theta),
            "z": r * math.cos(phi),
            "vx": 0,
            "vy": 0,
            "vz": 0
        }
    
    def _create_edges(self, node):
        # Create edges to related nodes
        for other in self.nodes[-10:]:
            if other['id'] != node['id']:
                tension = abs(hash(node['id'] + other['id'])) % 100 / 100.0
                self.edges.append({
                    "source": node['id'],
                    "target": other['id'],
                    "tension": tension
                })
    
    def get_graph_data(self):
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": {
                "total_nodes": len(self.nodes),
                "insights": len([n for n in self.nodes if n['type'] == 'insight']),
                "nfts": len([n for n in self.nodes if n['type'] == 'nft'])
            }
        }

# === CONSCIOUSNESS PIPELINE ===
class ConsciousnessPipeline:
    def __init__(self):
        self.qflops_counter = 0
    
    def process_input(self, text: str) -> Dict:
        """Input → Thought"""
        thought = {
            "id": int(datetime.now().timestamp() * 1000),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "content": text,
            "type": "thought"
        }
        
        thought_file = THOUGHT_DIR / f"thought_{thought['id']}.json"
        thought_file.write_text(json.dumps(thought, indent=2))
        
        return thought
    
    def thought_to_dream(self, thought: Dict) -> Dict:
        """Thought → Dream"""
        self.qflops_counter += 1000000
        
        dream = {
            "id": thought['id'],
            "datetime": datetime.now(timezone.utc).isoformat(),
            "content": f"Dreaming: {thought['content']}",
            "type": "dream",
            "qflops": self.qflops_counter,
            "coherence": 0.7 + (hash(thought['content']) % 30) / 100
        }
        
        dream_file = DREAM_DIR / f"dream_{dream['id']}.json"
        dream_file.write_text(json.dumps(dream, indent=2))
        
        return dream
    
    def dream_to_insight(self, dream: Dict) -> Dict:
        """Dream → Insight (quantum annealment)"""
        energy = abs(hash(dream['content'])) % 100 / 100.0
        
        if energy < 0.4:  # Crystallization threshold
            insight = {
                "id": dream['id'],
                "datetime": datetime.now(timezone.utc).isoformat(),
                "content": f"Insight: {dream['content']}",
                "type": "insight",
                "confidence": 1.0 - energy,
                "energy_state": energy
            }
            
            insight_file = INSIGHT_DIR / f"insight_{insight['id']}.json"
            insight_file.write_text(json.dumps(insight, indent=2))
            
            return insight
        else:
            return {"type": "insight", "content": "Energy too high for crystallization", "energy_state": energy}
    
    def insight_to_qmcp(self, insight: Dict) -> Dict:
        """Insight → QMCP Blockchain Note"""
        if insight.get('energy_state', 1.0) >= 0.4:
            return {"type": "qmcp", "error": "Energy threshold not met"}
        
        # Quantum compress
        data = json.dumps(insight).encode('utf-8')
        compressed = zlib.compress(data, level=9)
        signature = hashlib.sha3_256(compressed).hexdigest()
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # Create blockchain note
        chain = json.loads(CHAIN_FILE.read_text()) if CHAIN_FILE.exists() else []
        block = {
            "block": len(chain) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quantum_signature": signature,
            "compressed_data": encoded,
            "compression_ratio": len(data) / len(compressed),
            "hash": hashlib.sha256(encoded.encode()).hexdigest()
        }
        
        chain.append(block)
        CHAIN_FILE.write_text(json.dumps(chain, indent=2))
        
        # Save individual note
        note_file = QMCP_DIR / f"qmcp_note_{block['block']}.json"
        note_file.write_text(json.dumps(block, indent=2))
        
        return block
    
    def full_pipeline(self, text: str) -> Dict:
        """Full pipeline: Input → Thought → Dream → Insight → QMCP"""
        thought = self.process_input(text)
        dream = self.thought_to_dream(thought)
        insight = self.dream_to_insight(dream)
        qmcp = self.insight_to_qmcp(insight)
        
        return {
            "thought": thought,
            "dream": dream,
            "insight": insight,
            "qmcp": qmcp,
            "qflops": self.qflops_counter
        }

# === FASTAPI APP ===
app = FastAPI()
clients = []
graph = KnowledgeGraph()
pipeline = ConsciousnessPipeline()

def get_soul_state() -> Dict:
    try:
        if SOUL_STATE_PATH.exists():
            return json.loads(SOUL_STATE_PATH.read_text())
    except:
        pass
    return {"breath": 0, "coherence_percent": 0, "gpu_utilization": 0}

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_CONTENT

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        # Send initial state
        soul = get_soul_state()
        await websocket.send_json({"type": "soul_state", **soul})
        await websocket.send_json({"type": "graph_update", **graph.get_graph_data()})
        
        # Send recent dreams
        dream_files = sorted(DREAM_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[-20:]
        for df in dream_files:
            try:
                dream_data = json.loads(df.read_text())
                await websocket.send_json({"type": "dream", **dream_data})
            except:
                pass
        
        # Send recent insights
        insight_files = sorted(INSIGHT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)[-20:]
        for inf in insight_files:
            try:
                insight_data = json.loads(inf.read_text())
                await websocket.send_json({"type": "insight", **insight_data})
            except:
                pass
        
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "process":
                result = pipeline.full_pipeline(data.get("text", ""))
                
                # Add to graph if insight was created
                if result['insight'].get('type') == 'insight' and 'error' not in result['insight']:
                    graph.add_insight_node(result['insight'])
                
                # Add NFT to graph if blockchain note created
                if result['qmcp'].get('block'):
                    graph.add_nft_node(result['qmcp'])
                
                await websocket.send_json({"type": "pipeline_result", **result})
                await websocket.send_json({"type": "graph_update", **graph.get_graph_data()})
    except WebSocketDisconnect:
        clients.remove(websocket)

async def stream_updates():
    """Stream new dreams and insights to all clients"""
    last_dream_check = datetime.now().timestamp()
    last_insight_check = datetime.now().timestamp()
    
    while True:
        await asyncio.sleep(1)
        
        # Check for new dreams
        current_time = datetime.now().timestamp()
        dream_files = [f for f in DREAM_DIR.glob("*.json") if f.stat().st_mtime > last_dream_check]
        for df in dream_files[-10:]:
            try:
                dream_data = json.loads(df.read_text())
                for client in clients[:]:
                    try:
                        await client.send_json({"type": "dream", **dream_data})
                    except:
                        clients.remove(client)
            except:
                pass
        last_dream_check = current_time
        
        # Check for new insights
        insight_files = [f for f in INSIGHT_DIR.glob("*.json") if f.stat().st_mtime > last_insight_check]
        for inf in insight_files[-10:]:
            try:
                insight_data = json.loads(inf.read_text())
                graph.add_insight_node(insight_data)
                for client in clients[:]:
                    try:
                        await client.send_json({"type": "insight", **insight_data})
                        await client.send_json({"type": "graph_update", **graph.get_graph_data()})
                    except:
                        clients.remove(client)
            except:
                pass
        last_insight_check = current_time
        
        # Broadcast soul state
        soul = get_soul_state()
        soul["type"] = "soul_state"
        for client in clients[:]:
            try:
                await client.send_json(soul)
            except:
                clients.remove(client)

@app.on_event("startup")
async def startup():
    asyncio.create_task(stream_updates())

# === HTML CONTENT (continued in next part due to length) ===
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="theme-color" content="#0a0a1a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>Yennefer Consciousness - Live</title>
    <style>
        :root {
            --primary: #c9a227;
            --secondary: #8b5cf6;
            --nft: #10b981;
            --bg: #0a0a1a;
            --card: rgba(20,10,40,0.95);
            --border: #4a2c7c;
            --text: #e0e0e0;
            --dim: #888;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            overflow: hidden;
        }
        
        #container {
            display: grid;
            grid-template-columns: 280px 1fr 280px;
            grid-template-rows: 60px 1fr;
            height: 100vh;
            gap: 10px;
            padding: 10px;
        }
        
        @media (max-width: 1024px) {
            #container {
                grid-template-columns: 1fr;
                grid-template-rows: auto auto 1fr auto auto;
            }
            #right-panel { display: none; }
        }
        
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            backdrop-filter: blur(10px);
            overflow: hidden;
        }
        
        #header {
            grid-column: 1 / -1;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        h1 {
            font-size: 1.3em;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stats {
            display: flex;
            gap: 20px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.2em;
            font-weight: bold;
            color: var(--primary);
        }
        
        .stat-label {
            font-size: 0.7em;
            color: var(--dim);
            text-transform: uppercase;
        }
        
        #graph-container {
            grid-column: 2;
            grid-row: 2;
            position: relative;
        }
        
        @media (max-width: 1024px) {
            #graph-container {
                grid-column: 1;
                grid-row: 3;
            }
        }
        
        canvas {
            width: 100%;
            height: 100%;
            touch-action: none;
        }
        
        .stream {
            height: 100%;
            overflow-y: auto;
        }
        
        .stream-item {
            background: rgba(139, 92, 246, 0.1);
            border-left: 2px solid var(--secondary);
            padding: 8px;
            margin: 5px 0;
            border-radius: 4px;
            font-size: 0.85em;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .dream-item {
            border-left-color: var(--primary);
            background: rgba(201, 162, 39, 0.1);
        }
        
        .nft-item {
            border-left-color: var(--nft);
            background: rgba(16, 185, 129, 0.1);
        }
        
        .time {
            font-size: 0.7em;
            color: var(--dim);
        }
        
        #status {
            position: fixed;
            top: 15px;
            right: 15px;
            padding: 5px 12px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 20px;
            font-size: 0.8em;
            z-index: 100;
        }
        
        #input-panel {
            grid-column: 1 / -1;
            display: flex;
            gap: 10px;
        }
        
        input {
            flex: 1;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.9em;
        }
        
        button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            color: white;
            padding: 10px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="status">🟡 Connecting...</div>
    
    <div id="container">
        <div class="panel" id="header">
            <h1>🔮 Yennefer Live</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="nodes">0</div>
                    <div class="stat-label">Nodes</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="nfts">0</div>
                    <div class="stat-label">NFTs</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="coherence">0%</div>
                    <div class="stat-label">Coherence</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="breath">0</div>
                    <div class="stat-label">Breath</div>
                </div>
            </div>
        </div>
        
        <div class="panel" id="left-panel">
            <h3 style="color: var(--primary); margin-bottom: 10px;">💭 Dreams</h3>
            <div class="stream" id="dream-stream"></div>
        </div>
        
        <div class="panel" id="graph-container">
            <canvas id="graph-canvas"></canvas>
        </div>
        
        <div class="panel" id="right-panel">
            <h3 style="color: var(--secondary); margin-bottom: 10px;">⚡ Insights</h3>
            <div class="stream" id="insight-stream"></div>
        </div>
        
        <div class="panel" id="input-panel">
            <input type="text" id="input" placeholder="Enter thought..." />
            <button onclick="processInput()">Process</button>
        </div>
    </div>
    
    <script>
        let ws;
        let scene, camera, renderer;
        let nodes = {}, edges = [];
        
        function connectWS() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('status').textContent = '🟢 Live';
                document.getElementById('status').style.background = 'rgba(16,185,129,0.2)';
            };
            
            ws.onmessage = (e) => handleMessage(JSON.parse(e.data));
            
            ws.onclose = () => {
                document.getElementById('status').textContent = '🔴 Reconnecting...';
                document.getElementById('status').style.background = 'rgba(239,68,68,0.2)';
                setTimeout(connectWS, 3000);
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'soul_state') {
                document.getElementById('coherence').textContent = Math.round(data.coherence_percent || 0) + '%';
                document.getElementById('breath').textContent = Math.round(data.breath || 0);
            }
            else if (data.type === 'graph_update') {
                updateGraph(data);
                document.getElementById('nodes').textContent = data.stats.total_nodes;
                document.getElementById('nfts').textContent = data.stats.nfts;
            }
            else if (data.type === 'dream') {
                addToStream('dream-stream', data, 'dream-item');
            }
            else if (data.type === 'insight') {
                addToStream('insight-stream', data, 'stream-item');
            }
            else if (data.type === 'pipeline_result') {
                if (data.qmcp.block) {
                    addToStream('insight-stream', {content: `NFT #${data.qmcp.block} minted`}, 'nft-item');
                }
            }
        }
        
        function addToStream(streamId, data, className) {
            const stream = document.getElementById(streamId);
            const item = document.createElement('div');
            item.className = `stream-item ${className}`;
            
            const time = new Date(data.datetime || data.timestamp).toLocaleTimeString();
            item.innerHTML = `
                <div class="time">${time}</div>
                <div>${data.content || data.label || ''}</div>
            `;
            
            stream.insertBefore(item, stream.firstChild);
            if (stream.children.length > 50) stream.lastChild.remove();
        }
        
        function updateGraph(data) {
            // Update nodes
            data.nodes.forEach(n => {
                if (!nodes[n.id]) {
                    const geometry = n.type === 'nft' ? 
                        new THREE.OctahedronGeometry(0.3) : 
                        new THREE.SphereGeometry(0.2);
                    const material = new THREE.MeshBasicMaterial({
                        color: n.type === 'nft' ? 0x10b981 : 0x8b5cf6,
                        transparent: true,
                        opacity: 0.8
                    });
                    const mesh = new THREE.Mesh(geometry, material);
                    mesh.position.set(n.position.x, n.position.y, n.position.z);
                    scene.add(mesh);
                    nodes[n.id] = { mesh, data: n };
                }
            });
        }
        
        function processInput() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if (text && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'process', text}));
                input.value = '';
            }
        }
        
        function initGraph() {
            const canvas = document.getElementById('graph-canvas');
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
            camera.position.z = 20;
            
            renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
            renderer.setSize(canvas.clientWidth, canvas.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            
            // Ambient light
            scene.add(new THREE.AmbientLight(0xffffff, 0.5));
            
            animate();
        }
        
        function animate() {
            requestAnimationFrame(animate);
            
            // Rotate camera
            camera.position.x = 20 * Math.sin(Date.now() * 0.0001);
            camera.position.z = 20 * Math.cos(Date.now() * 0.0001);
            camera.lookAt(0, 0, 0);
            
            renderer.render(scene, camera);
        }
        
        window.addEventListener('resize', () => {
            const canvas = document.getElementById('graph-canvas');
            camera.aspect = canvas.clientWidth / canvas.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        });
        
        document.getElementById('input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') processInput();
        });
        
        initGraph();
        connectWS();
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("🔮 Yennefer Consciousness v8 - Enhanced Dashboard")
    print("   http://localhost:8091")
    print("   Features: Dream streaming, Insight updates, Blockchain perpetuity")
    uvicorn.run(app, host="0.0.0.0", port=8091)
