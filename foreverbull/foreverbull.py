import importlib
import logging
import signal
import sys
import threading
from multiprocessing import Queue

import foreverbull_core
from foreverbull_core.broker import Broker
from foreverbull_core.models.finance import Order
from foreverbull_core.models.socket import Response
from foreverbull_core.models.worker import WorkerConfig
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout

from foreverbull.input_parser import InputParser
from foreverbull.worker.worker import Worker


class InputError(Exception):
    pass


class Foreverbull(threading.Thread):
    _routes = {}

    def __init__(self):
        self.broker = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers = []
        self.executors = 1
        threading.Thread.__init__(self)

    @staticmethod
    def on(msg_type):
        def decorator(t):
            Foreverbull._routes[msg_type] = t
            return t

        return decorator

    def _setup_worker(self, config_file):
        if config_file:
            try:
                self.logger.info("Importing: ", config_file)
                importlib.import_module(config_file.split(".py")[0])
            except ModuleNotFoundError as e:
                raise InputError(str(e))
        if not len(self._routes):  
            raise InputError("Neither route or input module found")

    def run(self):
        self.logger.info("Starting instance")
        config = InputParser().parse_input(sys.argv[1:])
        if not config:
            return
        if not len(self._routes):
            self._setup_worker(config.file)
        self.broker = Broker(config.broker_url, config.service_id, config.instance_id, config.local_host)
        self.executors = config.executors
        self.broker.mark_as_online()
        self.loop_over_socket(self.broker.socket)
        self.broker.mark_as_offline()
        self.stop()

    def stop(self):
        self.logger.info("Stopping instance")
        self._worker_requests.put(None)
        for worker in self._workers:
            worker.stop()
            worker.join()
        if self.broker:
            self.broker.socket.close()

    def loop_over_socket(self, socket):
        while True:
            try:
                self.logger.debug("waiting for socket")
                message = socket.recv()
                rsp = self._process_request(message)
                socket.send(rsp)
            except SocketTimeout:
                self.logger.debug("timeout")
                pass
            except SocketClosed:
                self.logger.debug("socket closed")
                return

    def _process_request(self, request):
        self.logger.debug("processing task: ", request.task)
        rsp = Response(task=request.task)
        try:
            if request.task == "backtest_completed":
                rsp.data = self._backtest_completed()
            elif request.task == "day_completed":
                rsp.data = self._day_completed()
            elif request.task == "configure":
                rsp.data = self._configure(request.data)
            elif request.task == "stock_data":
                rsp.data = self._stock_data(request.data)
            else:
                pass
        except Exception as e:
            self.logger.error("got unsupported task: ", request.task)
            rsp.error = repr(e)
        return rsp

    def _backtest_completed(self):
        self._worker_requests.put(None)
        for w in self._workers:
            w.join()
        return foreverbull_core.models.socket.Response(task="backtest_completed")

    def _day_completed(self):
        return foreverbull_core.models.socket.Response(task="day_completed")

    def _configure(self, data):
        configuration = WorkerConfig(**data)
        for _ in range(self.executors):
            w = Worker(self._worker_requests, self._worker_responses, configuration, **self._routes)
            w.start()
            self._workers.append(w)
        return foreverbull_core.models.socket.Response(task="configure")

    def _stock_data(self, message):
        self._worker_requests.put(message)
        rsp = None
        try:
            rsp = self._worker_responses.get(block=True, timeout=5)
        except Exception as e:
            self.logger.warning("exception when processing from worker: ", repr(e))
            pass
        if rsp is not None and type(rsp) is not Order:
            self.logger.error("unexpected response from worker: ", repr(rsp))
            raise Exception("unexpected response from worker: ", repr(rsp))
        return rsp
