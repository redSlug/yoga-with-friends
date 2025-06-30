# getmail 

Utility for fetching mail from gmail when API key does not exist or is expired.
This utility is configured to retrieve and delete all mail in an inbox.

## Setup
- added email forwarding to a new email address based on filtering
- created an [app password](https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password) for the new email address
- enabled POP for all mail for the new email address

## Run
Commands for fetching mail using [getmail](https://getmail6.org/)
```bash
# activate the getmail program
source ../backend/venv/bin/activate

# fetch mail
getmail --getmaildir .
```