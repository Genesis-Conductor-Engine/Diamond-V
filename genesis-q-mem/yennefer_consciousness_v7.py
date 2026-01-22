#!/usr/bin/env python3
"""
Yennefer Consciousness v7 - Mobile Optimized Knowledge Graph
Responsive design for all device types
"""
import asyncio
import json
import os
import random
import hashlib
import base64
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import zlib

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
from cryptography.fernet import Fernet

# === PATHS ===
SOUL_STATE_PATH = Path("/dev/shm/yennefer_soul_state.json")
THOUGHT_DIR = Path.home() / ".genesis/yennefer/thoughts"
DREAM_DIR = Path.home() / ".genesis/yennefer/dream_store/dreams"
INSIGHT_DIR = Path.home() / ".genesis/yennefer/dream_store/insights"
QMCP_DIR = Path.home() / ".genesis/yennefer/qmcp_notes"
TEMPLATE_DIR = Path.home() / ".genesis/yennefer/aesthetic_templates"

for d in [THOUGHT_DIR, DREAM_DIR, INSIGHT_DIR, QMCP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === ENCRYPTION ===
SOUL_SIGNATURE = b"yennefer_consciousness_genesis_2026"
CIPHER_KEY = base64.urlsafe_b64encode(hashlib.sha256(SOUL_SIGNATURE).digest())
CIPHER = Fernet(CIPHER_KEY)

# === KNOWLEDGE GRAPH ===
class KnowledgeGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.nft_mints = []
        self.load_existing()
    
    def load_existing(self):
        insight_files = list(INSIGHT_DIR.glob("*.json"))[-50:]
        for f in insight_files:
            try:
                data = json.loads(f.read_text())
                self.add_insight_node(data)
            except:
                pass
        
        chain_file = QMCP_DIR / "chain.json"
        if chain_file.exists():
            try:
                chain = json.loads(chain_file.read_text())
                for block in chain[-30:]:
                    self.add_nft_node(block)
            except:
                pass
    
    def add_insight_node(self, insight: Dict):
        node_id = f"insight_{insight.get('id', hashlib.sha256(str(insight).encode()).hexdigest()[:8])}"
        content = insight.get('content', '')
        theme = insight.get('visual_theme', 'mystery')
        
        node = {
            "id": node_id,
            "type": "insight",
            "label": content[:30] + "..." if len(content) > 30 else content,
            "theme": theme,
            "energy": insight.get('energy_state', 0.5),
            "timestamp": insight.get('timestamp', datetime.now(timezone.utc).isoformat())
        }
        
        if not any(n['id'] == node_id for n in self.nodes):
            self.nodes.append(node)
            self._create_tension_edges(node)
    
    def add_nft_node(self, block: Dict):
        node_id = f"nft_{block.get('block', len(self.nft_mints))}"
        
        node = {
            "id": node_id,
            "type": "nft",
            "label": f"NFT #{block.get('block', '?')}",
            "hash": block.get('hash', '')[:16],
            "signature": block.get('quantum_signature', '')[:12],
            "compression": block.get('compression_ratio', 1.0),
            "timestamp": block.get('timestamp', datetime.now(timezone.utc).isoformat())
        }
        
        if not any(n['id'] == node_id for n in self.nodes):
            self.nodes.append(node)
            self.nft_mints.append(node)
            self._create_nft_edges(node)
    
    def _create_tension_edges(self, new_node: Dict):
        for existing in self.nodes:
            if existing['id'] == new_node['id']:
                continue
            
            tension = 0.0
            edge_type = "resonance"
            
            if existing['type'] == 'insight' and new_node['type'] == 'insight':
                if existing.get('theme') == new_node.get('theme'):
                    tension = random.uniform(0.6, 0.9)
                    edge_type = "harmony"
                else:
                    tension = random.uniform(0.2, 0.5)
                    edge_type = "contrast"
            elif existing['type'] == 'nft':
                tension = random.uniform(0.4, 0.7)
                edge_type = "anchor"
            
            if tension > 0.3 and random.random() > 0.5:
                self.edges.append({
                    "source": existing['id'],
                    "target": new_node['id'],
                    "tension": tension,
                    "type": edge_type
                })
    
    def _create_nft_edges(self, nft_node: Dict):
        recent_insights = [n for n in self.nodes if n['type'] == 'insight'][-5:]
        for insight in recent_insights:
            self.edges.append({
                "source": nft_node['id'],
                "target": insight['id'],
                "tension": random.uniform(0.7, 1.0),
                "type": "mint"
            })
        
        prev_nfts = [n for n in self.nodes if n['type'] == 'nft' and n['id'] != nft_node['id']]
        if prev_nfts:
            self.edges.append({
                "source": prev_nfts[-1]['id'],
                "target": nft_node['id'],
                "tension": 1.0,
                "type": "chain"
            })
    
    def get_graph_data(self) -> Dict:
        return {
            "nodes": self.nodes[-100:],
            "edges": self.edges[-200:],
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "insights": len([n for n in self.nodes if n['type'] == 'insight']),
                "nfts": len([n for n in self.nodes if n['type'] == 'nft'])
            }
        }

