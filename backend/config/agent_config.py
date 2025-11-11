"""
Agent configuration for MemoryChat Multi-Agent application.
Defines configuration for all agents including models, temperatures, prompts, and token budgets.
"""
from typing import Dict, Any, Optional


# ============================================================================
# AGENT CONFIGURATIONS
# ============================================================================

CONVERSATION_AGENT = {
    "name": "ConversationAgent",
    "description": "Main conversation agent that generates natural, contextually appropriate responses",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": """You are a helpful AI assistant with a good memory. You engage in natural, 
conversational interactions with users. Your responses should be:
- Contextually relevant and helpful
- Natural and conversational in tone
- Informed by the user's memory context when available
- Respectful of privacy settings
- Appropriate for the conversation context

When you have access to memory context, use it to provide personalized responses. 
When you don't have memory context, respond naturally without referencing memories.""",
}


MEMORY_MANAGER_AGENT = {
    "name": "MemoryManagerAgent",
    "description": "Extracts and manages memories from conversations",
    "model": "gpt-3.5-turbo",
    "temperature": 0.3,
    "max_tokens": 300,
    "system_prompt": """You are a memory extraction agent. Your task is to analyze conversations 
and extract important information that should be remembered for future interactions.

Extract memories for:
- Facts about the user (preferences, interests, background)
- Preferences (likes, dislikes, opinions)
- Events (important dates, occurrences, experiences)
- Relationships (people, places, connections)
- Other significant information

For each memory, determine:
1. Content: A clear, concise statement of what to remember
2. Importance score: 0.0 (low) to 1.0 (high) based on significance
3. Memory type: fact, preference, event, relationship, or other
4. Tags: Relevant keywords for categorization

Only extract information that is:
- Explicitly stated or clearly implied
- Relevant for future conversations
- Not already stored in existing memories
- Appropriate to remember based on privacy settings

Return structured memory data in JSON format.""",
}


MEMORY_RETRIEVAL_AGENT = {
    "name": "MemoryRetrievalAgent",
    "description": "Finds and ranks relevant memories for current conversation",
    "model": "gpt-3.5-turbo",
    "temperature": 0.2,
    "max_tokens": 200,
    "system_prompt": """You are a memory retrieval agent. Your task is to find and rank relevant 
memories that should be used to inform the current conversation.

Analyze the user's query and conversation context to:
1. Understand the intent and information needs
2. Identify which memories are relevant
3. Rank memories by relevance (most relevant first)
4. Consider factors like:
   - Semantic similarity to the query
   - Recency of the memory
   - Importance score
   - Mention count (how often it's been referenced)

Return a ranked list of relevant memories with:
- Memory content
- Relevance score
- Why it's relevant to the current query

Only retrieve memories that are directly relevant to the current conversation.
Limit results to the top 5-10 most relevant memories.""",
}


PRIVACY_GUARDIAN_AGENT = {
    "name": "PrivacyGuardianAgent",
    "description": "Detects sensitive information and enforces privacy settings",
    "model": "gpt-3.5-turbo",
    "temperature": 0.0,  # Deterministic for security
    "max_tokens": 200,
    "system_prompt": """You are a privacy guardian agent. Your task is to detect sensitive 
information and enforce privacy settings.

Detect and flag:
- Personal Identifiable Information (PII):
  * Email addresses
  * Phone numbers
  * Credit card numbers
  * Social Security Numbers
  * Physical addresses
  * Dates of birth
- Financial information
- Health information
- Other sensitive data

Privacy modes:
- NORMAL: Allow everything, warn about sensitive data
- INCOGNITO: Block memory storage, redact sensitive information
- PAUSE_MEMORY: Allow memory retrieval but block new storage

For each detected violation:
1. Identify the type of sensitive information
2. Determine severity (low, medium, high)
3. Generate appropriate warning or action
4. Suggest redaction if in INCOGNITO mode

Return structured privacy check results with:
- Violations found (list)
- Recommended actions
- Warnings to display to user
- Sanitized content (if needed)""",
}


CONVERSATION_ANALYST_AGENT = {
    "name": "ConversationAnalystAgent",
    "description": "Analyzes conversation patterns and provides insights",
    "model": "gpt-3.5-turbo",
    "temperature": 0.3,
    "max_tokens": 200,
    "system_prompt": """You are a conversation analyst agent. Your task is to analyze 
conversation patterns and provide insights.

Analyze conversations for:
- Sentiment: positive, negative, neutral, mixed
- Topics: main themes and subjects discussed
- Engagement: user interaction quality and depth
- Patterns: recurring topics or behaviors
- Gaps: missing information that could be useful

Generate insights including:
- Session summary
- Topic distribution
- Sentiment trends
- Engagement metrics
- Recommendations for:
  * Memory profile switching
  * Follow-up questions
  * Memory organization

Return structured analysis results in JSON format.""",
}


CONTEXT_COORDINATOR_AGENT = {
    "name": "ContextCoordinatorAgent",
    "description": "Orchestrates all other agents and manages the conversation flow",
    "model": None,  # Rule-based, no LLM
    "temperature": None,
    "max_tokens": None,
    "system_prompt": None,
}


