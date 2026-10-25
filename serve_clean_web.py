import http.server
import socketserver
import os

PORT = 64482
WEB_DIR = r"C:\Users\rajti\Downloads\Projects\DAKSH\mobile_app\build\web"

os.chdir(WEB_DIR)

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"SERVING DAKSH CLEAN BUILD AT PORT {PORT}")
    httpd.serve_forever()
