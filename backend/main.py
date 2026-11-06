"""FastAPI Main Application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base, apply_lightweight_migrations
from .api.routes import router

# Create database tables automatically
Base.metadata.create_all(bind=engine)
apply_lightweight_migrations()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real AI-Powered Bug Triage & Resolution Workflow integrated with Switch Collaboration"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
