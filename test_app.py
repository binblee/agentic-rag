import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
import sys
import os

# Add the project directory to the path so we can import app
sys.path.insert(0, os.path.dirname(__file__))

# Import the app
from app import app, user_sessions, api_key_to_user

# Clear any existing sessions and API key mappings
user_sessions.clear()
api_key_to_user.clear()

# Set up test API key mappings
api_key_to_user.update({
    "test-key-1": "test-user-1",
    "test-key-2": "test-user-1",  # Same user, different key
    "test-key-3": "test-user-2",  # Different user
})

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_sessions():
    """Reset sessions before each test"""
    user_sessions.clear()
    yield
    user_sessions.clear()

class MockAgent:
    """Mock agent that returns predefined responses"""
    def __init__(self, *args, **kwargs):
        self.memory = MagicMock()
        self.memory.steps = []
        
    def run(self, message, reset=False):
        return f"Mock response to: {message}"

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_create_session_success(mock_load_index):
    """Test creating a new session with valid API key"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)
    assert len(data["session_id"]) > 0
    
    # Verify session was created
    assert "test-user-1" in user_sessions
    assert data["session_id"] in user_sessions["test-user-1"]

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_list_sessions_empty(mock_load_index):
    """Test listing sessions when empty"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    response = client.get("/sessions", headers={"x-api-key": "test-key-1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "session_ids" in data
    assert data["session_ids"] == []

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_list_sessions_with_data(mock_load_index):
    """Test listing sessions with active sessions"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create a session first
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # List sessions
    response = client.get("/sessions", headers={"x-api-key": "test-key-1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "session_ids" in data
    assert len(data["session_ids"]) == 1
    assert data["session_ids"][0] == session_id

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_send_message_success(mock_load_index):
    """Test sending message to valid session"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create a session first
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Send a message
    message_data = {
        "message": "Hello, world!",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "session_id" in data
    assert data["session_id"] == session_id
    assert "Mock response to: Hello, world!" in data["response"]
    
    # Verify message was stored in session history
    assert len(user_sessions["test-user-1"][session_id]) == 2
    assert user_sessions["test-user-1"][session_id][0]["role"] == "user"
    assert user_sessions["test-user-1"][session_id][0]["content"] == "Hello, world!"
    assert user_sessions["test-user-1"][session_id][1]["role"] == "assistant"
    assert "Mock response to: Hello, world!" in user_sessions["test-user-1"][session_id][1]["content"]

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_get_history_success(mock_load_index):
    """Test getting history for valid session"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create a session and send a message
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    message_data = {
        "message": "Hello, world!",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    
    # Get history
    response = client.get(f"/sessions/{session_id}/history", headers={"x-api-key": "test-key-1"})
    
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "session_id" in data
    assert data["session_id"] == session_id
    assert len(data["history"]) == 2
    assert data["history"][0]["role"] == "user"
    assert data["history"][0]["content"] == "Hello, world!"
    assert data["history"][1]["role"] == "assistant"

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_complete_session_flow(mock_load_index):
    """Test complete session flow"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # 1. Create session
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # 2. Send first message
    message_data = {
        "message": "First message",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    
    # 3. Send second message
    message_data = {
        "message": "Second message",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    
    # 4. Get history
    response = client.get(f"/sessions/{session_id}/history", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["history"]) == 4  # 2 user messages + 2 assistant responses
    
    # 5. List sessions
    response = client.get("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["session_ids"]) == 1
    assert data["session_ids"][0] == session_id

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_invalid_api_key(mock_load_index):
    """Test that invalid API key returns 401"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Test missing API key
    response = client.post("/sessions")
    assert response.status_code == 401
    
    # Test invalid API key
    response = client.post("/sessions", headers={"x-api-key": "invalid-key"})
    assert response.status_code == 401

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_access_nonexistent_session(mock_load_index):
    """Test accessing non-existent session returns 404"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    fake_session_id = str(uuid.uuid4())
    
    # Try to send message to non-existent session
    message_data = {
        "message": "Hello",
        "session_id": fake_session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-1"})
    assert response.status_code == 404
    
    # Try to get history for non-existent session
    response = client.get(f"/sessions/{fake_session_id}/history", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 404

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_access_session_with_wrong_user(mock_load_index):
    """Test accessing session with wrong user returns 404"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create session with test-user-1
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Try to access with test-user-2
    message_data = {
        "message": "Hello",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-3"})
    assert response.status_code == 404

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_multiple_keys_same_user(mock_load_index):
    """Test sessions created with one key accessible by another key from same user"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create session with first key
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Access session with second key (same user)
    message_data = {
        "message": "Hello from second key",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-2"})
    assert response.status_code == 200
    
    # Verify response
    data = response.json()
    assert "Mock response to: Hello from second key" in data["response"]

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_sessions_not_accessible_by_different_users(mock_load_index):
    """Test sessions not accessible by keys from different users"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    # Create session with test-user-1
    response = client.post("/sessions", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Try to access with test-user-2's key
    message_data = {
        "message": "Hello",
        "session_id": session_id
    }
    response = client.post("/messages", json=message_data, headers={"x-api-key": "test-key-3"})
    assert response.status_code == 404

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_health_check(mock_load_index):
    """Test health check endpoint"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    response = client.get("/health", headers={"x-api-key": "test-key-1"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@patch('app.ToolCallingAgent', MockAgent)
@patch('app.load_index')
def test_health_check_invalid_api_key(mock_load_index):
    """Test health check with invalid API key"""
    # Mock the vector database
    mock_load_index.return_value = MagicMock()
    
    response = client.get("/health", headers={"x-api-key": "invalid-key"})
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__])