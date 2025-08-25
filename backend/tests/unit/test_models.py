import pytest
from sqlalchemy.orm import Session
from app.models import User, SearchHistory, ImageHistory
from app.security import get_password_hash
from datetime import datetime

class TestUserModel:
    """Test cases for User model."""
    
    def test_create_user(self, db_session: Session):
        """Test creating a basic user."""
        user = User(
            username="testuser",
            hashed_password=get_password_hash("testpass123")
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_admin is False
        assert user.created_at is not None

    def test_create_admin_user(self, db_session: Session):
        """Test creating an admin user."""
        user = User(
            username="adminuser",
            hashed_password=get_password_hash("adminpass123"),
            is_admin=True
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.is_admin is True

    def test_user_username_uniqueness(self, db_session: Session):
        """Test that usernames must be unique."""
        user1 = User(
            username="duplicate",
            hashed_password=get_password_hash("pass1")
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            username="duplicate",
            hashed_password=get_password_hash("pass2")
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()
        
        db_session.rollback()

    def test_user_relationships(self, db_session: Session):
        """Test user relationships with search and image history."""
        user = User(
            username="testuser",
            hashed_password=get_password_hash("testpass123")
        )
        db_session.add(user)
        db_session.commit()
        
        # Test search relationship
        search = SearchHistory(
            query="test query",
            results="[]",
            user_id=user.id
        )
        db_session.add(search)
        
        # Test image relationship
        image = ImageHistory(
            prompt="test prompt",
            image_url="https://example.com/image.jpg",
            user_id=user.id
        )
        db_session.add(image)
        db_session.commit()
        
        # Verify relationships
        assert len(user.searches) == 1
        assert len(user.images) == 1
        assert user.searches[0].query == "test query"
        assert user.images[0].prompt == "test prompt"

class TestSearchHistoryModel:
    """Test cases for SearchHistory model."""
    
    def test_create_search_history(self, db_session: Session, test_user: User):
        """Test creating search history entry."""
        search = SearchHistory(
            query="test search query",
            results='[{"title": "Test", "body": "Content"}]',
            user_id=test_user.id
        )
        db_session.add(search)
        db_session.commit()
        
        assert search.id is not None
        assert search.query == "test search query"
        assert search.user_id == test_user.id
        assert search.timestamp is not None

    def test_search_history_user_relationship(self, db_session: Session, test_user: User):
        """Test search history relationship with user."""
        search = SearchHistory(
            query="test query",
            results="[]",
            user_id=test_user.id
        )
        db_session.add(search)
        db_session.commit()
        
        assert search.owner.id == test_user.id
        assert search.owner.username == test_user.username

class TestImageHistoryModel:
    """Test cases for ImageHistory model."""
    
    def test_create_image_history(self, db_session: Session, test_user: User):
        """Test creating image history entry."""
        image = ImageHistory(
            prompt="A beautiful sunset",
            image_url="https://example.com/sunset.jpg",
            user_id=test_user.id
        )
        db_session.add(image)
        db_session.commit()
        
        assert image.id is not None
        assert image.prompt == "A beautiful sunset"
        assert image.image_url == "https://example.com/sunset.jpg"
        assert image.user_id == test_user.id
        assert image.timestamp is not None

    def test_image_history_user_relationship(self, db_session: Session, test_user: User):
        """Test image history relationship with user."""
        image = ImageHistory(
            prompt="test prompt",
            image_url="https://example.com/image.jpg",
            user_id=test_user.id
        )
        db_session.add(image)
        db_session.commit()
        
        assert image.owner.id == test_user.id
        assert image.owner.username == test_user.username

    def test_cascade_delete(self, db_session: Session, test_user: User):
        """Test that deleting a user cascades to their history."""
        # Create search and image history
        search = SearchHistory(
            query="test query",
            results="[]",
            user_id=test_user.id
        )
        image = ImageHistory(
            prompt="test prompt",
            image_url="https://example.com/image.jpg",
            user_id=test_user.id
        )
        db_session.add_all([search, image])
        db_session.commit()
        
        # Verify they exist
        assert db_session.query(SearchHistory).filter_by(user_id=test_user.id).count() == 1
        assert db_session.query(ImageHistory).filter_by(user_id=test_user.id).count() == 1
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify history is deleted
        assert db_session.query(SearchHistory).filter_by(user_id=test_user.id).count() == 0
        assert db_session.query(ImageHistory).filter_by(user_id=test_user.id).count() == 0