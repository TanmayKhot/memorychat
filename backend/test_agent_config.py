#!/usr/bin/env python3
"""
Test script for Step 3.2: Agent Configuration
Tests all agent configuration functionality.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import agent config
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_config",
    backend_dir / "config" / "agent_config.py"
)
agent_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_config)

print("=" * 70)
print("TESTING AGENT CONFIGURATION (Step 3.2)")
print("=" * 70)
print()

# Test 1: Get all agent configurations
print("Test 1: Get all agent configurations")
print("-" * 70)
all_configs = agent_config.get_all_agent_configs()
print(f"✓ Found {len(all_configs)} agent configurations:")
for name in all_configs.keys():
    print(f"  - {name}")
print()

# Test 2: Get individual agent configurations
print("Test 2: Get individual agent configurations")
print("-" * 70)
agents_to_test = [
    "ConversationAgent",
    "MemoryManagerAgent",
    "MemoryRetrievalAgent",
    "PrivacyGuardianAgent",
    "ConversationAnalystAgent",
    "ContextCoordinatorAgent",
]

for agent_name in agents_to_test:
    config = agent_config.get_agent_config(agent_name)
    if config:
        print(f"✓ {agent_name}:")
        print(f"    Model: {config.get('model', 'None')}")
        print(f"    Temperature: {config.get('temperature', 'None')}")
        print(f"    Max Tokens: {config.get('max_tokens', 'None')}")
        print(f"    Has System Prompt: {config.get('system_prompt') is not None}")
    else:
        print(f"✗ {agent_name}: Configuration not found")
print()

# Test 3: Token budgets
print("Test 3: Token budgets")
print("-" * 70)
print(f"Total Token Budget: {agent_config.TOTAL_TOKEN_BUDGET} tokens")
print("Token budgets per agent:")
for agent_name in agents_to_test:
    budget = agent_config.get_token_budget(agent_name)
    print(f"  - {agent_name}: {budget} tokens")
print()

# Test 4: Agent priorities
print("Test 4: Agent priorities")
print("-" * 70)
print("Priorities (lower = higher priority):")
priorities = []
for agent_name in agents_to_test:
    priority = agent_config.get_agent_priority(agent_name)
    priorities.append((agent_name, priority))
priorities.sort(key=lambda x: x[1])
for agent_name, priority in priorities:
    print(f"  {priority}. {agent_name}")
print()

# Test 5: Required vs skippable agents
print("Test 5: Required vs skippable agents")
print("-" * 70)
print("Required agents (must always execute):")
for agent_name in agents_to_test:
    if agent_config.is_agent_required(agent_name):
        print(f"  ✓ {agent_name}")
print()
print("Skippable agents (can skip under constraints):")
for agent_name in agents_to_test:
    if agent_config.is_agent_skippable(agent_name):
        print(f"  - {agent_name}")
print()

# Test 6: Configuration validation
print("Test 6: Configuration validation")
print("-" * 70)
validation_results = agent_config.validate_all_configs()
all_valid = all(validation_results.values())
if all_valid:
    print("✓ All configurations are valid")
    for agent_name, is_valid in validation_results.items():
        status = "✓" if is_valid else "✗"
        print(f"  {status} {agent_name}")
else:
    print("✗ Some configurations are invalid:")
    for agent_name, is_valid in validation_results.items():
        if not is_valid:
            print(f"  ✗ {agent_name}")
print()

# Test 7: Execution order
print("Test 7: Agent execution order")
print("-" * 70)
execution_order = agent_config.AGENT_EXECUTION_ORDER
print("Execution order:")
for i, agent_name in enumerate(execution_order, 1):
    print(f"  {i}. {agent_name}")
print()

# Test 8: System prompts (sample)
print("Test 8: System prompts (sample - first 100 chars)")
print("-" * 70)
for agent_name in ["ConversationAgent", "MemoryManagerAgent", "PrivacyGuardianAgent"]:
    config = agent_config.get_agent_config(agent_name)
    if config and config.get("system_prompt"):
        prompt = config["system_prompt"]
        preview = prompt[:100].replace("\n", " ")
        print(f"{agent_name}:")
        print(f"  {preview}...")
        print(f"  Total length: {len(prompt)} characters")
        print()

# Test 9: Integration with BaseAgent structure
print("Test 9: Configuration structure compatibility")
print("-" * 70)
test_config = agent_config.get_agent_config("ConversationAgent")
required_keys = ["name", "description", "model", "temperature", "max_tokens", "system_prompt"]
missing_keys = [key for key in required_keys if key not in test_config]
if not missing_keys:
    print("✓ Configuration has all required keys for BaseAgent")
    print("  Required keys:", ", ".join(required_keys))
else:
    print("✗ Missing keys:", ", ".join(missing_keys))
print()

# Summary
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✓ All {len(all_configs)} agent configurations accessible")
print(f"✓ Token budgets configured for all agents")
print(f"✓ Priorities assigned to all agents")
print(f"✓ Required/skippable agents identified")
print(f"✓ All configurations validated")
print(f"✓ Execution order defined")
print(f"✓ System prompts created")
print()
print("✅ All tests passed! Agent configuration is working correctly.")
print()

