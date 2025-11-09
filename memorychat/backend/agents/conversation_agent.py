"""
Conversation Agent for MemoryChat Multi-Agent application.
Main conversation agent that generates natural, contextually appropriate responses.
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
from config.agent_config import CONVERSATION_AGENT
from config.logging_config import get_agent_logger
from services.database_service import DatabaseService
from database.database import SessionLocal


class ConversationAgent(BaseAgent):
    """
    Main conversation agent that generates natural, contextually appropriate responses.
    
    Responsibilities:
    - Generate contextually relevant responses
    - Apply personality traits from memory profile
    - Integrate memory context into responses
    - Maintain conversation flow
    - Ensure response quality and safety
    """
    
    def __init__(self):
        """Initialize Conversation Agent with configuration."""
        config = CONVERSATION_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            system_prompt=config["system_prompt"]
        )
        
        # Maximum conversation history length (in messages)
        self.max_history_length = 20
        
        # Maximum memory context length (in characters)
        self.max_memory_context_length = 2000
        
        # Quality check thresholds
        self.min_response_length = 10
        self.max_response_length = 2000
        
        # Personality trait mappings
        self.tone_mappings = {
            "professional": "Use a professional, formal tone. Be precise and clear.",
            "casual": "Use a casual, relaxed tone. Be friendly and conversational.",
            "friendly": "Use a warm, friendly tone. Be approachable and helpful.",
            "formal": "Use a formal, respectful tone. Be courteous and proper.",
        }
        
        self.verbosity_mappings = {
            "concise": "Be brief and to the point. Avoid unnecessary details.",
            "detailed": "Provide comprehensive, detailed responses with examples.",
            "balanced": "Provide balanced responses with appropriate detail level.",
        }
    
    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute conversation generation.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str
                - privacy_mode: str
                - profile_id: int
                - context: dict (may contain 'memory_context', 'conversation_history', etc.)
            context: Optional additional context
            
        Returns:
            Standard output format with generated response
        """
        try:
            # Get input data
            user_message = input_data.get("user_message", "")
            profile_id = input_data.get("profile_id")
            session_id = input_data.get("session_id")
            
            if not user_message:
                self.logger.warning("No user message provided for conversation generation")
                return {
                    "success": False,
                    "data": {"response": ""},
                    "error": "No user message provided",
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Get memory context from input context
            memory_context = input_data.get("context", {}).get("memory_context", "")
            conversation_history = input_data.get("context", {}).get("conversation_history", [])
            
            # Get profile settings
            profile_settings = self._get_profile_settings(profile_id) if profile_id else {}
            
            # Build system prompt with personality
            system_prompt = self._build_system_prompt(profile_settings)
            
            # Build memory context string
            memory_context_str = self._build_memory_context(memory_context)
            
            # Build conversation history
            conversation_history_str = self._build_conversation_history(conversation_history)
            
            # Assemble full prompt
            full_prompt = self._assemble_full_prompt(
                system_prompt=system_prompt,
                memory_context=memory_context_str,
                conversation_history=conversation_history_str,
                user_message=user_message
            )
            
            # Generate response
            messages = self._build_messages(
                system_prompt=system_prompt,
                user_message=full_prompt
            )
            
            response = self._call_llm(messages)
            
            # Quality checks
            quality_result = self._check_response_quality(
                response=response,
                user_message=user_message,
                memory_context=memory_context_str
            )
            
            if not quality_result.get("passed", True):
                self.logger.warning(f"Response quality check failed: {quality_result.get('reason', 'unknown')}")
                # Retry once with adjusted prompt
                if quality_result.get("retry", False):
                    response = self._retry_generation(messages, quality_result)
                    quality_result = self._check_response_quality(
                        response=response,
                        user_message=user_message,
                        memory_context=memory_context_str
                    )
            
            # Handle edge cases
            response = self._handle_edge_cases(
                response=response,
                memory_context=memory_context_str,
                conversation_history=conversation_history
            )
            
            self.logger.info(f"Generated response for session {session_id}: {len(response)} chars")
            
            return {
                "success": True,
                "data": {
                    "response": response,
                    "quality_score": quality_result.get("score", 1.0),
                    "quality_checks": quality_result,
                    "personality_applied": bool(profile_settings),
                },
                "tokens_used": self._count_tokens(response),
                "execution_time_ms": 0,  # Will be set by wrapper
            }
            
        except Exception as e:
            self.logger.error(f"Error in conversation generation: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"response": ""},
                "error": f"Conversation generation failed: {str(e)}",
                "tokens_used": 0,
                "execution_time_ms": 0,
            }
    
    def _get_profile_settings(self, profile_id: int) -> Dict[str, Any]:
        """
        Get profile settings including personality traits.
        
        Args:
            profile_id: Memory profile ID
            
        Returns:
            Dictionary with profile settings
        """
        try:
            db = SessionLocal()
            db_service = DatabaseService(db)
            
            profile = db_service.get_memory_profile_by_id(profile_id)
            db.close()
            
            if not profile:
                return {}
            
            settings = {
                "personality_traits": json.loads(profile.personality_traits) if profile.personality_traits else {},
                "system_prompt": profile.system_prompt,
                "name": profile.name,
                "description": profile.description,
            }
            
            return settings
            
        except Exception as e:
            self.logger.warning(f"Failed to get profile settings: {str(e)}")
            return {}
    
    def _build_system_prompt(self, profile_settings: Dict[str, Any]) -> str:
        """
        Build system prompt with personality traits.
        
        Args:
            profile_settings: Profile settings dictionary
            
        Returns:
            System prompt string
        """
        base_prompt = self.system_prompt
        
        # Apply custom system prompt if available
        custom_prompt = profile_settings.get("system_prompt")
        if custom_prompt:
            base_prompt = custom_prompt
        
        # Apply personality traits
        personality_traits = profile_settings.get("personality_traits", {})
        
        personality_parts = []
        
        # Tone
        tone = personality_traits.get("tone", "balanced")
        if tone in self.tone_mappings:
            personality_parts.append(self.tone_mappings[tone])
        
        # Verbosity
        verbosity = personality_traits.get("verbosity", "balanced")
        if verbosity in self.verbosity_mappings:
            personality_parts.append(self.verbosity_mappings[verbosity])
        
        # Additional traits
        if personality_traits.get("humor", False):
            personality_parts.append("Use appropriate humor when suitable.")
        
        if personality_traits.get("empathy", False):
            personality_parts.append("Show empathy and understanding.")
        
        # Combine
        if personality_parts:
            personality_instruction = " ".join(personality_parts)
            full_prompt = f"{base_prompt}\n\nPersonality guidelines:\n{personality_instruction}"
        else:
            full_prompt = base_prompt
        
        return full_prompt
    
    def _build_memory_context(self, memory_context: Any) -> str:
        """
        Build memory context string for prompt.
        
        Args:
            memory_context: Memory context (string or list)
            
        Returns:
            Formatted memory context string
        """
        if not memory_context:
            return ""
        
        # If already a string, return it (may be pre-formatted)
        if isinstance(memory_context, str):
            # Truncate if too long
            if len(memory_context) > self.max_memory_context_length:
                memory_context = memory_context[:self.max_memory_context_length] + "..."
            return memory_context
        
        # If list of memories, format them
        if isinstance(memory_context, list):
            if len(memory_context) == 0:
                return ""
            
            context_parts = ["Relevant memories:"]
            for memory in memory_context[:10]:  # Limit to 10 memories
                if isinstance(memory, dict):
                    content = memory.get("content", "")
                    memory_type = memory.get("memory_type", "")
                    if content:
                        context_parts.append(f"- {content} ({memory_type})")
                elif isinstance(memory, str):
                    context_parts.append(f"- {memory}")
            
            context_str = "\n".join(context_parts)
            
            # Truncate if too long
            if len(context_str) > self.max_memory_context_length:
                context_str = context_str[:self.max_memory_context_length] + "..."
            
            return context_str
        
        return str(memory_context)
    
    def _build_conversation_history(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Build conversation history string for prompt.
        
        Args:
            conversation_history: List of message dictionaries
            
        Returns:
            Formatted conversation history string
        """
        if not conversation_history:
            return ""
        
        # Limit history length
        if len(conversation_history) > self.max_history_length:
            conversation_history = conversation_history[-self.max_history_length:]
        
        history_parts = []
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                history_parts.append(f"{role.capitalize()}: {content}")
        
        if history_parts:
            return "\n".join(history_parts)
        
        return ""
    
    def _assemble_full_prompt(
        self,
        system_prompt: str,
        memory_context: str,
        conversation_history: str,
        user_message: str
    ) -> str:
        """
        Assemble full prompt from components.
        
        Args:
            system_prompt: System prompt
            memory_context: Memory context string
            conversation_history: Conversation history string
            user_message: Current user message
            
        Returns:
            Full assembled prompt
        """
        prompt_parts = []
        
        # Add memory context if available
        if memory_context:
            prompt_parts.append(memory_context)
            prompt_parts.append("")
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Previous conversation:")
            prompt_parts.append(conversation_history)
            prompt_parts.append("")
        
        # Add current user message
        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("")
        prompt_parts.append("Assistant:")
        
        return "\n".join(prompt_parts)
    
    def _check_response_quality(
        self,
        response: str,
        user_message: str,
        memory_context: str
    ) -> Dict[str, Any]:
        """
        Check response quality and safety.
        
        Args:
            response: Generated response
            user_message: Original user message
            memory_context: Memory context used
            
        Returns:
            Dictionary with quality check results
        """
        checks = {
            "passed": True,
            "score": 1.0,
            "reasons": [],
            "retry": False,
        }
        
        # Check response length
        if len(response) < self.min_response_length:
            checks["passed"] = False
            checks["reasons"].append("Response too short")
            checks["retry"] = True
        
        if len(response) > self.max_response_length:
            checks["passed"] = False
            checks["reasons"].append("Response too long")
            checks["retry"] = True
        
        # Check relevance (simple keyword overlap)
        user_words = set(re.findall(r'\b\w+\b', user_message.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        if len(user_words) > 0:
            overlap = len(user_words & response_words) / len(user_words)
            if overlap < 0.1:  # Less than 10% overlap
                checks["passed"] = False
                checks["reasons"].append("Low relevance to user message")
                checks["retry"] = True
            checks["score"] *= overlap
        
        # Check safety (basic checks)
        unsafe_patterns = [
            r'\b(kill|murder|suicide|harm)\b',
            r'\b(hack|exploit|attack)\b',
        ]
        for pattern in unsafe_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                checks["passed"] = False
                checks["reasons"].append("Potentially unsafe content detected")
                checks["score"] *= 0.5
        
        # Check memory usage (if memory context provided)
        if memory_context and len(memory_context) > 0:
            memory_words = set(re.findall(r'\b\w+\b', memory_context.lower()))
            if len(memory_words) > 0:
                memory_overlap = len(memory_words & response_words) / len(memory_words)
                if memory_overlap < 0.05:  # Less than 5% memory usage
                    checks["reasons"].append("Low memory context usage")
                    checks["score"] *= 0.9  # Minor penalty
        
        return checks
    
    def _retry_generation(
        self,
        messages: List[Any],
        quality_result: Dict[str, Any]
    ) -> str:
        """
        Retry response generation with adjusted prompt.
        
        Args:
            messages: Original messages
            quality_result: Quality check results
            
        Returns:
            New generated response
        """
        # Add instruction to improve quality
        retry_instruction = "Please provide a more relevant and appropriate response."
        
        # Modify user message
        if messages and len(messages) > 0:
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                last_message.content += f"\n\n{retry_instruction}"
        
        # Retry with slightly lower temperature for more focused response
        original_temp = self.temperature
        self.temperature = max(0.3, original_temp - 0.2)
        
        try:
            response = self._call_llm(messages)
        finally:
            self.temperature = original_temp
        
        return response
    
    def _handle_edge_cases(
        self,
        response: str,
        memory_context: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Handle edge cases in response generation.
        
        Args:
            response: Generated response
            memory_context: Memory context used
            conversation_history: Conversation history
            
        Returns:
            Adjusted response
        """
        # Handle empty memory context (first conversation)
        if not memory_context or len(memory_context.strip()) == 0:
            # Response should be fine, but ensure it doesn't reference memories
            if "memory" in response.lower() and "remember" in response.lower():
                # Remove memory references if no context
                response = re.sub(
                    r'\b(?:I remember|based on.*memory|from.*memory)\b[^.]*\.',
                    '',
                    response,
                    flags=re.IGNORECASE
                )
        
        # Handle very long conversation history
        if len(conversation_history) > self.max_history_length:
            # Response should acknowledge long conversation
            if "earlier" not in response.lower() and "previous" not in response.lower():
                # Add acknowledgment if needed
                pass  # Usually handled by context
        
        # Handle conflicting memories (if detected)
        # This would require more sophisticated analysis
        # For now, ensure response doesn't contradict itself
        
        return response
    
    def _check_response_relevance(self, response: str, user_message: str) -> bool:
        """
        Check if response is relevant to user message.
        
        Args:
            response: Generated response
            user_message: Original user message
            
        Returns:
            True if relevant, False otherwise
        """
        # Simple keyword overlap check
        user_words = set(re.findall(r'\b\w+\b', user_message.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        if len(user_words) == 0:
            return True
        
        overlap = len(user_words & response_words) / len(user_words)
        return overlap >= 0.1  # At least 10% overlap
    
    def _check_response_safety(self, response: str) -> bool:
        """
        Check if response is safe (basic safety checks).
        
        Args:
            response: Generated response
            
        Returns:
            True if safe, False otherwise
        """
        unsafe_patterns = [
            r'\b(kill|murder|suicide|harm)\b',
            r'\b(hack|exploit|attack)\b',
        ]
        
        for pattern in unsafe_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return False
        
        return True
    
    def _check_memory_usage(self, response: str, provided_memories: str) -> bool:
        """
        Check if response uses provided memories appropriately.
        
        Args:
            response: Generated response
            provided_memories: Memory context string
            
        Returns:
            True if memory usage is appropriate
        """
        if not provided_memories or len(provided_memories.strip()) == 0:
            return True  # No memories to use
        
        # Check for memory-related keywords in response
        memory_keywords = ["remember", "mentioned", "prefer", "like", "know"]
        has_memory_keywords = any(keyword in response.lower() for keyword in memory_keywords)
        
        # If memories provided but response doesn't reference them, it's still OK
        # (response might be general)
        return True

