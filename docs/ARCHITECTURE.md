# Architecture Overview

## System Architecture

MemoryChat Multi-Agent is a conversational AI system that maintains persistent memory across sessions using a multi-agent architecture and Mem0 for intelligent memory management.

## Core Components

### 1. API Layer
- **Technology**: FastAPI
- **Purpose**: RESTful API endpoints for user interactions
- **Endpoints**:
  - User management
  - Memory profile management
  - Chat sessions
  - Memory operations
  - Analytics

### 2. Services Layer
- **Database Service**: Manages SQLite database operations
- **Chat Service**: Handles conversation processing
- **Mem0 Service**: Integrates with Mem0 for memory management
- **Monitoring Service**: Tracks system health and performance
- **Error Handler**: Centralized error handling

### 3. Multi-Agent System
The system uses specialized AI agents that work together:

- **Context Coordinator Agent**: Orchestrates all agents and manages conversation flow
- **Conversation Agent**: Generates natural, contextually appropriate responses
- **Memory Manager Agent**: Extracts and manages memories using Mem0
- **Memory Retrieval Agent**: Finds and ranks relevant memories using Mem0
- **Privacy Guardian Agent**: Detects sensitive information and enforces privacy settings
- **Conversation Analyst Agent**: Analyzes conversations and provides insights

### 4. Data Storage

#### SQLite Database
- **Purpose**: Structured relational data storage
- **Stores**:
  - User accounts
  - Memory profiles
  - Chat sessions
  - Message history
  - Analytics metadata
- **Location**: `data/sqlite/memorychat.db`

#### Mem0 Memory Storage
- **Purpose**: Intelligent memory storage and retrieval
- **Technology**: Mem0 library with Qdrant vector database
- **Features**:
  - Automatic memory extraction from conversations
  - Semantic search for relevant memories
  - Memory deduplication
  - Importance scoring
  - Profile-based memory isolation
- **Storage**: Qdrant vector database in `data/qdrant/`
- **Integration**: Each memory profile maps to a Mem0 user_id for isolation

## Data Flow

1. **User Input** → API Endpoint
2. **API** → Context Coordinator Agent
3. **Context Coordinator** → Privacy Guardian Agent (if needed)
4. **Context Coordinator** → Memory Retrieval Agent (retrieves relevant memories via Mem0)
5. **Context Coordinator** → Conversation Agent (generates response with context)
6. **Context Coordinator** → Memory Manager Agent (extracts new memories via Mem0)
7. **Response** → API → User

## Memory Management

### Mem0 Integration
- **Primary Memory System**: Mem0 handles all memory operations
- **Vector Database**: Qdrant (managed by Mem0)
- **Memory Types**: Facts, preferences, events, relationships
- **Isolation**: Each memory profile has isolated memories via Mem0 user_id mapping

### Memory Lifecycle
1. **Extraction**: Memory Manager Agent extracts memories from conversations using Mem0
2. **Storage**: Mem0 stores memories in Qdrant with embeddings
3. **Retrieval**: Memory Retrieval Agent queries Mem0 for relevant memories
4. **Usage**: Retrieved memories provide context to Conversation Agent

## Privacy Modes

1. **Normal Mode**: Full memory creation and usage
2. **Incognito Mode**: No memory creation or usage
3. **Pause Memory Mode**: Use existing memories but don't create new ones

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Memory Management**: Mem0, Qdrant
- **Database**: SQLite
- **AI/LLM**: OpenAI API
- **Frontend**: Vanilla JavaScript, HTML, CSS
- **Logging**: Loguru

## Security & Privacy

- Memory profiles provide isolation between different contexts
- Privacy Guardian Agent enforces privacy settings
- Sensitive information detection and handling
- User-controlled privacy modes

