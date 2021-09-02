import argparse
import os
import socket


class InputParser:
    def __init__(self) -> None:
        self.broker_url = "127.0.0.1:8080"
        self.local_host = socket.gethostbyname(socket.gethostname())
        self.executors = 1
        self.service_id = None
        self.instance_id = None
        self.file = None 


        self.parser = argparse.ArgumentParser(
            prog="foreverbull", formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.parser.add_argument("file", nargs="?")
        self.parser.add_argument("--broker-url", help="URL of broker", default=self.broker_url)
        self.parser.add_argument("--local-host", help="Local Address", default=self.local_host)
        self.parser.add_argument("--executors", help="Number of Executors", default=self.executors)
        self.parser.add_argument("--service-id", help="Service ID", default=self.service_id)
        self.parser.add_argument("--instance-id", help="Instance ID", default=self.instance_id)

    def _parse_environment(self):
        self.broker_url = os.environ.get("BROKER_URL", self.broker_url)
        self.local_host = os.environ.get("LOCAL_HOST", self.local_host)
        self.executors = os.environ.get("EXECUTORS", self.executors)
        self.service_id = os.environ.get("SERVICE_ID", self.service_id)
        self.instance_id = os.environ.get("INSTANCE_ID", self.instance_id)

    def _parse_arguments(self, *arguments):
        args = self.parser.parse_args(*arguments)
        if args.file:
            self.file = args.file
        if args.service_id:
            self.service_id = args.service_id
        if args.instance_id:
            self.instance_id = args.instance_id
        if args.broker_url and args.broker_url != self.parser.get_default('broker_url'):
            self.broker_url = args.broker_url
        if args.local_host and args.broker_url != self.parser.get_default('local_host'):
            self.local_host = args.local_host
        if args.executors and args.broker_url != self.parser.get_default('executors'):
            self.executors = args.executors

    def _input_is_set(self):
        if not self.service_id:
            return False
        if not self.instance_id:
            return False
        return True

    def _print_help(self):
        self.parser.print_help()
        print("error: the following arguments are required: ", end="")
        if not self.service_id:
            print("--service-id ", end="")
        if not self.instance_id:
            print("--instance-id", end="")
        print("")

    def _verify_input(self):
        if not self._input_is_set():
            self._print_help()
            return False
        return self

    def parse_input(self, *arguments):
        self._parse_environment()
        self._parse_arguments(*arguments)
        return self._verify_input()
