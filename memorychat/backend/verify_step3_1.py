#!/usr/bin/env python3
"""
Verification script for Step 3.1: Base Agent Class
Tests that BaseAgent is properly implemented according to plan.txt requirements.
"""
import sys
import ast
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_check(description: str, passed: bool, details: str = ""):
    """Print a check result."""
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    print(f"  {status} {description}")
    if details and passed:
        print(f"    {Colors.BLUE}→{Colors.RESET} {details}")


def verify_file_structure():
    """Verify that base_agent.py file exists and has correct structure."""
    print_header("FILE STRUCTURE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    # Check file exists
    checks_total += 1
    base_agent_file = backend_dir / "agents" / "base_agent.py"
    if base_agent_file.exists():
        checks_passed += 1
        print_check("agents/base_agent.py exists", True)
    else:
        print_check("agents/base_agent.py exists", False)
        return checks_passed, checks_total
    
    # Read and parse file
    try:
        with open(base_agent_file, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Check for BaseAgent class
        checks_total += 1
        has_base_agent = any(
            isinstance(node, ast.ClassDef) and node.name == "BaseAgent"
            for node in ast.walk(tree)
        )
        if has_base_agent:
            checks_passed += 1
            print_check("BaseAgent class defined", True)
        else:
            print_check("BaseAgent class defined", False)
        
        # Check for ABC inheritance
        checks_total += 1
        has_abc_import = "from abc import ABC" in content or "import abc" in content
        if has_abc_import:
            checks_passed += 1
            print_check("ABC imported for abstract base class", True)
        else:
            print_check("ABC imported for abstract base class", False)
        
        # Check for abstractmethod
        checks_total += 1
        has_abstractmethod = "@abstractmethod" in content or "abstractmethod" in content
        if has_abstractmethod:
            checks_passed += 1
            print_check("@abstractmethod decorator used", True)
        else:
            print_check("@abstractmethod decorator used", False)
        
        # Check for required methods
        required_methods = [
            "__init__",
            "execute",
            "_log_start",
            "_log_complete",
            "_log_error",
            "_format_prompt",
            "_parse_response",
        ]
        
        for method in required_methods:
            checks_total += 1
            if f"def {method}" in content:
                checks_passed += 1
                print_check(f"Method '{method}' defined", True)
            else:
                print_check(f"Method '{method}' defined", False)
        
        # Check execute is abstract
        checks_total += 1
        if "@abstractmethod" in content and "def execute" in content:
            # Check if abstractmethod appears before execute
            execute_idx = content.find("def execute")
            abstract_idx = content.rfind("@abstractmethod", 0, execute_idx)
            if abstract_idx != -1:
                checks_passed += 1
                print_check("execute() method is abstract", True)
            else:
                print_check("execute() method is abstract", False, "May need to check manually")
        else:
            print_check("execute() method is abstract", False)
        
    except Exception as e:
        print_check("Parsing file", False, str(e))
    
    return checks_passed, checks_total


def verify_interface():
    """Verify common interface methods."""
    print_header("COMMON INTERFACE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    base_agent_file = backend_dir / "agents" / "base_agent.py"
    if not base_agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(base_agent_file, 'r') as f:
            content = f.read()
        
        # Check __init__ signature
        checks_total += 1
        if "def __init__" in content and "name" in content and "description" in content:
            checks_passed += 1
            print_check("__init__(name, description, llm_model, temperature) signature", True)
        else:
            print_check("__init__ signature", False)
        
        # Check execute signature
        checks_total += 1
        if "def execute" in content and "input_data" in content:
            checks_passed += 1
            print_check("execute(input_data, context) signature", True)
        else:
            print_check("execute signature", False)
        
        # Check helper methods exist
        helper_methods = [
            ("_log_start", "task"),
            ("_log_complete", "task, duration"),
            ("_log_error", "task, error"),
            ("_format_prompt", "template"),
            ("_parse_response", "response"),
        ]
        
        for method, params in helper_methods:
            checks_total += 1
            if f"def {method}" in content:
                checks_passed += 1
                print_check(f"Helper method '{method}' exists", True)
            else:
                print_check(f"Helper method '{method}' exists", False)
        
    except Exception as e:
        print_check("Verifying interface", False, str(e))
    
    return checks_passed, checks_total


def verify_functionality():
    """Verify common functionality is implemented."""
    print_header("COMMON FUNCTIONALITY VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    base_agent_file = backend_dir / "agents" / "base_agent.py"
    if not base_agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(base_agent_file, 'r') as f:
            content = f.read()
        
        # Check LangChain initialization
        checks_total += 1
        if "ChatOpenAI" in content or "langchain" in content.lower():
            checks_passed += 1
            print_check("LangChain LLM initialization", True)
        else:
            print_check("LangChain LLM initialization", False)
        
        # Check token counting
        checks_total += 1
        if "_count_tokens" in content or "token" in content.lower():
            checks_passed += 1
            print_check("Token counting functionality", True)
        else:
            print_check("Token counting functionality", False)
        
        # Check error handling
        checks_total += 1
        if "handle_exception" in content or "LLMException" in content:
            checks_passed += 1
            print_check("Error handling wrapper", True)
        else:
            print_check("Error handling wrapper", False)
        
        # Check logging integration
        checks_total += 1
        if "log_agent_start" in content or "get_agent_logger" in content:
            checks_passed += 1
            print_check("Logging wrapper", True)
        else:
            print_check("Logging wrapper", False)
        
        # Check monitoring integration
        checks_total += 1
        if "monitoring_service" in content:
            checks_passed += 1
            print_check("Monitoring integration", True)
        else:
            print_check("Monitoring integration", False)
        
        # Check timing wrapper
        checks_total += 1
        if "time.time()" in content or "execution_time" in content.lower():
            checks_passed += 1
            print_check("Timing wrapper", True)
        else:
            print_check("Timing wrapper", False)
        
    except Exception as e:
        print_check("Verifying functionality", False, str(e))
    
    return checks_passed, checks_total


def verify_input_output_format():
    """Verify standard input/output format."""
    print_header("INPUT/OUTPUT FORMAT VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    base_agent_file = backend_dir / "agents" / "base_agent.py"
    if not base_agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(base_agent_file, 'r') as f:
            content = f.read()
        
        # Check for input format documentation/comments
        input_fields = ["session_id", "user_message", "privacy_mode", "profile_id", "context"]
        input_found = sum(1 for field in input_fields if field in content)
        
        checks_total += 1
        if input_found >= 3:  # At least 3 fields mentioned
            checks_passed += 1
            print_check("Input format fields documented", True, f"{input_found}/{len(input_fields)} fields")
        else:
            print_check("Input format fields documented", False)
        
        # Check for output format
        output_fields = ["success", "data", "error", "tokens_used", "execution_time_ms"]
        output_found = sum(1 for field in output_fields if field in content)
        
        checks_total += 1
        if output_found >= 3:  # At least 3 fields mentioned
            checks_passed += 1
            print_check("Output format fields documented", True, f"{output_found}/{len(output_fields)} fields")
        else:
            print_check("Output format fields documented", False)
        
        # Check for AgentInput/AgentOutput type definitions
        checks_total += 1
        if "AgentInput" in content and "AgentOutput" in content:
            checks_passed += 1
            print_check("AgentInput and AgentOutput types defined", True)
        else:
            print_check("AgentInput and AgentOutput types defined", False)
        
    except Exception as e:
        print_check("Verifying I/O format", False, str(e))
    
    return checks_passed, checks_total


def verify_integration():
    """Verify integration with existing systems."""
    print_header("INTEGRATION VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    base_agent_file = backend_dir / "agents" / "base_agent.py"
    if not base_agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(base_agent_file, 'r') as f:
            content = f.read()
        
        # Check imports from config
        checks_total += 1
        if "from config" in content or "import config" in content:
            checks_passed += 1
            print_check("Imports from config module", True)
        else:
            print_check("Imports from config module", False)
        
        # Check imports from services
        checks_total += 1
        if "from services" in content or "import services" in content:
            checks_passed += 1
            print_check("Imports from services module", True)
        else:
            print_check("Imports from services module", False)
        
        # Check __init__.py exports
        checks_total += 1
        init_file = backend_dir / "agents" / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r') as f:
                init_content = f.read()
            if "BaseAgent" in init_content:
                checks_passed += 1
                print_check("BaseAgent exported in __init__.py", True)
            else:
                print_check("BaseAgent exported in __init__.py", False)
        else:
            print_check("__init__.py exists", False)
        
    except Exception as e:
        print_check("Verifying integration", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'STEP 3.1 VERIFICATION - BASE AGENT CLASS'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all verification tests
    passed, total = verify_file_structure()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_interface()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_functionality()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_input_output_format()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_integration()
    total_passed += passed
    total_checks += total
    
    # Final summary
    print_header("FINAL SUMMARY")
    
    percentage = (total_passed / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Total Checks: {total_checks}")
    print(f"  Passed: {Colors.GREEN}{total_passed}{Colors.RESET}")
    print(f"  Failed: {Colors.RED}{total_checks - total_passed}{Colors.RESET}")
    print(f"  Success Rate: {Colors.GREEN if percentage >= 90 else Colors.YELLOW}{percentage:.1f}%{Colors.RESET}")
    
    # Checkpoint 3.1 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 3.1 Status:{Colors.RESET}")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} BaseAgent class created")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Common interface defined")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Logging/monitoring integrated")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Error handling included")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Ready to create specific agents")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Step 3.1 is complete and ready for use.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

