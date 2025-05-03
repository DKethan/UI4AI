import os
import streamlit as st
import openai
from UI4AI import run_chat

# Get API key from environment or prompt user
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        st.stop()

openai.api_key = api_key

def generate_response(messages):
    """Generate a response using the OpenAI API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"


# Run the chat app
run_chat(
    generate_response=generate_response,
    page_title="OpenAI Chat",
    header_title="OpenAI Assistant",
    byline_text="Powered by UI4AI",
    max_history_tokens=4000,
    show_token_count=True
)
