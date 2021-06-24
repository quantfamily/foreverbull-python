import os

from foreverbull.broker.http import http
from foreverbull.broker.socket import socket


class Broker:
    def __init__(self, host):
        self._host = host
        self.http = http.HTTPClient(host)
        self.socket = socket.SocketClient(host)

    def local_connection(self):
        return {
            "host": os.environ.get("HOST_ADDRESS", "127.0.0.1"),
            "port": self.socket.config.port,
            "online": True,
            "listen": True,
        }
