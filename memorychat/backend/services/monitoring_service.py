"""
Monitoring service for tracking agent performance and system health.
Provides decorators and utilities for performance tracking, token usage, and metrics.
"""
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
import threading

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config.logging_config import (
    app_logger,
    get_agent_logger,
    log_agent_start,
    log_agent_complete,
    log_agent_error,
)


class MonitoringService:
    """
    Service for monitoring agent performance and system health.
    Thread-safe for concurrent operations.
    """
    
    def __init__(self):
        """Initialize monitoring service with empty metrics storage."""
        # Thread-safe storage for metrics
        self._lock = threading.Lock()
        
        # Performance metrics
        self._agent_execution_times: Dict[str, List[float]] = defaultdict(list)
        self._agent_token_usage: Dict[str, Dict[str, int]] = defaultdict(
            lambda: {"input": 0, "output": 0, "total": 0, "cost": 0.0}
        )
        self._agent_errors: Dict[str, int] = defaultdict(int)
        self._memory_operations: Dict[str, Dict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self._privacy_checks: Dict[int, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        
        # Timestamps for tracking time ranges
        self._metrics_timestamps: List[datetime] = []
        
        app_logger.info("MonitoringService initialized")
    
    def track_execution_time(
        self, agent_name: str, function: Optional[Callable] = None
    ):
        """
        Decorator to track execution time of agent functions.
        
        Usage:
            @monitoring_service.track_execution_time("conversation")
            def my_function():
                ...
        
        Args:
            agent_name: Name of the agent being monitored
            function: Optional function to wrap (for decorator usage)
            
        Returns:
            Decorated function that tracks execution time
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                task_name = f"{func.__name__}"
                
                try:
                    log_agent_start(agent_name, task_name)
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record execution time
                    with self._lock:
                        self._agent_execution_times[agent_name].append(duration)
                        self._metrics_timestamps.append(datetime.now())
                    
                    log_agent_complete(agent_name, task_name, duration)
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    log_agent_error(agent_name, task_name, e)
                    
                    # Record error
                    with self._lock:
                        self._agent_errors[agent_name] += 1
                    
                    raise
            
            return wrapper
        
        # If called with function, apply decorator immediately
        if function is not None:
            return decorator(function)
        
        # Otherwise return decorator
        return decorator
    
    def log_token_usage(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        cost: float = 0.0
    ) -> None:
        """
        Log token usage for an agent.
        
        Args:
            agent_name: Name of the agent
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            cost: Estimated cost in USD (optional)
        """
        with self._lock:
            self._agent_token_usage[agent_name]["input"] += input_tokens
            self._agent_token_usage[agent_name]["output"] += output_tokens
            self._agent_token_usage[agent_name]["total"] += (
                input_tokens + output_tokens
            )
            self._agent_token_usage[agent_name]["cost"] += cost
        
        logger = get_agent_logger(agent_name)
        logger.info(
            f"Token usage - Input: {input_tokens}, Output: {output_tokens}, "
            f"Total: {input_tokens + output_tokens}, Cost: ${cost:.4f}"
        )
    
    def log_memory_operation(
        self,
        operation_type: str,
        profile_id: int,
        count: int = 1
    ) -> None:
        """
        Log memory operations for tracking.
        
        Args:
            operation_type: Type of operation (CREATE, READ, UPDATE, DELETE, SEARCH)
            profile_id: Memory profile ID
            count: Number of operations (default: 1)
        """
        with self._lock:
            self._memory_operations[operation_type.upper()][profile_id] += count
        
        app_logger.debug(
            f"Memory operation: {operation_type} on profile {profile_id}, "
            f"count: {count}"
        )
    
    def log_privacy_check(
        self,
        session_id: int,
        mode: str,
        violations_found: int = 0
    ) -> None:
        """
        Log privacy check results.
        
        Args:
            session_id: Chat session ID
            mode: Privacy mode (normal, incognito, pause_memory)
            violations_found: Number of privacy violations detected
        """
        with self._lock:
            self._privacy_checks[session_id][mode] += 1
            if violations_found > 0:
                self._privacy_checks[session_id]["violations"] += violations_found
        
        app_logger.info(
            f"Privacy check - Session {session_id}, Mode: {mode}, "
            f"Violations: {violations_found}"
        )
    
    def get_performance_stats(
        self, time_range: str = "1h"
    ) -> Dict[str, Any]:
        """
        Get performance statistics for the specified time range.
        
        Args:
            time_range: Time range string (e.g., '1h', '24h', '7d')
                Supports: '1h', '24h', '7d', '30d', 'all'
            
        Returns:
            Dictionary containing performance metrics:
            - agent_response_times: Average response times per agent
            - token_usage: Token usage per agent
            - error_rates: Error counts per agent
            - memory_operations: Memory operation counts
            - privacy_checks: Privacy check statistics
        """
        # Parse time range
        now = datetime.now()
        if time_range == "all":
            cutoff_time = datetime.min
        elif time_range.endswith("h"):
            hours = int(time_range[:-1])
            cutoff_time = now - timedelta(hours=hours)
        elif time_range.endswith("d"):
            days = int(time_range[:-1])
            cutoff_time = now - timedelta(days=days)
        else:
            # Default to 1 hour
            cutoff_time = now - timedelta(hours=1)
        
        # Filter timestamps
        with self._lock:
            recent_timestamps = [
                ts for ts in self._metrics_timestamps if ts >= cutoff_time
            ]
            
            # Calculate agent response times (average)
            agent_response_times = {}
            for agent_name, times in self._agent_execution_times.items():
                if times:
                    agent_response_times[agent_name] = {
                        "average": sum(times) / len(times),
                        "min": min(times),
                        "max": max(times),
                        "count": len(times),
                    }
            
            # Token usage per agent
            token_usage = dict(self._agent_token_usage)
            
            # Error rates per agent
            error_rates = dict(self._agent_errors)
            
            # Memory operations
            memory_operations = {}
            for op_type, profiles in self._memory_operations.items():
                total_count = sum(profiles.values())
                memory_operations[op_type] = {
                    "total": total_count,
                    "by_profile": dict(profiles),
                }
            
            # Privacy checks summary
            privacy_checks_summary = {
                "total_sessions": len(self._privacy_checks),
                "by_mode": defaultdict(int),
                "total_violations": 0,
            }
            for session_data in self._privacy_checks.values():
                for mode, count in session_data.items():
                    if mode == "violations":
                        privacy_checks_summary["total_violations"] += count
                    else:
                        privacy_checks_summary["by_mode"][mode] += count
            
            privacy_checks_summary["by_mode"] = dict(
                privacy_checks_summary["by_mode"]
            )
        
        return {
            "time_range": time_range,
            "metrics_count": len(recent_timestamps),
            "agent_response_times": agent_response_times,
            "token_usage": token_usage,
            "error_rates": error_rates,
            "memory_operations": memory_operations,
            "privacy_checks": privacy_checks_summary,
        }
    
    def get_agent_stats(self, agent_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary with agent-specific statistics
        """
        with self._lock:
            execution_times = self._agent_execution_times.get(agent_name, [])
            token_usage = self._agent_token_usage.get(
                agent_name, {"input": 0, "output": 0, "total": 0, "cost": 0.0}
            )
            error_count = self._agent_errors.get(agent_name, 0)
            
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
            else:
                avg_time = min_time = max_time = 0.0
            
            total_executions = len(execution_times)
            error_rate = (
                error_count / total_executions if total_executions > 0 else 0.0
            )
        
        return {
            "agent_name": agent_name,
            "total_executions": total_executions,
            "average_response_time": avg_time,
            "min_response_time": min_time,
            "max_response_time": max_time,
            "error_count": error_count,
            "error_rate": error_rate,
            "token_usage": token_usage,
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing or periodic cleanup)."""
        with self._lock:
            self._agent_execution_times.clear()
            self._agent_token_usage.clear()
            self._agent_errors.clear()
            self._memory_operations.clear()
            self._privacy_checks.clear()
            self._metrics_timestamps.clear()
        
        app_logger.info("Monitoring metrics reset")


# Create singleton instance
monitoring_service = MonitoringService()

