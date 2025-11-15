# Directory Structure

This document describes the directory structure of the MemoryChat Multi-Agent application.

## Data Directories

### `data/qdrant/`
- **Purpose**: Stores Mem0's vector database
- **Content**: Qdrant vector database files used by Mem0 for memory storage and retrieval
- **Managed by**: Mem0 library (automatically created and managed)
- **Git**: Ignored (see `.gitignore`)

### `data/sqlite/`
- **Purpose**: Stores structured relational data
- **Content**: 
  - User accounts and authentication data
  - Memory profiles (isolated memory spaces)
  - Chat sessions
  - Message history
  - Analytics and metadata
- **Files**: `memorychat.db` (SQLite database file)
- **Git**: Database files are ignored, but schema is tracked in `backend/database/schema.sql`

## Project Structure

```
memory-multi-agent/
├── backend/              # Backend API and services
│   ├── agents/          # Multi-agent system
│   ├── api/             # API endpoints and middleware
│   ├── config/          # Configuration files
│   ├── database/        # Database models and schema
│   ├── services/       # Business logic services
│   └── tests/           # Test files
├── data/                # Data storage (git-ignored)
│   ├── qdrant/         # Mem0 vector database
│   └── sqlite/         # SQLite database files
├── docs/                # Documentation
├── frontend/            # Frontend web application
└── scripts/             # Utility scripts
```

## Notes

- **Memory Storage**: Mem0 handles all memory storage using Qdrant as the underlying vector database
- **Data Isolation**: Memory profiles are isolated at the application level, with each profile mapping to a Mem0 user_id
- **Persistence**: Both SQLite (structured data) and Qdrant (vector embeddings) persist data to disk

