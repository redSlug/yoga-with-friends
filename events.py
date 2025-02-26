import json
import os
import re
import datetime
from dataclasses import dataclass
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
LOOKBACK_DAYS = 2


@dataclass
class Event:
    time: str
    meridiem: str
    day_of_week: str
    date: str


def get_gmail_service():
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
    return build("gmail", "v1", credentials=creds)


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
    service = get_gmail_service()
    two_days_ago = datetime.datetime.now() - datetime.timedelta(days=LOOKBACK_DAYS)
    date_str = two_days_ago.strftime("%Y/%m/%d")
    query = f'from:info@heatwise-studio.com subject:"Your spot has been reserved" after:{date_str}'
    messages = search_messages(service, query)

    if not messages:
        print("No matching emails found.")
        return

    # Raw example data
    # We will see you at <strong>8:45 AM</strong> on <strong>Tuesday</strong>, <strong>March 4</strong>.</p>
    pattern = r"<strong>(\d+:\d+) (AM|PM)</strong> on <strong>(.*?)</strong>, <strong>(.*?)</strong>"

    events: List[Event]  = []
    for msg in messages:
        print("messages", msg)
        msg_id = msg["id"]
        content = get_message_content(service, msg_id)

        if content:
            match = re.search(pattern, content)
            if match:
                events.append(
                    {
                        "time": match.group(1),
                        "meridiem": match.group(2),
                        "day_of_week": match.group(3),
                        "date": match.group(4),
                    }
                )
    return events


if __name__ == "__main__":
    events = main()
    print(json.dumps(events))
