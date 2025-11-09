"""
Memory Manager Agent for MemoryChat Multi-Agent application.
Extracts and manages memories from conversations.
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from config.agent_config import MEMORY_MANAGER_AGENT
from config.logging_config import get_agent_logger


class MemoryManagerAgent(BaseAgent):
    """
    Agent that extracts and manages memories from conversations.
    
    Analyzes conversation history to extract:
    - Facts about the user
    - Preferences (likes, dislikes, opinions)
    - Events (important dates, occurrences)
    - Relationships (people, places, connections)
    - Other significant information
    """
    
    def __init__(self):
        """Initialize Memory Manager Agent with configuration."""
        config = MEMORY_MANAGER_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            system_prompt=config["system_prompt"]
        )
        
        # Memory type categories
        self.memory_types = ["fact", "preference", "event", "relationship", "other"]
        
        # Prompt templates
        self.extraction_prompt_template = """Analyze the following conversation and extract important information that should be remembered.

Conversation:
User: {user_message}
Assistant: {assistant_response}

Extract memories as a JSON array. Each memory should have:
- "content": Clear, concise statement of what to remember
- "importance_score": Number from 0.0 to 1.0 (higher = more important)
- "memory_type": One of: fact, preference, event, relationship, other
- "tags": Array of relevant keywords

Only extract information that is:
- Explicitly stated or clearly implied
- Relevant for future conversations
- Not trivial or temporary

Return ONLY valid JSON array, no other text.
Example format:
[
  {{
    "content": "User prefers Python over Java",
    "importance_score": 0.7,
    "memory_type": "preference",
    "tags": ["programming", "python", "java"]
  }}
]"""

        self.importance_prompt_template = """Rate the importance of this memory on a scale of 0.0 to 1.0.

Memory: {memory_content}
Type: {memory_type}

Consider:
- 0.0-0.3: Trivial, temporary, or low relevance
- 0.4-0.6: Moderately important, useful for context
- 0.7-0.9: Very important, core preferences or facts
- 1.0: Critical information, fundamental to user identity

Return ONLY a number between 0.0 and 1.0."""

        self.categorization_prompt_template = """Categorize this memory into one of these types:
- fact: Objective information about the user
- preference: Likes, dislikes, opinions
- event: Important dates, occurrences, experiences
- relationship: People, places, connections
- other: Anything that doesn't fit above categories

Memory: {memory_content}

Return ONLY the category name (fact, preference, event, relationship, or other)."""

        self.tag_generation_prompt_template = """Generate 2-5 relevant tags for this memory.

Memory: {memory_content}
Type: {memory_type}

Tags should be:
- Relevant keywords
- Lowercase
- Concise (1-2 words each)
- Useful for searching/categorization

Return ONLY a JSON array of tag strings.
Example: ["programming", "python", "preference"]"""

        self.consolidation_prompt_template = """These memories are similar and may be duplicates or updates:

{memories}

If they represent the same information, consolidate into a single memory.
If they are different but related, keep separate but note the relationship.

