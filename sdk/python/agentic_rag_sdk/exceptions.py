"""
Custom exceptions for the Agentic RAG SDK.
"""

class AgenticRAGError(Exception):
    """Base exception for Agentic RAG SDK errors."""
    pass


class AgenticRAGAPIError(AgenticRAGError):
    """Exception raised for API-related errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")