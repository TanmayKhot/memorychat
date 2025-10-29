"""
LLM service.
Handles AI chat completions using OpenAI or other providers.
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import OpenAI, AsyncOpenAI
from openai import OpenAIError, APITimeoutError, APIConnectionError, RateLimitError
from app.core.config import settings


class LLMService:
    """
    Service class for LLM operations.
    Handles chat completions, streaming, context injection, and error handling.
    """
    
    def __init__(self):
        """Initialize LLM client with configuration."""
        # Initialize synchronous client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize async client for async operations
        self.async_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Configuration
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.backoff_factor = 2.0
    
    # ========================
    # Context Building
    # ========================
    
    def _build_system_prompt(self, context: Optional[str] = None) -> str:
        """
        Build system prompt with optional memory context.
        
        Args:
            context: Optional memory context to include
            
        Returns:
            Complete system prompt
        """
        base_prompt = (
            "You are a helpful AI assistant with access to the user's conversation history and memories. "
            "Use the provided context to give personalized and relevant responses. "
            "Be conversational, helpful, and remember details the user has shared."
        )
        
        if context:
            return f"{base_prompt}\n\nUser's Memory Context:\n{context}"
        
        return base_prompt
    
    def _prepare_messages(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Prepare messages with system prompt and context injection.
        
        Args:
            messages: List of chat messages with 'role' and 'content'
            context: Optional memory context to inject
            
        Returns:
            List of messages with system prompt prepended
        """
        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Check if messages already has a system message
        has_system = any(msg.get("role") == "system" for msg in messages)
        
        if has_system:
            # Replace existing system message with our enhanced one
            prepared_messages = [
                {"role": "system", "content": system_prompt} if msg.get("role") == "system"
                else msg
                for msg in messages
            ]
        else:
            # Prepend system message
            prepared_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
        
        return prepared_messages
    
    # ========================
    # Error Handling & Retry
    # ========================
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except (APITimeoutError, APIConnectionError, RateLimitError) as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    # Calculate delay with exponential backoff
                    delay = self.retry_delay * (self.backoff_factor ** attempt)
                    print(f"LLM API error (attempt {attempt + 1}/{self.max_retries}): {e}")
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    print(f"LLM API failed after {self.max_retries} attempts")
                    raise
            except OpenAIError as e:
                # Don't retry on other OpenAI errors (auth, invalid request, etc.)
                print(f"LLM API error: {e}")
                raise
            except Exception as e:
                # Don't retry on unknown errors
                print(f"Unexpected error in LLM service: {e}")
                raise
        
        # If we get here, all retries failed
        raise last_exception
    
    # ========================
    # Response Generation
    # ========================
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of chat messages with 'role' and 'content'
            context: Optional memory context to inject
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            Dictionary with response content and metadata
        """
        try:
            # Prepare messages with context
            prepared_messages = self._prepare_messages(messages, context)
            
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # Define the API call as an async function
            async def make_api_call():
                response = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=prepared_messages,
                    temperature=temp,
                    max_tokens=tokens
                )
                return response
            
            # Execute with retry logic
            response = await self._retry_with_backoff(make_api_call)
            
            # Extract response data
            choice = response.choices[0]
            content = choice.message.content
            
            return {
                "success": True,
                "content": content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": choice.finish_reason
            }
            
        except OpenAIError as e:
            print(f"OpenAI API error in generate_response: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        except Exception as e:
            print(f"Unexpected error in generate_response: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError"
            }
    
    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Generate a streaming chat completion response.
        
        Args:
            messages: List of chat messages with 'role' and 'content'
            context: Optional memory context to inject
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Yields:
            Dictionary chunks with content and metadata
        """
        try:
            # Prepare messages with context
            prepared_messages = self._prepare_messages(messages, context)
            
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens
            
            # Define the streaming API call
            async def make_streaming_call():
                stream = await self.async_client.chat.completions.create(
                    model=self.model,
                    messages=prepared_messages,
                    temperature=temp,
                    max_tokens=tokens,
                    stream=True
                )
                return stream
            
            # Execute with retry logic
            stream = await self._retry_with_backoff(make_streaming_call)
            
            # Stream the response
            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    
                    # Check if there's content in the delta
                    if choice.delta.content:
                        yield {
                            "success": True,
                            "content": choice.delta.content,
                            "finish_reason": choice.finish_reason
                        }
                    
                    # If stream is finished, send final chunk
                    if choice.finish_reason:
                        yield {
                            "success": True,
                            "content": "",
                            "finish_reason": choice.finish_reason,
                            "done": True
                        }
            
        except OpenAIError as e:
            print(f"OpenAI API error in stream_response: {e}")
            yield {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        except Exception as e:
            print(f"Unexpected error in stream_response: {e}")
            yield {
                "success": False,
                "error": str(e),
                "error_type": "UnexpectedError"
            }
    
    # ========================
    # Helper Methods
    # ========================
    
    async def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        This is a rough estimate; for accurate counting, use tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token
        return len(text) // 4
    
    async def format_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """
        Format memory entries into context string.
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Formatted context string
        """
        if not memories:
            return ""
        
        context_parts = []
        for i, memory in enumerate(memories, 1):
            memory_text = memory.get("memory", "")
            if memory_text:
                context_parts.append(f"{i}. {memory_text}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    async def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """
        Validate message format.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            True if valid, False otherwise
        """
        if not messages:
            return False
        
        valid_roles = {"system", "user", "assistant"}
        
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if "role" not in msg or "content" not in msg:
                return False
            if msg["role"] not in valid_roles:
                return False
            if not isinstance(msg["content"], str):
                return False
        
        return True


# Create a singleton instance
llm_service = LLMService()
