import datetime

from data_types.all import Event


def convert_to_datetime(event_data: Event) -> datetime.datetime:
    time_str = event_data.time
    meridiem = event_data.meridiem
    date_str = event_data.date

    hour, minute = map(int, time_str.split(":"))
    if meridiem == "PM" and hour < 12:
        hour += 12
    elif meridiem == "AM" and hour == 12:
        hour = 0

    month_name, day = date_str.split()
    day = int(day)

    month_dict = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }
    month = month_dict[month_name]

    # TODO: intuit based on current and target month and year
    year = datetime.datetime.now().year
    return datetime.datetime(year, month, day, hour, minute)
