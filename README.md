# ChatGPT Stateful Agent with Zep Memory

A powerful ChatGPT-based conversational agent with both short-term and long-term memory capabilities using **Zep** - a long-term memory store for AI assistants. Designed for integration with workflow automation tools like N8N.

## Features

### 🧠 Advanced Memory with Zep
- **Short-term Memory**: Maintains conversation context within the current session (up to 10 messages)
- **Long-term Memory with Zep**: Vector-based persistent memory with semantic search
- **Automatic Summarization**: Zep automatically generates conversation summaries
- **Fallback Support**: Works with local JSON storage if Zep is unavailable

### 🔌 Integrations
- **OpenAI API**: Leverages GPT-4 or other OpenAI models
- **Zep Memory Store**: Production-grade long-term memory with PostgreSQL backend
- **N8N Compatible**: RESTful API endpoints for workflow automation
- **Flask REST API**: Easy integration with any HTTP client
- **Docker Support**: Complete Docker Compose setup included

### 📊 Key Capabilities
- Context-aware conversations with intelligent memory recall
- Semantic search across conversation history
- Fact storage with importance ranking
- Automatic memory summarization (via Zep)
- Session management and export
- Token usage tracking
- Configurable model parameters

## Quick Start

### Option 1: Docker (Recommended)

The easiest way to get started with full Zep memory support:

```bash
# Clone the repository
git clone https://github.com/dho1GH/Systems.git
cd Systems

# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key_here

# Start all services (Zep, PostgreSQL, Agent)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f agent
```

The agent API will be available at `http://localhost:5000` and Zep at `http://localhost:8000`.

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/dho1GH/Systems.git
cd Systems

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

#### Start Zep (Optional but Recommended)

```bash
# Using Docker
docker run -d -p 8000:8000 \
  -e ZEP_STORE_TYPE=memory \
  --name zep \
  ghcr.io/getzep/zep:latest
```

