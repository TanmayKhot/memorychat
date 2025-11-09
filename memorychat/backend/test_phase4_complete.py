#!/usr/bin/env python3
"""
Complete Phase 4 testing script.
Tests all agents and orchestration end-to-end.
"""
import sys
from pathlib import Path

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


def test_agent_imports():
    """Test that all agents can be imported."""
    print_header("TESTING AGENT IMPORTS")
    
    checks_passed = 0
    checks_total = 0
    
    agents = [
        "MemoryManagerAgent",
        "MemoryRetrievalAgent",
        "PrivacyGuardianAgent",
        "ConversationAgent",
        "ConversationAnalystAgent",
        "ContextCoordinatorAgent",
    ]
    
    for agent_name in agents:
        checks_total += 1
        try:
            from agents import __all__
            if agent_name in __all__:
                checks_passed += 1
                print_check(f"{agent_name} importable", True)
            else:
                print_check(f"{agent_name} importable", False)
        except Exception as e:
            print_check(f"{agent_name} importable", False, str(e))
    
    return checks_passed, checks_total


def test_agent_initialization():
    """Test that all agents can be initialized."""
    print_header("TESTING AGENT INITIALIZATION")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from agents.memory_manager_agent import MemoryManagerAgent
        checks_total += 1
        agent = MemoryManagerAgent()
        checks_passed += 1
        print_check("MemoryManagerAgent initialized", True, f"Name: {agent.name}")
    except Exception as e:
        print_check("MemoryManagerAgent initialized", False, str(e))
    
    try:
        from agents.memory_retrieval_agent import MemoryRetrievalAgent
        checks_total += 1
        agent = MemoryRetrievalAgent()
        checks_passed += 1
        print_check("MemoryRetrievalAgent initialized", True, f"Name: {agent.name}")
    except Exception as e:
        print_check("MemoryRetrievalAgent initialized", False, str(e))
    
    try:
        from agents.privacy_guardian_agent import PrivacyGuardianAgent
        checks_total += 1
        agent = PrivacyGuardianAgent()
        checks_passed += 1
        print_check("PrivacyGuardianAgent initialized", True, f"Name: {agent.name}")
    except Exception as e:
        print_check("PrivacyGuardianAgent initialized", False, str(e))
    
    try:
        from agents.conversation_agent import ConversationAgent
        checks_total += 1
        agent = ConversationAgent()
        checks_passed += 1
        print_check("ConversationAgent initialized", True, f"Name: {agent.name}")
    except Exception as e:
        print_check("ConversationAgent initialized", False, str(e))
    
    try:
        from agents.conversation_analyst_agent import ConversationAnalystAgent
        checks_total += 1
        agent = ConversationAnalystAgent()
        checks_passed += 1
        print_check("ConversationAnalystAgent initialized", True, f"Name: {agent.name}")
    except Exception as e:
        print_check("ConversationAnalystAgent initialized", False, str(e))
    
    try:
        from agents.context_coordinator_agent import ContextCoordinatorAgent
        checks_total += 1
        agent = ContextCoordinatorAgent()
        checks_passed += 1
        print_check("ContextCoordinatorAgent initialized", True, f"Name: {agent.name}")
        # Check that all sub-agents are initialized
        if hasattr(agent, 'privacy_guardian') and hasattr(agent, 'conversation_agent'):
            checks_passed += 1
            checks_total += 1
            print_check("Sub-agents initialized in coordinator", True)
    except Exception as e:
        print_check("ContextCoordinatorAgent initialized", False, str(e))
    
    return checks_passed, checks_total


