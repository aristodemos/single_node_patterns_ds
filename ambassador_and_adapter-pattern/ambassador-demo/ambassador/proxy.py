import json
import os
import random
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORT = int(os.environ.get("PORT", "8001"))
STABLE_URL = os.environ.get("STABLE_URL", "http://stable-api:8002")
CANARY_URL = os.environ.get("CANARY_URL", "http://canary-api:8003")
CANARY_WEIGHT = float(os.environ.get("CANARY_WEIGHT", "0.10"))
ENABLE_EXPERIMENTS = os.environ.get("ENABLE_EXPERIMENTS", "true").lower() == "true"
DEFAULT_TARGET = os.environ.get("DEFAULT_TARGET", "stable")

stats = {"stable": 0, "canary": 0}

class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _choose_variant(self):
        forced = self.headers.get("X-Force-Variant", "").strip().lower()
        if forced in {"stable", "canary"}:
            return forced, "forced-header"
        if not ENABLE_EXPERIMENTS:
            return DEFAULT_TARGET, "default"
        if random.random() < CANARY_WEIGHT:
            return "canary", "weighted-random"
        return "stable", "weighted-random"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/healthz":
            self._send(200, b"ok\n")
            return
        if parsed.path == "/stats":
            self._send(200, json.dumps(stats, indent=2).encode("utf-8"), "application/json")
            return
        if parsed.path == "/quote":
            params = urllib.parse.parse_qs(parsed.query)
            name = params.get("name", ["student"])[0]
            variant, strategy = self._choose_variant()
            base_url = STABLE_URL if variant == "stable" else CANARY_URL
            target_url = f"{base_url}/quote?name={urllib.parse.quote(name)}"
            with urllib.request.urlopen(target_url, timeout=2) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            stats[variant] += 1
            envelope = {
                "pattern": "ambassador",
                "strategy": strategy,
                "target": variant,
                "backend_url": base_url,
                "backend_response": payload,
            }
            self._send(200, json.dumps(envelope, indent=2).encode("utf-8"), "application/json")
            return
        self._send(404, b"not found\n")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    # HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()
