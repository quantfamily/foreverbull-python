import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from foreverbull.worker.worker import WorkerHandler
from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull_core.models.worker import Instance
from foreverbull_core.socket.client import ContextClient, SocketClient
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter


class Request(threading.Thread):
    def __init__(self, context_socket):
        self.context_socket = context_socket

    def run(self):
        message = self.context_socket.recv()
        rsp = self._routes(message)
        self.logger.debug(f"recieved task: {rsp.task}")
        self.context_socket.send(rsp)
        self.logger.debug(f"reply sent for task: {rsp.task}")
        self.context_socket.close()

    def _stock_data(self, message: EndOfDay):
        if len(self._workers) == 0:
            raise Exception("workers are not initialized")
        self._worker_requests.put(message)
        rsp = None
        try:
            rsp = self._worker_responses.get(block=True, timeout=5)
        except Exception as e:
            self.logger.warning("exception when processing from worker: %s", repr(e))
            self.logger.exception(e)
            pass
        if rsp is not None and type(rsp) is not Order:
            self.logger.error("unexpected response from worker: %s", repr(rsp))
            raise Exception("unexpected response from worker: %s", repr(rsp))
        return rsp


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
        self._routes.add_route(self._backtest_completed, "backtest_completed")
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
                self._request_thread.submit(self._process, context_socket)
            except SocketClosed:
                self.logger.info("main socket closed, exiting")
                return
        self.socket.close()
        self.logger.info("exiting")

    def _process(self, socket: ContextClient):
        try:
            message = socket.recv()
            rsp = self._routes(message)
            self.logger.debug(f"recieved task: {rsp.task}")
            socket.send(rsp)
            self.logger.debug(f"reply sent for task: {rsp.task}")
            socket.close()
        except (SocketTimeout, SocketClosed) as exc:
            self.logger.error("Unable to process context socket")
            self.logger.exception(exc)
        except Exception as exc:
            self.logger.error("unknown excetion when processing context socket")
            self.logger.exception(exc)

    def stop(self):
        self.logger.info("Stopping instance")
        self.running = False
        self._worker_requests.put(None)
        for worker in self._workers:
            worker.join()

    def _backtest_completed(self):
        self._worker_requests.put(None)
        for w in self._workers:
            w.join()
        self._workers = []
        self.running = False
        return

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

        try:
            worker.process(message)
        except Exception as exc:
            self.logger.error("Error processing to worker")
            self.logger.exception(exc)

        worker.release()
