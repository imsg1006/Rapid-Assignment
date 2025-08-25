import pytest
from datetime import datetime
from app.schemas import (
    UserCreate, 
    UserResponse, 
    Token, 
    TokenData,
    ImageRequest, 
    ImageResponse,
    SearchResponse,
    DashboardEntry,
    HistoryBase,
    HistoryCreate,
    HistoryResponse
)

class TestUserSchemas:
    """Test cases for user-related schemas."""
    
    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        user_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        user = UserCreate(**user_data)
        
        assert user.username == "testuser"
        assert user.password == "testpass123"

    def test_user_create_schema_validation(self):
        """Test UserCreate schema validation rules."""
        # Valid data
        valid_data = {"username": "validuser", "password": "validpass"}
        user = UserCreate(**valid_data)
        assert user.username == "validuser"
        
        # Test username length constraints
        with pytest.raises(ValueError):
            UserCreate(username="", password="testpass")
        
        # Test password length constraints
        with pytest.raises(ValueError):
            UserCreate(username="testuser", password="")

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        user_data = {
            "id": 1,
            "username": "testuser",
            "is_admin": False,
            "created_at": datetime.now()
        }
        user = UserResponse(**user_data)
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.is_admin is False
        assert user.created_at == user_data["created_at"]

class TestTokenSchemas:
    """Test cases for token-related schemas."""
    
    def test_token_schema(self):
        """Test Token schema."""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        token = Token(**token_data)
        
        assert token.access_token == token_data["access_token"]
        assert token.token_type == "bearer"

    def test_token_data_schema(self):
        """Test TokenData schema."""
        # With username
        token_data = {
            "username": "testuser",
            "is_admin": False
        }
        token = TokenData(**token_data)
        
        assert token.username == "testuser"
        assert token.is_admin is False
        
        # Without username (optional)
        token_data_no_username = {"is_admin": True}
        token = TokenData(**token_data_no_username)
        
        assert token.username is None
        assert token.is_admin is True

class TestImageSchemas:
    """Test cases for image-related schemas."""
    
    def test_image_request_schema(self):
        """Test ImageRequest schema."""
        image_data = {"prompt": "A beautiful sunset"}
        image = ImageRequest(**image_data)
        
        assert image.prompt == "A beautiful sunset"

    def test_image_request_validation(self):
        """Test ImageRequest validation rules."""
        # Valid prompt
        valid_data = {"prompt": "A beautiful sunset"}
        image = ImageRequest(**valid_data)
        assert image.prompt == "A beautiful sunset"
        
        # Empty prompt should fail
        with pytest.raises(ValueError):
            ImageRequest(prompt="")

    def test_image_response_schema(self):
        """Test ImageResponse schema."""
        image_data = {
            "id": 1,
            "prompt": "A beautiful sunset",
            "image_url": "https://example.com/sunset.jpg",
            "timestamp": datetime.now(),
            "user_id": 1
        }
        image = ImageResponse(**image_data)
        
        assert image.id == 1
        assert image.prompt == "A beautiful sunset"
        assert image.image_url == "https://example.com/sunset.jpg"
        assert image.user_id == 1
        assert image.timestamp == image_data["timestamp"]

class TestSearchSchemas:
    """Test cases for search-related schemas."""
    
    def test_search_response_schema(self):
        """Test SearchResponse schema."""
        search_data = {
            "id": 1,
            "query": "test query",
            "results": '[{"title": "Test", "body": "Content"}]',
            "timestamp": datetime.now(),
            "user_id": 1
        }
        search = SearchResponse(**search_data)
        
        assert search.id == 1
        assert search.query == "test query"
        assert search.results == search_data["results"]
        assert search.user_id == 1
        assert search.timestamp == search_data["timestamp"]

