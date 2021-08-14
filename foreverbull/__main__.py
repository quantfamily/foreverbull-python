import argparse
import importlib
import os
import time

from foreverbull.foreverbull import Foreverbull

parser = argparse.ArgumentParser(prog="foreverbull")
parser.add_argument("file")
parser.add_argument("-b", "--broker-host", help="Address of broker")
parser.add_argument("-e", "--executors", help="Number of Executors")
parser.add_argument("-bid", "--backtest-id", help="Backtest id")
parser.add_argument("-sid", "--session-id", help="Session id")
parser.add_argument("-la", "--local-address", help="Local Address")
parser.add_argument("-lp", "--local-port", help="Local Port")
parser.add_argument("-sid", "--service-id", help="Service ID", required=True)
parser.add_argument("-siid", "--instance-id", help="Instance ID", required=True)


def main():
    args = parser.parse_args()

    importlib.import_module(args.file)

    fb = Foreverbull(args.broker_host, args.executors)
    if args.service_id:
        service_id = args.service_id
    else:
        service_id = os.environ.get("service_id")
        if service_id is None:
            raise
    if args.instance_id:
        instance_id = args.instance_id
    else:
        instance_id = os.environ.get("instance_id")
        if instance_id is None:
            raise

    fb.start()
    fb.broker.mark_as_online(service_id, instance_id, args.local_addres, args.local_port)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        fb.broker.mark_as_offline()
        fb.stop()
        fb.join()
    return


if __name__ == "__main__":
    main()
