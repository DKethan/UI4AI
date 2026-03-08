"""
Minimal UI4AI — frontend only, no API key. Run: streamlit run examples/minimal_example.py

Replace generate_response with your LLM call when ready.
"""
from UI4AI import run_chat


def generate_response(messages):
    return f"You said: {messages[-1]['content']}"


run_chat(generate_response=generate_response)
