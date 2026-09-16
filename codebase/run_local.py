# -*- coding: utf-8 -*-
"""Mở UI bằng http server để tránh lỗi CORS khi đọc clusters.json.

Chạy:  python codebase/run_local.py
Rồi mở:  http://localhost:8000/index.html
"""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import os

PORT = 8000
os.chdir(Path(__file__).resolve().parent)

handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    url = "http://localhost:%d/index.html" % PORT
    print("FeedbackRadar dang chay tai %s" % url)
    print("Nhan Ctrl+C de dung.")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDa dung.")
