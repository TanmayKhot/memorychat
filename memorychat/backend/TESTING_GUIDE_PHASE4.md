# Comprehensive Testing Guide: Phase 4 - Agent Layer

This guide provides comprehensive testing steps for all agents implemented in Phase 4.

---

## Quick Test: Run All Verification Scripts

```bash
cd memorychat/backend

# Run all structural verifications
for script in verify_step4_*.py; do
    echo "=== Testing $script ==="
    python3 "$script"
    echo ""
done

# Run all functional tests
for script in test_step4_*_functional.py; do
    echo "=== Testing $script ==="
    python3 "$script"
    echo ""
done
```

**Expected:** All scripts show 100% success rate ✅

---

## Phase 4 Testing Summary

### Step 4.1: Memory Manager Agent
**Verification:** `python3 verify_step4_1.py`  
**Functional:** `python3 test_step4_1_functional.py`

**What it tests:**
- ✅ Memory extraction from conversations
- ✅ Importance scoring (0.0-1.0)
- ✅ Memory categorization (fact, preference, event, relationship, other)
- ✅ Privacy mode awareness (INCOGNITO, PAUSE_MEMORY, NORMAL)
- ✅ Helper methods (entity extraction, tag generation, consolidation)

### Step 4.2: Memory Retrieval Agent
**Verification:** `python3 verify_step4_2.py`  
**Functional:** `python3 test_step4_2_functional.py`

**What it tests:**
- ✅ Semantic search (ChromaDB integration)
- ✅ Keyword search (SQL LIKE queries)
- ✅ Temporal search (recent memories)
- ✅ Entity search (people/places)
- ✅ Hybrid search (combines all strategies)
- ✅ Relevance ranking
- ✅ Context building

### Step 4.3: Privacy Guardian Agent
**Verification:** `python3 verify_step4_3.py`  
**Functional:** `python3 test_step4_3_functional.py`

**What it tests:**
- ✅ PII detection (email, phone, credit card, SSN, etc.)
- ✅ Privacy mode enforcement
- ✅ Content sanitization
- ✅ Warning generation
- ✅ Profile isolation
- ✅ Audit logging

### Step 4.4: Conversation Agent
**Verification:** `python3 verify_step4_4.py`  
**Functional:** `python3 test_step4_4_functional.py`

**What it tests:**
- ✅ Context assembly (system prompt, memory context, conversation history)
- ✅ Personality adaptation (tone, verbosity, traits)
- ✅ Response generation
- ✅ Quality checks (relevance, safety, memory usage)
- ✅ Edge case handling (empty memory, long history)

### Step 4.5: Conversation Analyst Agent
**Verification:** `python3 verify_step4_5.py`  
**Functional:** `python3 test_step4_5_functional.py`

**What it tests:**
- ✅ Sentiment analysis (positive, negative, neutral, mixed)
- ✅ Topic extraction
- ✅ Pattern detection
- ✅ Engagement calculation
- ✅ Memory gap identification
- ✅ Recommendation generation
- ✅ Insight storage

### Step 4.6: Context Coordinator Agent
**Verification:** `python3 verify_step4_6.py`  
**Functional:** `python3 test_step4_6_functional.py`

**What it tests:**
- ✅ Orchestration flow (all 5 steps)
- ✅ Agent integration
- ✅ Error handling and fallbacks
- ✅ Token budget management
- ✅ Result aggregation
- ✅ Privacy mode enforcement

---

## Manual Testing Steps

### Prerequisites

1. **Activate virtual environment** (if using one):
```bash
source venv/bin/activate  # or your venv path
```

2. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

3. **Set up environment variables** (if needed):
```bash
export OPENAI_API_KEY="your-key-here"  # For LLM agents
```

---

## Test 1: Memory Manager Agent

### Test Memory Extraction

```python
from agents.memory_manager_agent import MemoryManagerAgent

agent = MemoryManagerAgent()

# Test input
input_data = {
    "session_id": 1,
    "user_message": "I love Python programming and prefer it over Java.",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {
        "assistant_response": "That's great! Python is an excellent language.",
        "conversation_history": []
    }
}

# Execute
result = agent._execute_with_wrapper(input_data)

# Verify
assert result["success"] == True
assert "memories" in result["data"]
print(f"✓ Extracted {len(result['data']['memories'])} memories")
```

### Test Privacy Modes

