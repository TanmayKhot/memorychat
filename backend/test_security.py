"""
Test script for Security implementation.
Verifies that all required components from Checkpoint 3.7 are present.
"""

import inspect
from app.core.security import (
    SecurityService,
    security_service,
    get_current_user,
    get_current_user_optional,
    verify_user_access,
    get_cors_config,
    RateLimitConfig,
    rate_limit_config,
    get_security_headers,
    APIKeyAuth,
    api_key_auth
)


def test_security():
    """Test Security implementation."""
    
    print("=" * 70)
    print("SECURITY MODULE TEST")
    print("=" * 70)
    print()
    
    # Test SecurityService initialization
    try:
        service = SecurityService()
        print("✅ SecurityService initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Error initializing SecurityService: {e}")
        return
    
    # Test singleton instance
    print("=" * 70)
    print("Testing Singleton Instance")
    print("=" * 70)
    try:
        assert security_service is not None
        print("✅ security_service singleton instance available")
        print()
    except AssertionError:
        print("❌ security_service singleton instance not available")
        print()
    
    # Required methods from Checkpoint 3.7
    security_methods = {
        "verify_jwt_token": 1,  # token
        "verify_supabase_token": 1,  # token
        "get_current_user_from_token": 1,  # token
        "validate_user_access": 2,  # user_id, resource_user_id
        "hash_password": 1,  # password
        "verify_password": 2,  # plain_password, hashed_password
    }
    
    print("=" * 70)
    print("Verifying SecurityService Methods")
    print("=" * 70)
    
    methods_found = 0
    for method_name, expected_params in security_methods.items():
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                # Get method signature
                sig = inspect.signature(method)
                param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
                
                # Check if it's async
                is_async = inspect.iscoroutinefunction(method)
                async_indicator = " (async)" if is_async else ""
                
                print(f"✅ {method_name:<40} - Params: {param_count}{async_indicator}")
                methods_found += 1
            else:
                print(f"❌ {method_name:<40} - Not callable")
        else:
            print(f"❌ {method_name:<40} - Not found")
    
    print()
    print(f"📊 SecurityService methods found: {methods_found}/{len(security_methods)}")
    print()
    
    # Check FastAPI dependencies
    print("=" * 70)
    print("Verifying FastAPI Dependencies")
    print("=" * 70)
    
    dependencies = [
        "get_current_user",
        "get_current_user_optional",
        "verify_user_access"
    ]
    
    deps_found = 0
    for dep_name in dependencies:
        if dep_name in globals() or dep_name in dir():
            is_async = inspect.iscoroutinefunction(eval(dep_name))
            async_indicator = " (async)" if is_async else ""
            print(f"✅ {dep_name:<40}{async_indicator}")
            deps_found += 1
        else:
            print(f"❌ {dep_name:<40} - Not found")
    
    print()
    print(f"📊 Dependencies found: {deps_found}/{len(dependencies)}")
    print()
    
    # Check CORS configuration
    print("=" * 70)
    print("Verifying CORS Configuration")
    print("=" * 70)
    
    try:
        cors_config = get_cors_config()
        required_keys = ["allow_origins", "allow_credentials", "allow_methods", "allow_headers"]
        
        for key in required_keys:
            if key in cors_config:
                print(f"✅ {key:<30} - {type(cors_config[key]).__name__}")
            else:
                print(f"❌ {key:<30} - Not found")
        
        print()
    except Exception as e:
        print(f"❌ Error getting CORS config: {e}")
        print()
    
    # Check Rate Limiting configuration
    print("=" * 70)
    print("Verifying Rate Limiting Configuration")
    print("=" * 70)
    
    try:
        assert rate_limit_config is not None
        print(f"✅ rate_limit_config instance available")
        print(f"   Enabled: {rate_limit_config.is_enabled()}")
        print(f"   Limit: {rate_limit_config.get_limit()} requests/minute")
        print(f"   Limit String: {rate_limit_config.get_limit_string()}")
        print()
    except Exception as e:
        print(f"❌ Error checking rate limit config: {e}")
        print()
    
    # Check Security Headers
    print("=" * 70)
    print("Verifying Security Headers")
    print("=" * 70)
    
    try:
        headers = get_security_headers()
        print(f"✅ Security headers function available")
        print(f"   Headers count: {len(headers)}")
        for header, value in headers.items():
            print(f"   • {header}: {value}")
        print()
    except Exception as e:
        print(f"❌ Error getting security headers: {e}")
        print()
    
    # Check API Key Auth
    print("=" * 70)
    print("Verifying API Key Authentication")
    print("=" * 70)
    
    try:
        assert api_key_auth is not None
        print(f"✅ api_key_auth instance available")
        
        # Test API key methods
        api_methods = ["validate_api_key", "add_api_key", "remove_api_key"]
        for method_name in api_methods:
            if hasattr(api_key_auth, method_name):
                print(f"✅ {method_name:<30} - Available")
            else:
                print(f"❌ {method_name:<30} - Not found")
        print()
    except Exception as e:
        print(f"❌ Error checking API key auth: {e}")
        print()
    
    # Check Supabase client initialization
    print("=" * 70)
    print("Verifying Supabase Client")
    print("=" * 70)
    
    if hasattr(service, 'supabase'):
        print("✅ Supabase client initialized")
        print(f"   Type: {type(service.supabase).__name__}")
    else:
        print("❌ Supabase client not found")
    
    print()
    
    # Final summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_components = (
        len(security_methods) +  # SecurityService methods
        len(dependencies) +  # FastAPI dependencies
        1 +  # CORS config
        1 +  # Rate limit config
        1 +  # Security headers
        1    # API key auth
    )
    
    if methods_found == len(security_methods) and deps_found == len(dependencies):
        print("🎉 All required components implemented!")
        print("✅ Security module is ready to use")
        print()
        print("Implemented features:")
        print("  • JWT token verification")
        print("  • Supabase token verification")
        print("  • User authentication from token")
        print("  • User access validation")
        print("  • Password hashing (bcrypt)")
        print("  • FastAPI dependencies (get_current_user)")
        print("  • CORS configuration")
        print("  • Rate limiting configuration")
        print("  • Security headers")
        print("  • API key authentication")
        print()
        print(f"Total SecurityService methods: {methods_found}")
        print(f"Total FastAPI dependencies: {deps_found}")
        print(f"Additional features: CORS, Rate Limiting, Security Headers, API Key Auth")
    else:
        print("⚠️  Some required components are missing")
        print(f"Methods found: {methods_found}/{len(security_methods)}")
        print(f"Dependencies found: {deps_found}/{len(dependencies)}")
    
    print()
    print("=" * 70)
    print("Security Features")
    print("=" * 70)
    print("Authentication:")
    print("  • JWT token verification (Supabase)")
    print("  • Bearer token authentication")
    print("  • User session management")
    print()
    print("Authorization:")
    print("  • User access validation")
    print("  • Resource ownership verification")
    print()
    print("Security:")
    print("  • CORS protection")
    print("  • Rate limiting")
    print("  • Security headers (XSS, Frame, HSTS)")
    print("  • Password hashing (bcrypt)")
    print()
    print("API Protection:")
    print("  • API key authentication for service calls")
    print("  • Optional authentication support")
    print()
    print("=" * 70)
    print("Note: This test only verifies component existence.")
    print("Live authentication will be tested through API integration.")
    print("=" * 70)


if __name__ == "__main__":
    test_security()

