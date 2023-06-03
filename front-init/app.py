from http.server import HTTPServer, BaseHTTPRequestHandler
import pathlib
import urllib.parse
import mimetypes
import json
import socket
from datetime import datetime
from threading import Thread

BASE_DIR = pathlib.Path(__file__).resolve().parent
UDP_SERVER_ADDRESS = ('localhost', 3000)

class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        path = url_parts.path
        
        if path == '/':
            self.send_html('index.html')
        elif path == '/message.html':
            self.send_html('message.html')
        elif path == '/style.css':
            self.send_static('style.css')
        elif path == '/logo.png':
            self.send_static('logo.png')
        else:
            file = BASE_DIR / path[1:]
            if file.exists():
                self.send_static(file)
            else:
                self.send_html('error.html', 404)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        data = urllib.parse.parse_qs(body)
        username = data.get('username', [''])[0]
        message = data.get('message', [''])[0]
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Message Sent!</h1></body></html>')
        self.send_data_to_socket_server(username, message)


    def send_data_to_socket_server(self, username, message):
        data = {
            'username': username,
            'message': message,
        }
        json_data = json.dumps(data).encode('utf-8')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json_data, UDP_SERVER_ADDRESS)

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
        
    def send_static(self, filename):
        self.send_response(200)
        mime_type, *rest = mimetypes.guess_type(filename)
        print(mime_type)
        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
        
class SocketServerThread(Thread):
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(UDP_SERVER_ADDRESS)
        while True:
            data, address = sock.recvfrom(1024)
            data_dict = json.loads(data.decode('utf-8'))
            timestamp = datetime.now().isoformat()
            self.save_data_to_json(timestamp, data_dict)

    def save_data_to_json(self, timestamp, data_dict):
        file_path = BASE_DIR / 'storage' / 'data.json'
        with open(file_path, 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
            data[timestamp] = data_dict
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        

def run_http_server():
    server_address = ('', 3000)
    http_server = HTTPServer(server_address, HttpRequestHandler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


def run_socket_server():
    socket_server_thread = SocketServerThread()
    socket_server_thread.start()


if __name__ == '__main__':
    thread1 = Thread(target=run_http_server)
    thread2 = Thread(target=run_socket_server)
    thread1.start()
    thread2.start()