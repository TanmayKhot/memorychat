"""
Context Coordinator Agent for MemoryChat Multi-Agent application.
Orchestrates all other agents and manages the conversation flow.
"""
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from agents.privacy_guardian_agent import PrivacyGuardianAgent
from agents.memory_retrieval_agent import MemoryRetrievalAgent
from agents.conversation_agent import ConversationAgent
from agents.memory_manager_agent import MemoryManagerAgent
from agents.conversation_analyst_agent import ConversationAnalystAgent
from config.agent_config import (
    CONTEXT_COORDINATOR_AGENT,
    AGENT_TOKEN_BUDGETS,
    AGENT_PRIORITIES,
    TOTAL_TOKEN_BUDGET,
)
from config.logging_config import get_agent_logger


class ContextCoordinatorAgent(BaseAgent):
    """
    Orchestrator agent that coordinates all other agents.
    
    This is a rule-based agent (no LLM) that:
    - Routes requests to appropriate agents
    - Manages execution order
    - Handles errors and fallbacks
    - Manages token budgets
    - Aggregates results
    """
    
    def __init__(self):
        """Initialize Context Coordinator Agent."""
        config = CONTEXT_COORDINATOR_AGENT
        super().__init__(
            name=config["name"],
            description=config["description"],
            llm_model=None,  # Rule-based, no LLM
            temperature=None,
            max_tokens=None,
            system_prompt=None
        )
        
        # Initialize all agents
        self.privacy_guardian = PrivacyGuardianAgent()
        self.memory_retrieval = MemoryRetrievalAgent()
        self.conversation_agent = ConversationAgent()
        self.memory_manager = MemoryManagerAgent()
        self.conversation_analyst = ConversationAnalystAgent()
        
        # Token budget tracking
        self.token_budgets = AGENT_TOKEN_BUDGETS.copy()
        self.total_budget = TOTAL_TOKEN_BUDGET
        
        # Agent priorities
        self.agent_priorities = AGENT_PRIORITIES.copy()
        
        # Analysis interval (analyze every N messages)
        self.analysis_interval = 5
        
        # Execution tracking
        self.agents_executed = []
        self.tokens_used_by_agent = {}
    
    def execute(self, input_data: AgentInput, context: Optional[Dict[str, Any]] = None) -> AgentOutput:
        """
        Execute orchestration flow.
        
        Args:
            input_data: Standard input format with:
                - session_id: int
                - user_message: str
                - privacy_mode: str
                - profile_id: int
                - context: dict
            context: Optional additional context
            
        Returns:
            Standard output format with final response and metadata
        """
        start_time = datetime.now()
        self.agents_executed = []
        self.tokens_used_by_agent = {}
        
        try:
            # Get input data
            session_id = input_data.get("session_id")
            user_message = input_data.get("user_message", "")
            privacy_mode = input_data.get("privacy_mode", "normal").lower()
            profile_id = input_data.get("profile_id")
            
            if not user_message:
                return {
                    "success": False,
                    "data": {"response": ""},
                    "error": "No user message provided",
                    "tokens_used": 0,
                    "execution_time_ms": 0,
                }
            
            # Initialize context
            orchestration_context = {
                "session_id": session_id,
                "privacy_mode": privacy_mode,
                "profile_id": profile_id,
                "user_message": user_message,
                "conversation_history": input_data.get("context", {}).get("conversation_history", []),
                "existing_memories": input_data.get("context", {}).get("existing_memories", []),
            }
            
            # STEP 1: Privacy Check
            privacy_result = self._execute_privacy_check(input_data, orchestration_context)
            if not privacy_result.get("success", True):
                return self._build_error_response(
                    "Privacy check failed",
                    privacy_result.get("error", "Unknown error"),
                    orchestration_context
                )
            
            # Check if blocked by privacy
            if privacy_result.get("data", {}).get("allowed") == False:
                return {
                    "success": False,
                    "data": {
                        "response": "I'm sorry, but I cannot process this message due to privacy restrictions.",
                        "warnings": privacy_result.get("data", {}).get("warnings", []),
                    },
                    "error": "Message blocked by privacy guardian",
                    "tokens_used": self._get_total_tokens_used(),
                    "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                    "agents_executed": self.agents_executed,
                }
            
            # Update context with sanitized content if needed
            sanitized_content = privacy_result.get("data", {}).get("sanitized_content")
            if sanitized_content and sanitized_content != user_message:
                orchestration_context["user_message"] = sanitized_content
                orchestration_context["sanitized"] = True
            
            # STEP 2: Memory Retrieval (if not INCOGNITO)
            memory_context = ""
            if privacy_mode != "incognito":
                retrieval_result = self._execute_memory_retrieval(input_data, orchestration_context)
                if retrieval_result.get("success"):
                    memory_context = retrieval_result.get("data", {}).get("context", "")
                    orchestration_context["memory_context"] = memory_context
                else:
                    self.logger.warning("Memory retrieval failed, continuing without memories")
            
            # STEP 3: Conversation Generation (ALWAYS execute)
            conversation_result = self._execute_conversation_generation(
                input_data, orchestration_context
            )
            
            if not conversation_result.get("success"):
                # Fallback: simple response
                return {
                    "success": True,
                    "data": {
                        "response": "I apologize, but I'm having trouble generating a response right now. Please try again.",
                        "fallback": True,
                    },
                    "tokens_used": self._get_total_tokens_used(),
                    "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                    "agents_executed": self.agents_executed,
                }
            
            response = conversation_result.get("data", {}).get("response", "")
            
            # STEP 4: Memory Management (if NORMAL mode)
            # Skip if INCOGNITO or PAUSE_MEMORY mode
            memory_extraction_result = None
            if privacy_mode == "normal":
                # Prepare input for memory manager
                memory_input = {
                    "session_id": session_id,
                    "user_message": user_message,
                    "privacy_mode": privacy_mode,
                    "profile_id": profile_id,
                    "context": {
                        "assistant_response": response,
                        "conversation_history": orchestration_context.get("conversation_history", []),
                    }
                }
                memory_extraction_result = self._execute_memory_management(
                    memory_input, orchestration_context
                )
                if not memory_extraction_result.get("success"):
                    self.logger.warning("Memory extraction failed, continuing without storing memories")
            
            # STEP 5: Analysis (periodic)
            analysis_result = None
            conversation_history = orchestration_context.get("conversation_history", [])
            if len(conversation_history) > 0 and len(conversation_history) % self.analysis_interval == 0:
                analysis_result = self._execute_analysis(input_data, orchestration_context)
                if not analysis_result.get("success"):
                    self.logger.debug("Analysis failed, continuing without analysis")
            
            # Aggregate results
            final_response = self._aggregate_results(
                privacy_result=privacy_result,
                retrieval_result=retrieval_result if privacy_mode != "incognito" else None,
                conversation_result=conversation_result,
                memory_result=memory_extraction_result,
                analysis_result=analysis_result,
                orchestration_context=orchestration_context
            )
            
            execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            self.logger.info(
                f"Orchestration completed: {len(self.agents_executed)} agents executed, "
                f"{self._get_total_tokens_used()} tokens used, {execution_time_ms}ms"
            )
            
            return {
                "success": True,
                "data": final_response,
                "tokens_used": self._get_total_tokens_used(),
                "execution_time_ms": execution_time_ms,
                "agents_executed": self.agents_executed,
                "tokens_by_agent": self.tokens_used_by_agent.copy(),
            }
            
        except Exception as e:
            self.logger.error(f"Error in orchestration: {str(e)}", exc_info=True)
            return {
                "success": False,
                "data": {"response": ""},
                "error": f"Orchestration failed: {str(e)}",
                "tokens_used": self._get_total_tokens_used(),
                "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "agents_executed": self.agents_executed,
            }
    
    def _execute_privacy_check(
        self,
        input_data: AgentInput,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute privacy check step."""
        try:
            self.logger.debug("Executing privacy check...")
            result = self.privacy_guardian._execute_with_wrapper(input_data)
            self._track_agent_execution("PrivacyGuardianAgent", result)
            return result
        except Exception as e:
            self.logger.error(f"Privacy check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {"allowed": False},
            }
    
    def _execute_memory_retrieval(
        self,
        input_data: AgentInput,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute memory retrieval step."""
        try:
            self.logger.debug("Executing memory retrieval...")
            result = self.memory_retrieval._execute_with_wrapper(input_data)
            self._track_agent_execution("MemoryRetrievalAgent", result)
            return result
        except Exception as e:
            self.logger.warning(f"Memory retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {"memories": [], "context": ""},
            }
    
    def _execute_conversation_generation(
        self,
        input_data: AgentInput,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute conversation generation step."""
        try:
            self.logger.debug("Executing conversation generation...")
            # Add memory context to input
            enhanced_input = input_data.copy()
            enhanced_input["context"] = enhanced_input.get("context", {})
            enhanced_input["context"]["memory_context"] = context.get("memory_context", "")
            enhanced_input["context"]["conversation_history"] = context.get("conversation_history", [])
            
            result = self.conversation_agent._execute_with_wrapper(enhanced_input)
            self._track_agent_execution("ConversationAgent", result)
            return result
        except Exception as e:
            self.logger.error(f"Conversation generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {"response": ""},
            }
    
    def _execute_memory_management(
        self,
        input_data: AgentInput,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute memory management step."""
        try:
            self.logger.debug("Executing memory management...")
            result = self.memory_manager._execute_with_wrapper(input_data)
            self._track_agent_execution("MemoryManagerAgent", result)
            return result
        except Exception as e:
            self.logger.warning(f"Memory management failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {"memories": []},
            }
    
    def _execute_analysis(
        self,
        input_data: AgentInput,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute conversation analysis step."""
        try:
            self.logger.debug("Executing conversation analysis...")
            # Add conversation history to input
            enhanced_input = input_data.copy()
            enhanced_input["context"] = enhanced_input.get("context", {})
            enhanced_input["context"]["conversation_history"] = context.get("conversation_history", [])
            enhanced_input["context"]["existing_memories"] = context.get("existing_memories", [])
            
            result = self.conversation_analyst._execute_with_wrapper(enhanced_input)
            self._track_agent_execution("ConversationAnalystAgent", result)
            return result
        except Exception as e:
            self.logger.debug(f"Analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": {"analysis": {}, "insights": {}, "recommendations": []},
            }
    
    def _track_agent_execution(self, agent_name: str, result: Dict[str, Any]) -> None:
        """Track agent execution and token usage."""
        self.agents_executed.append(agent_name)
        tokens_used = result.get("tokens_used", 0)
        self.tokens_used_by_agent[agent_name] = tokens_used
        
        # Check token budget
        budget = self.token_budgets.get(agent_name, 0)
        if budget > 0 and tokens_used > budget:
            self.logger.warning(
                f"Agent {agent_name} exceeded token budget: {tokens_used} > {budget}"
            )
    
    def _get_total_tokens_used(self) -> int:
        """Get total tokens used across all agents."""
        return sum(self.tokens_used_by_agent.values())
    
    def _determine_required_agents(
        self,
        request_type: str,
        privacy_mode: str
    ) -> List[str]:
        """
        Determine which agents are required for this request.
        
        Args:
            request_type: Type of request
            privacy_mode: Privacy mode
            
        Returns:
            List of agent names in execution order
        """
        agents = []
        
        # Privacy check is always required
        agents.append("PrivacyGuardianAgent")
        
        # Memory retrieval (skip if INCOGNITO)
        if privacy_mode != "incognito":
            agents.append("MemoryRetrievalAgent")
        
        # Conversation generation is always required
        agents.append("ConversationAgent")
        
        # Memory management (only in NORMAL mode)
        if privacy_mode == "normal":
            agents.append("MemoryManagerAgent")
        
        # Analysis (periodic, optional)
        # Handled separately in execute()
        
        return agents
    
    def _aggregate_results(
        self,
        privacy_result: Dict[str, Any],
        retrieval_result: Optional[Dict[str, Any]],
        conversation_result: Dict[str, Any],
        memory_result: Optional[Dict[str, Any]],
        analysis_result: Optional[Dict[str, Any]],
        orchestration_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate results from all agents into final response.
        
        Args:
            privacy_result: Privacy check results
            retrieval_result: Memory retrieval results
            conversation_result: Conversation generation results
            memory_result: Memory management results
            analysis_result: Analysis results
            orchestration_context: Orchestration context
            
        Returns:
            Aggregated response dictionary
        """
        # Get main response
        response = conversation_result.get("data", {}).get("response", "")
        
        # Get warnings from privacy check
        warnings = privacy_result.get("data", {}).get("warnings", [])
        
        # Get memory context info
        memory_info = {}
        if retrieval_result:
            memory_info = {
                "memories_retrieved": len(retrieval_result.get("data", {}).get("memories", [])),
                "memory_context_provided": bool(retrieval_result.get("data", {}).get("context", "")),
            }
        
        # Get memory extraction info
        memory_extraction_info = {}
        if memory_result:
            memory_extraction_info = {
                "memories_extracted": len(memory_result.get("data", {}).get("memories", [])),
                "memories_stored": memory_result.get("success", False),
            }
        
        # Get analysis info
        analysis_info = {}
        if analysis_result:
            analysis_info = {
                "analysis_performed": True,
                "sentiment": analysis_result.get("data", {}).get("analysis", {}).get("sentiment", {}).get("sentiment"),
                "topics_count": len(analysis_result.get("data", {}).get("analysis", {}).get("topics", [])),
                "recommendations_count": len(analysis_result.get("data", {}).get("recommendations", [])),
            }
        
        return {
            "response": response,
            "warnings": warnings,
            "memory_info": memory_info,
            "memory_extraction_info": memory_extraction_info,
            "analysis_info": analysis_info,
            "privacy_mode": orchestration_context.get("privacy_mode"),
            "sanitized": orchestration_context.get("sanitized", False),
        }
    
    def _build_error_response(
        self,
        error_type: str,
        error_message: str,
        context: Dict[str, Any]
    ) -> AgentOutput:
        """Build error response."""
        return {
            "success": False,
            "data": {
                "response": f"I apologize, but I encountered an error: {error_type}",
                "error_type": error_type,
            },
            "error": error_message,
            "tokens_used": self._get_total_tokens_used(),
            "execution_time_ms": 0,
            "agents_executed": self.agents_executed,
        }

