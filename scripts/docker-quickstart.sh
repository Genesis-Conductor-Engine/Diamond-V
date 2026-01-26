#!/bin/bash
# Yennefer Docker Quick Start
# Builds and runs the entire stack with one command

set -e

cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🐳 YENNEFER DOCKER QUICK START"
echo "═══════════════════════════════════════════════════════════════════════════"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'ENV'
# Yennefer Environment Variables
NODE_ENV=production
COMPUTE_MODE=dual
MONITORING_MODE=simulated
ALWAYS_ON=true

# Add your secrets here:
# ETH_PRIVATE_KEY=
# ALCHEMY_API_KEY=
ENV
fi

# Build images
echo ""
echo "📦 Building Docker images..."
docker compose -f docker-compose.yennefer.yml build --parallel

# Start services
echo ""
echo "🚀 Starting services..."
docker compose -f docker-compose.yennefer.yml up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check health
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.yennefer.yml ps

echo ""
echo "🔗 Endpoints:"
echo "  Diamond Vault: http://localhost:8100"
echo "  A2A Handoff:   http://localhost:8200"
echo "  Soul API:      http://localhost:8088"
echo "  Q-Mem Gateway: http://localhost:8003"

echo ""
echo "✅ Yennefer is running!"
echo ""
echo "Commands:"
echo "  View logs:     docker compose -f docker-compose.yennefer.yml logs -f"
echo "  Stop:          docker compose -f docker-compose.yennefer.yml down"
echo "  Restart:       docker compose -f docker-compose.yennefer.yml restart"
