"""
ChatGPT Stateful Agent with Memory
Provides short-term and long-term memory capabilities for conversational AI.
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any
from openai import OpenAI
import tiktoken


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


class LongTermMemory:
    """Manages persistent memory across sessions."""
    
    def __init__(self, persistence_path: str = "./data/memory"):
        self.persistence_path = persistence_path
        os.makedirs(persistence_path, exist_ok=True)
        self.memory_file = os.path.join(persistence_path, "long_term_memory.json")
        self.facts: List[Dict[str, Any]] = []
        self.load()
    
    def add_fact(self, fact: str, context: str = "", importance: int = 5):
        """Store a fact in long-term memory."""
        fact_entry = {
            "fact": fact,
            "context": context,
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        self.facts.append(fact_entry)
        self.save()
    
    def search_facts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant facts (simple keyword matching)."""
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
        return relevant_facts[:top_k]
    
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


class StatefulAgent:
    """Main agent with both short-term and long-term memory."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-4",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        persistence_path: str = "./data/memory"
    ):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory(persistence_path)
        
        self.session_id = f"session_{int(time.time())}"
        self.system_prompt = """You are a helpful AI assistant with memory capabilities.
You have access to both short-term memory (current conversation) and long-term memory (facts from previous sessions).
When relevant facts from long-term memory are provided, use them to give more contextual and personalized responses."""
    
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
        if use_long_term_memory:
            relevant_facts = self.long_term_memory.search_facts(user_message)
        
        # Build context from long-term memory
        long_term_context = ""
        if relevant_facts:
            long_term_context = "\n\nRelevant information from previous conversations:\n"
            for fact in relevant_facts:
                long_term_context += f"- {fact['fact']}\n"
        
        # Add user message to short-term memory
        enhanced_message = user_message
        if long_term_context:
            enhanced_message += long_term_context
        
        self.short_term_memory.add_message("user", user_message)
        
        # Prepare messages for API
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.short_term_memory.get_messages())
        
        # If we have long-term context, add it as a system message
        if long_term_context:
            messages.insert(1, {
                "role": "system",
                "content": long_term_context
            })
        
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
            
            # Extract and store important facts if requested
            if store_in_long_term:
                self._extract_and_store_facts(user_message, assistant_message)
            
            return {
                "response": assistant_message,
                "session_id": self.session_id,
                "model": self.model_name,
                "relevant_facts_count": len(relevant_facts),
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
    
    def add_to_long_term_memory(self, fact: str, context: str = "", importance: int = 5):
        """Manually add a fact to long-term memory."""
        self.long_term_memory.add_fact(fact, context, importance)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.short_term_memory.messages
    
    def clear_short_term_memory(self):
        """Clear the current conversation context."""
        self.short_term_memory.clear()
    
    def clear_long_term_memory(self):
        """Clear all persistent memory."""
        self.long_term_memory.clear()
    
    def export_session(self) -> Dict:
        """Export the current session state."""
        return {
            "session_id": self.session_id,
            "short_term_memory": self.short_term_memory.to_dict(),
            "long_term_facts_count": len(self.long_term_memory.facts),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about the agent's memory."""
        return {
            "session_id": self.session_id,
            "short_term_messages": len(self.short_term_memory.messages),
            "long_term_facts": len(self.long_term_memory.facts),
            "total_fact_accesses": sum(
                fact.get("access_count", 0) 
                for fact in self.long_term_memory.facts
            )
        }
