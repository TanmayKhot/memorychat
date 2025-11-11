"""
Comprehensive logging configuration for the MemoryChat application.
Provides multiple loggers for different components with file rotation.
"""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from config.settings import settings


# Define log directory paths
LOG_DIR = Path(__file__).parent.parent / "logs"
AGENTS_LOG_DIR = LOG_DIR / "agents"

# Ensure log directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
AGENTS_LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_log_level() -> int:
    """Convert string log level to logging constant."""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[int] = None,
    propagate: bool = False,
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name
        log_file: Optional path to log file (relative to LOG_DIR)
        level: Logging level (defaults to settings.LOG_LEVEL)
        propagate: Whether to propagate to parent logger
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(level or get_log_level())
    logger.propagate = propagate
    
    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level or get_log_level())
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (if log_file specified)
    if log_file:
        log_path = LOG_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level or get_log_level())
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_error_logger() -> logging.Logger:
    """Set up dedicated error logger for errors only."""
    logger = logging.getLogger("errors")
    
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Error file handler
    error_file = LOG_DIR / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Initialize main application logger
app_logger = setup_logger("app", log_file="app.log")

# Initialize error logger
error_logger = setup_error_logger()

# Initialize database logger
database_logger = setup_logger("database", log_file="database.log")

# Initialize API logger
api_logger = setup_logger("api", log_file="app.log")  # Shares app.log

# Initialize agent-specific loggers
conversation_logger = setup_logger(
    "agents.conversation",
    log_file="agents/conversation.log"
)
memory_manager_logger = setup_logger(
    "agents.memory_manager",
    log_file="agents/memory_manager.log"
)
memory_retrieval_logger = setup_logger(
    "agents.memory_retrieval",
    log_file="agents/memory_retrieval.log"
)
privacy_guardian_logger = setup_logger(
    "agents.privacy_guardian",
    log_file="agents/privacy_guardian.log"
)
analyst_logger = setup_logger(
    "agents.analyst",
    log_file="agents/analyst.log"
)
coordinator_logger = setup_logger(
    "agents.coordinator",
    log_file="agents/coordinator.log"
)


def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get logger for a specific agent.
    
    Args:
        agent_name: Name of the agent (e.g., 'conversation', 'memory_manager')
        
    Returns:
        Logger instance for the agent
    """
    agent_map = {
        "conversation": conversation_logger,
        "memory_manager": memory_manager_logger,
        "memory_retrieval": memory_retrieval_logger,
        "privacy_guardian": privacy_guardian_logger,
        "analyst": analyst_logger,
        "coordinator": coordinator_logger,
        "conversation_analyst": analyst_logger,
        "context_coordinator": coordinator_logger,
    }
    
    # Normalize agent name
    agent_name = agent_name.lower().replace("_", "_").replace("agent", "").strip()
    
    return agent_map.get(agent_name, app_logger)


# Logging utility functions
def log_agent_start(agent_name: str, task: str) -> None:
    """
    Log the start of an agent task.
    
    Args:
        agent_name: Name of the agent
        task: Description of the task being performed
    """
    logger = get_agent_logger(agent_name)
    logger.info(f"Agent '{agent_name}' starting task: {task}")


def log_agent_complete(agent_name: str, task: str, duration: float) -> None:
    """
    Log the completion of an agent task.
    
    Args:
        agent_name: Name of the agent
        task: Description of the task that was completed
        duration: Execution time in seconds
    """
    logger = get_agent_logger(agent_name)
    logger.info(
        f"Agent '{agent_name}' completed task '{task}' in {duration:.3f}s"
    )


def log_agent_error(agent_name: str, task: str, error: Exception) -> None:
    """
    Log an error that occurred during agent execution.
    
    Args:
        agent_name: Name of the agent
        task: Description of the task that failed
        error: The exception that occurred
    """
    logger = get_agent_logger(agent_name)
    error_logger.error(
        f"Agent '{agent_name}' error in task '{task}': {str(error)}",
        exc_info=True
    )
    logger.error(f"Agent '{agent_name}' error in task '{task}': {str(error)}")


def log_api_request(endpoint: str, method: str, user_id: Optional[int] = None) -> None:
    """
    Log an API request.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        user_id: Optional user ID making the request
    """
    user_info = f" user_id={user_id}" if user_id else ""
    api_logger.info(f"API Request: {method} {endpoint}{user_info}")


def log_database_query(query_type: str, table: str) -> None:
    """
    Log a database query operation.
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Table name being queried
    """
    database_logger.debug(f"Database {query_type} on table '{table}'")

