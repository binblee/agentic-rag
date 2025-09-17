"""
Tests for the Agentic RAG client.
"""

import pytest
import respx
from httpx import Response
from agentic_rag_sdk import AgenticRAGClient
from agentic_rag_sdk.models import (
    SessionResponse,
    MessageResponse,
    SessionHistory,
    SessionList,
    HealthResponse,
    Message
)
from agentic_rag_sdk.exceptions import AgenticRAGAPIError


@pytest.fixture
def client():
    """Create a test client."""
    return AgenticRAGClient(api_key="test-key", base_url="http://test-server")


@respx.mock
def test_create_session(client):
    """Test creating a new session."""
    # Mock the API response
    mock_response = {"session_id": "test-session-id"}
    respx.post("http://test-server/sessions").mock(
        return_value=Response(200, json=mock_response)
    )

    # Test the method
    response = client.create_session()

    # Verify the response
    assert isinstance(response, SessionResponse)
    assert response.session_id == "test-session-id"


@respx.mock
def test_send_message(client):
    """Test sending a message."""
    # Mock the API response
    mock_response = {
        "response": "Test response",
        "session_id": "test-session-id"
    }
    respx.post("http://test-server/messages").mock(
        return_value=Response(200, json=mock_response)
    )

    # Test the method
    response = client.send_message("Test message", "test-session-id")

    # Verify the response
    assert isinstance(response, MessageResponse)
    assert response.response == "Test response"
    assert response.session_id == "test-session-id"


@respx.mock
def test_get_session_history(client):
    """Test retrieving session history."""
    # Mock the API response
    mock_response = {
        "history": [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"}
        ],
        "session_id": "test-session-id"
    }
    respx.get("http://test-server/sessions/test-session-id/history").mock(
        return_value=Response(200, json=mock_response)
    )

    # Test the method
    response = client.get_session_history("test-session-id")

    # Verify the response
    assert isinstance(response, SessionHistory)
    assert response.session_id == "test-session-id"
    assert len(response.history) == 2
    assert isinstance(response.history[0], Message)
    assert response.history[0].role == "user"
    assert response.history[0].content == "Test message"


@respx.mock
def test_list_sessions(client):
    """Test listing sessions."""
    # Mock the API response
    mock_response = {
        "session_ids": ["session-1", "session-2"]
    }
    respx.get("http://test-server/sessions").mock(
        return_value=Response(200, json=mock_response)
    )

    # Test the method
    response = client.list_sessions()

    # Verify the response
    assert isinstance(response, SessionList)
    assert len(response.session_ids) == 2
    assert "session-1" in response.session_ids
    assert "session-2" in response.session_ids


@respx.mock
def test_health_check(client):
    """Test health check."""
    # Mock the API response
    mock_response = {"status": "healthy"}
    respx.get("http://test-server/health").mock(
        return_value=Response(200, json=mock_response)
    )

    # Test the method
    response = client.health_check()

    # Verify the response
    assert isinstance(response, HealthResponse)
    assert response.status == "healthy"


@respx.mock
def test_api_error(client):
    """Test API error handling."""
    # Mock an error response
    respx.post("http://test-server/sessions").mock(
        return_value=Response(500, text="Internal server error")
    )

    # Test that the error is raised
    with pytest.raises(AgenticRAGAPIError) as exc_info:
        client.create_session()

    assert exc_info.value.status_code == 500
    assert "Failed to create session" in str(exc_info.value)


def test_client_initialization():
    """Test client initialization."""
    client = AgenticRAGClient(api_key="test-key", base_url="http://localhost:8000")

    assert client.api_key == "test-key"
    assert client.base_url == "http://localhost:8000"
    assert client.headers["x-api-key"] == "test-key"
    assert client.headers["Content-Type"] == "application/json"