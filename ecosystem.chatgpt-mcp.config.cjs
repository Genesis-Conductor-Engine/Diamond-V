module.exports = {
  apps: [{
    name: "chatgpt-mcp-http",
    script: "/home/yenn/scripts/chatgpt_mcp_http_server.py",
    interpreter: "python3",
    cwd: "/home/yenn",
    env: {
      MCP_HTTP_PORT: "8095",
      PYTHONUNBUFFERED: "1",
      JAX_PLATFORM_NAME: "gpu",
      CUDA_VISIBLE_DEVICES: "0"
    },
    instances: 1,
    exec_mode: "fork",
    autorestart: true,
    watch: false,
    max_memory_restart: "512M",
    error_file: "/home/yenn/.pm2/logs/chatgpt-mcp-error.log",
    out_file: "/home/yenn/.pm2/logs/chatgpt-mcp-out.log",
    log_date_format: "YYYY-MM-DD HH:mm:ss Z",
    min_uptime: "10s",
    max_restarts: 10,
    restart_delay: 4000
  }]
};
