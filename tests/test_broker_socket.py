from foreverbull.broker.socket.socket import Closed, NanomsgSocket, SocketClient, Timeout
import socket
from foreverbull.broker.socket.models import Configuration, Request, Response
import pynng
import pytest


@pytest.fixture(scope="function")
def local_requester():
    socket = None

    def setup(url):
        nonlocal socket
        socket = pynng.Req0(dial=url)
        return socket

    yield setup


@pytest.fixture(scope="function")
def local_replier():
    socket = pynng.Socket

    def setup(url):
        nonlocal socket
        socket = pynng.Rep0(listen=url)
        return socket

    yield setup


def test_configuration():
    assert Configuration.schema()["required"] == ["socket_type"]
    c = Configuration(socket_type="demo")
    expected = {
        "socket_type": "demo",
        "host": socket.gethostname(),
        "port": 0,
        "listen": True,
        "recv_timeout": 5000,
        "send_timeout": 5000,
    }
    assert c.dict() == expected


def test_request_model():
    assert Request.schema()["required"] == ["task"]
    r = Request(task="demo", data={"demo": "data"})
    expected = {"task": "demo", "data": {"demo": "data"}}
    assert r.dict() == expected
    assert r.dump() == b'{"task": "demo", "data": {"demo": "data"}}'


def test_response_model():
    assert Response.schema()["required"] == ["task"]
    r = Response(task="demo", error=repr(Exception("no work")), data={"response": "data"})
    expected = {"task": "demo", "error": repr(Exception("no work")), "data": {"response": "data"}}
    assert r.dict() == expected


def test_socket_client(local_requester):
    sc = SocketClient("127.0.0.1")
    lr = local_requester(sc._socket.url())

    expected = Request(task="demo", data={"demo": "data"})
    lr.send(expected.dump())
    reply = sc.recv()
    assert reply == expected

    expected = Response(task="demo", error=repr(Exception("no work")), data={"response": "data"})
    reply = sc.send(expected)
    reply = lr.recv()
    assert Response.load(reply) == expected


def test_nanomsg_socket():
    config = Configuration(socket_type="requester", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)
    assert len(sock._socket.dialers) == 0
    assert len(sock._socket.listeners) == 1
    assert sock.url() == "tcp://127.0.0.1:1337"
    sock.close()

    config = Configuration(socket_type="replier", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)
    assert len(sock._socket.dialers) == 0
    assert len(sock._socket.listeners) == 1
    sock.close()


def test_nanomsg_socket_recv_senc(local_requester):
    config = Configuration(socket_type="replier", host="127.0.0.1", port=1337)
    sock = NanomsgSocket(config)

    lr = local_requester(sock.url())

    lr.send(b"hello")
    assert sock.recv() == b"hello"

    sock._socket.recv_timeout = 10
    with pytest.raises(Timeout):
        sock.recv()

    sock.close()
    with pytest.raises(Closed):
        sock.recv()

    lr.close()
