import datetime
from os import environ

from flask import Blueprint, Flask, make_response

from cfserdika.client import Cfserdika

bp = Blueprint("cfserdika", __name__)

client = Cfserdika(
    email=environ["CFSERDIKA_EMAIL"],
    password=environ["CFSERDIKA_PASSWORD"],
)


@bp.route("/ical")
def ical():
    start = (
        datetime.datetime.now()
        .astimezone(Cfserdika.TZ)
        .replace(hour=0, minute=0, second=0, microsecond=0)
    )
    end = start + datetime.timedelta(hours=7)
    calendar = client.get_ical(start=start, end=end)
    resp = make_response(calendar.to_ical())
    resp.headers["Content-Type"] = "text/calendar; charset=utf-8"
    return resp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)

    return app
