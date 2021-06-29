from foreverbull.foreverbull import Foreverbull
import argparse
import importlib

parser = argparse.ArgumentParser(prog="foreverbull")
parser.add_argument("file")
parser.add_argument("-b", "--broker-host", help="Address of broker")
parser.add_argument("-e", "--executors", help="Number of Executors")
parser.add_argument("-bid", "--backtest-id", help="Backtest id")
parser.add_argument("-sid", "--session-id", help="Session id")


def main():
    args = parser.parse_args()

    importlib.import_module(args.file)

    print(args)
    fb = Foreverbull(args.broker_host, args.executors)
    fb.run(args.backtest_id, args.session_id)
    print("main")


if __name__ == "__main__":
    main()
