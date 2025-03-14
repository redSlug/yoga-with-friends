import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"


def get_refresh_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", scopes=SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline", prompt="consent", include_granted_scopes="true"
    )

    print(f"Please go to this URL and authorize access: {auth_url}")

    code = input("Enter the authorization code: ")

    flow.fetch_token(code=code)
    credentials = flow.credentials

    print(f"Access token: {credentials.token}")
    print(f"Refresh token: {credentials.refresh_token}")
    token_info = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    with open("token.json", "w", encoding="utf-8") as token_file:
        json.dump(token_info, token_file)  # type: ignore
    return credentials.refresh_token


if __name__ == "__main__":
    refresh_token = get_refresh_token()
    print(f"Your refresh token was saved to token.json")
