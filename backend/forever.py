from time import sleep

from events import main

ONE_MINUTE = 60

if __name__ == "__main__":
    while True:
        print("I am awake!")
        main()
        print("I am going to sleep!")
        sleep(ONE_MINUTE)
