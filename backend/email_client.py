import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_credentials(token_path):
    creds = None
    with open(token_path, "r") as token_file:
        token_data = json.load(token_file)
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes"),
        )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as token_file:
            token_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            }
            json.dump(token_data, token_file)

    return creds


def get_service():
    credentials = get_credentials("token.json")
    return build("gmail", "v1", credentials=credentials)
