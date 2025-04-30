import streamlit as st
import uuid
import json
from datetime import datetime
from typing import List, Dict, Callable, Optional


# Persistence functions
def _load_conversations() -> Dict:
    try:
        with open("conversations.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
        return {}


def _save_conversations():
    try:
        with open("conversations.json", "w") as f:
            json.dump(st.session_state.conversations, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error saving conversations: {e}")


# Date formatting
def _get_date_category(created_at: str) -> str:
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


def _init_session_state():
    defaults = {
        "conversations": _load_conversations(),
        "current_convo_id": None,
        "messages": [],
        "editing_convo": None,
        "menu_open": None,
        "menu_states": {},
        "edit_states": {}
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _render_sidebar(
        generate_title: Optional[Callable],
        count_tokens: Optional[Callable],
        new_conversation_label: str,
        show_edit_options: bool,
        primary_color: str,
        hover_color: str,
        date_grouping: bool,
        show_token_count: bool,
        max_title_length: int
):
    # New chat button
    if st.button(new_conversation_label, use_container_width=True):
        _reset_conversation()

    st.markdown("---")

    # Custom CSS for button styling
    st.markdown("""
    <style>
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div {
            gap: 0.2rem;
        }
        button.small-button {
            padding: 0 0.3rem !important;
            min-height: 1.5rem !important;
            margin: 0 0.1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

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
                        _save_conversations()
                        st.rerun()
                    # Cancel button
                    if st.button("Cancel", key=f"cancel_{convo_id}", use_container_width=True):
                        st.session_state.edit_states[convo_id] = False
                        st.rerun()
            continue

        # Title formatting
        title = (convo["title"][:max_title_length] + "...") if len(convo["title"]) > max_title_length else convo[
            "title"]
        if show_token_count and count_tokens:
            title += f" ({convo.get('token_count', '?')}"

        # Date grouping
        if date_grouping:
            group = _get_date_category(convo["created_at"])
            if group != current_group:
                st.markdown(f"**{group}**")
                current_group = group

        # Conversation row
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
                    st.session_state.messages = convo["messages"]
                    st.rerun()

            # Menu column
            with cols[1]:
                if st.session_state.menu_states.get(convo_id, False):
                    if st.button("✏️", key=f"edit_{convo_id}", help="Rename",
                                 type="secondary", use_container_width=True,
                                 kwargs={"class": "small-button"}):
                        st.session_state.edit_states[convo_id] = True
                        st.session_state.menu_states[convo_id] = False
                        st.rerun()
                    if st.button("🗑️", key=f"delete_{convo_id}", help="Delete",
                                 type="secondary", use_container_width=True,
                                 kwargs={"class": "small-button"}):
                        del st.session_state.conversations[convo_id]
                        if st.session_state.current_convo_id == convo_id:
                            _reset_conversation()
                        _save_conversations()
                        st.rerun()
                    if st.button("✕", key=f"close_{convo_id}", help="Close menu",
                                 type="secondary", use_container_width=True,
                                 kwargs={"class": "small-button"}):
                        st.session_state.menu_states[convo_id] = False
                        st.rerun()
                else:
                    if st.button("⋯", key=f"dots_{convo_id}",
                                 type="secondary", use_container_width=True,
                                 kwargs={"class": "small-button"}):
                        st.session_state.menu_states[convo_id] = True
                        st.rerun()


def _render_chat_history():
    """Display the chat message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def _handle_user_input(
        generate_response: Optional[Callable],
        generate_title: Optional[Callable],
        count_tokens: Optional[Callable],
        chat_placeholder: str,
        spinner_text: str,
        max_history_tokens: Optional[int]
):
    """Process user input, generate responses, and update conversation"""
    if prompt := st.chat_input(chat_placeholder):
        # Add user message to chat
        st.chat_message("user").markdown(prompt)

        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create a conversation if needed
        _create_conversation_if_needed(generate_title, prompt)

        # Generate AI response
        if generate_response:
            with st.chat_message("assistant"):
                with st.spinner(spinner_text):
                    # Truncate messages if needed
                    if max_history_tokens and count_tokens:
                        st.session_state.messages = _truncate_messages(
                            st.session_state.messages,
                            max_history_tokens,
                            count_tokens
                        )

                    # Generate response
                    response = generate_response(st.session_state.messages)
                    st.markdown(response)

            # Add response to state and save
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Update conversation in storage
            convo_id = st.session_state.current_convo_id
            st.session_state.conversations[convo_id]["messages"] = st.session_state.messages

            # Update token count if provided
            if count_tokens:
                token_count = count_tokens(st.session_state.messages)
                st.session_state.conversations[convo_id]["token_count"] = token_count

            _save_conversations()


def _create_conversation_if_needed(generate_title: Optional[Callable], first_prompt: str):
    """Create a new conversation if one doesn't exist"""
    if st.session_state.current_convo_id is None:
        convo_id = str(uuid.uuid4())
        st.session_state.current_convo_id = convo_id

        # Set default title, which may be updated later
        title = "New Conversation"
        if generate_title:
            title = generate_title(first_prompt)

        st.session_state.conversations[convo_id] = {
            "id": convo_id,
            "title": title,
            "messages": st.session_state.messages,
            "created_at": datetime.now().isoformat(),
            "token_count": 0
        }
        _save_conversations()


def _reset_conversation():
    """Reset to a new empty conversation"""
    st.session_state.current_convo_id = None
    st.session_state.messages = []
    st.session_state.menu_open = None
    st.rerun()


def _truncate_messages(messages: List[Dict], max_tokens: int, count_tokens: Callable) -> List[Dict]:
    """Truncate message history to fit within token limit"""
    if not messages:
        return messages

    # Always keep the system message if present
    system_message = None
    other_messages = messages.copy()

    if messages[0]["role"] == "system":
        system_message = messages[0]
        other_messages = messages[1:]

    # Check if we need to truncate
    if count_tokens(messages) <= max_tokens:
        return messages

    # Truncate older messages first
    truncated_messages = []
    if system_message:
        truncated_messages.append(system_message)

    # Add messages from newest to oldest until we hit the token limit
    for message in reversed(other_messages):
        test_messages = truncated_messages + [message]
        if count_tokens(test_messages) <= max_tokens:
            truncated_messages = [message] + truncated_messages
        else:
            break

    return truncated_messages


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
        max_title_length: int = 25
):
    """Enhanced Streamlit chat UI with three-dot menu styling"""

    _init_session_state()
    st.set_page_config(page_title=page_title, layout=layout)

    # Main chat interface
    st.sidebar.markdown(f"<h1 style='margin-bottom:0'>{header_title}</h1>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<small>{byline_text}</small>", unsafe_allow_html=True)

    with st.sidebar:
        _render_sidebar(
            generate_title=generate_title,
            count_tokens=count_tokens,
            new_conversation_label=new_conversation_label,
            show_edit_options=show_edit_options,
            primary_color=primary_color,
            hover_color=hover_color,
            date_grouping=date_grouping,
            show_token_count=show_token_count,
            max_title_length=max_title_length
        )

    _render_chat_history()
    _handle_user_input(
        generate_response=generate_response,
        generate_title=generate_title,
        count_tokens=count_tokens,
        chat_placeholder=chat_placeholder,
        spinner_text=spinner_text,
        max_history_tokens=max_history_tokens
    )