import datetime
import json
from typing import List

from data_types.all import Event


def _get_date(time_str, meridiem, date_str) -> datetime:
    hour, minute = map(int, time_str.split(":"))
    if meridiem == "PM" and hour < 12:
        hour += 12
    elif meridiem == "AM" and hour == 12:
        hour = 0

    month_name, day = date_str.split()
    day = int(day)

    month_dict = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    month = month_dict[month_name]

    # TODO: intuit based on current and target month and year
    year = datetime.datetime.now().year
    return datetime.datetime(year, month, day, hour, minute)


def get_timestamp(time_str, meridiem, date_str) -> int:
    return int(_get_date(time_str, meridiem, date_str).timestamp())


def get_waitlist_timestamp(time_str, meridiem, month, day) -> int:
    date_str = f"{month} {day}"
    return int(_get_date(time_str, meridiem, date_str).timestamp())


def get_cancellation_timestamp(date, time_str, meridiem):
    date_str = date.replace("/", "-") + "-" + time_str + "-" + meridiem
    date_object = datetime.datetime.strptime(date_str, "%m-%d-%Y-%H:%M-%p")
    return int(date_object.timestamp())


def convert_to_datetime(event: Event) -> datetime:
    return _get_date(event.time, event.meridiem, event.date)


def get_events_json(events: List[Event]) -> str:
    return json.dumps([event.__dict__ for event in events])


def maybe_strip(s):
    try:
        return s.strip()
    except s:
        return ""
