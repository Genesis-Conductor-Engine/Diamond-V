/**
 * OpenCode AI PM2 Ecosystem Configuration
 * Integrates OpenCode with PM2, MCP servers, and A2A protocols
 */

module.exports = {
  apps: [
    // OpenCode ACP Server (Agent Client Protocol)
    {
      name: 'opencode-acp',
      script: 'npx',
      args: 'opencode-ai acp --port 8300 --hostname 0.0.0.0',
      cwd: '/home/yenn',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        OPENCODE_CONFIG: '/home/yenn/.opencode/config.json'
      },
      error_file: '/home/yenn/.yennefer/logs/opencode-acp-error.log',
      out_file: '/home/yenn/.yennefer/logs/opencode-acp-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // OpenCode Headless Server (for remote API access)
    {
      name: 'opencode-server',
      script: 'npx',
      args: 'opencode-ai serve --port 8301 --hostname 0.0.0.0',
      cwd: '/home/yenn',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        OPENCODE_CONFIG: '/home/yenn/.opencode/config.json'
      },
      error_file: '/home/yenn/.yennefer/logs/opencode-server-error.log',
      out_file: '/home/yenn/.yennefer/logs/opencode-server-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // OpenCode MCP Bridge (connects to existing MCP servers)
    {
      name: 'opencode-mcp-bridge',
      script: '/home/yenn/scripts/opencode_mcp_bridge.cjs',
      cwd: '/home/yenn',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        NODE_ENV: 'production',
        MCP_YENNEFER: 'http://localhost:8088',
        MCP_QMCP_GATEWAY: 'http://localhost:8099',
        MCP_DIAMOND_VAULT: 'http://localhost:8100',
        A2A_HANDOFF: 'http://localhost:8200'
      },
      error_file: '/home/yenn/.yennefer/logs/opencode-mcp-bridge-error.log',
      out_file: '/home/yenn/.yennefer/logs/opencode-mcp-bridge-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },

    // OpenCode A2A Client (connects to A2A Handoff Server)
    {
      name: 'opencode-a2a-client',
      script: '/home/yenn/scripts/opencode_a2a_client.cjs',
      cwd: '/home/yenn',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        NODE_ENV: 'production',
        A2A_HANDOFF_URL: 'http://localhost:8200',
        OPENCODE_ACP_URL: 'http://localhost:8300'
      },
      error_file: '/home/yenn/.yennefer/logs/opencode-a2a-client-error.log',
      out_file: '/home/yenn/.yennefer/logs/opencode-a2a-client-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
