#!/usr/bin/env python3
"""
Verification script for Step 3.2: Agent Configuration
Tests that agent configurations are properly defined according to plan.txt requirements.
"""
import sys
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


def verify_file_exists():
    """Verify that agent_config.py exists."""
    print_header("FILE STRUCTURE VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    checks_total += 1
    config_file = backend_dir / "config" / "agent_config.py"
    if config_file.exists():
        checks_passed += 1
        print_check("config/agent_config.py exists", True)
    else:
        print_check("config/agent_config.py exists", False)
        return checks_passed, checks_total
    
    return checks_passed, checks_total


def verify_agent_configurations():
    """Verify all agent configurations are defined."""
    print_header("AGENT CONFIGURATIONS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Import agent config
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_config",
            backend_dir / "config" / "agent_config.py"
        )
        agent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_config)
        
        CONVERSATION_AGENT = agent_config.CONVERSATION_AGENT
        MEMORY_MANAGER_AGENT = agent_config.MEMORY_MANAGER_AGENT
        MEMORY_RETRIEVAL_AGENT = agent_config.MEMORY_RETRIEVAL_AGENT
        PRIVACY_GUARDIAN_AGENT = agent_config.PRIVACY_GUARDIAN_AGENT
        CONVERSATION_ANALYST_AGENT = agent_config.CONVERSATION_ANALYST_AGENT
        CONTEXT_COORDINATOR_AGENT = agent_config.CONTEXT_COORDINATOR_AGENT
        
        agent_configs = {
            "ConversationAgent": CONVERSATION_AGENT,
            "MemoryManagerAgent": MEMORY_MANAGER_AGENT,
            "MemoryRetrievalAgent": MEMORY_RETRIEVAL_AGENT,
            "PrivacyGuardianAgent": PRIVACY_GUARDIAN_AGENT,
            "ConversationAnalystAgent": CONVERSATION_ANALYST_AGENT,
            "ContextCoordinatorAgent": CONTEXT_COORDINATOR_AGENT,
        }
        
        # Check each agent configuration
        for agent_name, config in agent_configs.items():
            checks_total += 1
            if isinstance(config, dict) and "name" in config:
                checks_passed += 1
                print_check(f"{agent_name} configuration exists", True)
            else:
                print_check(f"{agent_name} configuration exists", False)
            
            # Check required fields
            required_fields = ["name", "description"]
            for field in required_fields:
                checks_total += 1
                if field in config:
                    checks_passed += 1
                    print_check(f"{agent_name} has '{field}' field", True)
                else:
                    print_check(f"{agent_name} has '{field}' field", False)
            
            # Check model configuration
            checks_total += 1
            if "model" in config:
                checks_passed += 1
                print_check(f"{agent_name} has 'model' field", True)
            else:
                print_check(f"{agent_name} has 'model' field", False)
            
            # Check temperature (if model is not None)
            if config.get("model") is not None:
                checks_total += 1
                if "temperature" in config:
                    checks_passed += 1
                    print_check(f"{agent_name} has 'temperature' field", True)
                else:
                    print_check(f"{agent_name} has 'temperature' field", False)
            
            # Check system_prompt (if model is not None)
            if config.get("model") is not None:
                checks_total += 1
                if "system_prompt" in config:
                    checks_passed += 1
                    print_check(f"{agent_name} has 'system_prompt' field", True)
                else:
                    print_check(f"{agent_name} has 'system_prompt' field", False)
        
    except ImportError as e:
        print_check("Importing agent configurations", False, str(e))
        return checks_passed, checks_total
    
    return checks_passed, checks_total


