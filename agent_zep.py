"""
ChatGPT Stateful Agent with Zep Memory Integration
Provides short-term and long-term memory capabilities using Zep memory store.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from openai import OpenAI
import tiktoken

try:
    from zep_python import ZepClient
    from zep_python.memory import Memory, Message, Session
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False
    # Define placeholder classes when Zep is not available
    class Memory:
        pass
    class Message:
        pass
    class Session:
        pass
    class ZepClient:
        pass
    print("Warning: zep-python not installed. Long-term memory will use local storage.")


class ShortTermMemory:
    """Manages conversation context for the current session."""
    
    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to short-term memory."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages for API context."""
        return [{"role": msg["role"], "content": msg["content"]} 
                for msg in self.messages]
    
    def clear(self):
        """Clear short-term memory."""
        self.messages = []
    
    def to_dict(self) -> Dict:
        """Export to dictionary."""
        return {"messages": self.messages}
    
    def from_dict(self, data: Dict):
        """Import from dictionary."""
        self.messages = data.get("messages", [])


class ZepLongTermMemory:
    """Manages persistent memory using Zep memory store."""
    
    def __init__(self, api_url: str = "http://localhost:8000", api_key: Optional[str] = None, session_id: str = None):
        if not ZEP_AVAILABLE:
            raise ImportError("zep-python package is required. Install with: pip install zep-python")
        
        self.api_url = api_url
        self.api_key = api_key
        self.session_id = session_id or f"session_{int(time.time())}"
        
        # Initialize Zep client
        self.client = ZepClient(base_url=api_url, api_key=api_key)
        
        # Ensure session exists
        self._ensure_session()
    
    def _ensure_session(self):
        """Ensure the session exists in Zep."""
        try:
            self.client.memory.get_session(session_id=self.session_id)
        except Exception:
            # Session doesn't exist, create it
            try:
                session = Session(
                    session_id=self.session_id,
                    metadata={"created_at": datetime.now().isoformat()}
                )
                self.client.memory.add_session(session)
            except Exception as e:
                print(f"Warning: Could not create Zep session: {e}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to Zep memory."""
        try:
            message = Message(
                role=role,
                content=content,
                metadata=metadata or {}
            )
            self.client.memory.add_memory(
                session_id=self.session_id,
                memory=Memory(messages=[message])
            )
        except Exception as e:
            print(f"Error adding message to Zep: {e}")
    
    def add_fact(self, fact: str, context: str = "", importance: int = 5, metadata: Optional[Dict] = None):
        """Store a fact in Zep memory."""
        try:
            fact_metadata = {
                "type": "fact",
                "context": context,
                "importance": importance,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }
            
            message = Message(
                role="system",
                content=f"FACT: {fact}",
                metadata=fact_metadata
            )
            
            self.client.memory.add_memory(
                session_id=self.session_id,
                memory=Memory(messages=[message])
            )
        except Exception as e:
            print(f"Error adding fact to Zep: {e}")
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Zep memory for relevant information."""
        try:
            # Get memory with search
            memory = self.client.memory.get_session_memory(
                session_id=self.session_id,
                memory_type="perpetual"
            )
            
            if not memory or not memory.messages:
                return []
            
            # Extract facts and relevant messages
            results = []
            for msg in memory.messages[-20:]:  # Get last 20 messages
                if msg.metadata and msg.metadata.get("type") == "fact":
                    results.append({
                        "fact": msg.content.replace("FACT: ", ""),
                        "context": msg.metadata.get("context", ""),
                        "importance": msg.metadata.get("importance", 5),
                        "timestamp": msg.metadata.get("timestamp", ""),
                        "role": msg.role
                    })
            
            return results[:limit]
        except Exception as e:
            print(f"Error searching Zep memory: {e}")
            return []
    
    def get_session_memory(self) -> Optional[Memory]:
        """Get the full session memory from Zep."""
        try:
            return self.client.memory.get_session_memory(
                session_id=self.session_id,
                memory_type="perpetual"
            )
        except Exception as e:
            print(f"Error getting Zep session memory: {e}")
            return None
    
    def get_summary(self) -> Optional[str]:
        """Get memory summary from Zep."""
        try:
            memory = self.get_session_memory()
            if memory and hasattr(memory, 'summary'):
                return memory.summary
            return None
        except Exception as e:
            print(f"Error getting Zep summary: {e}")
            return None
    
    def clear(self):
        """Clear Zep session memory."""
        try:
            self.client.memory.delete_memory(session_id=self.session_id)
            # Recreate session
            self._ensure_session()
        except Exception as e:
            print(f"Error clearing Zep memory: {e}")
    
    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Get all stored facts from Zep."""
        return self.search_memory("", limit=100)


class LocalLongTermMemory:
    """Fallback: Local file-based long-term memory when Zep is not available."""
    
    def __init__(self, persistence_path: str = "./data/memory", session_id: str = None):
        self.persistence_path = persistence_path
        self.session_id = session_id or f"session_{int(time.time())}"
        os.makedirs(persistence_path, exist_ok=True)
        self.memory_file = os.path.join(persistence_path, f"memory_{self.session_id}.json")
        self.facts: List[Dict[str, Any]] = []
        self.load()
    
    def add_fact(self, fact: str, context: str = "", importance: int = 5, metadata: Optional[Dict] = None):
        """Store a fact in local memory."""
        fact_entry = {
            "fact": fact,
            "context": context,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None,
            "metadata": metadata or {}
        }
        self.facts.append(fact_entry)
        self.save()
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant facts (simple keyword matching)."""
        if not query:
            return self.facts[:limit]
        
        query_lower = query.lower()
        relevant_facts = []
        
        for fact in self.facts:
            fact_text = f"{fact['fact']} {fact['context']}".lower()
            if any(word in fact_text for word in query_lower.split()):
                fact["access_count"] += 1
                fact["last_accessed"] = datetime.now().isoformat()
                relevant_facts.append(fact)
        
        # Sort by importance and access count
        relevant_facts.sort(
            key=lambda x: (x["importance"], x["access_count"]), 
            reverse=True
        )
        
        self.save()
        return relevant_facts[:limit]
    
    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Get all stored facts."""
        return self.facts
    
    def clear(self):
        """Clear all long-term memory."""
        self.facts = []
        self.save()
    
    def save(self):
        """Save memory to disk."""
        with open(self.memory_file, 'w') as f:
            json.dump({"facts": self.facts}, f, indent=2)
    
    def load(self):
        """Load memory from disk."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.facts = data.get("facts", [])
            except Exception as e:
                print(f"Error loading long-term memory: {e}")
                self.facts = []


class StatefulAgentWithZep:
    """Main agent with Zep memory integration for both short-term and long-term memory."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        zep_api_url: Optional[str] = None,
        zep_api_key: Optional[str] = None,
        persistence_path: str = "./data/memory",
        session_id: Optional[str] = None,
        use_zep: bool = True
    ):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        self.session_id = session_id or f"session_{int(time.time())}"
        self.short_term_memory = ShortTermMemory()
        
        # Initialize long-term memory with Zep or fallback to local
        self.use_zep = use_zep and ZEP_AVAILABLE and zep_api_url
        
        if self.use_zep:
            try:
                self.long_term_memory = ZepLongTermMemory(
                    api_url=zep_api_url,
                    api_key=zep_api_key,
                    session_id=self.session_id
                )
                print(f"✓ Using Zep memory store at {zep_api_url}")
            except Exception as e:
                print(f"Failed to initialize Zep, falling back to local storage: {e}")
                self.use_zep = False
                self.long_term_memory = LocalLongTermMemory(persistence_path, self.session_id)
        else:
            self.long_term_memory = LocalLongTermMemory(persistence_path, self.session_id)
            if not ZEP_AVAILABLE:
                print("✓ Using local memory store (Zep not available)")
            else:
                print("✓ Using local memory store")
        
        self.system_prompt = """You are a helpful AI assistant with advanced memory capabilities powered by Zep.
You have access to both short-term memory (current conversation) and long-term memory (facts from previous sessions).
When relevant information from long-term memory is provided, use them to give more contextual and personalized responses.
Your memory system allows you to build deep, contextual understanding over time."""
    
    def chat(
        self, 
        user_message: str, 
        use_long_term_memory: bool = True,
        store_in_long_term: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: The user's input message
            use_long_term_memory: Whether to search and use long-term memory
            store_in_long_term: Whether to store important facts from this conversation
            
        Returns:
            Dictionary containing response and metadata
        """
        # Search long-term memory for relevant context
        relevant_facts = []
        memory_summary = None
        
        if use_long_term_memory:
            if self.use_zep:
                # Get Zep memory summary
                memory_summary = self.long_term_memory.get_summary()
                relevant_facts = self.long_term_memory.search_memory(user_message)
            else:
                relevant_facts = self.long_term_memory.search_memory(user_message)
        
        # Build context from long-term memory
        long_term_context = ""
        if memory_summary:
            long_term_context += f"\n\nMemory Summary:\n{memory_summary}\n"
        
        if relevant_facts:
            long_term_context += "\n\nRelevant information from previous conversations:\n"
            for fact in relevant_facts:
                fact_text = fact.get('fact', fact.get('content', ''))
                long_term_context += f"- {fact_text}\n"
        
        # Add user message to short-term memory
        self.short_term_memory.add_message("user", user_message)
        
        # Also add to Zep if available
        if self.use_zep and isinstance(self.long_term_memory, ZepLongTermMemory):
            self.long_term_memory.add_message("user", user_message)
        
        # Prepare messages for API
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add long-term context if available
        if long_term_context:
            messages.append({
                "role": "system",
                "content": long_term_context
            })
        
        messages.extend(self.short_term_memory.get_messages())
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to short-term memory
            self.short_term_memory.add_message("assistant", assistant_message)
            
            # Also add to Zep if available
            if self.use_zep and isinstance(self.long_term_memory, ZepLongTermMemory):
                self.long_term_memory.add_message("assistant", assistant_message)
            
            # Extract and store important facts if requested
            if store_in_long_term:
                self._extract_and_store_facts(user_message, assistant_message)
            
            return {
                "response": assistant_message,
                "session_id": self.session_id,
                "model": self.model_name,
                "memory_type": "zep" if self.use_zep else "local",
                "relevant_facts_count": len(relevant_facts),
                "has_summary": bool(memory_summary),
                "tokens_used": response.usage.total_tokens if response.usage else None
            }
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            return {
                "response": error_message,
                "error": True,
                "session_id": self.session_id
            }
    
    def _extract_and_store_facts(self, user_message: str, assistant_message: str):
        """Extract important facts and store them in long-term memory."""
        # Simple heuristic: store user statements as potential facts
        if len(user_message) > 20 and not user_message.endswith("?"):
            self.long_term_memory.add_fact(
                fact=user_message,
                context=assistant_message[:200],
                importance=5
            )
    
    def add_to_long_term_memory(self, fact: str, context: str = "", importance: int = 5, metadata: Optional[Dict] = None):
        """Manually add a fact to long-term memory."""
        self.long_term_memory.add_fact(fact, context, importance, metadata)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.short_term_memory.messages
    
    def get_memory_summary(self) -> Optional[str]:
        """Get memory summary (only available with Zep)."""
        if self.use_zep and isinstance(self.long_term_memory, ZepLongTermMemory):
            return self.long_term_memory.get_summary()
        return None
    
    def clear_short_term_memory(self):
        """Clear the current conversation context."""
        self.short_term_memory.clear()
    
    def clear_long_term_memory(self):
        """Clear all persistent memory."""
        self.long_term_memory.clear()
    
    def export_session(self) -> Dict:
        """Export the current session state."""
        summary = self.get_memory_summary()
        
        return {
            "session_id": self.session_id,
            "memory_type": "zep" if self.use_zep else "local",
            "short_term_memory": self.short_term_memory.to_dict(),
            "memory_summary": summary,
            "long_term_facts_count": len(self.long_term_memory.get_all_facts()),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about the agent's memory."""
        facts = self.long_term_memory.get_all_facts()
        
        stats = {
            "session_id": self.session_id,
            "memory_type": "zep" if self.use_zep else "local",
            "short_term_messages": len(self.short_term_memory.messages),
            "long_term_facts": len(facts)
        }
        
        # Add local-specific stats if using local storage
        if not self.use_zep:
            stats["total_fact_accesses"] = sum(
                fact.get("access_count", 0) for fact in facts
            )
        
        return stats
