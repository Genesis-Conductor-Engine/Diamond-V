#!/usr/bin/env python3
"""
QMCP ZMQ MESSAGE QUEUE
Lightweight message queue for async computation results using ZeroMQ.

Architecture:
- REQ/REP (5555): Synchronous compute requests
- PUB/SUB (5556): Async result notifications  
- PUSH/PULL (5557): Job queue for Diamond Vault workers

Job Lifecycle:
1. Client submits job via REQ → Gateway responds with job_id
2. Gateway PUSHes job to worker queue
3. Worker PULLs job, executes, PUBs result
4. Client polls result via REQ or subscribes via SUB
"""

import os
import json
import time
import uuid
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import zmq

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

ZMQ_REQ_PORT = int(os.getenv("QMCP_ZMQ_REQ_PORT", "5565"))
ZMQ_PUB_PORT = int(os.getenv("QMCP_ZMQ_PUB_PORT", "5566"))
ZMQ_PUSH_PORT = int(os.getenv("QMCP_ZMQ_PUSH_PORT", "5567"))
ZMQ_HOST = os.getenv("QMCP_ZMQ_HOST", "127.0.0.1")

# Job storage path (for persistence across restarts)
JOB_STORE_PATH = "/dev/shm/qmcp_job_store.json"

# Timeouts
DEFAULT_SYNC_TIMEOUT_MS = 30000   # 30 seconds
DEFAULT_ASYNC_TIMEOUT_MS = 300000  # 5 minutes


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class QMCPJob:
    """Represents an async computation job"""
    job_id: str
    skill: str
    params: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    worker_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['status'] = self.status.value
        return d
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'QMCPJob':
        d['status'] = JobStatus(d['status'])
        return cls(**d)


# ═══════════════════════════════════════════════════════════════════════════════
# JOB STORE (Thread-Safe)
# ═══════════════════════════════════════════════════════════════════════════════

