"""
Base template for UI4AI — uses ALL features, no API key.

Run: streamlit run examples/base_example.py

INSTRUCTIONS
------------
1. Customize by changing parameters in run_chat(...) below.
2. Replace generate_response with your LLM call (OpenAI, Anthropic, local, etc.).
3. All run_chat parameters are shown — enable/disable as needed.

FEATURES DEMONSTRATED
--------------------
- generate_response      Your LLM call. Use generate_response_stream for streaming.
- generate_title        Auto-title conversations from first message
- count_tokens          Token count per conversation + enables max_history
- max_history_tokens    Truncate old messages to fit context window
- system_prompt         System message for every conversation
- enable_search         Search conversations in sidebar
- suggestions           Clickable chips on welcome screen
- user_avatar / assistant_avatar  Emoji, :material/icon:, or image URL
- storage_path          Custom JSON path for conversations
- setup_callback        For API key prompt (when using external APIs)
- Styling: primary_color, hover_color, layout, chat_placeholder, etc.
"""
from UI4AI import run_chat


def generate_response(messages):
    """Replace with your LLM call (OpenAI, Anthropic, etc.)."""
    return f"You said: {messages[-1]['content']}"


def generate_title(first_message: str) -> str:
    """Short title for sidebar. Truncate; or call your LLM for a smarter title."""
    return (first_message[:22] + "...") if len(first_message) > 25 else first_message


def count_tokens(messages):
    """Approximate token count (~4 chars/token). For exact: pip install tiktoken."""
    return sum(len(m.get("content", "")) // 4 for m in messages)


run_chat(
    generate_response=generate_response,
    generate_title=generate_title,
    count_tokens=count_tokens,
    page_title="AI Chat",
    header_title="AI Chat",
    byline_text="Powered by UI4AI",
    layout="wide",
    new_conversation_label="➕ New Chat",
    chat_placeholder="Ask me anything...",
    spinner_text="Thinking...",
    max_history_tokens=4000,
    show_edit_options=True,
    primary_color="#4f8bf9",
    hover_color="#f0f2f6",
    date_grouping=True,
    show_token_count=True,
    max_title_length=25,
    storage_path=None,
    system_prompt="You are a helpful assistant. Be concise.",
    enable_search=True,
    user_avatar="🧑",
    assistant_avatar="🤖",
    welcome_title="Welcome",
    welcome_message="How can I help you today?",
    suggestions=[
        "Explain quantum computing in simple terms",
        "Write a short haiku",
        "Help me debug this Python code",
    ],
)
