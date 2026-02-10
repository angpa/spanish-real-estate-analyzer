import http.server
import socketserver
import urllib.parse
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import handler as IndexHandler
from api.demographics import handler as DemographicsHandler

PORT = 5328

class DevServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Route mapping
        if path == "/api" or path == "/api/":
            handler = IndexHandler(self.request, self.client_address, self.server)
            # Handler handles the request in its init/constructor usually? 
            # No, BaseHTTPRequestHandler handles it in handle() which calls do_GET.
            # But here we are instantiating it. 
            # Wait, Vercel's `class handler(BaseHTTPRequestHandler)` pattern relies on the runtime to instantiate it for each request.
            # If we instantiate it, it will try to read from rfile/wfile.
            # We can't easily wrap it like this because `BaseHTTPRequestHandler.__init__` calls `setup()` and `handle()`.
            # So we need to delegate `do_GET` to it?
            
            # Actually, `BaseHTTPRequestHandler` expects `request`, `client_address`, `server`.
            # Passing them will trigger `handle()` which calls `do_GET()`.
            return

        if path.startswith("/api/demographics"):
            # We need to ensure query params are passed. 
            # The handler reads self.path, so we just need to pass the same request context.
            handler = DemographicsHandler(self.request, self.client_address, self.server)
            return

        # Default 404
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

    # Start the server
print(f"Starting Python API server on port {PORT}...")
with socketserver.TCPServer(("", PORT), DevServerHandler) as httpd:
    print("Serving forever")
    httpd.serve_forever()
