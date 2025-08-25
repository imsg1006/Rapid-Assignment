import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User, ImageHistory
import json

class TestMCPIntegration:
    """Integration tests for MCP (Model Context Protocol) interactions."""
    
    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_successful_image_generation_flow(self, mock_session, mock_client, client: TestClient, auth_headers: dict, db_session: Session):
        """Test complete successful image generation flow through MCP."""
        # Mock MCP client session
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock successful image generation response
        mock_response = AsyncMock(
            isError=False,
            content=[AsyncMock(text='{"imageUrl": "https://example.com/generated-image.jpg"}')]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Test image generation endpoint
        image_data = {"prompt": "A beautiful sunset over mountains"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 201
        response_data = response.json()
        
        assert "message" in response_data
        assert "image_url" in response_data
        assert "history_id" in response_data
        assert response_data["image_url"] == "https://example.com/generated-image.jpg"
        
        # Verify MCP interactions were called correctly
        mock_session_instance.initialize.assert_called_once()
        mock_session_instance.list_tools.assert_called_once()
        mock_session_instance.call_tool.assert_called_once_with(
            name="generateImageUrl",
            arguments={"prompt": "A beautiful sunset over mountains"}
        )
        
        # Verify image history was saved to database
        image_history = db_session.query(ImageHistory).filter_by(
            prompt="A beautiful sunset over mountains"
        ).first()
        assert image_history is not None
        assert image_history.image_url == "https://example.com/generated-image.jpg"

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_connection_failure(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of MCP connection failures."""
        # Mock connection failure
        mock_client.side_effect = Exception("Connection failed to MCP server")
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "Image generation failed" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_no_tools_available(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling when MCP server has no tools available."""
        # Mock MCP session with no tools
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[]))
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "No tools available from Flux MCP" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_tool_execution_error(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of MCP tool execution errors."""
        # Mock MCP session with tool execution error
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock tool execution error
        mock_response = AsyncMock(
            isError=True,
            content=[]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "No valid response from generateImageUrl" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_invalid_response_format(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of invalid response format from MCP."""
        # Mock MCP session with invalid response format
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock invalid response format
        mock_response = AsyncMock(
            isError=False,
            content=[AsyncMock(text='invalid json response')]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "Image generation failed" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_missing_image_url(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling when MCP response is missing imageUrl."""
        # Mock MCP session with response missing imageUrl
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock response without imageUrl
        mock_response = AsyncMock(
            isError=False,
            content=[AsyncMock(text='{"otherField": "value"}')]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "No imageUrl in response" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_session_initialization_failure(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of MCP session initialization failures."""
        # Mock MCP session initialization failure
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock(side_effect=Exception("Initialization failed"))
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "Image generation failed" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_empty_content_response(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of MCP response with empty content."""
        # Mock MCP session with empty content
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock response with empty content
        mock_response = AsyncMock(
            isError=False,
            content=[]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "No valid content from generateImageUrl" in response_data["detail"]

class TestMCPErrorHandling:
    """Test error handling in MCP integration."""
    
    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_network_timeout(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of network timeouts."""
        # Mock network timeout
        mock_client.side_effect = asyncio.TimeoutError("Connection timeout")
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "Image generation failed" in response_data["detail"]

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_mcp_authentication_failure(self, mock_session, mock_client, client: TestClient, auth_headers: dict):
        """Test handling of MCP authentication failures."""
        # Mock authentication failure
        mock_client.side_effect = Exception("Authentication failed: Invalid API key")
        
        image_data = {"prompt": "Test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        response_data = response.json()
        assert "detail" in response_data
        assert "Image generation failed" in response_data["detail"]

class TestMCPDataPersistence:
    """Test data persistence during MCP interactions."""
    
    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_image_history_persistence_on_success(self, mock_session, mock_client, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that image history is properly persisted on successful generation."""
        # Mock successful MCP response
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        mock_response = AsyncMock(
            isError=False,
            content=[AsyncMock(text='{"imageUrl": "https://example.com/persisted-image.jpg"}')]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Generate image
        image_data = {"prompt": "Persistent test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 201
        
        # Verify persistence in database
        image_history = db_session.query(ImageHistory).filter_by(
            prompt="Persistent test prompt"
        ).first()
        
        assert image_history is not None
        assert image_history.image_url == "https://example.com/persisted-image.jpg"
        assert image_history.user_id is not None

    @pytest.mark.asyncio
    @patch('app.routes.image.streamablehttp_client')
    @patch('app.routes.image.mcp.ClientSession')
    async def test_database_rollback_on_mcp_failure(self, mock_session, mock_client, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that database changes are rolled back on MCP failures."""
        # Mock MCP failure after successful database operations
        mock_session_instance = AsyncMock()
        mock_session_instance.initialize = AsyncMock()
        mock_session_instance.list_tools = AsyncMock(return_value=AsyncMock(tools=[AsyncMock()]))
        
        # Mock tool execution failure
        mock_response = AsyncMock(
            isError=True,
            content=[]
        )
        mock_session_instance.call_tool = AsyncMock(return_value=mock_response)
        
        mock_session.return_value.__aenter__.return_value = mock_session_instance
        
        # Count initial records
        initial_count = db_session.query(ImageHistory).count()
        
        # Attempt image generation (should fail)
        image_data = {"prompt": "Rollback test prompt"}
        response = client.post("/images/generate", json=image_data, headers=auth_headers)
        
        assert response.status_code == 500
        
        # Verify no new records were added
        final_count = db_session.query(ImageHistory).count()
        assert final_count == initial_count
        
        # Verify no partial data exists
        partial_record = db_session.query(ImageHistory).filter_by(
            prompt="Rollback test prompt"
        ).first()
        assert partial_record is None