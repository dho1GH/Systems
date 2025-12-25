# Systems

An intelligent agent system that combines OpenAI's powerful language models with Zep's memory management for persistent, context-aware conversations.

## Features

- **OpenAI Integration**: Leverages OpenAI's GPT models for natural language understanding and generation
- **Zep Memory Management**: Persistent conversation memory with automatic summarization
- **Session Management**: Support for multiple concurrent conversation sessions
- **Flexible Configuration**: Easy customization through environment variables

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Zep server (optional, can run locally or use cloud instance)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dho1GH/Systems.git
cd Systems
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
ZEP_API_URL=http://localhost:8000
ZEP_API_KEY=your_zep_api_key_here  # Optional, depending on your Zep setup
```

## Quick Start

### Running the Example

```bash
python example.py
```

This will start an interactive chat session where you can:
- Chat with the AI agent
- Type `quit` to exit
- Type `clear` to clear conversation memory
- Type `summary` to see a summary of the conversation

### Using the Agent in Your Code

```python
from agent import ZepOpenAIAgent
import uuid

# Create a new agent instance
session_id = str(uuid.uuid4())
agent = ZepOpenAIAgent(session_id=session_id, user_id="user123")

# Send a message
response = agent.chat("Hello, how are you?")
print(response)

# Continue the conversation (with memory)
response = agent.chat("What did I just ask you?")
print(response)

# Clear conversation memory
agent.clear_memory()
```

## Architecture

### Components

1. **config.py**: Configuration management using environment variables
2. **agent.py**: Main agent implementation with OpenAI and Zep integration
3. **example.py**: Interactive demo application

### How It Works

1. **User Input**: The user sends a message to the agent
2. **Memory Retrieval**: The agent retrieves conversation history from Zep
3. **OpenAI Processing**: The message and history are sent to OpenAI's API
4. **Response Generation**: OpenAI generates a contextually relevant response
5. **Memory Storage**: The conversation turn is saved to Zep for future reference

## Configuration Options

The following environment variables can be set in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | Your OpenAI API key | Required |
| OPENAI_MODEL | OpenAI model to use | gpt-4 |
| ZEP_API_URL | URL of your Zep server | http://localhost:8000 |
| ZEP_API_KEY | Zep API key (if required) | None |
| AGENT_NAME | Name of the agent | Assistant |
| MAX_TOKENS | Maximum tokens in response | 2000 |
| TEMPERATURE | Response randomness (0-1) | 0.7 |

## Setting Up Zep

### Option 1: Local Docker Instance

```bash
docker run -d -p 8000:8000 ghcr.io/getzep/zep:latest
```

### Option 2: Zep Cloud

Sign up at [getzep.com](https://www.getzep.com) and use the provided API URL and key.

## Advanced Usage

### Custom System Prompt

```python
agent = ZepOpenAIAgent(session_id=session_id)
agent.system_prompt = "You are a helpful coding assistant specializing in Python."
```

### Using Without History

```python
# One-off question without conversation context
response = agent.chat("What is Python?", use_history=False)
```

### Getting Memory Summary

```python
summary = agent.get_memory_summary()
if summary:
    print(f"Conversation summary: {summary}")
```

## Troubleshooting

### "OPENAI_API_KEY is required"
Make sure you've created a `.env` file and added your OpenAI API key.

### "Could not retrieve memory from Zep"
- Check that your Zep server is running
- Verify the `ZEP_API_URL` is correct
- If using Zep Cloud, ensure `ZEP_API_KEY` is set

### Connection Issues
- Ensure you have an active internet connection
- Check that API keys are valid and not expired
- Verify firewall settings aren't blocking the connections

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Zep Documentation](https://docs.getzep.com)
- [Python dotenv](https://github.com/theskumar/python-dotenv)