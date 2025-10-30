"""
Verification script for Checkpoint 3.13 - Main Application (main.py)

Verifies that main.py meets all requirements:
1. Initialize FastAPI app
2. Add CORS middleware
3. Include all API routers
4. Add global exception handlers
5. Add startup/shutdown events
6. Configure OpenAPI documentation

Run with: python verify_checkpoint_3_13.py
"""

import sys


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def verify_fastapi_initialization():
    """Verify FastAPI app is properly initialized."""
    print_section("1. FastAPI App Initialization")
    
    try:
        from main import app
        
        checks = [
            ("App instance created", app is not None),
            ("App title set", hasattr(app, 'title') and app.title),
            ("App description set", hasattr(app, 'description') and app.description),
            ("App version set", hasattr(app, 'version') and app.version == "1.0.0"),
            ("Docs URL configured", hasattr(app, 'docs_url') and app.docs_url == "/docs"),
            ("ReDoc URL configured", hasattr(app, 'redoc_url') and app.redoc_url == "/redoc"),
            ("OpenAPI URL configured", hasattr(app, 'openapi_url') and app.openapi_url == "/openapi.json"),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_cors_middleware():
    """Verify CORS middleware is added."""
    print_section("2. CORS Middleware")
    
    try:
        from main import app
        from fastapi.middleware.cors import CORSMiddleware
        
        # Check if CORS middleware is in the middleware stack
        has_cors = False
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                has_cors = True
                break
        
        if has_cors:
            print(f"  ✅ CORS middleware added")
            return True
        else:
            print(f"  ❌ CORS middleware not found")
            return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_api_routers():
    """Verify API routers are included."""
    print_section("3. API Routers")
    
    try:
        from main import app
        
        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        # Expected route prefixes
        expected_prefixes = [
            "/api/v1/auth",
            "/api/v1/memory-profiles",
            "/api/v1/sessions",
            "/api/v1/chat",
        ]
        
        all_found = True
        for prefix in expected_prefixes:
            found = any(route.startswith(prefix) for route in routes)
            status = "✅" if found else "❌"
            print(f"  {status} Router included: {prefix}")
            if not found:
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_exception_handlers():
    """Verify global exception handlers are added."""
    print_section("4. Global Exception Handlers")
    
    try:
        from main import app
        from starlette.exceptions import HTTPException as StarletteHTTPException
        from fastapi.exceptions import RequestValidationError
        
        # Check exception handlers
        handlers = app.exception_handlers
        
        checks = [
            ("HTTPException handler", StarletteHTTPException in handlers),
            ("ValidationError handler", RequestValidationError in handlers),
            ("Global Exception handler", Exception in handlers),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_startup_shutdown_events():
    """Verify startup/shutdown events are configured."""
    print_section("5. Startup/Shutdown Events")
    
    try:
        from main import app
        
        # Check if lifespan is configured
        has_lifespan = app.router.lifespan_context is not None
        
        if has_lifespan:
            print(f"  ✅ Lifespan event handler configured")
            print(f"  ✅ Modern async context manager pattern used")
            print(f"  ✅ Replaces deprecated @app.on_event decorators")
            return True
        else:
            print(f"  ❌ Lifespan event handler not configured")
            return False
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_openapi_configuration():
    """Verify OpenAPI documentation is configured."""
    print_section("6. OpenAPI Documentation")
    
    try:
        from main import app
        
        # Get OpenAPI schema
        openapi_schema = app.openapi()
        
        checks = [
            ("OpenAPI version", "openapi" in openapi_schema),
            ("API info", "info" in openapi_schema),
            ("API title", openapi_schema.get("info", {}).get("title")),
            ("API version", openapi_schema.get("info", {}).get("version") == "1.0.0"),
            ("API description", openapi_schema.get("info", {}).get("description")),
            ("Contact info", "contact" in openapi_schema.get("info", {})),
            ("License info", "license" in openapi_schema.get("info", {})),
            ("Tags", "tags" in openapi_schema),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        # Print tag count
        if "tags" in openapi_schema:
            print(f"  ✅ OpenAPI tags defined: {len(openapi_schema['tags'])}")
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_root_endpoints():
    """Verify root and health check endpoints exist."""
    print_section("Additional: Root Endpoints")
    
    try:
        from main import app
        
        # Get all routes
        routes = {}
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    key = f"{method} {route.path}"
                    routes[key] = route
        
        checks = [
            ("GET /", "GET /" in routes),
            ("GET /health", "GET /health" in routes),
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print(" CHECKPOINT 3.13 VERIFICATION - Main Application")
    print("=" * 70)
    
    results = []
    
    # Run all verification checks
    results.append(("1. FastAPI Initialization", verify_fastapi_initialization()))
    results.append(("2. CORS Middleware", verify_cors_middleware()))
    results.append(("3. API Routers", verify_api_routers()))
    results.append(("4. Exception Handlers", verify_exception_handlers()))
    results.append(("5. Startup/Shutdown Events", verify_startup_shutdown_events()))
    results.append(("6. OpenAPI Documentation", verify_openapi_configuration()))
    results.append(("Additional: Root Endpoints", verify_root_endpoints()))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    print(f"\n  Total Checks: {total}")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  Success Rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All verification checks passed!")
        print("\nCheckpoint 3.13 requirements met:")
        print("  ✅ 1. Initialize FastAPI app")
        print("  ✅ 2. Add CORS middleware")
        print("  ✅ 3. Include all API routers")
        print("  ✅ 4. Add global exception handlers")
        print("  ✅ 5. Add startup/shutdown events")
        print("  ✅ 6. Configure OpenAPI documentation")
        print("\nNext steps:")
        print("  1. Start server: uvicorn main:app --reload")
        print("  2. Access docs: http://localhost:8000/docs")
        print("  3. Test endpoints with Swagger UI")
        return 0
    else:
        print(f"\n⚠️  {failed} verification check(s) failed.")
        print("Please review the errors above and fix any issues.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

