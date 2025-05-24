from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import uuid
from fastapi import UploadFile, HTTPException, status

# Initialize MinIO client
try:
    minio_client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE
    )
    # Make a bucket if it doesn't exist.
    found = minio_client.bucket_exists(settings.MINIO_BUCKET_NAME)
    if not found:
        minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
    else:
        print(f"Bucket '{settings.MINIO_BUCKET_NAME}' already exists.")
except Exception as e:
    print(f"Error initializing MinIO client or checking bucket: {e}")
    minio_client = None # Ensure it's None if initialization fails

def generate_file_url(object_name: str) -> str:
    if not minio_client:
        return "" # Or raise an error
    return f"http{'s' if settings.MINIO_SECURE else ''}://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{object_name}"

def upload_file_to_minio(file: UploadFile, bucket_name: str) -> Optional[str]:
    if not minio_client:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MinIO service not available")
    try:
        file_extension = file.filename.split(".")[-1]
        object_name = f"{uuid.uuid4()}.{file_extension}"
        minio_client.put_object(
            bucket_name,
            object_name,
            file.file,
            length=file.size, # Use file.size
            content_type=file.content_type
        )
        return generate_file_url(object_name)
    except S3Error as exc:
        print(f"MinIO S3Error during upload: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload to MinIO: {exc}")
    except Exception as e:
        print(f"Unexpected error during MinIO upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during file upload: {e}")


def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.Event]:
    return db.query(models.Event).order_by(models.Event.event_start_date.asc()).offset(skip).limit(limit).all()

def create_event(db: Session, event_data: schemas.EventCreate,
                 main_poster: Optional[UploadFile] = None,
                 event_photos: Optional[List[UploadFile]] = None) -> models.Event:
    db_event_data = event_data.model_dump() # Use model_dump for Pydantic v2

    main_poster_url = None
    if main_poster:
        main_poster_url = upload_file_to_minio(main_poster, settings.MINIO_BUCKET_NAME)
        if not main_poster_url:
             raise HTTPException(status_code=500, detail="Could not upload main poster.")

    event_photos_urls = []
    if event_photos:
        for photo in event_photos:
            photo_url = upload_file_to_minio(photo, settings.MINIO_BUCKET_NAME)
            if photo_url:
                event_photos_urls.append(photo_url)
            else:
                # Decide on error handling: skip photo, or fail creation
                print(f"Warning: Could not upload one of the event photos: {photo.filename}")


    db_event = models.Event(
        **db_event_data,
        event_main_poster_url=main_poster_url,
        event_photos_urls=event_photos_urls
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event_data: schemas.EventUpdate,
                 main_poster: Optional[UploadFile] = None,
                 event_photos: Optional[List[UploadFile]] = None) -> Optional[models.Event]:
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    update_data = event_data.model_dump(exclude_unset=True) # Use model_dump

    if main_poster:
        # TODO: Optionally delete old poster from MinIO
        main_poster_url = upload_file_to_minio(main_poster, settings.MINIO_BUCKET_NAME)
        if main_poster_url:
            update_data["event_main_poster_url"] = main_poster_url
        else:
            raise HTTPException(status_code=500, detail="Could not upload new main poster.")


    if event_photos:
        # TODO: Handle updating/replacing event photos more robustly
        # (e.g., deleting old ones, adding new ones)
        new_photos_urls = []
        for photo in event_photos:
            photo_url = upload_file_to_minio(photo, settings.MINIO_BUCKET_NAME)
            if photo_url:
                new_photos_urls.append(photo_url)
        # This example just replaces all old photos with new ones if any are uploaded
        if new_photos_urls:
             update_data["event_photos_urls"] = new_photos_urls
        # For a more granular update, you might need a different approach.

    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int) -> Optional[models.Event]:
    db_event = get_event(db, event_id)
    if db_event:
        # TODO: Delete associated images from MinIO before deleting the event record
        # This requires storing object names or having a way to list objects by event ID.
        db.delete(db_event)
        db.commit()
    return db_event


