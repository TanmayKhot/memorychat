"""
Test script for configuration module.
Verifies that settings are loaded correctly from .env file.
"""

from app.core.config import get_settings, settings


def test_settings():
    """Test that settings are loaded correctly."""
    print("=" * 60)
    print("CONFIGURATION TEST")
    print("=" * 60)
    
    # Get settings instance
    config = get_settings()
    
    print("\n✅ Settings loaded successfully!")
    print("\n" + "=" * 60)
    print("APPLICATION SETTINGS")
    print("=" * 60)
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"App Name: {config.APP_NAME}")
    print(f"API Prefix: {config.API_V1_PREFIX}")
    
    print("\n" + "=" * 60)
    print("SUPABASE CONFIGURATION")
    print("=" * 60)
    print(f"URL: {config.SUPABASE_URL}")
    print(f"Anon Key: {config.SUPABASE_KEY[:20]}..." if len(config.SUPABASE_KEY) > 20 else f"Anon Key: {config.SUPABASE_KEY}")
    print(f"Service Key: {config.SUPABASE_SERVICE_KEY[:20]}..." if len(config.SUPABASE_SERVICE_KEY) > 20 else f"Service Key: {config.SUPABASE_SERVICE_KEY}")
    
    print("\n" + "=" * 60)
    print("MEM0 CONFIGURATION")
    print("=" * 60)
    if config.MEM0_API_KEY:
        print(f"API Key: {config.MEM0_API_KEY[:20]}...")
    else:
        print("API Key: Not configured (using self-hosted mem0)")
    
    print("\n" + "=" * 60)
    print("LLM SETTINGS (OpenAI)")
    print("=" * 60)
    print(f"API Key: {config.OPENAI_API_KEY[:20]}..." if len(config.OPENAI_API_KEY) > 20 else f"API Key: {config.OPENAI_API_KEY}")
    print(f"Model: {config.OPENAI_MODEL}")
    print(f"Max Tokens: {config.OPENAI_MAX_TOKENS}")
    print(f"Temperature: {config.OPENAI_TEMPERATURE}")
    
    print("\n" + "=" * 60)
    print("JWT SETTINGS")
    print("=" * 60)
    print(f"Algorithm: {config.JWT_ALGORITHM}")
    print(f"Token Expiry: {config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    
    print("\n" + "=" * 60)
    print("CORS SETTINGS")
    print("=" * 60)
    print(f"Allowed Origins: {config.CORS_ORIGINS}")
    print(f"Allow Credentials: {config.CORS_CREDENTIALS}")
    
    print("\n" + "=" * 60)
    print("OTHER SETTINGS")
    print("=" * 60)
    print(f"Log Level: {config.LOG_LEVEL}")
    print(f"Rate Limiting: {'Enabled' if config.RATE_LIMIT_ENABLED else 'Disabled'}")
    
    # Test that singleton works
    config2 = get_settings()
    assert config is config2, "Settings should be a singleton!"
    print("\n✅ Singleton pattern verified!")
    
    # Test convenience import
    assert settings is config, "Convenience import should work!"
    print("✅ Convenience import verified!")
    
    print("\n" + "=" * 60)
    print("🎉 ALL CONFIGURATION TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_settings()
    except Exception as e:
        print(f"\n❌ Configuration test failed: {str(e)}")
        print("\nPlease ensure:")
        print("  1. .env file exists in backend directory")
        print("  2. All required environment variables are set")
        print("  3. Values are valid")
        import traceback
        traceback.print_exc()

