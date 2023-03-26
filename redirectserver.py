import http.server
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from pathlib import Path
from io import BytesIO
from PIL import Image
import os

RUDP_FILESERVER_PORT = 3247
RUDP_FILESERVER_IP = '127.0.0.3'
TCP_FILESERVER_PORT = 2060
TCP_FILESERVER_IP = '127.0.0.2'
REDIRECTSERVER_IP = '127.0.0.1'
REDIRECTSERVER_PORT = 2746


class RedirectServer(SimpleHTTPRequestHandler):

    def do_GET(self):
        token = self.headers.get('X-Auth-Token')
        if token == 'tcp' or token == 'TCP':
            if self.path == '/file_tcp.txt':
                self.send_response(302)
                self.send_header('Location', f'http://{TCP_FILESERVER_IP}:{TCP_FILESERVER_PORT}/file_tcp.txt')
                self.end_headers()
            elif self.path == '/image_tcp.jpg':
                self.send_response(302)
                self.send_header('Location', f'http://{TCP_FILESERVER_IP}:{TCP_FILESERVER_PORT}/image_tcp.jpg')
                self.end_headers()
            else:
                self.send_error(404)
        elif token == 'rudp' or token == 'RUDP':
            if self.path == '/file_udp.txt':
                self.send_response(302)
                self.send_header('Location', f'http://{RUDP_FILESERVER_IP}:{RUDP_FILESERVER_PORT}/file_udp.txt')
                self.end_headers()
            elif self.path == '/image_udp.jpg':
                self.send_response(302)
                self.send_header('Location', f'http://{RUDP_FILESERVER_IP}:{RUDP_FILESERVER_PORT}/image_udp.jpg')
                self.end_headers()
            else:
                self.send_error(404)


if __name__ == '__main__':
    server_address = (REDIRECTSERVER_IP, REDIRECTSERVER_PORT)
    server = (HTTPServer(server_address, RedirectServer))
    print(f"SERVER IP and PORT: {REDIRECTSERVER_IP}:{REDIRECTSERVER_PORT}")
    print("Waiting for connection...")
    server.serve_forever()