def verify_model_selections():
    """Verify model selections are appropriate."""
    print_header("MODEL SELECTIONS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Import agent config
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_config",
            backend_dir / "config" / "agent_config.py"
        )
        agent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_config)
        
        CONVERSATION_AGENT = agent_config.CONVERSATION_AGENT
        MEMORY_MANAGER_AGENT = agent_config.MEMORY_MANAGER_AGENT
        MEMORY_RETRIEVAL_AGENT = agent_config.MEMORY_RETRIEVAL_AGENT
        PRIVACY_GUARDIAN_AGENT = agent_config.PRIVACY_GUARDIAN_AGENT
        CONVERSATION_ANALYST_AGENT = agent_config.CONVERSATION_ANALYST_AGENT
        CONTEXT_COORDINATOR_AGENT = agent_config.CONTEXT_COORDINATOR_AGENT
        
        # Check ConversationAgent uses gpt-4 (highest quality)
        checks_total += 1
        if CONVERSATION_AGENT.get("model") == "gpt-4":
            checks_passed += 1
            print_check("ConversationAgent uses gpt-4 (appropriate for main interaction)", True)
        else:
            print_check("ConversationAgent uses gpt-4", False, f"Found: {CONVERSATION_AGENT.get('model')}")
        
        # Check other agents use gpt-3.5-turbo (cost-effective)
        other_agents = [
            ("MemoryManagerAgent", MEMORY_MANAGER_AGENT),
            ("MemoryRetrievalAgent", MEMORY_RETRIEVAL_AGENT),
            ("PrivacyGuardianAgent", PRIVACY_GUARDIAN_AGENT),
            ("ConversationAnalystAgent", CONVERSATION_ANALYST_AGENT),
        ]
        
        for agent_name, config in other_agents:
            checks_total += 1
            model = config.get("model")
            if model == "gpt-3.5-turbo" or model is None:
                checks_passed += 1
                print_check(f"{agent_name} uses appropriate model", True, f"Model: {model}")
            else:
                print_check(f"{agent_name} uses appropriate model", False, f"Found: {model}")
        
        # Check ContextCoordinatorAgent is rule-based
        checks_total += 1
        if CONTEXT_COORDINATOR_AGENT.get("model") is None:
            checks_passed += 1
            print_check("ContextCoordinatorAgent is rule-based (no LLM)", True)
        else:
            print_check("ContextCoordinatorAgent is rule-based", False)
        
    except ImportError as e:
        print_check("Verifying model selections", False, str(e))
    
    return checks_passed, checks_total


def verify_temperature_settings():
    """Verify temperature settings are optimized."""
    print_header("TEMPERATURE SETTINGS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from config.agent_config import (
            CONVERSATION_AGENT,
            MEMORY_MANAGER_AGENT,
            MEMORY_RETRIEVAL_AGENT,
            PRIVACY_GUARDIAN_AGENT,
            CONVERSATION_ANALYST_AGENT,
        )
        
        # Check ConversationAgent has higher temperature (creative)
        checks_total += 1
        temp = CONVERSATION_AGENT.get("temperature")
        if temp is not None and 0.6 <= temp <= 0.8:
            checks_passed += 1
            print_check("ConversationAgent temperature optimized (0.6-0.8 for creativity)", True, f"Temperature: {temp}")
        else:
            print_check("ConversationAgent temperature optimized", False, f"Found: {temp}")
        
        # Check MemoryManagerAgent has lower temperature (precise)
        checks_total += 1
        temp = MEMORY_MANAGER_AGENT.get("temperature")
        if temp is not None and 0.2 <= temp <= 0.4:
            checks_passed += 1
            print_check("MemoryManagerAgent temperature optimized (0.2-0.4 for precision)", True, f"Temperature: {temp}")
        else:
            print_check("MemoryManagerAgent temperature optimized", False, f"Found: {temp}")
        
        # Check MemoryRetrievalAgent has low temperature (precise)
        checks_total += 1
        temp = MEMORY_RETRIEVAL_AGENT.get("temperature")
        if temp is not None and 0.1 <= temp <= 0.3:
            checks_passed += 1
            print_check("MemoryRetrievalAgent temperature optimized (0.1-0.3 for precision)", True, f"Temperature: {temp}")
        else:
            print_check("MemoryRetrievalAgent temperature optimized", False, f"Found: {temp}")
        
        # Check PrivacyGuardianAgent has temperature 0.0 (deterministic)
        checks_total += 1
        temp = PRIVACY_GUARDIAN_AGENT.get("temperature")
        if temp == 0.0:
            checks_passed += 1
            print_check("PrivacyGuardianAgent temperature optimized (0.0 for security)", True)
        else:
            print_check("PrivacyGuardianAgent temperature optimized", False, f"Found: {temp}")
        
        # Check ConversationAnalystAgent has moderate temperature
        checks_total += 1
        temp = CONVERSATION_ANALYST_AGENT.get("temperature")
        if temp is not None and 0.2 <= temp <= 0.4:
            checks_passed += 1
            print_check("ConversationAnalystAgent temperature optimized (0.2-0.4)", True, f"Temperature: {temp}")
        else:
            print_check("ConversationAnalystAgent temperature optimized", False, f"Found: {temp}")
        
    except ImportError as e:
        print_check("Verifying temperature settings", False, str(e))
    
    return checks_passed, checks_total


