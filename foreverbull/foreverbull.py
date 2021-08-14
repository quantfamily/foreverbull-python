import os
import threading
from multiprocessing import Queue

import foreverbull_core
from foreverbull_core.models.finance import Order
from foreverbull_core.models.socket import Response
from foreverbull_core.models.worker import WorkerConfig
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout

from foreverbull_core.broker import Broker
from foreverbull.worker.worker import Worker


class Foreverbull(threading.Thread):
    _routes = {}

    def __init__(self, broker, executors=1):
        self.broker = broker
        self.running = False
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers = []
        self.executors = executors
        threading.Thread.__init__(self)

    @staticmethod
    def on(msg_type):
        print("HEREE:", msg_type)

        def decorator(t):
            print("Addingg")
            Foreverbull._routes[msg_type] = t
            return t

        return decorator

    def run(self):
        while True:
            try:
                message = self.broker.socket.recv()
                rsp = self._process(message)
                self.broker.socket.send(rsp)
            except SocketTimeout:
                pass
            except SocketClosed:
                return

    def stop(self):
        self.broker.socket.close()

    def _process(self, request):
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
            print("Timeout: ", repr(e))
        if rsp is not None and type(rsp) is not Order:
            print(type(rsp))
            raise Exception("unexpected response from worker: ", str(rsp))
        return rsp
