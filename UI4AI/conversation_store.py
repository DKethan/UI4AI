import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import streamlit as st


def load_conversations(file_path: Optional[str] = None) -> Dict:
    """
    Load conversations from a JSON file.
    
    Args:
        file_path: Path to the conversations JSON file. If None, uses 'conversations.json'
        
    Returns:
        Dictionary of conversations or empty dict if file not found
    """
    try:
        path = file_path or "conversations.json"
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
        return {}


def save_conversations(file_path: Optional[str] = None):
    """
    Save conversations to a JSON file.
    
    Args:
        file_path: Path to save conversations. If None, uses 'conversations.json'
    """
    try:
        path = file_path or "conversations.json"
        with open(path, "w") as f:
            json.dump(st.session_state.conversations, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error saving conversations: {e}")


def get_date_category(created_at: str) -> str:
    """
    Determine the display category for a conversation based on its creation date.
    
    Args:
        created_at: ISO format datetime string
        
    Returns:
        String representation of the date category (Today, Yesterday, day of week, or date)
    """
    created_date = datetime.fromisoformat(created_at).date()
    today = datetime.now().date()
    delta = today - created_date

    if delta.days == 0:
        return "Today"
    elif delta.days == 1:
        return "Yesterday"
    elif delta.days < 7:
        return created_date.strftime("%A")
    return created_date.strftime("%b %-d, %Y")


def export_conversations(file_path: str, format_type: str = "json") -> bool:
    """
    Export conversations to a file in the specified format.
    
    Args:
        file_path: Path where the export file will be saved
        format_type: Format type ('json' or 'txt')
        
    Returns:
        True if export successful, False otherwise
    """
    try:
        if format_type.lower() == "json":
            with open(file_path, "w") as f:
                json.dump(st.session_state.conversations, f, indent=2, default=str)
        elif format_type.lower() == "txt":
            with open(file_path, "w") as f:
                for convo_id, convo in st.session_state.conversations.items():
                    f.write(f"# Conversation: {convo['title']}\n")
                    f.write(f"# Date: {convo['created_at']}\n\n")
                    
                    for msg in convo['messages']:
                        f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")
                    
                    f.write("-" * 80 + "\n\n")
        else:
            st.error(f"Unsupported export format: {format_type}")
            return False
        
        return True
    except Exception as e:
        st.error(f"Error exporting conversations: {e}")
        return False


def import_conversations(file_path: str) -> bool:
    """
    Import conversations from a JSON file and merge with existing conversations.
    
    Args:
        file_path: Path to the JSON file containing conversations
        
    Returns:
        True if import successful, False otherwise
    """
    try:
        with open(file_path, "r") as f:
            imported_convos = json.load(f)
        
        # Merge with existing conversations
        for convo_id, convo in imported_convos.items():
            # Skip if conversation already exists
            if convo_id in st.session_state.conversations:
                continue
            
            st.session_state.conversations[convo_id] = convo
        
        save_conversations()
        return True
    except Exception as e:
        st.error(f"Error importing conversations: {e}")
        return False


def backup_conversations(backup_dir: str) -> bool:
    """
    Create a timestamped backup of conversations.
    
    Args:
        backup_dir: Directory where backups will be stored
        
    Returns:
        True if backup successful, False otherwise
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"conversations_backup_{timestamp}.json")
        
        # Save conversations to backup file
        with open(backup_path, "w") as f:
            json.dump(st.session_state.conversations, f, indent=2, default=str)
        
        return True
    except Exception as e:
        st.error(f"Error creating backup: {e}")
        return False


def search_conversations(query: str) -> List[str]:
    """
    Search conversations for a query string.
    
    Args:
        query: Search string to look for in conversation titles and messages
        
    Returns:
        List of conversation IDs matching the query
    """
    if not query:
        return []
    
    query = query.lower()
    matching_ids = []
    
    for convo_id, convo in st.session_state.conversations.items():
        # Check title
        if query in convo.get('title', '').lower():
            matching_ids.append(convo_id)
            continue
        
        # Check messages
        for msg in convo.get('messages', []):
            if query in msg.get('content', '').lower():
                matching_ids.append(convo_id)
                break
    
    return matching_ids


def get_conversation_statistics() -> Dict[str, Any]:
    """
    Calculate statistics about stored conversations.
    
    Returns:
        Dictionary with conversation statistics
    """
    conversations = st.session_state.conversations
    
    if not conversations:
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "avg_messages_per_conversation": 0,
            "oldest_conversation": None,
            "newest_conversation": None
        }
    
    # Calculate stats
    total_conversations = len(conversations)
    total_messages = sum(len(convo.get('messages', [])) for convo in conversations.values())
    avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
    
    # Find oldest and newest conversations
    dates = [(convo_id, convo.get('created_at')) 
             for convo_id, convo in conversations.items() 
             if convo.get('created_at')]
    
    oldest_id, newest_id = None, None
    
    if dates:
        dates.sort(key=lambda x: x[1])
        oldest_id = dates[0][0]
        newest_id = dates[-1][0]
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "avg_messages_per_conversation": round(avg_messages, 1),
        "oldest_conversation": oldest_id,
        "newest_conversation": newest_id
    }
