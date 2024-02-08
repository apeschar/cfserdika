import datetime
import sys
from argparse import ArgumentParser
from os import environ

import dateparser
import requests

from cfserdika.client import Cfserdika


def get_parser():
    parser = ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    subparsers = parser.add_subparsers(required=True, dest="command")

    ical_parser = subparsers.add_parser("ical")
    ical_parser.set_defaults(func=cmd_ical)

    reserve_parser = subparsers.add_parser("reserve")
    reserve_parser.set_defaults(func=cmd_reserve)
    reserve_parser.add_argument("--at", type=datetime.time.fromisoformat, required=True)
    reserve_parser.add_argument("--days", type=int, default=7)

    return parser


def main():
    args = get_parser().parse_args()
    if args.debug:
        enable_logging()
    return args.func(args)


def enable_logging():
    import logging

    import requests

    # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # The only thing missing will be the response.body which is not logged.
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    # You must initialize logging, otherwise you'll not see debug output.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def cmd_ical(args):
    start = (
        datetime.datetime.now()
        .astimezone(Cfserdika.TZ)
        .replace(hour=0, minute=0, second=0, microsecond=0)
    )
    end = start + datetime.timedelta(days=7)
    sys.stdout.buffer.write(get_client().get_ical(start=start, end=end).to_ical())


def cmd_reserve(args):
    try:
        reserve_at = datetime.datetime.now(Cfserdika.TZ).replace(
            hour=args.at.hour,
            minute=args.at.minute,
            second=args.at.second,
            microsecond=args.at.microsecond,
        ) + datetime.timedelta(days=args.days)

        client = get_client()

        event = client.get_event_at(reserve_at, title="CrossFit")

        if not event:
            raise RuntimeError("Could not find event at %s" % reserve_at.isoformat())

        client.reserve(event)

        send_notification(
            "Reserved class at %s" % reserve_at.strftime("%A %d %B at %H:%M")
        )
    except Exception as e:
        notify_exception(e)

        raise e


def notify_exception(e):
    send_notification("Could not reserve: %s" % e.args[0])


def send_notification(message):
    if "PUSHOVER_TOKEN" not in environ or "PUSHOVER_USER" not in environ:
        return

    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": environ["PUSHOVER_TOKEN"],
            "user": environ["PUSHOVER_USER"],
            "message": message,
        },
    )


def get_client():
    return Cfserdika(
        email=environ["CFSERDIKA_EMAIL"],
        password=environ["CFSERDIKA_PASSWORD"],
    )


if __name__ == "__main__":
    sys.exit(main())
