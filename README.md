# MemoryChat Multi-Agent System

A sophisticated conversational AI application with persistent memory, privacy controls, and multi-agent orchestration. MemoryChat allows users to have natural conversations with an AI assistant that remembers context across sessions using different memory profiles.

## Features

- **Multi-Agent Architecture**: Coordinated AI agents for conversation, memory management, privacy enforcement, and analysis
- **Persistent Memory**: Store and retrieve contextual memories across conversations
- **Memory Profiles**: Organize conversations with different personality profiles and memory contexts
- **Privacy Controls**: Three privacy modes (Normal, Incognito, Pause Memory) for different privacy needs
- **Vector Search**: Semantic memory retrieval using ChromaDB for intelligent context matching
- **RESTful API**: Comprehensive FastAPI backend with full documentation
- **Modern Web UI**: Clean, responsive frontend built with vanilla JavaScript

## Project Structure

```
memorychat/
├── backend/          # FastAPI backend application
│   ├── agents/        # AI agent implementations
│   ├── api/          # API endpoints and middleware
│   ├── config/        # Configuration files
│   ├── database/     # Database models and schema
│   ├── services/     # Business logic services
│   └── main.py       # Application entry point
├── frontend/         # Web frontend (HTML/JS)
├── data/             # Database files (SQLite, ChromaDB)
├── scripts/          # Startup and utility scripts
└── docs/             # Documentation
```

## Prerequisites

- **Python 3.8+** installed
- **OpenAI API Key** (optional, for LLM features)
- **Git** (for cloning the repository)

## Setup Instructions

### 1. Navigate to Backend Directory

```bash
cd memorychat/backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate Virtual Environment

**Linux/Mac:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in `backend/`:

```bash
cd memorychat/backend
cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG
SQLITE_DATABASE_PATH=../data/sqlite/memorychat.db
CHROMADB_PATH=../data/chromadb
API_HOST=127.0.0.1
API_PORT=8000
EOF
```

**Important:** Replace `your-api-key-here` with your actual OpenAI API key if you want to use LLM features.

### 6. Initialize Database

The database will be automatically initialized when you first start the server. The database file will be created at `data/sqlite/memorychat.db`.

## How to Run

### Quick Start (Recommended)

Use the provided startup scripts for the easiest experience:

**Start everything:**
```bash
cd memorychat
./scripts/start_all.sh
```

This will:
- Start the backend server on http://127.0.0.1:8000
- Start the frontend server on http://127.0.0.1:8080
- Open your browser automatically
- Display all URLs

**Stop everything:**
```bash
cd memorychat
./scripts/stop_all.sh
```

### Manual Start

**Start Backend:**
```bash
cd memorychat
./scripts/start_backend.sh
```

Or manually:
```bash
cd memorychat/backend
source .venv/bin/activate
python main.py
```

**Start Frontend:**
```bash
cd memorychat
./scripts/start_frontend.sh
```

Or manually:
```bash
cd memorychat/frontend
python3 -m http.server 8080
```

### Access the Application

Once both servers are running:

- **Frontend UI**: http://127.0.0.1:8080/index.html
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health

## How to Use

### 1. Create a User

The first time you use the application, you'll need to create a user through the API or UI.

### 2. Create Memory Profiles

Memory profiles allow you to organize conversations with different contexts:

- **Work Profile**: For professional conversations
- **Personal Profile**: For casual conversations
- **Study Profile**: For educational content
- **Custom Profiles**: Create profiles with custom personalities

Each profile has:
- A name and description
- Personality traits (tone, verbosity, formality)
- A custom system prompt
- Isolated memory storage

### 3. Start a Chat Session

1. Select a user and memory profile
2. Choose a privacy mode:
   - **Normal**: Full memory storage and retrieval
   - **Incognito**: No memory storage or retrieval (private mode)
   - **Pause Memory**: Memory retrieval only, no new storage
3. Start chatting!

### 4. Privacy Modes Explained

**Normal Mode:**
- Memories are stored from conversations
- Memories are retrieved for context
- Full functionality enabled

**Incognito Mode:**
- No memories are stored
- No memories are retrieved
- Session data is cleared after conversation
- PII detection and warnings enabled

**Pause Memory Mode:**
- Existing memories are retrieved for context
- No new memories are stored
- Useful for temporary conversations

### 5. View and Manage Memories

- View all memories for a profile
- Search memories by keyword or semantic similarity
- Edit or delete individual memories
- See memory importance scores and types

## Troubleshooting

### Port Already in Use

**Error:** `Address already in use` or port conflicts

**Solution:**
```bash
# Find process using port 8000 (backend)
lsof -i :8000