class JobStore:
    """Thread-safe job storage with optional persistence"""
    
    def __init__(self, persist_path: Optional[str] = JOB_STORE_PATH):
        self.jobs: Dict[str, QMCPJob] = {}
        self.persist_path = persist_path
        self._lock = threading.Lock()
        self._load_persisted()
    
    def _load_persisted(self):
        """Load jobs from persistent storage"""
        if self.persist_path and os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r') as f:
                    data = json.load(f)
                    for job_id, job_dict in data.items():
                        self.jobs[job_id] = QMCPJob.from_dict(job_dict)
            except Exception:
                pass  # Start fresh if corrupted
    
    def _persist(self):
        """Persist jobs to storage"""
        if self.persist_path:
            try:
                with open(self.persist_path, 'w') as f:
                    json.dump({k: v.to_dict() for k, v in self.jobs.items()}, f)
            except Exception:
                pass
    
    def create_job(self, skill: str, params: Dict[str, Any]) -> QMCPJob:
        """Create a new job"""
        job_id = str(uuid.uuid4())
        job = QMCPJob(job_id=job_id, skill=skill, params=params)
        with self._lock:
            self.jobs[job_id] = job
            self._persist()
        return job
    
    def get_job(self, job_id: str) -> Optional[QMCPJob]:
        """Get job by ID"""
        with self._lock:
            return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, **kwargs) -> Optional[QMCPJob]:
        """Update job fields"""
        with self._lock:
            job = self.jobs.get(job_id)
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                self._persist()
            return job
    
    def list_jobs(self, status: Optional[JobStatus] = None, limit: int = 100) -> list:
        """List jobs, optionally filtered by status"""
        with self._lock:
            jobs = list(self.jobs.values())
            if status:
                jobs = [j for j in jobs if j.status == status]
            return sorted(jobs, key=lambda j: j.created_at, reverse=True)[:limit]
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Remove jobs older than max_age_seconds"""
        cutoff = time.time() - max_age_seconds
        with self._lock:
            to_remove = [jid for jid, job in self.jobs.items() 
                        if job.completed_at and job.completed_at < cutoff]
            for jid in to_remove:
                del self.jobs[jid]
            if to_remove:
                self._persist()


# ═══════════════════════════════════════════════════════════════════════════════
# ZMQ PUBLISHER (Gateway → Clients)
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPPublisher:
    """Publishes job results to subscribers"""
    
    def __init__(self, port: int = ZMQ_PUB_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://127.0.0.1:{port}")  # Bind to localhost
        self.port = port
        print(f"📡 QMCP Publisher bound to tcp://127.0.0.1:{port}")
    
    def publish_result(self, job: QMCPJob):
        """Publish job result to subscribers"""
        topic = f"job.{job.skill}"
        message = json.dumps(job.to_dict())
        self.socket.send_multipart([topic.encode(), message.encode()])
    
    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish generic event"""
        topic = f"event.{event_type}"
        message = json.dumps(data)
        self.socket.send_multipart([topic.encode(), message.encode()])
    
    def close(self):
        self.socket.close()
        self.context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# ZMQ SUBSCRIBER (Clients ← Gateway)
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPSubscriber:
    """Subscribes to job results"""
    
    def __init__(self, host: str = ZMQ_HOST, port: int = ZMQ_PUB_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.host = host
        self.port = port
    
    def subscribe(self, topic: str = ""):
        """Subscribe to topic (empty = all)"""
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
    
    def receive(self, timeout_ms: int = 5000) -> Optional[tuple]:
        """Receive message with timeout"""
        self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
        try:
            topic, message = self.socket.recv_multipart()
            return topic.decode(), json.loads(message.decode())
        except zmq.Again:
            return None
    
    def close(self):
        self.socket.close()
        self.context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# ZMQ JOB QUEUE (Gateway → Workers)
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPJobQueue:
    """PUSH/PULL job queue for distributing work to workers"""
    
    def __init__(self, port: int = ZMQ_PUSH_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(f"tcp://127.0.0.1:{port}")  # Bind to localhost
        self.port = port
        print(f"📤 QMCP Job Queue bound to tcp://127.0.0.1:{port}")
    
    def push_job(self, job: QMCPJob):
        """Push job to worker queue"""
        message = json.dumps(job.to_dict())
        self.socket.send_string(message)
    
    def close(self):
        self.socket.close()
        self.context.term()


class QMCPWorkerQueue:
    """Worker-side job queue (PULL)"""
    
    def __init__(self, host: str = ZMQ_HOST, port: int = ZMQ_PUSH_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(f"tcp://{host}:{port}")
        self.host = host
        self.port = port
    
    def pull_job(self, timeout_ms: int = 5000) -> Optional[QMCPJob]:
        """Pull job from queue with timeout"""
        self.socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
        try:
            message = self.socket.recv_string()
            return QMCPJob.from_dict(json.loads(message))
        except zmq.Again:
            return None
    
    def close(self):
        self.socket.close()
        self.context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# ZMQ REQ/REP (Sync API)
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPReqClient:
    """REQ client for synchronous requests to gateway"""
    
    def __init__(self, host: str = ZMQ_HOST, port: int = ZMQ_REQ_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt(zmq.RCVTIMEO, DEFAULT_SYNC_TIMEOUT_MS)
        self.host = host
        self.port = port
    
    def request(self, action: str, **kwargs) -> Dict[str, Any]:
        """Send request and wait for response"""
        message = json.dumps({"action": action, **kwargs})
        self.socket.send_string(message)
        try:
            response = self.socket.recv_string()
            return json.loads(response)
        except zmq.Again:
            return {"error": "Request timeout", "action": action}
    
    def submit_job(self, skill: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit async job"""
        return self.request("submit_job", skill=skill, params=params)
    
    def poll_job(self, job_id: str) -> Dict[str, Any]:
        """Poll job status"""
        return self.request("poll_job", job_id=job_id)
    
    def call_skill(self, skill: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call skill synchronously"""
        return self.request("call_skill", skill=skill, params=params)
    
    def close(self):
        self.socket.close()
        self.context.term()


class QMCPRepServer:
    """REP server for handling synchronous requests"""
    
    def __init__(self, port: int = ZMQ_REQ_PORT):
        self.port = port
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self._context = None
        self._socket = None
        print(f"🔌 QMCP REP Server configured for port {port}")
    
    def register_handler(self, action: str, handler: Callable):
        """Register handler for action"""
        self.handlers[action] = handler
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request"""
        action = request.get("action")
        if not action:
            return {"error": "Missing action"}
        
        handler = self.handlers.get(action)
        if not handler:
            return {"error": f"Unknown action: {action}"}
        
        try:
            return handler(request)
        except Exception as e:
            return {"error": str(e), "action": action}
    
    def run(self):
        """Run server loop - creates socket in this thread"""
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(f"tcp://127.0.0.1:{self.port}")
        self._socket.setsockopt(zmq.RCVTIMEO, 1000)
        self.running = True
        print(f"🚀 QMCP REP Server running on port {self.port}")
        
        while self.running:
            try:
                message = self._socket.recv_string()
                request = json.loads(message)
                response = self.handle_request(request)
                self._socket.send_string(json.dumps(response))
            except zmq.Again:
                continue  # Timeout, check if still running
            except Exception as e:
                try:
                    self._socket.send_string(json.dumps({"error": str(e)}))
                except:
                    pass
        
        self._socket.close()
        self._context.term()
    
    def stop(self):
        self.running = False
    
    def close(self):
        self.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT REPORTER (Worker → Gateway)
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPResultReporter:
    """Workers use this to report results back to gateway"""
    
    def __init__(self, host: str = ZMQ_HOST, req_port: int = ZMQ_REQ_PORT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{host}:{req_port}")
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.host = host
    
    def report_started(self, job_id: str, worker_id: str):
        """Report job started"""
        message = json.dumps({
            "action": "job_started",
            "job_id": job_id,
            "worker_id": worker_id
        })
        self.socket.send_string(message)
        return self.socket.recv_string()
    
    def report_completed(self, job_id: str, result: Dict[str, Any]):
        """Report job completed"""
        message = json.dumps({
            "action": "job_completed",
            "job_id": job_id,
            "result": result
        })
        self.socket.send_string(message)
        return self.socket.recv_string()
    
    def report_failed(self, job_id: str, error: str):
        """Report job failed"""
        message = json.dumps({
            "action": "job_failed",
            "job_id": job_id,
            "error": error
        })
        self.socket.send_string(message)
        return self.socket.recv_string()
    
    def close(self):
        self.socket.close()
        self.context.term()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE: ALL-IN-ONE QUEUE MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class QMCPQueueManager:
    """
    All-in-one queue manager for the gateway.
    Handles job storage, publishing, and worker distribution.
    
    NOTE: All ZMQ socket creation is deferred to the run() thread to avoid
    cross-thread socket issues.
    """
    
    def __init__(self):
        self.store = JobStore()
        self._server_thread = None
        self._running = False
        
        # These will be created in run()
        self._context = None
        self._rep_socket = None
        self._pub_socket = None
        self._push_socket = None
        
        # Handler registry
        self._handlers = {
            "submit_job": self._handle_submit_job,
            "poll_job": self._handle_poll_job,
            "list_jobs": self._handle_list_jobs,
            "job_started": self._handle_job_started,
            "job_completed": self._handle_job_completed,
            "job_failed": self._handle_job_failed,
        }
    
    def _handle_submit_job(self, request: Dict) -> Dict:
        """Handle job submission"""
        skill = request.get("skill")
        params = request.get("params", {})
        
        if not skill:
            return {"error": "Missing skill"}
        
        job = self.store.create_job(skill, params)
        
        # Push to worker queue
        if self._push_socket:
            try:
                self._push_socket.send_string(json.dumps(job.to_dict()), zmq.NOBLOCK)
            except zmq.Again:
                pass  # No workers available, job stays pending
        
        return {
            "status": "submitted",
            "job_id": job.job_id,
            "skill": skill
        }
    
    def _handle_poll_job(self, request: Dict) -> Dict:
        """Handle job poll"""
        job_id = request.get("job_id")
        if not job_id:
            return {"error": "Missing job_id"}
        
        job = self.store.get_job(job_id)
        if not job:
            return {"error": "Job not found", "job_id": job_id}
        
        return job.to_dict()
    
    def _handle_list_jobs(self, request: Dict) -> Dict:
        """Handle job listing"""
        status = request.get("status")
        limit = request.get("limit", 100)
        
        if status:
            status = JobStatus(status)
        
        jobs = self.store.list_jobs(status=status, limit=limit)
        return {
            "jobs": [j.to_dict() for j in jobs],
            "count": len(jobs)
        }
    
    def _handle_job_started(self, request: Dict) -> Dict:
        """Handle job started notification from worker"""
        job_id = request.get("job_id")
        worker_id = request.get("worker_id")
        
        job = self.store.update_job(
            job_id,
            status=JobStatus.RUNNING,
            started_at=time.time(),
            worker_id=worker_id
        )
        
        if job:
            self._publish_event("job_started", {"job_id": job_id, "worker_id": worker_id})
            return {"status": "ok"}
        return {"error": "Job not found"}
    
    def _handle_job_completed(self, request: Dict) -> Dict:
        """Handle job completed notification from worker"""
        job_id = request.get("job_id")
        result = request.get("result", {})
        
        job = self.store.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            completed_at=time.time(),
            result=result
        )
        
        if job:
            self._publish_result(job)
            return {"status": "ok"}
        return {"error": "Job not found"}
    
    def _handle_job_failed(self, request: Dict) -> Dict:
        """Handle job failed notification from worker"""
        job_id = request.get("job_id")
        error = request.get("error", "Unknown error")
        
        job = self.store.update_job(
            job_id,
            status=JobStatus.FAILED,
            completed_at=time.time(),
            error=error
        )
        
        if job:
            self._publish_result(job)
            return {"status": "ok"}
        return {"error": "Job not found"}
    
    def _publish_result(self, job: QMCPJob):
        """Publish job result"""
        if self._pub_socket:
            try:
                topic = f"job.{job.skill}"
                message = json.dumps(job.to_dict())
                self._pub_socket.send_multipart([topic.encode(), message.encode()], zmq.NOBLOCK)
            except zmq.Again:
                pass
    
    def _publish_event(self, event_type: str, data: Dict):
        """Publish event"""
        if self._pub_socket:
            try:
                topic = f"event.{event_type}"
                message = json.dumps(data)
                self._pub_socket.send_multipart([topic.encode(), message.encode()], zmq.NOBLOCK)
            except zmq.Again:
                pass
    
    def _run_loop(self):
        """Main server loop - creates all sockets in this thread"""
        # Create ZMQ context and sockets in this thread
        self._context = zmq.Context()
        
        # REP socket for request/reply
        self._rep_socket = self._context.socket(zmq.REP)
        self._rep_socket.bind(f"tcp://127.0.0.1:{ZMQ_REQ_PORT}")
        self._rep_socket.setsockopt(zmq.RCVTIMEO, 1000)
        print(f"🔌 QMCP REP Server running on port {ZMQ_REQ_PORT}")
        
        # PUB socket for notifications
        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.bind(f"tcp://127.0.0.1:{ZMQ_PUB_PORT}")
        print(f"📡 QMCP Publisher running on port {ZMQ_PUB_PORT}")
        
        # PUSH socket for worker distribution
        self._push_socket = self._context.socket(zmq.PUSH)
        self._push_socket.bind(f"tcp://127.0.0.1:{ZMQ_PUSH_PORT}")
        print(f"📤 QMCP Job Queue running on port {ZMQ_PUSH_PORT}")
        
        self._running = True
        
        while self._running:
            try:
                message = self._rep_socket.recv_string()
                request = json.loads(message)
                action = request.get("action")
                
                handler = self._handlers.get(action)
                if handler:
                    response = handler(request)
                else:
                    response = {"error": f"Unknown action: {action}"}
                
                self._rep_socket.send_string(json.dumps(response))
            except zmq.Again:
                continue  # Timeout, check running flag
            except Exception as e:
                try:
                    self._rep_socket.send_string(json.dumps({"error": str(e)}))
                except:
                    pass
        
        # Cleanup
        self._rep_socket.close()
        self._pub_socket.close()
        self._push_socket.close()
        self._context.term()
    
    def start(self, blocking: bool = True):
        """Start the queue manager"""
        if blocking:
            self._run_loop()
        else:
            self._server_thread = threading.Thread(target=self._run_loop, daemon=True)
            self._server_thread.start()
            time.sleep(0.5)  # Give sockets time to bind
    
    def stop(self):
        """Stop the queue manager"""
        self._running = False
        if self._server_thread:
            self._server_thread.join(timeout=2.0)
    
    def close(self):
        """Close the queue manager"""
        self.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='QMCP ZMQ Queue')
    parser.add_argument('mode', choices=['server', 'client', 'worker'],
                       help='Run mode: server (gateway), client (test), worker (pull jobs)')
    parser.add_argument('--host', default=ZMQ_HOST, help='Host to connect to')
    args = parser.parse_args()
    
    if args.mode == 'server':
        print("Starting QMCP Queue Manager...")
        manager = QMCPQueueManager()
        try:
            manager.start(blocking=True)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            manager.close()
    
    elif args.mode == 'client':
        print("QMCP Client Test")
        client = QMCPReqClient(host=args.host)
        
        # Submit a test job
        result = client.submit_job("test_skill", {"value": 42})
        print(f"Submit result: {result}")
        
        if "job_id" in result:
            # Poll the job
            job_id = result["job_id"]
            time.sleep(0.5)
            poll_result = client.poll_job(job_id)
            print(f"Poll result: {poll_result}")
        
        client.close()
    
    elif args.mode == 'worker':
        print("QMCP Worker (pull jobs)")
        queue = QMCPWorkerQueue(host=args.host)
        reporter = QMCPResultReporter(host=args.host)
        worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        
        try:
            while True:
                job = queue.pull_job(timeout_ms=5000)
                if job:
                    print(f"Received job: {job.job_id} ({job.skill})")
                    reporter.report_started(job.job_id, worker_id)
                    
                    # Simulate work
                    time.sleep(1)
                    
                    reporter.report_completed(job.job_id, {"result": "done", "worker": worker_id})
                    print(f"Completed job: {job.job_id}")
        except KeyboardInterrupt:
            print("\n🛑 Worker stopping...")
            queue.close()
            reporter.close()
