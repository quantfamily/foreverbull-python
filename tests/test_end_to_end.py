from foreverbull_core.models.socket import Request, Response
from foreverbull_core.models.worker import Parameter, WorkerConfig
from foreverbull.foreverbull import Foreverbull
from foreverbull_core.broker import Broker
from foreverbull.input_parser import InputParser
import pytest
from unittest.mock import create_autospec
from unittest import mock
import pytest_mock
from foreverbull_core.http.service import Service
import time
@pytest.mark.skip()
def test_message_simulation(sample_data, session):
    local_session = session()

    for pair in sample_data:
        _ = local_session.send(pair["req"].dump())
        local_session.recv()


def on_message(data, dataframe, ma_high, ma_low):
    print("high", ma_high)
    pass

def test_simple_simulation():
    input_parser = InputParser()
    input_parser.service_id = "service_id"
    input_parser.instance_id = "instance_id"
    input_parser.broker_url = "foreverbull.com"
    input_parser.local_host = "127.0.0.1"


    ## setup
    fb = Foreverbull()
    fb._routes['stock_data'] = on_message
    #fb._setup_worker(None)
    ## configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = WorkerConfig(session_id="123", parameters=[param1, param2])
    req = Request(task="configure", data=worker_config)
    rsp = fb._process_request(req)
    assert rsp.error is None
    ## stock_data
    req = Request(task="stock_data", data={"welcome": "home"})
    rsp = fb._process_request(req)
    ## taredown
    fb.stop()

def test_simple_simulation_2(mocker):
    input_parser = InputParser()
    input_parser.service_id = "service_id"
    input_parser.instance_id = "instance_id"
    input_parser.broker_url = "foreverbull.com"
    input_parser.local_host = "127.0.0.1"
    input_parser.file = None

    ## setup
    fb = Foreverbull()
    fb._routes['stock_data'] = on_message

    mocker.patch.object(InputParser, "parse_input", return_value=input_parser)
    mocker.patch.object(Service, "update_instance", return_value=True)
    fb.start()

    ## configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    worker_config = WorkerConfig(session_id="123", parameters=[param1, param2])
    req = Request(task="configure", data=worker_config)
    rsp = fb._process_request(req)
    assert rsp.error is None
    ## stock_data
    for _ in range(200):
        req = Request(task="stock_data", data={"welcome": "home"})
        rsp = fb._process_request(req)
        assert rsp.error is None
        assert rsp.data is None
    ## taredown
    fb.stop()
    fb.join()
