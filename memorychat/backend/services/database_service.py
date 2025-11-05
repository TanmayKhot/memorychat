"""
Database service layer for MemoryChat Multi-Agent application.
Provides CRUD operations for all database entities with error handling and transaction management.
"""
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, and_

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database.models import (
    User, MemoryProfile, ChatSession, ChatMessage, Memory, AgentLog
)


class DatabaseService:
    """Service class for database operations."""
    
    def __init__(self, db: Session):
        """Initialize database service with a database session."""
        self.db = db
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    def create_user(self, email: str, username: str) -> User:
        """Create a new user."""
        try:
            user = User(email=email, username=username)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"User with email '{email}' or username '{username}' already exists") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create user: {str(e)}") from e
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get user: {str(e)}") from e
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get user: {str(e)}") from e
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return None
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Update violates unique constraint: {str(e)}") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update user: {str(e)}") from e
    
    # ========================================================================
    # MEMORY PROFILE OPERATIONS
    # ========================================================================
    
    def create_memory_profile(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False,
        system_prompt: Optional[str] = None,
        personality_traits: Optional[Dict[str, Any]] = None
    ) -> MemoryProfile:
        """Create a new memory profile."""
        try:
            # If this is the first profile or is_default is True, unset other defaults
            if is_default:
                self.db.query(MemoryProfile).filter(
                    MemoryProfile.user_id == user_id,
                    MemoryProfile.is_default == True
                ).update({"is_default": False})
            
            # If no profiles exist, make this one default
            existing_count = self.db.query(MemoryProfile).filter(
                MemoryProfile.user_id == user_id
            ).count()
            if existing_count == 0:
                is_default = True
            
            # Convert personality_traits dict to JSON string if provided
            traits_json = json.dumps(personality_traits) if personality_traits else None
            
            profile = MemoryProfile(
                user_id=user_id,
                name=name,
                description=description,
                is_default=is_default,
                system_prompt=system_prompt,
                personality_traits=traits_json
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Profile with name '{name}' already exists for this user") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create memory profile: {str(e)}") from e
    
    def get_memory_profiles_by_user(self, user_id: int) -> List[MemoryProfile]:
        """Get all memory profiles for a user."""
        try:
            return self.db.query(MemoryProfile).filter(
                MemoryProfile.user_id == user_id
            ).order_by(MemoryProfile.is_default.desc(), MemoryProfile.created_at.desc()).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get memory profiles: {str(e)}") from e
    
    def get_memory_profile_by_id(self, profile_id: int) -> Optional[MemoryProfile]:
        """Get memory profile by ID."""
        try:
            return self.db.query(MemoryProfile).filter(MemoryProfile.id == profile_id).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get memory profile: {str(e)}") from e
    
    def update_memory_profile(self, profile_id: int, **kwargs) -> Optional[MemoryProfile]:
        """Update memory profile fields."""
        try:
            profile = self.get_memory_profile_by_id(profile_id)
            if not profile:
                return None
            
            # Handle is_default specially - unset other defaults if setting this one
            if kwargs.get("is_default") is True:
                self.db.query(MemoryProfile).filter(
                    MemoryProfile.user_id == profile.user_id,
                    MemoryProfile.id != profile_id,
                    MemoryProfile.is_default == True
                ).update({"is_default": False})
            
            # Handle personality_traits conversion
            if "personality_traits" in kwargs and isinstance(kwargs["personality_traits"], dict):
                kwargs["personality_traits"] = json.dumps(kwargs["personality_traits"])
            
            for key, value in kwargs.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Update violates unique constraint: {str(e)}") from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update memory profile: {str(e)}") from e
    
    def delete_memory_profile(self, profile_id: int) -> bool:
        """Delete a memory profile."""
        try:
            profile = self.get_memory_profile_by_id(profile_id)
            if not profile:
                return False
            
            # Check if this is the only profile for the user
            profile_count = self.db.query(MemoryProfile).filter(
                MemoryProfile.user_id == profile.user_id
            ).count()
            
            if profile_count <= 1:
                raise ValueError("Cannot delete the only memory profile for a user")
            
            self.db.delete(profile)
            self.db.commit()
            return True
        except ValueError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete memory profile: {str(e)}") from e
    
    def set_default_profile(self, profile_id: int, user_id: int) -> Optional[MemoryProfile]:
        """Set a memory profile as default for a user."""
        try:
            profile = self.get_memory_profile_by_id(profile_id)
            if not profile or profile.user_id != user_id:
                return None
            
            # Unset all other defaults for this user
            self.db.query(MemoryProfile).filter(
                MemoryProfile.user_id == user_id,
                MemoryProfile.id != profile_id
            ).update({"is_default": False})
            
            # Set this one as default
            profile.is_default = True
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to set default profile: {str(e)}") from e
    
    def get_default_profile(self, user_id: int) -> Optional[MemoryProfile]:
        """Get the default memory profile for a user."""
        try:
            return self.db.query(MemoryProfile).filter(
                MemoryProfile.user_id == user_id,
                MemoryProfile.is_default == True
            ).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get default profile: {str(e)}") from e
    
    # ========================================================================
    # SESSION OPERATIONS
    # ========================================================================
    
    def create_session(
        self,
        user_id: int,
        memory_profile_id: Optional[int] = None,
        privacy_mode: str = "normal",
        title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        try:
            # Validate privacy_mode
            if privacy_mode not in ["normal", "incognito", "pause_memory"]:
                raise ValueError(f"Invalid privacy_mode: {privacy_mode}")
            
            session = ChatSession(
                user_id=user_id,
                memory_profile_id=memory_profile_id,
                privacy_mode=privacy_mode,
                title=title
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create session: {str(e)}") from e
    
    def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        try:
            return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get session: {str(e)}") from e
    
    def get_sessions_by_user(self, user_id: int, limit: int = 20) -> List[ChatSession]:
        """Get all sessions for a user, ordered by most recent."""
        try:
            return self.db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(ChatSession.updated_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get sessions: {str(e)}") from e
    
    def update_session(self, session_id: int, **kwargs) -> Optional[ChatSession]:
        """Update session fields."""
        try:
            session = self.get_session_by_id(session_id)
            if not session:
                return None
            
            # Validate privacy_mode if being updated
            if "privacy_mode" in kwargs:
                if kwargs["privacy_mode"] not in ["normal", "incognito", "pause_memory"]:
                    raise ValueError(f"Invalid privacy_mode: {kwargs['privacy_mode']}")
            
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            self.db.commit()
            self.db.refresh(session)
            return session
        except ValueError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update session: {str(e)}") from e
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a session and all its messages."""
        try:
            session = self.get_session_by_id(session_id)
            if not session:
                return False
            
            self.db.delete(session)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete session: {str(e)}") from e
    
    # ========================================================================
    # MESSAGE OPERATIONS
    # ========================================================================
    
    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Create a new chat message."""
        try:
            # Validate role
            if role not in ["user", "assistant", "system"]:
                raise ValueError(f"Invalid role: {role}")
            
            # Convert metadata dict to JSON string if provided
            metadata_json = json.dumps(metadata) if metadata else None
            
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                agent_name=agent_name,
                message_metadata=metadata_json
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except ValueError:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create message: {str(e)}") from e
    
    def get_messages_by_session(self, session_id: int) -> List[ChatMessage]:
        """Get all messages for a session, ordered by creation time."""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get messages: {str(e)}") from e
    
    def get_recent_messages(self, session_id: int, limit: int = 10) -> List[ChatMessage]:
        """Get recent messages for a session."""
        try:
            return self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get recent messages: {str(e)}") from e
    
    def delete_messages_by_session(self, session_id: int) -> int:
        """Delete all messages for a session."""
        try:
            count = self.db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).delete()
            self.db.commit()
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete messages: {str(e)}") from e
    
    # ========================================================================
    # MEMORY OPERATIONS
    # ========================================================================
    
    def create_memory(
        self,
        user_id: int,
        profile_id: int,
        content: str,
        importance_score: float = 0.5,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Memory:
        """Create a new memory."""
        try:
            # Convert tags list to JSON string if provided
            tags_json = json.dumps(tags) if tags else None
            
            memory = Memory(
                user_id=user_id,
                memory_profile_id=profile_id,
                content=content,
                importance_score=importance_score,
                memory_type=memory_type,
                tags=tags_json
            )
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            return memory
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create memory: {str(e)}") from e
    
    def get_memories_by_profile(self, profile_id: int) -> List[Memory]:
        """Get all memories for a profile."""
        try:
            return self.db.query(Memory).filter(
                Memory.memory_profile_id == profile_id
            ).order_by(Memory.importance_score.desc(), Memory.created_at.desc()).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get memories: {str(e)}") from e
    
    def update_memory(self, memory_id: int, **kwargs) -> Optional[Memory]:
        """Update memory fields."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return None
            
            # Handle tags conversion
            if "tags" in kwargs and isinstance(kwargs["tags"], list):
                kwargs["tags"] = json.dumps(kwargs["tags"])
            
            for key, value in kwargs.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            
            self.db.commit()
            self.db.refresh(memory)
            return memory
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update memory: {str(e)}") from e
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return False
            
            self.db.delete(memory)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete memory: {str(e)}") from e
    
    def increment_mention_count(self, memory_id: int) -> Optional[Memory]:
        """Increment the mention count for a memory."""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return None
            
            memory.mentioned_count = (memory.mentioned_count or 0) + 1
            self.db.commit()
            self.db.refresh(memory)
            return memory
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to increment mention count: {str(e)}") from e
    
    def search_memories(self, profile_id: int, query_text: str, limit: int = 10) -> List[Memory]:
        """Search memories by content (simple text search)."""
        try:
            return self.db.query(Memory).filter(
                and_(
                    Memory.memory_profile_id == profile_id,
                    Memory.content.like(f"%{query_text}%")
                )
            ).order_by(Memory.importance_score.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to search memories: {str(e)}") from e
    
    # ========================================================================
    # AGENT LOG OPERATIONS
    # ========================================================================
    
    def log_agent_action(
        self,
        session_id: Optional[int],
        agent_name: str,
        action: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> AgentLog:
        """Log an agent action."""
        try:
            # Convert dicts to JSON strings
            input_json = json.dumps(input_data) if input_data else None
            output_json = json.dumps(output_data) if output_data else None
            
            log = AgentLog(
                session_id=session_id,
                agent_name=agent_name,
                action=action,
                input_data=input_json,
                output_data=output_json,
                execution_time_ms=execution_time_ms,
                status=status,
                error_message=error_message
            )
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to log agent action: {str(e)}") from e
    
    def get_logs_by_session(self, session_id: int) -> List[AgentLog]:
        """Get all logs for a session."""
        try:
            return self.db.query(AgentLog).filter(
                AgentLog.session_id == session_id
            ).order_by(AgentLog.created_at.desc()).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get logs: {str(e)}") from e
    
    def get_logs_by_agent(self, agent_name: str, limit: int = 100) -> List[AgentLog]:
        """Get recent logs for an agent."""
        try:
            return self.db.query(AgentLog).filter(
                AgentLog.agent_name == agent_name
            ).order_by(AgentLog.created_at.desc()).limit(limit).all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to get logs: {str(e)}") from e

