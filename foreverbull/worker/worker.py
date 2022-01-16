import logging
from multiprocessing import Process
from multiprocessing.queues import Queue

from foreverbull.data import Database
from foreverbull.worker.exceptions import WorkerException
from foreverbull_core.models.worker import Instance


class Worker(Process):
    def __init__(self, worker_requests: Queue, worker_responses: Queue, configuration: Instance, **routes):
        super(Worker, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("setting up worker")
        self._worker_requests = worker_requests
        self._worker_responses = worker_responses
        self._routes = routes
        self.session_id = configuration.session_id
        self.logger.debug("setting up database connection")

        self.database = Database(session_id=configuration.session_id, db_conf=configuration.database)
        self.parameters = {}
        self.logger.debug("setting up parameters")
        if configuration.parameters is None:
            return
        for parameter in configuration.parameters:
            self.logger.debug("Setting %s to %s", parameter.key, parameter.value)
            self.parameters[parameter.key] = parameter.value
        self.logger.debug("worker configured correctly")

    def _process_request(self, data):
        self.logger.debug("sending request to worker")
        return self._routes["stock_data"](data, self.database, **self.parameters)

    def run(self):
        self.database.connect()
        while True:
            try:
                request = self._worker_requests.get()
                self.logger.debug("recieved request")
                if request is None:
                    self.logger.info("request is None, shutting downn")
                    self._worker_requests.put(None)
                    return
                self.logger.debug("processing request")
                response = self._process_request(request)
                self.logger.debug("processing done")
                self._worker_responses.put(response)
            except Exception as e:
                self.logger.exception(repr(e))
                raise WorkerException(repr(e))
