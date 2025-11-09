#!/usr/bin/env python3
"""
Verification script for Step 5.5: API Documentation
Verifies documentation is complete and OpenAPI schema generates correctly.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

checks_passed = 0
checks_total = 0


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(name: str, passed: bool, details: str = ""):
    """Print check result."""
    global checks_passed, checks_total
    checks_total += 1
    status = "✓" if passed else "✗"
    print(f"  {status} {name}")
    if details:
        print(f"    {details}")
    if passed:
        checks_passed += 1


def verify_openapi_schema():
    """Verify OpenAPI schema generates correctly."""
    print_header("VERIFYING OPENAPI SCHEMA")
    
    try:
        # Try to activate virtual environment if it exists
        venv_path = backend_dir / ".venv"
        if venv_path.exists():
            import sys
            venv_site_packages = venv_path / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
            if venv_site_packages.exists() and str(venv_site_packages) not in sys.path:
                sys.path.insert(0, str(venv_site_packages))
        
        from main import app
        
        # Generate OpenAPI schema
        schema = app.openapi()
        
        # Check basic structure
        has_info = "info" in schema
        print_check("OpenAPI schema has info section", has_info)
        
        has_paths = "paths" in schema
        print_check("OpenAPI schema has paths section", has_paths)
        
        if has_paths:
            path_count = len(schema["paths"])
            print_check(f"OpenAPI schema has {path_count} paths", path_count > 0, f"Found {path_count} paths")
        
        # Check for tags
        has_tags = "tags" in schema
        print_check("OpenAPI schema has tags", has_tags)
        
        if has_tags:
            tag_count = len(schema["tags"])
            print_check(f"OpenAPI schema has {tag_count} tags", tag_count > 0, f"Found {tag_count} tags")
        
        # Check main.py configuration
        has_title = schema.get("info", {}).get("title") == "MemoryChat Multi-Agent API"
        print_check("API title configured correctly", has_title)
        
        has_description = "description" in schema.get("info", {})
        print_check("API description present", has_description)
        
        has_version = schema.get("info", {}).get("version") == "1.0.0"
        print_check("API version configured", has_version)
        
        return True
        
    except ImportError as e:
        if "fastapi" in str(e).lower():
            print_check("OpenAPI schema generation", False,
                       f"Dependencies not installed. Run: pip install -r requirements.txt")
        else:
            print_check("OpenAPI schema generation", False, str(e))
        return False
    except Exception as e:
        print_check("OpenAPI schema generation", False, str(e))
        import traceback
        traceback.print_exc()
        return False


def verify_endpoint_documentation():
    """Verify endpoints have documentation."""
    print_header("VERIFYING ENDPOINT DOCUMENTATION")
    
    endpoint_files = [
        "api/endpoints/users.py",
        "api/endpoints/memory_profiles.py",
        "api/endpoints/sessions.py",
        "api/endpoints/chat.py",
        "api/endpoints/memories.py",
        "api/endpoints/analytics.py",
    ]
    
    for file_path in endpoint_files:
        file = backend_dir / file_path
        if file.exists():
            with open(file, 'r') as f:
                content = f.read()
            
            # Check for docstrings
            has_docstring = '"""' in content or "'''" in content
            print_check(f"{file_path} has docstrings", has_docstring)
        else:
            print_check(f"{file_path} exists", False)


def verify_model_examples():
    """Verify Pydantic models have examples."""
    print_header("VERIFYING MODEL EXAMPLES")
    
    models_file = backend_dir / "models" / "api_models.py"
    if not models_file.exists():
        print_check("api_models.py exists", False)
        return False
    
    print_check("api_models.py exists", True)
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Check for examples in key models
    key_models = [
        "CreateUserRequest",
        "CreateMemoryProfileRequest",
        "SendMessageRequest",
        "ChatResponse",
    ]
    
    for model in key_models:
        # Check for examples field or json_schema_extra
        # Look for the model class definition and check for examples nearby
        model_pattern = f"class {model}"
        if model_pattern in content:
            # Find the model class and check for examples in its Config or Field definitions
            model_start = content.find(model_pattern)
            # Look for examples in the next 200 lines after class definition
            model_section = content[model_start:model_start+2000]
            has_examples = ("examples=" in model_section or "json_schema_extra" in model_section or '"example"' in model_section)
            print_check(f"{model} has examples", has_examples)
        else:
            print_check(f"{model} class found", False)
    
    return True


def verify_main_documentation():
    """Verify main.py has documentation configuration."""
    print_header("VERIFYING MAIN.PY DOCUMENTATION")
    
    main_file = backend_dir / "main.py"
    if not main_file.exists():
        print_check("main.py exists", False)
        return False
    
    print_check("main.py exists", True)
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Check for FastAPI configuration
    has_title = 'title="MemoryChat Multi-Agent API"' in content
    print_check("FastAPI title configured", has_title)
    
    has_description = 'description=' in content
    print_check("FastAPI description configured", has_description)
    
    has_tags = "openapi_tags" in content
    print_check("OpenAPI tags configured", has_tags)
    
    has_docs_url = 'docs_url="/docs"' in content
    print_check("Docs URL configured", has_docs_url)
    
    return True


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  STEP 5.5 VERIFICATION: API DOCUMENTATION")
    print("=" * 70)
    
    verify_main_documentation()
    verify_endpoint_documentation()
    verify_model_examples()
    
    # Try OpenAPI schema if possible
    try:
        verify_openapi_schema()
    except Exception as e:
        print(f"\n  Note: OpenAPI schema verification skipped (dependencies may not be installed)")
        print(f"    Error: {str(e)}")
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    print(f"  Total Checks: {checks_total}")
    print(f"  Passed: {checks_passed}")
    print(f"  Failed: {checks_total - checks_passed}")
    
    if checks_passed == checks_total:
        print("\n  ✓ ALL CHECKS PASSED!")
        print("\n  To view the API documentation:")
        print("  1. Start the server: python main.py")
        print("  2. Open http://localhost:8000/docs in your browser")
        print("  3. Or view ReDoc at http://localhost:8000/redoc")
        return 0
    else:
        print("\n  ✗ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

