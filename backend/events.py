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
from utils.get_date import convert_to_datetime, get_timestamp

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
    filepath = os.path.abspath(os.path.join(BASE_PATH, "..", "frontend", "src", "data", "events.json"))
    with open(filepath, 'w') as f:
        f.write(json.dumps([event.__dict__ for event in events]))
    print(f'wrote json to file: ', filepath)


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
    print("creating calendar event")
    event: Dict[str, Any] = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_datetime.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime.isoformat(),
            "timeZone": timezone,
        },
    }
    try:
        event = service.events().insert(calendarId="primary", body=event).execute()
        print("created calendar event", event)
        return event
    except Exception as error:
        print(f"An error occurred: {error}")
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


def main():
    gmail_service = get_gmail_service()
    today = datetime.datetime.now()
    two_days_ago = today - datetime.timedelta(days=LOOKBACK_DAYS)
    date_str = two_days_ago.strftime("%Y/%m/%d")
    query = f'from:info@heatwise-studio.com subject:"Your spot has been reserved" after:{date_str}'
    messages = search_messages(gmail_service, query)

    if not messages:
        print("No matching emails found.")
        return

    # Created using https://python-fiddle.com/tools/regex and Raw example data:
    # We will see you at <strong>8:45 AM</strong> on <strong>Tuesday</strong>, <strong>March 4</strong>.</p>
    pattern = (r"with <strong>([a-zA-Z ]*?)</strong> at <strong>(.*?)</strong>. We will see you at"
               r" <strong>(\d+:\d+) (AM|PM)</strong> on <strong>("
               r".*?)</strong>, <strong>(.*?)</strong>")

    calendar_events: List[Event] = []
    for msg in messages:
        print("messages", msg)
        msg_id = msg["id"]
        content = get_message_content(gmail_service, msg_id)

        if content:
            match = re.search(pattern, content)
            if match:
                time = match.group(3)
                meridiem = match.group(4)
                date = match.group(6)

                calendar_events.append(
                    Event(
                        instructor=match.group(1),
                        location=match.group(2).split('-')[0],
                        timestamp=get_timestamp(time, meridiem, date),
                        time=time,
                        meridiem=meridiem,
                        day_of_week=match.group(5),
                        date=date,
                    )
                )
            else:
                print("no match")

    calendar_events = [e for e in calendar_events if e.timestamp > today.timestamp()]
    calendar_events.sort(key=lambda e: e.timestamp)

    if len(calendar_events) > 0:
        next_event = calendar_events[0]
        save_ppm_file(next_event.time + next_event.meridiem)
        save_events_for_frontend(calendar_events)
    calendar_service = get_calendar_service()

    for event in calendar_events:
        print("creating event", event)
        start_datetime = convert_to_datetime(event)
        if start_datetime < datetime.datetime.now():
            print("skipping past event", event)
            continue

        create_calendar_event(
            service=calendar_service,
            summary="Yoga Class in " + event.location,
            location="",
            description="with instructor " + event.instructor,
            start_datetime=start_datetime,
            end_datetime=start_datetime + datetime.timedelta(minutes=60),
            timezone="America/New_York",
        )
    return calendar_events


if __name__ == "__main__":
    events = main()
    print(events)
