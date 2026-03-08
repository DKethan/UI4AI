from typing import List, Dict, Callable, Optional, Iterator, Any

import streamlit as st

from .conversation_store import save_conversations
from .session_manager import init_session_state, reset_conversation
from .ui_components import (
    apply_global_styling,
    render_sidebar,
    render_chat_history,
    render_chat_header,
    render_welcome_screen,
)
from .message_handler import handle_user_input, create_system_message


def run_chat(
        generate_response: Optional[Callable[[List[Dict]], str]] = None,
        generate_response_stream: Optional[Callable[[List[Dict]], Iterator[str]]] = None,
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
        enable_search: bool = False,
        user_avatar: Optional[str] = None,
        assistant_avatar: Optional[str] = None,
        welcome_title: str = "Welcome",
        welcome_message: str = "How can I help you today?",
        suggestions: Optional[List[str]] = None,
        setup_callback: Optional[Callable[[], None]] = None,
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
    # set_page_config MUST be first Streamlit command
    st.set_page_config(page_title=page_title, layout=layout)

    # Optional setup (e.g. API key prompt) — runs after page config
    if setup_callback:
        setup_callback()

    # Initialize session state
    init_session_state(storage_path)

    # Render sidebar header (minimal - Instructions/History in sidebar)
    render_chat_header(header_title, byline_text)

    # Add system message if provided (including for new conversations)
    if system_prompt:
        create_system_message(system_prompt)

    # Define a save function to use in components (with path from session state)
    def save_func():
        save_conversations(st.session_state.storage_path)

    # Render sidebar
    with st.sidebar:
        render_sidebar(
            enable_search=enable_search,
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
            save_conversations_func=save_func,
            header_title=header_title,
            byline_text=byline_text,
        )

    # Apply global styling (chat input, etc.) and render main chat interface
    apply_global_styling()
    messages = st.session_state.messages
    has_visible_messages = len(messages) > 1 or (len(messages) == 1 and messages[0]["role"] != "system")
    has_pending_suggestion = "pending_suggestion" in st.session_state and st.session_state.pending_suggestion
    # Read chat input here so we can hide welcome as soon as user sends (even during "Thinking...")
    chat_input_value = st.chat_input(chat_placeholder)
    has_input_this_run = (chat_input_value is not None) or has_pending_suggestion
    if not has_visible_messages and not has_input_this_run:
        render_welcome_screen(
            welcome_title=welcome_title,
            welcome_message=welcome_message,
            suggestions=suggestions,
        )
    else:
        render_chat_history(user_avatar=user_avatar, assistant_avatar=assistant_avatar)

    # Handle user input (processes pending_suggestion or chat_input_value)
    handle_user_input(
        generate_response=generate_response,
        generate_response_stream=generate_response_stream,
        generate_title=generate_title,
        count_tokens=count_tokens,
        chat_placeholder=chat_placeholder,
        spinner_text=spinner_text,
        max_history_tokens=max_history_tokens,
        save_conversations_func=save_func,
        user_avatar=user_avatar,
        assistant_avatar=assistant_avatar,
        chat_input_value=chat_input_value,
    )


def run_chat_openai(
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    stream: bool = False,
    **kwargs: Any,
) -> None:
    """
    One-call OpenAI chat. Uses OPENAI_API_KEY env or sidebar input if not passed.

    Example:
        from UI4AI import run_chat_openai
        run_chat_openai()  # that's it

    Override any run_chat parameter via kwargs:
        run_chat_openai(page_title="My Bot", system_prompt="You are helpful.")
    """
    import os
    from openai import OpenAI

    def setup():
        key = api_key or os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key")
        if not key:
            key = st.sidebar.text_input("OpenAI API key:", type="password", key="openai_api_key")
            if not key:
                st.warning("Enter your OpenAI API key to continue.")
                st.stop()

    def make_client():
        key = api_key or os.getenv("OPENAI_API_KEY") or st.session_state.get("openai_api_key")
        return OpenAI(api_key=key)

    if stream:

        def gen(messages: List[Dict]) -> Iterator[str]:
            client = make_client()
            stream_resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream_resp:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        run_chat(setup_callback=setup, generate_response_stream=gen, **kwargs)
    else:

        def gen(messages: List[Dict]) -> str:
            client = make_client()
            r = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return r.choices[0].message.content or ""

        run_chat(setup_callback=setup, generate_response=gen, **kwargs)