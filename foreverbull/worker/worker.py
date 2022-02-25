import logging
import threading
from multiprocessing import Process, Queue

from foreverbull.data import Database
from foreverbull.worker.exceptions import WorkerException
from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull_core.models.worker import Instance, Parameter


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
        if configuration.parameters:
            self.logger.debug("setting up parameters")
            self._setup_parameters(configuration.parameters)
        self.logger.info("worker configured correctly")

    def _setup_parameters(self, *parameters: Parameter):
        for parameter in parameters:
            self.logger.debug("Setting %s to %s", parameter.key, parameter.value)
            self.parameters[parameter.key] = parameter.value

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
                    return
                self.logger.debug("processing request")
                response = self._process_request(request)
                self.logger.debug("processing done")
                self._worker_responses.put(response)
            except Exception as e:
                self.logger.exception(repr(e))
                raise WorkerException(repr(e))


class WorkerHandler:
    def __init__(self, configuration: Instance, **routes):
        self.logger = logging.getLogger(__name__)
        self._reqeust = Queue()
        self._response = Queue()
        self._worker = Worker(self._reqeust, self._response, configuration, **routes)
        self._worker.start()
        self._lock = threading.Lock()

    def locked(self) -> bool:
        return self._lock.locked()

    def acquire(self, blocking: bool, timeout: float) -> bool:
        return self._lock.acquire(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        return self._lock.release()

    def process(self, message: EndOfDay):
        self._reqeust.put(message)
        rsp = None
        try:
            rsp = self._response.get(block=True, timeout=5)
        except Exception as e:
            self.logger.warning("exception when processing from worker: %s", repr(e))
            self.logger.exception(e)
            pass
        if rsp is not None and type(rsp) is not Order:
            self.logger.error("unexpected response from worker: %s", repr(rsp))
            raise Exception("unexpected response from worker: %s", repr(rsp))
        return rsp

    def stop(self):
        self._reqeust.put(None)
        self._worker.join()
