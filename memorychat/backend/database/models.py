"""
SQLAlchemy ORM models for MemoryChat Multi-Agent application.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Boolean, REAL, ForeignKey, CheckConstraint, TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model representing application users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    memory_profiles = relationship("MemoryProfile", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MemoryProfile(Base):
    """Memory profile model representing different memory contexts for users."""
    __tablename__ = "memory_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    personality_traits = Column(Text)  # JSON string
    system_prompt = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="memory_profiles")
    chat_sessions = relationship("ChatSession", back_populates="memory_profile")
    memories = relationship("Memory", back_populates="memory_profile", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("is_default IN (0, 1)", name="check_is_default"),
    )

    def __repr__(self):
        return f"<MemoryProfile(id={self.id}, user_id={self.user_id}, name='{self.name}', is_default={self.is_default})>"

    def to_dict(self):
        """Convert memory profile to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "is_default": bool(self.is_default),
            "personality_traits": self.personality_traits,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatSession(Base):
    """Chat session model representing a conversation session."""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_profile_id = Column(Integer, ForeignKey("memory_profiles.id", ondelete="SET NULL"), nullable=True)
    privacy_mode = Column(String, default="normal")
    title = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    memory_profile = relationship("MemoryProfile", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="session")

    __table_args__ = (
        CheckConstraint("privacy_mode IN ('normal', 'incognito', 'pause_memory')", name="check_privacy_mode"),
    )

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, privacy_mode='{self.privacy_mode}')>"

    def to_dict(self):
        """Convert chat session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "memory_profile_id": self.memory_profile_id,
            "privacy_mode": self.privacy_mode,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ChatMessage(Base):
    """Chat message model representing individual messages in a session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    agent_name = Column(String)
    message_metadata = Column(Text)  # JSON string (renamed from metadata to avoid SQLAlchemy conflict)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_role"),
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}')>"

    def to_dict(self):
        """Convert chat message to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "agent_name": self.agent_name,
            "metadata": self.message_metadata,  # Map to 'metadata' in API
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Memory(Base):
    """Memory model representing extracted memories from conversations."""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    memory_profile_id = Column(Integer, ForeignKey("memory_profiles.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    importance_score = Column(REAL, default=0.5)
    memory_type = Column(String)
    tags = Column(Text)  # JSON array as string
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    mentioned_count = Column(Integer, default=1)

    # Relationships
    user = relationship("User", back_populates="memories")
    memory_profile = relationship("MemoryProfile", back_populates="memories")

    def __repr__(self):
        return f"<Memory(id={self.id}, user_id={self.user_id}, profile_id={self.memory_profile_id}, type='{self.memory_type}')>"

    def to_dict(self):
        """Convert memory to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "memory_profile_id": self.memory_profile_id,
            "content": self.content,
            "importance_score": self.importance_score,
            "memory_type": self.memory_type,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "mentioned_count": self.mentioned_count,
        }


class AgentLog(Base):
    """Agent log model representing agent execution logs."""
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    input_data = Column(Text)  # JSON string
    output_data = Column(Text)  # JSON string
    execution_time_ms = Column(Integer)
    status = Column(String)
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    session = relationship("ChatSession", back_populates="agent_logs")

    def __repr__(self):
        return f"<AgentLog(id={self.id}, agent_name='{self.agent_name}', action='{self.action}', status='{self.status}')>"

    def to_dict(self):
        """Convert agent log to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "action": self.action,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

