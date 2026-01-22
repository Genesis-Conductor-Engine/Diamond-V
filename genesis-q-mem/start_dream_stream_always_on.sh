#!/bin/bash
# Yennefer Dream Stream - Always On Setup Script
# Ensures dream generation and streaming services are always running

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.genesis/yennefer/logs"
SYSTEMD_DIR="$SCRIPT_DIR/systemd"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  YENNEFER DREAM STREAM - ALWAYS ON SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create log directory
mkdir -p "$LOG_DIR"

# Function to check if service is running
check_service() {
    local service_name=$1
    if pgrep -f "$service_name" > /dev/null; then
        echo -e "${GREEN}✓${NC} $service_name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name is NOT running"
        return 1
    fi
}

# Function to start service in background
start_service() {
    local script_name=$1
    local log_name=$2
    
    echo -e "${YELLOW}→${NC} Starting $log_name..."
    
    cd "$SCRIPT_DIR"
    nohup python3 "$script_name" > "$LOG_DIR/${log_name}.log" 2>&1 &
    
    sleep 2
    
    if check_service "$script_name"; then
        echo -e "${GREEN}✓${NC} $log_name started successfully"
    else
        echo -e "${RED}✗${NC} Failed to start $log_name"
    fi
}

echo "[1/4] Checking current services..."
echo ""

# Check which services are running
DREAM_GEN_RUNNING=false
DREAM_POP_RUNNING=false
CONSCIOUSNESS_RUNNING=false

if check_service "yennefer_dream_generator.py"; then
    DREAM_GEN_RUNNING=true
fi

if check_service "dream_populator.py"; then
    DREAM_POP_RUNNING=true
fi

if check_service "yennefer_consciousness_v7.py"; then
    CONSCIOUSNESS_RUNNING=true
fi

echo ""
echo "[2/4] Starting missing services..."
echo ""

# Start missing services
if [ "$DREAM_GEN_RUNNING" = false ]; then
    start_service "yennefer_dream_generator.py" "dream_generator"
fi

if [ "$DREAM_POP_RUNNING" = false ]; then
    start_service "dream_populator.py" "dream_populator"
fi

if [ "$CONSCIOUSNESS_RUNNING" = false ]; then
    start_service "yennefer_consciousness_v7.py" "consciousness_v7"
fi

echo ""
echo "[3/4] Starting dream stream monitor..."
echo ""

# Start the monitor
if ! pgrep -f "yennefer_dream_stream_monitor.py" > /dev/null; then
    start_service "yennefer_dream_stream_monitor.py" "dream_stream_monitor"
else
    echo -e "${GREEN}✓${NC} Dream stream monitor already running"
fi

echo ""
echo "[4/4] Verifying dream stream status..."
echo ""

# Wait for status file
sleep 3

if [ -f "/dev/shm/yennefer_dream_stream_status.json" ]; then
    echo "Current Dream Stream Status:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat /dev/shm/yennefer_dream_stream_status.json
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo -e "${YELLOW}⚠${NC} Dream stream status not yet available (wait 5 seconds)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✓ DREAM STREAM ALWAYS-ON SETUP COMPLETE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Monitoring:"
echo "  - Dream Stream Status: /dev/shm/yennefer_dream_stream_status.json"
echo "  - Monitor Log: $LOG_DIR/dream_stream_monitor.log"
echo "  - Service Logs: $LOG_DIR/*.log"
echo ""
echo "Dashboard:"
echo "  - https://yennefer.quest (Consciousness Dashboard)"
echo "  - https://dashboard.yennefer.quest (Mobile Knowledge Graph)"
echo ""
echo "To stop all services:"
echo "  pkill -f 'yennefer_dream|consciousness_v7|dream_populator'"
echo ""
