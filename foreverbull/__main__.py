from argparse import ArgumentParser
import time
from foreverbull import input_parser
from foreverbull.input_parser import InputError, InputParser
import foreverbull_core.logger
from foreverbull_core import cli

from foreverbull import Foreverbull

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
    input.setup_worker_file()
    fb.start()
    if input.service_instance:
        input.service_instance.online = True
        input.service_instance.listen = True
        _run_input.broker.http.service.update_instance(input.service_instance)
    else:
        input.broker.run_test_run(input.backtest_id)
    try:
        while fb.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        fb.stop()
    
    if input.service_instance:
        input.service_instance.online = True
        input.service_instance.listen = True
        _run_input.broker.http.service.update_instance(input.service_instance)
    else:
        pass # Make stop backtest
        

if __name__ == "__main__":
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