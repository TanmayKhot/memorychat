"""
Test script for LLMService implementation.
Verifies that all required methods from Checkpoint 3.5 are present.
"""

import inspect
import asyncio
from app.services.llm_service import LLMService, llm_service


def test_llm_service():
    """Test LLMService implementation."""
    
    print("=" * 70)
    print("LLM SERVICE TEST")
    print("=" * 70)
    print()
    
    # Test service initialization
    try:
        service = LLMService()
        print("✅ LLMService initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Error initializing LLMService: {e}")
        return
    
    # Test singleton instance
    print("=" * 70)
    print("Testing Singleton Instance")
    print("=" * 70)
    try:
        assert llm_service is not None
        print("✅ llm_service singleton instance available")
        print()
    except AssertionError:
        print("❌ llm_service singleton instance not available")
        print()
    
    # Required methods from Checkpoint 3.5
    required_methods = {
        "generate_response": 4,  # messages, context, temperature, max_tokens
        "stream_response": 4,  # messages, context, temperature, max_tokens
    }
    
    # Helper/internal methods
    helper_methods = {
        "_build_system_prompt": 1,  # context
        "_prepare_messages": 2,  # messages, context
        "_retry_with_backoff": None,  # variable args
        "count_tokens": 1,  # text
        "format_memory_context": 1,  # memories
        "validate_messages": 1,  # messages
    }
    
    print("=" * 70)
    print("Verifying Required Methods")
    print("=" * 70)
    
    methods_found = 0
    for method_name, expected_params in required_methods.items():
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
    print(f"📊 Required methods found: {methods_found}/{len(required_methods)}")
    print()
    
    # Check helper methods
    print("=" * 70)
    print("Verifying Helper Methods")
    print("=" * 70)
    
    helper_found = 0
    for method_name, expected_params in helper_methods.items():
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                sig = inspect.signature(method)
                param_count = len([p for p in sig.parameters.values() if p.name != 'self'])
                
                # Check if it's async
                is_async = inspect.iscoroutinefunction(method)
                async_indicator = " (async)" if is_async else ""
                
                print(f"✅ {method_name:<40} - Params: {param_count}{async_indicator}")
                helper_found += 1
            else:
                print(f"❌ {method_name:<40} - Not callable")
        else:
            print(f"❌ {method_name:<40} - Not found")
    
    print()
    print(f"📊 Helper methods found: {helper_found}/{len(helper_methods)}")
    print()
    
    # Verify client initialization
    print("=" * 70)
    print("Verifying Client Initialization")
    print("=" * 70)
    
    client_checks = {
        "client": "Synchronous OpenAI client",
        "async_client": "Asynchronous OpenAI client",
        "model": "Model configuration",
        "temperature": "Temperature setting",
        "max_tokens": "Max tokens setting",
        "max_retries": "Retry configuration",
        "retry_delay": "Retry delay setting",
        "backoff_factor": "Backoff factor setting"
    }
    
    for attr, description in client_checks.items():
        if hasattr(service, attr):
            value = getattr(service, attr)
            print(f"✅ {attr:<20} - {description}: {type(value).__name__}")
        else:
            print(f"❌ {attr:<20} - {description}: Not found")
    
    print()
    
    # Verify configuration
    print("=" * 70)
    print("Configuration Details")
    print("=" * 70)
    print(f"Model: {service.model}")
    print(f"Temperature: {service.temperature}")
    print(f"Max Tokens: {service.max_tokens}")
    print(f"Max Retries: {service.max_retries}")
    print(f"Retry Delay: {service.retry_delay}s")
    print(f"Backoff Factor: {service.backoff_factor}")
    print()
    
    # Final summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if methods_found == len(required_methods):
        print("🎉 All required methods implemented!")
        print("✅ LLMService is ready to use")
        print()
        print("Implemented features:")
        print("  • Chat completion generation (async)")
        print("  • Streaming response support (async)")
        print("  • Context injection (memories + system prompt)")
        print("  • Exponential backoff retry logic")
        print("  • Error handling for API failures")
        print("  • Helper methods for validation and formatting")
        print()
        print(f"Total required methods: {methods_found}")
        print(f"Total methods (with helpers): {methods_found + helper_found}")
    else:
        print("⚠️  Some required methods are missing")
        print(f"Found: {methods_found}/{len(required_methods)}")
    
    print()
    print("=" * 70)
    print("Note: This test only verifies method signatures and initialization.")
    print("Live API calls will be tested through integration tests.")
    print("=" * 70)


async def test_message_validation():
    """Test message validation functionality."""
    print()
    print("=" * 70)
    print("BONUS: Testing Message Validation")
    print("=" * 70)
    
    service = LLMService()
    
    test_cases = [
        {
            "name": "Valid messages",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ],
            "expected": True
        },
        {
            "name": "Empty messages",
            "messages": [],
            "expected": False
        },
        {
            "name": "Invalid role",
            "messages": [{"role": "invalid", "content": "test"}],
            "expected": False
        },
        {
            "name": "Missing content",
            "messages": [{"role": "user"}],
            "expected": False
        }
    ]
    
    for test_case in test_cases:
        result = await service.validate_messages(test_case["messages"])
        status = "✅" if result == test_case["expected"] else "❌"
        print(f"{status} {test_case['name']}: {result} (expected {test_case['expected']})")


async def test_context_formatting():
    """Test context formatting functionality."""
    print()
    print("=" * 70)
    print("BONUS: Testing Context Formatting")
    print("=" * 70)
    
    service = LLMService()
    
    # Test with sample memories
    memories = [
        {"memory": "User prefers Python programming"},
        {"memory": "User is interested in AI and machine learning"},
        {"memory": "User's name is Alice"}
    ]
    
    context = await service.format_memory_context(memories)
    print("Formatted context:")
    print(context)
    print()
    
    # Test with empty memories
    empty_context = await service.format_memory_context([])
    print(f"Empty memories context: '{empty_context}' (should be empty)")
    print()


if __name__ == "__main__":
    test_llm_service()
    
    # Run async tests
    print()
    asyncio.run(test_message_validation())
    asyncio.run(test_context_formatting())

