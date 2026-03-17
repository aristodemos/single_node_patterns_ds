import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORT", "9101"))
TARGET_BASE_URL = os.environ.get("TARGET_BASE_URL", "http://legacy-app:8100")
SCRAPE_TIMEOUT_SECONDS = float(os.environ.get("SCRAPE_TIMEOUT_SECONDS", "1.5"))


def fetch_stats():
    with urllib.request.urlopen(f"{TARGET_BASE_URL}/internal/stats", timeout=SCRAPE_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def to_prometheus(data):
    lines = [
        "# HELP legacy_requests_total Total requests handled by the legacy app",
        "# TYPE legacy_requests_total counter",
        f"legacy_requests_total {data['requests_total']}",
        "# HELP legacy_errors_total Total failed requests handled by the legacy app",
        "# TYPE legacy_errors_total counter",
        f"legacy_errors_total {data['errors_total']}",
        "# HELP legacy_last_latency_milliseconds Most recent request latency",
        "# TYPE legacy_last_latency_milliseconds gauge",
        f"legacy_last_latency_milliseconds {data['last_latency_ms']}",
        "# HELP legacy_queue_depth Current synthetic queue depth",
        "# TYPE legacy_queue_depth gauge",
        f"legacy_queue_depth {data['queue_depth']}",
    ]
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            self._send(200, b"ok\n")
            return
        if self.path == "/metrics":
            try:
                payload = to_prometheus(fetch_stats()).encode("utf-8")
                self._send(200, payload, "text/plain; version=0.0.4")
            except Exception as exc:
                body = f"adapter scrape failed: {exc}\n".encode("utf-8")
                self._send(500, body)
            return
        self._send(404, b"not found\n")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    # HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()