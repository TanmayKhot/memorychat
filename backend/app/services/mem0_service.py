"""
mem0 service.
Handles memory operations using mem0 AI.
"""

import os
from typing import Optional, List, Dict, Any
from mem0 import Memory
from app.core.config import settings


class Mem0Service:
    """
    Service class for mem0 memory operations.
    Handles memory storage, retrieval, and management with memory profile support.
    """
    
    def __init__(self):
        """Initialize mem0 client with configuration."""
        # Configure mem0 with LLM and vector store
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": settings.OPENAI_MODEL,
                    "temperature": settings.OPENAI_TEMPERATURE,
                    "max_tokens": settings.OPENAI_MAX_TOKENS,
                    "api_key": settings.OPENAI_API_KEY
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "api_key": settings.OPENAI_API_KEY
                }
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "memorychat_memories",
                    "path": "./qdrant_data"  # Local Qdrant storage
                }
            }
        }
        
        # Initialize Memory client
        self.memory = Memory.from_config(config)
    
    # ========================
    # Core Memory Operations
    # ========================
    
    async def add_memory(
        self,
        user_id: str,
        memory_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new memory for a user.
        
        Args:
            user_id: User UUID
            memory_content: Content to store as memory
            metadata: Optional metadata including memory_profile_id
            
        Returns:
            Dictionary with memory ID and status
        """
        try:
            # Prepare metadata with memory profile ID
            mem_metadata = metadata or {}
            
            # Create user identifier with profile namespacing
            # Format: user_id:profile_id
            profile_id = mem_metadata.get("memory_profile_id", "default")
            user_identifier = f"{user_id}:{profile_id}"
            
            # Add memory using mem0
            result = self.memory.add(
                messages=memory_content,
                user_id=user_identifier,
                metadata=mem_metadata
            )
            
            return {
                "success": True,
                "memory_id": result.get("id") if isinstance(result, dict) else None,
                "result": result
            }
        except Exception as e:
            print(f"Error adding memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_memories(
        self,
        user_id: str,
        memory_profile_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a user and memory profile.
        
        Args:
            user_id: User UUID
            memory_profile_id: Optional memory profile UUID
            
        Returns:
            List of memory records
        """
        try:
            # Create user identifier with profile namespacing
            profile_id = memory_profile_id or "default"
            user_identifier = f"{user_id}:{profile_id}"
            
            # Get all memories for this user/profile
            result = self.memory.get_all(user_id=user_identifier)
            
            if isinstance(result, dict) and "results" in result:
                return result["results"]
            elif isinstance(result, list):
                return result
            else:
                return []
        except Exception as e:
            print(f"Error getting memories: {e}")
            return []
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        memory_profile_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories based on query.
        
        Args:
            user_id: User UUID
            query: Search query
            memory_profile_id: Optional memory profile UUID
            limit: Maximum number of results
            
        Returns:
            List of relevant memory records
        """
        try:
            # Create user identifier with profile namespacing
            profile_id = memory_profile_id or "default"
            user_identifier = f"{user_id}:{profile_id}"
            
            # Search memories
            result = self.memory.search(
                query=query,
                user_id=user_identifier,
                limit=limit
            )
            
            if isinstance(result, dict) and "results" in result:
                return result["results"]
            elif isinstance(result, list):
                return result
            else:
                return []
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if successful
        """
        try:
            self.memory.delete(memory_id=memory_id)
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    async def update_memory(
        self,
        memory_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Update an existing memory's content.
        
        Args:
            memory_id: Memory ID to update
            content: New content
            
        Returns:
            Updated memory information
        """
        try:
            result = self.memory.update(
                memory_id=memory_id,
                data=content
            )
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            print(f"Error updating memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_all_memories(
        self,
        user_id: str,
        memory_profile_id: Optional[str] = None
    ) -> bool:
        """
        Delete all memories for a user and memory profile.
        
        Args:
            user_id: User UUID
            memory_profile_id: Optional memory profile UUID
            
        Returns:
            True if successful
        """
        try:
            # Create user identifier with profile namespacing
            profile_id = memory_profile_id or "default"
            user_identifier = f"{user_id}:{profile_id}"
            
            # Clear all memories for this user/profile
            self.memory.delete_all(user_id=user_identifier)
            return True
        except Exception as e:
            print(f"Error deleting all memories: {e}")
            return False
    
    # ========================
    # Memory Extraction
    # ========================
    
    async def extract_memories_from_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        memory_profile_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract and store memories from a conversation.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User UUID
            memory_profile_id: Optional memory profile UUID
            
        Returns:
            Dictionary with extraction results
        """
        try:
            # Create user identifier with profile namespacing
            profile_id = memory_profile_id or "default"
            user_identifier = f"{user_id}:{profile_id}"
            
            # Prepare metadata
            metadata = {
                "memory_profile_id": profile_id,
                "extracted_from": "conversation"
            }
            
            # Add memories from conversation
            # mem0 will automatically extract relevant information
            result = self.memory.add(
                messages=messages,
                user_id=user_identifier,
                metadata=metadata
            )
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            print(f"Error extracting memories from conversation: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================
    # Memory Profile Management
    # ========================
    
    def _create_user_identifier(self, user_id: str, memory_profile_id: Optional[str] = None) -> str:
        """
        Create a namespaced user identifier for memory profile isolation.
        
        Args:
            user_id: User UUID
            memory_profile_id: Optional memory profile UUID
            
        Returns:
            Formatted user identifier (user_id:profile_id)
        """
        profile_id = memory_profile_id or "default"
        return f"{user_id}:{profile_id}"
    
    async def copy_memories_to_profile(
        self,
        user_id: str,
        source_profile_id: str,
        target_profile_id: str
    ) -> bool:
        """
        Copy memories from one profile to another.
        
        Args:
            user_id: User UUID
            source_profile_id: Source memory profile UUID
            target_profile_id: Target memory profile UUID
            
        Returns:
            True if successful
        """
        try:
            # Get all memories from source profile
            source_memories = await self.get_memories(user_id, source_profile_id)
            
            # Add each memory to target profile
            target_identifier = self._create_user_identifier(user_id, target_profile_id)
            
            for memory_entry in source_memories:
                memory_content = memory_entry.get("memory", "")
                if memory_content:
                    self.memory.add(
                        messages=memory_content,
                        user_id=target_identifier,
                        metadata={
                            "memory_profile_id": target_profile_id,
                            "copied_from": source_profile_id
                        }
                    )
            
            return True
        except Exception as e:
            print(f"Error copying memories: {e}")
            return False


# Create a singleton instance
mem0_service = Mem0Service()
