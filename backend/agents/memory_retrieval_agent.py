"""
Memory Retrieval Agent for MemoryChat Multi-Agent application.
Finds and ranks relevant memories for current conversation.
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from config.agent_config import MEMORY_RETRIEVAL_AGENT
from config.logging_config import get_agent_logger
from services.vector_service import VectorService
from services.database_service import DatabaseService
from database.database import SessionLocal


class MemoryRetrievalAgent(BaseAgent):
    """
    Agent that finds and ranks relevant memories for current conversation.
    
    Uses multiple search strategies:
    - Semantic search (vector similarity via ChromaDB)
    - Keyword search (SQL LIKE queries)
    - Temporal search (recent memories)
    - Entity search (specific people/places)
    - Hybrid search (combines all strategies)
    """
    
    def __init__(self):
        """Initialize Memory Retrieval Agent with configuration."""
        config = MEMORY_RETRIEVAL_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            system_prompt=config["system_prompt"]
        )
        
        # Initialize services
        self.vector_service = VectorService()
        
        # Ranking weights
        self.ranking_weights = {
            "semantic_similarity": 0.4,  # Highest weight for semantic match
            "recency": 0.2,               # Recent memories are more relevant
            "importance": 0.2,            # Important memories are more relevant
            "mention_count": 0.1,         # Frequently mentioned = more relevant
            "query_match": 0.1,            # Direct keyword matches
        }
        
        # Default number of results
        self.default_n_results = 5
        
        # Prompt templates
        self.intent_understanding_prompt = """Analyze this user query and identify:
1. Main intent (what information is the user seeking?)
2. Key entities (people, places, things mentioned)
3. Time references (recent, last week, etc.)
4. Topic keywords

Query: {query}

