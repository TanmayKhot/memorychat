"""
Analytics endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from services.database_service import DatabaseService
from agents.conversation_analyst_agent import ConversationAnalystAgent

router = APIRouter()


@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get conversation analytics for a session.
    Returns sentiment, topics, and insights.
    
    Args:
        session_id: Session ID
        
    Returns:
        dict: Analytics data including sentiment, topics, insights
    """
    db_service = DatabaseService(db)
    
    session = db_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {session_id} not found"
        )
    
    try:
        # Get all messages
        messages = db_service.get_messages_by_session(session_id)
        
        if not messages:
            return {
                "session_id": session_id,
                "sentiment": "neutral",
                "topics": [],
                "insights": {},
                "message_count": 0
            }
        
        # Prepare conversation history for analysis
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Use ConversationAnalystAgent
        analyst = ConversationAnalystAgent()
        agent_input = {
            "session_id": session_id,
            "user_message": "",  # Not needed for analysis
            "privacy_mode": session.privacy_mode,
            "profile_id": session.memory_profile_id,
            "context": {
                "conversation_history": conversation_history
            }
        }
        
        result = analyst.execute(agent_input)
        
        if result.get("success"):
            analysis_data = result.get("data", {})
            return {
                "session_id": session_id,
                "sentiment": analysis_data.get("sentiment", "neutral"),
                "topics": analysis_data.get("topics", []),
                "insights": analysis_data.get("insights", {}),
                "recommendations": analysis_data.get("recommendations", []),
                "message_count": len(messages),
                "analysis_metadata": {
                    "tokens_used": result.get("tokens_used", 0),
                    "execution_time_ms": result.get("execution_time_ms", 0)
                }
            }
        else:
            # Return basic analytics if analysis fails
            return {
                "session_id": session_id,
                "sentiment": "unknown",
                "topics": [],
                "insights": {},
                "message_count": len(messages),
                "error": result.get("error", "Analysis failed")
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session analytics: {str(e)}"
        )


@router.get("/profiles/{profile_id}/analytics")
async def get_profile_analytics(
    profile_id: int,
    db: Session = Depends(get_db)
):
    """
    Get profile usage analytics.
    Returns conversation count, memory count, and topics.
    
    Args:
        profile_id: Profile ID
        
    Returns:
        dict: Profile analytics data
    """
    db_service = DatabaseService(db)
    
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        # Get all sessions using this profile
        from database.models import ChatSession
        sessions = db.query(ChatSession).filter(
            ChatSession.memory_profile_id == profile_id
        ).all()
        
        # Count conversations and messages
        conversation_count = len(sessions)
        total_messages = 0
        for session in sessions:
            messages = db_service.get_messages_by_session(session.id)
            total_messages += len(messages)
        
        # Get memories
        memories = db_service.get_memories_by_profile(profile_id)
        memory_count = len(memories)
        
        # Extract topics from memories (simple extraction)
        topics = set()
        for mem in memories:
            if mem.memory_type:
                topics.add(mem.memory_type)
            if mem.tags:
                try:
                    import json
                    tags = json.loads(mem.tags) if isinstance(mem.tags, str) else mem.tags
                    if isinstance(tags, list):
                        topics.update(tags)
                except:
                    pass
        
        return {
            "profile_id": profile_id,
            "profile_name": profile.name,
            "conversation_count": conversation_count,
            "total_messages": total_messages,
            "memory_count": memory_count,
            "topics": list(topics),
            "average_messages_per_conversation": (
                total_messages / conversation_count if conversation_count > 0 else 0
            )
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile analytics: {str(e)}"
        )