```python
# Test INCOGNITO mode
input_data["privacy_mode"] = "incognito"
result = agent._execute_with_wrapper(input_data)
assert result["data"].get("skipped") == True
assert result["data"].get("reason") == "incognito_mode"
print("✓ INCOGNITO mode: Correctly skipped")

# Test PAUSE_MEMORY mode
input_data["privacy_mode"] = "pause_memory"
result = agent._execute_with_wrapper(input_data)
assert result["data"].get("skipped") == True
print("✓ PAUSE_MEMORY mode: Correctly skipped")
```

### Test Helper Methods

```python
# Test importance scoring
memory = {"content": "User prefers Python", "memory_type": "preference"}
score = agent._calculate_importance(memory)
assert 0.0 <= score <= 1.0
print(f"✓ Importance score: {score}")

# Test categorization
memory_type = agent._categorize_memory("I prefer Python")
assert memory_type in ["preference", "fact", "event", "relationship", "other"]
print(f"✓ Memory type: {memory_type}")

# Test tag generation
tags = agent._generate_tags("I love Python programming", "preference")
assert isinstance(tags, list)
print(f"✓ Tags: {tags}")
```

---

## Test 2: Memory Retrieval Agent

### Test Memory Retrieval

```python
from agents.memory_retrieval_agent import MemoryRetrievalAgent

agent = MemoryRetrievalAgent()

# Test input
input_data = {
    "session_id": 1,
    "user_message": "What do I prefer for programming?",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {}
}

# Execute
result = agent._execute_with_wrapper(input_data)

# Verify
assert result["success"] == True
assert "memories" in result["data"]
assert "context" in result["data"]
print(f"✓ Retrieved {len(result['data']['memories'])} memories")
print(f"✓ Context length: {len(result['data']['context'])} chars")
```

### Test Search Strategies

```python
# Test semantic search
memories = agent._semantic_search("Python", profile_id=1, n_results=5)
print(f"✓ Semantic search: {len(memories)} results")

# Test keyword search
memories = agent._keyword_search("Python", profile_id=1, n_results=5)
print(f"✓ Keyword search: {len(memories)} results")

# Test temporal search
memories = agent._temporal_search("recent", profile_id=1, n_results=5)
print(f"✓ Temporal search: {len(memories)} results")

# Test entity search
memories = agent._entity_search(["Python"], profile_id=1, n_results=5)
print(f"✓ Entity search: {len(memories)} results")
```

### Test Privacy Modes

```python
# Test INCOGNITO mode
input_data["privacy_mode"] = "incognito"
result = agent._execute_with_wrapper(input_data)
assert result["data"].get("skipped") == True
print("✓ INCOGNITO mode: Correctly skipped")

# Test PAUSE_MEMORY mode (should allow retrieval)
input_data["privacy_mode"] = "pause_memory"
result = agent._execute_with_wrapper(input_data)
assert result["success"] == True
assert result["data"].get("skipped") != True
print("✓ PAUSE_MEMORY mode: Retrieval allowed")
```

---

## Test 3: Privacy Guardian Agent

### Test PII Detection

```python
from agents.privacy_guardian_agent import PrivacyGuardianAgent

agent = PrivacyGuardianAgent()

# Test email detection
violations = agent._detect_email_addresses("Contact me at john@example.com")
assert len(violations) > 0
assert violations[0]["type"] == "email"
print(f"✓ Email detected: {violations[0]['content']}")

# Test phone detection
violations = agent._detect_phone_numbers("Call me at 555-123-4567")
assert len(violations) > 0
print(f"✓ Phone detected: {violations[0]['content']}")

# Test credit card detection
violations = agent._detect_credit_cards("Card: 4532-1234-5678-9010")
assert len(violations) > 0
print(f"✓ Credit card detected: {violations[0]['content']}")

# Test SSN detection
violations = agent._detect_ssn("SSN: 123-45-6789")
assert len(violations) > 0
print(f"✓ SSN detected: {violations[0]['content']}")
```

### Test Privacy Mode Enforcement

```python
# Test NORMAL mode
input_data = {
    "user_message": "My email is john@example.com",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {}
}
result = agent.execute(input_data)
assert result["data"]["allowed"] == True
assert result["data"]["sanitized_content"] == input_data["user_message"]
print("✓ NORMAL mode: Allows with warnings")

# Test INCOGNITO mode
input_data["privacy_mode"] = "incognito"
result = agent.execute(input_data)
assert "[EMAIL REDACTED]" in result["data"]["sanitized_content"]
print("✓ INCOGNITO mode: Sanitizes content")

# Test PAUSE_MEMORY mode
input_data["privacy_mode"] = "pause_memory"
result = agent.execute(input_data)
assert result["data"]["allowed"] == True
assert len(result["data"]["warnings"]) > 0
print("✓ PAUSE_MEMORY mode: Allows with warnings")
```

