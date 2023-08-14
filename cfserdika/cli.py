import datetime
import sys
from argparse import ArgumentParser
from os import environ

from cfserdika.client import Cfserdika

parser = ArgumentParser()
subparsers = parser.add_subparsers(required=True, dest="command")

ical_parser = subparsers.add_parser("ical")


def main():
    args = parser.parse_args()
    return commands[args.command](args)


def cmd_ical(args):
    start = (
        datetime.datetime.now()
        .astimezone(Cfserdika.TZ)
        .replace(hour=0, minute=0, second=0, microsecond=0)
    )
    end = start + datetime.timedelta(days=7)
    sys.stdout.buffer.write(
        Cfserdika(
            email=environ["CFSERDIKA_EMAIL"],
            password=environ["CFSERDIKA_PASSWORD"],
        )
        .get_ical(start=start, end=end)
        .to_ical()
    )


commands = {"ical": cmd_ical}

if __name__ == "__main__":
    sys.exit(main())
