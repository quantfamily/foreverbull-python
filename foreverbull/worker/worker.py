from foreverbull.broker.data.data import Database
from multiprocessing import Process

import foreverbull


class Worker(Process):
    def __init__(self, queue, session_id, database, **routes):
        super(Worker, self).__init__()
        self._queue = queue
        self._routes = routes
        self.session_id = session_id
        self.database = Database(session_id=session_id, **database)
        print(type(self.database))
        print(dir(self.database))

    def __call__(self, request):
        rsp = foreverbull.broker.socket.models.Response(task=request.task)
        return rsp

    def run(self):
        self.database.connect()
        while True:
            data = self._queue.get()
            if data == "None":
                self._queue.put("None")
                return
            if data.task == "eod_stock_data":
                self._routes["stock_data"](data.data, self.database)
