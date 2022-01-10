import logging
import threading
from multiprocessing import Queue

from foreverbull.worker.worker import Worker
from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull_core.models.worker import Instance
from foreverbull_core.socket.client import SocketClient
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
        self._workers = []
        self.executors = executors
        self._routes = MessageRouter()
        self._routes.add_route(self._backtest_completed, "backtest_completed")
        self._routes.add_route(self._configure, "configure", Instance)
        self._routes.add_route(self._stock_data, "stock_data", EndOfDay)
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
                message = self.socket.recv()
                rsp = self._routes(message)
                self.logger.debug(f"recieved task: {rsp.task}")
                self.socket.send(rsp)
                self.logger.debug(f"reply sent for task: {rsp.task}")
            except SocketTimeout:
                self.logger.debug("timeout")
                pass
            except SocketClosed:
                self.logger.info("socket closed")
                return
            except Exception as e:
                self.logger.error("Unknown exception on socket")
                self.logger.exception(e)
                return
        self.socket.close()
        self.logger.info("exiting")

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

    def _configure(self, config: Instance):
        for _ in range(self.executors):
            w = Worker(self._worker_requests, self._worker_responses, config, **self._worker_routes)
            w.start()
            self._workers.append(w)
        return

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
