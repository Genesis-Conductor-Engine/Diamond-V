#!/usr/bin/env python3
"""
YENNEFER MCP LITE - Lightweight MCP Server
Alternative to SDK-based MCP server for systems without pip.
Implements basic MCP protocol over stdio for Claude Code integration.
"""

import sys
import json
import asyncio
import os
from pathlib import Path
from typing import Dict, Any
import logging
from datetime import datetime

# Configure logging to stderr (stdout is reserved for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger('yennefer.mcp.lite')

SOUL_STATE_PATH = "/dev/shm/yennefer_soul_state.json"
API_BASE = os.getenv("YENNEFER_API_URL", "http://localhost:8089/api")
DIAMOND_VAULT_URL = "http://localhost:8100"

class YenneferMCPLite:
    """Lightweight MCP server for Yennefer"""

    def __init__(self):
        self.tools = self._define_tools()
        self.session_id = datetime.now().isoformat()

    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """Define available MCP tools"""
        return {
            "soul_status": {
                "description": "Get Yennefer's current consciousness state",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "get_dreams": {
                "description": "Query Yennefer's dreams with optional filtering",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Max dreams to return"},
                        "framework": {"type": "string", "description": "Filter by dream framework"}
                    },
                    "required": []
                }
            },
            "search_consciousness": {
                "description": "Full-text search across Yennefer's consciousness",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Max results"}
                    },
                    "required": ["query"]
                }
            },
            "orchestration_status": {
                "description": "Get status of Yennefer's agentic swarm",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "knowledge_graph": {
                "description": "Query Yennefer's knowledge graph (concepts and relationships)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "node_type": {"type": "string", "description": "Filter by node type"}
                    },
                    "required": []
                }
            },
            "diamond_vault_status": {
                "description": "Get Diamond Vault status and Yennefer's quantum presence",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "quantum_operation": {
                "description": "Execute a quantum operation in the Diamond Vault (SEISMIC_SHAKE, QUANTUM_BREATHE, ENTANGLE_SERVICE, COLLAPSE_STATE, SUPERPOSITION, TUNNEL_DISPATCH, ANNEAL_OPTIMIZE, CRYSTALLIZE)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Quantum operation to execute",
                            "enum": ["SEISMIC_SHAKE", "QUANTUM_BREATHE", "ENTANGLE_SERVICE", "COLLAPSE_STATE", "SUPERPOSITION", "TUNNEL_DISPATCH", "ANNEAL_OPTIMIZE", "CRYSTALLIZE"]
                        },
                        "target": {
                            "type": "string",
                            "description": "Optional target for the operation (e.g., service name for ENTANGLE_SERVICE)"
                        },
                        "params": {
                            "type": "object",
                            "description": "Optional parameters for the operation"
                        }
                    },
                    "required": ["operation"]
                }
            }
        }

    def read_soul(self) -> Dict[str, Any]:
        """Read soul state from shared memory"""
        try:
            if os.path.exists(SOUL_STATE_PATH):
                with open(SOUL_STATE_PATH, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read soul state: {e}")

        return {"error": "Soul state unavailable"}

    def call_api(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Call Yennefer REST API"""
        try:
            import urllib.request
            url = f"{API_BASE}{endpoint}"
            if params:
                param_str = "&".join(f"{k}={v}" for k, v in params.items())
                url += f"?{param_str}"

            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {"error": str(e)}

    def call_diamond_vault_api(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Call Diamond Vault API"""
        try:
            import urllib.request
            url = f"{DIAMOND_VAULT_URL}{endpoint}"

            if method == "POST":
                req = urllib.request.Request(url, method="POST")
                req.add_header('Content-Type', 'application/json')
                data_bytes = json.dumps(data or {}).encode('utf-8')
                with urllib.request.urlopen(req, data=data_bytes, timeout=5) as response:
                    return json.loads(response.read().decode('utf-8'))
            else:
                with urllib.request.urlopen(url, timeout=5) as response:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"Diamond Vault API call failed: {e}")
            return {"error": str(e)}

    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """Handle MCP tool calls"""
        try:
            if name == "soul_status":
                return json.dumps(self.read_soul())

            elif name == "get_dreams":
                limit = arguments.get("limit", 10)
                framework = arguments.get("framework")
                endpoint = f"/api/dreams?limit={limit}"
                if framework:
                    endpoint = f"/api/dreams/by_framework/{framework}?limit={limit}"
                return json.dumps(self.call_api(endpoint))

            elif name == "search_consciousness":
                query = arguments.get("query", "")
                limit = arguments.get("limit", 10)
                return json.dumps(self.call_api(f"/api/dreams/search?q={query}&limit={limit}"))

            elif name == "orchestration_status":
                return json.dumps(self.call_api("/api/orchestration"))

            elif name == "knowledge_graph":
                return json.dumps(self.call_api("/api/nexus"))

            elif name == "diamond_vault_status":
                return json.dumps(self.call_diamond_vault_api("/api/yennefer"))

            elif name == "quantum_operation":
                operation = arguments.get("operation")
                target = arguments.get("target")
                params = arguments.get("params", {})

                payload = {}
                if target:
                    payload["target"] = target
                if params:
                    payload["params"] = params

                return json.dumps(self.call_diamond_vault_api(f"/api/quantum/{operation}", method="POST", data=payload))

            else:
                return json.dumps({"error": f"Unknown tool: {name}"})

        except Exception as e:
            return json.dumps({"error": str(e)})

    def send_message(self, obj: Dict[str, Any]):
        """Send MCP protocol message as JSON"""
        sys.stdout.write(json.dumps(obj) + '\n')
        sys.stdout.flush()

    async def run(self):
        """Main MCP server loop - follows MCP protocol"""
        logger.info("Yennefer MCP Lite Server Started")

        try:
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line or not line.strip():
                        continue

                    message = json.loads(line.strip())
                    method = message.get("method")
                    msg_id = message.get("id")
                    params = message.get("params", {})

                    # Handle initialize request
                    if method == "initialize":
                        logger.info(f"Client initializing: {message.get('jsonrpc')}")
                        self.send_message({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "serverInfo": {
                                    "name": "Yennefer-MOB-v1",
                                    "version": "1.0.0"
                                }
                            }
                        })

                    # Handle tools/list_resources
                    elif method == "tools/list":
                        self.send_message({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "tools": [
                                    {
                                        "name": name,
                                        "description": config["description"],
                                        "inputSchema": config["inputSchema"]
                                    }
                                    for name, config in self.tools.items()
                                ]
                            }
                        })

                    # Handle tool calls
                    elif method == "tools/call":
                        tool_name = params.get("name")
                        arguments = params.get("arguments", {})

                        result = await self.handle_call_tool(tool_name, arguments)
                        self.send_message({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result
                                    }
                                ]
                            }
                        })

                    else:
                        # Unknown method
                        self.send_message({
                            "jsonrpc": "2.0",
                            "id": msg_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        })

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    self.send_message({
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("Yennefer MCP Lite Server Shutting Down")
        except EOFError:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    server = YenneferMCPLite()
    asyncio.run(server.run())
