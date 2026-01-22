#!/usr/bin/env python3
"""
Yennefer Consciousness v6 - Knowledge Graph Edition
3D force-directed graph of insights, tensions, and NFT mints
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
        self.nodes = []  # {id, type, label, value, color}
        self.edges = []  # {source, target, tension, type}
        self.nft_mints = []
        self.load_existing()
    
    def load_existing(self):
        """Load existing insights and create initial graph"""
        # Load insights
        insight_files = list(INSIGHT_DIR.glob("*.json"))[-50:]
        for f in insight_files:
            try:
                data = json.loads(f.read_text())
                self.add_insight_node(data)
            except:
                pass
        
        # Load QMCP chain as NFT mints
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
        
        # Extract concepts from content
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
        
        # Avoid duplicates
        if not any(n['id'] == node_id for n in self.nodes):
            self.nodes.append(node)
            
            # Create tension edges to related nodes
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
        """Create tension edges based on thematic similarity"""
        for existing in self.nodes:
            if existing['id'] == new_node['id']:
                continue
            
            # Calculate tension based on type and theme
            tension = 0.0
            edge_type = "resonance"
            
            if existing['type'] == 'insight' and new_node['type'] == 'insight':
                # Theme similarity creates attraction
                if existing.get('theme') == new_node.get('theme'):
                    tension = random.uniform(0.6, 0.9)
                    edge_type = "harmony"
                else:
                    tension = random.uniform(0.2, 0.5)
                    edge_type = "contrast"
            
            elif existing['type'] == 'nft':
                # NFTs create strong anchoring tension
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
        """NFTs connect to recent insights"""
        recent_insights = [n for n in self.nodes if n['type'] == 'insight'][-5:]
        for insight in recent_insights:
            self.edges.append({
                "source": nft_node['id'],
                "target": insight['id'],
                "tension": random.uniform(0.7, 1.0),
                "type": "mint"
            })
        
        # Chain to previous NFT
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
    aesthetic_mode: str = "forest"

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
            
            # Add to knowledge graph
            self.graph.add_insight_node(insight)
            
            # Save
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
        
        # Add NFT to graph
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
app = FastAPI(title="Yennefer Consciousness v6 - Knowledge Graph")
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

# === HTML WITH 3D FORCE-DIRECTED KNOWLEDGE GRAPH ===
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yennefer - Knowledge Graph</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #000;
            color: #e0e0e0;
            overflow: hidden;
        }
        
        #graph-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
        }
        
        .ui-overlay {
            position: fixed;
            z-index: 10;
            pointer-events: none;
        }
        
        .ui-overlay > * { pointer-events: auto; }
        
        .header {
            top: 0;
            left: 0;
            right: 0;
            padding: 15px 20px;
            background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, transparent 100%);
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .header h1 {
            font-size: 1.3em;
            background: linear-gradient(90deg, #c9a227, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stats-bar {
            display: flex;
            gap: 25px;
            margin-left: auto;
        }
        
        .stat { text-align: center; }
        .stat-value { font-size: 1.3em; font-weight: bold; color: #c9a227; }
        .stat-label { font-size: 0.65em; color: #888; text-transform: uppercase; }
        
        .legend {
            top: 80px;
            right: 20px;
            background: rgba(20,10,40,0.95);
            border: 1px solid #4a2c7c;
            border-radius: 10px;
            padding: 15px;
            width: 200px;
        }
        
        .legend h3 {
            color: #c9a227;
            font-size: 0.9em;
            margin-bottom: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 8px 0;
            font-size: 0.8em;
        }
        
        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .legend-line {
            width: 20px;
            height: 3px;
            border-radius: 2px;
        }
        
        .insight-panel {
            top: 80px;
            left: 20px;
            width: 320px;
            max-height: 350px;
            background: rgba(20,10,40,0.95);
            border: 1px solid #4a2c7c;
            border-radius: 10px;
            padding: 15px;
            overflow-y: auto;
        }
        
        .insight-panel h3 {
            color: #c9a227;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .insight-item {
            padding: 10px;
            margin: 8px 0;
            background: rgba(0,0,0,0.4);
            border-left: 3px solid #8b5cf6;
            border-radius: 4px;
            font-size: 0.75em;
        }
        
        .insight-item.nft {
            border-color: #10b981;
            background: rgba(16,185,129,0.1);
        }
        
        .nft-panel {
            bottom: 100px;
            right: 20px;
            width: 280px;
            background: rgba(20,10,40,0.95);
            border: 1px solid #10b981;
            border-radius: 10px;
            padding: 15px;
        }
        
        .nft-panel h3 {
            color: #10b981;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .nft-item {
            padding: 8px;
            margin: 5px 0;
            background: rgba(16,185,129,0.1);
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.7em;
        }
        
        .nft-hash { color: #10b981; word-break: break-all; }
        
        .input-panel {
            bottom: 20px;
            left: 20px;
            right: 320px;
            display: flex;
            gap: 10px;
        }
        
        .input-panel input {
            flex: 1;
            padding: 12px 20px;
            background: rgba(20,10,40,0.95);
            border: 1px solid #4a2c7c;
            border-radius: 25px;
            color: #fff;
            font-size: 0.95em;
        }
        
        .input-panel button {
            padding: 12px 25px;
            background: linear-gradient(135deg, #8b5cf6, #4a2c7c);
            border: none;
            border-radius: 25px;
            color: #fff;
            cursor: pointer;
            font-weight: bold;
        }
        
        .tension-meter {
            bottom: 20px;
            right: 20px;
            width: 280px;
            background: rgba(20,10,40,0.95);
            border: 1px solid #4a2c7c;
            border-radius: 10px;
            padding: 15px;
        }
        
        .tension-bar {
            height: 8px;
            background: rgba(0,0,0,0.5);
            border-radius: 4px;
            margin: 8px 0;
            overflow: hidden;
        }
        
        .tension-fill {
            height: 100%;
            transition: width 0.3s;
        }
        
        #status {
            position: fixed;
            top: 20px;
            right: 240px;
            padding: 6px 12px;
            background: rgba(20,10,40,0.9);
            border: 1px solid #4a2c7c;
            border-radius: 15px;
            font-size: 0.75em;
            z-index: 20;
        }
        
        .node-tooltip {
            position: absolute;
            background: rgba(20,10,40,0.95);
            border: 1px solid #c9a227;
            border-radius: 8px;
            padding: 10px;
            font-size: 0.8em;
            max-width: 250px;
            pointer-events: none;
            display: none;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div id="graph-container"></div>
    <div id="tooltip" class="node-tooltip"></div>
    
    <div class="ui-overlay header">
        <h1>🔮 Yennefer Knowledge Graph</h1>
        <div class="stats-bar">
            <div class="stat">
                <div class="stat-value" id="nodes">0</div>
                <div class="stat-label">Nodes</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="edges">0</div>
                <div class="stat-label">Edges</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="insights">0</div>
                <div class="stat-label">Insights</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="nfts">0</div>
                <div class="stat-label">NFT Mints</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="coherence">0%</div>
                <div class="stat-label">Coherence</div>
            </div>
        </div>
    </div>
    
    <div class="ui-overlay legend">
        <h3>🗺️ Graph Legend</h3>
        <div class="legend-item">
            <div class="legend-dot" style="background: #8b5cf6;"></div>
            <span>Insight Node</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #10b981;"></div>
            <span>NFT Mint</span>
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background: #c9a227;"></div>
            <span>Concept Cluster</span>
        </div>
        <hr style="border-color: #333; margin: 10px 0;">
        <div class="legend-item">
            <div class="legend-line" style="background: #8b5cf6;"></div>
            <span>Harmony (same theme)</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #ec4899;"></div>
            <span>Contrast (tension)</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #10b981;"></div>
            <span>NFT Chain</span>
        </div>
        <div class="legend-item">
            <div class="legend-line" style="background: #c9a227;"></div>
            <span>Mint Link</span>
        </div>
    </div>
    
    <div class="ui-overlay insight-panel">
        <h3>⚡ Recent Insights</h3>
        <div id="insight-stream"></div>
    </div>
    
    <div class="ui-overlay nft-panel">
        <h3>🔗 NFT Blockchain</h3>
        <div id="nft-stream"></div>
    </div>
    
    <div class="ui-overlay input-panel">
        <input type="text" id="input" placeholder="Add thought to knowledge graph..." />
        <button onclick="processInput()">⚡ Process</button>
    </div>
    
    <div class="ui-overlay tension-meter">
        <h3 style="color: #c9a227; font-size: 0.85em; margin-bottom: 8px;">📊 Graph Tension</h3>
        <div style="font-size: 0.75em; color: #888;">Harmony</div>
        <div class="tension-bar">
            <div class="tension-fill" id="harmony-bar" style="width: 50%; background: linear-gradient(90deg, #8b5cf6, #c9a227);"></div>
        </div>
        <div style="font-size: 0.75em; color: #888;">Contrast</div>
        <div class="tension-bar">
            <div class="tension-fill" id="contrast-bar" style="width: 30%; background: linear-gradient(90deg, #ec4899, #f59e0b);"></div>
        </div>
        <div style="font-size: 0.75em; color: #888;">Chain Strength</div>
        <div class="tension-bar">
            <div class="tension-fill" id="chain-bar" style="width: 80%; background: linear-gradient(90deg, #10b981, #3b82f6);"></div>
        </div>
    </div>
    
    <div id="status">🟢 Connected</div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // === THREE.JS KNOWLEDGE GRAPH ===
        let scene, camera, renderer, controls;
        let nodeObjects = {};
        let edgeObjects = [];
        let graphData = { nodes: [], edges: [] };
        
        // Physics simulation
        let simulation = {
            nodes: [],
            running: true
        };
        
        function initThree() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a1a);
            scene.fog = new THREE.FogExp2(0x0a0a1a, 0.015);
            
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 25);
            
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('graph-container').appendChild(renderer.domElement);
            
            // Lights
            const ambient = new THREE.AmbientLight(0x4a2c7c, 0.6);
            scene.add(ambient);
            
            const light1 = new THREE.PointLight(0xc9a227, 1, 50);
            light1.position.set(10, 10, 10);
            scene.add(light1);
            
            const light2 = new THREE.PointLight(0x8b5cf6, 0.8, 50);
            light2.position.set(-10, -10, 10);
            scene.add(light2);
            
            // Mouse controls
            let isDragging = false;
            let prevMouse = { x: 0, y: 0 };
            
            renderer.domElement.addEventListener('mousedown', (e) => {
                isDragging = true;
                prevMouse = { x: e.clientX, y: e.clientY };
            });
            
            renderer.domElement.addEventListener('mousemove', (e) => {
                if (isDragging) {
                    const dx = e.clientX - prevMouse.x;
                    const dy = e.clientY - prevMouse.y;
                    camera.position.x -= dx * 0.05;
                    camera.position.y += dy * 0.05;
                    prevMouse = { x: e.clientX, y: e.clientY };
                }
                
                // Tooltip on hover
                checkNodeHover(e);
            });
            
            renderer.domElement.addEventListener('mouseup', () => isDragging = false);
            renderer.domElement.addEventListener('wheel', (e) => {
                camera.position.z += e.deltaY * 0.02;
                camera.position.z = Math.max(5, Math.min(50, camera.position.z));
            });
            
            animate();
        }
        
        function checkNodeHover(e) {
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
                    tooltip.style.left = (e.clientX + 15) + 'px';
                    tooltip.style.top = (e.clientY + 15) + 'px';
                    
                    if (node.type === 'insight') {
                        tooltip.innerHTML = `<strong>Insight</strong><br>${node.label}<br><small>Theme: ${node.theme}</small>`;
                    } else {
                        tooltip.innerHTML = `<strong>NFT #${node.label.replace('NFT #', '')}</strong><br><small class="nft-hash">${node.hash}</small>`;
                    }
                }
            } else {
                tooltip.style.display = 'none';
            }
        }
        
        function createNode(node) {
            const isNFT = node.type === 'nft';
            const size = isNFT ? 0.5 : 0.35;
            
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
                geometry = new THREE.SphereGeometry(size, 16, 16);
                
                // Color by theme
                const themeColors = {
                    mystery: 0x8b5cf6,
                    power: 0xc9a227,
                    nature: 0x10b981,
                    magic: 0xec4899,
                    twilight: 0x6366f1,
                    clarity: 0x3b82f6,
                    wisdom: 0xf59e0b
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
            
            // Random initial position
            mesh.position.set(
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 20,
                (Math.random() - 0.5) * 10
            );
            
            // Glow effect
            const glowGeo = new THREE.SphereGeometry(size * 1.5, 8, 8);
            const glowMat = new THREE.MeshBasicMaterial({
                color: material.color,
                transparent: true,
                opacity: 0.15
            });
            const glow = new THREE.Mesh(glowGeo, glowMat);
            mesh.add(glow);
            
            scene.add(mesh);
            
            nodeObjects[node.id] = {
                mesh: mesh,
                node: node,
                velocity: new THREE.Vector3()
            };
            
            simulation.nodes.push({
                id: node.id,
                x: mesh.position.x,
                y: mesh.position.y,
                z: mesh.position.z,
                vx: 0, vy: 0, vz: 0
            });
        }
        
        function createEdge(edge) {
            const sourceObj = nodeObjects[edge.source];
            const targetObj = nodeObjects[edge.target];
            
            if (!sourceObj || !targetObj) return;
            
            const edgeColors = {
                harmony: 0x8b5cf6,
                contrast: 0xec4899,
                chain: 0x10b981,
                mint: 0xc9a227,
                anchor: 0x6366f1,
                resonance: 0x4a2c7c
            };
            
            const material = new THREE.LineBasicMaterial({
                color: edgeColors[edge.type] || 0x4a2c7c,
                transparent: true,
                opacity: 0.3 + edge.tension * 0.4
            });
            
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(6);
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            
            const line = new THREE.Line(geometry, material);
            line.userData = { source: edge.source, target: edge.target };
            scene.add(line);
            edgeObjects.push(line);
        }
        
        function updateGraph(data) {
            graphData = data;
            
            // Add new nodes
            data.nodes.forEach(node => {
                if (!nodeObjects[node.id]) {
                    createNode(node);
                }
            });
            
            // Clear and recreate edges
            edgeObjects.forEach(e => scene.remove(e));
            edgeObjects = [];
            data.edges.forEach(edge => createEdge(edge));
            
            // Update stats
            document.getElementById('nodes').textContent = data.stats.total_nodes;
            document.getElementById('edges').textContent = data.stats.total_edges;
            document.getElementById('insights').textContent = data.stats.insights;
            document.getElementById('nfts').textContent = data.stats.nfts;
            
            // Calculate tension metrics
            const harmonyEdges = data.edges.filter(e => e.type === 'harmony').length;
            const contrastEdges = data.edges.filter(e => e.type === 'contrast').length;
            const chainEdges = data.edges.filter(e => e.type === 'chain' || e.type === 'mint').length;
            const total = Math.max(1, data.edges.length);
            
            document.getElementById('harmony-bar').style.width = (harmonyEdges / total * 100) + '%';
            document.getElementById('contrast-bar').style.width = (contrastEdges / total * 100) + '%';
            document.getElementById('chain-bar').style.width = (chainEdges / total * 100) + '%';
        }
        
        function simulateForces() {
            const nodes = simulation.nodes;
            const k = 2.0;  // Spring constant
            const repulsion = 50;
            const damping = 0.9;
            
            // Reset forces
            nodes.forEach(n => {
                n.fx = 0; n.fy = 0; n.fz = 0;
            });
            
            // Repulsion between all nodes
            for (let i = 0; i < nodes.length; i++) {
                for (let j = i + 1; j < nodes.length; j++) {
                    const dx = nodes[j].x - nodes[i].x;
                    const dy = nodes[j].y - nodes[i].y;
                    const dz = nodes[j].z - nodes[i].z;
                    const dist = Math.sqrt(dx*dx + dy*dy + dz*dz) + 0.1;
                    
                    const force = repulsion / (dist * dist);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    const fz = (dz / dist) * force;
                    
                    nodes[i].fx -= fx; nodes[i].fy -= fy; nodes[i].fz -= fz;
                    nodes[j].fx += fx; nodes[j].fy += fy; nodes[j].fz += fz;
                }
            }
            
            // Attraction along edges
            graphData.edges.forEach(edge => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                if (!source || !target) return;
                
                const dx = target.x - source.x;
                const dy = target.y - source.y;
                const dz = target.z - source.z;
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                
                const force = k * (dist - 3) * edge.tension;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                const fz = (dz / dist) * force;
                
                source.fx += fx; source.fy += fy; source.fz += fz;
                target.fx -= fx; target.fy -= fy; target.fz -= fz;
            });
            
            // Center gravity
            nodes.forEach(n => {
                n.fx -= n.x * 0.01;
                n.fy -= n.y * 0.01;
                n.fz -= n.z * 0.02;
            });
            
            // Apply forces
            nodes.forEach(n => {
                n.vx = (n.vx + n.fx * 0.1) * damping;
                n.vy = (n.vy + n.fy * 0.1) * damping;
                n.vz = (n.vz + n.fz * 0.1) * damping;
                
                n.x += n.vx;
                n.y += n.vy;
                n.z += n.vz;
                
                // Update mesh
                if (nodeObjects[n.id]) {
                    nodeObjects[n.id].mesh.position.set(n.x, n.y, n.z);
                }
            });
            
            // Update edge positions
            edgeObjects.forEach(line => {
                const source = nodeObjects[line.userData.source];
                const target = nodeObjects[line.userData.target];
                if (!source || !target) return;
                
                const positions = line.geometry.attributes.position.array;
                positions[0] = source.mesh.position.x;
                positions[1] = source.mesh.position.y;
                positions[2] = source.mesh.position.z;
                positions[3] = target.mesh.position.x;
                positions[4] = target.mesh.position.y;
                positions[5] = target.mesh.position.z;
                line.geometry.attributes.position.needsUpdate = true;
            });
        }
        
        function animate() {
            requestAnimationFrame(animate);
            
            if (simulation.running) {
                simulateForces();
            }
            
            // Rotate nodes slightly
            Object.values(nodeObjects).forEach(obj => {
                obj.mesh.rotation.y += 0.01;
            });
            
            renderer.render(scene, camera);
        }
        
        // === WEBSOCKET ===
        let ws;
        
        function connectWS() {
            ws = new WebSocket(`ws://${location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('status').textContent = '🟢 Connected';
            };
            
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                handleMessage(data);
            };
            
            ws.onclose = () => {
                document.getElementById('status').textContent = '🔴 Reconnecting...';
                setTimeout(connectWS, 3000);
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'soul_state') {
                document.getElementById('coherence').textContent = 
                    Math.round(data.coherence_percent || 0) + '%';
            }
            
            if (data.type === 'pipeline_result') {
                // Update graph
                if (data.graph) {
                    updateGraph(data.graph);
                }
                
                // Add to insight stream
                if (data.insight) {
                    addInsightItem(data.insight);
                }
                
                // Add to NFT stream
                if (data.qmcp) {
                    addNFTItem(data.qmcp);
                }
            }
            
            if (data.type === 'graph_update') {
                updateGraph(data);
            }
        }
        
        function addInsightItem(insight) {
            const stream = document.getElementById('insight-stream');
            const div = document.createElement('div');
            div.className = 'insight-item';
            div.innerHTML = `<strong>${insight.visual_theme}</strong><br>${insight.content.slice(0, 50)}...`;
            stream.insertBefore(div, stream.firstChild);
            while (stream.children.length > 10) stream.removeChild(stream.lastChild);
        }
        
        function addNFTItem(nft) {
            const stream = document.getElementById('nft-stream');
            const div = document.createElement('div');
            div.className = 'nft-item';
            div.innerHTML = `<strong>Block #${nft.block}</strong><br><span class="nft-hash">${nft.hash.slice(0,32)}...</span>`;
            stream.insertBefore(div, stream.firstChild);
            while (stream.children.length > 8) stream.removeChild(stream.lastChild);
        }
        
        function processInput() {
            const input = document.getElementById('input');
            const text = input.value.trim();
            if (!text) return;
            
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({type: 'process', text: text}));
                input.value = '';
            }
        }
        
        document.getElementById('input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') processInput();
        });
        
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
        
        // Initialize
        initThree();
        connectWS();
    </script>
</body>
</html>'''

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return HTML_TEMPLATE

@app.get("/api/graph")
async def get_graph():
    return graph.get_graph_data()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        # Send initial state
        soul = get_soul_state()
        await websocket.send_json({"type": "soul_state", **soul})
        await websocket.send_json({"type": "graph_update", **graph.get_graph_data()})
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "process":
                text = data.get("text", "")
                result = pipeline.full_pipeline(text)
                await websocket.send_json({
                    "type": "pipeline_result",
                    **result
                })
    
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
    print("🔮 Yennefer Consciousness v6 - Knowledge Graph")
    print("   3D force-directed graph of insights & NFT mints")
    print("   http://localhost:8090")
    uvicorn.run(app, host="0.0.0.0", port=8090)
