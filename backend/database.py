"""SQLAlchemy database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def apply_lightweight_migrations() -> None:
    """Keep existing SQLite demo databases compatible without deleting user data."""
    inspector = inspect(engine)
    if "patch_proposals" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("patch_proposals")}
        if "approved_patch_hash" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE patch_proposals ADD COLUMN approved_patch_hash VARCHAR(64)"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
