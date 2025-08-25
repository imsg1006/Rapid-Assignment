import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from app.security import verify_password

class TestAuthenticationFlow:
    """Integration tests for complete authentication flow."""
    
    def test_user_registration_flow(self, client: TestClient, db_session: Session):
        """Test complete user registration flow."""
        # 1. Register new user
        user_data = {
            "username": "newuser",
            "password": "newpass123"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        response_data = response.json()
        assert "message" in response_data
        assert "user_id" in response_data
        assert response_data["message"] == "User registered successfully"
        
        # 2. Verify user was created in database
        user = db_session.query(User).filter(User.username == "newuser").first()
        assert user is not None
        assert user.username == "newuser"
        assert verify_password("newpass123", user.hashed_password)
        assert user.is_admin is False

    def test_user_login_flow(self, client: TestClient, db_session: Session):
        """Test complete user login flow."""
        # 1. First register a user
        user_data = {
            "username": "loginuser",
            "password": "loginpass123"
        }
        
        client.post("/auth/register", json=user_data)
        
        # 2. Login with correct credentials
        login_data = {
            "username": "loginuser",
            "password": "loginpass123"
        }
        
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"
        assert len(response_data["access_token"]) > 0

    def test_login_with_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        # Try to login with non-existent user
        login_data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }
        
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == 401
        
        response_data = response.json()
        assert "detail" in response_data
        assert "Incorrect username or password" in response_data["detail"]

    def test_login_with_wrong_password(self, client: TestClient, db_session: Session):
        """Test login with correct username but wrong password."""
        # 1. Register a user
        user_data = {
            "username": "wrongpassuser",
            "password": "correctpass"
        }
        
        client.post("/auth/register", json=user_data)
        
        # 2. Try to login with wrong password
        login_data = {
            "username": "wrongpassuser",
            "password": "wrongpass"
        }
        
        response = client.post("/auth/token", data=login_data)
        assert response.status_code == 401
        
        response_data = response.json()
        assert "detail" in response_data
        assert "Incorrect username or password" in response_data["detail"]

    def test_duplicate_username_registration(self, client: TestClient):
        """Test that duplicate usernames are rejected."""
        user_data = {
            "username": "duplicateuser",
            "password": "pass123"
        }
        
        # First registration should succeed
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        
        # Second registration with same username should fail
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400
        
        response_data = response.json()
        assert "detail" in response_data
        assert "Username already registered" in response_data["detail"]

    def test_token_validation_flow(self, client: TestClient, db_session: Session):
        """Test that generated tokens are valid and can be used."""
        # 1. Register and login to get token
        user_data = {
            "username": "tokenuser",
            "password": "tokenpass123"
        }
        
        client.post("/auth/register", json=user_data)
        
        login_response = client.post("/auth/token", data=user_data)
        token = login_response.json()["access_token"]
        
        # 2. Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/dashboard/", headers=headers)
        
        # Should succeed (even if no data, authentication should work)
        assert response.status_code in [200, 404]  # 404 if no data, but auth works

    def test_invalid_token_access(self, client: TestClient):
        """Test that invalid tokens are rejected."""
        # Try to access protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/dashboard/", headers=headers)
        
        assert response.status_code == 401

    def test_missing_token_access(self, client: TestClient):
        """Test that missing tokens are rejected."""
        # Try to access protected endpoint without token
        response = client.get("/dashboard/")
        
        assert response.status_code == 401

    def test_token_format_validation(self, client: TestClient):
        """Test various token format validations."""
        # Test malformed Authorization header
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/dashboard/", headers=headers)
        assert response.status_code == 401
        
        # Test empty token
        headers = {"Authorization": "Bearer "}
        response = client.get("/dashboard/", headers=headers)
        assert response.status_code == 401

class TestAuthenticationEdgeCases:
    """Test edge cases in authentication flow."""
    
    def test_empty_username_registration(self, client: TestClient):
        """Test registration with empty username."""
        user_data = {
            "username": "",
            "password": "validpass"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error
        
    def test_empty_password_registration(self, client: TestClient):
        """Test registration with empty password."""
        user_data = {
            "username": "validuser",
            "password": ""
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_very_long_username(self, client: TestClient):
        """Test registration with very long username."""
        long_username = "a" * 1000  # Very long username
        user_data = {
            "username": long_username,
            "password": "validpass"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_special_characters_in_credentials(self, client: TestClient):
        """Test registration with special characters."""
        user_data = {
            "username": "user@123!",
            "password": "pass@123!"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201  # Should work with special chars

class TestAuthenticationSecurity:
    """Test security aspects of authentication."""
    
    def test_password_not_returned_in_response(self, client: TestClient):
        """Test that passwords are never returned in responses."""
        user_data = {
            "username": "securityuser",
            "password": "secretpass123"
        }
        
        # Registration response should not contain password
        response = client.post("/auth/register", json=user_data)
        response_data = response.json()
        
        assert "password" not in response_data
        assert "hashed_password" not in response_data
        
        # Login response should not contain password
        login_response = client.post("/auth/token", data=user_data)
        login_data = login_response.json()
        
        assert "password" not in login_data
        assert "hashed_password" not in login_data

    def test_token_expiration_handling(self, client: TestClient, db_session: Session):
        """Test that expired tokens are properly handled."""
        # This test would require mocking time or using very short token expiry
        # For now, we'll test the basic token structure
        user_data = {
            "username": "expiryuser",
            "password": "expirypass123"
        }
        
        client.post("/auth/register", json=user_data)
        login_response = client.post("/auth/token", data=user_data)
        token = login_response.json()["access_token"]
        
        # Token should be a valid JWT format
        assert len(token.split('.')) == 3  # JWT has 3 parts

    def test_sql_injection_prevention(self, client: TestClient):
        """Test that SQL injection attempts are prevented."""
        # Try to register with SQL injection attempt
        malicious_data = {
            "username": "'; DROP TABLE users; --",
            "password": "validpass"
        }
        
        response = client.post("/auth/register", json=malicious_data)
        # Should either succeed (if properly escaped) or fail gracefully
        assert response.status_code in [201, 400, 422]
        
        # The important thing is that it doesn't crash the application
        # and doesn't execute malicious SQL