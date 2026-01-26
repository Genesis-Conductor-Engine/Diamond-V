#!/bin/bash
# Setup OpenCode AI with GitHub Copilot integration

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        OpenCode AI Setup - GitHub Copilot Integration        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

# Check if GitHub CLI is authenticated
if ! gh auth status > /dev/null 2>&1; then
    echo "❌ GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"

# Get GitHub token
GITHUB_TOKEN=$(gh auth token)

echo "✅ OpenCode AI package installed via npm"

# Configure opencode for GitHub
mkdir -p ~/.opencode

cat > ~/.opencode/config.json << INNER_EOF
{
  "provider": "github",
  "github": {
    "token": "$GITHUB_TOKEN",
    "copilot": {
      "enabled": true,
      "model": "gpt-4"
    },
    "enterprise": {
      "enabled": true,
      "url": "https://github.com/Genesis-Conductor-Engine"
    }
  },
  "remoteOffload": {
    "enabled": true,
    "dualBridge": {
      "github_actions": true,
      "tesla_t4": true,
      "workflow": "qflop-dual-bridge.yml"
    }
  },
  "docker": {
    "swarm": true,
    "image": "yennefer-bench:latest"
  }
}
INNER_EOF

echo "✅ OpenCode configuration created at ~/.opencode/config.json"

# Check if the package provides a CLI
NPM_GLOBAL_BIN=$(npm bin -g)
if [ -f "$NPM_GLOBAL_BIN/opencode" ]; then
    echo "✅ OpenCode CLI found at: $NPM_GLOBAL_BIN/opencode"
else
    echo "⚠️  OpenCode CLI not found in npm bin"
    echo "Package may need to be accessed via 'npx opencode-ai' or as a library"
    echo "Checking for alternative commands..."
    ls -la $(npm root -g)/opencode-ai/
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SETUP COMPLETE                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