Return consolidated memory as JSON with same format:
- "content": Updated/consolidated content
- "importance_score": Updated score (use highest)
- "memory_type": Type (keep if same, use most specific)
- "tags": Combined unique tags
"""

    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute memory extraction from conversation.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str
                - privacy_mode: str ('normal', 'incognito', 'pause_memory')
                - profile_id: int
                - context: dict (may contain 'assistant_response', 'conversation_history')
            context: Optional additional context
            
        Returns:
            Standard output format with extracted memories in data['memories']
        """
        try:
            # Check privacy mode - skip if not NORMAL
            privacy_mode = input_data.get("privacy_mode", "normal").lower()
            if privacy_mode == "incognito":
                self.logger.info("Skipping memory extraction in INCOGNITO mode")
                return {
                    "success": True,
                    "data": {"memories": [], "skipped": True, "reason": "incognito_mode"},
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            if privacy_mode == "pause_memory":
                self.logger.info("Skipping memory extraction in PAUSE_MEMORY mode")
                return {
                    "success": True,
                    "data": {"memories": [], "skipped": True, "reason": "pause_memory_mode"},
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Get conversation data
            user_message = input_data.get("user_message", "")
            assistant_response = input_data.get("context", {}).get("assistant_response", "")
            conversation_history = input_data.get("context", {}).get("conversation_history", [])
            
            if not user_message:
                self.logger.warning("No user message provided for memory extraction")
                return {
                    "success": False,
                    "data": {"memories": []},
                    "error": "No user message provided",
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Extract memories using LLM
            extracted_memories = self._extract_memories(user_message, assistant_response)
            
            if not extracted_memories:
                self.logger.info("No memories extracted from conversation")
                return {
                    "success": True,
                    "data": {"memories": []},
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Process each memory
            processed_memories = []
            for memory in extracted_memories:
                # Enhance memory with additional processing
                enhanced_memory = self._process_memory(memory, conversation_history)
                if enhanced_memory:
                    processed_memories.append(enhanced_memory)
            
            # Check for conflicts/updates with existing memories
            profile_id = input_data.get("profile_id")
            if profile_id and processed_memories:
                processed_memories = self._check_for_conflicts(processed_memories, profile_id)
            
            # Consolidate similar memories
            if len(processed_memories) > 1:
                processed_memories = self._consolidate_similar_memories(processed_memories)
            
            self.logger.info(f"Extracted {len(processed_memories)} memories from conversation")
            
            return {
                "success": True,
                "data": {
                    "memories": processed_memories,
                    "count": len(processed_memories),
                },
                "tokens_used": self._count_tokens(str(processed_memories)),
                "execution_time_ms": 0,  # Will be set by wrapper
            }
            
        except Exception as e:
            self.logger.error(f"Error in memory extraction: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"memories": []},
                "error": f"Memory extraction failed: {str(e)}",
                "tokens_used": 0,
                "execution_time_ms": 0,
            }
    
    def _extract_memories(self, user_message: str, assistant_response: str) -> List[Dict[str, Any]]:
        """
        Extract memories from conversation using LLM.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
            
        Returns:
            List of extracted memory dictionaries
        """
        try:
            # Build prompt
            prompt = self._format_prompt(
                self.extraction_prompt_template,
                user_message=user_message,
                assistant_response=assistant_response
            )
            
            # Build messages
            messages = self._build_messages(
                system_prompt=self.system_prompt,
                user_message=prompt
            )
            
            # Call LLM
            response_text = self._call_llm(messages)
            
            # Parse JSON response
            memories = self._parse_memory_json(response_text)
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Error extracting memories: {str(e)}", exc_info=True)
            return []
    
    def _parse_memory_json(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse JSON response from LLM.
        
        Args:
            response_text: LLM response text
            
        Returns:
            List of memory dictionaries
        """
        try:
            # Try to extract JSON array from response
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Try to find JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON
            memories = json.loads(response_text)
            
            # Validate structure
            if not isinstance(memories, list):
                memories = [memories] if isinstance(memories, dict) else []
            
            # Validate each memory
            valid_memories = []
            for memory in memories:
                if isinstance(memory, dict) and "content" in memory:
                    # Ensure required fields
                    memory.setdefault("importance_score", 0.5)
                    memory.setdefault("memory_type", "other")
                    memory.setdefault("tags", [])
                    
                    # Validate importance score
                    importance = float(memory["importance_score"])
                    memory["importance_score"] = max(0.0, min(1.0, importance))
                    
                    # Validate memory type
                    if memory["memory_type"] not in self.memory_types:
                        memory["memory_type"] = "other"
                    
                    # Ensure tags is a list
                    if not isinstance(memory["tags"], list):
                        memory["tags"] = []
                    
                    valid_memories.append(memory)
            
            return valid_memories
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
            self.logger.debug(f"Response text: {response_text[:200]}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing memory JSON: {str(e)}", exc_info=True)
            return []
    
    def _process_memory(self, memory: Dict[str, Any], conversation_history: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        Process and enhance a memory with additional information.
        
        Args:
            memory: Raw memory dictionary
            conversation_history: Conversation history for context
            
        Returns:
            Enhanced memory dictionary or None if invalid
        """
        try:
            content = memory.get("content", "").strip()
            if not content:
                return None
            
            # Enhance importance score if needed
            importance = memory.get("importance_score", 0.5)
            if importance == 0.5:  # Default, try to calculate better
                importance = self._calculate_importance(memory)
                memory["importance_score"] = importance
            
            # Enhance memory type if needed
            memory_type = memory.get("memory_type", "other")
            if memory_type == "other":
                memory_type = self._categorize_memory(content)
                memory["memory_type"] = memory_type
            
            # Enhance tags if needed
            tags = memory.get("tags", [])
            if not tags or len(tags) < 2:
                tags = self._generate_tags(content, memory_type)
                memory["tags"] = tags
            
            # Extract entities
            entities = self._extract_entities(content)
            if entities:
                memory["entities"] = entities
            
            return memory
            
        except Exception as e:
            self.logger.error(f"Error processing memory: {str(e)}", exc_info=True)
            return memory  # Return original if processing fails
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract entities (people, places, things) from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of extracted entities
        """
        # Simple entity extraction using patterns
        entities = []
        
        # Extract capitalized words (potential names/places)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        entities.extend(capitalized_words)
        
        # Extract quoted strings (often names or specific terms)
        quoted = re.findall(r'"([^"]+)"', text)
        entities.extend(quoted)
        
        # Remove duplicates and common words
        common_words = {"The", "This", "That", "These", "Those", "I", "You", "He", "She", "It", "We", "They"}
        entities = [e for e in set(entities) if e not in common_words]
        
        return entities[:10]  # Limit to 10 entities
    
    def _calculate_importance(self, memory: Dict[str, Any]) -> float:
        """
        Calculate importance score for a memory.
        
        Args:
            memory: Memory dictionary
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        try:
            content = memory.get("content", "").lower()
            memory_type = memory.get("memory_type", "other").lower()
            
            # Base score by type
            type_scores = {
                "preference": 0.7,
                "fact": 0.6,
                "relationship": 0.8,
                "event": 0.6,
                "other": 0.5,
            }
            base_score = type_scores.get(memory_type, 0.5)
            
            # Adjust based on keywords
            important_keywords = ["prefer", "like", "dislike", "love", "hate", "important", "always", "never"]
            if any(keyword in content for keyword in important_keywords):
                base_score = min(1.0, base_score + 0.2)
            
            # Adjust based on length (longer = more detailed = potentially more important)
            if len(content) > 100:
                base_score = min(1.0, base_score + 0.1)
            
            return round(base_score, 2)
            
        except Exception as e:
            self.logger.warning(f"Error calculating importance: {str(e)}")
            return 0.5  # Default score
    
    def _categorize_memory(self, content: str) -> str:
        """
        Categorize memory type.
        
        Args:
            content: Memory content
            
        Returns:
            Memory type string
        """
        content_lower = content.lower()
        
        # Simple keyword-based categorization
        if any(word in content_lower for word in ["prefer", "like", "dislike", "love", "hate", "favorite", "opinion"]):
            return "preference"
        elif any(word in content_lower for word in ["event", "happened", "occurred", "date", "time", "when"]):
            return "event"
        elif any(word in content_lower for word in ["friend", "family", "colleague", "knows", "met", "relationship"]):
            return "relationship"
        elif any(word in content_lower for word in ["is", "has", "works", "lives", "from"]):
            return "fact"
        else:
            return "other"
    
    def _generate_tags(self, content: str, memory_type: str) -> List[str]:
        """
        Generate tags for a memory.
        
        Args:
            content: Memory content
            memory_type: Memory type
            
        Returns:
            List of tag strings
        """
        tags = []
        
        # Add memory type as tag
        tags.append(memory_type)
        
        # Extract keywords (simple approach)
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())
        
        # Common words to exclude
        stop_words = {"that", "this", "with", "from", "have", "been", "will", "would", "could", "should"}
        keywords = [w for w in words if w not in stop_words][:5]
        tags.extend(keywords)
        
        # Remove duplicates and limit
        tags = list(dict.fromkeys(tags))[:5]  # Preserve order, limit to 5
        
        return tags
    
    def _check_for_conflicts(self, new_memories: List[Dict[str, Any]], profile_id: int) -> List[Dict[str, Any]]:
        """
        Check for conflicts with existing memories.
        
        Args:
            new_memories: Newly extracted memories
            profile_id: Memory profile ID
            
        Returns:
            List of memories (may be updated if conflicts found)
        """
        # Note: This would ideally query the database for existing memories
        # For now, we'll do a simple check within the new memories
        # Full implementation would require database access
        
        # Check for duplicates within new memories
        seen_contents = set()
        unique_memories = []
        
        for memory in new_memories:
            content_key = memory.get("content", "").lower().strip()
            if content_key and content_key not in seen_contents:
                seen_contents.add(content_key)
                unique_memories.append(memory)
            else:
                self.logger.debug(f"Skipping duplicate memory: {memory.get('content', '')[:50]}")
        
        return unique_memories
    
    def _consolidate_similar_memories(self, memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Consolidate similar or duplicate memories.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Consolidated list of memories
        """
        if len(memories) <= 1:
            return memories
        
        # Simple consolidation: group by memory type and check similarity
        consolidated = []
        processed_indices = set()
        
        for i, memory1 in enumerate(memories):
            if i in processed_indices:
                continue
            
            similar_group = [memory1]
            
            # Find similar memories
            for j, memory2 in enumerate(memories[i+1:], start=i+1):
                if j in processed_indices:
                    continue
                
                if self._are_similar(memory1, memory2):
                    similar_group.append(memory2)
                    processed_indices.add(j)
            
            # Consolidate group
            if len(similar_group) > 1:
                consolidated_memory = self._merge_memories(similar_group)
                consolidated.append(consolidated_memory)
            else:
                consolidated.append(memory1)
            
            processed_indices.add(i)
        
        return consolidated
    
    def _are_similar(self, memory1: Dict[str, Any], memory2: Dict[str, Any]) -> bool:
        """
        Check if two memories are similar.
        
        Args:
            memory1: First memory
            memory2: Second memory
            
        Returns:
            True if similar, False otherwise
        """
        content1 = memory1.get("content", "").lower()
        content2 = memory2.get("content", "").lower()
        
        # Check if same type
        if memory1.get("memory_type") != memory2.get("memory_type"):
            return False
        
        # Check word overlap (simple similarity)
        words1 = set(re.findall(r'\b\w+\b', content1))
        words2 = set(re.findall(r'\b\w+\b', content2))
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap > 0.5  # 50% word overlap threshold
    
    def _merge_memories(self, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple similar memories into one.
        
        Args:
            memories: List of similar memories
            
        Returns:
            Merged memory dictionary
        """
        if len(memories) == 1:
            return memories[0]
        
        # Use the longest content (most detailed)
        merged = max(memories, key=lambda m: len(m.get("content", "")))
        
        # Use highest importance score
        max_importance = max(m.get("importance_score", 0.5) for m in memories)
        merged["importance_score"] = max_importance
        
        # Combine tags
        all_tags = []
        for memory in memories:
            tags = memory.get("tags", [])
            if isinstance(tags, list):
                all_tags.extend(tags)
        merged["tags"] = list(dict.fromkeys(all_tags))[:10]  # Unique tags, limit to 10
        
        return merged

