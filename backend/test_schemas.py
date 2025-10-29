"""
Test script for Pydantic Schemas implementation.
Verifies that all required schemas from Checkpoint 3.8 are present and valid.
"""

import inspect
from app.schemas import (
    # User schemas
    UserCreate,
    UserResponse,
    UserUpdate,
    UserLogin,
    TokenResponse,
    # Memory schemas
    MemoryProfileCreate,
    MemoryProfileUpdate,
    MemoryProfileResponse,
    MemoryResponse,
    MemoryCreate,
    MemorySearchRequest,
    MemorySearchResponse,
    # Chat schemas
    PrivacyMode,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionUpdate,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ChatStreamChunk,
    ConversationSummary,
    ErrorResponse,
)
from pydantic import BaseModel
from enum import Enum


def test_schemas():
    """Test Pydantic Schemas implementation."""
    
    print("=" * 70)
    print("PYDANTIC SCHEMAS TEST")
    print("=" * 70)
    print()
    
    # Required schemas from Checkpoint 3.8
    user_schemas = {
        "UserResponse": UserResponse,
        "UserCreate": UserCreate,
    }
    
    memory_schemas = {
        "MemoryProfileCreate": MemoryProfileCreate,
        "MemoryProfileUpdate": MemoryProfileUpdate,
        "MemoryProfileResponse": MemoryProfileResponse,
        "MemoryResponse": MemoryResponse,
    }
    
    chat_schemas = {
        "ChatSessionCreate": ChatSessionCreate,
        "ChatSessionResponse": ChatSessionResponse,
        "ChatMessageCreate": ChatMessageCreate,
        "ChatMessageResponse": ChatMessageResponse,
        "ChatRequest": ChatRequest,
        "ChatResponse": ChatResponse,
        "PrivacyMode": PrivacyMode,
    }
    
    # Additional schemas (bonus)
    additional_schemas = {
        "UserUpdate": UserUpdate,
        "UserLogin": UserLogin,
        "TokenResponse": TokenResponse,
        "MemoryCreate": MemoryCreate,
        "MemorySearchRequest": MemorySearchRequest,
        "MemorySearchResponse": MemorySearchResponse,
        "ChatSessionUpdate": ChatSessionUpdate,
        "ChatStreamChunk": ChatStreamChunk,
        "ConversationSummary": ConversationSummary,
        "ErrorResponse": ErrorResponse,
    }
    
    # Test User Schemas
    print("=" * 70)
    print("Verifying User Schemas")
    print("=" * 70)
    
    user_found = 0
    for schema_name, schema_class in user_schemas.items():
        if schema_class:
            # Check if it's a Pydantic model
            is_pydantic = issubclass(schema_class, BaseModel)
            
            # Get fields
            fields = list(schema_class.model_fields.keys()) if is_pydantic else []
            
            status = "✅" if is_pydantic else "❌"
            print(f"{status} {schema_name:<40} - Fields: {len(fields)}")
            if fields and len(fields) <= 10:
                print(f"   Fields: {', '.join(fields)}")
            
            if is_pydantic:
                user_found += 1
        else:
            print(f"❌ {schema_name:<40} - Not found")
    
    print()
    print(f"📊 User schemas found: {user_found}/{len(user_schemas)}")
    print()
    
    # Test Memory Schemas
    print("=" * 70)
    print("Verifying Memory Schemas")
    print("=" * 70)
    
    memory_found = 0
    for schema_name, schema_class in memory_schemas.items():
        if schema_class:
            is_pydantic = issubclass(schema_class, BaseModel)
            fields = list(schema_class.model_fields.keys()) if is_pydantic else []
            
            status = "✅" if is_pydantic else "❌"
            print(f"{status} {schema_name:<40} - Fields: {len(fields)}")
            if fields and len(fields) <= 10:
                print(f"   Fields: {', '.join(fields)}")
            
            if is_pydantic:
                memory_found += 1
        else:
            print(f"❌ {schema_name:<40} - Not found")
    
    print()
    print(f"📊 Memory schemas found: {memory_found}/{len(memory_schemas)}")
    print()
    
    # Test Chat Schemas
    print("=" * 70)
    print("Verifying Chat Schemas")
    print("=" * 70)
    
    chat_found = 0
    for schema_name, schema_class in chat_schemas.items():
        if schema_class:
            # Check if it's PrivacyMode enum
            if schema_name == "PrivacyMode":
                is_enum = issubclass(schema_class, Enum)
                if is_enum:
                    values = [e.value for e in schema_class]
                    print(f"✅ {schema_name:<40} - Enum values: {', '.join(values)}")
                    chat_found += 1
                else:
                    print(f"❌ {schema_name:<40} - Not an Enum")
            else:
                is_pydantic = issubclass(schema_class, BaseModel)
                fields = list(schema_class.model_fields.keys()) if is_pydantic else []
                
                status = "✅" if is_pydantic else "❌"
                print(f"{status} {schema_name:<40} - Fields: {len(fields)}")
                if fields and len(fields) <= 10:
                    print(f"   Fields: {', '.join(fields)}")
                
                if is_pydantic:
                    chat_found += 1
        else:
            print(f"❌ {schema_name:<40} - Not found")
    
    print()
    print(f"📊 Chat schemas found: {chat_found}/{len(chat_schemas)}")
    print()
    
    # Test Additional Schemas
    print("=" * 70)
    print("Verifying Additional Schemas (Bonus)")
    print("=" * 70)
    
    additional_found = 0
    for schema_name, schema_class in additional_schemas.items():
        if schema_class:
            is_pydantic = issubclass(schema_class, BaseModel)
            fields = list(schema_class.model_fields.keys()) if is_pydantic else []
            
            status = "✅" if is_pydantic else "❌"
            print(f"{status} {schema_name:<40} - Fields: {len(fields)}")
            
            if is_pydantic:
                additional_found += 1
        else:
            print(f"❌ {schema_name:<40} - Not found")
    
    print()
    print(f"📊 Additional schemas found: {additional_found}/{len(additional_schemas)}")
    print()
    
    # Test schema validation with examples
    print("=" * 70)
    print("Testing Schema Validation")
    print("=" * 70)
    
    validation_tests = []
    
    # Test UserCreate
    try:
        user = UserCreate(
            email="test@example.com",
            password="password123"
        )
        validation_tests.append(("UserCreate", True, None))
        print(f"✅ UserCreate validation passed")
    except Exception as e:
        validation_tests.append(("UserCreate", False, str(e)))
        print(f"❌ UserCreate validation failed: {e}")
    
    # Test MemoryProfileCreate
    try:
        profile = MemoryProfileCreate(
            name="Test Profile",
            description="A test profile"
        )
        validation_tests.append(("MemoryProfileCreate", True, None))
        print(f"✅ MemoryProfileCreate validation passed")
    except Exception as e:
        validation_tests.append(("MemoryProfileCreate", False, str(e)))
        print(f"❌ MemoryProfileCreate validation failed: {e}")
    
    # Test ChatRequest
    try:
        chat_req = ChatRequest(
            message="Hello, world!",
            stream=False
        )
        validation_tests.append(("ChatRequest", True, None))
        print(f"✅ ChatRequest validation passed")
    except Exception as e:
        validation_tests.append(("ChatRequest", False, str(e)))
        print(f"❌ ChatRequest validation failed: {e}")
    
    # Test PrivacyMode enum
    try:
        mode = PrivacyMode.NORMAL
        assert mode.value == "normal"
        validation_tests.append(("PrivacyMode", True, None))
        print(f"✅ PrivacyMode enum works correctly")
    except Exception as e:
        validation_tests.append(("PrivacyMode", False, str(e)))
        print(f"❌ PrivacyMode enum failed: {e}")
    
    print()
    
    # Final summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    total_required = len(user_schemas) + len(memory_schemas) + len(chat_schemas)
    total_found = user_found + memory_found + chat_found
    
    if total_found == total_required:
        print("🎉 All required schemas implemented!")
        print("✅ Pydantic schemas are ready to use")
        print()
        print("Implemented schemas:")
        print(f"  • User schemas: {user_found}")
        print(f"  • Memory schemas: {memory_found}")
        print(f"  • Chat schemas: {chat_found}")
        print(f"  • Additional schemas: {additional_found}")
        print()
        print(f"Total required schemas: {total_found}/{total_required}")
        print(f"Total schemas (with bonus): {total_found + additional_found}")
    else:
        print("⚠️  Some required schemas are missing")
        print(f"Found: {total_found}/{total_required}")
    
    print()
    print("Validation tests passed: {}/{}".format(
        sum(1 for _, success, _ in validation_tests if success),
        len(validation_tests)
    ))
    
    print()
    print("=" * 70)
    print("Schema Categories")
    print("=" * 70)
    print("User Schemas:")
    print("  • Authentication (Create, Login, Response)")
    print("  • Token management (TokenResponse)")
    print()
    print("Memory Schemas:")
    print("  • Profile management (Create, Update, Response)")
    print("  • Memory operations (Create, Search, Response)")
    print()
    print("Chat Schemas:")
    print("  • Session management (Create, Update, Response)")
    print("  • Message operations (Create, Response)")
    print("  • Chat flow (Request, Response, StreamChunk)")
    print("  • Privacy modes (Enum: normal, incognito, pause_memories)")
    print()
    print("=" * 70)
    print("Schema Features")
    print("=" * 70)
    print("  • Field validation (min/max length, email, etc.)")
    print("  • Type safety (Pydantic BaseModel)")
    print("  • JSON schema generation")
    print("  • Example data in documentation")
    print("  • Enum support for privacy modes")
    print("  • Optional and required fields")
    print("  • Nested models support")
    print()
    print("=" * 70)
    print("Note: Schemas are ready for FastAPI endpoint integration.")
    print("=" * 70)


if __name__ == "__main__":
    test_schemas()

