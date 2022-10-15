import uuid
from enum import IntEnum
from typing import List

from pydantic import BaseModel


class CreateEvent(BaseModel):
    activated: int = 1
    comments: str = "random event from backend"
    eventImage: str = "no image"
    eventType: int = 0
    id: str = uuid.uuid4()
    location: str = "40.6403,22.9356"
    timestamp: float = 1661884529238
    userEmail: str = ""


class EventType(IntEnum):
    FIRE = 0
    EARTHQUAKE = 1
    FLOOD = 2
    OTHER = 3


class SingleEventDetails(BaseModel):
    event_id: str = ''
    point: list = []
    timestamp: float = 0.0



class EventDetails(BaseModel):
    event: List[SingleEventDetails] = []


class Event(BaseModel):
    event_type: EventType = 0
    status_importance: float = 0.0
    master_event_id: str = ''
    master_event_point: list = []
    sub_events: List[EventDetails] = []


class EventsList(BaseModel):
    events: List[Event] = []

    class Config:
        arbitrary_types_allowed = True
