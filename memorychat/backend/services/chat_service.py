"""
Chat service for MemoryChat Multi-Agent application.
Handles message processing, agent orchestration, and data persistence.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.context_coordinator_agent import ContextCoordinatorAgent
from services.database_service import DatabaseService
from services.vector_service import VectorService
from config.logging_config import get_agent_logger


class ChatService:
    """
    Service class for processing chat messages through the agent system.
    
    Handles:
    - Agent orchestration via ContextCoordinatorAgent
    - Message persistence
    - Memory storage (database and vector store)
    - Request tracking and logging
    """
    
    def __init__(self, db: Session):
        """
        Initialize ChatService with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.db_service = DatabaseService(db)
        self.vector_service = VectorService()
        self.coordinator = ContextCoordinatorAgent()
        self.logger = get_agent_logger("ChatService")
    
    def process_message(
        self,
        session_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent system.
        
        This method:
        1. Gets session and profile from database
        2. Prepares input for ContextCoordinatorAgent
        3. Executes agent orchestration
        4. Saves messages to database
        5. Saves memories to database and vector store (if applicable)
        6. Logs agent execution
        7. Returns formatted response
        
        Args:
            session_id: Chat session ID
            user_message: User's message content
            
        Returns:
            Dictionary with response data:
            - message: Assistant response
            - memories_used: Number of memories used
            - new_memories_created: Number of new memories created
            - warnings: List of warnings
            - metadata: Additional metadata (tokens, execution time, etc.)
            
        Raises:
            ValueError: If session not found or invalid input
            RuntimeError: If processing fails
        """
        start_time = datetime.now()
        
        try:
            # Get session
            session = self.db_service.get_session_by_id(session_id)
            if not session:
                raise ValueError(f"Session with ID {session_id} not found")
            
            # Get profile if available
            profile = None
            if session.memory_profile_id:
                profile = self.db_service.get_memory_profile_by_id(session.memory_profile_id)
                if not profile:
                    self.logger.warning(f"Profile {session.memory_profile_id} not found for session {session_id}")
            
            # Get conversation history
            messages = self.db_service.get_messages_by_session(session_id)
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in messages[-10:]  # Last 10 messages for context
            ]
            
            # Prepare input for ContextCoordinatorAgent
            agent_input = self._prepare_agent_input(
                session=session,
                message=user_message,
                conversation_history=conversation_history
            )
            
            # Execute orchestration
            self.logger.info(f"Processing message for session {session_id}")
            result = self.coordinator.execute(agent_input)
            
            if not result.get("success"):
                error_msg = result.get("error", "Failed to process message")
                self.logger.error(f"Agent orchestration failed: {error_msg}")
                raise RuntimeError(error_msg)
            
            # Extract response data
            response_data = result.get("data", {})
            assistant_message = response_data.get("response", "")
            
            # Save conversation
            user_msg, assistant_msg = self._save_conversation(
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message
            )
            
            # Save memories if applicable (ONLY in normal mode)
            memory_extraction_info = response_data.get("memory_extraction_info", {})
            memories_extracted = memory_extraction_info.get("memories_extracted", 0)
            extracted_memories = response_data.get("extracted_memories", [])
            new_memories_created = 0
            
            # Explicitly check privacy mode - never save in incognito or pause_memory mode
            privacy_mode = session.privacy_mode.lower()
            if privacy_mode == "incognito":
                self.logger.debug(f"Skipping memory storage in INCOGNITO mode for session {session_id}")
            elif privacy_mode == "pause_memory":
                self.logger.debug(f"Skipping memory storage in PAUSE_MEMORY mode for session {session_id}")
            elif memories_extracted > 0 and privacy_mode == "normal" and extracted_memories:
                # Save memories to database and vector store (only in normal mode)
                if session.user_id and session.memory_profile_id:
                    new_memories_created = self._save_memories(
                        memories=extracted_memories,
                        profile_id=session.memory_profile_id,
                        user_id=session.user_id
                    )
                    self.logger.info(
                        f"Saved {new_memories_created} memories for session {session_id}"
                    )
                else:
                    self.logger.warning(
                        f"Cannot save memories: missing user_id or profile_id for session {session_id}"
                    )
            elif memories_extracted > 0:
                # Log if memories were extracted but not saved (shouldn't happen in normal mode)
                self.logger.warning(
                    f"Memories extracted ({memories_extracted}) but not saved for session {session_id} "
                    f"(privacy_mode={privacy_mode}, has_extracted={bool(extracted_memories)})"
                )
            
            # Extract metadata
            memory_info = response_data.get("memory_info", {})
            memories_used = memory_info.get("memories_retrieved", 0)
            warnings = response_data.get("warnings", [])
            
            # Build metadata
            execution_time_ms = result.get("execution_time_ms", 0)
            metadata = {
                "tokens_used": result.get("tokens_used", 0),
                "execution_time_ms": execution_time_ms,
                "agents_executed": result.get("agents_executed", []),
                "tokens_by_agent": result.get("tokens_by_agent", {}),
                "privacy_mode": session.privacy_mode,
                "profile_id": session.memory_profile_id,
            }
            
            # Log agent execution
            self.db_service.log_agent_action(
                session_id=session_id,
                agent_name="ContextCoordinatorAgent",
                action="process_message",
                input_data={
                    "message": user_message,
                    "session_id": session_id,
                    "privacy_mode": session.privacy_mode
                },
                output_data={
                    "response": assistant_message,
                    "memories_used": memories_used,
                    "new_memories_created": new_memories_created
                },
                execution_time_ms=execution_time_ms,
                status="success"
            )
            
            # Handle privacy mode specific actions
            self._handle_privacy_mode(session, result)
            
            total_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.logger.info(
                f"Message processed successfully: session={session_id}, "
                f"tokens={metadata['tokens_used']}, time={total_time_ms}ms"
            )
            
            return {
                "message": assistant_message,
                "memories_used": memories_used,
                "new_memories_created": new_memories_created,
                "warnings": warnings,
                "metadata": metadata
            }
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            
            # Log error
            try:
                self.db_service.log_agent_action(
                    session_id=session_id,
                    agent_name="ContextCoordinatorAgent",
                    action="process_message",
                    input_data={"message": user_message, "session_id": session_id},
                    output_data=None,
                    status="error",
                    error_message=str(e)
                )
            except:
                pass
            
            raise RuntimeError(f"Failed to process message: {str(e)}") from e
    
    def _prepare_agent_input(
        self,
        session: Any,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Prepare input data for ContextCoordinatorAgent.
        
        Args:
            session: ChatSession object
            message: User message
            conversation_history: List of previous messages
            
        Returns:
            Formatted input dictionary for agent
        """
        return {
            "session_id": session.id,
            "user_message": message,
            "privacy_mode": session.privacy_mode,
            "profile_id": session.memory_profile_id,
            "context": {
                "conversation_history": conversation_history
            }
        }
    
    def _save_conversation(
        self,
        session_id: int,
        user_message: str,
        assistant_message: str
    ) -> tuple:
        """
        Save user and assistant messages to database.
        
        Args:
            session_id: Session ID
            user_message: User message content
            assistant_message: Assistant response content
            
        Returns:
            Tuple of (user_message_obj, assistant_message_obj)
        """
        # Save user message
        user_msg = self.db_service.create_message(
            session_id=session_id,
            role="user",
            content=user_message
        )
        
        # Save assistant response
        assistant_msg = self.db_service.create_message(
            session_id=session_id,
            role="assistant",
            content=assistant_message,
            agent_name="ContextCoordinatorAgent"
        )
        
        return user_msg, assistant_msg
    
    def _save_memories(
        self,
        memories: List[Dict[str, Any]],
        profile_id: int,
        user_id: int
    ) -> int:
        """
        Save memories to database and vector store.
        
        Args:
            memories: List of memory dictionaries with:
                - content: str
                - importance_score: float
                - memory_type: str
                - tags: List[str]
            profile_id: Memory profile ID
            user_id: User ID
            
        Returns:
            Number of memories successfully saved
        """
        saved_count = 0
        
        for memory_data in memories:
            try:
                # Create memory in database
                memory = self.db_service.create_memory(
                    user_id=user_id,
                    profile_id=profile_id,
                    content=memory_data.get("content", ""),
                    importance_score=memory_data.get("importance_score", 0.5),
                    memory_type=memory_data.get("memory_type"),
                    tags=memory_data.get("tags", [])
                )
                
                # Add to vector store
                metadata = {
                    "profile_id": profile_id,
                    "user_id": user_id,
                    "memory_type": memory_data.get("memory_type", "other"),
                    "importance_score": memory_data.get("importance_score", 0.5)
                }
                
                self.vector_service.add_memory_embedding(
                    memory_id=memory.id,
                    content=memory.content,
                    metadata=metadata
                )
                
                saved_count += 1
                
            except Exception as e:
                self.logger.error(f"Failed to save memory: {str(e)}", exc_info=True)
                continue
        
        return saved_count
    
    def _handle_privacy_mode(
        self,
        session: Any,
        result: Dict[str, Any]
    ) -> None:
        """
        Handle privacy mode specific actions after message processing.
        
        Args:
            session: ChatSession object
            result: Agent orchestration result
        """
        privacy_mode = session.privacy_mode.lower()
        
        if privacy_mode == "incognito":
            # In incognito mode, ensure no memories were stored
            # The coordinator should have already prevented this, but double-check
            self.logger.debug(f"Incognito mode active for session {session.id}")
            
        elif privacy_mode == "pause_memory":
            # In pause memory mode, memories can be retrieved but not stored
            # This is already handled by the coordinator
            self.logger.debug(f"Pause memory mode active for session {session.id}")
            
        # Normal mode - no special handling needed
        # Memories are stored as part of normal flow

