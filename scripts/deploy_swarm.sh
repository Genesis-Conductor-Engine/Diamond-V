#!/bin/bash
set -e

echo "🚀 Deploying Yennefer AI Swarm..."

# 1. Start swarm API
cd /home/yenn/genesis-q-mem
pkill -f swarm_api || true
nohup python3 swarm_api.py > /tmp/swarm_api.log 2>&1 &
sleep 3

# 2. Verify API
curl -f http://localhost:8300/health || exit 1
echo "✓ Swarm API running on :8300"

# 3. Restart MCP server with swarm tools
pkill -f yennefer_mcp_lite || true
nohup python3 yennefer_mcp_lite.py > /tmp/mcp.log 2>&1 &
sleep 2
echo "✓ MCP server restarted with swarm tools"

# 4. Restart landing server
cd /home/yenn/yennefer-core
sudo systemctl restart yennefer-landing || echo "⚠ Landing server not managed by systemd"
echo "✓ Landing page available at http://localhost:8000/swarm"

echo "✅ Deployment complete!"
echo "📊 Test with: cd /home/yenn/genesis-q-mem && python3 test_swarm_e2e.py"
