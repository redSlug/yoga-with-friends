from ics import Calendar, Event
import json
import datetime
import pytz


def create_calendar(data, filepath):
    calendar = Calendar()
    for item in data:
        timestamp = item["timestamp"]
        location = item["location"]
        instructor = item["instructor"]
        enrolled_name = f"Yoga in {location} with {instructor}"
        waitlisted_name = f"Waitlisted with {instructor}"
        is_waitlisted = item['waitlisted'] == True

        event = Event()
        event.name = waitlisted_name if is_waitlisted else enrolled_name
        # Creates time in UTC timezone because it's what calendar expects
        begin_time = datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc)
        event.begin = begin_time
        event.end = begin_time + datetime.timedelta(hours=1)
        calendar.events.add(event)

    with open(filepath, "w") as f:
        print("saving ICS file to", filepath)
        f.writelines(calendar)


if __name__ == "__main__":
    print("Creating ICS file with example data from example/events_output.json")
    with open("example/events_output.json", "r") as file:
        data = json.load(file)
    create_calendar(data)
