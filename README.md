# MemoryChat

MemoryChat is a conversational AI that keeps track of your conversations across sessions, so you can pick up right where you left off. It uses a smart multi-agent system to manage memories, enforce privacy, and give you full control over how your data is stored and used.

## Features

### Three Privacy Modes - Full Control Over Your Data

- **Normal Mode**: Your conversations are saved and used to provide better context in future chats. The AI remembers important details about you and uses them to give more personalized responses.

- **Incognito Mode**: Complete privacy - nothing gets saved. Your messages aren't stored, memories aren't created, and the session clears when you're done. Perfect for sensitive conversations or when you just want a quick chat without leaving traces.

- **Pause Memory Mode**: Use existing memories for context but don't create new ones. Great for temporary conversations where you want the AI to remember past context but don't want to add to your memory bank.

### Smart Memory Management

- Intelligently extracts important information from your conversations - **facts about you**, **preferences**, **events**, **relationships** - and stores them with importance scores
- Uses **semantic search** to find relevant memories when you need them, making conversations feel more natural and contextually aware

### Memory Profiles

- Create different personality profiles for different contexts - a **work profile** for professional conversations, a **personal one** for casual chats, or **custom profiles** with their own memory spaces
- Each profile has **isolated memories**, so your work conversations don't mix with personal ones

### Multi-Agent Architecture

- Behind the scenes, a team of specialized AI agents work together - one handles conversations, another manages memories, one enforces privacy, and they're all coordinated by a central orchestrator
- This makes the system more **reliable** and gives you **better control**

## Steps to Run the Project

1. **Navigate to Backend Directory**
   ```bash
   cd memorychat/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate Virtual Environment**
   
   **Linux/Mac:**
   ```bash
   source .venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**
   
   Create a `.env` file in `backend/`:
   ```bash
   cd memorychat/backend
   cat > .env << EOF
   OPENAI_API_KEY=your-api-key-here
   ENVIRONMENT=development
   LOG_LEVEL=DEBUG
   SQLITE_DATABASE_PATH=../data/sqlite/memorychat.db
   MEM0_API_KEY=your-mem0-api-key-here
   MEM0_ORGANIZATION_ID=your-org-id-here
   MEM0_PROJECT_ID=your-project-id-here
   QDRANT_PATH=../data/qdrant
   QDRANT_HOST=localhost
   QDRANT_PORT=6333
   API_HOST=127.0.0.1
   API_PORT=8000
   EOF
   ```

6. **Start Backend Server**
   ```bash
   cd memorychat
   ./scripts/start_backend.sh
   ```

7. **Start Frontend Server**
   ```bash
   cd memorychat
   ./scripts/start_frontend.sh
   ```

8. **Access the Application**
   - **Frontend UI**: http://127.0.0.1:8080/index.html
   - **Backend API**: http://127.0.0.1:8000
   - **API Documentation**: http://127.0.0.1:8000/docs

## Architecture

- **API Endpoints**: RESTful API layer handling user requests for users, memory profiles, sessions, chat, memories, and analytics
- **Services**: Business logic layer providing database operations, memory management, chat processing, monitoring, and error handling
- **Database**: SQLite database for structured data storage and Mem0 with Qdrant for intelligent memory storage and retrieval
- **Agents**: Multi-agent system coordinating conversation, memory management, privacy enforcement, and analysis
- **Frontend**: Web-based user interface built with vanilla JavaScript for interacting with the backend API

## List of Agents

- **Context Coordinator Agent**: Orchestrates all other agents and manages the conversation flow
- **Privacy Guardian Agent**: Detects sensitive information and enforces privacy settings
- **Memory Retrieval Agent**: Finds and ranks relevant memories for current conversation
- **Conversation Agent**: Main conversation agent that generates natural, contextually appropriate responses
- **Memory Manager Agent**: Extracts and manages memories from conversations
- **Conversation Analyst Agent**: Analyzes conversations and provides insights
