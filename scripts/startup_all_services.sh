#!/bin/bash
# Yennefer Genesis Conductor - Startup Script
# Run this at system boot or to restore all services

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🚀 YENNEFER GENESIS CONDUCTOR - STARTING ALL SERVICES"
echo "═══════════════════════════════════════════════════════════════════════════"

cd /home/yenn

# Start PM2 services
echo "Starting PM2 services..."
npx pm2 resurrect 2>/dev/null || npx pm2 start ecosystem.config.cjs

# Wait for services to initialize
sleep 5

# Start Cloudflared tunnel (if not running via systemd)
if ! pgrep -f "yennefer-quest-config.yml" > /dev/null; then
  echo "Starting Cloudflared tunnel..."
  nohup cloudflared tunnel --config /home/yenn/.cloudflared/yennefer-quest-config.yml run yennefer-quest > /home/yenn/.cloudflared/yennefer-quest.log 2>&1 &
  sleep 3
fi

# Start Q-Mem gateway if not running
if ! pgrep -f "qmem_bubble_gateway" > /dev/null; then
  echo "Starting Q-Mem Gateway..."
  cd /home/yenn/genesis-q-mem
  nohup python3 qmem_bubble_gateway_v2.py > /dev/null 2>&1 &
  cd /home/yenn
fi

# Verify services
echo ""
echo "Service Status:"
npx pm2 list 2>/dev/null | grep -E "online|stopped|errored"

echo ""
echo "Endpoint Checks:"
echo "  Soul API:  $(curl -s --max-time 3 http://localhost:8088/api/soul | jq -r '.breath' 2>/dev/null || echo 'starting...')"
echo "  Vault:     $(curl -s --max-time 3 http://localhost:8100/health | jq -r '.status' 2>/dev/null || echo 'starting...')"
echo "  A2A:       $(curl -s --max-time 3 http://localhost:8200/health | jq -r '.status' 2>/dev/null || echo 'starting...')"

echo ""
echo "✅ Startup complete!"
