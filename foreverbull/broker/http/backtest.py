import requests


class RequestError(Exception):
    pass


class Backtest:
    def __init__(self, host) -> None:
        self.host = host

    def list_backtests(self):
        rsp = requests.get(f"http://{self.host}:8080/backtests")
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def create_backtest(self, backtest):
        rsp = requests.post(f"http://{self.host}:8080/backtests", json=backtest)
        if not rsp.ok:
            print("text: ", rsp.text)
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def get_backtest(self, backtest_id):
        rsp = requests.get(f"http://{self.host}:8080/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_backtest():
        pass

    def delete_backtest(self, backtest_id):
        rsp = requests.delete(f"http://{self.host}:8080/backtests/{backtest_id}")
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return True

    def list_backtest_services(self, backtest_id):
        rsp = requests.get(f"http://{self.host}:8080/backtests/{backtest_id}/services")
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def add_backtest_service(self, backtest_id, service):
        rsp = requests.post(
            f"http://{self.host}:8080/backtests/{backtest_id}/services", json=service
        )
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        # return rsp.json

    def list_sessions(self, backtest_id):
        rsp = requests.get(f"http://{self.host}:8080/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def create_session(self, backtest_id):
        rsp = requests.post(f"http://{self.host}:8080/backtests/{backtest_id}/sessions")
        if not rsp.ok:
            print(rsp.json())
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def get_session(self, backtest_id, session_id):
        rsp = requests.get(
            f"http://{self.host}:8080/backtests/{backtest_id}/sessions/{session_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()

    def update_session():
        pass

    def delete_session(self, backtest_id, session_id):
        rsp = requests.delete(
            f"http://{self.host}:8080/backtests/{backtest_id}/sessions/{session_id}"
        )
        if not rsp.ok:
            raise RequestError(
                f"call to backtests gave bad return code: {rsp.status_code}"
            )
        return True

    def run_session(self, backtest_id, session_id, run_workers):
        rsp = requests.post(
            f"http://{self.host}:8080/backtests/{backtest_id}/sessions/{session_id}/run",
            json=run_workers,
        )
        if not rsp.ok:
            print(rsp.text)
            raise RequestError(
                f"call to dbacktests gave bad return code: {rsp.status_code}"
            )
        return rsp.json()
