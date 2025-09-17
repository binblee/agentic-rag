"""
Agentic RAG SDK
~~~~~~~~~~~~~~~

A Python SDK for interacting with the Agentic RAG API.

Basic usage:
    >>> from agentic_rag_sdk import AgenticRAGClient
    >>> client = AgenticRAGClient(api_key="your-api-key")
    >>> session = client.create_session()
"""

from .client import AgenticRAGClient
from .exceptions import AgenticRAGError, AgenticRAGAPIError
from .models import Message, SessionHistory, SessionList

__all__ = [
    "AgenticRAGClient",
    "AgenticRAGError",
    "AgenticRAGAPIError",
    "Message",
    "SessionHistory",
    "SessionList"
]
__version__ = "0.1.0"