Or follow [Zep installation guide](https://docs.getzep.com/deployment/quickstart/)

### Configuration

Edit `.env` file with your settings:

```env
OPENAI_API_KEY=your_openai_api_key_here
AGENT_PORT=5000
MEMORY_PERSISTENCE_PATH=./data/memory
MODEL_NAME=gpt-4
MAX_TOKENS=2000
TEMPERATURE=0.7

# Zep Configuration (optional - uses local storage if not set)
ZEP_API_URL=http://localhost:8000
ZEP_API_KEY=optional_zep_api_key
```

### Usage Options

#### Option A: Python API (Direct Usage)

```python
from agent_zep import StatefulAgentWithZep

# Initialize agent with Zep
agent = StatefulAgentWithZep(
    api_key="your-openai-api-key",
    model_name="gpt-4",
    zep_api_url="http://localhost:8000",  # Optional
    use_zep=True  # Set False for local storage fallback
)

# Chat with short-term memory
response = agent.chat("Hello! My name is Alice.")
print(response['response'])

# Follow-up question (agent remembers context)
response = agent.chat("What's my name?")
print(response['response'])  # Will recall "Alice"

# Add to long-term memory
agent.add_to_long_term_memory(
    fact="Alice prefers Python programming",
    context="Programming preferences",
    importance=8
)

# Chat using long-term memory (with Zep semantic search)
response = agent.chat(
    "What programming languages do I like?",
    use_long_term_memory=True
)
print(response['response'])

# Get memory summary (Zep feature)
summary = agent.get_memory_summary()
if summary:
    print(f"Memory summary: {summary}")
```

**Run the example:**

```bash
python example_usage.py
```

#### Option B: REST API Server (N8N Integration)

```bash
# Start the API server
python api_server.py
```

The server runs on port 5000 (configurable via `AGENT_PORT` environment variable).

**API Endpoints:**

- `GET /` - Health check (shows memory type: Zep or Local)
- `POST /chat` - Send a message
- `POST /memory/add` - Add fact to long-term memory
- `POST /memory/search` - Search long-term memory
- `GET /memory/facts` - Get all stored facts
- `GET /memory/summary` - Get memory summary (Zep only)
- `POST /memory/clear` - Clear memory (short/long/all)
- `GET /session/history` - Get conversation history
- `GET /session/export` - Export session data
- `GET /stats` - Get memory statistics

**Example cURL requests:**

```bash
# Chat with the agent
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! Tell me about AI."}'

# Add a fact to long-term memory
curl -X POST http://localhost:5000/memory/add \
  -H "Content-Type: application/json" \
  -d '{
    "fact": "User is interested in machine learning",
    "context": "Technical interests",
    "importance": 8
  }'

# Search long-term memory
curl -X POST http://localhost:5000/memory/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'

# Get conversation history
curl http://localhost:5000/session/history

# Get memory statistics
curl http://localhost:5000/stats

# Get memory summary (Zep only)
curl http://localhost:5000/memory/summary
```

## What is Zep?

**Zep** is a long-term memory store specifically designed for AI assistants and agents. It provides:

- **Vector-based Memory**: Semantic search using embeddings
- **Automatic Summarization**: Intelligently summarizes conversations
- **PostgreSQL Backend**: Production-ready persistent storage
- **Fact Extraction**: Automatically extracts important facts from conversations
- **Temporal Memory**: Understands time-based context
- **High Performance**: Optimized for real-time AI applications

### Why Use Zep?

1. **Better Memory Recall**: Semantic search finds relevant context even without exact keyword matches
2. **Automatic Summaries**: No manual fact curation needed
3. **Scalable**: Handles thousands of conversations efficiently
4. **Production Ready**: Built for real-world AI applications
5. **Easy Integration**: Simple REST API

Learn more at [getzep.com](https://www.getzep.com)

#### Option C: Zep Dashboard

If you're running Zep, you can view memory data through the Zep API:

```bash
# View session data
curl http://localhost:8000/api/v1/sessions/{session_id}

# View session memory
curl http://localhost:8000/api/v1/sessions/{session_id}/memory
```

## Architecture

### Components

1. **StatefulAgentWithZep** (`agent_zep.py`)
   - Main agent class coordinating memory and OpenAI API
   - Handles chat interactions and context management
   - Integrates with Zep or falls back to local storage

2. **ShortTermMemory**
   - In-memory storage for current conversation
   - Automatically manages message history with size limits

3. **ZepLongTermMemory**
   - Zep-based persistent memory with vector search
   - Automatic summarization and fact extraction
   - Session management

4. **LocalLongTermMemory** (Fallback)
   - JSON-based local storage when Zep unavailable
   - Simple keyword-based search

5. **API Server** (`api_server.py`)
   - Flask-based REST API
   - CORS-enabled for web integrations
   - N8N and workflow tool compatible

### Memory Architecture with Zep

```
┌─────────────────────────────────────────┐
│      StatefulAgentWithZep               │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │   ShortTermMemory (RAM)           │  │
│  │   - Last 10 messages              │  │
│  │   - Current conversation context  │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │   Zep Memory Store                │  │
│  │   - Vector-based search           │  │
│  │   - Automatic summaries           │  │
│  │   - Fact extraction               │  │
│  │   - PostgreSQL backend            │  │
│  └───────────────────────────────────┘  │
│          │                               │
│          │ Fallback                      │
│          ▼                               │
│  ┌───────────────────────────────────┐  │
│  │   LocalLongTermMemory (Disk)      │  │
│  │   - JSON-based storage            │  │
│  │   - Keyword search                │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │   OpenAI API Integration          │  │
│  │   - GPT-4 / GPT-3.5               │  │
│  │   - Configurable parameters       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## N8N Integration Example

Here's how to use the agent in an N8N workflow:

1. **HTTP Request Node** - Send message to agent
   - Method: POST
   - URL: `http://localhost:5000/chat`
   - Body: `{"message": "{{ $json.userInput }}"}`

2. **Process Response** - Extract agent's reply
   - Expression: `{{ $json.response }}`

3. **Store Important Info** - Add to long-term memory
   - Method: POST
   - URL: `http://localhost:5000/memory/add`
   - Body: `{"fact": "{{ $json.extractedFact }}", "importance": 8}`

### Sample N8N Workflow JSON

```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "chatbot",
        "method": "POST"
      }
    },
    {
      "name": "Chat with Agent",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://localhost:5000/chat",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "{\"message\": \"{{ $json.body.message }}\"}"
      }
    },
    {
      "name": "Return Response",
      "type": "n8n-nodes-base.respond",
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ $json }}"
      }
    }
  ]
}
```

## Use Cases

### 1. Customer Support Chatbot
- Remember customer preferences and history
- Provide personalized responses based on past interactions
- Track important customer information

### 2. Personal AI Assistant
- Maintain context across multiple conversations
- Remember user preferences and habits
- Provide contextual recommendations

### 3. Educational Tutor
- Track student learning progress
- Remember areas of difficulty
- Provide personalized learning paths

### 4. Research Assistant
- Store important research findings
- Connect related concepts across sessions
- Build knowledge base over time

## Advanced Features

### Memory Importance Ranking

Facts are stored with importance levels (1-10):
- **1-3**: Low importance (casual mentions)
- **4-6**: Medium importance (preferences, general info)
- **7-9**: High importance (critical facts, key preferences)
- **10**: Critical importance (identity, core values)

### Access Tracking

Long-term memory tracks:
- Number of times each fact is accessed
- Last access timestamp
- Context of original storage

### Configurable Parameters

Customize agent behavior:
- `model_name`: Choose OpenAI model (gpt-4, gpt-3.5-turbo, etc.)
- `max_tokens`: Control response length
- `temperature`: Adjust creativity (0.0-2.0)
- `max_messages`: Short-term memory size

## Development

### Project Structure

```
Systems/
├── agent.py                 # Legacy agent (basic memory)
├── agent_zep.py            # Main agent with Zep integration
├── api_server.py           # REST API server
├── example_usage.py        # Python usage examples
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image
├── docker-compose.yml      # Full stack deployment
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── data/                 # Memory storage (created at runtime)
    └── memory/
        └── *.json        # Local fallback storage
```

### Testing

```python
# Test with Zep
from agent_zep import StatefulAgentWithZep

agent = StatefulAgentWithZep(
    api_key="your-key",
    zep_api_url="http://localhost:8000",
    use_zep=True
)
result = agent.chat("Hello!")
assert 'response' in result
assert agent.use_zep == True

# Test memory
agent.add_to_long_term_memory("Test fact", "context", 5)
facts = agent.long_term_memory.search_memory("Test", 5)
assert len(facts) > 0

# Test fallback to local storage
agent_local = StatefulAgentWithZep(
    api_key="your-key",
    use_zep=False
)
assert agent_local.use_zep == False
```

## Security Considerations

- Store API keys in environment variables, never in code
- Use `.gitignore` to exclude `.env` files from version control
- Implement rate limiting in production deployments
- Sanitize user inputs before processing
- Use HTTPS for API endpoints in production

## Performance Tips

1. **Model Selection**: Use `gpt-3.5-turbo` for faster, cost-effective responses
2. **Token Limits**: Adjust `max_tokens` based on use case
3. **Memory Size**: Limit short-term memory to prevent context overflow
4. **Batch Operations**: Use API efficiently by batching related queries

## Troubleshooting

### Common Issues

**Issue**: "OpenAI API key not found"
- **Solution**: Set `OPENAI_API_KEY` in `.env` file

**Issue**: "Module 'zep_python' not found"
- **Solution**: Run `pip install zep-python` or `pip install -r requirements.txt`

**Issue**: "Cannot connect to Zep"
- **Solution**: 
  - Check if Zep is running: `curl http://localhost:8000/healthz`
  - Start Zep with Docker: `docker-compose up -d zep`
  - Or set `use_zep=False` to use local storage

**Issue**: Memory not persisting (Zep mode)
- **Solution**: Check Zep PostgreSQL connection and ensure database is running

**Issue**: Memory not persisting (Local mode)
- **Solution**: Check write permissions for `MEMORY_PERSISTENCE_PATH`

**Issue**: Rate limit errors
- **Solution**: Implement request throttling or upgrade OpenAI plan

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- OpenAI for GPT models
- Zep for advanced memory management
- N8N for workflow automation inspiration
- Flask for lightweight API framework

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.