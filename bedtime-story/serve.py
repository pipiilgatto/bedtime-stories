#!/usr/bin/env python3
"""
Simple HTTP server for bedtime stories.
Serves static files and provides a status endpoint.
"""

import http.server
import socketserver
import os
import json
from datetime import datetime
import socket
import threading

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Custom endpoint for server info
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            info = {
                "service": "Pipi's Bedtime Stories",
                "time": datetime.now().isoformat(),
                "stories_count": self.count_stories(),
                "directory": DIRECTORY,
                "endpoints": {
                    "/": "Main page (index.html)",
                    "/stories.json": "Raw stories JSON",
                    "/status": "This status page"
                }
            }
            self.wfile.write(json.dumps(info, indent=2).encode())
            return
        # Default static file serving
        super().do_GET()

    def count_stories(self):
        try:
            with open(os.path.join(DIRECTORY, 'stories.json'), 'r') as f:
                data = json.load(f)
                return len(data)
        except:
            return 0

    def log_message(self, format, *args):
        # Suppress normal request logs
        pass

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def main():
    os.chdir(DIRECTORY)
    ip = get_local_ip()
    print(f"Starting bedtime story server at http://{ip}:{PORT}")
    print(f"Local: http://127.0.0.1:{PORT}")
    print(f"Directory: {DIRECTORY}")
    print("Press Ctrl+C to stop.")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()