def verify_system_prompts():
    """Verify system prompts are created."""
    print_header("SYSTEM PROMPTS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Import agent config
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_config",
            backend_dir / "config" / "agent_config.py"
        )
        agent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_config)
        
        CONVERSATION_AGENT = agent_config.CONVERSATION_AGENT
        MEMORY_MANAGER_AGENT = agent_config.MEMORY_MANAGER_AGENT
        MEMORY_RETRIEVAL_AGENT = agent_config.MEMORY_RETRIEVAL_AGENT
        PRIVACY_GUARDIAN_AGENT = agent_config.PRIVACY_GUARDIAN_AGENT
        CONVERSATION_ANALYST_AGENT = agent_config.CONVERSATION_ANALYST_AGENT
        CONTEXT_COORDINATOR_AGENT = agent_config.CONTEXT_COORDINATOR_AGENT
        
        agents_with_prompts = [
            ("ConversationAgent", CONVERSATION_AGENT),
            ("MemoryManagerAgent", MEMORY_MANAGER_AGENT),
            ("MemoryRetrievalAgent", MEMORY_RETRIEVAL_AGENT),
            ("PrivacyGuardianAgent", PRIVACY_GUARDIAN_AGENT),
            ("ConversationAnalystAgent", CONVERSATION_ANALYST_AGENT),
        ]
        
        for agent_name, config in agents_with_prompts:
            checks_total += 1
            prompt = config.get("system_prompt")
            if prompt and isinstance(prompt, str) and len(prompt) > 20:
                checks_passed += 1
                print_check(f"{agent_name} has system prompt", True, f"Length: {len(prompt)} chars")
            else:
                print_check(f"{agent_name} has system prompt", False)
        
        # Check ContextCoordinatorAgent has None prompt (rule-based)
        checks_total += 1
        if CONTEXT_COORDINATOR_AGENT.get("system_prompt") is None:
            checks_passed += 1
            print_check("ContextCoordinatorAgent has None system_prompt (rule-based)", True)
        else:
            print_check("ContextCoordinatorAgent has None system_prompt", False)
        
    except ImportError as e:
        print_check("Verifying system prompts", False, str(e))
    
    return checks_passed, checks_total


def verify_token_budgets():
    """Verify token budgets and priorities are configured."""
    print_header("TOKEN BUDGETS AND PRIORITIES VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Import agent config
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_config",
            backend_dir / "config" / "agent_config.py"
        )
        agent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_config)
        
        AGENT_TOKEN_BUDGETS = agent_config.AGENT_TOKEN_BUDGETS
        AGENT_PRIORITIES = agent_config.AGENT_PRIORITIES
        TOTAL_TOKEN_BUDGET = agent_config.TOTAL_TOKEN_BUDGET
        get_token_budget = agent_config.get_token_budget
        get_agent_priority = agent_config.get_agent_priority
        
        # Check token budgets exist
        checks_total += 1
        if isinstance(AGENT_TOKEN_BUDGETS, dict) and len(AGENT_TOKEN_BUDGETS) > 0:
            checks_passed += 1
            print_check("AGENT_TOKEN_BUDGETS defined", True, f"{len(AGENT_TOKEN_BUDGETS)} agents")
        else:
            print_check("AGENT_TOKEN_BUDGETS defined", False)
        
        # Check priorities exist
        checks_total += 1
        if isinstance(AGENT_PRIORITIES, dict) and len(AGENT_PRIORITIES) > 0:
            checks_passed += 1
            print_check("AGENT_PRIORITIES defined", True, f"{len(AGENT_PRIORITIES)} agents")
        else:
            print_check("AGENT_PRIORITIES defined", False)
        
        # Check total token budget
        checks_total += 1
        if isinstance(TOTAL_TOKEN_BUDGET, int) and TOTAL_TOKEN_BUDGET > 0:
            checks_passed += 1
            print_check("TOTAL_TOKEN_BUDGET defined", True, f"{TOTAL_TOKEN_BUDGET} tokens")
        else:
            print_check("TOTAL_TOKEN_BUDGET defined", False)
        
        # Check helper functions exist
        checks_total += 1
        if callable(get_token_budget):
            checks_passed += 1
            print_check("get_token_budget() function exists", True)
        else:
            print_check("get_token_budget() function exists", False)
        
        checks_total += 1
        if callable(get_agent_priority):
            checks_passed += 1
            print_check("get_agent_priority() function exists", True)
        else:
            print_check("get_agent_priority() function exists", False)
        
        # Test helper functions
        checks_total += 1
        try:
            budget = get_token_budget("ConversationAgent")
            if isinstance(budget, int):
                checks_passed += 1
                print_check("get_token_budget() works correctly", True, f"ConversationAgent: {budget} tokens")
            else:
                print_check("get_token_budget() works correctly", False)
        except Exception as e:
            print_check("get_token_budget() works correctly", False, str(e))
        
    except ImportError as e:
        print_check("Verifying token budgets", False, str(e))
    
    return checks_passed, checks_total


