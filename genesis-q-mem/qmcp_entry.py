#!/usr/bin/env python3
"""
QMCP Consumer Release Entry Point
Combines LiveBench daemon and API gateway into single executable
"""

import threading
import time
import sys
import os
import signal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[QMCP] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment setup for consumer release
os.environ['MONITORING_MODE'] = 'real'
os.environ['CSV_LOG_DIR'] = os.path.expanduser('~/.qmcp/logs')
os.environ['UPDATE_INTERVAL_SEC'] = '1.0'
os.environ['CLOUD_LATENCY_AVG_MS'] = '250.0'
os.environ['CLOUD_POWER_AVG_WATTS'] = '400.0'

# Import Q-Mem components
try:
    from qmem_live_bench_v2 import LiveBenchmark
    from qmem_bubble_gateway_v2 import app
    import uvicorn
    IMPORTS_OK = True
except ImportError as e:
    logger.error(f"Failed to import Q-Mem components: {e}")
    IMPORTS_OK = False

class QMCPConsumerApp:
    """Main application controller for QMCP consumer release"""
    
    def __init__(self):
        self.daemon = None
        self.daemon_thread = None
        self.gateway_thread = None
        self.running = True
        
        # Create user data directory
        os.makedirs(os.path.expanduser('~/.qmcp/logs'), exist_ok=True)
        
        logger.info("="*70)
        logger.info("QMCP CONSUMER RELEASE - QUANTUM MEMORY CONTROL PROTOCOL")
        logger.info("="*70)
        logger.info("Version: 1.0.0")
        logger.info("Mode: Consumer Release")
        logger.info("="*70)
    
    def run_daemon(self):
        """Run the quantum benchmark daemon"""
        logger.info("🚀 Starting Quantum Benchmark Daemon...")
        try:
            self.daemon = LiveBenchmark()
            self.daemon.run()
        except Exception as e:
            logger.error(f"Daemon error: {e}")
    
    def run_gateway(self):
        """Run the API gateway"""
        logger.info("🌐 Starting API Gateway on http://127.0.0.1:8003")
        try:
            config = uvicorn.Config(
                app,
                host="127.0.0.1",
                port=8003,
                log_level="error",
                access_log=False
            )
            server = uvicorn.Server(config)
            server.run()
        except Exception as e:
            logger.error(f"Gateway error: {e}")
    
    def start(self):
        """Start both daemon and gateway"""
        if not IMPORTS_OK:
            logger.error("Cannot start: missing dependencies")
            sys.exit(1)
        
        # Start daemon in background thread
        self.daemon_thread = threading.Thread(target=self.run_daemon, daemon=True)
        self.daemon_thread.start()
        logger.info("✅ Daemon thread started")
        
        # Wait for daemon to initialize
        time.sleep(3)
        
        # Start gateway (blocking)
        logger.info("✅ Starting gateway (blocking)...")
        self.run_gateway()
    
    def stop(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down QMCP...")
        self.running = False
        sys.exit(0)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start application
    app = QMCPConsumerApp()
    
    try:
        app.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        app.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
