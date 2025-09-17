# Agentic RAG SDK

Python SDK for interacting with the Agentic RAG API.

## Installation

```bash
uv sync
```

## Usage

Sample code in [sample.py](sample.py)
### Basic Usage

```python
from agentic_rag_sdk import AgenticRAGClient

# Initialize the client
client = AgenticRAGClient(api_key="your-api-key")

# Create a new session
session = client.create_session()
print(f"Session ID: {session.session_id}")

# Send a message
response = client.send_message("What is the博士生活补贴?", session.session_id)
print(f"Response: {response.response}")

# Get session history
history = client.get_session_history(session.session_id)
for message in history.history:
    print(f"{message.role}: {message.content}")

# List all sessions
sessions = client.list_sessions()
print(f"Active sessions: {sessions.session_ids}")

# Health check
health = client.health_check()
print(f"Server status: {health.status}")
```

### Using Context Manager

```python
from agentic_rag_sdk import AgenticRAGClient

# Using context manager for automatic cleanup
with AgenticRAGClient(api_key="your-api-key") as client:
    session = client.create_session()
    response = client.send_message("Hello, world!", session.session_id)
    print(response.response)
```

## API Reference

### AgenticRAGClient

#### `__init__(api_key, base_url)`
Initialize the client with your API key and base URL.

#### `create_session()`
Create a new session for the authenticated user.

Returns: `SessionResponse`

#### `send_message(message, session_id)`
Send a message to the agent within an existing session.

Returns: `MessageResponse`

#### `get_session_history(session_id)`
Retrieve the conversation history for a session.

Returns: `SessionHistory`

#### `list_sessions()`
List all active session IDs for the authenticated user.

Returns: `SessionList`

#### `health_check()`
Check if the API server is running.

Returns: `HealthResponse`

## Error Handling

The SDK raises `AgenticRAGAPIError` for API-related errors:

```python
from agentic_rag_sdk import AgenticRAGClient, AgenticRAGAPIError

try:
    client = AgenticRAGClient(api_key="your-api-key")
    session = client.create_session()
except AgenticRAGAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
```

## Running Tests

```bash
uv run pytest
```