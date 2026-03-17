from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8080

print(f"Starting HTTP server on port {PORT}")
HTTPServer(("", PORT), SimpleHTTPRequestHandler).serve_forever()