from foreverbull.worker.exceptions import WorkerException
from foreverbull.broker.data.data import Database
from multiprocessing import Process


class Worker(Process):
    def __init__(self, queue, session_id, database, **routes):
        super(Worker, self).__init__()
        self._queue = queue
        self._routes = routes
        self.session_id = session_id
        self.database = Database(session_id=session_id, db_conf=database)

    def _process_request(self, request):
        if request.task == "eod_stock_data":
            self._routes["stock_data"](request.data, self.database)

    def run(self):
        self.database.connect()
        while True:
            try:
                message = self._queue.get()
                if message is None or message == "None":
                    self._queue.put(None)
                    return
                self._process_request(message)
            except Exception as e:
                raise WorkerException(repr(e))
