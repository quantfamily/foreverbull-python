from multiprocessing import Queue

from foreverbull.worker.worker import Worker
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Instance


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
