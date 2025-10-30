"""
Chat endpoints.
Handles chat message processing and streaming.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user, verify_user_access
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
    ErrorResponse
)
from app.services.chat_service import chat_service
from app.services.supabase_service import supabase_service
import json


# Create router
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{session_id}", response_model=ChatResponse)
async def send_message(
    session_id: str,
    chat_request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ChatResponse:
    """
    Send a message to a chat session and get AI response.
    
    This endpoint:
    1. Validates session access
    2. Retrieves relevant memories based on privacy mode
    3. Generates AI response with context
    4. Saves both user and assistant messages
    5. Extracts new memories (if privacy mode allows)
    
    Args:
        session_id: Chat session UUID
        chat_request: Request with user message
        current_user: Current authenticated user (from dependency)
        
    Returns:
        ChatResponse with AI response and metadata
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
        HTTPException: 500 if processing fails
    """
    try:
        # Verify session exists and user has access
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Process the message through chat service
        result = await chat_service.process_user_message(
            session_id=session_id,
            user_message=chat_request.message
        )
        
        # Check if processing was successful
        if not result.get("success"):
            error_type = result.get("error_type", "ProcessingError")
            error_msg = result.get("error", "Failed to process message")
            
            # Map error types to HTTP status codes
            if error_type == "SessionNotFound":
                status_code = status.HTTP_404_NOT_FOUND
            elif error_type == "LLMError":
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            raise HTTPException(
                status_code=status_code,
                detail=error_msg
            )
        
        # Return successful response
        return ChatResponse(
            success=True,
            content=result["content"],
            session_id=result["session_id"],
            privacy_mode=result["privacy_mode"],
            memories_used=result["memories_used"],
            memories_extracted=result["memories_extracted"],
            metadata=result.get("metadata")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in send_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.post("/{session_id}/stream")
async def stream_message(
    session_id: str,
    chat_request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a message to a chat session and stream AI response.
    
    This endpoint streams the AI response in real-time using Server-Sent Events (SSE).
    The response is streamed in chunks as the AI generates it, providing a better
    user experience for long responses.
    
    Stream format:
    - Each line is a JSON object with type field
    - Types: "metadata", "content", "complete", "error"
    - Content chunks contain partial response text
    - Complete message signals end of stream
    
    Args:
        session_id: Chat session UUID
        chat_request: Request with user message
        current_user: Current authenticated user (from dependency)
        
    Returns:
        StreamingResponse with text/event-stream content type
        
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
    """
    try:
        # Verify session exists and user has access
        session = await supabase_service.get_chat_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify user has access to this session
        verify_user_access(current_user, session["user_id"])
        
        # Define async generator for streaming
        async def generate_stream():
            """Generate SSE stream from chat service."""
            try:
                async for chunk in chat_service.stream_user_message(
                    session_id=session_id,
                    user_message=chat_request.message
                ):
                    # Format as SSE
                    chunk_json = json.dumps(chunk)
                    yield f"data: {chunk_json}\n\n"
                    
                    # If there's an error, stop streaming
                    if not chunk.get("success", True):
                        break
                
                # Send stream end marker
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"Error during streaming: {e}")
                error_chunk = {
                    "success": False,
                    "type": "error",
                    "error": str(e),
                    "error_type": "StreamingError"
                }
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable buffering for nginx
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in stream_message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start message stream"
        )
