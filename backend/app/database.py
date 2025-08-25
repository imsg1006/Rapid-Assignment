from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Fix: Ensure correct database driver for SQLAlchemy sync engine
db_url = settings.database_url.replace("+asyncpg", "")  # remove async if present

# Create a SQLAlchemy engine with connection pooling
if db_url.startswith('sqlite'):
    # SQLite configuration
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=settings.debug
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections after 5 minutes
        echo=settings.debug   # Log SQL queries in debug mode
    )

# Create a SessionLocal class to get a database session for each request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for your database models
Base = declarative_base()

def get_db():
    """Dependency function to provide a database session"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        return False

def test_database_connection():
    """Test if the database connection works"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {e}")
        return False