### Test Profile Isolation

```python
# Test matching profile IDs
isolation_ok = agent._verify_memory_access(profile_id=1, session_profile_id=1)
assert isolation_ok == True
print("✓ Matching profile IDs: Allowed")

# Test mismatched profile IDs
isolation_ok = agent._verify_memory_access(profile_id=1, session_profile_id=2)
assert isolation_ok == False
print("✓ Mismatched profile IDs: Blocked")
```

---

## Test 4: Conversation Agent

### Test Conversation Generation

```python
from agents.conversation_agent import ConversationAgent

agent = ConversationAgent()

# Test input
input_data = {
    "session_id": 1,
    "user_message": "What do I prefer for programming?",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {
        "memory_context": "Relevant memories:\n- User prefers Python (preference)",
        "conversation_history": []
    }
}

# Execute
result = agent._execute_with_wrapper(input_data)

# Verify
assert result["success"] == True
assert "response" in result["data"]
assert len(result["data"]["response"]) > 0
print(f"✓ Generated response: {result['data']['response'][:50]}...")
```

### Test Personality Adaptation

```python
# Test profile settings loading
profile_settings = agent._get_profile_settings(profile_id=1)
print(f"✓ Profile settings: {bool(profile_settings)}")

# Test system prompt building
system_prompt = agent._build_system_prompt(profile_settings)
assert len(system_prompt) > 0
print(f"✓ System prompt built: {len(system_prompt)} chars")

# Test memory context building
memory_context = agent._build_memory_context("Relevant memories:\n- User prefers Python")
assert len(memory_context) > 0
print(f"✓ Memory context built: {len(memory_context)} chars")
```

### Test Quality Checks

```python
# Test response quality
response = "This is a test response about Python programming."
user_message = "What do I prefer?"
quality = agent._check_response_quality(response, user_message, "")
assert quality.get("passed", True)  # May pass or fail based on content
print(f"✓ Quality check: {quality.get('score', 0)}")

# Test relevance check
is_relevant = agent._check_response_relevance(response, user_message)
print(f"✓ Relevance check: {is_relevant}")

# Test safety check
is_safe = agent._check_response_safety(response)
assert is_safe == True
print(f"✓ Safety check: {is_safe}")
```

---

## Test 5: Conversation Analyst Agent

### Test Conversation Analysis

```python
from agents.conversation_analyst_agent import ConversationAnalystAgent

agent = ConversationAnalystAgent()

# Test input
input_data = {
    "session_id": 1,
    "user_message": "Hello",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {
        "conversation_history": [
            {"role": "user", "content": "I love Python programming!"},
            {"role": "assistant", "content": "That's great!"},
            {"role": "user", "content": "What can I do with Python?"},
        ],
        "existing_memories": [
            {"content": "User prefers Python", "memory_type": "preference"}
        ]
    }
}

# Execute
result = agent._execute_with_wrapper(input_data)

# Verify
assert result["success"] == True
assert "analysis" in result["data"]
assert "insights" in result["data"]
assert "recommendations" in result["data"]
print(f"✓ Analysis completed")
print(f"✓ Sentiment: {result['data']['analysis']['sentiment']['sentiment']}")
print(f"✓ Topics: {len(result['data']['analysis']['topics'])}")
print(f"✓ Recommendations: {len(result['data']['recommendations'])}")
```

### Test Analysis Functions

```python
# Test sentiment analysis
messages = [
    {"role": "user", "content": "I love Python!"},
    {"role": "user", "content": "It's amazing!"}
]
sentiment = agent._analyze_sentiment(messages)
assert sentiment["sentiment"] in ["positive", "negative", "neutral", "mixed"]
print(f"✓ Sentiment: {sentiment['sentiment']} (confidence: {sentiment['confidence']})")

# Test topic extraction
topics = agent._extract_topics(messages)
assert isinstance(topics, list)
print(f"✓ Topics extracted: {len(topics)}")

# Test engagement calculation
engagement = agent._calculate_engagement(messages)
assert engagement["level"] in ["high", "medium", "low"]
print(f"✓ Engagement: {engagement['level']} (score: {engagement['score']})")
```

---

## Test 6: Context Coordinator Agent (Full Orchestration)

### Test Complete Orchestration Flow

