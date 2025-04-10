import streamlit as st
import uuid
from datetime import datetime
from typing import List, Dict, Callable, Optional


def run_chat(
    generate_response: Optional[Callable[[List[Dict]], str]],
    generate_title: Optional[Callable[[str], str]] = None,
    count_tokens: Optional[Callable[[List[Dict]], int]] = None,
    page_title: str = "AI Chat",
    title: str = "Conversational bot",
    layout: str = "wide",
    new_conversation: str = "➕ New Chat",
    chat_placeholder: str = "Ask me anything...",
    sidebar_instructions: str = "Conversation History",
    spinner_text: str = "Thinking...",
    max_history_tokens: Optional[int] = None
):
    """Streamlit UI for LLM chat with flexible core"""

    if not generate_response:
        print("No generate_response function provided.")
        st.set_page_config(page_title="Error", layout="wide")
        st.error("No `generate_response` function provided.")
        return

    _init_session_state()

    st.set_page_config(page_title=page_title, layout=layout)
    st.title(title)

    with st.sidebar:
        _render_sidebar(generate_title, count_tokens, sidebar_instructions, new_conversation)

    _render_chat_history()

    _handle_user_input(
        generate_response,
        generate_title,
        count_tokens,
        chat_placeholder,
        spinner_text,
        max_history_tokens
    )


def _init_session_state():
    defaults = {"conversations": {}, "current_convo_id": None, "messages": []}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _render_sidebar(
    generate_title: Optional[Callable],
    count_tokens: Optional[Callable],
    instructions: str,
    new_conversation: str
):
    st.markdown("### 📖 Instructions")
    st.markdown(instructions)

    if st.button(new_conversation):
        print("🔄 New conversation started")
        _reset_conversation()

    if generate_title:
        for convo_id, convo in st.session_state.conversations.items():
            label = convo["title"]
            if count_tokens:
                label += f" ({convo.get('token_count', '?')} tokens)"
            if st.button(label, key=convo_id):
                st.session_state.current_convo_id = convo_id
                st.session_state.messages = convo["messages"]
                st.rerun()


def _render_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _handle_user_input(
    generate_response: Callable,
    generate_title: Optional[Callable],
    count_tokens: Optional[Callable],
    placeholder: str,
    spinner_text: str,
    max_tokens: Optional[int]
):
    if prompt := st.chat_input(placeholder):
        print(f"User: {prompt}")
        _create_conversation_if_needed(prompt, generate_title)

        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            with st.spinner(spinner_text):
                if count_tokens and max_tokens:
                    messages_for_api = _truncate_messages(
                        st.session_state.messages,
                        count_tokens,
                        max_tokens
                    )
                elif generate_title or count_tokens:
                    messages_for_api = st.session_state.messages
                else:
                    messages_for_api = [st.session_state.messages[-1]]

                response = generate_response(messages_for_api)

                st.chat_message("assistant").markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

                if st.session_state.current_convo_id:
                    convo = st.session_state.conversations[st.session_state.current_convo_id]
                    convo["messages"] = st.session_state.messages
                    if count_tokens:
                        convo["token_count"] = count_tokens(st.session_state.messages)

        except Exception as e:
            print(f"Exception: {e}")
            st.error(f"Error: {str(e)}")


def _create_conversation_if_needed(prompt: str, generate_title: Optional[Callable]):
    if not st.session_state.current_convo_id:
        convo_id = str(uuid.uuid4())
        title = generate_title(prompt) if generate_title else "Untitled Chat"
        st.session_state.conversations[convo_id] = {
            "id": convo_id,
            "title": title,
            "messages": [],
            "token_count": 0,
            "created_at": datetime.now().isoformat()
        }
        st.session_state.current_convo_id = convo_id


def _reset_conversation():
    st.session_state.current_convo_id = None
    st.session_state.messages = []


def _truncate_messages(messages: List[Dict], count_tokens: Callable, max_tokens: int) -> List[Dict]:
    trimmed = []
    total_tokens = 0

    for msg in reversed(messages):
        tokens = count_tokens([msg])
        if total_tokens + tokens > max_tokens:
            break
        trimmed.insert(0, msg)
        total_tokens += tokens

    return trimmed
