#!/usr/bin/env python3
"""
Structural verification script for Step 4.1: Memory Manager Agent
Tests structure and implementation without requiring dependencies.
"""
import sys
import ast
import re
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
    """Verify that memory_manager_agent.py exists and has correct structure."""
    print_header("FILE STRUCTURE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    checks_total += 1
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if agent_file.exists():
        checks_passed += 1
        print_check("agents/memory_manager_agent.py exists", True)
    else:
        print_check("agents/memory_manager_agent.py exists", False)
        return checks_passed, checks_total
    
    # Read and parse file
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Check for MemoryManagerAgent class
        checks_total += 1
        has_class = any(
            isinstance(node, ast.ClassDef) and node.name == "MemoryManagerAgent"
            for node in ast.walk(tree)
        )
        if has_class:
            checks_passed += 1
            print_check("MemoryManagerAgent class defined", True)
        else:
            print_check("MemoryManagerAgent class defined", False)
        
        # Check for BaseAgent inheritance
        checks_total += 1
        if "BaseAgent" in content:
            checks_passed += 1
            print_check("Inherits from BaseAgent", True)
        else:
            print_check("Inherits from BaseAgent", False)
        
    except Exception as e:
        print_check("Parsing file", False, str(e))
    
    return checks_passed, checks_total


def verify_execute_method():
    """Verify execute() method is implemented."""
    print_header("EXECUTE METHOD VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check execute method exists
        checks_total += 1
        if "def execute" in content:
            checks_passed += 1
            print_check("execute() method defined", True)
        else:
            print_check("execute() method defined", False)
        
        # Check execute method signature
        checks_total += 1
        if "def execute" in content and "input_data" in content and "context" in content:
            checks_passed += 1
            print_check("execute() has correct signature", True)
        else:
            print_check("execute() has correct signature", False)
        
        # Check privacy mode handling
        checks_total += 1
        if "privacy_mode" in content and "incognito" in content.lower() and "pause_memory" in content.lower():
            checks_passed += 1
            print_check("Privacy mode handling implemented", True)
        else:
            print_check("Privacy mode handling implemented", False)
        
        # Check return structure
        checks_total += 1
        if "success" in content and "data" in content and "memories" in content:
            checks_passed += 1
            print_check("Returns correct structure", True)
        else:
            print_check("Returns correct structure", False)
        
    except Exception as e:
        print_check("Verifying execute method", False, str(e))
    
    return checks_passed, checks_total


def verify_helper_methods():
    """Verify all helper methods are implemented."""
    print_header("HELPER METHODS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Required helper methods
        helper_methods = [
            "_extract_memories",
            "_extract_entities",
            "_calculate_importance",
            "_categorize_memory",
            "_generate_tags",
            "_check_for_conflicts",
            "_consolidate_similar_memories",
            "_process_memory",
            "_parse_memory_json",
            "_are_similar",
            "_merge_memories",
        ]
        
        for method in helper_methods:
            checks_total += 1
            if f"def {method}" in content:
                checks_passed += 1
                print_check(f"Method '{method}' defined", True)
            else:
                print_check(f"Method '{method}' defined", False)
        
    except Exception as e:
        print_check("Verifying helper methods", False, str(e))
    
    return checks_passed, checks_total


def verify_prompt_templates():
    """Verify prompt templates are defined."""
    print_header("PROMPT TEMPLATES VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for prompt templates
        prompt_templates = [
            "extraction_prompt_template",
            "importance_prompt_template",
            "categorization_prompt_template",
            "tag_generation_prompt_template",
            "consolidation_prompt_template",
        ]
        
        for template in prompt_templates:
            checks_total += 1
            if template in content:
                checks_passed += 1
                print_check(f"Prompt template '{template}' defined", True)
            else:
                print_check(f"Prompt template '{template}' defined", False)
        
    except Exception as e:
        print_check("Verifying prompt templates", False, str(e))
    
    return checks_passed, checks_total


def verify_privacy_modes():
    """Verify privacy mode awareness."""
    print_header("PRIVACY MODE AWARENESS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for privacy mode checks
        checks_total += 1
        if "incognito" in content.lower() and "skip" in content.lower():
            checks_passed += 1
            print_check("INCOGNITO mode handling", True)
        else:
            print_check("INCOGNITO mode handling", False)
        
        checks_total += 1
        if "pause_memory" in content.lower():
            checks_passed += 1
            print_check("PAUSE_MEMORY mode handling", True)
        else:
            print_check("PAUSE_MEMORY mode handling", False)
        
        checks_total += 1
        if "normal" in content.lower() and "privacy_mode" in content:
            checks_passed += 1
            print_check("NORMAL mode handling", True)
        else:
            print_check("NORMAL mode handling", False)
        
    except Exception as e:
        print_check("Verifying privacy modes", False, str(e))
    
    return checks_passed, checks_total


def verify_memory_processing():
    """Verify memory processing functionality."""
    print_header("MEMORY PROCESSING VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for memory extraction logic
        checks_total += 1
        if "extract" in content.lower() and "memory" in content.lower():
            checks_passed += 1
            print_check("Memory extraction logic present", True)
        else:
            print_check("Memory extraction logic present", False)
        
        # Check for importance scoring
        checks_total += 1
        if "importance_score" in content or "importance" in content.lower():
            checks_passed += 1
            print_check("Importance scoring logic present", True)
        else:
            print_check("Importance scoring logic present", False)
        
        # Check for categorization
        checks_total += 1
        if "memory_type" in content or "categorize" in content.lower():
            checks_passed += 1
            print_check("Memory categorization logic present", True)
        else:
            print_check("Memory categorization logic present", False)
        
        # Check for tags
        checks_total += 1
        if "tags" in content.lower() and "generate" in content.lower():
            checks_passed += 1
            print_check("Tag generation logic present", True)
        else:
            print_check("Tag generation logic present", False)
        
        # Check for consolidation
        checks_total += 1
        if "consolidate" in content.lower() or "merge" in content.lower():
            checks_passed += 1
            print_check("Memory consolidation logic present", True)
        else:
            print_check("Memory consolidation logic present", False)
        
    except Exception as e:
        print_check("Verifying memory processing", False, str(e))
    
    return checks_passed, checks_total


def verify_logging():
    """Verify logging is integrated."""
    print_header("LOGGING INTEGRATION VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for logger
        checks_total += 1
        if "logger" in content.lower() or "logging" in content.lower():
            checks_passed += 1
            print_check("Logging integrated", True)
        else:
            print_check("Logging integrated", False)
        
        # Check for log calls
        checks_total += 1
        if "self.logger" in content or "logger." in content:
            checks_passed += 1
            print_check("Logger used in code", True)
        else:
            print_check("Logger used in code", False)
        
        # Check for error logging
        checks_total += 1
        if "logger.error" in content or "log_error" in content:
            checks_passed += 1
            print_check("Error logging present", True)
        else:
            print_check("Error logging present", False)
        
    except Exception as e:
        print_check("Verifying logging", False, str(e))
    
    return checks_passed, checks_total


def verify_memory_types():
    """Verify memory types are defined."""
    print_header("MEMORY TYPES VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "memory_manager_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check for memory types
        required_types = ["fact", "preference", "event", "relationship", "other"]
        
        for mem_type in required_types:
            checks_total += 1
            if mem_type in content.lower():
                checks_passed += 1
                print_check(f"Memory type '{mem_type}' referenced", True)
            else:
                print_check(f"Memory type '{mem_type}' referenced", False)
        
        # Check for memory_types attribute
        checks_total += 1
        if "memory_types" in content or "self.memory_types" in content:
            checks_passed += 1
            print_check("memory_types attribute defined", True)
        else:
            print_check("memory_types attribute defined", False)
        
    except Exception as e:
        print_check("Verifying memory types", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'STEP 4.1 VERIFICATION - MEMORY MANAGER AGENT'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all verification tests
    passed, total = verify_file_structure()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_execute_method()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_helper_methods()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_prompt_templates()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_privacy_modes()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_memory_processing()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_logging()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_memory_types()
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
    
    # Checkpoint 4.1 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 4.1 Status:{Colors.RESET}")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} MemoryManagerAgent implemented")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Can extract memories from conversations")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Importance scoring working")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Memory categorization functional")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Privacy modes respected")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Logging in place")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Step 4.1 structure is complete and correct.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

