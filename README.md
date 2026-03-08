# UI4AI

[![PyPI version](https://badge.fury.io/py/UI4AI.svg)](https://pypi.org/project/UI4AI/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, lightweight, and plug-and-play Streamlit-based UI for LLM chatbot applications with ChatGPT-style features.

---

## Features

- Plug in your own `generate_response` or **streaming** `generate_response_stream` function
- Built-in sidebar history and session management
- **Welcome screen** with optional suggestion chips when starting a new chat
- **Custom avatars** for user and assistant messages
- Optional: title generation, token counting, max history control
- Editable conversation titles and persistent sessions (survives refresh/restart)
- Optional conversation search

---

## Installation

```bash
pip install UI4AI
```

---

## Minimal usage (frontend only, no API key)

```python
from UI4AI import run_chat

def generate_response(messages):
    return f"You said: {messages[-1]['content']}"

run_chat(generate_response=generate_response)
```

Run: `streamlit run app.py`

For OpenAI: use `run_chat_openai()` (requires API key).

---

## Basic usage (customize with parameters)

Use `run_chat()` with your own `generate_response`:

```python
from UI4AI import run_chat
from openai import OpenAI

client = OpenAI(api_key="<YOUR_API_KEY>")

def generate_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""

run_chat(
    generate_response=generate_response,
    page_title="My Chatbot",
    header_title="My Chatbot",
)
```

Or use `run_chat_openai()` and override any parameter:

```python
run_chat_openai(
    page_title="My Bot",
    system_prompt="You are a helpful assistant.",
    model="gpt-4o",
)
```

Run the app: `streamlit run app.py`

---

## Examples

| File | Description |
|------|-------------|
| `examples/minimal_example.py` | Frontend only, no API key |
| `examples/simple_example.py` | Echo bot with more responses |
| `examples/openai_example.py` | OpenAI (requires API key) |
| `examples/base_example.py` | Full template with all parameters documented |

---

## Streaming (typewriter effect)

Pass a **generator** that yields string chunks to get a ChatGPT-like streaming response:

```python
from UI4AI import run_chat
from openai import OpenAI

client = OpenAI(api_key="<YOUR_API_KEY>")

def generate_response_stream(messages):
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

run_chat(
    generate_response_stream=generate_response_stream,
    page_title="Streaming Chat",
)
```

---

## Welcome screen and avatars

```python
run_chat(
    generate_response=my_response_fn,
    welcome_title="Welcome",
    welcome_message="How can I help you today?",
    suggestions=[
        "Explain quantum computing in simple terms",
        "Write a short poem",
        "Help me debug this code",
    ],
    user_avatar="🧑",
    assistant_avatar="🤖",
)
```

---

## run_chat_openai parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` or `None` | `None` | OpenAI API key (or use `OPENAI_API_KEY` env / sidebar) |
| `model` | `str` | `"gpt-4o-mini"` | Model name |
| `temperature` | `float` | `0.7` | Sampling temperature |
| `stream` | `bool` | `False` | Use streaming responses |
| `**kwargs` | — | — | Any `run_chat` parameter (e.g. `page_title`, `system_prompt`) |

---

## run_chat parameter reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `generate_response` | `Callable[[List[Dict]], str]` or `None` | `None` | Function that takes messages and returns the full response text. |
| `generate_response_stream` | `Callable[[List[Dict]], Iterator[str]]` or `None` | `None` | Generator that yields response chunks (used for streaming; takes priority over `generate_response`). |
| `generate_title` | `Callable[[str], str]` or `None` | `None` | Generates a conversation title from the first user message. |
| `count_tokens` | `Callable[[List[Dict]], int]` or `None` | `None` | Returns token count for the conversation (enables token display and `max_history_tokens`). |
| `page_title` | `str` | `"AI Chat"` | Browser tab title. |
| `header_title` | `str` | `"UI4AI"` | Sidebar header title. |
| `byline_text` | `str` | `"Powered by Kethan Dosapati"` | Byline under the header. |
| `layout` | `str` | `"wide"` | Streamlit layout: `"wide"` or `"centered"`. |
| `new_conversation_label` | `str` | `"➕ New Chat"` | Label for the new conversation button. |
| `chat_placeholder` | `str` | `"Ask me anything..."` | Placeholder for the chat input. |
| `spinner_text` | `str` | `"Thinking..."` | Text shown while generating (non-streaming). |
| `max_history_tokens` | `int` or `None` | `None` | Max tokens to keep in context (requires `count_tokens`). |
| `show_edit_options` | `bool` | `True` | Show edit/delete in conversation menu. |
| `primary_color` | `str` | `"#4f8bf9"` | Primary UI color. |
| `hover_color` | `str` | `"#f0f2f6"` | Hover color. |
| `date_grouping` | `bool` | `True` | Group conversations by date in sidebar. |
| `show_token_count` | `bool` | `True` | Show token count per conversation. |
| `max_title_length` | `int` | `25` | Max length of conversation title in sidebar. |
| `storage_path` | `str` or `None` | `None` | Custom path for conversation JSON file. |
| `system_prompt` | `str` or `None` | `None` | System message added to each conversation. |
| `enable_search` | `bool` | `False` | Enable conversation search in sidebar. |
| `user_avatar` | `str` or `None` | `None` | Avatar for user (emoji, `:material/icon_name:`, or image URL). |
| `assistant_avatar` | `str` or `None` | `None` | Avatar for assistant. |
| `welcome_title` | `str` | `"Welcome"` | Title shown when there are no messages. |
| `welcome_message` | `str` | `"How can I help you today?"` | Message shown on welcome screen. |
| `suggestions` | `List[str]` or `None` | `None` | Optional suggestion chips on welcome screen. |
| `setup_callback` | `Callable` or `None` | `None` | Called after `set_page_config` (e.g. for API key prompt). Use when you need `st.*` before the main UI. |

---

## Additional features

- **Title generation** — Automatically generates a conversation title from the first message when `generate_title` is provided.
- **Token counting** — Displays total token count per conversation when `count_tokens` is provided.
- **Max history** — Use `max_history_tokens` with `count_tokens` to limit context length (older messages are truncated).
- **Editable titles** — Rename conversations from the sidebar menu.
- **Persistent sessions** — Conversations are saved to a JSON file and persist across refreshes and restarts.
- **Sidebar history** — Switch between past conversations in the sidebar.

---

## License

MIT
