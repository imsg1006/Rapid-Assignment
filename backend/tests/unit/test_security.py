import pytest
from datetime import datetime, timedelta
from app.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    decode_access_token
)
from app.config import settings

class TestPasswordHashing:
    """Test cases for password hashing functions."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) > len(password)
        
        # Should verify correctly
        assert verify_password(password, hashed) is True
        
        # Wrong password should not verify
        assert verify_password("wrongpassword", hashed) is False
        assert verify_password("", hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password produces different hashes."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # Both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_empty_password(self):
        """Test handling of empty passwords."""
        empty_hash = get_password_hash("")
        assert verify_password("", empty_hash) is True
        assert verify_password("notempty", empty_hash) is False

    def test_special_characters_password(self):
        """Test passwords with special characters."""
        special_password = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = get_password_hash(special_password)
        
        assert verify_password(special_password, hashed) is True
        assert verify_password("!@#$%^&*()_+-=[]{}|;:,.<>", hashed) is False

class TestJWTTokenCreation:
    """Test cases for JWT token creation."""
    
    def test_create_access_token(self):
        """Test basic token creation."""
        data = {"sub": "testuser", "is_admin": False}
        token = create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_create_access_token_with_custom_expiry(self):
        """Test token creation with custom expiry."""
        data = {"sub": "testuser", "is_admin": True}
        custom_expiry = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_expiry)
        
        # Decode and check expiry
        decoded = decode_access_token(token)
        assert decoded["sub"] == "testuser"
        assert decoded["is_admin"] is True
        
        # Check that expiry is roughly 2 hours from now
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        # Should be within 2 hours (with some tolerance)
        time_diff = exp_datetime - now
        assert timedelta(hours=1, minutes=50) <= time_diff <= timedelta(hours=2, minutes=10)

    def test_create_access_token_default_expiry(self):
        """Test token creation with default expiry from settings."""
        data = {"sub": "testuser", "is_admin": False}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        # Should be within default expiry time from settings
        expected_expiry = timedelta(minutes=settings.access_token_expire_minutes)
        time_diff = exp_datetime - now
        
        # Allow some tolerance for test execution time
        tolerance = timedelta(minutes=1)
        assert (expected_expiry - tolerance) <= time_diff <= (expected_expiry + tolerance)

    def test_token_payload_integrity(self):
        """Test that token payload contains all expected data."""
        data = {"sub": "testuser", "is_admin": True, "custom_field": "custom_value"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        # Check all original data is preserved
        assert decoded["sub"] == "testuser"
        assert decoded["is_admin"] is True
        assert decoded["custom_field"] == "custom_value"
        
        # Check that exp field is added
        assert "exp" in decoded

class TestJWTTokenDecoding:
    """Test cases for JWT token decoding and validation."""
    
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser", "is_admin": False}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "testuser"
        assert decoded["is_admin"] is False
        assert "exp" in decoded

    def test_decode_token_with_admin_flag(self):
        """Test decoding token with admin flag."""
        data = {"sub": "adminuser", "is_admin": True}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded["sub"] == "adminuser"
        assert decoded["is_admin"] is True

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):  # Should raise HTTPException
            decode_access_token(invalid_token)

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        data = {"sub": "testuser", "is_admin": False}
        # Create token with very short expiry
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        # Wait for token to expire
        import time
        time.sleep(2)
        
        with pytest.raises(Exception):  # Should raise HTTPException for expired token
            decode_access_token(expired_token)

    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        malformed_token = "not.a.valid.jwt.token"
        
        with pytest.raises(Exception):
            decode_access_token(malformed_token)

class TestSecurityIntegration:
    """Integration tests for security functions."""
    
    def test_full_auth_flow(self):
        """Test complete authentication flow."""
        # 1. Create user with hashed password
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        # 2. Verify password
        assert verify_password(password, hashed) is True
        
        # 3. Create access token
        user_data = {"sub": "testuser", "is_admin": False}
        token = create_access_token(user_data)
        
        # 4. Decode and verify token
        decoded = decode_access_token(token)
        assert decoded["sub"] == "testuser"
        assert decoded["is_admin"] is False
        
        # 5. Verify token is not expired
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        assert exp_datetime > now

    def test_admin_user_flow(self):
        """Test authentication flow for admin user."""
        # 1. Create admin user
        password = "adminpass123"
        hashed = get_password_hash(password)
        
        # 2. Verify password
        assert verify_password(password, hashed) is True
        
        # 3. Create admin token
        admin_data = {"sub": "adminuser", "is_admin": True}
        token = create_access_token(admin_data)
        
        # 4. Decode and verify admin token
        decoded = decode_access_token(token)
        assert decoded["sub"] == "adminuser"
        assert decoded["is_admin"] is True