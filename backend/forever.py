from time import sleep

from email_client import get_service
from events import main

ONE_MINUTE = 60

if __name__ == "__main__":
    gmail_service = get_service()
    while True:
        print("I am awake!")
        main(gmail_service)
        print("I am going to sleep!")
        sleep(ONE_MINUTE)
