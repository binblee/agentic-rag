# Agentic RAG Demo

## Quick Start

### Prerequisites

- Python 3.13+
- UV package manager
- OpenAI-compatible API key (DASHSCOPE_API_KEY)

### Installation

```bash
# Init and update submodule(gte-small-zh embedding)
git submodule update --init

# Install dependencies with UV
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and add your DASHSCOPE_API_KEY
```

### Build Index

Place your text documents in the `texts/` directory:

```bash
mkdir -p texts/
# Add your .txt files to the texts/ directory
# Build the FAISS index from documents
uv run build_index.py
```

This will:
- Load all `.txt` files from the `texts/` directory
- Split documents into chunks using semantic text splitting
- Generate embeddings using `thenlper/gte-small` model
- Save the FAISS index to `faiss_index/`

If you have a pre-built index, place it in the project directory and the system will automatically load it.

### Run Demo

#### Local Development

```bash
# Start the FastAPI server
uv run app.py
```

The API will be available at `http://localhost:8000`


#### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or manually with Docker
docker build -t agentic-rag .
docker run -p 7860:7860 -e DASHSCOPE_API_KEY=your_key_here agentic-rag
```

## API Documentation

### Base URL
`http://localhost:8000`

### Endpoints

#### Create New Session
- **URL**: `/sessions`
- **Method**: `POST`
- **Description**: Creates a new session for the authenticated user and returns a unique session ID
- **Headers**: 
  - `x-api-key`: API key for authentication
- **Response**:
  ```json
  {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

#### Send Message
- **URL**: `/messages`
- **Method**: `POST`
- **Description**: Sends a message to the agent within an existing session
- **Headers**: 
  - `x-api-key`: API key for authentication
- **Body**:
  ```json
  {
    "message": "What is the博士生活补贴?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```
- **Response**:
  ```json
  {
    "response": "博士生活补贴 ...",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

#### Get Session History
- **URL**: `/sessions/{session_id}/history`
- **Method**: `GET`
- **Description**: Retrieves the conversation history for a session
- **Headers**: 
  - `x-api-key`: API key for authentication
- **Response**:
  ```json
  {
    "history": [
      {"role": "user", "content": "博士生活补贴是多少?"},
      {"role": "assistant", "content": "博士生活补贴 ..."}
    ],
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

#### List Sessions
- **URL**: `/sessions`
- **Method**: `GET`
- **Description**: Lists all active session IDs for the authenticated user
- **Headers**: 
  - `x-api-key`: API key for authentication
- **Response**:
  ```json
  {
    "session_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
    ]
  }
  ```

#### Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Checks if the API server is running
- **Headers**: 
  - `x-api-key`: API key for authentication
- **Response**:
  ```json
  {
    "status": "healthy"
  }
  ```

### Example Usage

#### 1. Create a new session:
```bash
curl -X POST http://localhost:8000/sessions \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json"

# httpie
http post :8000/sessions \
  x-api-key:your-api-key
```

#### 2. Send a message:
```bash
curl -X POST http://localhost:8000/messages \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "博士生活补贴是多少?", "session_id": "550e8400-e29b-41d4-a716-446655440000"}'

# httpie
http post :8000/messages \
  x-api-key:your-api-key \
  message="本科生活补贴是多少?" \
  session_id="d50314c4-33c5-444d-801f-a6fa8707d92a" 
```

#### 3. Get conversation history:
```bash
curl "http://localhost:8000/sessions/550e8400-e29b-41d4-a716-446655440000/history" \
  -H "x-api-key: your-api-key"

# httpie
http get :8000/sessions/d50314c4-33c5-444d-801f-a6fa8707d92a/history \
  x-api-key:your-api-key
```

#### 4. List all sessions:
```bash
curl "http://localhost:8000/sessions" \
  -H "x-api-key: your-api-key"

# httpie
http get :8000/sessions \
  x-api-key:your-api-key
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHSCOPE_API_KEY` | API key for DASHSCOPE/OpenAI-compatible service | Required |
| `OPENAI_MODEL` | Model to use | `deepseek-v3` |
| `OPENAI_API_URL` | API endpoint | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `API_KEYS` | Comma-separated list of valid API keys for authentication (format: "key1:user1,key2:user2") | `default-api-key:default-user` |

## Unit Test
Run unit test, all calls to LLM are mocked.

```bash
uv run run_tests.py
# or
uv run pytest
```

## References
[https://huggingface.co/learn/cookbook/agent_rag](https://huggingface.co/learn/cookbook/agent_rag)

