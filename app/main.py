from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import events
from app.database import engine, Base, get_db # Ensure get_db is imported if used globally
from app.core.config import settings
from sqlalchemy.orm import Session

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(events.router, prefix=settings.API_V1_STR + "/events", tags=["events"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Event Builder API"}

# Example of how to ensure DB is available (optional, can be removed if get_db is only used in routes)
@app.on_event("startup")
async def startup_event():
    try:
        # Test DB connection
        db: Session = next(get_db())
        db.connection()
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        # Optionally, exit if DB is critical for startup
        # raise RuntimeError("Could not connect to the database.") from e



