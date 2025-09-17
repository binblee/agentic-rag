"""
Tests for the Agentic RAG data models.
"""

from agentic_rag_sdk.models import (
    Message,
    SessionResponse,
    MessageResponse,
    SessionHistory,
    SessionList,
    HealthResponse
)


def test_message_model():
    """Test Message model creation."""
    message = Message(content="Test message", role="user")

    assert message.content == "Test message"
    assert message.role == "user"


def test_session_response_model():
    """Test SessionResponse model creation."""
    response = SessionResponse(session_id="test-session-id")

    assert response.session_id == "test-session-id"


def test_message_response_model():
    """Test MessageResponse model creation."""
    response = MessageResponse(response="Test response", session_id="test-session-id")

    assert response.response == "Test response"
    assert response.session_id == "test-session-id"


def test_session_history_model():
    """Test SessionHistory model creation."""
    messages = [
        Message(content="Test message 1", role="user"),
        Message(content="Test response 1", role="assistant")
    ]
    history = SessionHistory(history=messages, session_id="test-session-id")

    assert len(history.history) == 2
    assert history.session_id == "test-session-id"
    assert isinstance(history.history[0], Message)
    assert history.history[0].content == "Test message 1"


def test_session_list_model():
    """Test SessionList model creation."""
    session_ids = ["session-1", "session-2"]
    session_list = SessionList(session_ids=session_ids)

    assert len(session_list.session_ids) == 2
    assert "session-1" in session_list.session_ids
    assert "session-2" in session_list.session_ids


def test_health_response_model():
    """Test HealthResponse model creation."""
    response = HealthResponse(status="healthy")

    assert response.status == "healthy"