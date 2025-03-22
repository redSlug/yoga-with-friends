import argparse
import base64
import datetime
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from api.email_client import get_service
from data_types.all import Event
from api.calendar_client import publish
from ppm.image import create_text_image, save_should_render, save_render_true, save_render_false

from s3.publisher import upload_file_to_s3
from utils.all import (
    get_timestamp,
    get_cancellation_timestamp,
    get_waitlist_timestamp,
    get_events_json,
    maybe_strip,
)

LOOK_BACK_DAYS = 30


def get_pi_path(file_name):
    return os.path.abspath(Path(Path.cwd().parent.joinpath("pi", file_name)))


def get_assets_file_path(file_name):
    return os.path.abspath(
        Path(Path.cwd().parent.joinpath("frontend", "src", "assets", file_name))
    )


def save_events(file_path: str, events: List[Event]):
    with open(file_path, "w") as f:
        f.write(get_events_json(events))
    print(f"wrote json to file: ", file_path)


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


def get_added_to_waitlist(service, start_date_str):
    print("gathering wait list potential reservations")
    query = f'from:info@heatwise-studio.com subject:"You\'re on the waitlist" after:{start_date_str}'
    messages = search_messages(service, query)
    calendar_events: List[Event] = []

    if not messages:
        print("No matching wait list potential reservation emails found.")
        return calendar_events

    # <p>For now, you have been added to the waitlist for Some Like it Hot with Jeremy Good at
    # 9:00 AM on Monday, March 31.</p>
    pattern = (
        r"with ([a-zA-Z ]+) at (\d+:\d+) (AM|PM) on ([\D+]+?), ([a-zA-Z0-9 ]+).</p>"
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

        instructor = maybe_strip(match.group(1))
        time = maybe_strip(match.group(2))
        meridiem = match.group(3)
        day_of_week = maybe_strip(match.group(4))
        date = maybe_strip(match.group(5))

        calendar_events.append(
            Event(
                msg_id=msg_id,
                event_type="waitlist",
                instructor=instructor,
                location="unknown",
                timestamp=get_timestamp(time, meridiem, date),
                time=time,
                meridiem=meridiem,
                day_of_week=day_of_week,
                date=date,
                waitlisted=True,
            )
        )
    return calendar_events


def get_waitlist_reservations(service, start_date_str, instructors):
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
        location = maybe_strip(match.group(6).split("-")[0])
        timestamp = get_waitlist_timestamp(time, meridiem, month, day)
        instructor = instructors[timestamp] if timestamp in instructors else ""
        calendar_events.append(
            Event(
                msg_id=msg_id,
                event_type="reservation",
                instructor=instructor,
                location=location,
                timestamp=timestamp,
                time=time,
                meridiem=meridiem,
                day_of_week=day_of_week,
                date=f"{month} {day}",
                waitlisted=False,
            )
        )
    return calendar_events


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
                waitlisted=False,
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
                waitlisted=False,
            )
        )
    return cancellation_events


def publish_reservations_for_frontend(file_path: str, events: List[Event]):
    with open(file_path, "w") as f:
        f.write(get_events_json(events))
    upload_file_to_s3(file_path)


@dataclass
class ResultsCounts:
    reservations: int
    added_to_waitlist: int
    waitlist_instructors: int
    reserved_from_waitlist: int
    reserved_timestamps: Optional[int] = None
    all_reservations: Optional[int] = None
    cancellations: Optional[int] = None
    cancelled_timestamps: Optional[int] = None
    all_reservations_minus_cancellations: Optional[int] = None
    future_reservations: Optional[int] = None


def main(gmail_service):
    today = datetime.datetime.now()
    start_date = (today - datetime.timedelta(days=LOOK_BACK_DAYS)).strftime("%Y/%m/%d")
    reservations = get_reservations(gmail_service, start_date)
    added_to_waitlist = get_added_to_waitlist(gmail_service, start_date)
    waitlist_instructors_by_time = {
        e.timestamp: e.instructor for e in added_to_waitlist
    }
    reserved_from_waitlist = get_waitlist_reservations(
        gmail_service, start_date, waitlist_instructors_by_time
    )
    reserved_timestamps = [r.timestamp for r in reserved_from_waitlist]
    results = ResultsCounts(
        reservations=len(reservations),
        added_to_waitlist=len(added_to_waitlist),
        waitlist_instructors=len(waitlist_instructors_by_time),
        reserved_from_waitlist=len(reserved_from_waitlist),
        reserved_timestamps=len(reserved_timestamps),
    )
    reservations.extend(reserved_from_waitlist)
    # NOTE: bug here if multiple reservations with same timestamp at different locations
    [
        reservations.append(r)
        for r in added_to_waitlist
        if r.timestamp not in reserved_timestamps
    ]
    results.all_reservations = len(reservations)
    cancellations = get_cancellations(gmail_service, start_date)
    results.cancellations = len(cancellations)
    cancelled_timestamps = set([e.timestamp for e in cancellations])
    results.cancelled_timestamps = len(cancelled_timestamps)
    # TODO: handle case where person cancels then re-registers; look at email sent time
    reservations = [r for r in reservations if r.timestamp not in cancelled_timestamps]
    results.all_reservations_minus_cancellations = len(reservations)
    future_reservations = [e for e in reservations if e.timestamp > today.timestamp()]
    future_reservations.sort(key=lambda e: e.timestamp)
    results.future_reservations = len(future_reservations)

    print("results", json.dumps(results.__dict__, indent=4))

    if len(future_reservations) == 0:
        print("no future events found")

    next_event = future_reservations[0]
    ppm_text = next_event.time + next_event.meridiem
    create_text_image(get_pi_path("yoga.ppm"), ppm_text)
    save_should_render(get_pi_path("render.txt"), next_event)
    publish("yoga.ics", future_reservations)
    publish_reservations_for_frontend("yoga.json", future_reservations)
    return gmail_service


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yoga with Friends")
    parser.add_argument("--force_render", type=str, help="Force LEDs, enter YES or NO")
    args = parser.parse_args()

    if args.force_render == "YES":
        save_render_true("render.txt")
    elif args.force_render == "NO":
        save_render_false("render.txt")
    else:
        events = main(get_service())

    print("Done.")
