from typing import List, Dict, Callable, Optional

import streamlit as st

from .conversation_store import save_conversations
from .session_manager import init_session_state, reset_conversation
from .ui_components import render_sidebar, render_chat_history, render_chat_header
from .message_handler import handle_user_input


def run_chat(
        generate_response: Optional[Callable[[List[Dict]], str]],
        generate_title: Optional[Callable[[str], str]] = None,
        count_tokens: Optional[Callable[[List[Dict]], int]] = None,
        page_title: str = "AI Chat",
        header_title: str = "UI4AI",
        byline_text: str = "Powered by Kethan Dosapati",
        layout: str = "wide",
        new_conversation_label: str = "➕ New Chat",
        chat_placeholder: str = "Ask me anything...",
        spinner_text: str = "Thinking...",
        max_history_tokens: Optional[int] = None,
        show_edit_options: bool = True,
        primary_color: str = "#4f8bf9",
        hover_color: str = "#f0f2f6",
        date_grouping: bool = True,
        show_token_count: bool = True,
        max_title_length: int = 25,
        storage_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
        enable_search: bool = False
):
    """
    Run the enhanced Streamlit chat UI with all features.
    
    Args:
        generate_response: Function that takes messages and returns a response
        generate_title: Optional function to generate a title from the first message
        count_tokens: Optional function to count tokens in a conversation
        page_title: Browser tab title
        header_title: Header title displayed in the sidebar
        byline_text: Byline text displayed under the header
        layout: Streamlit layout ("wide" or "centered")
        new_conversation_label: Label for the new conversation button
        chat_placeholder: Placeholder text for the chat input
        spinner_text: Text displayed while generating a response
        max_history_tokens: Maximum tokens to keep in history (requires count_tokens)
        show_edit_options: Whether to show edit options in the conversation menu
        primary_color: Primary UI color
        hover_color: Hover UI color
        date_grouping: Whether to group conversations by date
        show_token_count: Whether to show token counts for conversations
        max_title_length: Maximum length for displayed conversation titles
        storage_path: Optional custom path to store conversations
        system_prompt: Optional system prompt to include in each conversation
        enable_search: Whether to enable conversation search feature
    """
    # Initialize session state
    init_session_state(storage_path)
    
    # Configure page
    st.set_page_config(page_title=page_title, layout=layout)

    # Render chat header
    render_chat_header(header_title, byline_text)

    # Add system message if provided
    if system_prompt and st.session_state.messages:
        from .message_handler import create_system_message
        create_system_message(system_prompt)

    # Define a save function to use in components (with path from session state)
    def save_func():
        save_conversations(st.session_state.storage_path)

    # Render sidebar with search if enabled
    with st.sidebar:
        if enable_search:
            from .ui_components import render_search_box
            render_search_box()
            
        render_sidebar(
            generate_title=generate_title,
            count_tokens=count_tokens,
            new_conversation_label=new_conversation_label,
            show_edit_options=show_edit_options,
            primary_color=primary_color,
            hover_color=hover_color,
            date_grouping=date_grouping,
            show_token_count=show_token_count,
            max_title_length=max_title_length,
            reset_conversation_func=reset_conversation,
            save_conversations_func=save_func
        )

    # Render main chat interface
    render_chat_history()
    
    # Handle user input
    handle_user_input(
        generate_response=generate_response,
        generate_title=generate_title,
        count_tokens=count_tokens,
        chat_placeholder=chat_placeholder,
        spinner_text=spinner_text,
        max_history_tokens=max_history_tokens,
        save_conversations_func=save_func
    )