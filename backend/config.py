"""
Configuration and settings module.
Application-level configuration - convenience import.
"""

# Import from core config for convenience
from app.core.config import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]

