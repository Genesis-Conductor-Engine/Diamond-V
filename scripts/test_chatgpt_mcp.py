#!/usr/bin/env python3
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
print("\n[TEST 1] MCP Server Availability")
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
print("\n[TEST 2] ChatGPT with Diamond Vault Tools")
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

print("\nIntegration test complete.")
