"""
FeedbackRadar Local Development Server
Author: Nguyen Ho Nam (Dev / Agent Engineer)
Description: Khởi chạy HTTP server cục bộ tại thư mục codebase để mở index.html và fetch('clusters.json') mà không bị chặn CORS của trình duyệt.
"""

import os
import sys
import webbrowser
import http.server
import socketserver
from pathlib import Path

# Đảm bảo UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8000
DIRECTORY = Path(__file__).resolve().parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def run_server():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 60)
        print("  FEEDBACKRADAR LOCAL WEB SERVER")
        print(f"  Đang chạy tại: {url}")
        print("  Bấm Ctrl+C để dừng server.")
        print("=" * 60)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[i] Đã dừng server.")

if __name__ == "__main__":
    run_server()
