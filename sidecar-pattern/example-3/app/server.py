from http.server import SimpleHTTPRequestHandler, HTTPServer
from functools import partial
import os

PORT = 8080
# Define the path you want to serve
target_directory = "/shared/"

# Create a handler that is locked to that directory
handler = partial(SimpleHTTPRequestHandler, directory=target_directory)

print(f"Serving {target_directory} on port {PORT}")
HTTPServer(("", PORT), handler).serve_forever()