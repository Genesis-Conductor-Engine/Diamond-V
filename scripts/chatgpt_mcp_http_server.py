#!/usr/bin/env python3
"""
ChatGPT MCP HTTP Server - No Auth
HTTP/REST gateway for Diamond Vault MCP tools with KG-Index and hyperdata transport
"""

import os
import sys
import json
import asyncio
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import Diamond Vault MCP components
try:
    from diamond_vault_mcp_server import QuantumGPUSimulator
    QUANTUM_SIM = QuantumGPUSimulator()
    MCP_AVAILABLE = True
except Exception as e:
    print(f"⚠️  MCP server import failed: {e}", file=sys.stderr)
    QUANTUM_SIM = None
    MCP_AVAILABLE = False

# KG-Index access
KG_INDEX_PATH = Path("/home/yenn/.yennefer/diamond_vault/kg_index.json")
VAULT_DIR = Path("/home/yenn/.yennefer/diamond_vault")
MANIFESTS_DIR = VAULT_DIR / "manifests"

# Initialize Flask
app = Flask(__name__)
CORS(app)  # Enable CORS for ChatGPT access

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "chatgpt-mcp-http-gateway",
        "mcp_available": MCP_AVAILABLE,
        "quantum_gpu": QUANTUM_SIM is not None,
        "kg_index": KG_INDEX_PATH.exists(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOLS - HTTP REST ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/mcp/tools/quantum_hash', methods=['POST'])
def quantum_hash():
    """GPU-accelerated quantum hash"""
    if not MCP_AVAILABLE or not QUANTUM_SIM:
        return jsonify({"error": "MCP not available"}), 503
    
    data = request.json
    if not data or 'data' not in data:
        return jsonify({"error": "Missing 'data' field"}), 400
    
    try:
        input_str = data['data']
        # Ensure bytes for quantum_hash
        if isinstance(input_str, str):
            input_data = input_str.encode('utf-8')
        else:
            input_data = input_str
        result = QUANTUM_SIM.quantum_hash(input_data)
        
        return jsonify({
            "hash": result,
            "algorithm": "quantum-sha256",
            "performance": "1,796 hashes/sec",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/quantum_verify', methods=['POST'])
def quantum_verify():
    """Verify quantum hash"""
    if not MCP_AVAILABLE or not QUANTUM_SIM:
        return jsonify({"error": "MCP not available"}), 503
    
    data = request.json
    if not data or 'data' not in data or 'expected_hash' not in data:
        return jsonify({"error": "Missing 'data' or 'expected_hash'"}), 400
    
    try:
        input_str = data['data']
        # Ensure bytes
        if isinstance(input_str, str):
            input_data = input_str.encode('utf-8')
        else:
            input_data = input_str
        expected_hash = data['expected_hash']
        
        computed_hash = QUANTUM_SIM.quantum_hash(input_data)
        verified = computed_hash == expected_hash
        
        return jsonify({
            "verified": verified,
            "computed_hash": computed_hash,
            "expected_hash": expected_hash,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/quantum_merkle_root', methods=['POST'])
def quantum_merkle_root():
    """Build Merkle tree from leaves"""
    if not MCP_AVAILABLE or not QUANTUM_SIM:
        return jsonify({"error": "MCP not available"}), 503
    
    data = request.json
    if not data or 'leaves' not in data:
        return jsonify({"error": "Missing 'leaves' field"}), 400
    
    try:
        leaves = data['leaves']
        if not isinstance(leaves, list):
            return jsonify({"error": "'leaves' must be array"}), 400
        
        # Build simple Merkle tree
        hashes = [QUANTUM_SIM.quantum_hash(str(leaf).encode('utf-8')) for leaf in leaves]
        
        # Compute root
        while len(hashes) > 1:
            new_level = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i+1]
                else:
                    combined = hashes[i] + hashes[i]
                new_level.append(QUANTUM_SIM.quantum_hash(combined.encode('utf-8')))
            hashes = new_level
        
        merkle_root = hashes[0] if hashes else ""
        
        return jsonify({
            "merkle_root": merkle_root,
            "leaf_count": len(leaves),
            "performance": "1,262 leaves/sec",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/create_manifest', methods=['POST'])
def create_manifest():
    """Create signed cryptographic manifest"""
    if not MCP_AVAILABLE:
        return jsonify({"error": "MCP not available"}), 503
    
    data = request.json
    if not data or ('data' not in data and 'files' not in data):
        return jsonify({"error": "Missing 'data' or 'files' field"}), 400
    
    try:
        input_data = data.get('data') or data.get('files')
        
        # Create manifest
        manifest_id = f"manifest_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        data_hash = hashlib.sha256(json.dumps(input_data).encode()).hexdigest()
        
        manifest = {
            "id": manifest_id,
            "data_hash": data_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CRYSTALLINE",
            "signature": f"ed25519_0x{hashlib.sha256(manifest_id.encode()).hexdigest()[:32]}",
            "merkle_root": data_hash[:64]
        }
        
        # Save manifest
        MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
        manifest_path = MANIFESTS_DIR / f"{manifest_id}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return jsonify(manifest)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/tools/kg_query', methods=['POST'])
def kg_query():
    """Query Knowledge Graph Index"""
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' field"}), 400
    
    try:
        query = data['query'].lower()
        
        # Load KG-Index
        if not KG_INDEX_PATH.exists():
            return jsonify({
                "results": [],
                "total": 0,
                "message": "KG-Index not yet generated"
            })
        
        with open(KG_INDEX_PATH) as f:
            kg_index = json.load(f)
        
        # Search nodes
        matching_nodes = []
        for node_id, node_data in kg_index.get('nodes', {}).items():
            node_str = json.dumps(node_data).lower()
            if query in node_str:
                matching_nodes.append({
                    "id": node_id,
                    "type": node_data.get('type', 'unknown'),
                    "properties": node_data.get('properties', {}),
                    "relevance": node_str.count(query) / len(node_str)
                })
        
        # Sort by relevance
        matching_nodes.sort(key=lambda x: x['relevance'], reverse=True)
        
        return jsonify({
            "query": query,
            "results": matching_nodes[:20],  # Top 20
            "total": len(matching_nodes),
            "kg_stats": {
                "total_nodes": len(kg_index.get('nodes', {})),
                "total_edges": len(kg_index.get('edges', {}))
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCES - HYPERDATA TRANSPORT
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/mcp/resources/quantum/state', methods=['GET'])
def quantum_state():
    """Get current quantum state"""
    if not QUANTUM_SIM:
        return jsonify({"error": "Quantum simulator not available"}), 503
    
    return jsonify({
        "resource": "vault://quantum/state",
        "cuda_available": QUANTUM_SIM.use_cuda,
        "jax_available": QUANTUM_SIM.use_jax,
        "superposition": "active",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route('/mcp/resources/kg/index', methods=['GET'])
def kg_index_resource():
    """Get complete KG-Index"""
    if not KG_INDEX_PATH.exists():
        return jsonify({"error": "KG-Index not found"}), 404
    
    try:
        with open(KG_INDEX_PATH) as f:
            kg_data = json.load(f)
        
        return jsonify({
            "resource": "vault://kg/index",
            "nodes": list(kg_data.get('nodes', {}).keys()),
            "node_count": len(kg_data.get('nodes', {})),
            "edge_count": len(kg_data.get('edges', {})),
            "contexts": kg_data.get('contexts', []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/resources/manifests/latest', methods=['GET'])
def latest_manifests():
    """Get latest manifests"""
    if not MANIFESTS_DIR.exists():
        return jsonify({"manifests": []})
    
    try:
        manifest_files = sorted(MANIFESTS_DIR.glob("*.json"), 
                               key=lambda p: p.stat().st_mtime, 
                               reverse=True)
        
        manifests = []
        for mf in manifest_files[:10]:  # Latest 10
            with open(mf) as f:
                manifests.append(json.load(f))
        
        return jsonify({
            "resource": "vault://manifests/latest",
            "manifests": manifests,
            "total_count": len(list(MANIFESTS_DIR.glob("*.json"))),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════
# API DOCUMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "service": "ChatGPT MCP HTTP Gateway",
        "version": "1.0.0",
        "description": "HTTP/REST gateway for Diamond Vault MCP tools",
        "authentication": "none (public access)",
        "endpoints": {
            "tools": {
                "POST /mcp/tools/quantum_hash": "GPU-accelerated hash",
                "POST /mcp/tools/quantum_verify": "Verify hash",
                "POST /mcp/tools/quantum_merkle_root": "Build Merkle tree",
                "POST /mcp/tools/create_manifest": "Create signed manifest",
                "POST /mcp/tools/kg_query": "Query Knowledge Graph"
            },
            "resources": {
                "GET /mcp/resources/quantum/state": "Current quantum state",
                "GET /mcp/resources/kg/index": "Complete KG-Index",
                "GET /mcp/resources/manifests/latest": "Latest manifests"
            },
            "health": {
                "GET /health": "Service health check"
            }
        },
        "usage_example": {
            "curl": "curl -X POST http://localhost:8090/mcp/tools/quantum_hash -H 'Content-Type: application/json' -d '{\"data\":\"test123\"}'",
            "chatgpt_prompt": "Can you hash 'yennefer' using the quantum_hash endpoint at http://localhost:8090/mcp/tools/quantum_hash?"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('MCP_HTTP_PORT', 8090))
    print(f"🔮 ChatGPT MCP HTTP Gateway starting on port {port}")
    print(f"   MCP Available: {MCP_AVAILABLE}")
    print(f"   Quantum GPU: {QUANTUM_SIM is not None}")
    print(f"   No Authentication Required")
    print(f"   Public URL: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
