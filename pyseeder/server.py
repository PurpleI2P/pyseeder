import http.server
import urllib.parse
import ssl
import os

class ReseedHandler(http.server.SimpleHTTPRequestHandler):
    """Handles reseeding requests"""
    i2pseeds_file = ""
    server_version = "Pyseeder Server"
    sys_version = ""

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/i2pseeds.su3":
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length",
                    os.path.getsize(self.i2pseeds_file))
            self.end_headers()
            with open(self.i2pseeds_file, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Not found")

def run_server(host, port, priv_key, cert, i2pseeds_file):
    """Start HTTPS server"""
    Handler = ReseedHandler
    Handler.i2pseeds_file = i2pseeds_file

    httpd = http.server.HTTPServer((host, int(port)), Handler)
    httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True,
            keyfile=priv_key, certfile=cert, ssl_version=ssl.PROTOCOL_TLSv1)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        exit()