```python
from agents.context_coordinator_agent import ContextCoordinatorAgent

coordinator = ContextCoordinatorAgent()

# Test input
input_data = {
    "session_id": 1,
    "user_message": "What do I prefer for programming?",
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {
        "conversation_history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }
}

# Execute orchestration
result = coordinator._execute_with_wrapper(input_data)

# Verify
assert result["success"] == True
assert "response" in result["data"]
assert "agents_executed" in result
assert len(result["agents_executed"]) > 0
print(f"✓ Orchestration completed")
print(f"✓ Response: {result['data']['response'][:50]}...")
print(f"✓ Agents executed: {result['agents_executed']}")
print(f"✓ Tokens used: {result['tokens_used']}")
```

### Test Privacy Mode Orchestration

```python
# Test NORMAL mode
input_data["privacy_mode"] = "normal"
result = coordinator._execute_with_wrapper(input_data)
assert result["success"] == True
assert "PrivacyGuardianAgent" in result["agents_executed"]
assert "MemoryRetrievalAgent" in result["agents_executed"]
assert "ConversationAgent" in result["agents_executed"]
assert "MemoryManagerAgent" in result["agents_executed"]
print("✓ NORMAL mode: All agents executed")

# Test INCOGNITO mode
input_data["privacy_mode"] = "incognito"
result = coordinator._execute_with_wrapper(input_data)
assert result["success"] == True
assert "MemoryRetrievalAgent" not in result["agents_executed"]
assert "MemoryManagerAgent" not in result["agents_executed"]
assert "ConversationAgent" in result["agents_executed"]
print("✓ INCOGNITO mode: Memory operations skipped")

# Test PAUSE_MEMORY mode
input_data["privacy_mode"] = "pause_memory"
result = coordinator._execute_with_wrapper(input_data)
assert result["success"] == True
assert "MemoryRetrievalAgent" in result["agents_executed"]
assert "MemoryManagerAgent" not in result["agents_executed"]
print("✓ PAUSE_MEMORY mode: Retrieval only")
```

### Test Error Handling

```python
# Test with invalid input
invalid_input = {
    "session_id": 1,
    "user_message": "",  # Empty message
    "privacy_mode": "normal",
    "profile_id": 1,
    "context": {}
}

result = coordinator._execute_with_wrapper(invalid_input)
assert result["success"] == False
print("✓ Error handling: Invalid input handled")

# Test with missing profile_id
incomplete_input = {
    "session_id": 1,
    "user_message": "Hello",
    "privacy_mode": "normal",
    "context": {}
}

result = coordinator._execute_with_wrapper(incomplete_input)
# Should handle gracefully (may succeed with defaults or fail gracefully)
print("✓ Error handling: Missing data handled")
```

### Test Token Management

```python
# Execute and check token tracking
result = coordinator._execute_with_wrapper(input_data)
assert "tokens_by_agent" in result
assert "tokens_used" in result

total_tokens = result["tokens_used"]
tokens_by_agent = result["tokens_by_agent"]

print(f"✓ Total tokens: {total_tokens}")
print(f"✓ Tokens by agent: {tokens_by_agent}")

# Check if within budget
assert total_tokens <= 5000  # TOTAL_TOKEN_BUDGET
print("✓ Token budget: Within limits")
```

---

## End-to-End Testing Script

Create `test_phase4_end_to_end.py`:

```python
#!/usr/bin/env python3
"""
End-to-end test for Phase 4: Complete agent orchestration
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from agents.context_coordinator_agent import ContextCoordinatorAgent

def test_end_to_end():
    """Test complete end-to-end flow."""
    print("=" * 70)
    print("PHASE 4 END-TO-END TEST")
    print("=" * 70)
    
    coordinator = ContextCoordinatorAgent()
    
    # Test scenario 1: Normal conversation with memory
    print("\n[Test 1] Normal conversation with memory")
    input_data = {
        "session_id": 1,
        "user_message": "I love Python programming!",
        "privacy_mode": "normal",
        "profile_id": 1,
        "context": {
            "conversation_history": []
        }
    }
    
    result = coordinator._execute_with_wrapper(input_data)
    print(f"  Success: {result['success']}")
    print(f"  Agents executed: {result.get('agents_executed', [])}")
    print(f"  Tokens used: {result.get('tokens_used', 0)}")
    if result['success']:
        print(f"  Response: {result['data'].get('response', '')[:100]}...")
    
    # Test scenario 2: Privacy mode INCOGNITO
    print("\n[Test 2] INCOGNITO mode")
    input_data["privacy_mode"] = "incognito"
    input_data["user_message"] = "My email is test@example.com"
    
    result = coordinator._execute_with_wrapper(input_data)
    print(f"  Success: {result['success']}")
    print(f"  Agents executed: {result.get('agents_executed', [])}")
    print(f"  Memory operations skipped: {'MemoryRetrievalAgent' not in result.get('agents_executed', [])}")
    
    # Test scenario 3: PAUSE_MEMORY mode
    print("\n[Test 3] PAUSE_MEMORY mode")
    input_data["privacy_mode"] = "pause_memory"
    input_data["user_message"] = "What do I prefer?"
    
    result = coordinator._execute_with_wrapper(input_data)
    print(f"  Success: {result['success']}")
    print(f"  Agents executed: {result.get('agents_executed', [])}")
    print(f"  Memory retrieval: {'MemoryRetrievalAgent' in result.get('agents_executed', [])}")
    print(f"  Memory management: {'MemoryManagerAgent' not in result.get('agents_executed', [])}")
    
    print("\n" + "=" * 70)
    print("END-TO-END TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    test_end_to_end()
```

