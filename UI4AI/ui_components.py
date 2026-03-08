import base64
import streamlit as st
from typing import Callable, Dict, List, Optional

from .conversation_store import get_date_category

# Default avatars matching conversational bot design: user=orange, assistant=golden
USER_AVATAR_SVG = base64.b64encode("""
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="16" fill="#e85d5d"/>
  <circle cx="16" cy="12" r="4" fill="white"/>
  <path d="M10 24c0-3.3 2.7-6 6-6s6 2.7 6 6v2H10v-2z" fill="white"/>
</svg>
""".strip().encode()).decode()
ASSISTANT_AVATAR_SVG = base64.b64encode("""
<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
  <circle cx="16" cy="16" r="16" fill="#f4b942"/>
  <rect x="10" y="10" width="12" height="6" rx="1" fill="white"/>
  <circle cx="13" cy="14" r="1" fill="#f4b942"/>
  <circle cx="19" cy="14" r="1" fill="#f4b942"/>
  <rect x="11" y="18" width="10" height="4" rx="1" fill="white"/>
</svg>
""".strip().encode()).decode()
DEFAULT_USER_AVATAR = f"data:image/svg+xml;base64,{USER_AVATAR_SVG}"
DEFAULT_ASSISTANT_AVATAR = f"data:image/svg+xml;base64,{ASSISTANT_AVATAR_SVG}"


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
        save_conversations_func: Callable,
        instructions_label: str = "Instructions",
        conversation_history_label: str = "Conversation History",
        header_title: str = "UI4AI",
        byline_text: Optional[str] = "Powered by Kethan Dosapati",
        enable_search: bool = False,
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
        instructions_label: Label for the Instructions section
        conversation_history_label: Label for the Conversation History section
        header_title: App title displayed at top of sidebar (e.g. UI4AI)
        byline_text: Optional byline under the title (e.g. Powered by ...)
        enable_search: If True, show search box above the conversation list
    """
    # App branding at top of sidebar
    st.markdown(
        f"<div style='margin-bottom:1rem;'>"
        f"<div style='font-size:1.5rem; font-weight:700; letter-spacing:-0.02em; color:#ececec;'>{header_title}</div>"
        + (f"<div style='font-size:0.8rem; color:rgba(236,236,236,0.7); margin-top:0.25rem;'>{byline_text}</div>" if byline_text else "")
        + f"</div>",
        unsafe_allow_html=True,
    )
    # Instructions section with book icon
    st.markdown(
        f"<div style='display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;'>"
        f"<span style='font-size:1rem;'>📖</span>"
        f"<span style='font-weight:600; font-size:0.95rem; color:#ececec;'>{instructions_label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Conversation History heading
    st.markdown(
        f"<p style='font-size:0.9rem; color:rgba(236,236,236,0.9); margin:0.5rem 0 0.75rem 0;'>{conversation_history_label}</p>",
        unsafe_allow_html=True,
    )

    # New chat button - styled to match reference (rounded, light border, transparent bg)
    if st.button(new_conversation_label, use_container_width=True, type="secondary"):
        reset_conversation_func()

    # Search box above conversation list (when enabled)
    if enable_search:
        render_search_box()

    # Apply CSS styling (must be before conversation list for proper styling)
    apply_sidebar_styling()

    # Conversation list: always keep full history in date order (don't disturb it)
    sorted_convos = sorted(
        st.session_state.conversations.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )

    search_query = ""
    matching_ids = set()
    if enable_search:
        search_query = (st.session_state.get("conversation_search") or "").strip()
        if search_query:
            from .conversation_store import search_conversations
            matching_ids = set(search_conversations(search_query))

    # When search is active: show matched conversations on top (no dates), then full history below
    if search_query and matching_ids:
        matched = [c for c in sorted_convos if c["id"] in matching_ids]
        st.markdown(
            "<p style='font-size:0.9rem; color:rgba(236,236,236,0.9); margin:0.5rem 0 0.75rem 0;'>Search results</p>",
            unsafe_allow_html=True,
        )
        for convo in matched:
            convo_id = convo["id"]
            is_current = convo_id == st.session_state.current_convo_id
            if st.session_state.edit_states.get(convo_id, False):
                render_edit_conversation_row(convo, convo_id, save_conversations_func)
                continue
            title = format_conversation_title(
                convo, max_title_length, show_token_count, count_tokens
            )
            render_conversation_row(
                convo_id, title, is_current, show_edit_options,
                reset_conversation_func, save_conversations_func
            )
        st.markdown(
            "<p style='font-size:0.9rem; color:rgba(236,236,236,0.9); margin:1rem 0 0.75rem 0;'>Conversation history</p>",
            unsafe_allow_html=True,
        )

    # Full conversation history in original date order (when searching, show only non-matches here to avoid duplicates)
    convos_to_list = [c for c in sorted_convos if c["id"] not in matching_ids] if (search_query and matching_ids) else sorted_convos
    current_group = None
    for convo in convos_to_list:
        convo_id = convo["id"]
        is_current = convo_id == st.session_state.current_convo_id

        if st.session_state.edit_states.get(convo_id, False):
            render_edit_conversation_row(convo, convo_id, save_conversations_func)
            continue

        title = format_conversation_title(
            convo, max_title_length, show_token_count, count_tokens
        )

        if date_grouping:
            group = get_date_category(convo["created_at"])
            if group != current_group:
                st.markdown(f"**{group}**")
                current_group = group

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

        # Title column - use primary for active (highlighted), secondary for inactive
        with cols[0]:
            btn = st.button(
                title,
                key=f"title_{convo_id}",
                use_container_width=True,
                help="Select conversation",
                type="primary" if is_current else "secondary",
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
    """Format a conversation title for display (single line: title + token count in brackets)."""
    # Reserve space for " (0)" or " (999)" so the full string fits on one line
    usable = max_length - (8 if show_token_count and count_tokens_func else 0)
    usable = max(12, usable)
    title = (convo["title"][:usable] + "...") if len(convo["title"]) > usable else convo["title"]

    if show_token_count and count_tokens_func:
        # Compute from messages so every conversation (including existing/loaded) shows token count
        messages = convo.get("messages", [])
        count = count_tokens_func(messages) if messages else 0
        title += f" ({count})"
        
    return title


def render_welcome_screen(
    welcome_title: str,
    welcome_message: str,
    suggestions: Optional[List[str]] = None,
):
    """Render a welcome screen when there are no messages (optionally with suggestion chips)."""
    # Spacer so content isn't pushed to top (avoids "looks so up" layout)
    st.markdown(
        '<div style="min-height: 30vh;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h2 style='margin:0 0 0.5rem 0; font-size:1.5rem; font-weight:600; color:#ececec;'>{welcome_title}</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='margin:0 0 1.5rem 0; font-size:1rem; color:rgba(236,236,236,0.8);'>{welcome_message}</p>",
        unsafe_allow_html=True,
    )
    if suggestions:
        for i, suggestion in enumerate(suggestions):
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                st.session_state.pending_suggestion = suggestion
                st.rerun()


def render_chat_history(user_avatar=None, assistant_avatar=None):
    """Display the chat message history (system messages are hidden, still sent to LLM)."""
    user_avatar = user_avatar or DEFAULT_USER_AVATAR
    assistant_avatar = assistant_avatar or DEFAULT_ASSISTANT_AVATAR
    # Space above first message so it sits a little lower, not cramped at top
    st.markdown('<div style="min-height: 7vh;"></div>', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        avatar = user_avatar if message["role"] == "user" else assistant_avatar
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])


def apply_sidebar_styling():
    """Apply CSS styling for conversational bot sidebar: compact rows, rounded corners, active state."""
    st.markdown("""
    <style>
        /* Sidebar background - slightly darker than main */
        div[data-testid="stSidebar"] {
            background-color: #171717 !important;
        }
        /* Invisible scrollbar on sidebar – scrolling still works */
        div[data-testid="stSidebar"] > div,
        div[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
            scrollbar-width: none !important;
        }
        div[data-testid="stSidebar"] > div::-webkit-scrollbar,
        div[data-testid="stSidebar"] [data-testid="stSidebarContent"]::-webkit-scrollbar {
            width: 0 !important;
            display: none !important;
        }
        /* Compact spacing in sidebar */
        div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.25rem;
        }
        /* New Chat button: rounded, light grey border, transparent dark background */
        div[data-testid="stSidebar"] button[kind="secondary"],
        div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
            border-radius: 0.5rem !important;
            padding: 0.5rem 0.75rem !important;
            border: 1px solid rgba(128, 128, 128, 0.4) !important;
            background-color: transparent !important;
            color: #ececec !important;
        }
        div[data-testid="stSidebar"] button[kind="secondary"]:hover,
        div[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
            background-color: rgba(128, 128, 128, 0.15) !important;
        }
        /* Conversation list: single line, ellipsis; min-width 0 so flex child can shrink */
        div[data-testid="stSidebar"] button {
            border-radius: 0.5rem !important;
            padding: 0.5rem 0.75rem !important;
            min-height: 2.25rem !important;
            min-width: 0 !important;
            transition: background-color 0.15s ease;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            display: block !important;
        }
        div[data-testid="stSidebar"] [data-testid="column"] {
            min-width: 0 !important;
        }
        div[data-testid="stSidebar"] button:hover {
            background-color: rgba(128, 128, 128, 0.2) !important;
        }
        /* Active conversation - subtle highlight (lighter grey) */
        div[data-testid="stSidebar"] button[kind="primary"] {
            background-color: rgba(128, 128, 128, 0.25) !important;
            color: #ececec !important;
            border: 1px solid rgba(128, 128, 128, 0.3) !important;
        }
        /* Clean divider */
        div[data-testid="stSidebar"] hr {
            margin: 0.5rem 0 !important;
            border-color: rgba(128, 128, 128, 0.3) !important;
        }
    </style>
    """, unsafe_allow_html=True)


def apply_global_styling():
    """Apply global CSS for conversational bot theme: chat input, main area."""
    st.markdown("""
    <style>
        /* Main content - more vertical padding so content isn't pushed to top */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        /* Chat input container – remove padding */
        .st-emotion-cache-1fjgssw {
            padding: 0 !important;
        }
        /* Chat message content – push text down a bit for better alignment */
        div[data-testid="stChatMessage"] > div {
            padding-top: 0.5rem !important;
        }
        /* Chat input container – increase height of the input block */
        div[data-testid="stChatInput"] {
            min-height: 4rem !important;
        }
        /* Chat input – style only the textarea, leave containers alone to avoid arc artifacts */
        div[data-testid="stChatInput"] textarea {
            border-radius: 1.5rem !important;
            background-color: #2d2d2d !important;
            border: 1px solid rgba(128, 128, 128, 0.3) !important;
            padding: 1.25rem 1rem 1rem 2.5ch !important;
            min-height: 4rem !important;
            line-height: 1.5 !important;
            box-sizing: border-box !important;
        }
    </style>
    """, unsafe_allow_html=True)


def render_chat_header(header_title: str, byline_text: str):
    """Render a minimal header in the sidebar (Instructions section replaces full header)."""
    pass  # Header moved to main content via render_main_header


def render_main_header(
    header_title: str,
    show_deploy_button: bool = True,
    deploy_label: str = "Deploy",
):
    """Render the main content header with title, Deploy button, and options menu."""
    apply_global_styling()

    col_title, col_deploy, col_menu = st.columns([6, 1, 1])
    with col_title:
        st.markdown(
            f"<h1 style='margin:0; font-size:1.75rem; font-weight:700; letter-spacing:-0.02em; color:#ececec;'>{header_title}</h1>",
            unsafe_allow_html=True,
        )
    with col_deploy:
        if show_deploy_button:
            st.button(deploy_label, key="header_deploy", type="secondary")
    with col_menu:
        st.button("⋮", key="header_menu", type="secondary", help="Options")


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