class TestDashboardSchemas:
    """Test cases for dashboard-related schemas."""
    
    def test_dashboard_entry_schema(self):
        """Test DashboardEntry schema."""
        # Create sample search and image responses
        search_response = SearchResponse(
            id=1,
            query="test query",
            results="[]",
            timestamp=datetime.now(),
            user_id=1
        )
        
        image_response = ImageResponse(
            id=1,
            prompt="test prompt",
            image_url="https://example.com/image.jpg",
            timestamp=datetime.now(),
            user_id=1
        )
        
        dashboard_data = {
            "searches": [search_response],
            "images": [image_response]
        }
        
        dashboard = DashboardEntry(**dashboard_data)
        
        assert len(dashboard.searches) == 1
        assert len(dashboard.images) == 1
        assert dashboard.searches[0].query == "test query"
        assert dashboard.images[0].prompt == "test prompt"

class TestHistorySchemas:
    """Test cases for history-related schemas."""
    
    def test_history_base_schema(self):
        """Test HistoryBase schema."""
        history_data = {
            "type": "search",
            "query": "test query",
            "result": "test result",
            "meta_data": "additional info"
        }
        history = HistoryBase(**history_data)
        
        assert history.type == "search"
        assert history.query == "test query"
        assert history.result == "test result"
        assert history.meta_data == "additional info"

    def test_history_create_schema(self):
        """Test HistoryCreate schema."""
        history_data = {
            "type": "image",
            "query": "test prompt",
            "result": "image url",
            "meta_data": None
        }
        history = HistoryCreate(**history_data)
        
        assert history.type == "image"
        assert history.query == "test prompt"
        assert history.result == "image url"
        assert history.meta_data is None

    def test_history_response_schema(self):
        """Test HistoryResponse schema."""
        history_data = {
            "id": 1,
            "type": "search",
            "query": "test query",
            "result": "test result",
            "meta_data": "additional info",
            "user_id": 1,
            "timestamp": datetime.now()
        }
        history = HistoryResponse(**history_data)
        
        assert history.id == 1
        assert history.type == "search"
        assert history.query == "test query"
        assert history.result == "test result"
        assert history.meta_data == "additional info"
        assert history.user_id == 1
        assert history.timestamp == history_data["timestamp"]

class TestSchemaValidation:
    """Test cases for schema validation rules."""
    
    def test_username_validation(self):
        """Test username validation rules."""
        # Valid usernames
        valid_usernames = ["user123", "test_user", "user-name", "user.name"]
        for username in valid_usernames:
            user = UserCreate(username=username, password="testpass")
            assert user.username == username
        
        # Invalid usernames
        invalid_usernames = ["", "a" * 256]  # Too short or too long
        for username in invalid_usernames:
            with pytest.raises(ValueError):
                UserCreate(username=username, password="testpass")

    def test_password_validation(self):
        """Test password validation rules."""
        # Valid passwords
        valid_passwords = ["pass123", "secure_password", "!@#$%^&*()"]
        for password in valid_passwords:
            user = UserCreate(username="testuser", password=password)
            assert user.password == password
        
        # Invalid passwords
        invalid_passwords = ["", "a" * 1001]  # Too short or too long
        for password in invalid_passwords:
            with pytest.raises(ValueError):
                UserCreate(username="testuser", password=password)

    def test_url_validation(self):
        """Test URL validation in schemas."""
        # Valid URLs
        valid_urls = [
            "https://example.com/image.jpg",
            "http://localhost:3000/image.png",
            "https://sub.domain.com/path/to/image.gif"
        ]
        
        for url in valid_urls:
            image = ImageResponse(
                id=1,
                prompt="test",
                image_url=url,
                timestamp=datetime.now(),
                user_id=1
            )
            assert image.image_url == url

    def test_timestamp_validation(self):
        """Test timestamp validation in schemas."""
        # Valid timestamps
        valid_timestamps = [
            datetime.now(),
            datetime(2024, 1, 1, 12, 0, 0),
            datetime.utcnow()
        ]
        
        for timestamp in valid_timestamps:
            user = UserResponse(
                id=1,
                username="testuser",
                is_admin=False,
                created_at=timestamp
            )
            assert user.created_at == timestamp