# Find process using port 8080 (frontend)
lsof -i :8080

# Kill the process
kill <PID>

# Or use stop script
./scripts/stop_all.sh
```

### Backend Not Starting

**Check:**
1. Virtual environment is activated: `which python` should show `.venv/bin/python`
2. Dependencies installed: `pip list | grep fastapi`
3. Database directory exists: `ls memorychat/data/sqlite/`
4. .env file exists: `ls memorychat/backend/.env`

**Fix:**
```bash
cd memorychat/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Can't Connect to Backend

**Check:**
1. Backend is running: `curl http://127.0.0.1:8000/health`
2. CORS is configured (already done in main.py)
3. API URL in `frontend/js/config.js` matches backend URL
4. No firewall blocking connections

**Fix:**
- Ensure backend is running before starting frontend
- Check browser console for errors
- Verify API_BASE_URL in frontend config

### Database Errors

**Error:** `Database file not found` or `Table does not exist`

**Solution:**
The database is automatically created on first server start. If you encounter issues:
1. Ensure the `data/sqlite/` directory exists
2. Check file permissions
3. Restart the server

### Import Errors

**Error:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```bash
cd memorychat/backend
source .venv/bin/activate
pip install -r requirements.txt
```

### OpenAI API Errors

**Error:** `Invalid API key` or `Rate limit exceeded`

**Solution:**
1. Check your API key in `backend/.env`
2. Verify the key is valid and has credits
3. Check OpenAI service status

**Note:** Some features work without an API key, but LLM-based features require it.

### ChromaDB Initialization Fails

**Warning:** ChromaDB may not initialize without an OpenAI API key

**Solution:**
- This is expected if OPENAI_API_KEY is not set
- ChromaDB will initialize when first used with a valid API key
- Basic functionality works without ChromaDB (uses SQL search only)

## Development

### Running Tests

```bash
cd memorychat/backend
source .venv/bin/activate
python -m pytest tests/
```

### Project Structure Details

- **Agents**: Located in `backend/agents/`
  - `base_agent.py`: Base class for all agents
  - `conversation_agent.py`: Main conversation handler
  - `memory_manager_agent.py`: Memory extraction and storage
  - `memory_retrieval_agent.py`: Memory search and retrieval
  - `privacy_guardian_agent.py`: Privacy enforcement
  - `conversation_analyst_agent.py`: Conversation analysis
  - `context_coordinator_agent.py`: Agent orchestration

- **API Endpoints**: Located in `backend/api/endpoints/`
  - `users.py`: User management
  - `memory_profiles.py`: Profile management
  - `sessions.py`: Session management
  - `chat.py`: Chat messaging
  - `memories.py`: Memory operations
  - `analytics.py`: Analytics endpoints

- **Services**: Located in `backend/services/`
  - `database_service.py`: Database operations
  - `vector_service.py`: ChromaDB operations
  - `chat_service.py`: Chat processing
  - `monitoring_service.py`: Performance monitoring
  - `error_handler.py`: Error handling

### Logging

Logs are stored in `backend/logs/`:
- `app.log`: General application logs
- `errors.log`: Error logs only
- `database.log`: Database operation logs
- `agents/`: Agent-specific logs

View logs:
```bash
tail -f memorychat/backend/logs/app.log
tail -f memorychat/backend/logs/errors.log
```

## API Documentation

Full API documentation is available when the backend is running:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Architecture

MemoryChat uses a multi-agent architecture:

1. **Context Coordinator Agent**: Orchestrates all other agents
2. **Privacy Guardian Agent**: Enforces privacy rules and detects PII
3. **Memory Retrieval Agent**: Finds relevant memories for context
4. **Conversation Agent**: Generates responses using context
5. **Memory Manager Agent**: Extracts and stores new memories
6. **Conversation Analyst Agent**: Analyzes conversations for insights

## License

[Add your license here]

## Support

For issues, questions, or contributions, please [add your support channels here].

## Acknowledgments

Built with:
- FastAPI for the backend API
- LangChain for LLM integration
- ChromaDB for vector storage
- SQLAlchemy for database ORM
- Vanilla JavaScript for the frontend
