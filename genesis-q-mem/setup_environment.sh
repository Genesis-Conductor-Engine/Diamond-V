#!/bin/bash
# Yennefer Consciousness - Environment Setup Script
# Version: 7.0 - Mobile Optimized Knowledge Graph

set -e

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║   🔮 YENNEFER CONSCIOUSNESS - ENVIRONMENT SETUP                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"

# Create required directories
echo "📁 Creating directories..."
mkdir -p ~/.genesis/yennefer/{thoughts,dream_store/{dreams,insights,archive},qmcp_notes,aesthetic_templates}
mkdir -p ~/.qmcp/logs
mkdir -p /var/log/qmem 2>/dev/null || mkdir -p ~/.qmem/logs

# Set permissions
chmod -R 755 ~/.genesis/yennefer

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
pip3 install --quiet --upgrade fastapi uvicorn websockets cryptography pynvml 2>/dev/null || true

# Generate aesthetic templates if not exist
if [ ! -f ~/.genesis/yennefer/aesthetic_templates/manifest.json ]; then
    echo "🎨 Generating aesthetic templates..."
    cd ~/genesis-q-mem
    python3 yennefer_aesthetic_encoder.py 2>/dev/null || echo "   (templates will be generated on first run)"
fi

# Check shared memory
echo "💾 Checking shared memory..."
if [ -d /dev/shm ]; then
    touch /dev/shm/yennefer_test && rm /dev/shm/yennefer_test
    echo "   ✓ /dev/shm writable"
else
    echo "   ⚠ /dev/shm not available, using file-based state"
fi

# Display configuration
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║   CONFIGURATION                                                              ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║   Thoughts:     ~/.genesis/yennefer/thoughts/                                ║"
echo "║   Dreams:       ~/.genesis/yennefer/dream_store/dreams/                      ║"
echo "║   Insights:     ~/.genesis/yennefer/dream_store/insights/                    ║"
echo "║   QMCP Chain:   ~/.genesis/yennefer/qmcp_notes/                              ║"
echo "║   Templates:    ~/.genesis/yennefer/aesthetic_templates/                     ║"
echo "║   Soul State:   /dev/shm/yennefer_soul_state.json                            ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║   PORTS                                                                      ║"
echo "║   Dashboard:    8090 (https://yennefer.quest)                                ║"
echo "║   QMCP API:     8003 (https://bench.yennefer.quest)                          ║"
echo "║   Soul API:     8088 (https://api.yennefer.quest)                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "✓ Environment setup complete!"
echo ""
echo "To start Yennefer Consciousness:"
echo "  cd ~/genesis-q-mem && python3 yennefer_consciousness_v7.py"
echo ""
echo "To start QMCP:"
echo "  cd ~/genesis-q-mem && python3 qmcp_entry.py"
