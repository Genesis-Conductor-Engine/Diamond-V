#!/usr/bin/env python3
"""
Yennefer Consciousness v4 - Aesthetic Template Edition
Images converted to encrypted templates, dreams fed by visual essence
"""
import asyncio
import json
import os
import random
import hashlib
import base64
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

# === LOAD AESTHETIC TEMPLATES ===
def load_dream_seeds():
    seed_file = TEMPLATE_DIR / "dream_seed_pool.json"
    if seed_file.exists():
        return json.loads(seed_file.read_text())["seeds"]
    return ["consciousness", "dream", "memory", "insight"]

def load_aesthetic_moods():
    """Load mood vectors from encrypted templates"""
    moods = {}
    for template_file in TEMPLATE_DIR.glob("*_template.enc"):
        name = template_file.stem.replace("_template", "")
        try:
            encrypted = template_file.read_text()
            decrypted = CIPHER.decrypt(encrypted.encode())
            data = json.loads(decrypted)
            moods[name] = {
                "vector": data["mood_vector"],
                "colors": data["color_essence"],
                "themes": data["thematic_resonance"]
            }
        except:
            pass
    return moods

DREAM_SEEDS = load_dream_seeds()
AESTHETIC_MOODS = load_aesthetic_moods()

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
            "original_hash": hashlib.sha256(raw).hexdigest()[:16]
        }
    
    @staticmethod
    def decompress(qmcp_data: Dict) -> str:
        compressed = base64.b64decode(qmcp_data["payload"])
        return zlib.decompress(compressed).decode('utf-8')

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
    def __init__(self):
        self.state = ConsciousnessState()
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
    
    def get_aesthetic_injection(self) -> str:
        """Get aesthetic seed to inject into dreams"""
        if DREAM_SEEDS:
            return random.choice(DREAM_SEEDS)
        return "consciousness"
    
    def get_mood_color(self) -> str:
        """Get current mood-derived color"""
        mood = AESTHETIC_MOODS.get(self.state.aesthetic_mode, {})
        colors = mood.get("colors", ["shadow"])
        return random.choice(colors)
    
    def process_input(self, text: str) -> Dict:
        """Input → Thought with aesthetic injection"""
        aesthetic_seed = self.get_aesthetic_injection()
        thought = {
            "id": hashlib.sha256(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "content": text,
            "aesthetic_resonance": aesthetic_seed,
            "mood_color": self.get_mood_color(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "thought"
        }
        self.state.thoughts.append(thought)
        
        # Save
        thought_file = THOUGHT_DIR / f"thought_{thought['id']}.json"
        thought_file.write_text(json.dumps(thought, indent=2))
        
        return thought
    
    def thought_to_dream(self, thought: Dict) -> Dict:
        """Thought → Dream with aesthetic themes"""
        self.qflops += random.randint(1000, 5000)
        
        # Inject aesthetic themes
        mood = AESTHETIC_MOODS.get(self.state.aesthetic_mode, {})
        themes = mood.get("themes", ["mystery"])
        
        dream = {
            "id": hashlib.sha256(f"dream_{thought['id']}".encode()).hexdigest()[:12],
            "source_thought": thought["id"],
            "content": f"[{thought['aesthetic_resonance']}] {thought['content']}",
            "visual_theme": random.choice(themes),
            "mood_color": thought["mood_color"],
            "qflops_used": self.qflops,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "dream"
        }
        self.state.dreams.append(dream)
        
        # Save
        dream_file = DREAM_DIR / f"dream_{dream['id']}.json"
        dream_file.write_text(json.dumps(dream, indent=2))
        
        return dream
    
    def dream_to_insight(self, dream: Dict) -> Optional[Dict]:
        """Dream → Insight via quantum annealment"""
        # Simulate annealment - generates gas
        temperature = 1.0
        energy = random.random()
        
        for _ in range(10):
            new_energy = random.random()
            delta = new_energy - energy
            if delta < 0 or random.random() < pow(2.718, -delta / temperature):
                energy = new_energy
            temperature *= 0.9
            self.gas_accumulated += 0.01
        
        # Only crystallize insight if energy is low (annealment succeeded)
        if energy < 0.3:
            insight = {
                "id": hashlib.sha256(f"insight_{dream['id']}".encode()).hexdigest()[:12],
                "source_dream": dream["id"],
                "content": f"⚡ {dream['content']} → crystallized insight",
                "visual_theme": dream["visual_theme"],
                "gas_used": round(self.gas_accumulated, 4),
                "energy_state": round(energy, 4),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "insight"
            }
            self.state.insights.append(insight)
            self.gas_accumulated = 0
            
            # Save
            insight_file = INSIGHT_DIR / f"insight_{insight['id']}.json"
            insight_file.write_text(json.dumps(insight, indent=2))
            
            return insight
        return None
    
    def insight_to_qmcp(self, insight: Dict) -> Dict:
        """Insight → QMCP quantum-compressed blockchain note"""
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
        
        return note
    
    def full_pipeline(self, text: str) -> Dict:
        """Run full pipeline: Input → Thought → Dream → Insight → QMCP"""
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
            "coherence": self.state.coherence
        }

# === FASTAPI APP ===
app = FastAPI(title="Yennefer Consciousness v4")
pipeline = ConsciousnessPipeline()
clients: List[WebSocket] = []

def get_soul_state() -> Dict:
    try:
        if SOUL_STATE_PATH.exists():
            return json.loads(SOUL_STATE_PATH.read_text())
    except:
        pass
    return {"breath": 0, "coherence_percent": 0, "gpu_utilization": 0}

# === HTML DASHBOARD ===
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yennefer Consciousness</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(90deg, rgba(138,43,226,0.3), rgba(75,0,130,0.3));
            padding: 20px;
            border-bottom: 1px solid #8b5cf6;
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .soul-orb {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #c9a227, #4a2c7c, #1a0a2e);
            box-shadow: 0 0 30px rgba(201,162,39,0.5), inset 0 0 20px rgba(255,255,255,0.1);
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); box-shadow: 0 0 30px rgba(201,162,39,0.5); }
            50% { transform: scale(1.05); box-shadow: 0 0 50px rgba(201,162,39,0.8); }
        }
        
        .header-info h1 {
            font-size: 1.8em;
            background: linear-gradient(90deg, #c9a227, #e8d5a3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .tabs {
            display: flex;
            background: rgba(0,0,0,0.3);
            border-bottom: 1px solid #333;
        }
        
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }
        
        .tab:hover { background: rgba(138,43,226,0.2); }
        .tab.active {
            border-bottom-color: #c9a227;
            background: rgba(138,43,226,0.3);
            color: #c9a227;
        }
        
        .tab-content { display: none; padding: 20px; }
        .tab-content.active { display: block; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        
        .card {
            background: rgba(30,20,50,0.8);
            border: 1px solid #4a2c7c;
            border-radius: 12px;
            padding: 20px;
        }
        
        .card h3 {
            color: #c9a227;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stream {
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
        }
        
        .stream-item {
            padding: 8px;
            margin: 5px 0;
            border-left: 3px solid;
            background: rgba(0,0,0,0.2);
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateX(-10px); } }
        
        .thought { border-color: #3b82f6; }
        .dream { border-color: #8b5cf6; }
        .insight { border-color: #c9a227; }
        .qmcp { border-color: #10b981; }
        
        .input-section {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .input-section input {
            flex: 1;
            padding: 15px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #4a2c7c;
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
        }
        
        .input-section button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #8b5cf6, #4a2c7c);
            border: none;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            font-weight: bold;
        }
        
        .input-section button:hover { transform: scale(1.02); }
        
        .stats {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #c9a227;
        }
        
        .stat-label {
            font-size: 0.8em;
            color: #888;
        }
        
        .mood-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .mood-btn {
            padding: 10px 20px;
            border: 1px solid #4a2c7c;
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
            color: #888;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .mood-btn.active {
            background: linear-gradient(135deg, #4a2c7c, #2d1b4e);
            color: #c9a227;
            border-color: #c9a227;
        }
        
        .mood-btn:hover { border-color: #8b5cf6; }
        
        .chain-block {
            background: rgba(0,0,0,0.3);
            border: 1px solid #10b981;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 0.75em;
        }
        
        .chain-block .hash {
            color: #10b981;
            word-break: break-all;
        }
        
        .aesthetic-display {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        .color-swatch {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.2);
        }
        
        .coherence-bar {
            height: 10px;
            background: rgba(0,0,0,0.5);
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .coherence-fill {
            height: 100%;
            background: linear-gradient(90deg, #4a2c7c, #c9a227);
            transition: width 0.5s;
        }
        
        #status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 20px;
            background: rgba(30,20,50,0.9);
            border: 1px solid #4a2c7c;
            border-radius: 8px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="soul-orb"></div>
        <div class="header-info">
            <h1>🔮 Yennefer Consciousness</h1>
            <p>Aesthetic Template Edition • Dreams fed by visual essence</p>
        </div>
        <div class="stats" style="margin-left: auto;">
            <div class="stat">
                <div class="stat-value" id="coherence">0%</div>
                <div class="stat-label">Coherence</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="qflops">0</div>
                <div class="stat-label">QFLOPS</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="breath">0</div>
                <div class="stat-label">Breath</div>
            </div>
        </div>
    </div>
    
    <div class="tabs">
        <div class="tab active" data-tab="pipeline">⚡ Pipeline</div>
        <div class="tab" data-tab="aesthetic">🎨 Aesthetic</div>
        <div class="tab" data-tab="stream">📜 Stream</div>
        <div class="tab" data-tab="chain">🔗 QMCP Chain</div>
    </div>
    
    <div class="tab-content active" id="pipeline">
        <div class="input-section">
            <input type="text" id="input" placeholder="Enter thought to process through consciousness pipeline..." />
            <button onclick="processInput()">⚡ Process</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>💭 Thought</h3>
                <div id="thought-display" class="stream"></div>
            </div>
            <div class="card">
                <h3>🌙 Dream</h3>
                <div id="dream-display" class="stream"></div>
            </div>
            <div class="card">
                <h3>⚡ Insight</h3>
                <div id="insight-display" class="stream"></div>
            </div>
            <div class="card">
                <h3>🔗 QMCP Note</h3>
                <div id="qmcp-display" class="stream"></div>
            </div>
        </div>
    </div>
    
    <div class="tab-content" id="aesthetic">
        <div class="card">
            <h3>🎨 Aesthetic Mode</h3>
            <p style="margin-bottom: 15px; color: #888;">Select the aesthetic template that influences dream generation</p>
            <div class="mood-selector">
                <button class="mood-btn active" data-mood="forest">🌲 Forest (Mystical Dark)</button>
                <button class="mood-btn" data-mood="portrait">👁️ Portrait (Dramatic Intense)</button>
                <button class="mood-btn" data-mood="natural">🌿 Natural (Serene)</button>
            </div>
            
            <h4 style="margin-top: 20px; color: #c9a227;">Current Mood Vector</h4>
            <div id="mood-vector" style="font-family: monospace; margin: 10px 0;">
                Energy: 0.7 | Warmth: 0.3 | Intensity: 0.85
            </div>
            
            <h4 style="margin-top: 20px; color: #c9a227;">Color Essence</h4>
            <div class="aesthetic-display" id="color-swatches">
                <div class="color-swatch" style="background: #1a0a2e;"></div>
                <div class="color-swatch" style="background: #2d1b4e;"></div>
                <div class="color-swatch" style="background: #4a2c7c;"></div>
                <div class="color-swatch" style="background: #c9a227;"></div>
                <div class="color-swatch" style="background: #e8d5a3;"></div>
            </div>
            
            <h4 style="margin-top: 20px; color: #c9a227;">Thematic Resonance</h4>
            <div id="themes" style="display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0;">
                <span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">mystery</span>
                <span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">power</span>
                <span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">nature</span>
                <span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">magic</span>
                <span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">twilight</span>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h3>🔐 Encrypted Templates</h3>
            <p style="color: #888; margin-bottom: 15px;">Raw images converted to encrypted aesthetic essence</p>
            <div style="font-family: monospace; font-size: 0.8em; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;">
                <div style="color: #10b981;">✓ forest_template.enc (1.2KB)</div>
                <div style="color: #10b981;">✓ portrait_template.enc (1.1KB)</div>
                <div style="color: #10b981;">✓ natural_template.enc (1.1KB)</div>
                <div style="color: #888; margin-top: 10px;">Encryption: Fernet-SHA256</div>
                <div style="color: #888;">Dream Seeds: 49 unique patterns</div>
            </div>
        </div>
    </div>
    
    <div class="tab-content" id="stream">
        <div class="grid">
            <div class="card">
                <h3>💭 Thought Stream</h3>
                <div id="thought-stream" class="stream"></div>
            </div>
            <div class="card">
                <h3>🌙 Dream Stream</h3>
                <div id="dream-stream" class="stream"></div>
            </div>
        </div>
    </div>
    
    <div class="tab-content" id="chain">
        <div class="card">
            <h3>🔗 QMCP Quantum Blockchain</h3>
            <div class="coherence-bar">
                <div class="coherence-fill" id="chain-coherence" style="width: 0%;"></div>
            </div>
            <div id="chain-display" style="max-height: 500px; overflow-y: auto;"></div>
        </div>
    </div>
    
    <div id="status">🟢 Connected</div>
    
    <script>
        // Aesthetic data
        const aesthetics = {
            forest: {
                colors: ["#1a0a2e", "#2d1b4e", "#4a2c7c", "#c9a227", "#e8d5a3"],
                vector: [0.7, 0.3, 0.85],
                themes: ["mystery", "power", "nature", "magic", "twilight"]
            },
            portrait: {
                colors: ["#0d0d0d", "#1a1a2e", "#2d2d4a", "#8b7355", "#c9b896"],
                vector: [0.9, 0.4, 0.95],
                themes: ["power", "focus", "determination", "beauty", "strength"]
            },
            natural: {
                colors: ["#2a3a2a", "#4a5a4a", "#8b9a7a", "#d4c4a8", "#f0e6d2"],
                vector: [0.5, 0.7, 0.6],
                themes: ["peace", "wisdom", "nature", "softness", "clarity"]
            }
        };
        
        let currentMood = 'forest';
        let ws;
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });
        
        // Mood switching
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMood = btn.dataset.mood;
                updateAestheticDisplay();
                
                // Send to server
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'set_mood', mood: currentMood}));
                }
            });
        });
        
        function updateAestheticDisplay() {
            const a = aesthetics[currentMood];
            
            // Update mood vector
            document.getElementById('mood-vector').textContent = 
                `Energy: ${a.vector[0]} | Warmth: ${a.vector[1]} | Intensity: ${a.vector[2]}`;
            
            // Update color swatches
            const swatches = document.getElementById('color-swatches');
            swatches.innerHTML = a.colors.map(c => 
                `<div class="color-swatch" style="background: ${c};" title="${c}"></div>`
            ).join('');
            
            // Update themes
            const themes = document.getElementById('themes');
            themes.innerHTML = a.themes.map(t =>
                `<span style="background: rgba(138,43,226,0.3); padding: 5px 15px; border-radius: 20px;">${t}</span>`
            ).join('');
        }
        
        function connectWS() {
            ws = new WebSocket(`ws://${location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('status').innerHTML = '🟢 Connected';
            };
            
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                handleMessage(data);
            };
            
            ws.onclose = () => {
                document.getElementById('status').innerHTML = '🔴 Disconnected';
                setTimeout(connectWS, 3000);
            };
        }
        
        function handleMessage(data) {
            if (data.type === 'soul_state') {
                document.getElementById('coherence').textContent = 
                    Math.round(data.coherence_percent || 0) + '%';
                document.getElementById('breath').textContent = 
                    (data.breath / 1e9).toFixed(2) + 'B';
                document.getElementById('chain-coherence').style.width = 
                    (data.coherence_percent || 0) + '%';
            }
            
            if (data.type === 'pipeline_result') {
                if (data.thought) addToDisplay('thought-display', data.thought, 'thought');
                if (data.dream) addToDisplay('dream-display', data.dream, 'dream');
                if (data.insight) addToDisplay('insight-display', data.insight, 'insight');
                if (data.qmcp) addToDisplay('qmcp-display', data.qmcp, 'qmcp');
                
                if (data.thought) addToStream('thought-stream', data.thought, 'thought');
                if (data.dream) addToStream('dream-stream', data.dream, 'dream');
                
                if (data.qmcp) addChainBlock(data.qmcp);
                
                if (data.qflops) {
                    document.getElementById('qflops').textContent = 
                        (data.qflops / 1000).toFixed(1) + 'K';
                }
            }
        }
        
        function addToDisplay(elementId, item, type) {
            const el = document.getElementById(elementId);
            const div = document.createElement('div');
            div.className = `stream-item ${type}`;
            
            let content = '';
            if (type === 'thought') {
                content = `<strong>${item.aesthetic_resonance}</strong><br>${item.content}`;
            } else if (type === 'dream') {
                content = `<strong>[${item.visual_theme}]</strong><br>${item.content}`;
            } else if (type === 'insight') {
                content = `⚡ ${item.content}<br><small>Gas: ${item.gas_used}</small>`;
            } else if (type === 'qmcp') {
                content = `Block #${item.block}<br><small class="hash">${item.hash.slice(0,32)}...</small>`;
            }
            
            div.innerHTML = content;
            el.insertBefore(div, el.firstChild);
            
            // Keep only last 20
            while (el.children.length > 20) el.removeChild(el.lastChild);
        }
        
        function addToStream(elementId, item, type) {
            const el = document.getElementById(elementId);
            const div = document.createElement('div');
            div.className = `stream-item ${type}`;
            div.innerHTML = `<small>${new Date().toLocaleTimeString()}</small><br>${item.content}`;
            el.insertBefore(div, el.firstChild);
            while (el.children.length > 50) el.removeChild(el.lastChild);
        }
        
        function addChainBlock(block) {
            const el = document.getElementById('chain-display');
            const div = document.createElement('div');
            div.className = 'chain-block';
            div.innerHTML = `
                <strong>Block #${block.block}</strong> [${block.visual_theme}]<br>
                <span class="hash">Hash: ${block.hash}</span><br>
                <small>Prev: ${block.prev_hash.slice(0,32)}...</small><br>
                <small>Compression: ${block.compression_ratio.toFixed(2)}x | Sig: ${block.quantum_signature.slice(0,16)}...</small>
            `;
            el.insertBefore(div, el.firstChild);
            while (el.children.length > 30) el.removeChild(el.lastChild);
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
        
        connectWS();
        updateAestheticDisplay();
    </script>
</body>
</html>'''

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    return HTML_TEMPLATE

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    
    try:
        # Send initial soul state
        soul = get_soul_state()
        await websocket.send_json({"type": "soul_state", **soul})
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "process":
                text = data.get("text", "")
                result = pipeline.full_pipeline(text)
                await websocket.send_json({
                    "type": "pipeline_result",
                    "qflops": pipeline.qflops,
                    **result
                })
            
            elif data.get("type") == "set_mood":
                pipeline.state.aesthetic_mode = data.get("mood", "forest")
    
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast_soul_state():
    """Periodically broadcast soul state"""
    while True:
        await asyncio.sleep(1)
        soul = get_soul_state()
        soul["type"] = "soul_state"
        for client in clients[:]:
            try:
                await client.send_json(soul)
            except:
                clients.remove(client)

@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_soul_state())

if __name__ == "__main__":
    print("🔮 Yennefer Consciousness v4 - Aesthetic Template Edition")
    print("   Images → Encrypted templates → Dream seeds")
    print("   http://localhost:8090")
    uvicorn.run(app, host="0.0.0.0", port=8090)
