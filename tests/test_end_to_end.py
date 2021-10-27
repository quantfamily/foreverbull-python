from datetime import datetime


import pytest
from foreverbull_core.http.service import Service
from foreverbull_core.models.finance import Asset, EndOfDay
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Config, Parameter

from foreverbull.foreverbull import Foreverbull
from foreverbull.input_parser import InputParser


def on_message(data, dataframe, ma_high, ma_low):
    pass


@pytest.mark.skip(reason="find better way for end to end")
def test_simple_simulation(mocker):
    input_parser = InputParser()
    input_parser.service_id = "service_id"
    input_parser.instance_id = "instance_id"
    input_parser.broker_url = "foreverbull.com"
    input_parser.local_host = "127.0.0.1"
    input_parser.file = None
    print("hello", flush=True)

    # setup
    fb = Foreverbull()
    fb._worker_routes["stock_data"] = on_message

    mocker.patch.object(InputParser, "parse_input", return_value=input_parser)
    mocker.patch.object(Service, "update_instance", return_value=True)
    print("STARTING", flush=True)
    fb.start()

    print("STARTED", flush=True)

    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = Config(session_id="123", parameters=[param1, param2])
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
    for _ in range(200):
        req = Request(task="stock_data", data=eod)
        rsp = fb._routes(req)
        assert rsp.error is None
        assert rsp.data is None
    # taredown
    fb._backtest_completed()
    fb.join()
