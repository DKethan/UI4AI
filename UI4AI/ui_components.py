import streamlit as st
from typing import Callable, Dict, List, Optional

from .conversation_store import get_date_category


def render_sidebar(
        generate_title: Optional[Callable],
        count_tokens: Optional[Callable],
        new_conversation_label: str,
        show_edit_options: bool,
        primary_color: str,
        hover_color: str,
        date_grouping: bool,
        show_token_count: bool,
        max_title_length: int,
        reset_conversation_func: Callable,
        save_conversations_func: Callable
):
    """
    Render the sidebar with conversation history and controls.
    
    Args:
        generate_title: Function to generate titles for conversations
        count_tokens: Function to count tokens in conversations
        new_conversation_label: Label for the new conversation button
        show_edit_options: Whether to show edit options for conversations
        primary_color: Primary UI color
        hover_color: Hover UI color
        date_grouping: Whether to group conversations by date
        show_token_count: Whether to show token counts
        max_title_length: Maximum length for displayed conversation titles
        reset_conversation_func: Function to reset the current conversation
        save_conversations_func: Function to save conversations
    """
    # New chat button
    if st.button(new_conversation_label, use_container_width=True):
        reset_conversation_func()

    st.markdown("---")

    # Apply CSS styling
    apply_sidebar_styling()

    # Conversation list rendering
    sorted_convos = sorted(
        st.session_state.conversations.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )

    current_group = None
    for convo in sorted_convos:
        convo_id = convo["id"]
        is_current = convo_id == st.session_state.current_convo_id

        # Check if this conversation is being edited
        if st.session_state.edit_states.get(convo_id, False):
            render_edit_conversation_row(convo, convo_id, save_conversations_func)
            continue

        # Title formatting
        title = format_conversation_title(
            convo, max_title_length, show_token_count, count_tokens
        )

        # Date grouping
        if date_grouping:
            group = get_date_category(convo["created_at"])
            if group != current_group:
                st.markdown(f"**{group}**")
                current_group = group

        # Conversation row
        render_conversation_row(
            convo_id, title, is_current, show_edit_options,
            reset_conversation_func, save_conversations_func
        )


def render_edit_conversation_row(convo, convo_id, save_func):
    """Render a row for editing a conversation title"""
    with st.container():
        cols = st.columns([6, 2])
        with cols[0]:
            # Show text input for editing title
            new_title = st.text_input(
                "New title",
                value=convo["title"],
                key=f"edit_title_{convo_id}",
                label_visibility="collapsed"
            )
        with cols[1]:
            # Save button
            if st.button("Save", key=f"save_{convo_id}", use_container_width=True):
                # Update title and save
                st.session_state.conversations[convo_id]["title"] = new_title
                st.session_state.edit_states[convo_id] = False
                save_func()
                st.rerun()
            # Cancel button
            if st.button("Cancel", key=f"cancel_{convo_id}", use_container_width=True):
                st.session_state.edit_states[convo_id] = False
                st.rerun()


def render_conversation_row(
        convo_id, title, is_current, show_edit_options, 
        reset_func, save_func
):
    """Render a single conversation row in the sidebar"""
    with st.container():
        cols = st.columns([8, 1])  # Adjusted column ratio

        # Title column
        with cols[0]:
            btn = st.button(
                title,
                key=f"title_{convo_id}",
                use_container_width=True,
                help="Select conversation"
            )
            if btn:
                st.session_state.current_convo_id = convo_id
                st.session_state.messages = st.session_state.conversations[convo_id]["messages"]
                st.rerun()

        # Menu column
        with cols[1]:
            if st.session_state.menu_states.get(convo_id, False):
                render_conversation_menu(
                    convo_id, is_current, reset_func, save_func
                )
            else:
                if st.button("⋯", key=f"dots_{convo_id}",
                             type="secondary", use_container_width=True):
                    st.session_state.menu_states[convo_id] = True
                    st.rerun()


def render_conversation_menu(convo_id, is_current, reset_func, save_func):
    """Render the menu options for a conversation"""
    if st.button("✏️", key=f"edit_{convo_id}", help="Rename",
                 type="secondary", use_container_width=True):
        st.session_state.edit_states[convo_id] = True
        st.session_state.menu_states[convo_id] = False
        st.rerun()
    
    if st.button("🗑️", key=f"delete_{convo_id}", help="Delete",
                 type="secondary", use_container_width=True):
        del st.session_state.conversations[convo_id]
        if st.session_state.current_convo_id == convo_id:
            reset_func()
        else:
            save_func()
            st.rerun()
    
    if st.button("✕", key=f"close_{convo_id}", help="Close menu",
                 type="secondary", use_container_width=True):
        st.session_state.menu_states[convo_id] = False
        st.rerun()


def format_conversation_title(convo, max_length, show_token_count, count_tokens_func):
    """Format a conversation title for display"""
    title = (convo["title"][:max_length] + "...") if len(convo["title"]) > max_length else convo["title"]

    if show_token_count and count_tokens_func:
        title += f" ({convo.get('token_count', '?')})"
        
    return title


def render_welcome_screen(
    welcome_title: str,
    welcome_message: str,
    suggestions: Optional[List[str]] = None,
):
    """Render a welcome screen when there are no messages (optionally with suggestion chips)."""
    st.markdown(f"## {welcome_title}")
    st.markdown(welcome_message)
    if suggestions:
        st.markdown("---")
        for i, suggestion in enumerate(suggestions):
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.pending_suggestion = suggestion
                st.rerun()


def render_chat_history(user_avatar=None, assistant_avatar=None):
    """Display the chat message history."""
    for message in st.session_state.messages:
        avatar = user_avatar if message["role"] == "user" else assistant_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


def apply_sidebar_styling():
    """Apply CSS styling for ChatGPT-like sidebar: compact rows, hover, rounded corners."""
    st.markdown("""
    <style>
        /* Compact spacing in sidebar */
        div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.25rem;
        }
        /* Conversation list: rounded buttons, hover effect */
        div[data-testid="stSidebar"] button {
            border-radius: 0.5rem !important;
            padding: 0.5rem 0.75rem !important;
            min-height: 2.25rem !important;
            transition: background-color 0.15s ease;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: rgba(128, 128, 128, 0.2) !important;
        }
        /* Clean divider below New Chat */
        div[data-testid="stSidebar"] hr {
            margin: 0.5rem 0 !important;
            border-color: rgba(128, 128, 128, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_chat_header(header_title: str, byline_text: str):
    """Render a polished chat header in the sidebar."""
    st.sidebar.markdown(
        f"<h1 style='margin-bottom:0; font-size:1.75rem; font-weight:600; letter-spacing:-0.02em;'>{header_title}</h1>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"<p style='margin-top:0.25rem; font-size:0.85rem; opacity:0.85;'>{byline_text}</p>",
        unsafe_allow_html=True,
    )


def render_search_box():
    """Render a search box for finding conversations (call within st.sidebar context)."""
    search_query = st.text_input(
        "Search conversations",
        placeholder="Type to search...",
        key="conversation_search"
    )

    if search_query:
        from .conversation_store import search_conversations

        matching_ids = search_conversations(search_query)
        if matching_ids:
            st.markdown(f"Found {len(matching_ids)} matches")
        else:
            st.markdown("No matches found")

    return search_query
