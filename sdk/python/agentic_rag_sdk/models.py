"""
Data models for the Agentic RAG API.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a message sent to or received from the agent."""
    content: str
    role: str = "user"  # "user" or "assistant"


@dataclass
class SessionResponse:
    """Response from session creation."""
    session_id: str


@dataclass
class MessageResponse:
    """Response from sending a message."""
    response: str
    session_id: str


@dataclass
class SessionHistory:
    """Session history containing conversation messages."""
    history: List[Message]
    session_id: str


@dataclass
class SessionList:
    """List of active session IDs."""
    session_ids: List[str]


@dataclass
class HealthResponse:
    """Response from health check."""
    status: str