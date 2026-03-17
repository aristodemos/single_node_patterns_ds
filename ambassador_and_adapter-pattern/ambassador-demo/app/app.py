import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("APP_PORT", "8000"))
AMBASSADOR_URL = os.environ.get("AMBASSADOR_URL", "http://ambassador:8001")

INDEX_HTML = """<!doctype html>
<html>
<head><title>Ambassador Demo App</title></head>
<body style="font-family: sans-serif; max-width: 760px; margin: 2rem auto;">
  <h1>Ambassador demo app</h1>
  <p>This app never talks to stable-api or canary-api directly. It only calls the ambassador.</p>
  <form method="get" action="/lookup">
    <label>Name: <input name="name" value="student" /></label>
    <button type="submit">Call ambassador</button>
  </form>
  <p>Try these URLs:</p>
  <ul>
    <li><a href="/lookup?name=student">/lookup?name=student</a></li>
    <li><a href="/lookup?name=student&force=canary">/lookup?name=student&force=canary</a></li>
    <li><a href="/lookup?name=student&force=stable">/lookup?name=student&force=stable</a></li>
  </ul>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: bytes, content_type: str = "text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send(200, INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return

        if parsed.path == "/healthz":
            self._send(200, b"ok\n")
            return

        if parsed.path == "/lookup":
            params = urllib.parse.parse_qs(parsed.query)
            name = params.get("name", ["student"])[0]
            force = params.get("force", [""])[0]
            url = f"{AMBASSADOR_URL}/quote?name={urllib.parse.quote(name)}"
            req = urllib.request.Request(url)
            if force:
                req.add_header("X-Force-Variant", force)
            with urllib.request.urlopen(req, timeout=2) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            page = {
                "app": "demo-app",
                "called_via": AMBASSADOR_URL,
                "response": payload,
            }
            self._send(200, json.dumps(page, indent=2).encode("utf-8"), "application/json")
            return

        self._send(404, b"not found\n")

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
