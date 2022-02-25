from multiprocessing import Queue
from time import sleep

from foreverbull.worker.worker import Worker, WorkerHandler
from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Instance
from pytest_mock import MockerFixture


def sample_task(data, *args):
    # assert data == {"to": "sample_task"}
    print("GOT IT", flush=True)
    return Order(amount=10)


def test_worker():
    # TODO: Have worker return stuff to verify
    req_queue = Queue()
    rsp_queue = Queue()

    def on_update(request, database):
        pass

    worker_conf = Instance(session_id=123)
    worker = Worker(req_queue, rsp_queue, worker_conf, **{"stock_data": on_update})

    req = Request(task="stock_data", data={"test": "abc"})

    worker._process_request(req)


def test_worker_process_start_stop():
    queue = Queue()
    worker_conf = Instance(session_id=123)
    worker = Worker(queue, 123, worker_conf)
    worker.start()
    queue.put(None)
    worker.join()


def test_worker_second():
    worker_req = Queue()
    worker_rsp = Queue()
    worker_config = Instance(session_id="123")

    def on_message(data, *any):
        assert data == {"hello": "worker"}
        return {"hello": "from worker"}

    worker = Worker(worker_req, worker_rsp, worker_config, stock_data=on_message)
    req = {"hello": "worker"}
    rsp = {"hello": "from worker"}
    assert worker._process_request(req) == rsp


def test_worker_handler():
    request = {"to": "sample_task"}
    response = Order(amount=10)

    worker_conf = Instance(session_id=123)
    wh = WorkerHandler(worker_conf, stock_data=sample_task)

    assert wh.locked() == False
    wh.acquire(False, -1)

    result = wh.process(request)

    wh.release()
    wh.stop()

    assert result == response