def verify_helper_functions():
    """Verify helper functions are available."""
    print_header("HELPER FUNCTIONS VERIFICATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        # Import agent config
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "agent_config",
            backend_dir / "config" / "agent_config.py"
        )
        agent_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_config)
        
        get_agent_config = agent_config.get_agent_config
        get_all_agent_configs = agent_config.get_all_agent_configs
        validate_agent_config = agent_config.validate_agent_config
        validate_all_configs = agent_config.validate_all_configs
        is_agent_required = agent_config.is_agent_required
        is_agent_skippable = agent_config.is_agent_skippable
        
        helper_functions = [
            ("get_agent_config", get_agent_config),
            ("get_all_agent_configs", get_all_agent_configs),
            ("validate_agent_config", validate_agent_config),
            ("validate_all_configs", validate_all_configs),
            ("is_agent_required", is_agent_required),
            ("is_agent_skippable", is_agent_skippable),
        ]
        
        for func_name, func in helper_functions:
            checks_total += 1
            if callable(func):
                checks_passed += 1
                print_check(f"{func_name}() function exists", True)
            else:
                print_check(f"{func_name}() function exists", False)
        
        # Test get_agent_config
        checks_total += 1
        try:
            config = get_agent_config("ConversationAgent")
            if config and isinstance(config, dict):
                checks_passed += 1
                print_check("get_agent_config() works correctly", True)
            else:
                print_check("get_agent_config() works correctly", False)
        except Exception as e:
            print_check("get_agent_config() works correctly", False, str(e))
        
        # Test validation
        checks_total += 1
        try:
            results = validate_all_configs()
            if isinstance(results, dict) and len(results) > 0:
                all_valid = all(results.values())
                if all_valid:
                    checks_passed += 1
                    print_check("validate_all_configs() works correctly", True, "All configs valid")
                else:
                    print_check("validate_all_configs() works correctly", False, "Some configs invalid")
            else:
                print_check("validate_all_configs() works correctly", False)
        except Exception as e:
            print_check("validate_all_configs() works correctly", False, str(e))
        
    except ImportError as e:
        print_check("Verifying helper functions", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all verification tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'STEP 3.2 VERIFICATION - AGENT CONFIGURATION'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all verification tests
    passed, total = verify_file_exists()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_agent_configurations()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_model_selections()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_temperature_settings()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_system_prompts()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_token_budgets()
    total_passed += passed
    total_checks += total
    
    passed, total = verify_helper_functions()
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
    
    # Checkpoint 3.2 summary
    print(f"\n{Colors.BOLD}CHECKPOINT 3.2 Status:{Colors.RESET}")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} All agent configurations defined")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Model selections appropriate")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Temperature settings optimized")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} System prompts created")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Step 3.2 is complete and ready for use.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME CHECKS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed checks above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