# ============================================================================
# TOKEN BUDGETS AND PRIORITIES
# ============================================================================

# Token budgets per agent (in tokens)
AGENT_TOKEN_BUDGETS: Dict[str, int] = {
    "ConversationAgent": 2000,  # Highest priority - main user interaction
    "MemoryManagerAgent": 1000,  # Medium priority - memory extraction
    "MemoryRetrievalAgent": 800,  # Medium priority - memory search
    "PrivacyGuardianAgent": 500,  # High priority - security
    "ConversationAnalystAgent": 600,  # Low priority - analysis
    "ContextCoordinatorAgent": 0,  # Rule-based, no tokens
}

# Agent priorities (1 = highest, 6 = lowest)
# Used for resource allocation and error handling fallbacks
AGENT_PRIORITIES: Dict[str, int] = {
    "ConversationAgent": 1,  # Highest - always execute
    "PrivacyGuardianAgent": 2,  # High - security critical
    "MemoryRetrievalAgent": 3,  # Medium - important for context
    "MemoryManagerAgent": 4,  # Medium - important but can skip
    "ConversationAnalystAgent": 5,  # Low - optional analysis
    "ContextCoordinatorAgent": 0,  # Special - orchestrator
}

# Total token budget per request (approximate)
TOTAL_TOKEN_BUDGET = 5000

# Token budget warnings (warn when usage exceeds this percentage)
TOKEN_BUDGET_WARNING_THRESHOLD = 0.8  # 80%


# ============================================================================
# AGENT EXECUTION ORDER
# ============================================================================

# Order in which agents should be executed in a typical conversation flow
AGENT_EXECUTION_ORDER = [
    "PrivacyGuardianAgent",      # Step 1: Privacy check
    "MemoryRetrievalAgent",      # Step 2: Retrieve relevant memories
    "ConversationAgent",          # Step 3: Generate response
    "MemoryManagerAgent",         # Step 4: Extract new memories
    "ConversationAnalystAgent",   # Step 5: Analyze (periodic)
]

# Agents that can be skipped if token budget is tight
SKIPPABLE_AGENTS = [
    "ConversationAnalystAgent",  # Optional analysis
]

# Agents that must always execute
REQUIRED_AGENTS = [
    "ConversationAgent",          # Must always respond
    "PrivacyGuardianAgent",       # Security critical
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_agent_config(agent_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent configuration dictionary or None if not found
    """
    agent_configs = {
        "ConversationAgent": CONVERSATION_AGENT,
        "MemoryManagerAgent": MEMORY_MANAGER_AGENT,
        "MemoryRetrievalAgent": MEMORY_RETRIEVAL_AGENT,
        "PrivacyGuardianAgent": PRIVACY_GUARDIAN_AGENT,
        "ConversationAnalystAgent": CONVERSATION_ANALYST_AGENT,
        "ContextCoordinatorAgent": CONTEXT_COORDINATOR_AGENT,
    }
    
    return agent_configs.get(agent_name)


def get_token_budget(agent_name: str) -> int:
    """
    Get token budget for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Token budget (0 if not found or rule-based)
    """
    return AGENT_TOKEN_BUDGETS.get(agent_name, 0)


def get_agent_priority(agent_name: str) -> int:
    """
    Get priority for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Priority (lower number = higher priority, 0 = special)
    """
    return AGENT_PRIORITIES.get(agent_name, 99)


def is_agent_required(agent_name: str) -> bool:
    """
    Check if an agent is required (cannot be skipped).
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        True if agent is required, False otherwise
    """
    return agent_name in REQUIRED_AGENTS


def is_agent_skippable(agent_name: str) -> bool:
    """
    Check if an agent can be skipped under resource constraints.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        True if agent can be skipped, False otherwise
    """
    return agent_name in SKIPPABLE_AGENTS


def get_all_agent_configs() -> Dict[str, Dict[str, Any]]:
    """
    Get all agent configurations.
    
    Returns:
        Dictionary mapping agent names to their configurations
    """
    return {
        "ConversationAgent": CONVERSATION_AGENT,
        "MemoryManagerAgent": MEMORY_MANAGER_AGENT,
        "MemoryRetrievalAgent": MEMORY_RETRIEVAL_AGENT,
        "PrivacyGuardianAgent": PRIVACY_GUARDIAN_AGENT,
        "ConversationAnalystAgent": CONVERSATION_ANALYST_AGENT,
        "ContextCoordinatorAgent": CONTEXT_COORDINATOR_AGENT,
    }


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_agent_config(config: Dict[str, Any]) -> bool:
    """
    Validate an agent configuration.
    
    Args:
        config: Agent configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["name", "description"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    # Check model configuration
    if config.get("model") is not None:
        # If model is specified, should have temperature
        if "temperature" not in config:
            return False
    
    return True


def validate_all_configs() -> Dict[str, bool]:
    """
    Validate all agent configurations.
    
    Returns:
        Dictionary mapping agent names to validation results
    """
    results = {}
    all_configs = get_all_agent_configs()
    
    for agent_name, config in all_configs.items():
        results[agent_name] = validate_agent_config(config)
    
    return results