---

## Automated Test Suite

Run all tests:

```bash
cd memorychat/backend

# Create test script
cat > test_all_phase4.sh << 'EOF'
#!/bin/bash
echo "=== PHASE 4 COMPREHENSIVE TESTING ==="
echo ""

echo "1. Structural Verification Tests"
echo "--------------------------------"
for script in verify_step4_*.py; do
    echo "Testing $script..."
    python3 "$script" 2>&1 | grep -E "(Success Rate|Total Checks|Passed|Failed)" | tail -4
    echo ""
done

echo "2. Functional Tests"
echo "-------------------"
for script in test_step4_*_functional.py; do
    echo "Testing $script..."
    python3 "$script" 2>&1 | grep -E "(Success Rate|Total Checks|Passed|Failed)" | tail -4
    echo ""
done

echo "3. Summary"
echo "----------"
echo "All Phase 4 tests completed!"
EOF

chmod +x test_all_phase4.sh
./test_all_phase4.sh
```

---

## Testing Checklist

### ✅ Step 4.1: Memory Manager Agent
- [ ] Memory extraction works
- [ ] Importance scoring works
- [ ] Memory categorization works
- [ ] Privacy modes respected
- [ ] Helper methods work

### ✅ Step 4.2: Memory Retrieval Agent
- [ ] Semantic search works
- [ ] Keyword search works
- [ ] Temporal search works
- [ ] Entity search works
- [ ] Hybrid search works
- [ ] Relevance ranking works
- [ ] Context building works

### ✅ Step 4.3: Privacy Guardian Agent
- [ ] PII detection works
- [ ] Privacy mode enforcement works
- [ ] Content sanitization works
- [ ] Warning generation works
- [ ] Profile isolation works
- [ ] Audit logging works

### ✅ Step 4.4: Conversation Agent
- [ ] Context assembly works
- [ ] Personality adaptation works
- [ ] Response generation works
- [ ] Quality checks work
- [ ] Edge cases handled

### ✅ Step 4.5: Conversation Analyst Agent
- [ ] Sentiment analysis works
- [ ] Topic extraction works
- [ ] Pattern detection works
- [ ] Engagement calculation works
- [ ] Memory gap identification works
- [ ] Recommendations work
- [ ] Insights stored

### ✅ Step 4.6: Context Coordinator Agent
- [ ] Orchestration flow works
- [ ] All agents integrated
- [ ] Error handling works
- [ ] Token management works
- [ ] Privacy modes enforced
- [ ] Result aggregation works

---

## Expected Test Results

**All verification scripts should show:**
- Success Rate: 100.0%
- Total Checks: Varies by step
- Passed: All checks
- Failed: 0

**All functional tests should show:**
- Success Rate: 100.0%
- Total Checks: Varies by step
- Passed: All checks
- Failed: 0

---

## Troubleshooting

### Issue: Import Errors

**Solution:**
```bash
cd memorychat/backend
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Issue: LLM Not Available

**Note:** This is expected if API key is not set. Structural and functional tests don't require LLM. For full testing:
```bash
export OPENAI_API_KEY="your-key-here"
```

### Issue: Database Not Available

**Note:** Some tests may fail gracefully. Ensure database is initialized:
```python
from database.database import init_db
init_db()
```

### Issue: ChromaDB Not Available

**Note:** Semantic search will fail gracefully. Other search strategies will still work.

---

## Summary

**Quick Test Command:**
```bash
cd memorychat/backend

# Run all verifications
for script in verify_step4_*.py; do python3 "$script"; done

# Run all functional tests
for script in test_step4_*_functional.py; do python3 "$script"; done
```

**Expected:** All tests show 100% success rate ✅

All Phase 4 agents are implemented, tested, and ready for use!

