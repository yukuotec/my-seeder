import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import urlparse

from agent.evolver import Evolver
from agent.agent_core import AgentCore

# Optional secret for simple bearer auth. Set env var APPROVAL_SECRET to enable.
APPROVAL_SECRET = os.environ.get('APPROVAL_SECRET')


def _require_auth(headers):
    if not APPROVAL_SECRET:
        return True
    auth = headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        return False
    token = auth.split(' ', 1)[1]
    return token == APPROVAL_SECRET


class ApprovalHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/pending':
            agent = AgentCore('approval-agent', [])
            evolver = Evolver(agent)
            items = evolver.list_pending()
            self._set_headers(200)
            self.wfile.write(json.dumps({'pending': items}).encode())
            return
        if parsed.path == '/status':
            self._set_headers(200)
            self.wfile.write(json.dumps({'ok': True}).encode())
            return
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'not found'}).encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else ''
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        # simple auth
        if not _require_auth(self.headers):
            self._set_headers(401)
            self.wfile.write(json.dumps({'ok': False, 'reason': 'unauthorized'}).encode())
            return

        if parsed.path == '/approve':
            pid = payload.get('pending_id')
            if not pid:
                self._set_headers(400)
                self.wfile.write(json.dumps({'ok': False, 'reason': 'missing pending_id'}).encode())
                return
            approve = payload.get('approve', True)
            agent = AgentCore('approval-agent', [])
            evolver = Evolver(agent)
            if not approve:
                # write rejection approval file so pending is cleaned by evolver.apply_pending_if_approved
                approval_payload = {'approve': False, 'rejected_by': payload.get('by')}
                res = evolver.apply_pending_by_id(pid, approval_payload=approval_payload)
                # apply_pending_by_id will return rejected reason; we reflect that
                self._set_headers(200)
                self.wfile.write(json.dumps({'ok': True, 'applied': res}).encode())
                return

            # write approval and apply
            approval_payload = {'approve': True, 'approved_by': payload.get('by')}
            res = evolver.apply_pending_by_id(pid, approval_payload=approval_payload)
            self._set_headers(200)
            self.wfile.write(json.dumps({'ok': True, 'result': res}).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({'error': 'not found'}).encode())


def run_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), ApprovalHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


def start_in_thread(port=8000):
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    return t
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

APPROVAL_FILE = os.path.join(os.path.dirname(__file__), 'approval.json')


class ApprovalHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path != '/approve':
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'not found'}).encode())
            return
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8') if length else ''
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}
        # write approval file
        try:
            with open(APPROVAL_FILE, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self._set_headers(200)
            self.wfile.write(json.dumps({'ok': True, 'written': True}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode())


def run_server(port=8000):
    server = HTTPServer(('0.0.0.0', port), ApprovalHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


def start_in_thread(port=8000):
    t = threading.Thread(target=run_server, args=(port,), daemon=True)
    t.start()
    return t
