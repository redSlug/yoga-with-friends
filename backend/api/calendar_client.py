from typing import List

from ics import Calendar, Event
from data_types.all import Event as EventType
import datetime
import pytz

from s3.publisher import upload_file_to_s3


def publish(file_path: str, data: List[EventType]):
    calendar = Calendar()
    for item in data:
        timestamp = item.timestamp
        location = item.location
        instructor = item.instructor
        enrolled_name = f"Yoga in {location} with {instructor}"
        waitlisted_name = f"Waitlisted with {instructor}"
        is_waitlisted = item.waitlisted == True

        event = Event()
        event.name = waitlisted_name if is_waitlisted else enrolled_name
        # Creates time in UTC timezone because it's what calendar expects
        begin_time = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)
        event.begin = begin_time
        event.end = begin_time + datetime.timedelta(hours=1)
        calendar.events.add(event)
    with open(file_path, "w") as f:
        f.writelines(calendar)
    upload_file_to_s3(file_path)
