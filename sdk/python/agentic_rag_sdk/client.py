"""
Main client for interacting with the Agentic RAG API.
"""

import httpx
from typing import Optional, List
from .models import (
    Message,
    SessionResponse,
    MessageResponse,
    SessionHistory,
    SessionList,
    HealthResponse
)
from .exceptions import AgenticRAGAPIError


class AgenticRAGClient:
    """
    Client for interacting with the Agentic RAG API.

    Provides methods for creating sessions, sending messages,
    retrieving session history, listing sessions, and health checks.
    """

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        """
        Initialize the Agentic RAG client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API (defaults to http://localhost:8000)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def create_session(self) -> SessionResponse:
        """
        Create a new session for the authenticated user.

        Returns:
            SessionResponse: Contains the unique session ID

        Raises:
            AgenticRAGAPIError: If the API returns an error
        """
        response = self.client.post("/sessions")

        if response.status_code != 200:
            raise AgenticRAGAPIError(
                response.status_code,
                f"Failed to create session: {response.text}"
            )

        data = response.json()
        return SessionResponse(session_id=data["session_id"])

    def send_message(self, message: str, session_id: str) -> MessageResponse:
        """
        Send a message to the agent within an existing session.

        Args:
            message: The message to send to the agent
            session_id: The ID of the session to send the message to

        Returns:
            MessageResponse: Contains the agent's response and session ID

        Raises:
            AgenticRAGAPIError: If the API returns an error
        """
        payload = {
            "message": message,
            "session_id": session_id
        }

        response = self.client.post("/messages", json=payload)

        if response.status_code != 200:
            raise AgenticRAGAPIError(
                response.status_code,
                f"Failed to send message: {response.text}"
            )

        data = response.json()
        return MessageResponse(
            response=data["response"],
            session_id=data["session_id"]
        )

    def get_session_history(self, session_id: str) -> SessionHistory:
        """
        Retrieve the conversation history for a session.

        Args:
            session_id: The ID of the session to retrieve history for

        Returns:
            SessionHistory: Contains the conversation history and session ID

        Raises:
            AgenticRAGAPIError: If the API returns an error
        """
        response = self.client.get(f"/sessions/{session_id}/history")

        if response.status_code != 200:
            raise AgenticRAGAPIError(
                response.status_code,
                f"Failed to get session history: {response.text}"
            )

        data = response.json()

        # Convert history items to Message objects
        history = [
            Message(content=item["content"], role=item["role"])
            for item in data["history"]
        ]

        return SessionHistory(
            history=history,
            session_id=data["session_id"]
        )

    def list_sessions(self) -> SessionList:
        """
        List all active session IDs for the authenticated user.

        Returns:
            SessionList: Contains a list of active session IDs

        Raises:
            AgenticRAGAPIError: If the API returns an error
        """
        response = self.client.get("/sessions")

        if response.status_code != 200:
            raise AgenticRAGAPIError(
                response.status_code,
                f"Failed to list sessions: {response.text}"
            )

        data = response.json()
        return SessionList(session_ids=data["session_ids"])

    def health_check(self) -> HealthResponse:
        """
        Check if the API server is running.

        Returns:
            HealthResponse: Contains the server status

        Raises:
            AgenticRAGAPIError: If the API returns an error
        """
        response = self.client.get("/health")

        if response.status_code != 200:
            raise AgenticRAGAPIError(
                response.status_code,
                f"Health check failed: {response.text}"
            )

        data = response.json()
        return HealthResponse(status=data["status"])

    def close(self) -> None:
        """Close the HTTP client connection."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()