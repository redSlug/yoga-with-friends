import base64
import datetime
import json
import os
import re
from pathlib import Path
from typing import List

from data_types.all import Event
from email_client import get_service
from ics_calendar import create_calendar
from ppm_generator import create_image_file
from publisher import upload_to_s3
from utils.get_date import (
    get_timestamp,
    get_cancellation_timestamp,
    get_wait_list_timestamp,
)

LOOK_BACK_DAYS = 30


def get_public_file_path(file_name):
    return os.path.abspath(
        Path(Path.cwd().parent.joinpath("frontend", "public", file_name))
    )


def get_assets_file_path(file_name):
    return os.path.abspath(
        Path(Path.cwd().parent.joinpath("frontend", "src", "assets", file_name))
    )


def save_ppm_file(text):
    create_image_file(text, get_public_file_path("yoga.ppm"))


def get_events_json(events: List[Event]) -> str:
    return json.dumps([event.__dict__ for event in events])


def save_events_for_frontend(events: List[Event]):
    static_file_path = get_public_file_path("yoga.json")
    with open(static_file_path, "w") as f:
        f.write(get_events_json(events))
    print(f"wrote json to file: ", static_file_path)


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


def get_wait_listed(service, start_date_str):
    print("gathering wait list potential reservations")
    query = f'from:info@heatwise-studio.com subject:"You\'re on the waitlist" after:{start_date_str}'
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No matching wait list potential reservation emails found.")
        return calendar_events

    # For now, you have been added to the waitlist for Some Like it Hot with Arianna Neikrug at 9:30 AM on Saturday, March 22.
    pattern = (
        r"waitlist for Some Like it Hot with Arianna Neikrug at (\d+:\d+) (AM|PM) on (.*?), (.*?)."
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
        date = match.group(4)

        calendar_events.append(
            Event(
                msg_id=msg_id,
                event_type="reservation",
                instructor="from wait list",
                location="unknown",
                timestamp=get_timestamp(time, meridiem, date),
                time=time,
                meridiem=meridiem,
                day_of_week=day_of_week,
                date=date,
            )
        )
    return calendar_events


def get_wait_list_reservations(service, start_date_str):
    print("gathering wait list reservations")
    query = f'from:info@heatwise-studio.com subject:"Heatwise waitlist update: You got a spot!" after:{start_date_str}'
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
                msg_id=msg_id,
                event_type="reservation",
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


def maybe_strip(s):
    try:
        return s.strip()
    except s:
        return ""

def get_reservations(service, start_date_str):
    print("gathering reservations")
    query = f'from:info@heatwise-studio.com subject:"Your spot has been reserved" after:{start_date_str}'
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No  matching reservation emails found.")
        return calendar_events

    # Created using https://python-fiddle.com/tools/regex and Raw example data:
    # with <strong>Erin Lyons</strong> at <strong>Park Slope - 7th Ave</strong>.
    # We will see you at <strong>8:45 AM</strong> on <strong>Tuesday</strong>, <strong>March 4</strong>.</p>
    pattern = (
        r"with <strong>([a-zA-Z. ]*?)</strong> at <strong>(.*?)</strong>. We will see you at"
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
                msg_id=msg_id,
                event_type="reservation",
                instructor=maybe_strip(match.group(1)),
                location=maybe_strip(match.group(2).split("-")[0]),
                timestamp=get_timestamp(time, meridiem, date),
                time=time,
                meridiem=meridiem,
                day_of_week=maybe_strip(match.group(5)),
                date=date,
            )
        )
    return calendar_events


def get_cancellations(service, start_date_str):
    print("gathering cancellations")
    query = f'from:info@heatwise-studio.com subject:"Reservation canceled" after:{start_date_str}'
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
                msg_id=msg_id,
                event_type="cancellation",
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


def main(gmail_service):
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=LOOK_BACK_DAYS)).strftime("%Y/%m/%d")
    reservations = get_reservations(gmail_service, start_date)
    reservations.extend(get_wait_list_reservations(gmail_service, start_date))
    cancellations = get_cancellations(gmail_service, start_date)
    cancelled_timestamps = set([e.timestamp for e in cancellations])
    print(
        f"reservations count={len(reservations)}, cancelled timestamps=",
        cancelled_timestamps,
    )

    # TODO: handle case where person cancels then re-registers; look at email sent time
    reservations = [r for r in reservations if r.timestamp not in cancelled_timestamps]
    print(f"reservations count after cancellations={ len(reservations)}")
    future_reservations = [e for e in reservations if e.timestamp > today.timestamp()]
    future_reservations.sort(key=lambda e: e.timestamp)

    print(f"future_reservations count={len(future_reservations)}")

    if len(future_reservations) > 0:
        next_event = future_reservations[0]
        save_ppm_file(next_event.time + next_event.meridiem)
        save_events_for_frontend(future_reservations)
        create_calendar(
            json.loads(get_events_json(future_reservations)),
            get_public_file_path("yoga.ics"),
        )
        upload_to_s3(get_public_file_path('yoga.ics'), 'yoga.ics')
        upload_to_s3(get_public_file_path("yoga.ppm"), 'yoga.ppm')
        upload_to_s3(get_public_file_path("yoga.json"), 'yoga.json')
    return gmail_service


if __name__ == "__main__":
    events = main(get_service())
    print("Done.")
