from multiprocessing import Queue

from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import WorkerConfig

from foreverbull.worker.worker import Worker


def test_worker():
    # TODO: Have worker return stuff to verify
    req_queue = Queue()
    rsp_queue = Queue()
    def on_update(request, database):
        pass

    worker_conf = WorkerConfig(session_id=123)
    worker = Worker(req_queue, rsp_queue, worker_conf, **{"stock_data": on_update})

    req = Request(task="stock_data", data={"test": "abc"})

    worker._process_request(req)


def test_worker_process():
    queue = Queue()
    worker_conf = WorkerConfig(session_id=123)
    worker = Worker(queue, 123, worker_conf)
    worker.start()
    queue.put(None)
    worker.join()
