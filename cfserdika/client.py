import datetime

import pytz
import requests
from icalendar import Alarm, Calendar, Event, vDatetime, vDuration


class Cfserdika:
    TZ = pytz.timezone("Europe/Sofia")

    def __init__(self, *, email, password):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/111.0"

    def get_customer_details(self):
        response = self.session.get(
            "https://crossfitserdika.customer.fitsys.co/calendar/fetch-data",
            params={
                "site_id": "1",
                "iframe": "true",
                "triedLogin": "false",
                "cookies_enabled": "true",
            },
        )
        response.raise_for_status()
        return response.json()

    def get_authenticated_customer_details(self):
        customer_details = self.get_customer_details()

        try:
            customer_email = customer_details["customer"]["email"]
        except KeyError:
            customer_email = None

        if customer_email == self.email:
            return customer_details

        response = self.session.post(
            "https://crossfitserdika.customer.fitsys.co/login",
            json={
                "email": self.email,
                "password": self.password,
                "remember": False,
                "facebook_id": None,
                "first_name": "",
                "last_name": "",
                "facebook_email": "",
                "user_id": None,
                "iframe": True,
                "triedLogin": False,
                "cookies_enabled": True,
            },
        )
        response.raise_for_status()
        assert response.json()["user"]["email"] == self.email

        customer_details = self.get_customer_details()
        assert customer_details["customer"]["email"] == self.email

        return customer_details

    def get_ical(self, *, start, end):
        customer_details = self.get_authenticated_customer_details()

        calendar = Calendar()

        for event in customer_details["next_events"]:
            calendar.add_component(self.generate_event(event))

        return calendar

    def generate_event(self, event):
        start = self.TZ.localize(datetime.datetime.fromisoformat(event["start"]))
        end = self.TZ.localize(datetime.datetime.fromisoformat(event["end"]))

        e = Event(
            UID="CFSERDIKA-%d" % event["id"],
            DTSTAMP=vDatetime(start),
            SUMMARY=event["title"],
            DTSTART=vDatetime(start),
            DTEND=vDatetime(end),
            LOCATION='Национален стадион "Васил Левски бул. "Евлоги и Христо Георгиеви" 38 вход от сектор В, ет. 2, 1164 Sofia',
        )

        e.add_component(
            Alarm(
                ACTION="DISPLAY",
                TRIGGER=vDuration(datetime.timedelta(minutes=-40)),
            ),
        )

        e.add_component(
            Alarm(
                ACTION="DISPLAY",
                TRIGGER=vDuration(
                    (
                        (start - datetime.timedelta(days=1)).replace(
                            hour=19, minute=0, second=0, microsecond=0
                        )
                    )
                    - start
                ),
            )
        )

        return e
