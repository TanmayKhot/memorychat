# Testing Guide: Step 3.2 - Agent Configuration

This guide provides comprehensive testing steps for Step 3.2: Agent Configuration.

---

## Prerequisites

Before testing, ensure:
1. ✅ All dependencies are installed (if testing runtime)
2. ✅ Code is in place (structural tests don't require dependencies)
3. ✅ You're in the `memorychat/backend` directory

---

## Quick Verification

Run the automated verification script:

```bash
cd memorychat/backend
python3 verify_step3_2.py
```

Expected output: **100% check pass rate (61/61 checks passed)**

---

## Manual Testing Steps

### Test 1: Verify File Structure

```bash
# Check that agent_config.py exists
ls -la config/agent_config.py

# Check file size (should be ~400+ lines)
wc -l config/agent_config.py
```

**Expected:** File exists and has substantial content.

---

### Test 2: Test Configuration Access

Run the test script:

```bash
cd memorychat/backend
python3 test_agent_config.py
```

This will test:
- ✅ All 6 agent configurations are accessible
- ✅ Each configuration has required fields
- ✅ Token budgets are configured
- ✅ Priorities are assigned
- ✅ Required/skippable agents are identified
- ✅ Configurations are valid
- ✅ Execution order is defined

**Expected Output:**
```
✓ Found 6 agent configurations
✓ All configurations have required fields
✓ Token budgets configured
✓ Priorities assigned
✓ All tests passed!
```

---

### Test 3: Test Individual Agent Configurations

Create a test script or use Python interactively:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Import agent config
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_config",
    Path.cwd() / "config" / "agent_config.py"
)
agent_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_config)

# Test ConversationAgent
config = agent_config.get_agent_config("ConversationAgent")
print(f"Name: {config['name']}")
print(f"Model: {config['model']}")
print(f"Temperature: {config['temperature']}")
print(f"Max Tokens: {config['max_tokens']}")
print(f"Has System Prompt: {config['system_prompt'] is not None}")
```

**Expected:**
- Name: "ConversationAgent"
- Model: "gpt-4"
- Temperature: 0.7
- Max Tokens: 500
- Has System Prompt: True

---

### Test 4: Test Token Budgets

```python
# Test token budgets
budget = agent_config.get_token_budget("ConversationAgent")
print(f"ConversationAgent budget: {budget} tokens")

# Test total budget
print(f"Total budget: {agent_config.TOTAL_TOKEN_BUDGET} tokens")

# Test all budgets
for agent_name in ["ConversationAgent", "MemoryManagerAgent", "MemoryRetrievalAgent"]:
    budget = agent_config.get_token_budget(agent_name)
    print(f"{agent_name}: {budget} tokens")
```

**Expected:**
- ConversationAgent: 2000 tokens
- MemoryManagerAgent: 1000 tokens
- MemoryRetrievalAgent: 800 tokens
- Total budget: 5000 tokens

---

### Test 5: Test Agent Priorities

```python
# Test priorities
priority = agent_config.get_agent_priority("ConversationAgent")
print(f"ConversationAgent priority: {priority}")

# Test all priorities (should be sorted)
priorities = []
for agent_name in ["ConversationAgent", "PrivacyGuardianAgent", "MemoryRetrievalAgent"]:
    priority = agent_config.get_agent_priority(agent_name)
    priorities.append((agent_name, priority))
priorities.sort(key=lambda x: x[1])
for name, prio in priorities:
    print(f"{prio}. {name}")
```

**Expected:**
- ConversationAgent: Priority 1 (highest)
- PrivacyGuardianAgent: Priority 2
- MemoryRetrievalAgent: Priority 3

---

### Test 6: Test Required vs Skippable Agents

```python
# Test required agents
required = agent_config.is_agent_required("ConversationAgent")
print(f"ConversationAgent required: {required}")

# Test skippable agents
skippable = agent_config.is_agent_skippable("ConversationAnalystAgent")
print(f"ConversationAnalystAgent skippable: {skippable}")

# List all required agents
print("Required agents:")
for agent_name in ["ConversationAgent", "PrivacyGuardianAgent", "MemoryManagerAgent"]:
    if agent_config.is_agent_required(agent_name):
        print(f"  ✓ {agent_name}")

# List all skippable agents
print("Skippable agents:")
for agent_name in ["ConversationAnalystAgent", "MemoryManagerAgent"]:
    if agent_config.is_agent_skippable(agent_name):
        print(f"  - {agent_name}")
```

**Expected:**
- ConversationAgent: Required = True
- PrivacyGuardianAgent: Required = True
- ConversationAnalystAgent: Skippable = True

---

### Test 7: Test Configuration Validation

```python
# Test validation
results = agent_config.validate_all_configs()
print("Validation results:")
for agent_name, is_valid in results.items():
    status = "✓" if is_valid else "✗"
    print(f"  {status} {agent_name}: {is_valid}")

# Test individual validation
test_config = agent_config.get_agent_config("ConversationAgent")
is_valid = agent_config.validate_agent_config(test_config)
print(f"ConversationAgent valid: {is_valid}")
```

**Expected:**
- All configurations: Valid = True
- Individual validation: True

---

### Test 8: Test Execution Order

```python
# Test execution order
execution_order = agent_config.AGENT_EXECUTION_ORDER
print("Execution order:")
for i, agent_name in enumerate(execution_order, 1):
    print(f"  {i}. {agent_name}")
