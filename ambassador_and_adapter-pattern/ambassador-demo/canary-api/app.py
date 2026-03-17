import json
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8002"))
VARIANT = os.environ.get("VARIANT", "stable")

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
        if parsed.path == "/quote":
            params = urllib.parse.parse_qs(parsed.query)
            name = params.get("name", ["student"])[0]
            payload = {
                "variant": VARIANT,
                "message": f"Hello, {name}! Served by the {VARIANT} backend.",
                "served_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            if VARIANT == "canary":
                payload["message"] += " Canary adds a new greeting format."
            self._send(200, json.dumps(payload, indent=2).encode("utf-8"), "application/json")
            return
        self._send(404, b"not found\n")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
