from agentic_rag_sdk import AgenticRAGClient

client = AgenticRAGClient(api_key="user1-apikey1")

# Create a new session
session = client.create_session()
print(f"Session ID: {session.session_id}")

# Send a message
response = client.send_message("本科生生活补贴是多少?", session.session_id)
print(f"Response: {response.response}")

# Get session history
history = client.get_session_history(session.session_id)
for message in history.history:
    print(f"{message.role}: {message.content}")

# List all sessions
sessions = client.list_sessions()
print(f"Active sessions: {sessions.session_ids}")
