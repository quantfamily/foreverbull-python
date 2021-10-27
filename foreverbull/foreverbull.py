import importlib
import logging
import sys
import threading
import time
from multiprocessing import Queue

from foreverbull_core.broker import Broker
from foreverbull_core.models.finance import EndOfDay, Order
from foreverbull_core.models.worker import Instance
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter

from foreverbull.input_parser import InputParser
from foreverbull.worker.worker import Worker


class InputError(Exception):
    pass


class Foreverbull(threading.Thread):
    _worker_routes = {}

    def __init__(self):
        self.broker = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers = []
        self.executors = 1
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

    def _setup_worker(self, config_file):
        if config_file:
            try:
                self.logger.info(f"Importing: {config_file}")
                importlib.import_module(config_file.split(".py")[0])
            except ModuleNotFoundError as e:
                raise InputError(str(e))
        if not len(self._worker_routes):
            raise InputError("Neither route or input module found")

    def run(self):
        self.logger.info("Starting instance")
        config = InputParser().parse_input(sys.argv[1:])
        if config.instance is None and config.backtest_id is None:
            return
        self.broker = Broker(config.broker_url, config.local_host)
        runner = threading.Thread(target=self.loop_over_socket)
        runner.start()

        self.executors = config.executors
        if not len(self._worker_routes):
            print("import: ", config.file)
            self._setup_worker(config.file)

        if config.instance:
            self.broker.mark_as_online(config.instance)
        elif config.backtest_id is not None:
            self.broker.run_test_run(config.backtest_id)

        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False

        self.stop()

    def stop(self):
        self.logger.info("Stopping instance")
        self._worker_requests.put(None)
        for worker in self._workers:
            worker.join()
        if self.broker:
            self.broker.socket.close()

    def loop_over_socket(self):
        while True:
            try:
                message = self.broker.socket.recv()
                rsp = self._routes(message)
                self.broker.socket.send(rsp)
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

    def _backtest_completed(self):
        self._worker_requests.put(None)
        for w in self._workers:
            w.join()
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
            pass
        if rsp is not None and type(rsp) is not Order:
            self.logger.error("unexpected response from worker: %s", repr(rsp))
            raise Exception("unexpected response from worker: %s", repr(rsp))
        return rsp
