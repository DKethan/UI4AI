A simple, lightweight, and plug-and-play Streamlit-based UI for LLM chatbot applications.

---

## 🚀 Features

- Plug in your own `generate_response` function  
- Built-in sidebar history and session management  
- Optional extras:
  - Title generation
  - Token counting
  - Max history control

![Chat Example](images/table001.png)

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

# Set your OpenAI API key
openai.api_key = "<YOUR_API_KEY>"

# Define how the chatbot generates responses
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

# Launch the chat app
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
Automatically generates a conversation title.  
![Title Generation](images/sample_title.png)

### 🔢 Token Counting  
Displays the total token count used in the conversation.  
![Token Counting](images/sample_title_with_tokens.png)

### 🕒 Customizable Max History  
Control how many messages are remembered in the chat history.  
![Max History](images/max_history.png)  
> For example, if you first ask “Who is Spider-Man?” When you later ask “Name all his movies?”, it assumes “his” means Spider-Man this is because of history.

### 📚 Sidebar History  
View and click through previous conversation threads in the sidebar.  
![Session History](images/sample_session.png)

### 💾 Persistent Sessions  
Your chat history persists even after refreshing the page. You can return and continue where you left off!  
![Session Persistence](images/sample_session.png)