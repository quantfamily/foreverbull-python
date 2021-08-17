from multiprocessing import Queue

from foreverbull_core.models.finance import Asset, Order
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Parameter, WorkerConfig

from foreverbull import Foreverbull
from foreverbull.worker import Worker


def test_sockets(mocker):
    fb = Foreverbull(None)

    message = Request(task="configure")
    mocker.patch.object(fb, "_configure", return_value="Works!")
    assert fb._process(message) == "Works!"


def test_worker():
    worker_req = Queue()
    worker_rsp = Queue()
    worker_config = WorkerConfig(session_id="123")

    def on_message(data, *any):
        assert data == {"hello": "worker"}
        return {"hello": "from worker"}

    worker = Worker(worker_req, worker_rsp, worker_config, stock_data=on_message)
    req = Request(task="stock_data", data={"hello": "worker"})
    rsp = worker._process_request(req)
    assert rsp == {"hello": "from worker"}


def take_stock_data(data, dataframe, ma_high, ma_low):
    assert data == {"welcome": "home"}
    assert ma_high == 64
    assert ma_low == 16
    asset = Asset(symbol="TSLA", exchange="QUANDL")
    return Order(asset=asset, amount=10)


def test_route():
    fb = Foreverbull(None)

    Foreverbull._routes["stock_data"] = take_stock_data

    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = WorkerConfig(session_id="123", parameters=[param1, param2])
    req = Request(task="configure", data=worker_config)
    rsp = fb._process(req)

    assert rsp.error is None
    assert len(fb._workers) == 1
    assert len(fb._routes) == 1

    req = Request(task="stock_data", data={"welcome": "home"})
    rsp = fb._process(req)
    assert rsp.error is None
    assert rsp.data is not None
    fb._backtest_completed()
