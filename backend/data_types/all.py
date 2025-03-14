import json
from dataclasses import dataclass, asdict


@dataclass
class Event:
    msg_id: str
    event_type: str
    instructor: str
    location: str
    timestamp: int
    time: str
    meridiem: str
    day_of_week: str
    date: str  # February 12
