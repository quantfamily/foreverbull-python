import argparse
import importlib
import sys
import signal
import time
from foreverbull_core.broker import Broker
import os
import socket

parser = argparse.ArgumentParser(prog="foreverbull")
parser.add_argument("file")
parser.add_argument("--broker-url", help="URL of broker")
parser.add_argument("--local-host", help="Local Address")
parser.add_argument("--executors", help="Number of Executors")
parser.add_argument("--service-id", help="Service ID")
parser.add_argument("--instance-id", help="Instance ID")

def algo_from_arguments(*arguments):
    algo = parser.parse_args(*arguments).file
    importlib.import_module(algo)

def broker_from_arguments(*arguments):
    args = parser.parse_args(*arguments)
    if args.service_id:
        service_id = args.service_id
    else:
        service_id = os.environ.get("SERVICE_ID")
        if service_id is None:
            raise SystemExit("missing service-id")
    if args.instance_id:
        instance_id = args.instance_id
    else:
        instance_id = os.environ.get("INSTANCE_ID")
        if instance_id is None:
            raise SystemExit("missing instance-id")
    if args.broker_url:
        broker_url = args.broker_url
    else:
        broker_url = os.environ.get("BROKER_URL", "127.0.0.1:8080")
    if args.local_host:
        local_host = args.local_host
    else:
        local_host = os.environ.get("LOCAL_HOST", socket.gethostbyname(socket.gethostname()))

    return Broker(broker_url, service_id, instance_id, local_host)


def run_application(application):
    return
    application.broker.mark_as_online()
    application.start()
    try:
        while application.running:
            time.sleep(1)
    except KeyboardInterrupt:
        application.stop()
    application.broker.mark_as_offline()
    application.join()


if __name__ == "__main__":
    algo_from_arguments(sys.argv[1:])
    broker = broker_from_arguments(sys.argv[1:])
    application = Foreverbull(broker)
    #signal.signal(signal.SIGTERM, application.stop())
    run_application(application)

