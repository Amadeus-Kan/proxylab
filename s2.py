## used http.server module
import http.server
import socketserver

PORT = 12138

handler = http.server.SimpleHTTPRequestHandler
class Myhandler(handler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Home Page</h1>')
        elif self.path == '/file':
            self.send_response(200)
        return super().do_GET()

with socketserver.TCPServer(("",PORT), handler) as httpd:
    print(f"services running at http://localhost:{PORT}")
    httpd.serve_forever()