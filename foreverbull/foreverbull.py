from foreverbull.broker.models import Initialization
import os
from multiprocessing import Queue
from threading import Thread

import foreverbull
from foreverbull.broker.broker import Broker
from foreverbull.worker.worker import Worker

from .models import Backtest as BacktestModel
from .models import Config, Container, Service, Session


class Foreverbull:
    _routes = {}

    def __init__(self, host=None, executors=1):
        self._host = os.environ.get("HOST", "127.0.0.1")
        self.broker = Broker(self._host)
        self.config = Config()
        self.backtest = BacktestModel(config=self.config)
        self.service = Service()
        self.container = Container()
        self.session = Session()
        self.running = False
        self._queue = Queue(maxsize=2000)
        self._workers = []
        self.executors = executors

    @staticmethod
    def on(msg_typ):
        def decorator(t):
            Foreverbull._routes[msg_typ] = t
            return t

        return decorator

    def run(self, backtest_id=None, session_id=None, executors=None):
        if executors is None:
            self.executors = int(os.environ.get("EXECUTORS", "1"))
        if backtest_id:
            rsp = self.broker.http.backtest.get_backtest(backtest_id)
            self.backtest.load(rsp)
        else:
            rsp = self.broker.http.backtest.create_backtest(self.backtest.dict())
            self.backtest = BacktestModel(**rsp)
            self._create_service(self.backtest)
        self._create_session(self.backtest)
        t1 = Thread(target=self._on_message)
        t1.start()
        self._run_session()
        t1.join()

        self._delete_session()

    def _on_message(self):
        while True:
            message = self.broker.socket.recv()
            if message.task == "backtest_completed":
                rsp = foreverbull.broker.socket.models.Response(task="backtest_completed")
                self.broker.socket.send(rsp)
                self._queue.put("None")
                for w in self._workers:
                    w.join()
                return
            elif message.task == "day_completed":
                rsp = foreverbull.broker.socket.models.Response(task="day_completed")
            elif message.task == "initialize":
                initialize = Initialization(**message.data)
                for _ in range(self.executors):
                    w = Worker(self._queue, initialize.session_id, initialize.database, **self._routes)
                    w.start()
                    self._workers.append(w)
                rsp = foreverbull.broker.socket.models.Response(task="initialize")
            else:
                self._worker_requests.put(message)
                rsp = self._worker_responses.get() 
            self.broker.socket.send(rsp)

    def _run_session(self):
        self.broker.http.backtest.run_session(
            self.backtest.id,
            self.session.id,
            {"instances": [self.broker.local_connection()], "services": []},
        )

    def _create_session(self, backtest):
        rsp = self.broker.http.backtest.create_session(backtest.id)
        self.session = Session(**rsp)
        return self.session

    def _create_service(self, backtest):
        rsp = self.broker.http.service.create_container(self.container.dict())
        self.container = Container(**rsp)
        self.service.container_id = self.container.id
        rsp = self.broker.http.service.create_service(self.service.dict())
        self.service = Service(**rsp)
        return self.broker.http.backtest.add_backtest_service(backtest.id, {"id": self.service.id})

    def _delete_session(self):
        self.broker.http.backtest.delete_session(self.backtest.id, self.session.id)

    def _delete_backtest(self):
        self.broker.http.backtest.delete_backtest(self.backtest.id)