```

**Expected Order:**
1. PrivacyGuardianAgent
2. MemoryRetrievalAgent
3. ConversationAgent
4. MemoryManagerAgent
5. ConversationAnalystAgent

---

### Test 9: Test System Prompts

```python
# Test system prompts
config = agent_config.get_agent_config("ConversationAgent")
prompt = config["system_prompt"]
print(f"ConversationAgent prompt length: {len(prompt)} characters")
print(f"First 200 chars: {prompt[:200]}...")

# Test all prompts
for agent_name in ["ConversationAgent", "MemoryManagerAgent", "PrivacyGuardianAgent"]:
    config = agent_config.get_agent_config(agent_name)
    if config.get("system_prompt"):
        print(f"{agent_name}: {len(config['system_prompt'])} chars")
```

**Expected:**
- All LLM-based agents have system prompts
- Prompts are substantial (200+ characters)
- ContextCoordinatorAgent has None (rule-based)

---

### Test 10: Test Integration with BaseAgent

```python
# Test that configuration can be used with BaseAgent
config = agent_config.get_agent_config("ConversationAgent")

# Check all required fields for BaseAgent.__init__
required_fields = {
    "name": config.get("name"),
    "description": config.get("description"),
    "llm_model": config.get("model"),
    "temperature": config.get("temperature"),
    "max_tokens": config.get("max_tokens"),
    "system_prompt": config.get("system_prompt"),
}

print("Configuration fields for BaseAgent:")
for field, value in required_fields.items():
    print(f"  {field}: {value}")

# All should be present and not None (except model for rule-based agents)
```

**Expected:**
- All fields present
- Values are appropriate types
- Can be passed directly to BaseAgent.__init__()

---

## Comprehensive Test Script

Run the comprehensive test script:

```bash
cd memorychat/backend
python3 test_agent_config.py
```

This runs all tests automatically and provides a summary.

---

## Expected Test Results

All tests should pass with:

✅ **File Structure:**
- `config/agent_config.py` exists
- File has substantial content

✅ **Configurations:**
- All 6 agents configured
- All required fields present
- Models appropriate (gpt-4 for ConversationAgent, gpt-3.5-turbo for others)
- Temperatures optimized (0.0-0.7)
- System prompts comprehensive

✅ **Token Budgets:**
- All agents have budgets
- Total budget = 5000 tokens
- ConversationAgent has highest budget (2000)

✅ **Priorities:**
- All agents have priorities
- ConversationAgent = 1 (highest)
- Priorities logical

✅ **Required/Skippable:**
- ConversationAgent and PrivacyGuardianAgent are required
- ConversationAnalystAgent is skippable

✅ **Validation:**
- All configurations valid
- Individual validation works

✅ **Execution Order:**
- Order defined correctly
- PrivacyGuardianAgent first
- ConversationAgent third

✅ **System Prompts:**
- All LLM agents have prompts
- Prompts are comprehensive
- ContextCoordinatorAgent has None

---

## Troubleshooting

### Issue: Import Errors

**Solution:** Ensure you're in the `memorychat/backend` directory and Python path is set correctly.

```bash
cd memorychat/backend
export PYTHONPATH=$PWD:$PYTHONPATH
python3 test_agent_config.py
```

### Issue: Configuration Not Found

**Solution:** Check that `config/agent_config.py` exists and has all agent definitions.

```bash
ls -la config/agent_config.py
grep -c "CONVERSATION_AGENT" config/agent_config.py
```

### Issue: Validation Fails

**Solution:** Check that all configurations have required fields:
- name
- description
- model (can be None for rule-based)
- temperature (if model is not None)
- system_prompt (if model is not None)

---

## Integration Testing

To test integration with BaseAgent (requires dependencies):

```python
# This requires dependencies to be installed
from agents.base_agent import BaseAgent
from config.agent_config import CONVERSATION_AGENT

# Create agent instance using configuration
agent = BaseAgent(
    name=CONVERSATION_AGENT["name"],
    description=CONVERSATION_AGENT["description"],
    llm_model=CONVERSATION_AGENT["model"],
    temperature=CONVERSATION_AGENT["temperature"],
    max_tokens=CONVERSATION_AGENT["max_tokens"],
    system_prompt=CONVERSATION_AGENT["system_prompt"]
)

print(f"Agent created: {agent.name}")
print(f"Model: {agent.llm_model}")
print(f"Temperature: {agent.temperature}")
```

**Note:** This requires dependencies (`pydantic-settings`, `langchain`, etc.) to be installed.

---

## Summary

**Quick Test:**
```bash
cd memorychat/backend
python3 verify_step3_2.py    # Verification (61 checks)
python3 test_agent_config.py  # Functional tests
```

**Expected:** All tests pass ✅

The agent configuration is working correctly if:
- ✅ All 6 agents are configured
- ✅ Configurations are accessible via helper functions
- ✅ Token budgets and priorities are set
- ✅ System prompts are comprehensive
- ✅ Validation passes
- ✅ Integration with BaseAgent works

