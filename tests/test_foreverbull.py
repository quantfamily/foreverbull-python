from pathlib import Path

import pytest
from foreverbull_core.models.worker import Instance

from foreverbull import Foreverbull
from foreverbull.foreverbull import InputError


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


def test_setup_worker_negative():
    fb = Foreverbull()

    with pytest.raises(InputError):
        fb._setup_worker("non_file.py")


def test_configure_and_completed():
    config = Instance(session_id="123")
    fb = Foreverbull()
    Foreverbull._worker_routes = {}
    fb.executors = 2
    fb._configure(config)
    assert len(fb._workers) == 2
    fb._backtest_completed()
