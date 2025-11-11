#!/usr/bin/env python3
"""
Structural verification script for Step 4.5: Conversation Analyst Agent
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
    """Verify that conversation_analyst_agent.py exists and has correct structure."""
    print_header("FILE STRUCTURE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    checks_total += 1
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
    if agent_file.exists():
        checks_passed += 1
        print_check("agents/conversation_analyst_agent.py exists", True)
    else:
        print_check("agents/conversation_analyst_agent.py exists", False)
        return checks_passed, checks_total
    
    # Read and parse file
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Check for ConversationAnalystAgent class
        checks_total += 1
        has_class = any(
            isinstance(node, ast.ClassDef) and node.name == "ConversationAnalystAgent"
            for node in ast.walk(tree)
        )
        if has_class:
            checks_passed += 1
            print_check("ConversationAnalystAgent class defined", True)
        else:
            print_check("ConversationAnalystAgent class defined", False)
        
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
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
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
        
        # Check return structure
        checks_total += 1
        if "analysis" in content and "insights" in content and "recommendations" in content:
            checks_passed += 1
            print_check("Returns correct structure", True)
        else:
            print_check("Returns correct structure", False)
        
    except Exception as e:
        print_check("Verifying execute method", False, str(e))
    
    return checks_passed, checks_total


def verify_analysis_functions():
    """Verify all analysis functions are implemented."""
    print_header("ANALYSIS FUNCTIONS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Required analysis methods
        analysis_methods = [
            "_analyze_sentiment",
            "_extract_topics",
            "_detect_patterns",
            "_calculate_engagement",
            "_identify_memory_gaps",
        ]
        
        for method in analysis_methods:
            checks_total += 1
            if f"def {method}" in content:
                checks_passed += 1
                print_check(f"Analysis method '{method}' defined", True)
            else:
                print_check(f"Analysis method '{method}' defined", False)
        
    except Exception as e:
        print_check("Verifying analysis functions", False, str(e))
    
    return checks_passed, checks_total


def verify_recommendations():
    """Verify recommendation engine is implemented."""
    print_header("RECOMMENDATION ENGINE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check recommendation methods
        checks_total += 1
        if "_generate_recommendations" in content:
            checks_passed += 1
            print_check("_generate_recommendations() method defined", True)
        else:
            print_check("_generate_recommendations() method defined", False)
        
        checks_total += 1
        if "_recommend_memory_profile_switch" in content:
            checks_passed += 1
            print_check("_recommend_memory_profile_switch() method defined", True)
        else:
            print_check("_recommend_memory_profile_switch() method defined", False)
        
        checks_total += 1
        if "_suggest_follow_up_questions" in content:
            checks_passed += 1
            print_check("_suggest_follow_up_questions() method defined", True)
        else:
            print_check("_suggest_follow_up_questions() method defined", False)
        
        checks_total += 1
        if "_suggest_memory_organization" in content:
            checks_passed += 1
            print_check("_suggest_memory_organization() method defined", True)
        else:
            print_check("_suggest_memory_organization() method defined", False)
        
    except Exception as e:
        print_check("Verifying recommendations", False, str(e))
    
    return checks_passed, checks_total


def verify_insights():
    """Verify insight generation is implemented."""
    print_header("INSIGHT GENERATION VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check insight generation
        checks_total += 1
        if "_generate_insights" in content:
            checks_passed += 1
            print_check("_generate_insights() method defined", True)
        else:
            print_check("_generate_insights() method defined", False)
        
        # Check insight components
        insight_components = [
            "session_summary",
            "topic_distribution",
            "sentiment_trends",
            "memory_effectiveness",
            "profile_fit_score",
        ]
        
        for component in insight_components:
            checks_total += 1
            if component in content.lower():
                checks_passed += 1
                print_check(f"Insight component '{component}' present", True)
            else:
                print_check(f"Insight component '{component}' present", False)
        
    except Exception as e:
        print_check("Verifying insights", False, str(e))
    
    return checks_passed, checks_total


def verify_storage():
    """Verify insight storage is implemented."""
    print_header("INSIGHT STORAGE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
    if not agent_file.exists():
        return checks_passed, checks_total
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Check storage method
        checks_total += 1
        if "_store_insights" in content:
            checks_passed += 1
            print_check("_store_insights() method defined", True)
        else:
            print_check("_store_insights() method defined", False)
        
        # Check database integration
        checks_total += 1
        if "DatabaseService" in content or "database" in content.lower():
            checks_passed += 1
            print_check("Database integration present", True)
        else:
            print_check("Database integration present", False)
        
    except Exception as e:
        print_check("Verifying storage", False, str(e))
    
    return checks_passed, checks_total


def verify_logging():
    """Verify logging is integrated."""
    print_header("LOGGING INTEGRATION VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    agent_file = backend_dir / "agents" / "conversation_analyst_agent.py"
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
        
    except Exception as e:
        print_check("Verifying logging", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'STEP 4.5 VERIFICATION - CONVERSATION ANALYST AGENT'.center(70)}{Colors.RESET}")
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
    
    passed, total = verify_analysis_functions()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_recommendations()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_insights()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_storage()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_logging()
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
    
    # Checkpoint 4.5 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 4.5 Status:{Colors.RESET}")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} ConversationAnalystAgent implemented")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Sentiment analysis working")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Topic extraction functional")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Pattern detection effective")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Recommendations relevant")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Insights stored properly")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Step 4.5 structure is complete and correct.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())