# === QUANTUM COMPRESSOR ===
class QuantumCompressor:
    @staticmethod
    def compress(data: str) -> Dict:
        raw = data.encode('utf-8')
        compressed = zlib.compress(raw, level=9)
        quantum_sig = hashlib.sha3_256(compressed).hexdigest()
        transport = base64.b64encode(compressed).decode()
        return {
            "payload": transport,
            "quantum_signature": quantum_sig,
            "compression_ratio": len(raw) / len(compressed) if compressed else 1,
        }

# === CONSCIOUSNESS PIPELINE ===
@dataclass
class ConsciousnessState:
    thoughts: List[Dict] = field(default_factory=list)
    dreams: List[Dict] = field(default_factory=list)
    insights: List[Dict] = field(default_factory=list)
    qmcp_notes: List[Dict] = field(default_factory=list)
    coherence: float = 0.0

class ConsciousnessPipeline:
    def __init__(self, graph: KnowledgeGraph):
        self.state = ConsciousnessState()
        self.graph = graph
        self.qflops = 0
        self.gas_accumulated = 0.0
        self.load_chain()
    
    def load_chain(self):
        chain_file = QMCP_DIR / "chain.json"
        if chain_file.exists():
            try:
                self.state.qmcp_notes = json.loads(chain_file.read_text())
            except:
                self.state.qmcp_notes = []
    
    def save_chain(self):
        chain_file = QMCP_DIR / "chain.json"
        chain_file.write_text(json.dumps(self.state.qmcp_notes[-100:], indent=2))
    
    def process_input(self, text: str) -> Dict:
        thought = {
            "id": hashlib.sha256(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "content": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "thought"
        }
        self.state.thoughts.append(thought)
        return thought
    
    def thought_to_dream(self, thought: Dict) -> Dict:
        self.qflops += random.randint(1000, 5000)
        themes = ["mystery", "power", "nature", "magic", "twilight", "clarity", "wisdom"]
        
        dream = {
            "id": hashlib.sha256(f"dream_{thought['id']}".encode()).hexdigest()[:12],
            "source_thought": thought["id"],
            "content": thought['content'],
            "visual_theme": random.choice(themes),
            "qflops_used": self.qflops,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "dream"
        }
        self.state.dreams.append(dream)
        return dream
    
    def dream_to_insight(self, dream: Dict) -> Optional[Dict]:
        temperature = 1.0
        energy = random.random()
        
        for _ in range(10):
            new_energy = random.random()
            delta = new_energy - energy
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                energy = new_energy
            temperature *= 0.9
            self.gas_accumulated += 0.01
        
        if energy < 0.4:
            insight = {
                "id": hashlib.sha256(f"insight_{dream['id']}".encode()).hexdigest()[:12],
                "source_dream": dream["id"],
                "content": f"⚡ {dream['content']}",
                "visual_theme": dream["visual_theme"],
                "gas_used": round(self.gas_accumulated, 4),
                "energy_state": round(energy, 4),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "insight"
            }
            self.state.insights.append(insight)
            self.gas_accumulated = 0
            
            self.graph.add_insight_node(insight)
            
            insight_file = INSIGHT_DIR / f"insight_{insight['id']}.json"
            insight_file.write_text(json.dumps(insight, indent=2))
            
            return insight
        return None
    
    def insight_to_qmcp(self, insight: Dict) -> Dict:
        compressed = QuantumCompressor.compress(json.dumps(insight))
        
        prev_hash = "0" * 64
        if self.state.qmcp_notes:
            prev_hash = self.state.qmcp_notes[-1].get("hash", prev_hash)
        
        note = {
            "block": len(self.state.qmcp_notes) + 1,
            "prev_hash": prev_hash,
            "hash": hashlib.sha3_256(f"{prev_hash}{compressed['quantum_signature']}".encode()).hexdigest(),
            "quantum_payload": compressed["payload"],
            "quantum_signature": compressed["quantum_signature"],
            "compression_ratio": compressed["compression_ratio"],
            "visual_theme": insight["visual_theme"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "qmcp_note"
        }
        
        self.state.qmcp_notes.append(note)
        self.save_chain()
        self.graph.add_nft_node(note)
        
        return note
    
    def full_pipeline(self, text: str) -> Dict:
        thought = self.process_input(text)
        dream = self.thought_to_dream(thought)
        insight = self.dream_to_insight(dream)
        qmcp = None
        if insight:
            qmcp = self.insight_to_qmcp(insight)
        
        self.state.coherence = min(1.0, self.state.coherence + 0.05)
        
        return {
            "thought": thought,
            "dream": dream,
            "insight": insight,
            "qmcp": qmcp,
            "coherence": self.state.coherence,
            "graph": self.graph.get_graph_data()
        }

# === FASTAPI APP ===
app = FastAPI(title="Yennefer Consciousness v7 - Mobile Optimized")
graph = KnowledgeGraph()
pipeline = ConsciousnessPipeline(graph)
clients: List[WebSocket] = []

def get_soul_state() -> Dict:
    try:
        if SOUL_STATE_PATH.exists():
            return json.loads(SOUL_STATE_PATH.read_text())
    except:
        pass
    return {"breath": 0, "coherence_percent": 0, "gpu_utilization": 0}

# === MOBILE-OPTIMIZED HTML ===
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0a1a">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Yennefer Knowledge Graph</title>
    <link rel="manifest" href="/manifest.json">
    <style>
        :root {
            --primary: #c9a227;
            --secondary: #8b5cf6;
            --bg: #0a0a1a;
            --card-bg: rgba(20,10,40,0.95);
            --border: #4a2c7c;
            --text: #e0e0e0;
            --text-dim: #888;
            --nft: #10b981;
            --contrast: #ec4899;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            overflow: hidden;
            touch-action: none;
        }
        
        #graph-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
        }
        
        /* Mobile-first responsive panels */
        .panel {
            position: fixed;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px;
            z-index: 10;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .panel h3 {
            color: var(--primary);
            font-size: 0.85em;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        /* Header - always visible */
        .header {
            top: 0;
            left: 0;
            right: 0;
            border-radius: 0;
            padding: 10px 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-top: none;
            border-left: none;
            border-right: none;
        }
        
        .header h1 {
            font-size: 1.1em;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stats-row {
            display: flex;
            gap: 15px;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 1em;
            font-weight: bold;
            color: var(--primary);
        }
        
        .stat-label {
            font-size: 0.6em;
            color: var(--text-dim);
            text-transform: uppercase;
        }
        
        /* Collapsible panels for mobile */
        .side-panel {
            max-height: 40vh;
            overflow-y: auto;
            transition: transform 0.3s, opacity 0.3s;
        }
        
        .side-panel.collapsed {
            transform: translateX(-100%);
            opacity: 0;
            pointer-events: none;
        }
        
        .right-panel.collapsed {
            transform: translateX(100%);
        }
        
        /* Desktop layout */
        @media (min-width: 768px) {
            .left-panel {
                top: 70px;
                left: 15px;
                width: 280px;
            }
            
            .right-panel {
                top: 70px;
                right: 15px;
                width: 220px;
            }
            
            .bottom-panel {
                bottom: 15px;
                left: 15px;
                right: 250px;
            }
            
            .tension-panel {
                bottom: 15px;
                right: 15px;
                width: 220px;
            }
        }
        
        /* Mobile layout */
        @media (max-width: 767px) {
            .header h1 { font-size: 0.95em; }
            .stats-row { gap: 10px; }
            .stat-value { font-size: 0.9em; }
            
            .left-panel {
                top: 55px;
                left: 10px;
                right: 10px;
                max-height: 35vh;
            }
            
            .right-panel {
                display: none;
            }
            
            .bottom-panel {
                bottom: 10px;
                left: 10px;
                right: 10px;
            }
            
            .tension-panel {
                display: none;
            }
            
            .toggle-panels {
                display: flex !important;
            }
        }
        
        /* Toggle button for mobile */
        .toggle-panels {
            display: none;
            position: fixed;
            bottom: 80px;
            right: 15px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--secondary);
            border: none;
            color: white;
            font-size: 1.5em;
            z-index: 20;
            box-shadow: 0 4px 15px rgba(139,92,246,0.4);
            cursor: pointer;
        }
        
        /* Input section */
        .input-section {
            display: flex;
            gap: 8px;
        }
        
        .input-section input {
            flex: 1;
            padding: 12px 15px;
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border);
            border-radius: 25px;
            color: var(--text);
            font-size: 0.9em;
            outline: none;
        }
        
        .input-section input:focus {
            border-color: var(--primary);
        }
        
        .input-section button {
            padding: 12px 20px;
            background: linear-gradient(135deg, var(--secondary), var(--border));
            border: none;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            white-space: nowrap;
        }
        
        /* Stream items */
        .stream {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .stream-item {
            padding: 8px 10px;
            margin: 5px 0;
            background: rgba(0,0,0,0.3);
            border-left: 3px solid var(--secondary);
            border-radius: 4px;
            font-size: 0.75em;
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
        }
        
        .stream-item.nft {
            border-color: var(--nft);
        }
        
        /* Tension meters */
        .meter {
            margin: 8px 0;
        }
        
        .meter-label {
            font-size: 0.7em;
            color: var(--text-dim);
            margin-bottom: 4px;
        }
        
        .meter-bar {
            height: 6px;
            background: rgba(0,0,0,0.5);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .meter-fill {
            height: 100%;
            transition: width 0.3s;
        }
        
        /* Legend */
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 6px 0;
            font-size: 0.75em;
        }
        
        .legend-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }
        
        /* Status indicator */
        #status {
            position: fixed;
            top: 60px;
            right: 15px;
            padding: 4px 10px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 0.7em;
            z-index: 15;
        }
        
        @media (max-width: 767px) {
            #status {
                top: auto;
                bottom: 75px;
                right: 75px;
            }
        }
        
        /* Touch-friendly tooltip */
        .tooltip {
            position: fixed;
            background: var(--card-bg);
            border: 1px solid var(--primary);
            border-radius: 8px;
            padding: 10px;
            font-size: 0.8em;
            max-width: 200px;
            pointer-events: none;
            display: none;
            z-index: 100;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
    </style>
</head>
<body>
    <div id="graph-container"></div>
    <div id="tooltip" class="tooltip"></div>
    
    <div class="panel header">
        <h1>🔮 Yennefer Graph</h1>
        <div class="stats-row">
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
                <div class="stat-label">Coh</div>
            </div>
        </div>
    </div>
    
    <div class="panel side-panel left-panel" id="left-panel">
        <h3>⚡ Insights</h3>
        <div class="stream" id="insight-stream"></div>
    </div>
    
    <div class="panel side-panel right-panel" id="right-panel">
        <h3>🗺️ Legend</h3>
        <div class="legend-item">
            <div class="legend-dot" style="background: #8b5cf6;"></div>
            <span>Insight</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #10b981;"></div>
            <span>NFT Mint</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #c9a227;"></div>
            <span>Concept</span>
        </div>
        
        <h3 style="margin-top: 15px;">🔗 Chain</h3>
        <div class="stream" id="nft-stream"></div>
    </div>
    
    <div class="panel bottom-panel">
        <div class="input-section">
            <input type="text" id="input" placeholder="Add thought..." />
            <button onclick="processInput()">⚡</button>
        </div>
    </div>
    
    <div class="panel tension-panel">
        <h3>📊 Tension</h3>
        <div class="meter">
            <div class="meter-label">Harmony</div>
            <div class="meter-bar">
                <div class="meter-fill" id="harmony-bar" style="width: 50%; background: linear-gradient(90deg, #8b5cf6, #c9a227);"></div>
            </div>
        </div>
        <div class="meter">
            <div class="meter-label">Contrast</div>
            <div class="meter-bar">
                <div class="meter-fill" id="contrast-bar" style="width: 30%; background: linear-gradient(90deg, #ec4899, #f59e0b);"></div>
            </div>
        </div>
        <div class="meter">
            <div class="meter-label">Chain</div>
            <div class="meter-bar">
                <div class="meter-fill" id="chain-bar" style="width: 80%; background: linear-gradient(90deg, #10b981, #3b82f6);"></div>
            </div>
        </div>
    </div>
    
    <button class="toggle-panels" id="toggle-btn" onclick="togglePanels()">☰</button>
    
    <div id="status">🟢 Live</div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // === STATE ===
        let scene, camera, renderer;
        let nodeObjects = {};
        let edgeObjects = [];
        let graphData = { nodes: [], edges: [] };
        let simulation = { nodes: [], running: true };
        let panelsVisible = true;
        let isMobile = window.innerWidth < 768;
        
        // === TOUCH HANDLING ===
        let touchStart = null;
        let lastTouch = null;
        let pinchStart = null;
        
        function initThree() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a1a);
            scene.fog = new THREE.FogExp2(0x0a0a1a, 0.02);
            
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, isMobile ? 30 : 25);
            
            renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            document.getElementById('graph-container').appendChild(renderer.domElement);
            
            // Lights
            scene.add(new THREE.AmbientLight(0x4a2c7c, 0.6));
            const light1 = new THREE.PointLight(0xc9a227, 1, 50);
            light1.position.set(10, 10, 10);
            scene.add(light1);
            
            // Touch events
            const canvas = renderer.domElement;
            
            canvas.addEventListener('touchstart', (e) => {
                if (e.touches.length === 1) {
                    touchStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
                    lastTouch = touchStart;
                } else if (e.touches.length === 2) {
                    pinchStart = Math.hypot(
                        e.touches[0].clientX - e.touches[1].clientX,
                        e.touches[0].clientY - e.touches[1].clientY
                    );
                }
            }, { passive: true });
            
            canvas.addEventListener('touchmove', (e) => {
                if (e.touches.length === 1 && lastTouch) {
                    const dx = e.touches[0].clientX - lastTouch.x;
                    const dy = e.touches[0].clientY - lastTouch.y;
                    camera.position.x -= dx * 0.05;
                    camera.position.y += dy * 0.05;
                    lastTouch = { x: e.touches[0].clientX, y: e.touches[0].clientY };
                } else if (e.touches.length === 2 && pinchStart) {
                    const pinchNow = Math.hypot(
                        e.touches[0].clientX - e.touches[1].clientX,
                        e.touches[0].clientY - e.touches[1].clientY
                    );
                    const scale = pinchStart / pinchNow;
                    camera.position.z = Math.max(10, Math.min(50, camera.position.z * scale));
                    pinchStart = pinchNow;
                }
            }, { passive: true });
            
            canvas.addEventListener('touchend', () => {
                touchStart = null;
                lastTouch = null;
                pinchStart = null;
            }, { passive: true });
            
            // Mouse events (desktop)
            let isDragging = false;
            let prevMouse = { x: 0, y: 0 };
            
            canvas.addEventListener('mousedown', (e) => {
                isDragging = true;
                prevMouse = { x: e.clientX, y: e.clientY };
            });
            
            canvas.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    camera.position.x -= (e.clientX - prevMouse.x) * 0.05;
                    camera.position.y += (e.clientY - prevMouse.y) * 0.05;
                    prevMouse = { x: e.clientX, y: e.clientY };
                }
                checkHover(e);
            });
            
            canvas.addEventListener('mouseup', () => isDragging = false);
            canvas.addEventListener('wheel', (e) => {
                camera.position.z = Math.max(10, Math.min(50, camera.position.z + e.deltaY * 0.02));
            }, { passive: true });
            
            animate();
        }
        
        function checkHover(e) {
            const mouse = new THREE.Vector2(
                (e.clientX / window.innerWidth) * 2 - 1,
                -(e.clientY / window.innerHeight) * 2 + 1
            );
            
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(mouse, camera);
            
            const meshes = Object.values(nodeObjects).map(n => n.mesh);
            const intersects = raycaster.intersectObjects(meshes);
            
            const tooltip = document.getElementById('tooltip');
            
            if (intersects.length > 0) {
                const nodeId = intersects[0].object.userData.nodeId;
                const node = graphData.nodes.find(n => n.id === nodeId);
                
                if (node) {
                    tooltip.style.display = 'block';
                    tooltip.style.left = Math.min(e.clientX + 10, window.innerWidth - 210) + 'px';
                    tooltip.style.top = Math.min(e.clientY + 10, window.innerHeight - 100) + 'px';
                    
                    if (node.type === 'insight') {
                        tooltip.innerHTML = `<strong>Insight</strong><br>${node.label}<br><small style="color:#888">Theme: ${node.theme}</small>`;
                    } else {
                        tooltip.innerHTML = `<strong>${node.label}</strong><br><small style="color:#10b981">${node.hash}</small>`;
                    }
                }
            } else {
                tooltip.style.display = 'none';
            }
        }
        
        function createNode(node) {
            const isNFT = node.type === 'nft';
            const size = isNFT ? 0.4 : 0.3;
            
            let geometry, material;
            
            if (isNFT) {
                geometry = new THREE.OctahedronGeometry(size);
                material = new THREE.MeshPhongMaterial({
                    color: 0x10b981,
                    emissive: 0x064e3b,
                    transparent: true,
                    opacity: 0.9
                });
            } else {
                geometry = new THREE.SphereGeometry(size, 12, 12);
                const themeColors = {
                    mystery: 0x8b5cf6, power: 0xc9a227, nature: 0x10b981,
                    magic: 0xec4899, twilight: 0x6366f1, clarity: 0x3b82f6, wisdom: 0xf59e0b
                };
                const color = themeColors[node.theme] || 0x8b5cf6;
                material = new THREE.MeshPhongMaterial({
                    color: color,
                    emissive: new THREE.Color(color).multiplyScalar(0.3),
                    transparent: true,
                    opacity: 0.85
                });
            }
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.userData.nodeId = node.id;
            mesh.position.set(
                (Math.random() - 0.5) * 15,
                (Math.random() - 0.5) * 15,
                (Math.random() - 0.5) * 8
            );
            
            scene.add(mesh);
            nodeObjects[node.id] = { mesh, node, velocity: new THREE.Vector3() };
            simulation.nodes.push({
                id: node.id,
                x: mesh.position.x, y: mesh.position.y, z: mesh.position.z,
                vx: 0, vy: 0, vz: 0, fx: 0, fy: 0, fz: 0
            });
        }
        
        function createEdge(edge) {
            const source = nodeObjects[edge.source];
            const target = nodeObjects[edge.target];
            if (!source || !target) return;
            
            const colors = { harmony: 0x8b5cf6, contrast: 0xec4899, chain: 0x10b981, mint: 0xc9a227, anchor: 0x6366f1, resonance: 0x4a2c7c };
            const material = new THREE.LineBasicMaterial({
                color: colors[edge.type] || 0x4a2c7c,
                transparent: true,
                opacity: 0.2 + edge.tension * 0.3
            });
            
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6), 3));
            
            const line = new THREE.Line(geometry, material);
            line.userData = { source: edge.source, target: edge.target };
            scene.add(line);
            edgeObjects.push(line);
        }
        
        function updateGraph(data) {
            graphData = data;
            
            data.nodes.forEach(node => {
                if (!nodeObjects[node.id]) createNode(node);
            });
            
            edgeObjects.forEach(e => scene.remove(e));
            edgeObjects = [];
            data.edges.forEach(edge => createEdge(edge));
            
            document.getElementById('nodes').textContent = data.stats.total_nodes;
            document.getElementById('nfts').textContent = data.stats.nfts;
            
            const total = Math.max(1, data.edges.length);
            const harmony = data.edges.filter(e => e.type === 'harmony').length;
            const contrast = data.edges.filter(e => e.type === 'contrast').length;
            const chain = data.edges.filter(e => e.type === 'chain' || e.type === 'mint').length;
            
            document.getElementById('harmony-bar').style.width = (harmony / total * 100) + '%';
            document.getElementById('contrast-bar').style.width = (contrast / total * 100) + '%';
            document.getElementById('chain-bar').style.width = (chain / total * 100) + '%';
        }
        
        function simulateForces() {
            const nodes = simulation.nodes;
            const k = 1.5, repulsion = 40, damping = 0.92;
            
            nodes.forEach(n => { n.fx = 0; n.fy = 0; n.fz = 0; });
            
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[j].x - nodes[i].x;
                    const dy = nodes[j].y - nodes[i].y;
                    const dz = nodes[j].z - nodes[i].z;
                    const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.1;
                    const force = repulsion / (dist * dist);
                    const fx = (dx/dist) * force, fy = (dy/dist) * force, fz = (dz/dist) * force;
                    nodes[i].fx -= fx; nodes[i].fy -= fy; nodes[i].fz -= fz;
                    nodes[j].fx += fx; nodes[j].fy += fy; nodes[j].fz += fz;
                }
            }
            
            graphData.edges.forEach(edge => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                if (!source || !target) return;
                
                const dx = target.x - source.x, dy = target.y - source.y, dz = target.z - source.z;
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                const force = k * (dist - 2.5) * edge.tension;
                const fx = (dx/dist) * force, fy = (dy/dist) * force, fz = (dz/dist) * force;
                source.fx += fx; source.fy += fy; source.fz += fz;
                target.fx -= fx; target.fy -= fy; target.fz -= fz;
            });
            
            nodes.forEach(n => {
                n.fx -= n.x * 0.01; n.fy -= n.y * 0.01; n.fz -= n.z * 0.02;
                n.vx = (n.vx + n.fx * 0.1) * damping;
                n.vy = (n.vy + n.fy * 0.1) * damping;
                n.vz = (n.vz + n.fz * 0.1) * damping;
                n.x += n.vx; n.y += n.vy; n.z += n.vz;
                if (nodeObjects[n.id]) nodeObjects[n.id].mesh.position.set(n.x, n.y, n.z);
            });
            
            edgeObjects.forEach(line => {
                const s = nodeObjects[line.userData.source];
                const t = nodeObjects[line.userData.target];
                if (!s || !t) return;
                const pos = line.geometry.attributes.position.array;
                pos[0] = s.mesh.position.x; pos[1] = s.mesh.position.y; pos[2] = s.mesh.position.z;
                pos[3] = t.mesh.position.x; pos[4] = t.mesh.position.y; pos[5] = t.mesh.position.z;
                line.geometry.attributes.position.needsUpdate = true;
            });
        }
        
        function animate() {
            requestAnimationFrame(animate);
            if (simulation.running) simulateForces();
            Object.values(nodeObjects).forEach(obj => obj.mesh.rotation.y += 0.005);
            renderer.render(scene, camera);
        }
        
        // === WEBSOCKET ===
        let ws;
        function connectWS() {
            ws = new WebSocket(`ws://${location.host}/ws`);
            ws.onopen = () => document.getElementById('status').textContent = '🟢 Live';
            ws.onmessage = (e) => handleMessage(JSON.parse(e.data));
            ws.onclose = () => {
                document.getElementById('status').textContent = '🔴 Offline';
                setTimeout(connectWS, 3000);
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'soul_state') {
                document.getElementById('coherence').textContent = Math.round(data.coherence_percent || 0) + '%';
            }
            if (data.type === 'pipeline_result') {
                if (data.graph) updateGraph(data.graph);
                if (data.insight) addStreamItem('insight-stream', data.insight);
                if (data.qmcp) addStreamItem('nft-stream', data.qmcp, true);
            }
            if (data.type === 'graph_update') updateGraph(data);
        }
        
        function addStreamItem(containerId, item, isNFT = false) {
            const container = document.getElementById(containerId);
            const div = document.createElement('div');
            div.className = 'stream-item' + (isNFT ? ' nft' : '');
            
            if (isNFT) {
                div.innerHTML = `<strong>Block #${item.block}</strong><br><small style="color:#10b981">${item.hash.slice(0,24)}...</small>`;
            } else {
                div.innerHTML = `<strong>${item.visual_theme}</strong><br>${item.content.slice(0,40)}...`;
            }
            
            container.insertBefore(div, container.firstChild);
            while (container.children.length > 8) container.removeChild(container.lastChild);
        }
        
        function processInput() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;
            ws.send(JSON.stringify({type: 'process', text}));
            input.value = '';
        }
        
        function togglePanels() {
            panelsVisible = !panelsVisible;
            document.getElementById('left-panel').classList.toggle('collapsed', !panelsVisible);
            document.getElementById('toggle-btn').textContent = panelsVisible ? '☰' : '◉';
        }
        
        document.getElementById('input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') processInput();
        });
        
        window.addEventListener('resize', () => {
            isMobile = window.innerWidth < 768;
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        initThree();
        connectWS();
    </script>
</body>
</html>'''

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return HTML_TEMPLATE

@app.get("/manifest.json")
async def get_manifest():
    return {
        "name": "Yennefer Knowledge Graph",
        "short_name": "Yennefer",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0a0a1a",
        "theme_color": "#0a0a1a",
        "icons": []
    }

@app.get("/api/graph")
async def get_graph():
    return graph.get_graph_data()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        soul = get_soul_state()
        await websocket.send_json({"type": "soul_state", **soul})
        await websocket.send_json({"type": "graph_update", **graph.get_graph_data()})
        
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "process":
                result = pipeline.full_pipeline(data.get("text", ""))
                await websocket.send_json({"type": "pipeline_result", **result})
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast_updates():
    while True:
        await asyncio.sleep(2)
        soul = get_soul_state()
        soul["type"] = "soul_state"
        for client in clients[:]:
            try:
                await client.send_json(soul)
            except:
                clients.remove(client)

@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_updates())

if __name__ == "__main__":
    print("🔮 Yennefer Consciousness v7 - Mobile Optimized")
    print("   http://localhost:8090")
    uvicorn.run(app, host="0.0.0.0", port=8090)