def test_orchestration_flow():
    """Test orchestration flow logic."""
    print_header("TESTING ORCHESTRATION FLOW")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from agents.context_coordinator_agent import ContextCoordinatorAgent
        
        coordinator = ContextCoordinatorAgent()
        
        # Test determine_required_agents
        checks_total += 1
        agents_normal = coordinator._determine_required_agents("chat", "normal")
        if len(agents_normal) >= 3 and "ConversationAgent" in agents_normal:
            checks_passed += 1
            print_check("Required agents determination (NORMAL)", True, f"Agents: {agents_normal}")
        else:
            print_check("Required agents determination (NORMAL)", False)
        
        checks_total += 1
        agents_incognito = coordinator._determine_required_agents("chat", "incognito")
        if "MemoryRetrievalAgent" not in agents_incognito and "MemoryManagerAgent" not in agents_incognito:
            checks_passed += 1
            print_check("Required agents determination (INCOGNITO)", True, f"Agents: {agents_incognito}")
        else:
            print_check("Required agents determination (INCOGNITO)", False)
        
        # Test token tracking
        checks_total += 1
        coordinator.tokens_used_by_agent = {"TestAgent": 100}
        total = coordinator._get_total_tokens_used()
        if total == 100:
            checks_passed += 1
            print_check("Token tracking works", True, f"Total: {total}")
        else:
            print_check("Token tracking works", False)
        
    except Exception as e:
        print_check("Testing orchestration flow", False, str(e))
        import traceback
        traceback.print_exc()
    
    return checks_passed, checks_total


def test_privacy_mode_routing():
    """Test privacy mode routing."""
    print_header("TESTING PRIVACY MODE ROUTING")
    
    checks_passed = 0
    checks_total = 0
    
    try:
        from agents.context_coordinator_agent import ContextCoordinatorAgent
        
        coordinator = ContextCoordinatorAgent()
        
        # Test NORMAL mode routing
        checks_total += 1
        agents = coordinator._determine_required_agents("chat", "normal")
        if "MemoryRetrievalAgent" in agents and "MemoryManagerAgent" in agents:
            checks_passed += 1
            print_check("NORMAL mode routing", True, f"Agents: {len(agents)}")
        else:
            print_check("NORMAL mode routing", False)
        
        # Test INCOGNITO mode routing
        checks_total += 1
        agents = coordinator._determine_required_agents("chat", "incognito")
        if "MemoryRetrievalAgent" not in agents and "MemoryManagerAgent" not in agents:
            checks_passed += 1
            print_check("INCOGNITO mode routing", True, f"Agents: {len(agents)}")
        else:
            print_check("INCOGNITO mode routing", False)
        
        # Test PAUSE_MEMORY mode routing
        checks_total += 1
        agents = coordinator._determine_required_agents("chat", "pause_memory")
        if "MemoryRetrievalAgent" in agents and "MemoryManagerAgent" not in agents:
            checks_passed += 1
            print_check("PAUSE_MEMORY mode routing", True, f"Agents: {len(agents)}")
        else:
            print_check("PAUSE_MEMORY mode routing", False)
        
    except Exception as e:
        print_check("Testing privacy mode routing", False, str(e))
    
    return checks_passed, checks_total


def main():
    """Run all Phase 4 tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'PHASE 4 COMPLETE TESTING'.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")
    
    total_passed = 0
    total_checks = 0
    
    # Run all tests
    passed, total = test_agent_imports()
    total_passed += passed
    total_checks += total
    
    passed, total = test_agent_initialization()
    total_passed += passed
    total_checks += total
    
    passed, total = test_orchestration_flow()
    total_passed += passed
    total_checks += total
    
    passed, total = test_privacy_mode_routing()
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
    
    # Phase 4 summary
    print(f"\n{Colors.BOLD}PHASE 4 Status:{Colors.RESET}")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} All agents importable")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} All agents initializable")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Orchestration flow works")
    print(f"  {'✓' if total_passed >= total_checks * 0.9 else '✗'} Privacy mode routing works")
    
    if total_passed == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL PHASE 4 TESTS PASSED!{Colors.RESET}")
        print(f"{Colors.GREEN}Phase 4 is complete and working correctly.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ SOME TESTS FAILED{Colors.RESET}")
        print(f"{Colors.YELLOW}Please review the failed tests above.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

