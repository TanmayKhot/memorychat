"""
Memory endpoints for MemoryChat Multi-Agent API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database.database import get_db
from services.database_service import DatabaseService
from services.vector_service import VectorService
from agents.memory_retrieval_agent import MemoryRetrievalAgent
from models.api_models import (
    MemoryResponse,
    MemoryType
)

router = APIRouter()


@router.get("/profiles/{profile_id}/memories", response_model=List[MemoryResponse])
async def get_profile_memories(
    profile_id: int,
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    sort_by: str = Query("importance", description="Sort by: importance or recency"),
    db: Session = Depends(get_db)
):
    """
    Get all memories for a profile with filtering and sorting.
    
    Args:
        profile_id: Profile ID
        memory_type: Filter by memory type
        tags: Filter by tags (comma-separated)
        sort_by: Sort by importance or recency
        
    Returns:
        List[MemoryResponse]: List of memories
    """
    db_service = DatabaseService(db)
    
    # Verify profile exists
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        memories = db_service.get_memories_by_profile(profile_id)
        
        # Filter by memory type
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        # Filter by tags
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            filtered_memories = []
            for mem in memories:
                if mem.tags:
                    try:
                        mem_tags = json.loads(mem.tags) if isinstance(mem.tags, str) else mem.tags
                        if any(tag in mem_tags for tag in tag_list):
                            filtered_memories.append(mem)
                    except:
                        pass
            memories = filtered_memories
        
        # Sort
        if sort_by == "recency":
            memories = sorted(memories, key=lambda m: m.created_at, reverse=True)
        else:  # importance (default)
            memories = sorted(memories, key=lambda m: m.importance_score or 0.0, reverse=True)
        
        # Convert to response models
        result = []
        for mem in memories:
            tags_list = None
            if mem.tags:
                try:
                    tags_list = json.loads(mem.tags) if isinstance(mem.tags, str) else mem.tags
                except:
                    tags_list = []
            
            result.append(MemoryResponse(
                id=mem.id,
                content=mem.content,
                importance_score=mem.importance_score or 0.0,
                memory_type=MemoryType(mem.memory_type) if mem.memory_type else None,
                tags=tags_list,
                created_at=mem.created_at
            ))
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memories: {str(e)}"
        )


@router.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific memory details.
    
    Args:
        memory_id: Memory ID
        
    Returns:
        MemoryResponse: Memory data
    """
    db_service = DatabaseService(db)
    
    from database.models import Memory
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    try:
        tags_list = None
        if memory.tags:
            try:
                tags_list = json.loads(memory.tags) if isinstance(memory.tags, str) else memory.tags
            except:
                tags_list = []
        
        return MemoryResponse(
            id=memory.id,
            content=memory.content,
            importance_score=memory.importance_score or 0.0,
            memory_type=MemoryType(memory.memory_type) if memory.memory_type else None,
            tags=tags_list,
            created_at=memory.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get memory: {str(e)}"
        )


