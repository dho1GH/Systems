"""
OpenAI and Zep Agent Implementation
"""
from typing import List, Optional, Dict
import openai
from zep_python.client import Zep
from zep_python import Message
from config import Config


class ZepOpenAIAgent:
    """
    An agent that uses OpenAI for natural language processing
    and Zep for conversation memory management.
    """
    
    def __init__(self, session_id: str, user_id: Optional[str] = None):
        """
        Initialize the agent with OpenAI and Zep
        
        Args:
            session_id: Unique identifier for the conversation session
            user_id: Optional user identifier
        """
        Config.validate()
        
        self.session_id = session_id
        self.user_id = user_id or "default_user"
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Initialize Zep client
        self.zep_client = None
        if Config.ZEP_API_KEY:
            self.zep_client = Zep(
                base_url=Config.ZEP_API_URL,
                api_key=Config.ZEP_API_KEY
            )
        else:
            self.zep_client = Zep(base_url=Config.ZEP_API_URL)
        
        self.system_prompt = f"You are {Config.AGENT_NAME}, a helpful AI assistant."
    
    def _get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Retrieve conversation history from Zep
        
        Returns:
            List of message dictionaries
        """
        try:
            memory = self.zep_client.memory.get(self.session_id)
            
            messages = []
            if memory and memory.messages:
                for msg in memory.messages:
                    # role_type is the primary field, role is kept for backward compatibility
                    role = msg.role_type if msg.role_type else msg.role
                    messages.append({
                        "role": role,
                        "content": msg.content
                    })
            
            return messages
        except Exception as e:
            print(f"Warning: Could not retrieve memory from Zep: {e}")
            return []
    
    def _save_to_memory(self, user_message: str, assistant_message: str):
        """
        Save the conversation turn to Zep
        
        Args:
            user_message: The user's message
            assistant_message: The assistant's response
        """
        try:
            messages = [
                Message(role_type="user", content=user_message),
                Message(role_type="assistant", content=assistant_message)
            ]
            
            self.zep_client.memory.add(self.session_id, messages=messages)
        except Exception as e:
            print(f"Warning: Could not save memory to Zep: {e}")
    
    def chat(self, user_message: str, use_history: bool = True) -> str:
        """
        Send a message and get a response from the agent
        
        Args:
            user_message: The user's input message
            use_history: Whether to include conversation history
        
        Returns:
            The agent's response
        """
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history from Zep if requested
        if use_history:
            history = self._get_conversation_history()
            messages.extend(history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get response from OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=messages,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE
            )
            
            assistant_message = response.choices[0].message.content
            
            # Save to Zep memory
            self._save_to_memory(user_message, assistant_message)
            
            return assistant_message
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_memory(self):
        """Clear the conversation memory for this session"""
        try:
            self.zep_client.memory.delete(self.session_id)
            print(f"Memory cleared for session: {self.session_id}")
        except Exception as e:
            print(f"Warning: Could not clear memory: {e}")
    
    def get_memory_summary(self) -> Optional[str]:
        """
        Get a summary of the conversation from Zep
        
        Returns:
            Summary text or None
        """
        try:
            memory = self.zep_client.memory.get(self.session_id)
            if memory and hasattr(memory, 'summary') and memory.summary:
                if hasattr(memory.summary, 'content'):
                    return memory.summary.content
                return str(memory.summary)
            return None
        except Exception as e:
            print(f"Warning: Could not get memory summary: {e}")
            return None
