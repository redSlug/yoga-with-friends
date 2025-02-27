import json
from dataclasses import dataclass, asdict


@dataclass
class Event:
    instructor: str
    location: str
    timestamp: float
    time: str
    meridiem: str
    day_of_week: str
    date: str

    def __str__(self):
        return json.dumps(asdict(self))