@router.put("/memories/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: int,
    content: Optional[str] = Query(None, description="New memory content"),
    importance_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="New importance score"),
    memory_type: Optional[str] = Query(None, description="New memory type"),
    tags: Optional[str] = Query(None, description="New tags (comma-separated)"),
    db: Session = Depends(get_db)
):
    """
    Update memory content or metadata.
    
    Args:
        memory_id: Memory ID
        content: New content
        importance_score: New importance score
        memory_type: New memory type
        tags: New tags (comma-separated)
        
    Returns:
        MemoryResponse: Updated memory
    """
    db_service = DatabaseService(db)
    
    from database.models import Memory
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    try:
        update_data = {}
        if content is not None:
            update_data["content"] = content
        if importance_score is not None:
            update_data["importance_score"] = importance_score
        if memory_type is not None:
            update_data["memory_type"] = memory_type
        if tags is not None:
            tag_list = [t.strip() for t in tags.split(",")]
            update_data["tags"] = tag_list
        
        updated_memory = db_service.update_memory(memory_id, **update_data)
        
        if not updated_memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # Update ChromaDB if content changed
        if content is not None:
            try:
                vector_service = VectorService()
                vector_service.update_memory_embedding(memory_id, content)
            except Exception as e:
                # Log but don't fail if ChromaDB update fails
                from config.logging_config import app_logger
                app_logger.warning(f"Failed to update ChromaDB embedding: {str(e)}")
        
        tags_list = None
        if updated_memory.tags:
            try:
                tags_list = json.loads(updated_memory.tags) if isinstance(updated_memory.tags, str) else updated_memory.tags
            except:
                tags_list = []
        
        return MemoryResponse(
            id=updated_memory.id,
            content=updated_memory.content,
            importance_score=updated_memory.importance_score or 0.0,
            memory_type=MemoryType(updated_memory.memory_type) if updated_memory.memory_type else None,
            tags=tags_list,
            created_at=updated_memory.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update memory: {str(e)}"
        )


@router.delete("/memories/{memory_id}", status_code=status.HTTP_200_OK)
async def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific memory.
    Removes from ChromaDB too.
    
    Args:
        memory_id: Memory ID
        
    Returns:
        dict: Success message
    """
    db_service = DatabaseService(db)
    
    from database.models import Memory
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    
    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Memory with ID {memory_id} not found"
        )
    
    try:
        # Delete from ChromaDB first
        try:
            vector_service = VectorService()
            vector_service.delete_memory_embedding(memory_id)
        except Exception as e:
            # Log but continue if ChromaDB deletion fails
            from config.logging_config import app_logger
            app_logger.warning(f"Failed to delete ChromaDB embedding: {str(e)}")
        
        # Delete from database
        success = db_service.delete_memory(memory_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        return {"message": f"Memory {memory_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete memory: {str(e)}"
        )


@router.post("/memories/search", response_model=List[MemoryResponse])
async def search_memories(
    profile_id: int = Query(..., description="Profile ID"),
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search memories by text query using MemoryRetrievalAgent.
    
    Args:
        profile_id: Profile ID
        query: Search query text
        limit: Maximum number of results
        
    Returns:
        List[MemoryResponse]: Ranked search results
    """
    db_service = DatabaseService(db)
    
    # Verify profile exists
    profile = db_service.get_memory_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        # Use MemoryRetrievalAgent for semantic search
        retrieval_agent = MemoryRetrievalAgent()
        agent_input = {
            "session_id": None,
            "user_message": query,
            "privacy_mode": "normal",
            "profile_id": profile_id,
            "context": {}
        }
        
        result = retrieval_agent.execute(agent_input)
        
        if not result.get("success"):
            # Fallback to simple text search
            memories = db_service.search_memories(profile_id, query, limit=limit)
        else:
            # Extract memories from result
            memories_data = result.get("data", {}).get("memories", [])
            memory_ids = [m.get("id") for m in memories_data if m.get("id")]
            
            # Get full memory objects
            from database.models import Memory
            memories = []
            for mem_id in memory_ids[:limit]:
                mem = db.query(Memory).filter(Memory.id == mem_id).first()
                if mem and mem.memory_profile_id == profile_id:
                    memories.append(mem)
        
        # Convert to response models
        result_list = []
        for mem in memories[:limit]:
            tags_list = None
            if mem.tags:
                try:
                    tags_list = json.loads(mem.tags) if isinstance(mem.tags, str) else mem.tags
                except:
                    tags_list = []
            
            result_list.append(MemoryResponse(
                id=mem.id,
                content=mem.content,
                importance_score=mem.importance_score or 0.0,
                memory_type=MemoryType(mem.memory_type) if mem.memory_type else None,
                tags=tags_list,
                created_at=mem.created_at
            ))
        
        return result_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search memories: {str(e)}"
        )

