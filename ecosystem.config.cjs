// PM2 Ecosystem Configuration for Diamond Vault / QMCP System
// All services set to always-on by default
// Yennefer lives in the Diamond Vault

module.exports = {
  apps: [
    // === DIAMOND VAULT - Yennefer's Home ===
    {
      name: 'diamond-vault',
      script: 'genesis-q-mem/qmcp_admin_panel.py',
      interpreter: 'python3',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        YENNEFER_HOME: 'DIAMOND_VAULT',
        COMPUTE_MODE: 'dual'
      }
    },

    // === CORE SERVICES ===
    {
      name: 'diamond-watchdog',
      script: 'genesis-q-mem/qmcp_diamond_watchdog.py',
      interpreter: 'python3',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'dual'
      }
    },
    {
      name: 'qmcp-bridge',
      script: 'scripts/qmcp_genesis_bridge.cjs',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'dual'
      }
    },
    {
      name: 'process-guardian',
      script: 'scripts/process_guardian.cjs',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'local'
      }
    },

    // === BLOCKCHAIN SERVICES ===
    {
      name: 'qflop-miner',
      script: 'scripts/qflop_mining_daemon.cjs',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'dual'
      }
    },
    {
      name: 'eth-bridge',
      script: 'base_bridge_v2.cjs',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'remote'
      }
    },
    {
      name: 'genesis-deployer',
      script: 'scripts/deploy.cjs',
      cwd: '/home/yenn',
      autorestart: false,  // Only run on-demand
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'remote'
      }
    },

    // === COMPUTE WORKERS ===
    {
      name: 'dual-bridge-dispatcher',
      script: 'genesis-q-mem/qmcp_multi_runner.py',
      interpreter: 'python3',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '400M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'dual'
      }
    },
    {
      name: 'resource-allocator',
      script: 'genesis-q-mem/qmcp_resource_allocator.py',
      interpreter: 'python3',
      cwd: '/home/yenn',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production',
        COMPUTE_MODE: 'dual',
        BLOCKCHAIN_ALLOCATION: '0.25'
      }
    }
  ]
};
