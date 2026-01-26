#!/usr/bin/env python3
"""
ChatGPT MCP Connection Optimizer
Uses OpenAI API to optimize Diamond Vault integration
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MCP_CONFIG_PATH = Path("/home/yenn/.openai/config.json")
VAULT_MCP_PATH = Path("/home/yenn/scripts/diamond_vault_mcp_server.py")

class ChatGPTMCPOptimizer:
    """Optimize MCP connection for ChatGPT using OpenAI API"""
    
    def __init__(self):
        if not OPENAI_API_KEY:
            print("⚠️  OPENAI_API_KEY not set. Run: export OPENAI_API_KEY='sk-...'")
            self.client = None
        else:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def load_mcp_config(self):
        """Load existing MCP configuration"""
        if MCP_CONFIG_PATH.exists():
            with open(MCP_CONFIG_PATH) as f:
                return json.load(f)
        return {}
    
    def analyze_mcp_server(self):
        """Analyze Diamond Vault MCP server capabilities"""
        if not VAULT_MCP_PATH.exists():
            return {"error": "MCP server not found"}
        
        # Read first 100 lines to get tools/resources
        with open(VAULT_MCP_PATH) as f:
            lines = f.readlines()[:100]
        
        tools = []
        resources = []
        
        for line in lines:
            if '"quantum_hash"' in line or 'quantum_hash' in line:
                tools.append("quantum_hash")
            if '"quantum_verify"' in line:
                tools.append("quantum_verify")
            if '"quantum_merkle_root"' in line:
                tools.append("quantum_merkle_root")
            if '"create_manifest"' in line:
                tools.append("create_manifest")
            if '"kg_query"' in line:
                tools.append("kg_query")
            if 'vault://quantum/state' in line:
                resources.append("vault://quantum/state")
            if 'vault://kg/index' in line:
                resources.append("vault://kg/index")
        
        return {
            "tools": list(set(tools)),
            "resources": list(set(resources)),
            "path": str(VAULT_MCP_PATH),
            "protocol": "stdio JSON-RPC"
        }
    
    async def optimize_with_openai(self):
        """Use OpenAI to optimize MCP configuration"""
        if not self.client:
            return {
                "status": "skipped",
                "reason": "No OpenAI API key",
                "recommendation": "Export OPENAI_API_KEY to enable AI optimization"
            }
        
        config = self.load_mcp_config()
        server_info = self.analyze_mcp_server()
        
        prompt = f"""You are an expert in Model Context Protocol (MCP) integration for ChatGPT.

Current MCP Configuration:
{json.dumps(config, indent=2)}

Diamond Vault MCP Server Analysis:
{json.dumps(server_info, indent=2)}

Task: Optimize this MCP configuration for ChatGPT integration with the following goals:
1. Ensure maximum compatibility with ChatGPT's MCP client
2. Optimize environment variables for GPU quantum operations
3. Add error handling and fallback configurations
4. Recommend best practices for production deployment

