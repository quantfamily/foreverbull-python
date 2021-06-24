import json
import os
import socket
from typing import Optional

from pydantic import BaseModel


class Configuration(BaseModel):
    socket_type: str
    host: str = os.getenv("HOSTNAME", socket.gethostname())
    port: int = 0
    listen: bool = True
    recv_timeout: int = 5000
    send_timeout: int = 5000


class Request(BaseModel):
    task: str
    data: Optional[dict] = None

    @classmethod
    def load(cls, data):
        loaded = json.loads(data.decode())
        return cls(**loaded)

    def dump(self):
        return self.json().encode()


class Response(BaseModel):
    task: str
    error: Optional[str] = None
    data: Optional[dict] = None

    @classmethod
    def load(cls, data):
        loaded = json.loads(data.decode())
        return cls(**loaded)

    def dump(self):
        return self.json().encode()
