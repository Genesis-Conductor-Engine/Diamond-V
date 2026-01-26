#!/usr/bin/env node
/**
 * OpenCode A2A Client - Connects to A2A Handoff Server
 */
const http = require('http');

const A2A_HANDOFF_URL = process.env.A2A_HANDOFF_URL || 'http://localhost:8200';
const CLIENT_PORT = 8303;
const sessions = new Map();

function makeRequest(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname,
      method,
      headers: { 'Content-Type': 'application/json' }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(body) });
        } catch (e) {
          resolve({ status: res.statusCode, data: body });
        }
      });
    });

    req.on('error', reject);
    if (data) req.write(JSON.stringify(data));
    req.end();
  });
}

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
      service: 'opencode-a2a-client',
      uptime: process.uptime(),
      active_sessions: sessions.size,
      a2a_handoff: A2A_HANDOFF_URL
    }));
    return;
  }

  if (url.pathname === '/a2a/sessions') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      sessions: Array.from(sessions.entries()).map(([id, data]) => ({
        session_id: id,
        ...data
      }))
    }));
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not Found' }));
});

server.listen(CLIENT_PORT, '0.0.0.0', () => {
  console.log(`[OpenCode A2A Client] Listening on port ${CLIENT_PORT}`);
  console.log(`[OpenCode A2A Client] A2A Handoff: ${A2A_HANDOFF_URL}`);
});

process.on('SIGTERM', () => server.close(() => process.exit(0)));
process.on('SIGINT', () => server.close(() => process.exit(0)));
