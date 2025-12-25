"""
Example usage of ChatGPT Stateful Agent with Zep Memory
"""

import os
from dotenv import load_dotenv
from agent_zep import StatefulAgentWithZep

# Load environment variables
load_dotenv()

def main():
    # Initialize agent with Zep
    print("Initializing ChatGPT Stateful Agent with Zep Memory...\n")
    
    agent = StatefulAgentWithZep(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("MODEL_NAME", "gpt-4"),
        zep_api_url=os.getenv("ZEP_API_URL", "http://localhost:8000"),
        zep_api_key=os.getenv("ZEP_API_KEY"),
        use_zep=True  # Set to False to use local storage fallback
    )
    
    print(f"✓ Agent initialized")
    print(f"  Session ID: {agent.session_id}")
    print(f"  Memory Type: {'Zep' if agent.use_zep else 'Local'}")
    print(f"  Model: {agent.model_name}\n")
    
    # Example 1: Basic conversation with short-term memory
    print("=" * 60)
    print("Example 1: Basic Conversation with Memory")
    print("=" * 60)
    
    response1 = agent.chat("Hello! My name is Alice and I'm a software engineer.")
    print(f"\n👤 User: Hello! My name is Alice and I'm a software engineer.")
    print(f"🤖 Assistant: {response1['response']}\n")
    
    response2 = agent.chat("What's my name and profession?")
    print(f"👤 User: What's my name and profession?")
    print(f"🤖 Assistant: {response2['response']}\n")
    
    # Example 2: Store facts in long-term memory
    print("=" * 60)
    print("Example 2: Storing Facts in Long-term Memory")
    print("=" * 60)
    
    agent.add_to_long_term_memory(
        fact="Alice prefers Python and Go programming languages",
        context="Programming language preferences",
        importance=8
    )
    print("\n✓ Stored: Alice prefers Python and Go\n")
    
    agent.add_to_long_term_memory(
        fact="Alice is working on a distributed systems project",
        context="Current projects",
        importance=9
    )
    print("✓ Stored: Working on distributed systems project\n")
    
    agent.add_to_long_term_memory(
        fact="Alice's favorite database is PostgreSQL",
        context="Technology stack preferences",
        importance=7
    )
    print("✓ Stored: Favorite database is PostgreSQL\n")
    
    # Example 3: Query using long-term memory
    print("=" * 60)
    print("Example 3: Querying with Long-term Memory")
    print("=" * 60)
    
    response3 = agent.chat(
        "What technologies and projects am I interested in?",
        use_long_term_memory=True
    )
    print(f"\n👤 User: What technologies and projects am I interested in?")
    print(f"🤖 Assistant: {response3['response']}")
    print(f"\n📊 Facts retrieved: {response3['relevant_facts_count']}\n")
    
    # Example 4: Get memory summary (Zep only)
    if agent.use_zep:
        print("=" * 60)
        print("Example 4: Memory Summary (Zep Feature)")
        print("=" * 60)
        
        summary = agent.get_memory_summary()
        if summary:
            print(f"\n📝 Memory Summary:\n{summary}\n")
        else:
            print("\n📝 No summary available yet (needs more conversation history)\n")
    
    # Example 5: View conversation history
    print("=" * 60)
    print("Example 5: Conversation History")
    print("=" * 60)
    
    history = agent.get_conversation_history()
    print(f"\n💬 Total messages in short-term memory: {len(history)}\n")
    
    for msg in history[:3]:  # Show first 3 messages
        role = msg['role'].upper()
        content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"{role}: {content}\n")
    
    # Example 6: Memory statistics
    print("=" * 60)
    print("Example 6: Memory Statistics")
    print("=" * 60)
    
    stats = agent.get_memory_stats()
    print(f"\n📊 Memory Stats:")
    print(f"  Session ID: {stats['session_id']}")
    print(f"  Memory Type: {stats['memory_type']}")
    print(f"  Short-term messages: {stats['short_term_messages']}")
    print(f"  Long-term facts: {stats['long_term_facts']}")
    
    # Example 7: Export session
    print("\n" + "=" * 60)
    print("Example 7: Export Session Data")
    print("=" * 60)
    
    session_data = agent.export_session()
    print(f"\n💾 Session exported:")
    print(f"  Session ID: {session_data['session_id']}")
    print(f"  Memory Type: {session_data['memory_type']}")
    print(f"  Timestamp: {session_data['timestamp']}")
    print(f"  Facts stored: {session_data['long_term_facts_count']}\n")
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
