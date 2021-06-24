import threading

import foreverbull


class Foreverbull(threading.Thread):
    def __init__(self, host, port):
        self.logger = foreverbull.get_logger(__name__)
        self._configuration = foreverbull.models.Configuration(socket_type="replier")
        self._socket = foreverbull.socket.NanomsgSocket(self._configuration)
        self.backtests = []
        self.running = False
        self._router = foreverbull.router.MessageRouter()
        threading.Thread.__init__(self)

    def info(self):
        return {"socket": self._configuration.dict(), "service_type": "worker"}

    def _process_message(self):
        req = self._socket.recv()
        rsp = self._router(req)
        self._socket.send(rsp)

    def run(self):
        self.running = True
        while self.running:
            try:
                self._process_message()
            except Exception as exc:
                self.logger.error(exc, exc_info=True)
        self._socket.close()

    def stop(self):
        self.running = False
