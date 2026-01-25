#!/usr/bin/env bash
#
# QMCP HYBRID MESH LAUNCHER
# Starts the complete QMCP fleet: Queue + Gateway + Local Worker + Remote Uplink
#
# Usage:
#   ./start_qmcp_mesh.sh [--local-only] [--remote-only] [--dry-run]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${HOME}/.qmcp/logs"
PID_DIR="${HOME}/.qmcp/pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo " QMCP HYBRID MESH LAUNCHER"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse arguments
LOCAL_ONLY=false
REMOTE_ONLY=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --local-only) LOCAL_ONLY=true ;;
        --remote-only) REMOTE_ONLY=true ;;
        --dry-run) DRY_RUN=true ;;
        --help)
            echo "Usage: $0 [--local-only] [--remote-only] [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --local-only   Only start local components (Queue, Gateway, Worker)"
            echo "  --remote-only  Only start remote uplink"
            echo "  --dry-run      Start uplink in dry-run mode (no actual dispatches)"
            exit 0
            ;;
    esac
done

print_header

# Check dependencies
echo "Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
print_status "Python 3 found"

if ! python3 -c "import zmq" 2>/dev/null; then
    print_warning "pyzmq not installed, installing..."
    pip3 install --break-system-packages pyzmq 2>/dev/null || pip3 install pyzmq
fi
print_status "pyzmq available"

if [ "$REMOTE_ONLY" != "true" ]; then
    # Check for CuPy (optional)
    if python3 -c "import cupy" 2>/dev/null; then
        print_status "CuPy available (GPU acceleration enabled)"
    else
        print_warning "CuPy not available (CPU mode)"
    fi
fi

if [ "$LOCAL_ONLY" != "true" ]; then
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) not found. Install with: sudo apt install gh"
        exit 1
    fi
    if ! gh auth status &>/dev/null; then
        print_error "GitHub CLI not authenticated. Run: gh auth login"
        exit 1
    fi
    print_status "GitHub CLI authenticated"
fi

echo ""
echo "Starting QMCP Mesh components..."
echo ""

# Function to start a component
start_component() {
    local name="$1"
    local cmd="$2"
    local log_file="$LOG_DIR/${name}.log"
    local pid_file="$PID_DIR/${name}.pid"
    
    # Kill existing if running
    if [ -f "$pid_file" ]; then
        local old_pid=$(cat "$pid_file")
        if kill -0 "$old_pid" 2>/dev/null; then
            print_warning "Stopping existing $name (PID: $old_pid)"
            kill "$old_pid" 2>/dev/null || true
            sleep 1
        fi
        rm -f "$pid_file"
    fi
    
    # Start new process
    echo "Starting $name..."
    cd "$SCRIPT_DIR"
    nohup $cmd > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "$pid_file"
    sleep 1
    
    if kill -0 $pid 2>/dev/null; then
        print_status "$name started (PID: $pid, Log: $log_file)"
    else
        print_error "$name failed to start. Check $log_file"
        return 1
    fi
}

# Start components
if [ "$REMOTE_ONLY" != "true" ]; then
    # 1. ZMQ Queue Manager
    start_component "qmcp-queue" "python3 qmcp_zmq_queue.py server"
    sleep 1
    
    # 2. Diamond Worker (Local GPU)
    start_component "qmcp-worker" "python3 qmcp_diamond_worker.py"
    sleep 1
    
    # 3. Unified Gateway (optional - for HTTP access)
    start_component "qmcp-gateway" "python3 qmcp_unified_gateway.py --mode http --port 8099"
    sleep 1
fi

if [ "$LOCAL_ONLY" != "true" ]; then
    # 4. Remote Uplink (GitHub Actions bridge)
    if [ "$DRY_RUN" = "true" ]; then
        start_component "qmcp-uplink" "python3 qmcp_remote_uplink.py --dry-run"
    else
        start_component "qmcp-uplink" "python3 qmcp_remote_uplink.py"
    fi
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} QMCP HYBRID MESH ONLINE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Components:"
if [ "$REMOTE_ONLY" != "true" ]; then
    echo "  • Queue Manager:  Port 5565 (REQ), 5566 (PUB), 5567 (PUSH)"
    echo "  • Local Worker:   Processing GPU jobs"
    echo "  • HTTP Gateway:   http://localhost:8099"
fi
if [ "$LOCAL_ONLY" != "true" ]; then
    echo "  • Remote Uplink:  Bridging to GitHub Actions (Tesla T4)"
fi
echo ""
echo "Logs:      $LOG_DIR/"
echo "PIDs:      $PID_DIR/"
echo ""
echo "Commands:"
echo "  • View logs:     tail -f $LOG_DIR/*.log"
echo "  • Stop all:      ./stop_qmcp_mesh.sh"
echo "  • Test local:    curl http://localhost:8099/api/soul"
echo "  • Test remote:   python3 qmcp_remote_uplink.py --dispatch --vector quantum"
echo ""
