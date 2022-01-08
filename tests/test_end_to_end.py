from datetime import datetime

from foreverbull.foreverbull import Foreverbull
from foreverbull.input_parser import InputParser
from foreverbull_core.http.service import Service
from foreverbull_core.models.finance import Asset, EndOfDay
from foreverbull_core.models.service import Instance as ServiceInstance
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Instance, Parameter


def on_message(data, dataframe, ma_high, ma_low):
    return


def test_simple_simulation(mocker):
    input_parser = InputParser()
    input_parser.instance = ServiceInstance(service_id="service-id", id="instance-id")
    input_parser.broker_url = "foreverbull.com"
    input_parser.local_host = "127.0.0.1"
    input_parser.file = None
    fb = Foreverbull()
    fb._worker_routes["stock_data"] = on_message

    mocker.patch.object(InputParser, "parse_input", return_value=input_parser)
    mocker.patch.object(Service, "update_instance", return_value=True)
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
    fb._backtest_completed()
    fb.join()
