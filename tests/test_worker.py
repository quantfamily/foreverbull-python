from foreverbull.worker.worker import Worker
from multiprocessing import Queue
from foreverbull.broker.socket.models import Request


def test_worker():
    # TODO: Have worker return stuff to verify
    queue = Queue()

    def on_update(request, database):
        pass

    worker = Worker(queue, 123, None, **{"stock_data": on_update})

    req = Request(task="stock_data", data={"test": "abc"})

    worker._process_request(req)


def test_worker_process():
    queue = Queue()
    worker = Worker(queue, 123, None)
    worker.start()
    queue.put(None)
    worker.join()
