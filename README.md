# UI4AI

A simple, lightweight, and plug-and-play Streamlit-based UI for LLM chatbot applications.

---

## 🚀 Features

- Plug in your own `generate_response` function
- Built-in sidebar history and session management
- Optional extras:
  - Title generation
  - Token counting
  - Max history control
  - Customizable and editable conversation history titles
  - Persistent session state: continue your chat even after restarting the app

---

## 📦 Installation

```bash
  pip install UI4AI
```

---

## 🧠 Basic Usage

```python
from UI4AI import run_chat
import openai

openai.api_key = "<YOUR_API_KEY>"

def generate_response(messages) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Response generation failed: {str(e)}")

run_chat(
    generate_response=generate_response,
    title="My Chatbot",
    sidebar=True,
    session_state=True,
    token_counting=True
)
```

---

## ▶️ Running the App

```bash
  streamlit run app.py  # Or replace with your own script name
```

---

## 🎨 Customization Options

You can customize the UI with these optional parameters:

```python
run_chat(
    generate_response: Callable[[List[Dict]], str],
    page_title: str = "AI Chat", 
    title: str = "Conversational Bot",
    layout: str = "wide",
    new_conversation: str = "➕ New Chat",
    chat_placeholder: str = "Ask me anything...",
    sidebar_instructions: str = "Conversation History",
    spinner_text: str = "Thinking...",
)
```

---

## 🔧 Additional Features

### 🧠 Title Generation  
>Automatically generates a conversation title.

### 🔢 Token Counting  
>Displays the total token count used in the conversation.  

### 🕒 Customizable Max History  
Control how many messages are remembered in the chat history.  
> For example, if you first ask “Who is Spider-Man?” When you later ask “Name all his movies?”, it assumes “his” means Spider-Man this is because of history.

### 📝 Customizable Conversation Titles
>You can edit or customize the title of any conversation in the history sidebar for better organization.

### 💾 Persistent Sessions
>Session state is stored automatically, so your chat history and context are preserved. You can continue your conversation even if you restart or refresh the app!

### 📚 Sidebar History  
>View and click through previous conversation threads in the sidebar.  

### 💾 Persistent Sessions  
>Your chat history persists even after refreshing the page or even restarting app. You can return and continue where you left off!