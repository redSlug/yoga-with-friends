# yoga-with-friends - backend
Retrieves email and publishes extracted yoga enrollments in JSON, PPM, ICS formats. 

## Setup
### Setup email credentials
1) Go to [google cloud](https://console.cloud.google.com/), create a project and enable Gmail API
2) Create "OAuth Client ID" for "Desktop app", and save credentials to `credentials.json` in 
   the format of [example_credentials.json](example_credentials.json)
3) Run `python get_refresh_token.py` from a desktop client to get the refresh token
4) Copy `token.json` to the `backend` directory on the server

### Setup bucket credentials
Copy [example_env](example_env) to `.env` and populate

### Install packages
```bash
python3.10 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Install cron
See [pi README](../pi/README.md)

## Future Ideas / Enhancements
* intuit year in get_date
* use persisted events to reduce the timeframe of the calendar client 
  query

## Troubleshooting
- if you encounter `ModuleNotFoundError: No module named 'google'`, there could a discrepancy
  between the python version you used to create your virtualenv and run the script
- to check date on OS X, run `date -r 1742301900`
- "google Token has been expired or revoked" the temporary workaround is to delete the `token.json`
- if you encounter `/google/auth/transport/requests.py ImportError: The requests 
library is not installed` it could mean you have given a module a name that overlaps with a
  lib name
