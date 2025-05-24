from sqlalchemy import Column, Integer, String, Date, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY # For event_photos
from app.database import Base
import enum

class EventCategory(str, enum.Enum):
    SCIENCE = "Science"
    TECHNOLOGY = "Technology"
    SPORTS = "Sports"
    LITERATURE = "Literature"
    DEBATE = "Debate"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_title = Column(String, nullable=False)
    event_host_name = Column(String, nullable=False)
    event_start_date = Column(Date, nullable=False)
    event_end_date = Column(Date, nullable=False)
    event_category = Column(SAEnum(EventCategory), nullable=True)
    event_main_poster_url = Column(String, nullable=True) # URL from MinIO
    event_description = Column(Text, nullable=True)
    total_organizer = Column(Integer, nullable=True)
    total_participant = Column(Integer, nullable=True)
    total_program = Column(Integer, nullable=True)
    event_photos_urls = Column(ARRAY(String), nullable=True) # URLs from MinIO



