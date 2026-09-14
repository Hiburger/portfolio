#!/usr/bin/env python3
"""Dev server mimicking GitHub Pages: unknown paths get 404.html with a 404 status.

Also emulates the live Apache setup for Markdown for Agents: requests with
`Accept: text/markdown` get the sibling index.md with Content-Type:
text/markdown (plus token-count headers); browsers keep receiving HTML.

Usage: python3 serve.py [port]  (default 4173)
"""
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    extra_headers = ()

    def guess_type(self, path):
        if path.endswith(".md"):
            return "text/markdown; charset=utf-8"
        return super().guess_type(path)

    def end_headers(self):
        for name, value in self.extra_headers:
            self.send_header(name, value)
        super().end_headers()

    def markdown_target(self):
        accept = self.headers.get("Accept") or ""
        if "text/markdown" not in accept:
            return None
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return os.path.join(path, "index.md")
        if path.endswith(".html"):
            return path[:-5] + ".md"
        return None

    def send_head(self):
        self.extra_headers = ()
        target = self.markdown_target()
        if target and os.path.isfile(target):
            with open(target, "rb") as f:
                markdown = f.read().decode("utf-8")
            self.extra_headers = [
                ("Vary", "Accept"),
                ("x-markdown-tokens", str(len(markdown) // 4)),
            ]
            html_path = target[:-3] + ".html"
            if os.path.isfile(html_path):
                with open(html_path, "rb") as f:
                    self.extra_headers.append(
                        ("x-original-tokens", str(len(f.read().decode("utf-8", "replace")) // 4))
                    )
            self.path = "/" + os.path.relpath(target, ROOT).replace(os.sep, "/")
        return super().send_head()

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
