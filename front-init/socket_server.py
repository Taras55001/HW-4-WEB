import socket
import json
from datetime import datetime
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent
UDP_SERVER_ADDRESS = ('localhost', 5000)


def save_data_to_json(timestamp, data_dict):
    file_path = BASE_DIR / 'storage' / 'data.json'
    if not file_path.exists():
        with open(file_path, 'w') as f:
            json.dump({}, f)
    with open(file_path, 'r+') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}
        data[timestamp] = data_dict
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(UDP_SERVER_ADDRESS)
    while True:
        data, address = sock.recvfrom(1024)
        data_dict = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().isoformat()
        save_data_to_json(timestamp, data_dict)


if __name__ == '__main__':
    run_socket_server()

