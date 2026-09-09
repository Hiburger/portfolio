#!/usr/bin/env python3
"""Dev server mimicking GitHub Pages: unknown paths get 404.html with a 404 status.

Usage: python3 serve.py [port]  (default 4173)
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def send_error(self, code, message=None, explain=None):
        if code == 404:
            try:
                with open(os.path.join(ROOT, "404.html"), "rb") as f:
                    body = f.read()
            except OSError:
                super().send_error(code, message, explain)
                return
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
        else:
            super().send_error(code, message, explain)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    print(f"Serving {ROOT} on http://127.0.0.1:{port} (404.html enabled)")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
