import json
import os
import random
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "8100"))
state = {
    "requests_total": 0,
    "errors_total": 0,
    "last_latency_ms": 0,
    "queue_depth": 0,
}

class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/healthz":
            self._send(200, b"ok\n")
            return
        if parsed.path == "/work":
            params = urllib.parse.parse_qs(parsed.query)
            fail = params.get("fail", ["0"])[0] == "1"
            latency_ms = random.randint(30, 220)
            time.sleep(latency_ms / 1000)
            state["requests_total"] += 1
            state["last_latency_ms"] = latency_ms
            state["queue_depth"] = random.randint(0, 12)
            if fail:
                state["errors_total"] += 1
                print(f"LEGACY level=ERROR msg='checkout failed' latency_ms={latency_ms}", flush=True)
                self._send(500, f"legacy failure after {latency_ms}ms\n".encode("utf-8"))
                return
            print(f"LEGACY level=INFO msg='checkout ok' latency_ms={latency_ms}", flush=True)
            self._send(200, f"legacy success after {latency_ms}ms\n".encode("utf-8"))
            return
        if parsed.path == "/internal/stats":
            payload = dict(state)
            payload["component"] = "legacy-checkout"
            self._send(200, json.dumps(payload, indent=2).encode("utf-8"), "application/json")
            return
        self._send(404, b"not found\n")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    # HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
