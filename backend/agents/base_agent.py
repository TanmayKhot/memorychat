"""
Base agent class for MemoryChat Multi-Agent application.
All agents inherit from this abstract base class.
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
    from langchain.callbacks import get_openai_callback
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Fallback for when LangChain is not available
    ChatOpenAI = None
    BaseMessage = None

from config.settings import settings
from config.logging_config import (
    get_agent_logger,
    log_agent_start,
    log_agent_complete,
    log_agent_error,
)
from services.monitoring_service import monitoring_service
from services.error_handler import (
    LLMException,
    handle_exception,
    format_error_message,
)


# Standard input/output format types
AgentInput = Dict[str, Any]
AgentOutput = Dict[str, Any]


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the MemoryChat system.
    
    Provides common functionality including:
    - LangChain LLM initialization
    - Token counting
    - Error handling
    - Logging integration
    - Performance monitoring
    - Standard input/output format
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (e.g., "ConversationAgent")
            description: Agent description
            llm_model: LLM model name (e.g., "gpt-4", "gpt-3.5-turbo"). 
                       If None, agent is rule-based (no LLM).
            temperature: LLM temperature (0.0 to 2.0)
            max_tokens: Maximum tokens for LLM response
            system_prompt: System prompt for the agent
        """
        self.name = name
        self.description = description
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        
        # Initialize logger
        self.logger = get_agent_logger(self.name.lower().replace("agent", "").strip())
        
        # Initialize LLM if model is provided
        self.llm = None
        if llm_model and LANGCHAIN_AVAILABLE:
            try:
                api_key = getattr(settings, 'OPENAI_API_KEY', None)
                if not api_key or api_key == "your-api-key-here":
                    self.logger.warning(
                        f"OPENAI_API_KEY not configured. Agent '{self.name}' will not be able to use LLM."
                    )
                else:
                    # Initialize ChatOpenAI with appropriate parameters
                    init_params = {
                        "model_name": llm_model,
                        "temperature": temperature,
                        "openai_api_key": api_key,
                    }
                    if max_tokens:
                        init_params["max_tokens"] = max_tokens
                    
                    self.llm = ChatOpenAI(**init_params)
                    self.logger.info(
                        f"Initialized LLM for agent '{self.name}': {llm_model} "
                        f"(temperature={temperature}, max_tokens={max_tokens})"
                    )
            except Exception as e:
                self.logger.error(f"Failed to initialize LLM for agent '{self.name}': {str(e)}")
                raise LLMException(f"Failed to initialize LLM: {str(e)}") from e
        elif llm_model and not LANGCHAIN_AVAILABLE:
            self.logger.warning(
                f"LangChain not available. Agent '{self.name}' will not be able to use LLM."
            )
        
        self.logger.info(f"Initialized agent: {self.name} - {self.description}")
    
    @abstractmethod
    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute the agent's main task.
        
        This is an abstract method that must be implemented by subclasses.
        
        Args:
            input_data: Standard input format:
                {
                    "session_id": int,
                    "user_message": str,
                    "privacy_mode": str,
                    "profile_id": int,
                    "context": dict
                }
            context: Optional additional context dictionary
            
        Returns:
            Standard output format:
                {
                    "success": bool,
                    "data": dict,
                    "error": str (if failed),
                    "tokens_used": int,
                    "execution_time_ms": int
                }
        """
        pass
    
    def _log_start(self, task: str) -> None:
        """
        Log the start of an agent task.
        
        Args:
            task: Description of the task being performed
        """
        log_agent_start(self.name, task)
        self.logger.debug(f"Starting task: {task}")
    
    def _log_complete(self, task: str, duration: float) -> None:
        """
        Log the completion of an agent task.
        
        Args:
            task: Description of the task that was completed
            duration: Execution time in seconds
        """
        log_agent_complete(self.name, task, duration)
        self.logger.debug(f"Completed task '{task}' in {duration:.3f}s")
    
    def _log_error(self, task: str, error: Exception) -> None:
        """
        Log an error that occurred during agent execution.
        
        Args:
            task: Description of the task that failed
            error: The exception that occurred
        """
        log_agent_error(self.name, task, error)
        self.logger.error(f"Error in task '{task}': {str(error)}", exc_info=True)
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """
        Format a prompt template with provided keyword arguments.
        
        Args:
            template: Prompt template string (supports {variable} placeholders)
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing variable in prompt template: {e}")
            raise ValueError(f"Missing variable in prompt template: {e}") from e
    
    def _parse_response(self, response: Any) -> str:
        """
        Parse LLM response to extract text content.
        
        Args:
            response: LLM response (can be string, BaseMessage, or other formats)
            
        Returns:
            Extracted text content as string
        """
        if isinstance(response, str):
            return response
        elif hasattr(response, 'content'):
            # LangChain BaseMessage objects
            return str(response.content)
        elif hasattr(response, 'text'):
            # Some response objects have .text attribute
            return str(response.text)
        else:
            # Fallback: convert to string
            return str(response)
    
    def _call_llm(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Call the LLM with a list of messages.
        
        Args:
            messages: List of LangChain message objects
            temperature: Optional temperature override
            max_tokens: Optional max_tokens override
            
        Returns:
            LLM response text
            
        Raises:
            LLMException: If LLM call fails
        """
        if not self.llm:
            raise LLMException(f"LLM not initialized for agent '{self.name}'")
        
        try:
            # Use temperature override if provided, otherwise use agent's default
            temp = temperature if temperature is not None else self.temperature
            
            # Temporarily override temperature if needed
            original_temp = getattr(self.llm, 'temperature', temp)
            if temp != original_temp and hasattr(self.llm, 'temperature'):
                self.llm.temperature = temp
            
            # Call LLM with token tracking
            tokens_used = 0
            input_tokens = 0
            output_tokens = 0
            cost = 0.0
            
            try:
                with get_openai_callback() as cb:
                    response = self.llm(messages)
                    tokens_used = getattr(cb, 'total_tokens', 0)
                    input_tokens = getattr(cb, 'prompt_tokens', 0)
                    output_tokens = getattr(cb, 'completion_tokens', 0)
                    cost = getattr(cb, 'total_cost', 0.0)
                    
                    # Log token usage if available
                    if tokens_used > 0:
                        monitoring_service.log_token_usage(
                            agent_name=self.name,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            cost=cost
                        )
                        
                        self.logger.debug(
                            f"LLM call completed: {input_tokens} input + {output_tokens} output = "
                            f"{tokens_used} total tokens (cost: ${cost:.4f})"
                        )
            except Exception as callback_error:
                # If callback fails, still try to get response
                self.logger.warning(f"Token tracking failed: {callback_error}")
                response = self.llm(messages)
            
            # Restore original temperature
            if temp != original_temp and hasattr(self.llm, 'temperature'):
                self.llm.temperature = original_temp
            
            return self._parse_response(response)
            
        except Exception as e:
            error_msg = f"LLM call failed for agent '{self.name}': {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise LLMException(error_msg) from e
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string.
        
        Uses tiktoken if available, otherwise estimates.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        try:
            import tiktoken
            # Use cl100k_base encoding (used by GPT-3.5 and GPT-4)
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            return len(text) // 4
    
    def _execute_with_wrapper(
        self,
        input_data: AgentInput,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """
        Execute agent with error handling, logging, and monitoring wrappers.
        
        This is a convenience method that wraps execute() with:
        - Timing
        - Error handling
        - Logging
        - Monitoring
        
        Args:
            input_data: Standard input format
            context: Optional additional context
            
        Returns:
            Standard output format with error handling
        """
        start_time = time.time()
        task_name = f"execute({input_data.get('session_id', 'unknown')})"
        
        try:
            # Log start
            self._log_start(task_name)
            
            # Execute agent-specific logic
            result = self.execute(input_data, context)
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"success": True, "data": result}
            
            # Add execution metadata
            result.setdefault("success", True)
            result.setdefault("tokens_used", result.get("tokens_used", 0))
            result["execution_time_ms"] = execution_time_ms
            
            # Log completion
            self._log_complete(task_name, execution_time_ms / 1000.0)
            
            # Track execution time in monitoring service
            # Note: The decorator is applied at function definition time,
            # so we manually record the execution time here
            with monitoring_service._lock:
                monitoring_service._agent_execution_times[self.name].append(execution_time_ms / 1000.0)
                monitoring_service._metrics_timestamps.append(datetime.now())
            
            return result
            
        except Exception as e:
            # Calculate execution time even on error
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log error
            self._log_error(task_name, e)
            
            # Handle exception and format error response
            error_response = handle_exception(
                e,
                context={
                    "agent_name": self.name,
                    "session_id": input_data.get("session_id"),
                    "task": task_name,
                },
                log_error=True
            )
            
            # Return standard error output format
            return {
                "success": False,
                "data": {},
                "error": format_error_message(e, user_friendly=True),
                "error_code": error_response.get("error_code", "UNKNOWN_ERROR"),
                "tokens_used": 0,
                "execution_time_ms": execution_time_ms,
            }
    
    def _build_messages(
        self,
        system_prompt: Optional[str] = None,
        user_message: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[BaseMessage]:
        """
        Build a list of LangChain messages from components.
        
        Args:
            system_prompt: System prompt (uses agent's default if not provided)
            user_message: User message
            conversation_history: Optional list of previous messages 
                                 [{"role": "user|assistant", "content": "..."}]
            
        Returns:
            List of LangChain BaseMessage objects
        """
        if not LANGCHAIN_AVAILABLE:
            raise LLMException("LangChain not available")
        
        messages = []
        
        # Add system prompt
        prompt = system_prompt or self.system_prompt
        if prompt:
            messages.append(SystemMessage(content=prompt))
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
        
        # Add current user message
        if user_message:
            messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        model_info = f"model={self.llm_model}" if self.llm_model else "rule-based"
        return f"<{self.__class__.__name__}(name='{self.name}', {model_info})>"

