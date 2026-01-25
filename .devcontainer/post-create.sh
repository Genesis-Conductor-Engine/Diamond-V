#!/bin/bash
# Post-create script for Yennefer GPU Codespace

set -e

echo "🧬 Initializing Yennefer Development Environment..."

# Install Python dependencies
if [ -f "genesis-q-mem/requirements.txt" ]; then
    echo "📦 Installing Q-Mem Python dependencies..."
    pip install --user -r genesis-q-mem/requirements.txt
fi

if [ -f "requirements.txt" ]; then
    echo "📦 Installing root Python dependencies..."
    pip install --user -r requirements.txt
fi

# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Build Ground Truth library if Makefile exists
if [ -f "genesis-q-mem/Makefile" ]; then
    echo "🔧 Building Ground Truth C library..."
    cd genesis-q-mem && make || echo "⚠️ Ground Truth build skipped (may need GPU)"
    cd ..
fi

# Initialize shared memory files
echo "💾 Initializing shared memory..."
mkdir -p /dev/shm
echo '{"initialized": true, "mode": "codespace", "timestamp": '$(date +%s)'}' > /dev/shm/qmem_live_stats.json
echo '{"breath": 1000, "coherence": 0.95, "mode": "codespace"}' > /dev/shm/yennefer_soul_state.json

# Check GPU availability
echo "🎮 Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
    echo "✅ GPU detected! Running in REAL mode."
    export MONITORING_MODE="real"
else
    echo "⚠️ No GPU detected. Running in SIMULATED mode."
    export MONITORING_MODE="simulated"
fi

# Create convenience aliases
echo "📝 Setting up shell aliases..."
cat >> ~/.bashrc << 'EOF'

# Yennefer aliases
alias qmem-start='cd ~/genesis-q-mem && ./start_live_bench_v2.sh --mini'
alias yenn-start='cd ~/genesis-q-mem && bash start_yennefer_full_system.sh'
alias qmem-health='curl -s http://localhost:8003/api/health | jq'
alias soul-state='curl -s http://localhost:8088/api/soul | jq'
alias logs-qmem='tail -f /var/log/qmem/live_bench.log 2>/dev/null || echo "No Q-Mem logs yet"'
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🧬 YENNEFER CODESPACE READY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  Quick commands:"
echo "    qmem-start   - Start Q-Mem benchmark (mini mode)"
echo "    yenn-start   - Start full Yennefer consciousness"
echo "    qmem-health  - Check Q-Mem API health"
echo "    soul-state   - View Yennefer soul state"
echo ""
echo "  GPU Mode: ${MONITORING_MODE:-simulated}"
echo ""
