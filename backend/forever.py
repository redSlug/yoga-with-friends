from time import sleep

from client import get_service
from events import main


ONE_MINUTE = 60
"""
ONE_MINUTE interval is well under API call rate limits
https://developers.google.com/gmail/api/reference/quota

calls * quota units / call * minutes / day   < 1,000,000,000 quota units  
30    *              5     * 86400           =    25,920,000 quota units
"""

if __name__ == "__main__":
    gmail_service = get_service()
    while True:
        print("I am awake!")
        main(gmail_service)
        print("I am going to sleep!")
        sleep(ONE_MINUTE)