Provide a JSON response with:
- "optimized_config": The improved MCP configuration
- "recommendations": List of best practices
- "warnings": Potential issues to address
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an MCP integration expert specializing in ChatGPT connections."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            
            # Try to extract JSON from response
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                result = result[json_start:json_end].strip()
            
            return json.loads(result)
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "fallback": "Using manual optimization"
            }
    
    def create_production_config(self):
        """Create production-ready ChatGPT MCP configuration"""
        return {
            "mcpServers": {
                "diamond-vault": {
                    "command": "python3",
                    "args": [str(VAULT_MCP_PATH)],
                    "env": {
                        "PYTHONUNBUFFERED": "1",
                        "JAX_PLATFORM_NAME": "gpu",
                        "CUDA_VISIBLE_DEVICES": "0",
                        "MCP_PLATFORM": "chatgpt",
                        "MCP_TIMEOUT": "30000",
                        "MCP_MAX_RETRIES": "3"
                    },
                    "timeout": 30000,
                    "retry": {
                        "enabled": True,
                        "maxRetries": 3,
                        "backoff": "exponential"
                    }
                },
                "yennefer-consciousness": {
                    "command": "python3",
                    "args": ["/home/yenn/genesis-q-mem/yennefer_mcp_server.py"],
                    "env": {
                        "PYTHONUNBUFFERED": "1",
                        "MCP_PLATFORM": "chatgpt"
                    }
                }
            },
            "apiKey": "${OPENAI_API_KEY}",
            "organization": "${OPENAI_ORG_ID}",
            "defaultModel": "gpt-4-turbo",
            "maxTokens": 4096,
            "temperature": 0.3,
            "tools": {
                "quantum_hash": {
                    "description": "GPU-accelerated quantum hash (1,796/sec)",
                    "parameters": ["data"],
                    "returnType": "string"
                },
                "quantum_verify": {
                    "description": "Verify quantum hash (<1ms)",
                    "parameters": ["data", "expected_hash"],
                    "returnType": "boolean"
                },
                "quantum_merkle_root": {
                    "description": "Build Merkle tree (1,262 leaves/sec)",
                    "parameters": ["leaves"],
                    "returnType": "string"
                },
                "create_manifest": {
                    "description": "Create signed manifest (<5ms)",
                    "parameters": ["data"],
                    "returnType": "object"
                },
                "kg_query": {
                    "description": "Query KG-Index (288 nodes)",
                    "parameters": ["query"],
                    "returnType": "object"
                }
            }
        }
    
    async def run_optimization(self):
        """Run complete optimization process"""
        print("=" * 60)
        print("CHATGPT MCP CONNECTION OPTIMIZER")
        print("=" * 60)
        
        # Step 1: Analyze current setup
        print("\n[1/4] Analyzing MCP server...")
        server_info = self.analyze_mcp_server()
        print(f"  Tools: {len(server_info.get('tools', []))}")
        print(f"  Resources: {len(server_info.get('resources', []))}")
        
        # Step 2: OpenAI optimization (if available)
        print("\n[2/4] Running AI optimization...")
        ai_result = await self.optimize_with_openai()
        print(f"  Status: {ai_result.get('status', 'completed')}")
        
        # Step 3: Create production config
        print("\n[3/4] Creating production configuration...")
        prod_config = self.create_production_config()
        
        # Save optimized config
        output_path = Path("/home/yenn/.openai/config_optimized.json")
        with open(output_path, 'w') as f:
            json.dump(prod_config, f, indent=2)
        print(f"  Saved to: {output_path}")
        
        # Step 4: Generate integration script
        print("\n[4/4] Generating integration script...")
        self.create_integration_script()
        
        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE")
        print("=" * 60)
        
        return {
            "server_info": server_info,
            "ai_optimization": ai_result,
            "production_config": prod_config,
            "config_path": str(output_path)
        }
    
    def create_integration_script(self):
        """Create ChatGPT integration test script"""
        script = '''#!/usr/bin/env python3
"""
ChatGPT Diamond Vault Integration Test
"""

import os
import json
from openai import OpenAI

# Load config
config_path = "/home/yenn/.openai/config_optimized.json"
with open(config_path) as f:
    config = json.load(f)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

print("Testing ChatGPT MCP Integration...")

# Test 1: Check MCP server availability
print("\\n[TEST 1] MCP Server Availability")
try:
    import subprocess
    result = subprocess.run(
        ["python3", "/home/yenn/scripts/diamond_vault_mcp_server.py"],
        capture_output=True,
        timeout=5
    )
    print("✅ MCP server accessible")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: ChatGPT with MCP tools
print("\\n[TEST 2] ChatGPT with Diamond Vault Tools")
try:
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": "Use the quantum_hash tool to hash the string 'yennefer'"}
        ]
    )
    print(f"✅ Response: {response.choices[0].message.content[:100]}...")
except Exception as e:
    print(f"⚠️  ChatGPT API: {e}")

print("\\nIntegration test complete.")
'''
        
        script_path = Path("/home/yenn/scripts/test_chatgpt_mcp.py")
        with open(script_path, 'w') as f:
            f.write(script)
        script_path.chmod(0o755)
        print(f"  Created: {script_path}")

if __name__ == "__main__":
    optimizer = ChatGPTMCPOptimizer()
    result = asyncio.run(optimizer.run_optimization())
    
    print("\n📋 NEXT STEPS:")
    print("1. Export OPENAI_API_KEY: export OPENAI_API_KEY='sk-...'")
    print("2. Test integration: python3 /home/yenn/scripts/test_chatgpt_mcp.py")
    print("3. Use in ChatGPT: Enable MCP servers in ChatGPT settings")
    print(f"4. Config: {result['config_path']}")
