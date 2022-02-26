import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from foreverbull.worker.worker import WorkerHandler
from foreverbull_core.models.finance import EndOfDay
from foreverbull_core.models.socket import Request
from foreverbull_core.models.worker import Instance
from foreverbull_core.socket.client import ContextClient, SocketClient
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter


class Foreverbull(threading.Thread):
    _worker_routes = {}

    def __init__(self, socket: SocketClient = None, executors: int = 1):
        self.socket = socket
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers: list[WorkerHandler] = []
        self.executors = executors
        self._routes = MessageRouter()
        self._routes.add_route(self.stop, "backtest_completed")
        self._routes.add_route(self._configure, "configure", Instance)
        self._routes.add_route(self._stock_data, "stock_data", EndOfDay)
        self._request_thread: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
        threading.Thread.__init__(self)

    @staticmethod
    def on(msg_type):
        def decorator(t):
            Foreverbull._worker_routes[msg_type] = t
            return t

        return decorator

    def run(self):
        self.running = True
        self.logger.info("Starting instance")
        while self.running:
            try:
                context_socket = self.socket.new_context()
                request = context_socket.recv()
                self._request_thread.submit(self._process_request, context_socket, request)
            except (SocketClosed, SocketTimeout):
                self.logger.info("main socket closed, exiting")
                return
        self.socket.close()
        self.logger.info("exiting")

    def _process_request(self, socket: ContextClient, request: Request):
        try:
            self.logger.debug(f"recieved task: {request.task}")
            response = self._routes(request)
            socket.send(response)
            self.logger.debug(f"reply sent for task: {response.task}")
            socket.close()
        except (SocketTimeout, SocketClosed) as exc:
            self.logger.warning(f"Unable to process context socket: {exc}")
            pass
        except Exception as exc:
            self.logger.error("unknown excetion when processing context socket")
            self.logger.exception(exc)

    def stop(self):
        self.logger.info("Stopping instance")
        self.running = False
        for worker in self._workers:
            worker.stop()
        self._workers = []

    def _configure(self, instance_configuration: Instance):
        for _ in range(self.executors):
            w = WorkerHandler(instance_configuration, **self._worker_routes)
            self._workers.append(w)
        return

    def _stock_data(self, message: EndOfDay):
        for worker in self._workers:
            if worker.locked():
                continue
            if worker.acquire():
                break
        else:
            raise Exception("workers are not initialized")

        try:
            worker.process(message)
        except Exception as exc:
            self.logger.error("Error processing to worker")
            self.logger.exception(exc)

        worker.release()
