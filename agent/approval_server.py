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
