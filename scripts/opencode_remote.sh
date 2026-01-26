#!/bin/bash
# OpenCode Remote Offload - Dual Bridge Execution

TASK="$1"
MODE="${2:-local}"  # local, remote, or dual

echo "🚀 OpenCode Remote Offload"
echo "Task: $TASK"
echo "Mode: $MODE"

if [ "$MODE" = "remote" ] || [ "$MODE" = "dual" ]; then
    echo "📡 Dispatching to GitHub Actions (Tesla T4)..."
    
    # Create task file
    cat > /tmp/opencode_task.json << INNER_EOF
{
  "task": "$TASK",
  "timestamp": "$(date -Iseconds)",
  "mode": "$MODE",
  "offload": {
    "github_actions": true,
    "workflow": "qflop-dual-bridge.yml",
    "duration_minutes": 10,
    "power_mode": "MAXPOWER"
  }
}
INNER_EOF
    
    # Dispatch workflow
    gh workflow run qflop-dual-bridge.yml \
        --field duration_minutes=10 \
        --field power_mode=MAXPOWER
    
    WORKFLOW_ID=$(gh run list --workflow=qflop-dual-bridge.yml --limit 1 --json databaseId --jq '.[0].databaseId')
    echo "✅ Dispatched to workflow: $WORKFLOW_ID"
    echo "Monitor: gh run view $WORKFLOW_ID --log"
fi

if [ "$MODE" = "local" ] || [ "$MODE" = "dual" ]; then
    echo "💻 Executing locally..."
    opencode "$TASK"
fi

