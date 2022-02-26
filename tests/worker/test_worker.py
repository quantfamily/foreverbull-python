from multiprocessing import Queue

from foreverbull.worker.worker import Worker, WorkerHandler
from foreverbull_core.models.finance import Order
from foreverbull_core.models.worker import Instance, Parameter


def just_return_order_amount_10(*_):
    return Order(amount=10)


def test_setup_parameters_is_None():
    req = Queue()
    rsp = Queue()
    worker_conf = Instance(session_id=123)
    worker = Worker(req, rsp, worker_conf)

    assert len(worker.parameters) == 0


def test_setup_parameters():
    req = Queue()
    rsp = Queue()
    param1 = Parameter(key="key1", value=22, default=11)
    worker_conf = Instance(session_id=123, parameters=[param1])
    worker = Worker(req, rsp, worker_conf)

    assert len(worker.parameters) == 1


def test_worker_process_request():
    order_to_return = Order(amount=1337)

    def on_update(request, _):
        assert request == {"stock": "data"}
        return order_to_return

    worker_conf = Instance(session_id=123)
    worker = Worker(None, None, worker_conf, **{"stock_data": on_update})

    assert worker._process_request({"stock": "data"}) == order_to_return


def test_worker_process_start_stop():
    queue = Queue()
    worker_conf = Instance(session_id=123)
    worker = Worker(queue, 123, worker_conf)
    worker.start()
    queue.put(None)
    worker.join()


def test_worker_handler_lock():
    worker_conf = Instance(session_id=123)
    wh = WorkerHandler(worker_conf)

    # Check if locked after init, acquire and make sure its locked
    assert wh.locked() is False
    assert wh.acquire() is True
    assert wh.locked() is True

    # second acquire should not work
    assert wh.acquire() is False

    # release and check its not locked anymore
    wh.release()
    assert wh.locked() is False
    wh.stop()


def test_worker_handler():
    request = "something that the worker will never read anyway"
    response = Order(amount=10)

    worker_conf = Instance(session_id=123)
    wh = WorkerHandler(worker_conf, stock_data=just_return_order_amount_10)

    assert wh.locked() is False
    wh.acquire(False, -1)

    result = wh.process(request)

    wh.release()
    wh.stop()

    assert result == response
