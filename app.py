# Core smolagents imports
import os
import uuid
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from smolagents import Tool, OpenAIServerModel, ToolCallingAgent
from langchain_core.vectorstores import VectorStore
from build_index import load_index

# Session storage - in-memory dictionary mapping user_id → {session_id → conversation_history}
user_sessions: Dict[str, Dict[str, List[Dict]]] = {}

# API key to user mapping - maps API keys to user IDs
api_key_to_user: Dict[str, str] = {}

# Load API key to user mappings from environment variable
api_keys_config = os.environ.get("API_KEYS", "")
if api_keys_config:
    # Parse API_KEYS as comma-separated list of key:user pairs
    for pair in api_keys_config.split(","):
        if ":" in pair:
            api_key, user_id = pair.split(":", 1)
            api_key_to_user[api_key.strip()] = user_id.strip()
        else:
            # Backward compatibility: if no user_id specified, use the api_key as both
            api_key = pair.strip()
            if api_key:
                api_key_to_user[api_key] = api_key
else:
    # Default configuration for development
    api_key_to_user["default-api-key"] = "default-user"

class RetrieverTool(Tool):
    name = "retriever"
    description = "Using semantic similarity, retrieves some documents from the knowledge base that have the closest embeddings to the input query."
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be semantically close to your target documents. Use the affirmative form rather than a question.",
        }
    }
    output_type = "string"

    def __init__(self, vectordb: VectorStore, **kwargs):
        super().__init__(**kwargs)
        self.vectordb = vectordb

    def forward(self, query: str) -> str:
        assert isinstance(query, str), "Your search query must be a string"

        docs = self.vectordb.similarity_search(
            query,
            k=7,
        )

        return "\nRetrieved documents:\n" + "".join(
            [
                f"===== Document {str(i)} =====\n" + doc.page_content
                for i, doc in enumerate(docs)
            ]
        )

class SessionCreateResponse(BaseModel):
    session_id: str

class MessageRequest(BaseModel):
    message: str
    session_id: str

class MessageResponse(BaseModel):
    response: str
    session_id: str

class HistoryResponse(BaseModel):
    history: List[Dict]
    session_id: str

class SessionsListResponse(BaseModel):
    session_ids: List[str]

def validate_api_key(api_key: str = Header(None, alias="x-api-key")):
    """Validate API key from request headers and resolve user_id"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is missing")
    if api_key not in api_key_to_user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key_to_user[api_key]

# Initialize the model and tools
model_id = os.environ.get("OPENAI_MODEL", "deepseek-v3")
api_base = os.environ.get("OPENAI_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
api_key = os.environ.get("DASHSCOPE_API_KEY", "")
print(f"Using model: {model_id}, API base: {api_base}, API key length: {len(api_key)}")

model = OpenAIServerModel(
    model_id=model_id,
    api_base=api_base,
    api_key=api_key,
)

vectordb = load_index()
retriever_tool = RetrieverTool(vectordb)

# Initialize FastAPI app
app = FastAPI(title="Multi-Session Agent API")

@app.post("/sessions", response_model=SessionCreateResponse)
async def create_session(api_key: str = Header(None, alias="x-api-key")):
    """Create a new session for a user and return a session ID"""
    # Validate API key and resolve user_id
    user_id = validate_api_key(api_key)
    
    session_id = str(uuid.uuid4())
    
    # Initialize user sessions if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    # Create new session for the user
    user_sessions[user_id][session_id] = []
    
    return SessionCreateResponse(session_id=session_id)

@app.post("/messages", response_model=MessageResponse)
async def send_message(request: MessageRequest, api_key: str = Header(None, alias="x-api-key")):
    """Send a message to the agent within an existing session"""
    # Validate API key and resolve user_id
    user_id = validate_api_key(api_key)
    
    session_id = request.session_id
    message = request.message
    
    # Check if user exists
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if session exists for this user
    if session_id not in user_sessions[user_id]:
        raise HTTPException(status_code=404, detail="Session not found for this user")
    
    # Get conversation history for this session
    conversation_history = user_sessions[user_id][session_id]
    
    # Create agent
    agent = ToolCallingAgent(
        tools=[retriever_tool], 
        model=model
    )
    
    # Manually populate the agent's memory with conversation history
    for entry in conversation_history:
        if entry["role"] == "user":
            # Add user message as a TaskStep
            from smolagents.memory import TaskStep
            agent.memory.steps.append(TaskStep(task=entry["content"]))
        # Note: Assistant responses are not directly added to memory as they're 
        # generated by the agent. The agent will use the user messages to 
        # generate appropriate responses.
    
    # Get response from agent
    response = agent.run(message, reset=False)
    
    # Update session history
    user_sessions[user_id][session_id].append({"role": "user", "content": message})
    user_sessions[user_id][session_id].append({"role": "assistant", "content": response})
    
    return MessageResponse(response=response, session_id=session_id)

@app.get("/sessions/{session_id}/history", response_model=HistoryResponse)
async def get_history(session_id: str, api_key: str = Header(None, alias="x-api-key")):
    """Retrieve the conversation history for a session"""
    # Validate API key and resolve user_id
    user_id = validate_api_key(api_key)
    
    # Check if user exists
    if user_id not in user_sessions:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if session exists for this user
    if session_id not in user_sessions[user_id]:
        raise HTTPException(status_code=404, detail="Session not found for this user")
    
    return HistoryResponse(history=user_sessions[user_id][session_id], session_id=session_id)

@app.get("/sessions", response_model=SessionsListResponse)
async def list_sessions(api_key: str = Header(None, alias="x-api-key")):
    """List all active session IDs for the authenticated user"""
    # Validate API key and resolve user_id
    user_id = validate_api_key(api_key)
    
    # Check if user exists
    if user_id not in user_sessions:
        return SessionsListResponse(session_ids=[])
    
    # Return list of session IDs for this user
    session_ids = list(user_sessions[user_id].keys())
    return SessionsListResponse(session_ids=session_ids)

@app.get("/health")
async def health_check(api_key: str = Header(None, alias="x-api-key")):
    """Health check endpoint"""
    # Validate API key and resolve user_id
    user_id = validate_api_key(api_key)
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)