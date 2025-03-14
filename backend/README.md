# yoga-with-friends backend

## Setup

### Get credentials
1) Go to [google cloud](https://console.cloud.google.com/), create a project and enable Gmail API
2) Create "OAuth Client ID" for "Desktop app", and save credentials to `credentials.json` in 
   the format of [example_credentials.json](example_credentials.json)
3) Run `python get_refresh_token.py` from a desktop client to get the refresh token
4) Copy `token.json` to the `backend` directory on the server

### Install packages
```bash
python3.10 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python forever.py
```

## Future Ideas / Enhancements
* handle "Reservation canceled" by skipping them and removing them from the calendar
* stop creating redundant calendar events when run multiple times
* intuit year in get_date
* persist ics UUIDs in a storage - better yet use the ID from the email (to not create dup 
  events on calendar)
* code to handle case where "google Token has been expired or revoked" 

## Troubleshooting
- if you encounter `ModuleNotFoundError: No module named 'google'`, there could a discrepancy
  between the python version you used to create your virtualenv and run the script
- to check date on OS X, run `date -r 1742301900`
- "google Token has been expired or revoked" the temporary workaround is to delete the `token.json`
- if you encounter `/google/auth/transport/requests.py ImportError: The requests 
library is not installed` it could mean you have given a module a name that overlaps with a
  lib name
