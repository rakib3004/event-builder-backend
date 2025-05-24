from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
from app import crud, models, schemas
from datetime import date  # <-- Add this line
from app.database import get_db
from app.models import EventCategory # Import Enum for form field

router = APIRouter()

@router.post("/", response_model=schemas.Event)
async def create_event_endpoint(
    event_title: Annotated[str, Form()],
    event_host_name: Annotated[str, Form()],
    event_start_date: Annotated[date, Form()],
    event_end_date: Annotated[date, Form()],
    event_category: Annotated[Optional[EventCategory], Form()] = None,
    event_description: Annotated[Optional[str], Form()] = None,
    total_organizer: Annotated[Optional[int], Form()] = None,
    total_participant: Annotated[Optional[int], Form()] = None,
    total_program: Annotated[Optional[int], Form()] = None,
    event_main_poster: Annotated[Optional[UploadFile], File()] = None,
    event_photos: Annotated[Optional[List[UploadFile]], File()] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new event.
    Mandatory fields: event_title, event_host_name, event_start_date, event_end_date.
    """
    if not all([event_title, event_host_name, event_start_date, event_end_date]):
        raise HTTPException(status_code=400, detail="Mandatory fields are missing.")

    event_data = schemas.EventCreate(
        event_title=event_title,
        event_host_name=event_host_name,
        event_start_date=event_start_date,
        event_end_date=event_end_date,
        event_category=event_category,
        event_description=event_description,
        total_organizer=total_organizer,
        total_participant=total_participant,
        total_program=total_program
    )
    try:
        return crud.create_event(db=db, event_data=event_data, main_poster=event_main_poster, event_photos=event_photos)
    except HTTPException as e:
        raise e # Re-raise HTTPExceptions from crud
    except Exception as e:
        # Log the exception e
        print(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the event.")


@router.get("/", response_model=List[schemas.EventList]) # Use EventList for dashboard
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events

@router.get("/{event_id}", response_model=schemas.Event) # Full event details for show/edit
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.put("/{event_id}", response_model=schemas.Event)
async def update_event_endpoint(
    event_id: int,
    event_title: Annotated[Optional[str], Form()] = None,
    event_host_name: Annotated[Optional[str], Form()] = None,
    event_start_date: Annotated[Optional[date], Form()] = None,
    event_end_date: Annotated[Optional[date], Form()] = None,
    event_category: Annotated[Optional[EventCategory], Form()] = None,
    event_description: Annotated[Optional[str], Form()] = None,
    total_organizer: Annotated[Optional[int], Form()] = None,
    total_participant: Annotated[Optional[int], Form()] = None,
    total_program: Annotated[Optional[int], Form()] = None,
    event_main_poster: Annotated[Optional[UploadFile], File()] = None,
    event_photos: Annotated[Optional[List[UploadFile]], File()] = None,
    db: Session = Depends(get_db)
):
    db_event = crud.get_event(db, event_id=event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data_dict = {
        "event_title": event_title,
        "event_host_name": event_host_name,
        "event_start_date": event_start_date,
        "event_end_date": event_end_date,
        "event_category": event_category,
        "event_description": event_description,
        "total_organizer": total_organizer,
        "total_participant": total_participant,
        "total_program": total_program,
    }
    # Filter out None values to only update provided fields
    update_data_filtered = {k: v for k, v in update_data_dict.items() if v is not None}

    event_update_schema = schemas.EventUpdate(**update_data_filtered)

    try:
        updated_event = crud.update_event(
            db=db,
            event_id=event_id,
            event_data=event_update_schema,
            main_poster=event_main_poster,
            event_photos=event_photos
        )
        return updated_event
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error updating event: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the event.")


@router.delete("/{event_id}", response_model=schemas.Event)
def delete_event_endpoint(event_id: int, db: Session = Depends(get_db)):
    deleted_event = crud.delete_event(db, event_id=event_id)
    if deleted_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return deleted_event

# Endpoints for Gallery and Timeline (can reuse read_events and read_event or create specific ones if formatting differs greatly)

@router.get("/gallery/all", response_model=List[schemas.Event]) # Example for gallery, might need specific formatting
def get_gallery_events(db: Session = Depends(get_db)):
    # Returns all event details, frontend will format it
    return crud.get_events(db, limit=1000) # Adjust limit as needed

# Timeline endpoint can reuse read_event(event_id) as it shows details for one event.
# Or, if you want a timeline of multiple events, you'd have a different structure.
# For now, assuming timeline refers to a single event's detailed view.




