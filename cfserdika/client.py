import datetime
from zoneinfo import ZoneInfo

import requests
from icalendar import Alarm, Calendar, Event, vDatetime, vDuration


class Cfserdika:
    TZ = ZoneInfo("Europe/Sofia")

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

    def get_events(self, *, start, end):
        assert end >= start
        response = self.session.get(
            "https://crossfitserdika.customer.fitsys.co/calendar/get-events",
            params={
                "site_id": "1",
                "instructor_id": "any",
                "class_id": "any",
                "class_title": "any",
                "category_id[]": "any",
                "resource_id": "any",
                "event_type": "any",
                "start": start.astimezone(self.TZ).isoformat(timespec="seconds"),
                "end": end.astimezone(self.TZ).isoformat(timespec="seconds"),
                "iframe": "true",
                "triedLogin": "false",
                "cookies_enabled": "true",
            },
        )
        response.raise_for_status()
        return response.json()

    def get_event_at(self, dt):
        events = self.get_events(start=dt, end=dt + datetime.timedelta(hours=24))

        for event in events["events"]:
            start = datetime.datetime.fromisoformat(event["start"]).replace(
                tzinfo=self.TZ
            )

            if start == dt:
                return event

        return None

    def reserve(self, event):
        self.get_authenticated_customer_details()

        response = self.session.post(
            "https://crossfitserdika.customer.fitsys.co/calendar/event/reserve",
            json={
                "event_id": event["id"],
                "contact_phone": "0894033321",
                "reservation_type": "free",
                "reservation_text": "плащане на място",
                "customer_note": "",
                "mandatoryPayOnline": False,
                "iframe": True,
                "triedLogin": False,
                "cookies_enabled": True,
            },
            headers={
                # "Origin": "https://crossfitserdika.customer.fitsys.co",
                # "Referer": "https://crossfitserdika.customer.fitsys.co/calendar/view_only?site_id=1",
            },
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                e = RuntimeError(response.json()["error"])
            except:
                pass
            raise e

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

        retrieved_at = datetime.datetime.now(datetime.timezone.utc)

        events = self.get_events(
            start=retrieved_at,
            end=retrieved_at + datetime.timedelta(days=7),
        )

        calendar = Calendar()

        for event in events["events"]:
            if not event["participant_user_id"]:
                continue
            calendar.add_component(
                self.generate_event(event, retrieved_at=retrieved_at)
            )

        return calendar

    def generate_event(self, event, *, retrieved_at):
        start = datetime.datetime.fromisoformat(event["start"]).replace(tzinfo=self.TZ)
        end = datetime.datetime.fromisoformat(event["end"]).replace(tzinfo=self.TZ)

        e = Event(
            UID="CFSERDIKA%s" % start.strftime("%Y%m%d%H%M%S"),
            DTSTAMP=vDatetime(retrieved_at),
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
