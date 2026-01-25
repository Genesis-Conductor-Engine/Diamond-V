#!/usr/bin/env bash
#
# QMCP HYBRID MESH STOPPER
# Stops all QMCP fleet components
#

PID_DIR="${HOME}/.qmcp/pids"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo "Stopping QMCP Mesh components..."
echo ""

for pid_file in "$PID_DIR"/*.pid; do
    if [ -f "$pid_file" ]; then
        name=$(basename "$pid_file" .pid)
        pid=$(cat "$pid_file")
        
        if kill -0 "$pid" 2>/dev/null; then
            echo -n "Stopping $name (PID: $pid)... "
            kill "$pid" 2>/dev/null
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            echo -e "${GREEN}stopped${NC}"
        else
            echo -e "$name: ${RED}not running${NC}"
        fi
        rm -f "$pid_file"
    fi
done

echo ""
echo "QMCP Mesh stopped."
