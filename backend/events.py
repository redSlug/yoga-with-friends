import json
import os
import re
import datetime
from typing import List, Any, Dict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

from ppm_generator import create_image_file
from data_types.all import Event
from utils.get_date import (
    convert_to_datetime,
    get_timestamp,
    get_cancellation_timestamp,
    get_wait_list_timestamp,
)

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]
LOOKBACK_DAYS = 2

BASE_PATH = os.path.dirname(__file__)


def save_ppm_file(text):
    filepath = os.path.abspath(os.path.join(BASE_PATH, "..", "output.ppm"))
    create_image_file(text, filepath)


def save_events_for_frontend(events: List[Event]):
    filepath = os.path.abspath(
        os.path.join(BASE_PATH, "..", "frontend", "src", "data", "events.json")
    )
    with open(filepath, "w") as f:
        f.write(json.dumps([event.__dict__ for event in events]))
    print(f"wrote json to file: ", filepath)


def get_gmail_service():
    return get_service("gmail", "v1")


def get_calendar_service():
    return get_service("calendar", "v3")


def get_service(name, version):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # user needs to log in and grant access
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build(name, version, credentials=creds)


def create_calendar_event(
    service: Any,
    summary: str,
    location: str,
    description: str,
    start_datetime: datetime.datetime,
    end_datetime: datetime.datetime,
    timezone: str = "America/New_York",
) -> Dict[str, Any]:
    start = start_datetime.isoformat()
    event: Dict[str, Any] = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": timezone,
        },
    }
    try:
        event = service.events().insert(calendarId="primary", body=event).execute()
        return event
    except Exception as error:
        print(f"An error occurred creating event w/ start {start}: {error}")
        return {}


def search_messages(service, query):
    result = service.users().messages().list(userId="me", q=query).execute()
    messages = []
    if "messages" in result:
        messages.extend(result["messages"])
    while "nextPageToken" in result:
        page_token = result["nextPageToken"]
        result = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        if "messages" in result:
            messages.extend(result["messages"])
    return messages


def get_message_content(service, msg_id):
    message = (
        service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    )
    payload = message["payload"]

    if "body" in payload and "data" in payload["body"]:
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8")


def get_wait_list_reservations(service, today):
    print("gathering wait list reservations")
    two_days_ago = today - datetime.timedelta(days=LOOKBACK_DAYS)
    date_str = two_days_ago.strftime("%Y/%m/%d")
    query = f'from:info@heatwise-studio.com subject:"Heatwise waitlist update: You got a spot!" after:{date_str}'
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No matching wait list emails found.")
        return calendar_events

    # Created using https://python-fiddle.com/tools/regex and Raw example data (copied from email):
    # <p>We will see you at <strong>8:00 PM</strong> on
    # <strong>Wednesday</strong>, <strong>February</strong> <strong>12</strong>
    # at our <strong>Park Slope - 7th Ave</strong> studio.</p>
    pattern = (
        r"We will see you at <strong>(\d+:\d+) (AM|PM)</strong> on "
        r"<strong>(.*?)</strong>, <strong>(.*?)</strong> <strong>(.*?)</strong> at our "
        r"<strong>(.*?)</strong> studio."
    )

    for msg in messages:
        msg_id = msg["id"]
        content = get_message_content(service, msg_id)

        if not content:
            print("no waitlist content")
            continue

        match = re.search(pattern, content)
        if not match:
            print(f"wait list regex didn't match {pattern}, content=", content)

        time = match.group(1)
        meridiem = match.group(2)
        day_of_week = match.group(3)
        month = match.group(4)
        day = match.group(5)
        location = match.group(6).split("-")[0]

        calendar_events.append(
            Event(
                instructor="from wait list",
                location=location,
                timestamp=get_wait_list_timestamp(time, meridiem, month, day),
                time=time,
                meridiem=meridiem,
                day_of_week=day_of_week,
                date=f"{month} {day}",
            )
        )
    return calendar_events


