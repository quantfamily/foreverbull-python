from pathlib import Path

import pytest
from foreverbull.foreverbull import Broker, Foreverbull, InputError
from foreverbull.input_parser import InputParser
from foreverbull_core.http.service import Service
from foreverbull_core.models.service import Instance
from foreverbull_core.models.worker import Instance as WorkerInstance
from pytest_mock import MockerFixture


def test_on():
    route = Foreverbull.on("stock_data")
    route("hello")
    assert "stock_data" in Foreverbull._worker_routes
    assert Foreverbull._worker_routes["stock_data"] == "hello"


def test_setup_worker():
    pyfile = """
from foreverbull import Foreverbull

@Foreverbull.on("magic_data")
def magic_func(*args):
    pass
    """

    demo_file = Path("demo.py")
    with open(demo_file.name, "w") as fw:
        fw.write(pyfile)
    fb = Foreverbull()
    fb._setup_worker(demo_file.name)

    assert "magic_data" in Foreverbull._worker_routes
    demo_file.unlink()
    Foreverbull._worker_routes = {}


def test_setup_worker_negative():
    fb = Foreverbull()
    with pytest.raises(InputError):
        fb._setup_worker("non_file.py")

    with pytest.raises(InputError):
        fb._setup_worker(False)


def test_configure_and_completed():
    config = WorkerInstance(session_id="session-id")
    fb = Foreverbull()
    Foreverbull._worker_routes = {}
    fb.executors = 2
    fb._configure(config)
    assert len(fb._workers) == 2
    fb._backtest_completed()
    assert len(fb._workers) == 0


def test_start_stop_as_instance(mocker: MockerFixture):
    input = InputParser()
    input.instance = Instance(service_id="service-id", id="instance-id")
    input.broker_url = "broker"
    input.local_host = "127.0.0.1"
    mocker.patch.object(Foreverbull, "_parse_input", return_value=input)
    mocker.patch.object(Service, "update_instance")
    mocker.patch.object(Foreverbull, "_setup_worker")
    fb = Foreverbull()
    fb.start()
    fb.stop()
    fb.join()


def test_start_stop_as_run(mocker: MockerFixture):
    input = InputParser()
    input.backtest_id = "backtest_id"
    mocker.patch.object(Foreverbull, "_parse_input", return_value=input)
    mocker.patch.object(Broker, "run_test_run")
    mocker.patch.object(Foreverbull, "_setup_worker")
    fb = Foreverbull()

    fb.start()
    fb.stop()
    fb.join()
