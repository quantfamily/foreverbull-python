from datetime import datetime

import pytest
from foreverbull.foreverbull import Foreverbull
from foreverbull.input_parser import InputParser
from foreverbull_core.models.finance import Asset, EndOfDay
from foreverbull_core.models.socket import Request, SocketConfig, SocketType
from foreverbull_core.models.worker import Instance, Parameter
from foreverbull_core.socket.client import SocketClient


def on_message(data, dataframe, ma_high, ma_low):
    return


def test_simple_simulation_without_socket():
    input_parser = InputParser()
    input_parser.algo_file = None
    input_parser.broker = input_parser.get_broker()
    input_parser.service_instance = input_parser.get_service_instance(input_parser.broker)
    fb = Foreverbull(input_parser.broker.socket, 1)
    fb._worker_routes["stock_data"] = on_message

    fb.start()

    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = Instance(session_id="123", parameters=[param1, param2])
    req = Request(task="configure", data=worker_config)
    rsp = fb._routes(req)
    assert rsp.error is None
    # stock_data
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")
    eod = EndOfDay(
        asset=a,
        date=datetime.now(),
        last_traded=datetime.now(),
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
    )
    for _ in range(10):
        req = Request(task="stock_data", data=eod)
        rsp = fb._routes(req)
        assert rsp.error is None
    # taredown
    fb.stop()
    fb.join()


@pytest.fixture
def get_requester():
    def inner(host: str, port: int) -> SocketClient:
        socket = SocketClient(
            SocketConfig(host=host, port=port, listen=False, dial=True, socket_type=SocketType.REQUESTER)
        )
        return socket

    return inner


def test_simulation_with_socket(get_requester):
    input_parser = InputParser()
    input_parser.algo_file = None
    input_parser.broker = input_parser.get_broker()
    input_parser.service_instance = input_parser.get_service_instance(input_parser.broker)
    fb = Foreverbull(input_parser.broker.socket, 1)
    fb._worker_routes["stock_data"] = on_message

    fb.start()

    socket = get_requester(input_parser.broker.socket_config.host, input_parser.broker.socket_config.port)

    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = Instance(session_id="123", parameters=[param1, param2])
    req = Request(task="configure", data=worker_config)

    context_socket = socket.new_context()
    context_socket.send(req)
    rsp = context_socket.recv()
    assert rsp.task == "configure"

    # stock_data
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")
    eod = EndOfDay(
        asset=a,
        date=datetime.now(),
        last_traded=datetime.now(),
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
    )
    for _ in range(10):
        req = Request(task="stock_data", data=eod)
        context_socket = socket.new_context()
        context_socket.send(req)
        rsp = context_socket.recv()
        assert rsp.task == "stock_data"
    # taredown
    fb.stop()
    fb.join()
