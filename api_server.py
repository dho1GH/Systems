"""
REST API Server for ChatGPT Stateful Agent with Zep Memory
Compatible with N8N and other workflow automation tools.
"""

import os
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from agent_zep import StatefulAgentWithZep

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the agent
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MEMORY_PATH = os.getenv("MEMORY_PERSISTENCE_PATH", "./data/memory")
ZEP_API_URL = os.getenv("ZEP_API_URL")
ZEP_API_KEY = os.getenv("ZEP_API_KEY")

agent = StatefulAgentWithZep(
    api_key=API_KEY,
    model_name=MODEL_NAME,
    max_tokens=MAX_TOKENS,
    temperature=TEMPERATURE,
    zep_api_url=ZEP_API_URL,
    zep_api_key=ZEP_API_KEY,
    persistence_path=MEMORY_PATH,
    use_zep=bool(ZEP_API_URL)
)


@app.route("/", methods=["GET"])
def index():
    """Health check endpoint."""
    memory_type = "Zep" if agent.use_zep else "Local"
    return jsonify({
        "status": "healthy",
        "service": "ChatGPT Stateful Agent with Zep Memory",
        "version": "2.0.0",
        "memory_type": memory_type,
        "session_id": agent.session_id
    })


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    
    Expected JSON body:
    {
        "message": "User's message",
        "use_long_term_memory": true,  // optional, default true
        "store_in_long_term": false    // optional, default false
    }
    """
    try:
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data["message"]
        use_long_term = data.get("use_long_term_memory", True)
        store_long_term = data.get("store_in_long_term", False)
        
        response = agent.chat(
            user_message=message,
            use_long_term_memory=use_long_term,
            store_in_long_term=store_long_term
        )
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/memory/add", methods=["POST"])
def add_memory():
    """
    Add a fact to long-term memory.
    
    Expected JSON body:
    {
        "fact": "The fact to store",
        "context": "Optional context",  // optional
        "importance": 5                  // optional, 1-10
    }
    """
    try:
        data = request.get_json()
        
        if not data or "fact" not in data:
            return jsonify({
                "error": "Missing 'fact' field in request body"
            }), 400
        
        fact = data["fact"]
        context = data.get("context", "")
        importance = data.get("importance", 5)
        
        agent.add_to_long_term_memory(fact, context, importance)
        
        return jsonify({
            "status": "success",
            "message": "Fact added to long-term memory"
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/memory/search", methods=["POST"])
def search_memory():
    """
    Search long-term memory.
    
    Expected JSON body:
    {
        "query": "Search query",
        "top_k": 5  // optional, default 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or "query" not in data:
            return jsonify({
                "error": "Missing 'query' field in request body"
            }), 400
        
        query = data["query"]
        top_k = data.get("top_k", 5)
        
        # Use the appropriate method based on memory type
        if hasattr(agent.long_term_memory, 'search_memory'):
            facts = agent.long_term_memory.search_memory(query, top_k)
        else:
            facts = agent.long_term_memory.search_facts(query, top_k)
        
        return jsonify({
            "facts": facts,
            "count": len(facts)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/memory/facts", methods=["GET"])
def get_all_facts():
    """Get all facts from long-term memory."""
    try:
        facts = agent.long_term_memory.get_all_facts()
        return jsonify({
            "facts": facts,
            "count": len(facts)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/memory/clear", methods=["POST"])
def clear_memory():
    """
    Clear memory.
    
    Expected JSON body:
    {
        "type": "short" | "long" | "all"  // default "short"
    }
    """
    try:
        data = request.get_json() or {}
        memory_type = data.get("type", "short")
        
        if memory_type == "short":
            agent.clear_short_term_memory()
            message = "Short-term memory cleared"
        elif memory_type == "long":
            agent.clear_long_term_memory()
            message = "Long-term memory cleared"
        elif memory_type == "all":
            agent.clear_short_term_memory()
            agent.clear_long_term_memory()
            message = "All memory cleared"
        else:
            return jsonify({
                "error": "Invalid memory type. Use 'short', 'long', or 'all'"
            }), 400
        
        return jsonify({
            "status": "success",
            "message": message
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/session/history", methods=["GET"])
def get_history():
    """Get the current conversation history."""
    try:
        history = agent.get_conversation_history()
        return jsonify({
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/session/export", methods=["GET"])
def export_session():
    """Export the current session state."""
    try:
        session_data = agent.export_session()
        return jsonify(session_data)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/memory/summary", methods=["GET"])
def get_memory_summary():
    """Get memory summary (only available with Zep)."""
    try:
        summary = agent.get_memory_summary()
        if summary:
            return jsonify({
                "summary": summary,
                "available": True
            })
        else:
            return jsonify({
                "summary": None,
                "available": False,
                "message": "Memory summary only available with Zep"
            })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get memory statistics."""
    try:
        stats = agent.get_memory_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("AGENT_PORT", "5000"))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
