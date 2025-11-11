#!/usr/bin/env python3
"""
Quick script to verify OpenAI API key is loaded from .env file
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory
os.chdir(backend_dir)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ Loaded .env from {env_path}")
    else:
        print(f"⚠ .env file not found at {env_path}")
except ImportError:
    print("⚠ dotenv not available, relying on pydantic-settings")

# Import settings
from config.settings import settings

# Check API key
if hasattr(settings, 'OPENAI_API_KEY'):
    api_key = settings.OPENAI_API_KEY
    if api_key and api_key != "your-api-key-here":
        print(f"✓ OpenAI API key is configured")
        print(f"  Key length: {len(api_key)} characters")
        print(f"  Key starts with: {api_key[:7]}...")
        # Set as environment variable
        os.environ["OPENAI_API_KEY"] = api_key
        print(f"✓ API key set in environment variable")
    else:
        print("✗ OpenAI API key is not configured or set to placeholder")
        print("  Please set OPENAI_API_KEY in backend/.env file")
else:
    print("✗ OPENAI_API_KEY not found in settings")


