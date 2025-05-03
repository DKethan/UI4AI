"""
UI4AI: A Streamlit UI for LLM chat applications.

This package provides a simple, plug-and-play interface for creating
chat applications with Streamlit, handling conversation history,
persistence, and UI components.

Example:
    from UI4AI import run_chat
    
    def generate_response(messages):
        # Your LLM integration here
        return "I'm a chatbot response"
    
    run_chat(generate_response=generate_response)
"""

__version__ = "0.2.0"

# Main interface function
from .chat_ui import run_chat

# Conversation storage functions
from .conversation_store import (
    load_conversations, 
    save_conversations,
    export_conversations,
    import_conversations,
    backup_conversations,
    search_conversations,
    get_conversation_statistics
)

# Message handling functions
from .message_handler import (
    create_system_message,
    extract_code_blocks,
    format_markdown_message
)

# Session management functions
from .session_manager import (
    reset_conversation,
    delete_conversation,
    update_conversation_title,
    switch_conversation,
    export_session_data
)

__all__ = [
    # Main interface
    "run_chat",
    
    # Conversation storage
    "load_conversations",
    "save_conversations",
    "export_conversations",
    "import_conversations",
    "backup_conversations",
    "search_conversations",
    "get_conversation_statistics",
    
    # Message handling
    "create_system_message",
    "extract_code_blocks",
    "format_markdown_message",
    
    # Session management
    "reset_conversation",
    "delete_conversation",
    "update_conversation_title",
    "switch_conversation",
    "export_session_data"
]
