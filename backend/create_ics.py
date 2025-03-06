
from ics import Calendar, Event
import json
import datetime
import pytz
import os

def create_file():
    print("Creating ICS file")
    with open('example/events_output.json', 'r') as file:
        data = json.load(file)

    calendar = Calendar()
    for item in data:
        timestamp = item['timestamp']
        location = item['location']
        instructor = item['instructor']
        event = Event()
        event.name = f"Yoga with {instructor} in {location}"
        # Creates time in UTC timezone because it's what calendar expects
        begin_time = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)
        event.begin = begin_time
        event.end = begin_time + datetime.timedelta(hours=1)
        calendar.events.add(event)


    BASE_PATH = os.path.dirname(__file__)
    filepath = os.path.abspath(
        os.path.join(BASE_PATH, "..", "frontend", "src", "data", "yoga_calendar.ics")
    )
    with open(filepath, 'w') as f:
        f.writelines(calendar)


if __name__ == '__main__':
    create_file()