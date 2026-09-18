"""
Entrypoint template for generated apps.
The agent replaces this file's content with the generated app code.
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler)
    print(f"Serving on port {PORT}")
    server.serve_forever()
