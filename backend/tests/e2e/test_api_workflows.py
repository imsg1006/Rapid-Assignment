import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User, SearchHistory, ImageHistory
from app.security import verify_password

class TestCompleteUserWorkflow:
    """End-to-end tests for complete user workflows."""
    
    def test_complete_user_lifecycle(self, client: TestClient, db_session: Session):
        """Test complete user lifecycle: register, login, use services, logout."""
        # 1. User Registration
        user_data = {
            "username": "lifecycleuser",
            "password": "lifecyclepass123"
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # 2. User Login
        login_response = client.post("/auth/token", data=user_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Access Dashboard (should be empty initially)
        dashboard_response = client.get("/dashboard/", headers=headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert "searches" in dashboard_data
        assert "images" in dashboard_data
        assert len(dashboard_data["searches"]) == 0
        assert len(dashboard_data["images"]) == 0
        
        # 4. Perform Web Search
        search_query = "test search query"
        search_response = client.get(f"/search/?query={search_query}", headers=headers)
        assert search_response.status_code == 200
        
        search_data = search_response.json()
        assert search_data["query"] == search_query
        assert "results" in search_data
        assert "history_id" in search_data
        
        # 5. Verify Search History in Dashboard
        dashboard_response = client.get("/dashboard/", headers=headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert len(dashboard_data["searches"]) == 1
        assert dashboard_data["searches"][0]["query"] == search_query
        
        # 6. Generate Image (with mocked MCP)
        from unittest.mock import AsyncMock, patch
        with patch('app.routes.image.streamablehttp_client'), \
             patch('app.routes.image.mcp.ClientSession'):
            
            # Mock successful image generation
            mock_session_instance = AsyncMock()
            mock_session_instance.initialize = AsyncMock()
            mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
            mock_response = AsyncMock(
                isError=False,
                content=[AsyncMock(text='{"imageUrl": "https://example.com/test-image.jpg"}')]
            )
            mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
            
            # Mock the session context manager
            import app.routes.image as image_module
            image_module.mcp.ClientSession.return_value.__aenter__.return_value = mock_session_instance
            
            image_data = {"prompt": "A test image"}
            image_response = client.post("/images/generate", json=image_data, headers=headers)
            assert image_response.status_code == 201
            
            image_response_data = image_response.json()
            assert "image_url" in image_response_data
            assert "history_id" in image_response_data
        
        # 7. Verify Image History in Dashboard
        dashboard_response = client.get("/dashboard/", headers=headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert len(dashboard_data["images"]) == 1
        assert dashboard_data["images"][0]["prompt"] == "A test image"
        
        # 8. Update Search Entry
        search_id = dashboard_data["searches"][0]["id"]
        update_data = {"query": "updated search query"}
        update_response = client.patch(f"/dashboard/search/{search_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        # 9. Update Image Entry
        image_id = dashboard_data["images"][0]["id"]
        image_update_data = {"prompt": "updated image prompt"}
        image_update_response = client.patch(f"/dashboard/image/{image_id}", json=image_update_data, headers=headers)
        assert image_update_response.status_code == 200
        
        # 10. Verify Updates in Dashboard
        dashboard_response = client.get("/dashboard/", headers=headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert dashboard_data["searches"][0]["query"] == "updated search query"
        assert dashboard_data["images"][0]["prompt"] == "updated image prompt"
        
        # 11. Delete Search Entry
        delete_search_response = client.delete(f"/dashboard/search/{search_id}", headers=headers)
        assert delete_search_response.status_code == 200
        
        # 12. Delete Image Entry
        delete_image_response = client.delete(f"/dashboard/image/{image_id}", headers=headers)
        assert delete_image_response.status_code == 200
        
        # 13. Verify Deletions in Dashboard
        dashboard_response = client.get("/dashboard/", headers=headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert len(dashboard_data["searches"]) == 0
        assert len(dashboard_data["images"]) == 0

class TestSearchWorkflow:
    """End-to-end tests for search functionality."""
    
    def test_complete_search_workflow(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test complete search workflow with history management."""
        # 1. Perform multiple searches
        search_queries = [
            "python programming",
            "machine learning",
            "web development",
            "data science",
            "artificial intelligence"
        ]
        
        search_results = []
        for query in search_queries:
            response = client.get(f"/search/?query={query}", headers=auth_headers)
            assert response.status_code == 200
            
            search_data = response.json()
            assert search_data["query"] == query
            search_results.append(search_data)
        
        # 2. Verify all searches are in dashboard
        dashboard_response = client.get("/dashboard/", headers=auth_headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert len(dashboard_data["searches"]) == len(search_queries)
        
        # 3. Verify search order (should be newest first)
        dashboard_searches = dashboard_data["searches"]
        for i in range(len(dashboard_searches) - 1):
            current_time = dashboard_searches[i]["timestamp"]
            next_time = dashboard_searches[i + 1]["timestamp"]
            assert current_time >= next_time  # Newest first
        
        # 4. Test search result parsing
        for search in dashboard_data["searches"]:
            assert "query" in search
            assert "results" in search
            assert "timestamp" in search
            assert "user_id" in search
            
            # Results should be valid JSON string
            try:
                parsed_results = json.loads(search["results"])
                assert isinstance(parsed_results, list)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON in search results: {search['results']}")

class TestImageGenerationWorkflow:
    """End-to-end tests for image generation functionality."""
    
    def test_complete_image_generation_workflow(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test complete image generation workflow with history management."""
        from unittest.mock import AsyncMock, patch
        
        # 1. Generate multiple images
        image_prompts = [
            "A beautiful sunset over mountains",
            "A futuristic cityscape with flying cars",
            "A serene forest with morning mist",
            "An underwater palace with coral reefs",
            "A steampunk airship in Victorian London"
        ]
        
        generated_images = []
        for prompt in image_prompts:
            with patch('app.routes.image.streamablehttp_client'), \
                 patch('app.routes.image.mcp.ClientSession'):
                
                # Mock successful image generation
                mock_session_instance = AsyncMock()
                mock_session_instance.initialize = AsyncMock()
                mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
                mock_response = AsyncMock(
                    isError=False,
                    content=[AsyncMock(text=f'{{"imageUrl": "https://example.com/{prompt.replace(" ", "-")}.jpg"}}')]
                )
                mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
                
                # Mock the session context manager
                import app.routes.image as image_module
                image_module.mcp.ClientSession.return_value.__aenter__.return_value = mock_session_instance
                
                image_data = {"prompt": prompt}
                response = client.post("/images/generate", json=image_data, headers=auth_headers)
                assert response.status_code == 201
                
                image_response_data = response.json()
                assert "image_url" in image_response_data
                assert "history_id" in image_response_data
                generated_images.append(image_response_data)
        
        # 2. Verify all images are in dashboard
        dashboard_response = client.get("/dashboard/", headers=auth_headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        assert len(dashboard_data["images"]) == len(image_prompts)
        
        # 3. Verify image order (should be newest first)
        dashboard_images = dashboard_data["images"]
        for i in range(len(dashboard_images) - 1):
            current_time = dashboard_images[i]["timestamp"]
            next_time = dashboard_images[i + 1]["timestamp"]
            assert current_time >= next_time  # Newest first
        
        # 4. Test image data integrity
        for image in dashboard_data["images"]:
            assert "prompt" in image
            assert "image_url" in image
            assert "timestamp" in image
            assert "user_id" in image
            
            # Image URL should be valid
            assert image["image_url"].startswith("https://")
            assert ".jpg" in image["image_url"]

class TestDashboardWorkflow:
    """End-to-end tests for dashboard functionality."""
    
    def test_dashboard_data_integrity(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test dashboard data integrity and relationships."""
        # 1. Create some test data
        from unittest.mock import AsyncMock, patch
        
        # Add search history
        search_query = "dashboard test query"
        search_response = client.get(f"/search/?query={search_query}", headers=auth_headers)
        assert search_response.status_code == 200
        
        # Add image history
        with patch('app.routes.image.streamablehttp_client'), \
             patch('app.routes.image.mcp.ClientSession'):
            
            mock_session_instance = AsyncMock()
            mock_session_instance.initialize = AsyncMock()
            mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
            mock_response = AsyncMock(
                isError=False,
                content=[AsyncMock(text='{"imageUrl": "https://example.com/dashboard-test.jpg"}')]
            )
            mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
            
            import app.routes.image as image_module
            image_module.mcp.ClientSession.return_value.__aenter__.return_value = mock_session_instance
            
            image_data = {"prompt": "Dashboard test image"}
            image_response = client.post("/images/generate", json=image_data, headers=auth_headers)
            assert image_response.status_code == 201
        
        # 2. Verify dashboard data structure
        dashboard_response = client.get("/dashboard/", headers=auth_headers)
        assert dashboard_response.status_code == 200
        
        dashboard_data = dashboard_response.json()
        
        # Check required fields
        assert "searches" in dashboard_data
        assert "images" in dashboard_data
        assert isinstance(dashboard_data["searches"], list)
        assert isinstance(dashboard_data["images"], list)
        
        # 3. Verify data relationships
        if dashboard_data["searches"]:
            search = dashboard_data["searches"][0]
            assert "id" in search
            assert "query" in search
            assert "results" in search
            assert "timestamp" in search
            assert "user_id" in search
        
        if dashboard_data["images"]:
            image = dashboard_data["images"][0]
            assert "id" in image
            assert "prompt" in image
            assert "image_url" in image
            assert "timestamp" in image
            assert "user_id" in image
        
        # 4. Verify user isolation
        # Create another user and verify data isolation
        other_user_data = {
            "username": "otheruser",
            "password": "otherpass123"
        }
        
        client.post("/auth/register", json=other_user_data)
        other_user_login = client.post("/auth/token", data=other_user_data)
        other_user_token = other_user_login.json()["access_token"]
        other_user_headers = {"Authorization": f"Bearer {other_user_token}"}
        
        # Other user's dashboard should be empty
        other_dashboard = client.get("/dashboard/", headers=other_user_headers)
        assert other_dashboard.status_code == 200
        
        other_dashboard_data = other_dashboard.json()
        assert len(other_dashboard_data["searches"]) == 0
        assert len(other_dashboard_data["images"]) == 0

class TestErrorHandlingWorkflow:
    """End-to-end tests for error handling scenarios."""
    
    def test_authentication_error_handling(self, client: TestClient):
        """Test error handling for authentication failures."""
        # 1. Try to access protected endpoint without token
        response = client.get("/dashboard/")
        assert response.status_code == 401
        
        # 2. Try to access with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/dashboard/", headers=headers)
        assert response.status_code == 401
        
        # 3. Try to access with malformed token
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/dashboard/", headers=headers)
        assert response.status_code == 401
    
    def test_validation_error_handling(self, client: TestClient):
        """Test error handling for validation failures."""
        # 1. Try to register with invalid data
        invalid_user_data = {
            "username": "",  # Empty username
            "password": "validpass"
        }
        response = client.post("/auth/register", json=invalid_user_data)
        assert response.status_code == 422
        
        # 2. Try to register with missing fields
        incomplete_user_data = {"username": "testuser"}  # Missing password
        response = client.post("/auth/register", json=incomplete_user_data)
        assert response.status_code == 422
    
    def test_database_error_handling(self, client: TestClient, auth_headers: dict):
        """Test error handling for database operation failures."""
        # This would require more complex mocking of database failures
        # For now, we'll test basic error responses
        
        # Try to access non-existent resource
        response = client.get("/dashboard/search/99999", headers=auth_headers)
        assert response.status_code == 404
        
        response = client.get("/dashboard/image/99999", headers=auth_headers)
        assert response.status_code == 404

class TestPerformanceWorkflow:
    """End-to-end tests for performance and scalability."""
    
    def test_multiple_concurrent_requests(self, client: TestClient, auth_headers: dict):
        """Test handling of multiple concurrent requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(request_id):
            try:
                response = client.get(f"/dashboard/", headers=auth_headers)
                results.append((request_id, response.status_code))
            except Exception as e:
                errors.append((request_id, str(e)))
        
        # Start multiple concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests completed successfully
        assert len(results) == 10
        assert len(errors) == 0
        
        for request_id, status_code in results:
            assert status_code == 200, f"Request {request_id} failed with status {status_code}"
    
    def test_large_data_handling(self, client: TestClient, auth_headers: dict):
        """Test handling of large data sets."""
        # This test would create many search and image records
        # and verify the dashboard can handle them efficiently
        
        # For now, we'll test basic functionality with existing data
        response = client.get("/dashboard/", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify response time is reasonable
        start_time = time.time()
        response = client.get("/dashboard/", headers=auth_headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 5.0  # Should respond within 5 seconds