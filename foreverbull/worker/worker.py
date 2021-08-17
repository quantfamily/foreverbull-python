from multiprocessing import Process
from multiprocessing.queues import Queue

from foreverbull_core.models.worker import Database, WorkerConfig

from foreverbull.worker.exceptions import WorkerException


class Worker(Process):
    def __init__(self, worker_requests: Queue, worker_responses: Queue, configuration: WorkerConfig, **routes):
        super(Worker, self).__init__()
        self._worker_requests = worker_requests
        self._worker_responses = worker_responses
        self._routes = routes
        self.session_id = configuration.session_id
        self.database = Database(session_id=configuration.session_id, db_conf=configuration.database)
        self.parameters = {}
        if configuration.parameters is None:
            return
        for parameter in configuration.parameters:
            self.parameters[parameter.key] = parameter.value

    def _process_request(self, data):
        return self._routes["stock_data"](data, self.database, **self.parameters)

    def run(self):
        self.database.connect()
        while True:
            try:
                request = self._worker_requests.get()
                if request is None:
                    self._worker_requests.put(None)
                    return
                response = self._process_request(request)
                self._worker_responses.put(response)
            except Exception as e:
                raise WorkerException(repr(e))

    def stop(self):
        return True
