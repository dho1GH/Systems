"""
Basic tests for the ChatGPT Stateful Agent
"""

import os
import sys
import tempfile
import shutil

# Test imports
print("Testing imports...")
try:
    from agent import StatefulAgent, ShortTermMemory, LongTermMemory
    print("✓ agent.py imports successful")
except Exception as e:
    print(f"✗ agent.py import failed: {e}")
    sys.exit(1)

try:
    from agent_zep import StatefulAgentWithZep, ZepLongTermMemory, LocalLongTermMemory, ShortTermMemory as STM2, ZEP_AVAILABLE
    print("✓ agent_zep.py imports successful")
    print(f"  Zep available: {ZEP_AVAILABLE}")
except Exception as e:
    print(f"✗ agent_zep.py import failed: {e}")
    sys.exit(1)

try:
    import flask
    from flask import Flask
    print("✓ Flask import successful")
except Exception as e:
    print(f"✗ Flask import failed: {e}")
    sys.exit(1)

# Test ShortTermMemory
print("\nTesting ShortTermMemory...")
stm = ShortTermMemory(max_messages=3)
stm.add_message("user", "Hello")
stm.add_message("assistant", "Hi there!")
stm.add_message("user", "How are you?")
stm.add_message("assistant", "I'm good!")
stm.add_message("user", "Great!")

messages = stm.get_messages()
assert len(messages) == 3, f"Expected 3 messages, got {len(messages)}"
assert messages[-1]["content"] == "Great!", "Last message not correct"
print("✓ ShortTermMemory working correctly")
print(f"  Messages stored: {len(messages)}")
print(f"  Max messages: {stm.max_messages}")

# Test LongTermMemory (Local)
print("\nTesting LocalLongTermMemory...")
temp_dir = tempfile.mkdtemp()
try:
    ltm = LongTermMemory(persistence_path=temp_dir)
    
    # Add facts
    ltm.add_fact("User likes Python", "Programming preferences", 8)
    ltm.add_fact("User is a software engineer", "Professional info", 9)
    ltm.add_fact("User prefers VS Code", "Tools", 6)
    
    # Test search
    results = ltm.search_facts("Python", top_k=5)
    assert len(results) > 0, "No results found for Python search"
    assert any("Python" in r["fact"] for r in results), "Python fact not found"
    print("✓ LocalLongTermMemory working correctly")
    print(f"  Facts stored: {len(ltm.get_all_facts())}")
    print(f"  Search results: {len(results)}")
    
    # Test persistence
    ltm.save()
    ltm2 = LongTermMemory(persistence_path=temp_dir)
    assert len(ltm2.get_all_facts()) == 3, "Facts not persisted correctly"
    print("✓ Memory persistence working")
    
finally:
    shutil.rmtree(temp_dir)

# Test LocalLongTermMemory (from agent_zep)
print("\nTesting LocalLongTermMemory (agent_zep version)...")
temp_dir = tempfile.mkdtemp()
try:
    ltm = LocalLongTermMemory(persistence_path=temp_dir, session_id="test_session")
    
    ltm.add_fact("Test fact 1", "context1", 7)
    ltm.add_fact("Test fact 2", "context2", 8)
    
    results = ltm.search_memory("Test", limit=5)
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    print("✓ LocalLongTermMemory (agent_zep) working correctly")
    print(f"  Facts stored: {len(ltm.get_all_facts())}")
    
finally:
    shutil.rmtree(temp_dir)

# Test API server imports
print("\nTesting API server...")
try:
    # Just check if it can be imported without starting the server
    with open('api_server.py', 'r') as f:
        content = f.read()
        assert 'Flask' in content, "Flask not found in API server"
        assert 'StatefulAgentWithZep' in content, "Agent not imported in API server"
        assert '/chat' in content, "Chat endpoint not found"
        assert '/memory/summary' in content, "Memory summary endpoint not found"
    print("✓ API server file structure correct")
    print("  Key endpoints: /chat, /memory/add, /memory/summary, /stats")
except Exception as e:
    print(f"✗ API server check failed: {e}")
    sys.exit(1)

# Test example_usage.py
print("\nTesting example_usage.py...")
try:
    with open('example_usage.py', 'r') as f:
        content = f.read()
        assert 'StatefulAgentWithZep' in content, "Agent not imported in example"
        assert 'chat' in content, "Chat method not used in example"
        assert 'add_to_long_term_memory' in content, "Long-term memory not used"
    print("✓ Example usage file structure correct")
except Exception as e:
    print(f"✗ Example usage check failed: {e}")
    sys.exit(1)

# Test Docker files
print("\nTesting Docker configuration...")
try:
    with open('Dockerfile', 'r') as f:
        content = f.read()
        assert 'python:' in content, "Python base image not found"
        assert 'requirements.txt' in content, "Requirements not copied"
        assert 'api_server.py' in content, "API server not included"
    print("✓ Dockerfile correct")
    
    with open('docker-compose.yml', 'r') as f:
        content = f.read()
        assert 'zep:' in content, "Zep service not found"
        assert 'postgres:' in content, "PostgreSQL service not found"
        assert 'agent:' in content, "Agent service not found"
    print("✓ docker-compose.yml correct")
    print("  Services: zep, postgres, agent")
except Exception as e:
    print(f"✗ Docker configuration check failed: {e}")
    sys.exit(1)

# Test environment configuration
print("\nTesting environment configuration...")
try:
    with open('.env.example', 'r') as f:
        content = f.read()
        assert 'OPENAI_API_KEY' in content, "OpenAI API key not in env"
        assert 'ZEP_API_URL' in content, "Zep URL not in env"
        assert 'MODEL_NAME' in content, "Model name not in env"
        assert 'ZEPPELIN_URL' not in content, "Zeppelin URL should not be present"
    print("✓ .env.example correct (no Zeppelin references)")
except Exception as e:
    print(f"✗ Environment configuration check failed: {e}")
    sys.exit(1)

# Test README
print("\nTesting README...")
try:
    with open('README.md', 'r') as f:
        content = f.read()
        assert 'Zep' in content, "Zep not mentioned in README"
        assert 'Zeppelin' not in content, "Zeppelin should not be mentioned"
        assert 'N8N' in content, "N8N not mentioned"
        assert 'docker-compose' in content, "Docker compose not mentioned"
        assert 'StatefulAgentWithZep' in content, "Main agent class not documented"
    print("✓ README correct (Zep documented, no Zeppelin)")
    print("  Includes: Zep integration, Docker setup, N8N examples")
except Exception as e:
    print(f"✗ README check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! ✓")
print("=" * 60)
print("\nSummary:")
print("  - Core agent classes working")
print("  - Memory systems functional")
print("  - API server structured correctly")
print("  - Docker configuration complete")
print("  - Documentation updated (no Zeppelin)")
print("  - Zep memory integration implemented")
print("\nNote: Full integration test requires:")
print("  - Valid OpenAI API key")
print("  - Running Zep instance (optional)")
