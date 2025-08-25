import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import get_password_hash
import os
import tempfile

# Test database setup
@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Use SQLite for testing
    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up test database
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
def db_session(test_engine):
    """Create database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        hashed_password=get_password_hash("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user."""
    user = User(
        username="adminuser",
        hashed_password=get_password_hash("adminpass123"),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def client(db_session):
    """Create FastAPI test client."""
    # Override database dependency for testing
    def override_get_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise
        finally:
            pass  # Don't close session in tests
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, test_admin_user):
    """Get authentication headers for admin user."""
    response = client.post("/auth/token", data={
        "username": "adminuser",
        "password": "adminpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Async support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()