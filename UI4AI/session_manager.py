import uuid
from datetime import datetime
from typing import Dict, Optional

import streamlit as st

from .conversation_store import load_conversations, save_conversations


def init_session_state(storage_path: Optional[str] = None):
    """
    Initialize the session state with default values.
    
    Args:
        storage_path: Optional path to store conversations
    """
    defaults = {
        "conversations": load_conversations(storage_path),
        "current_convo_id": None,
        "messages": [],
        "editing_convo": None,
        "menu_open": None,
        "menu_states": {},
        "edit_states": {},
        "storage_path": storage_path
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_current_conversation() -> Optional[Dict]:
    """
    Get the current conversation from session state.
    
    Returns:
        Current conversation dict or None if no conversation is selected
    """
    if not st.session_state.current_convo_id:
        return None
    
    convo_id = st.session_state.current_convo_id
    return st.session_state.conversations.get(convo_id)


def reset_conversation():
    """Reset to a new conversation"""
    # Clear current conversation
    st.session_state.messages = []
    st.session_state.menu_open = None

    # Create new conversation immediately
    convo_id = str(uuid.uuid4())
    st.session_state.current_convo_id = convo_id

    st.session_state.conversations[convo_id] = {
        "id": convo_id,
        "title": "New Conversation",  # Default title until user sends first message
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "token_count": 0
    }
    
    save_conversations(st.session_state.storage_path)
    st.rerun()


def delete_conversation(convo_id: str):
    """
    Delete a conversation and update session state.
    
    Args:
        convo_id: ID of the conversation to delete
    """
    if convo_id in st.session_state.conversations:
        del st.session_state.conversations[convo_id]
        
        # If we deleted the current conversation, reset
        if st.session_state.current_convo_id == convo_id:
            reset_conversation()
        else:
            save_conversations(st.session_state.storage_path)
            st.rerun()


def update_conversation_title(convo_id: str, new_title: str):
    """
    Update the title of a conversation.
    
    Args:
        convo_id: ID of the conversation to update
        new_title: New title for the conversation
    """
    if convo_id in st.session_state.conversations:
        st.session_state.conversations[convo_id]["title"] = new_title
        save_conversations(st.session_state.storage_path)


def switch_conversation(convo_id: str):
    """
    Switch to a different conversation.
    
    Args:
        convo_id: ID of the conversation to switch to
    """
    if convo_id in st.session_state.conversations:
        st.session_state.current_convo_id = convo_id
        st.session_state.messages = st.session_state.conversations[convo_id]["messages"]
        st.rerun()


def export_session_data(file_path: str, format_type: str = "json") -> bool:
    """
    Export all session data to a file.
    
    Args:
        file_path: Path to save the export
        format_type: Format to use for the export ('json' or 'txt')
        
    Returns:
        True if export was successful, False otherwise
    """
    from .conversation_store import export_conversations
    return export_conversations(file_path, format_type)
