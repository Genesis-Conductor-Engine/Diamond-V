#!/usr/bin/env node
/**
 * OpenCode MCP Bridge - Connects OpenCode to existing MCP servers
 */
const http = require('http');

const MCP_SERVERS = {
  yennefer: process.env.MCP_YENNEFER || 'http://localhost:8088',
  qmcp_gateway: process.env.MCP_QMCP_GATEWAY || 'http://localhost:8099',
  diamond_vault: process.env.MCP_DIAMOND_VAULT || 'http://localhost:8100'
};

const BRIDGE_PORT = 8302;

const server = http.createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      service: 'opencode-mcp-bridge',
      uptime: process.uptime(),
      mcp_servers: MCP_SERVERS
    }));
    return;
  }

  if (url.pathname === '/mcp/list') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      servers: Object.keys(MCP_SERVERS).map(key => ({
        name: key,
        url: MCP_SERVERS[key]
      }))
    }));
    return;
  }

  if (url.pathname.startsWith('/mcp/')) {
    const targetServer = url.pathname.split('/')[2];
    const targetPath = '/' + url.pathname.split('/').slice(3).join('/');

    if (!MCP_SERVERS[targetServer]) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'MCP server not found' }));
      return;
    }

    const targetUrl = new URL(targetPath, MCP_SERVERS[targetServer]);
    const proxyReq = http.request(targetUrl, { method: req.method }, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      console.error(`[MCP Bridge] Error:`, err.message);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Bad Gateway' }));
    });

    req.pipe(proxyReq);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not Found' }));
});

server.listen(BRIDGE_PORT, '0.0.0.0', () => {
  console.log(`[OpenCode MCP Bridge] Listening on port ${BRIDGE_PORT}`);
  Object.entries(MCP_SERVERS).forEach(([name, url]) => {
    console.log(`  • ${name}: ${url}`);
  });
});

process.on('SIGTERM', () => server.close(() => process.exit(0)));
process.on('SIGINT', () => server.close(() => process.exit(0)));