def get_reservations(service, today):
    print("gathering reservations")
    two_days_ago = today - datetime.timedelta(days=LOOKBACK_DAYS)
    date_str = two_days_ago.strftime("%Y/%m/%d")
    query = f'from:info@heatwise-studio.com subject:"Your spot has been reserved" after:{date_str}'
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No  matching reservation emails found.")
        return calendar_events

    # Created using https://python-fiddle.com/tools/regex and Raw example data:
    # with <strong>Erin Lyons</strong> at <strong>Park Slope - 7th Ave</strong>.
    # We will see you at <strong>8:45 AM</strong> on <strong>Tuesday</strong>, <strong>March 4</strong>.</p>
    pattern = (
        r"with <strong>([a-zA-Z ]*?)</strong> at <strong>(.*?)</strong>. We will see you at"
        r" <strong>(\d+:\d+) (AM|PM)</strong> on <strong>("
        r".*?)</strong>, <strong>(.*?)</strong>"
    )

    for msg in messages:
        msg_id = msg["id"]
        content = get_message_content(service, msg_id)

        if not content:
            continue
        match = re.search(pattern, content)
        if not match:
            print(f"reservations regex didn't match {pattern}, content=", content)
            continue

        time = match.group(3)
        meridiem = match.group(4)
        date = match.group(6)

        calendar_events.append(
            Event(
                instructor=match.group(1),
                location=match.group(2).split("-")[0],
                timestamp=get_timestamp(time, meridiem, date),
                time=time,
                meridiem=meridiem,
                day_of_week=match.group(5),
                date=date,
            )
        )
    return calendar_events


def get_cancellations(service, today):
    print("gathering cancellations")
    two_days_ago = today - datetime.timedelta(days=LOOKBACK_DAYS)
    date_str = two_days_ago.strftime("%Y/%m/%d")
    query = (
        f'from:info@heatwise-studio.com subject:"Reservation canceled" after:{date_str}'
    )
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No matching cancellation emails found.")
        return calendar_events

    # Created using https://python-fiddle.com/tools/regex and example copied directly from email:
    # on 2/17/2025 at 8:00 PM has been canceled.
    pattern = r"on (\d{1,2}\/\d{1,2}\/\d{4}) at (.*) (AM|PM) has been <strong>canceled</strong>"

    cancellation_events = []

    for msg in messages:
        msg_id = msg["id"]
        content = get_message_content(service, msg_id)

        if not content:
            print("no cancel content in message", msg_id)
            continue
        match = re.search(pattern, content)
        if not match:
            print(f"cancel regex didn't match {pattern}, content=", content)
            continue

        time = match.group(2)
        meridiem = match.group(3)
        date = match.group(1)

        cancellation_events.append(
            Event(
                instructor="",
                location="",
                timestamp=get_cancellation_timestamp(date, time, meridiem),
                time=time,
                meridiem=meridiem,
                day_of_week="",
                date=date,
            )
        )
    return cancellation_events


def main():
    gmail_service = get_gmail_service()
    today = datetime.datetime.now()
    reservations = get_reservations(gmail_service, today)
    reservations.extend(get_wait_list_reservations(gmail_service, today))
    cancellations = get_cancellations(gmail_service, today)
    cancelled_timestamps = set([e.timestamp for e in cancellations])
    print(
        f"reservations count={ len(reservations)}, cancelled timestamps=",
        cancelled_timestamps,
    )

    # TODO: case where person cancels then re-registers; look at email sent time
    reservations = [r for r in reservations if r.timestamp not in cancelled_timestamps]
    print(f"reservations count after cancellations={ len(reservations)}")
    reservations = [e for e in reservations if e.timestamp > today.timestamp()]
    reservations.sort(key=lambda e: e.timestamp)

    if len(reservations) > 0:
        next_event = reservations[0]
        save_ppm_file(next_event.time + next_event.meridiem)
        save_events_for_frontend(reservations)

    calendar_service = get_calendar_service()

    for event in reservations:
        print("creating event", event)
        start_datetime = convert_to_datetime(event)

        create_calendar_event(
            service=calendar_service,
            summary="Yoga Class in " + event.location,
            location="",
            description="with instructor " + event.instructor,
            start_datetime=start_datetime,
            end_datetime=start_datetime + datetime.timedelta(minutes=60),
            timezone="America/New_York",
        )
    return reservations


if __name__ == "__main__":
    events = main()
    print(events)
