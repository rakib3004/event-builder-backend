from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import date
from app.models import EventCategory # Import Enum

class EventBase(BaseModel):
    event_title: str
    event_host_name: str
    event_start_date: date
    event_end_date: date
    event_category: Optional[EventCategory] = None
    event_description: Optional[str] = None
    total_organizer: Optional[int] = None
    total_participant: Optional[int] = None
    total_program: Optional[int] = None

class EventCreate(EventBase):
    pass # Main poster and photos will be handled separately via UploadFile

class EventUpdate(EventBase):
    event_title: Optional[str] = None
    event_host_name: Optional[str] = None
    event_start_date: Optional[date] = None
    event_end_date: Optional[date] = None
    # Allow updating all fields

class EventInDBBase(EventBase):
    id: int
    event_main_poster_url: Optional[str] = None
    event_photos_urls: Optional[List[str]] = []

    class Config:
        from_attributes = True #  For SQLAlchemy model compatibility (formerly orm_mode)

class Event(EventInDBBase):
    pass

class EventList(BaseModel): # For dashboard table
    id: int
    event_title: str
    event_host_name: str
    event_start_date: date
    event_end_date: date
    event_category: Optional[EventCategory] = None
    event_main_poster_url: Optional[str] = None
    total_organizer: Optional[int] = None
    total_participant: Optional[int] = None
    total_program: Optional[int] = None

    class Config:
        from_attributes = True



