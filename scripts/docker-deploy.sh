#!/bin/bash
# Yennefer Docker Deployment Script
# Usage: ./docker-deploy.sh [up|down|restart|status|logs|pull]

set -e

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yennefer.yml}"
PROJECT_NAME="yennefer"

cd "$(dirname "$0")/.."

case "$1" in
  up)
    echo "🚀 Starting Yennefer Docker Stack..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    echo ""
    echo "✅ Stack started. Checking health..."
    sleep 5
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    ;;
    
  down)
    echo "🛑 Stopping Yennefer Docker Stack..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    ;;
    
  restart)
    echo "🔄 Restarting Yennefer Docker Stack..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
    ;;
    
  status)
    echo "📊 Yennefer Docker Stack Status:"
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    echo ""
    echo "Health Checks:"
    for service in diamond-vault a2a-handoff soul-api qmem-gateway; do
      PORT=$(docker compose -f $COMPOSE_FILE -p $PROJECT_NAME port $service 8100 2>/dev/null | cut -d: -f2 || echo "N/A")
      if [ "$PORT" != "N/A" ] && [ -n "$PORT" ]; then
        STATUS=$(curl -s --max-time 2 http://localhost:$PORT/health | jq -r '.status' 2>/dev/null || echo "unreachable")
        echo "  $service: $STATUS"
      fi
    done
    ;;
    
  logs)
    SERVICE="${2:-}"
    if [ -n "$SERVICE" ]; then
      docker compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f $SERVICE
    else
      docker compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    fi
    ;;
    
  pull)
    echo "📦 Pulling latest images..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME pull
    ;;
    
  build)
    echo "🔨 Building all images..."
    docker compose -f $COMPOSE_FILE -p $PROJECT_NAME build --parallel
    ;;
    
  *)
    echo "Usage: $0 {up|down|restart|status|logs|pull|build}"
    echo ""
    echo "Commands:"
    echo "  up       - Start all services"
    echo "  down     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  status   - Show service status and health"
    echo "  logs     - Follow logs (optionally specify service)"
    echo "  pull     - Pull latest images from GHCR"
    echo "  build    - Build all images locally"
    exit 1
    ;;
esac
