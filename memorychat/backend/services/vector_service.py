"""
Vector database service for MemoryChat Multi-Agent application.
Uses ChromaDB for storing and searching memory embeddings.
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

import sys
from pathlib import Path as PathLib

# Add backend directory to path for imports
backend_dir = PathLib(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.settings import settings


class VectorService:
    """Service for managing memory embeddings in ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self._client = None
        self._collection = None
        self._embedding_function = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Get ChromaDB path from settings
            chromadb_path = self._get_chromadb_path()
            
            # Ensure directory exists
            os.makedirs(chromadb_path, exist_ok=True)
            
            # Initialize OpenAI embedding function
            # Note: OpenAI API key should be set in environment or settings
            api_key = os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
            
            if api_key == "your-api-key-here":
                raise ValueError(
                    "OPENAI_API_KEY not configured. Please set it in .env file or environment."
                )
            
            self._embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name="text-embedding-ada-002"
            )
            
            # Initialize persistent ChromaDB client
            self._client = chromadb.PersistentClient(
                path=chromadb_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for memories
            collection_name = "memories"
            try:
                self._collection = self._client.get_collection(
                    name=collection_name,
                    embedding_function=self._embedding_function
                )
            except Exception:
                # Collection doesn't exist, create it
                self._collection = self._client.create_collection(
                    name=collection_name,
                    embedding_function=self._embedding_function,
                    metadata={"description": "Memory embeddings for MemoryChat"}
                )
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChromaDB: {str(e)}") from e
    
    def _get_chromadb_path(self) -> str:
        """Get the absolute path to ChromaDB storage."""
        chromadb_path = settings.CHROMADB_PATH
        
        # Handle relative paths
        if not os.path.isabs(chromadb_path):
            # Get the backend directory (parent of services directory)
            backend_dir = Path(__file__).parent.parent
            chromadb_path = backend_dir / chromadb_path
        
        return str(chromadb_path)
    
    def add_memory_embedding(
        self,
        memory_id: int,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a memory embedding to ChromaDB.
        
        Args:
            memory_id: The memory ID from SQLite database
            content: The memory content to embed
            metadata: Additional metadata (should include profile_id, user_id, etc.)
        
        Returns:
            True if successful
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Ensure memory_id is in metadata for retrieval
            metadata["memory_id"] = str(memory_id)
            
            # Convert all metadata values to strings (ChromaDB requirement)
            metadata_str = {k: str(v) for k, v in metadata.items()}
            
            # Add to collection
            self._collection.add(
                ids=[str(memory_id)],
                documents=[content],
                metadatas=[metadata_str]
            )
            
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to add memory embedding: {str(e)}") from e
    
    def search_similar_memories(
        self,
        query: str,
        profile_id: Optional[int] = None,
        user_id: Optional[int] = None,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar memories using semantic similarity.
        
        Args:
            query: The search query text
            profile_id: Filter by memory profile ID (for isolation)
            user_id: Filter by user ID (for isolation)
            n_results: Number of results to return
            filter_metadata: Additional metadata filters
        
        Returns:
            List of similar memories with scores
        """
        try:
            # Build where clause for filtering
            where = {}
            
            if profile_id is not None:
                where["memory_profile_id"] = str(profile_id)
            
            if user_id is not None:
                where["user_id"] = str(user_id)
            
            # Merge additional filters
            if filter_metadata:
                where.update({k: str(v) for k, v in filter_metadata.items()})
            
            # Perform search
            results = self._collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where if where else None
            )
            
            # Format results
            formatted_results = []
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "memory_id": int(results["ids"][0][i]),
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })
            
            return formatted_results
        except Exception as e:
            raise RuntimeError(f"Failed to search memories: {str(e)}") from e
    
    def update_memory_embedding(
        self,
        memory_id: int,
        new_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory embedding.
        
        Args:
            memory_id: The memory ID
            new_content: Updated content
            metadata: Updated metadata
        
        Returns:
            True if successful
        """
        try:
            # First, delete the old embedding
            self.delete_memory_embedding(memory_id)
            
            # Then add the new one
            return self.add_memory_embedding(memory_id, new_content, metadata)
        except Exception as e:
            raise RuntimeError(f"Failed to update memory embedding: {str(e)}") from e
    
    def delete_memory_embedding(self, memory_id: int) -> bool:
        """
        Delete a memory embedding from ChromaDB.
        
        Args:
            memory_id: The memory ID to delete
        
        Returns:
            True if successful
        """
        try:
            self._collection.delete(ids=[str(memory_id)])
            return True
        except Exception as e:
            # If memory doesn't exist, that's okay
            if "not found" in str(e).lower():
                return True
            raise RuntimeError(f"Failed to delete memory embedding: {str(e)}") from e
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a memory embedding by ID.
        
        Args:
            memory_id: The memory ID
        
        Returns:
            Memory data if found, None otherwise
        """
        try:
            results = self._collection.get(ids=[str(memory_id)])
            
            if results["ids"] and len(results["ids"]) > 0:
                return {
                    "memory_id": int(results["ids"][0]),
                    "content": results["documents"][0] if results["documents"] else "",
                    "metadata": results["metadatas"][0] if results["metadatas"] else {}
                }
            
            return None
        except Exception as e:
            raise RuntimeError(f"Failed to get memory by ID: {str(e)}") from e
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection."""
        try:
            count = self._collection.count()
            return {
                "collection_name": self._collection.name,
                "count": count,
                "embedding_function": "OpenAI text-embedding-ada-002"
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get collection info: {str(e)}") from e

