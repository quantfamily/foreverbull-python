import argparse
import os

from foreverbull_core import cli
from foreverbull_core.models import service


class InputParser:
    def __init__(self) -> None:
        self.broker_url = "127.0.0.1:8080"
        self.local_host = "127.0.0.1"
        self.executors = 1
        self.service_id = None
        self.instance_id = None
        self.file = None
        self.backtest_id = None

        self.instance: service.Instance = None

        self._service_input = cli.ServiceInput()
        self._backtets_input = cli.BacktestInput()
        self._worker_input = cli.WorkerInput()

        self.parser = argparse.ArgumentParser(
            prog="foreverbull", formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        subparser = self.parser.add_subparsers(dest="option")

        system = subparser.add_parser("service", help="service")
        self._service_input.add_arguments(system)
        backtest = subparser.add_parser("backtest", help="backtest")
        self._backtets_input.add_arguments(backtest)
        worker = subparser.add_parser("worker", help="worker")
        self._worker_input.add_arguments(worker)
        run = subparser.add_parser("run", help="run algo")
        self.add_arguments(run)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--broker-url", help="URL of broker", default=self.broker_url)
        parser.add_argument("--local-host", help="Local Address", default=self.local_host)
        parser.add_argument("--executors", help="Number of Executors", default=self.executors)
        parser.add_argument("--backtest-id", help="id of backtest", default=self.backtest_id)
        parser.add_argument("--file", required=True, help="python- file to run")
        subparser = parser.add_subparsers(dest="run_option")
        as_instance = subparser.add_parser("as_instance", help="run backtest as service instance")
        as_instance.add_argument("--service-id", help="service id", required=True)
        as_instance.add_argument("--instance-id", help="instance id", required=True)

    def _parse_environment(self):
        self.broker_url = os.environ.get("BROKER_URL", self.broker_url)
        self.local_host = os.environ.get("LOCAL_HOST", self.local_host)
        self.executors = os.environ.get("EXECUTORS", self.executors)
        self.service_id = os.environ.get("SERVICE_ID", self.service_id)
        self.instance_id = os.environ.get("INSTANCE_ID", self.instance_id)

    def parse(self, args: argparse.Namespace):
        self._parse_environment()
        self._parse_arguments(args)

    def _parse_arguments(self, *arguments):
        args = self.parser.parse_args(*arguments)
        if args.option == "run":
            self._parse_run(args)
        elif args.option == "service":
            return self._service_input.parse(args)
        elif args.option == "backtest":
            return self._backtets_input.parse(args)
        elif args.option == "worker":
            return self._worker_input.parse(args)
        else:
            self.parser.print_help()

    def _parse_run(self, args: argparse.Namespace):
        if args.file:
            self.file = args.file
        if args.broker_url and args.broker_url != self.parser.get_default("broker_url"):
            self.broker_url = args.broker_url
        if args.local_host and args.local_host != self.parser.get_default("local_host"):
            self.local_host = args.local_host
        if args.executors and args.executors != self.parser.get_default("executors"):
            self.executors = args.executors
        if args.run_option == "as_instance":
            self._parse_run_backtest(args)
        else:
            self.backtest_id = args.backtest_id

    def _parse_run_backtest(self, args: argparse.Namespace):
        if args.service_id:
            self.service_id = args.service_id
        if args.instance_id:
            self.instance_id = args.instance_id
        self.instance = service.Instance(id=self.instance_id, service_id=self.service_id)

    def parse_input(self, *arguments):
        self._parse_environment()
        self._parse_arguments(*arguments)
        return self
