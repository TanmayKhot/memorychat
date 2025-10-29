"""
Chat service.
Orchestrates SupabaseService, Mem0Service, and LLMService for complete chat flow.
"""

from typing import List, Dict, Any, Optional, AsyncIterator
from app.services.supabase_service import supabase_service
from app.services.mem0_service import mem0_service
from app.services.llm_service import llm_service


class ChatService:
    """
    Service class for chat operations.
    Orchestrates database, memory, and LLM services to handle conversations.
    """
    
    def __init__(self):
        """Initialize chat service with all required services."""
        self.supabase = supabase_service
        self.mem0 = mem0_service
        self.llm = llm_service
    
    # ========================
    # Core Chat Operations
    # ========================
    
    async def process_user_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message and generate AI response.
        
        This is the main orchestration method that:
        1. Gets session details and privacy mode
        2. Retrieves relevant memories (based on privacy mode)
        3. Constructs context with memories
        4. Generates AI response
        5. Saves both messages to database
        6. Extracts and saves new memories (based on privacy mode)
        
        Args:
            session_id: Chat session UUID
            user_message: User's message content
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Step 1: Get session details
            session = await self.supabase.get_chat_session(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found",
                    "error_type": "SessionNotFound"
                }
            
            user_id = session["user_id"]
            memory_profile_id = session.get("memory_profile_id")
            privacy_mode = session.get("privacy_mode", "normal")
            
            # Step 2: Get relevant memories based on privacy mode
            memories = []
            context = ""
            
            if privacy_mode in ["normal", "pause_memories"] and memory_profile_id:
                # Retrieve memories for context
                memories = await self.mem0.search_memories(
                    user_id=user_id,
                    query=user_message,
                    memory_profile_id=memory_profile_id,
                    limit=5
                )
                
                # Format memories into context string
                context = await self.llm.format_memory_context(memories)
            
            # Step 3: Get conversation history for context
            previous_messages = await self.supabase.get_session_messages(
                session_id=session_id,
                limit=10  # Last 10 messages for context
            )
            
            # Build message list for LLM
            conversation_messages = []
            for msg in previous_messages:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message
            conversation_messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Step 4: Generate AI response
            llm_response = await self.llm.generate_response(
                messages=conversation_messages,
                context=context
            )
            
            if not llm_response["success"]:
                return {
                    "success": False,
                    "error": "Failed to generate response",
                    "error_type": "LLMError",
                    "details": llm_response.get("error")
                }
            
            assistant_response = llm_response["content"]
            
            # Step 5: Save messages to database
            # Save user message
            await self.supabase.create_chat_message(
                session_id=session_id,
                role="user",
                content=user_message
            )
            
            # Save assistant message
            await self.supabase.create_chat_message(
                session_id=session_id,
                role="assistant",
                content=assistant_response,
                metadata={
                    "model": llm_response.get("model"),
                    "tokens": llm_response.get("usage", {}).get("total_tokens"),
                    "finish_reason": llm_response.get("finish_reason")
                }
            )
            
            # Step 6: Extract and save new memories (only in normal mode)
            memories_extracted = False
            if privacy_mode == "normal" and memory_profile_id:
                # Extract memories from the conversation
                extraction_result = await self.mem0.extract_memories_from_conversation(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": assistant_response}
                    ],
                    user_id=user_id,
                    memory_profile_id=memory_profile_id
                )
                memories_extracted = extraction_result.get("success", False)
            
            # Step 7: Return response
            return {
                "success": True,
                "content": assistant_response,
                "session_id": session_id,
                "privacy_mode": privacy_mode,
                "memories_used": len(memories),
                "memories_extracted": memories_extracted,
                "metadata": {
                    "model": llm_response.get("model"),
                    "tokens": llm_response.get("usage", {}),
                    "finish_reason": llm_response.get("finish_reason")
                }
            }
            
        except Exception as e:
            print(f"Error in process_user_message: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError"
            }
    
    async def stream_user_message(
        self,
        session_id: str,
        user_message: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a user message and stream AI response.
        
        Similar to process_user_message but streams the response in real-time.
        
        Args:
            session_id: Chat session UUID
            user_message: User's message content
            
        Yields:
            Dictionary chunks with response content and metadata
        """
        try:
            # Step 1: Get session details
            session = await self.supabase.get_chat_session(session_id)
            if not session:
                yield {
                    "success": False,
                    "error": "Session not found",
                    "error_type": "SessionNotFound"
                }
                return
            
            user_id = session["user_id"]
            memory_profile_id = session.get("memory_profile_id")
            privacy_mode = session.get("privacy_mode", "normal")
            
            # Step 2: Get relevant memories based on privacy mode
            memories = []
            context = ""
            
            if privacy_mode in ["normal", "pause_memories"] and memory_profile_id:
                memories = await self.mem0.search_memories(
                    user_id=user_id,
                    query=user_message,
                    memory_profile_id=memory_profile_id,
                    limit=5
                )
                context = await self.llm.format_memory_context(memories)
            
            # Step 3: Get conversation history
            previous_messages = await self.supabase.get_session_messages(
                session_id=session_id,
                limit=10
            )
            
            conversation_messages = []
            for msg in previous_messages:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            conversation_messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Step 4: Save user message first
            await self.supabase.create_chat_message(
                session_id=session_id,
                role="user",
                content=user_message
            )
            
            # Send metadata first
            yield {
                "success": True,
                "type": "metadata",
                "session_id": session_id,
                "privacy_mode": privacy_mode,
                "memories_used": len(memories)
            }
            
            # Step 5: Stream AI response
            full_response = ""
            async for chunk in self.llm.stream_response(
                messages=conversation_messages,
                context=context
            ):
                if chunk["success"]:
                    content = chunk.get("content", "")
                    full_response += content
                    
                    # Yield content chunk
                    yield {
                        "success": True,
                        "type": "content",
                        "content": content,
                        "done": chunk.get("done", False)
                    }
                else:
                    # Error during streaming
                    yield {
                        "success": False,
                        "type": "error",
                        "error": chunk.get("error"),
                        "error_type": chunk.get("error_type")
                    }
                    return
            
            # Step 6: Save assistant message
            await self.supabase.create_chat_message(
                session_id=session_id,
                role="assistant",
                content=full_response
            )
            
            # Step 7: Extract and save new memories (only in normal mode)
            memories_extracted = False
            if privacy_mode == "normal" and memory_profile_id:
                extraction_result = await self.mem0.extract_memories_from_conversation(
                    messages=[
                        {"role": "user", "content": user_message},
                        {"role": "assistant", "content": full_response}
                    ],
                    user_id=user_id,
                    memory_profile_id=memory_profile_id
                )
                memories_extracted = extraction_result.get("success", False)
            
            # Send final metadata
            yield {
                "success": True,
                "type": "complete",
                "memories_extracted": memories_extracted
            }
            
        except Exception as e:
            print(f"Error in stream_user_message: {e}")
            yield {
                "success": False,
                "type": "error",
                "error": str(e),
                "error_type": "UnexpectedError"
            }
    
    # ========================
    # Session Management
    # ========================
    
    async def create_new_session(
        self,
        user_id: str,
        memory_profile_id: Optional[str] = None,
        privacy_mode: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new chat session.
        
        Args:
            user_id: User UUID
            memory_profile_id: Optional memory profile UUID
            privacy_mode: Privacy mode (normal, incognito, pause_memories)
            
        Returns:
            Created session data
        """
        try:
            # If no profile specified, get default
            if not memory_profile_id and privacy_mode != "incognito":
                default_profile = await self.supabase.get_default_memory_profile(user_id)
                if default_profile:
                    memory_profile_id = default_profile["id"]
            
            # Create session
            session = await self.supabase.create_chat_session(
                user_id=user_id,
                profile_id=memory_profile_id,
                privacy_mode=privacy_mode
            )
            
            return {
                "success": True,
                "session": session
            }
        except Exception as e:
            print(f"Error creating session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """
        Get session details with message count and profile info.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Session details with additional metadata
        """
        try:
            session = await self.supabase.get_chat_session(session_id)
            if not session:
                return {
                    "success": False,
                    "error": "Session not found"
                }
            
            # Get message count
            messages = await self.supabase.get_session_messages(session_id)
            message_count = len(messages)
            
            # Get profile details if available
            profile = None
            if session.get("memory_profile_id"):
                profile = await self.supabase.get_memory_profile(
                    session["memory_profile_id"]
                )
            
            return {
                "success": True,
                "session": session,
                "message_count": message_count,
                "profile": profile
            }
        except Exception as e:
            print(f"Error getting session details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def change_session_privacy_mode(
        self,
        session_id: str,
        new_privacy_mode: str
    ) -> Dict[str, Any]:
        """
        Change the privacy mode of a session.
        
        Args:
            session_id: Session UUID
            new_privacy_mode: New privacy mode (normal, incognito, pause_memories)
            
        Returns:
            Updated session data
        """
        try:
            # Validate privacy mode
            valid_modes = ["normal", "incognito", "pause_memories"]
            if new_privacy_mode not in valid_modes:
                return {
                    "success": False,
                    "error": f"Invalid privacy mode. Must be one of: {valid_modes}"
                }
            
            # Update session
            updated_session = await self.supabase.update_chat_session(
                session_id=session_id,
                data={"privacy_mode": new_privacy_mode}
            )
            
            return {
                "success": True,
                "session": updated_session
            }
        except Exception as e:
            print(f"Error changing privacy mode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """
        Delete a chat session and all its messages.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Success status
        """
        try:
            # Delete session (messages will cascade delete)
            await self.supabase.delete_chat_session(session_id)
            
            return {
                "success": True,
                "message": "Session deleted successfully"
            }
        except Exception as e:
            print(f"Error deleting session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================
    # Helper Methods
    # ========================
    
    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the conversation in a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Conversation statistics and info
        """
        try:
            messages = await self.supabase.get_session_messages(session_id)
            
            user_messages = [m for m in messages if m["role"] == "user"]
            assistant_messages = [m for m in messages if m["role"] == "assistant"]
            
            return {
                "success": True,
                "total_messages": len(messages),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages),
                "first_message_at": messages[0]["created_at"] if messages else None,
                "last_message_at": messages[-1]["created_at"] if messages else None
            }
        except Exception as e:
            print(f"Error getting conversation summary: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def validate_session_access(
        self,
        session_id: str,
        user_id: str
    ) -> bool:
        """
        Validate that a user has access to a session.
        
        Args:
            session_id: Session UUID
            user_id: User UUID
            
        Returns:
            True if user has access, False otherwise
        """
        try:
            session = await self.supabase.get_chat_session(session_id)
            if not session:
                return False
            
            return session["user_id"] == user_id
        except Exception as e:
            print(f"Error validating session access: {e}")
            return False


# Create a singleton instance
chat_service = ChatService()