Return JSON with:
{{
  "intent": "description of intent",
  "entities": ["entity1", "entity2"],
  "time_reference": "recent|past_week|past_month|any",
  "keywords": ["keyword1", "keyword2"]
}}"""

    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute memory retrieval for current conversation.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str (query)
                - privacy_mode: str
                - profile_id: int
                - context: dict (may contain conversation_history, etc.)
            context: Optional additional context
            
        Returns:
            Standard output format with retrieved memories in data['memories']
        """
        try:
            # Check privacy mode - skip if INCOGNITO
            privacy_mode = input_data.get("privacy_mode", "normal").lower()
            if privacy_mode == "incognito":
                self.logger.info("Skipping memory retrieval in INCOGNITO mode")
                return {
                    "success": True,
                    "data": {
                        "memories": [],
                        "context": "",
                        "skipped": True,
                        "reason": "incognito_mode"
                    },
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # PAUSE_MEMORY mode: Allow retrieval but not storage
            # (Storage is handled by MemoryManagerAgent, retrieval is allowed here)
            if privacy_mode == "pause_memory":
                self.logger.info("Memory retrieval allowed in PAUSE_MEMORY mode (storage disabled)")
            
            # Get query and context
            user_query = input_data.get("user_message", "")
            profile_id = input_data.get("profile_id")
            session_id = input_data.get("session_id")
            
            if not user_query:
                self.logger.warning("No user query provided for memory retrieval")
                return {
                    "success": False,
                    "data": {"memories": [], "context": ""},
                    "error": "No user query provided",
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            if not profile_id:
                self.logger.warning("No profile_id provided for memory retrieval")
                return {
                    "success": False,
                    "data": {"memories": [], "context": ""},
                    "error": "No profile_id provided",
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Understand query intent
            query_intent = self._understand_query_intent(user_query)
            
            # Perform hybrid search
            n_results = context.get("n_results", self.default_n_results) if context else self.default_n_results
            memories = self._hybrid_search(
                query=user_query,
                profile_id=profile_id,
                query_intent=query_intent,
                n_results=n_results
            )
            
            # Rank memories by relevance
            ranked_memories = self._rank_memories(memories, user_query, query_intent)
            
            # Build context for conversation agent
            memory_context = self._build_memory_context(ranked_memories)
            
            self.logger.info(f"Retrieved {len(ranked_memories)} memories for query: {user_query[:50]}")
            
            return {
                "success": True,
                "data": {
                    "memories": ranked_memories,
                    "context": memory_context,
                    "count": len(ranked_memories),
                    "query_intent": query_intent,
                },
                "tokens_used": self._count_tokens(memory_context),
                "execution_time_ms": 0,  # Will be set by wrapper
            }
            
        except Exception as e:
            self.logger.error(f"Error in memory retrieval: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"memories": [], "context": ""},
                "error": f"Memory retrieval failed: {str(e)}",
                "tokens_used": 0,
                "execution_time_ms": 0,
            }
    
    def _understand_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Understand the intent and extract information from user query.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary with intent, entities, time_reference, keywords
        """
        try:
            # Build prompt
            prompt = self._format_prompt(self.intent_understanding_prompt, query=query)
            
            # Build messages
            messages = self._build_messages(
                system_prompt=self.system_prompt,
                user_message=prompt
            )
            
            # Call LLM
            response_text = self._call_llm(messages)
            
            # Parse JSON response
            try:
                # Remove markdown if present
                response_text = re.sub(r'```json\s*', '', response_text)
                response_text = re.sub(r'```\s*', '', response_text).strip()
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(0)
                
                intent_data = json.loads(response_text)
                
                # Ensure all fields present
                intent_data.setdefault("intent", "")
                intent_data.setdefault("entities", [])
                intent_data.setdefault("time_reference", "any")
                intent_data.setdefault("keywords", [])
                
                return intent_data
                
            except json.JSONDecodeError:
                # Fallback: extract keywords and entities manually
                self.logger.warning("Failed to parse intent JSON, using fallback")
                return self._extract_intent_fallback(query)
                
        except Exception as e:
            # Fallback if LLM fails
            self.logger.warning(f"Intent understanding failed: {str(e)}, using fallback")
            return self._extract_intent_fallback(query)
    
    def _extract_intent_fallback(self, query: str) -> Dict[str, Any]:
        """
        Fallback intent extraction without LLM.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary with intent information
        """
        query_lower = query.lower()
        
        # Extract entities (capitalized words)
        entities = re.findall(r'\b[A-Z][a-z]+\b', query)
        
        # Extract keywords (significant words)
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "can", "may", "might", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they"}
        words = re.findall(r'\b[a-z]{4,}\b', query_lower)
        keywords = [w for w in words if w not in stop_words][:10]
        
        # Detect time references
        time_reference = "any"
        if any(word in query_lower for word in ["recent", "recently", "lately", "now", "current"]):
            time_reference = "recent"
        elif any(word in query_lower for word in ["last week", "past week", "week"]):
            time_reference = "past_week"
        elif any(word in query_lower for word in ["last month", "past month", "month"]):
            time_reference = "past_month"
        
        return {
            "intent": query[:100],  # Use query as intent description
            "entities": entities,
            "time_reference": time_reference,
            "keywords": keywords,
        }
    
    def _semantic_search(
        self,
        query: str,
        profile_id: int,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity (vector search).
        
        Args:
            query: Search query text
            profile_id: Memory profile ID
            n_results: Number of results to return
            
        Returns:
            List of memory dictionaries with similarity scores
        """
        try:
            # Get user_id from profile (would need database access)
            # For now, we'll search with profile_id filter
            
            results = self.vector_service.search_similar_memories(
                query=query,
                profile_id=profile_id,
                n_results=n_results
            )
            
            # Format results
            memories = []
            for result in results:
                memory_data = {
                    "id": int(result.get("memory_id", 0)),
                    "content": result.get("content", ""),
                    "similarity_score": result.get("distance", 0.0),  # ChromaDB returns distance
                    "source": "semantic",
                }
                memories.append(memory_data)
            
            self.logger.debug(f"Semantic search found {len(memories)} memories")
            return memories
            
        except Exception as e:
            self.logger.warning(f"Semantic search failed: {str(e)}")
            return []
    
    def _keyword_search(
        self,
        query: str,
        profile_id: int,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories using keyword matching (SQL LIKE queries).
        
        Args:
            query: Search query text
            profile_id: Memory profile ID
            n_results: Number of results to return
            
        Returns:
            List of memory dictionaries
        """
        try:
            # Get database session
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            # Search memories using database service
            memories = db_service.search_memories(
                profile_id=profile_id,
                query_text=query,
                limit=n_results
            )
            
            db.close()
            
            # Format results
            formatted_memories = []
            for memory in memories:
                memory_data = {
                    "id": memory.id,
                    "content": memory.content,
                    "importance_score": memory.importance_score,
                    "memory_type": memory.memory_type,
                    "tags": json.loads(memory.tags) if memory.tags else [],
                    "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    "mentioned_count": memory.mentioned_count,
                    "source": "keyword",
                }
                formatted_memories.append(memory_data)
            
            self.logger.debug(f"Keyword search found {len(formatted_memories)} memories")
            return formatted_memories
            
        except Exception as e:
            self.logger.warning(f"Keyword search failed: {str(e)}")
            return []
    
    def _temporal_search(
        self,
        time_range: str,
        profile_id: int,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories by recency (temporal search).
        
        Args:
            time_range: Time range string ('recent', 'past_week', 'past_month', 'any')
            profile_id: Memory profile ID
            n_results: Number of results to return
            
        Returns:
            List of recent memory dictionaries
        """
        try:
            # Get database session
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            # Get all memories for profile
            all_memories = db_service.get_memories_by_profile(profile_id)
            
            db.close()
            
            # Filter by time range
            now = datetime.now()
            filtered_memories = []
            
            for memory in all_memories:
                if not memory.created_at:
                    continue
                
                memory_time = memory.created_at
                if isinstance(memory_time, str):
                    memory_time = datetime.fromisoformat(memory_time.replace('Z', '+00:00'))
                
                age = now - memory_time.replace(tzinfo=None) if memory_time.tzinfo else now - memory_time
                
                include = False
                if time_range == "recent":
                    include = age <= timedelta(days=7)
                elif time_range == "past_week":
                    include = age <= timedelta(days=7)
                elif time_range == "past_month":
                    include = age <= timedelta(days=30)
                else:  # "any"
                    include = True
                
                if include:
                    memory_data = {
                        "id": memory.id,
                        "content": memory.content,
                        "importance_score": memory.importance_score,
                        "memory_type": memory.memory_type,
                        "tags": json.loads(memory.tags) if memory.tags else [],
                        "created_at": memory.created_at.isoformat() if memory.created_at else None,
                        "mentioned_count": memory.mentioned_count,
                        "age_days": age.days,
                        "source": "temporal",
                    }
                    filtered_memories.append(memory_data)
            
            # Sort by recency (most recent first)
            filtered_memories.sort(key=lambda m: m.get("age_days", 999), reverse=False)
            
            # Return top N
            result = filtered_memories[:n_results]
            
            self.logger.debug(f"Temporal search found {len(result)} memories")
            return result
            
        except Exception as e:
            self.logger.warning(f"Temporal search failed: {str(e)}")
            return []
    
    def _entity_search(
        self,
        entities: List[str],
        profile_id: int,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories by entities (people, places, things).
        
        Args:
            entities: List of entity names to search for
            profile_id: Memory profile ID
            n_results: Number of results to return
            
        Returns:
            List of memory dictionaries containing entities
        """
        if not entities:
            return []
        
        try:
            # Get database session
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            # Get all memories for profile
            all_memories = db_service.get_memories_by_profile(profile_id)
            
            db.close()
            
            # Filter memories that contain entities
            matching_memories = []
            for memory in all_memories:
                content_lower = memory.content.lower()
                tags = json.loads(memory.tags) if memory.tags else []
                tags_lower = [t.lower() for t in tags]
                
                # Check if any entity appears in content or tags
                for entity in entities:
                    entity_lower = entity.lower()
                    if entity_lower in content_lower or entity_lower in tags_lower:
                        memory_data = {
                            "id": memory.id,
                            "content": memory.content,
                            "importance_score": memory.importance_score,
                            "memory_type": memory.memory_type,
                            "tags": tags,
                            "created_at": memory.created_at.isoformat() if memory.created_at else None,
                            "mentioned_count": memory.mentioned_count,
                            "matched_entity": entity,
                            "source": "entity",
                        }
                        matching_memories.append(memory_data)
                        break  # Only add once per memory
            
            # Sort by importance and mention count
            matching_memories.sort(
                key=lambda m: (m.get("importance_score", 0.5), m.get("mentioned_count", 1)),
                reverse=True
            )
            
            # Return top N
            result = matching_memories[:n_results]
            
            self.logger.debug(f"Entity search found {len(result)} memories for entities: {entities}")
            return result
            
        except Exception as e:
            self.logger.warning(f"Entity search failed: {str(e)}")
            return []
    
    def _hybrid_search(
        self,
        query: str,
        profile_id: int,
        query_intent: Optional[Dict[str, Any]] = None,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Combine all search strategies for comprehensive results.
        
        Args:
            query: Search query text
            profile_id: Memory profile ID
            query_intent: Optional query intent dictionary
            n_results: Number of results to return
            
        Returns:
            Combined and deduplicated list of memories
        """
        query_intent = query_intent or {}
        entities = query_intent.get("entities", [])
        time_reference = query_intent.get("time_reference", "any")
        
        # Perform all search strategies
        semantic_results = self._semantic_search(query, profile_id, n_results)
        keyword_results = self._keyword_search(query, profile_id, n_results)
        temporal_results = self._temporal_search(time_reference, profile_id, n_results)
        entity_results = self._entity_search(entities, profile_id, n_results) if entities else []
        
        # Combine results
        all_memories = {}
        
        # Add semantic results (highest priority)
        for memory in semantic_results:
            memory_id = memory.get("id")
            if memory_id:
                all_memories[memory_id] = memory
                all_memories[memory_id]["search_sources"] = ["semantic"]
        
        # Add keyword results
        for memory in keyword_results:
            memory_id = memory.get("id")
            if memory_id:
                if memory_id in all_memories:
                    all_memories[memory_id]["search_sources"].append("keyword")
                else:
                    memory["search_sources"] = ["keyword"]
                    all_memories[memory_id] = memory
        
        # Add temporal results
        for memory in temporal_results:
            memory_id = memory.get("id")
            if memory_id:
                if memory_id in all_memories:
                    all_memories[memory_id]["search_sources"].append("temporal")
                else:
                    memory["search_sources"] = ["temporal"]
                    all_memories[memory_id] = memory
        
        # Add entity results
        for memory in entity_results:
            memory_id = memory.get("id")
            if memory_id:
                if memory_id in all_memories:
                    all_memories[memory_id]["search_sources"].append("entity")
                else:
                    memory["search_sources"] = ["entity"]
                    all_memories[memory_id] = memory
        
        # Convert to list
        combined_memories = list(all_memories.values())
        
        self.logger.info(
            f"Hybrid search: semantic={len(semantic_results)}, keyword={len(keyword_results)}, "
            f"temporal={len(temporal_results)}, entity={len(entity_results)}, "
            f"combined={len(combined_memories)}"
        )
        
        return combined_memories
    
    def _calculate_relevance_score(
        self,
        memory: Dict[str, Any],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate relevance score for a memory.
        
        Args:
            memory: Memory dictionary
            query: User query text
            context: Optional context dictionary
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        weights = self.ranking_weights
        
        # Semantic similarity score (from vector search)
        semantic_score = 1.0 - memory.get("similarity_score", 0.5)  # Convert distance to similarity
        if semantic_score < 0:
            semantic_score = 0.0
        if semantic_score > 1.0:
            semantic_score = 1.0
        
        # Recency score (more recent = higher score)
        created_at_str = memory.get("created_at")
        recency_score = 0.5  # Default
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                if created_at.tzinfo:
                    created_at = created_at.replace(tzinfo=None)
                age_days = (datetime.now() - created_at).days
                # Score decreases with age (max 30 days)
                recency_score = max(0.0, 1.0 - (age_days / 30.0))
            except Exception:
                pass
        
        # Importance score (from memory)
        importance_score = memory.get("importance_score", 0.5)
        
        # Mention count score (normalized)
        mention_count = memory.get("mentioned_count", 1)
        mention_score = min(1.0, mention_count / 10.0)  # Cap at 10 mentions
        
        # Query match score (keyword overlap)
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        content_words = set(re.findall(r'\b\w+\b', memory.get("content", "").lower()))
        if len(query_words) > 0:
            query_match_score = len(query_words & content_words) / len(query_words)
        else:
            query_match_score = 0.0
        
        # Calculate weighted score
        relevance_score = (
            weights["semantic_similarity"] * semantic_score +
            weights["recency"] * recency_score +
            weights["importance"] * importance_score +
            weights["mention_count"] * mention_score +
            weights["query_match"] * query_match_score
        )
        
        return round(relevance_score, 3)
    
    def _rank_memories(
        self,
        memories: List[Dict[str, Any]],
        query: str,
        query_intent: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank memories by relevance score.
        
        Args:
            memories: List of memory dictionaries
            query: User query text
            query_intent: Optional query intent dictionary
            
        Returns:
            Ranked list of memories (most relevant first)
        """
        # Calculate relevance scores
        for memory in memories:
            memory["relevance_score"] = self._calculate_relevance_score(memory, query, query_intent)
        
        # Sort by relevance score (descending)
        ranked = sorted(memories, key=lambda m: m.get("relevance_score", 0.0), reverse=True)
        
        return ranked
    
    def _build_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Build formatted context string from memories for conversation agent.
        
        Args:
            memories: List of ranked memory dictionaries
            
        Returns:
            Formatted context string
        """
        if not memories:
            return ""
        
        # Group memories by type
        grouped = defaultdict(list)
        for memory in memories:
            memory_type = memory.get("memory_type", "other")
            grouped[memory_type].append(memory)
        
        # Build context sections
        context_parts = []
        
        # Add header
        context_parts.append("Relevant Memories:")
        context_parts.append("")
        
        # Add memories by type
        for memory_type in ["preference", "fact", "relationship", "event", "other"]:
            if memory_type in grouped:
                context_parts.append(f"{memory_type.title()}s:")
                for memory in grouped[memory_type][:3]:  # Limit to top 3 per type
                    content = memory.get("content", "")
                    relevance = memory.get("relevance_score", 0.0)
                    created_at = memory.get("created_at", "")
                    
                    # Format date if available
                    date_str = ""
                    if created_at:
                        try:
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = f" (from {dt.strftime('%Y-%m-%d')})"
                        except Exception:
                            pass
                    
                    context_parts.append(f"  - {content}{date_str} [relevance: {relevance:.2f}]")
                context_parts.append("")
        
        # Add summary
        context_parts.append(f"Total: {len(memories)} relevant memories found.")
        
        return "\n".join(context_parts)

