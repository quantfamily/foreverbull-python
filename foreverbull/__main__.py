import logging
import time
from argparse import ArgumentParser

import foreverbull_core.logger
from foreverbull import Foreverbull
from foreverbull.input_parser import InputError, InputParser
from foreverbull_core import cli
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.service import RawConnection

_service_input = cli.ServiceInput()
_backtets_input = cli.BacktestInput()
_worker_input = cli.WorkerInput()
_run_input = InputParser()

parser = ArgumentParser()
subparser = parser.add_subparsers(dest="option")

system = subparser.add_parser("service", help="service")
_service_input.add_arguments(system)
backtest = subparser.add_parser("backtest", help="backtest")
_backtets_input.add_arguments(backtest)
worker = subparser.add_parser("worker", help="worker")
_worker_input.add_arguments(worker)
run = subparser.add_parser("run", help="run algo")
_run_input.add_arguments(run)


def run_foreverbull(input: InputParser):
    fb = Foreverbull(_run_input.broker.socket, _run_input.executors)
    input.import_algo_file()
    fb.start()

    try:
        if input.service_instance:
            input.service_instance.online = True
            input.service_instance.listen = True
            _run_input.broker.http.service.update_instance(input.service_instance)
        elif input.backtest_id:
            session = Session(backtest_id=_run_input.backtest_id, worker_count=0, run_automaticlly=False)
            conn = RawConnection(host=_run_input.broker._local_host, port=_run_input.broker.socket.config.port)
            session = _run_input.broker.http.backtest.create_session(_run_input.backtest_id, session=session)
            _run_input.broker.http.backtest.setup_session(session.backtest_id, session.id)
            _run_input.broker.http.backtest.configure_session(session.backtest_id, session.id, conn)
            _run_input.broker.http.backtest.run_session(session.backtest_id, session.id)
        else:
            raise InputError("neither service_instance or backtest-id defined")

    except Exception as e:
        logging.error(f"unable to call backend: {repr(e)}")
        fb.stop()
        return

    try:
        while fb.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    fb.stop()

    if input.service_instance:
        input.service_instance.online = True
        input.service_instance.listen = True
        _run_input.broker.http.service.update_instance(input.service_instance)
    else:
        _run_input.broker.http.backtest.stop_session(session.backtest_id, session.id)


def main():
    foreverbull_core.logger.Logger()
    args = parser.parse_args()

    try:
        if args.option == "run":
            _run_input.parse(args)
            run_foreverbull(_run_input)
        elif args.option == "service":
            _service_input.parse(args)
        elif args.option == "backtest":
            _backtets_input.parse(args)
        elif args.option == "worker":
            _worker_input.parse(args)
        else:
            parser.print_help()
    except InputError as e:
        print(e)
        parser.print_help()


if __name__ == "__main__":
    main()
