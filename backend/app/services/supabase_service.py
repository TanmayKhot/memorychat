"""
Supabase service.
Handles all database operations through Supabase.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.core.config import settings


class SupabaseService:
    """
    Service class for all Supabase database operations.
    Handles users, memory profiles, chat sessions, messages, and memory references.
    """
    
    def __init__(self):
        """Initialize Supabase client with service key for admin operations."""
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )
    
    # ========================
    # User Operations
    # ========================
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User record or None if not found
        """
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            raise
    
    async def create_user(self, email: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user record.
        
        Args:
            email: User email
            user_id: Optional user UUID (from Supabase Auth)
            
        Returns:
            Created user record
        """
        try:
            user_data = {"email": email}
            if user_id:
                user_data["id"] = user_id
            
            response = self.client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    # ========================
    # Memory Profile Operations
    # ========================
    
    async def get_memory_profiles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all memory profiles for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            List of memory profile records
        """
        try:
            response = self.client.table("memory_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=False)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting memory profiles: {e}")
            raise
    
    async def create_memory_profile(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        is_default: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new memory profile.
        
        Args:
            user_id: User UUID
            name: Profile name
            description: Optional profile description
            is_default: Whether this is the default profile
            
        Returns:
            Created memory profile record
        """
        try:
            # If setting as default, unset other defaults first
            if is_default:
                await self._unset_all_defaults(user_id)
            
            profile_data = {
                "user_id": user_id,
                "name": name,
                "description": description,
                "is_default": is_default
            }
            
            response = self.client.table("memory_profiles").insert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating memory profile: {e}")
            raise
    
    async def update_memory_profile(
        self,
        profile_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a memory profile.
        
        Args:
            profile_id: Profile UUID
            data: Dictionary of fields to update
            
        Returns:
            Updated memory profile record
        """
        try:
            # If setting as default, get user_id and unset other defaults
            if data.get("is_default"):
                profile = await self.get_memory_profile(profile_id)
                if profile:
                    await self._unset_all_defaults(profile["user_id"])
            
            response = self.client.table("memory_profiles")\
                .update(data)\
                .eq("id", profile_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating memory profile: {e}")
            raise
    
    async def delete_memory_profile(self, profile_id: str) -> bool:
        """
        Delete a memory profile.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            True if successful
        """
        try:
            self.client.table("memory_profiles").delete().eq("id", profile_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting memory profile: {e}")
            raise
    
    async def get_memory_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single memory profile by ID.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Memory profile record or None
        """
        try:
            response = self.client.table("memory_profiles")\
                .select("*")\
                .eq("id", profile_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting memory profile: {e}")
            raise
    
    async def get_default_memory_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the default memory profile for a user.
        
        Args:
            user_id: User UUID
            
        Returns:
            Default memory profile or None
        """
        try:
            response = self.client.table("memory_profiles")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("is_default", True)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting default memory profile: {e}")
            raise
    
    async def set_default_memory_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Set a memory profile as default.
        
        Args:
            profile_id: Profile UUID
            
        Returns:
            Updated memory profile record
        """
        try:
            # Get the profile to find user_id
            profile = await self.get_memory_profile(profile_id)
            if not profile:
                raise ValueError("Profile not found")
            
            # Unset all other defaults for this user
            await self._unset_all_defaults(profile["user_id"])
            
            # Set this one as default
            return await self.update_memory_profile(profile_id, {"is_default": True})
        except Exception as e:
            print(f"Error setting default memory profile: {e}")
            raise
    
    async def _unset_all_defaults(self, user_id: str) -> None:
        """
        Unset is_default for all profiles of a user.
        
        Args:
            user_id: User UUID
        """
        try:
            self.client.table("memory_profiles")\
                .update({"is_default": False})\
                .eq("user_id", user_id)\
                .eq("is_default", True)\
                .execute()
        except Exception as e:
            print(f"Error unsetting defaults: {e}")
            # Don't raise here, as this is a helper method
    
    # ========================
    # Chat Session Operations
    # ========================
    
    async def create_chat_session(
        self,
        user_id: str,
        profile_id: Optional[str] = None,
        privacy_mode: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new chat session.
        
        Args:
            user_id: User UUID
            profile_id: Optional memory profile UUID
            privacy_mode: Privacy mode (normal, incognito, pause_memories)
            
        Returns:
            Created chat session record
        """
        try:
            session_data = {
                "user_id": user_id,
                "memory_profile_id": profile_id,
                "privacy_mode": privacy_mode
            }
            
            response = self.client.table("chat_sessions").insert(session_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating chat session: {e}")
            raise
    
    async def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat session by ID.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Chat session record or None
        """
        try:
            response = self.client.table("chat_sessions")\
                .select("*")\
                .eq("id", session_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting chat session: {e}")
            raise
    
    async def update_chat_session(
        self,
        session_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a chat session.
        
        Args:
            session_id: Session UUID
            data: Dictionary of fields to update
            
        Returns:
            Updated chat session record
        """
        try:
            response = self.client.table("chat_sessions")\
                .update(data)\
                .eq("id", session_id)\
                .execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating chat session: {e}")
            raise
    
    async def delete_chat_session(self, session_id: str) -> bool:
        """
        Delete a chat session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if successful
        """
        try:
            self.client.table("chat_sessions").delete().eq("id", session_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            raise
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User UUID
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of chat session records
        """
        try:
            response = self.client.table("chat_sessions")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .range(offset, offset + limit - 1)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            raise
    
    # ========================
    # Chat Message Operations
    # ========================
    
    async def create_chat_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new chat message.
        
        Args:
            session_id: Session UUID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Created chat message record
        """
        try:
            message_data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "metadata": metadata or {}
            }
            
            response = self.client.table("chat_messages").insert(message_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating chat message: {e}")
            raise
    
    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat session.
        
        Args:
            session_id: Session UUID
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List of chat message records
        """
        try:
            response = self.client.table("chat_messages")\
                .select("*")\
                .eq("session_id", session_id)\
                .order("created_at", desc=False)\
                .limit(limit)\
                .range(offset, offset + limit - 1)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting session messages: {e}")
            raise
    
    async def delete_session_messages(self, session_id: str) -> bool:
        """
        Delete all messages for a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if successful
        """
        try:
            self.client.table("chat_messages")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting session messages: {e}")
            raise
    
    # ========================
    # mem0 Memory Reference Operations
    # ========================
    
    async def store_mem0_memory_reference(
        self,
        user_id: str,
        profile_id: str,
        mem0_id: str,
        content: str
    ) -> Dict[str, Any]:
        """
        Store a reference to a mem0 memory in the database.
        
        Args:
            user_id: User UUID
            profile_id: Memory profile UUID
            mem0_id: mem0 memory ID
            content: Memory content
            
        Returns:
            Created memory reference record
        """
        try:
            memory_data = {
                "user_id": user_id,
                "memory_profile_id": profile_id,
                "mem0_memory_id": mem0_id,
                "memory_content": content
            }
            
            response = self.client.table("mem0_memories").insert(memory_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error storing mem0 memory reference: {e}")
            raise
    
    async def get_mem0_memory_references(
        self,
        profile_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all mem0 memory references for a profile.
        
        Args:
            profile_id: Memory profile UUID
            limit: Maximum number of references to return
            
        Returns:
            List of memory reference records
        """
        try:
            response = self.client.table("mem0_memories")\
                .select("*")\
                .eq("memory_profile_id", profile_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting mem0 memory references: {e}")
            raise
    
    async def delete_mem0_memory_reference(self, mem0_id: str) -> bool:
        """
        Delete a mem0 memory reference by mem0_memory_id.
        
        Args:
            mem0_id: mem0 memory ID
            
        Returns:
            True if successful
        """
        try:
            self.client.table("mem0_memories")\
                .delete()\
                .eq("mem0_memory_id", mem0_id)\
                .execute()
            return True
        except Exception as e:
            print(f"Error deleting mem0 memory reference: {e}")
            raise


# Create a singleton instance
supabase_service = SupabaseService()

