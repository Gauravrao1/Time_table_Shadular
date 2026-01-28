import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", "5173"))
DIRECTORY = os.path.dirname(__file__) or "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving frontend at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
