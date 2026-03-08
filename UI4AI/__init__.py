"""UI4AI: A Streamlit-based chat UI for LLM applications with history, persistence, and ChatGPT-style features."""

__version__ = "0.2.0"

# Main interface functions
from .chat_ui import run_chat, run_chat_openai

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
    get_current_conversation,
    reset_conversation,
    delete_conversation,
    update_conversation_title,
    switch_conversation,
    export_session_data,
)

__all__ = [
    # Main interface
    "run_chat",
    "run_chat_openai",
    
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
    "get_current_conversation",
    "reset_conversation",
    "delete_conversation",
    "update_conversation_title",
    "switch_conversation",
    "export_session_data",
]
