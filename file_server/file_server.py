import http.server
import socketserver
from pathlib import Path
from io import BytesIO
from PIL import Image
import os

class FileHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/file.txt':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Disposition', 'attachment; filename="file.txt"')
            self.end_headers()
            with open('hosted_files/file.txt', 'rb') as file:
                self.wfile.write(file.read())

        if self.path == '/file2.txt':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Disposition', 'attachment; filename="file2.txt"')
            self.end_headers()
            with open('hosted_files/file2.txt', 'rb') as file:
                self.wfile.write(file.read())
        
        if self.path == '/image_1.jpg':
            # file_path = os.path.abspath('hosted_files/image_1.jpg')
            # with open(file_path, 'rb') as file:
            #     file_data = file.read()
            with open('hosted_files/image_1.jpg', 'rb') as file:
                file_data = file.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpg')
            self.send_header('Content-Length', len(file_data))
            self.send_header('Content-Disposition', 'attachment; filename="image_1.jpg"')
            self.end_headers()
            # with open('hosted_files/image_1.png', 'rb') as file:
                # self.wfile.write(file.read())
            self.wfile.write(file_data)
        else:
            self.send_response(404)
PORT = 8002
FILESERVER_IP = '127.0.0.2'
# old ip - 127.0.0.3 / old port 8001

with socketserver.TCPServer((FILESERVER_IP, PORT), FileHandler) as httpd:
    print("Server started on ip ", FILESERVER_IP)
    print("Server started on port", PORT)
    

    httpd.serve_forever()
