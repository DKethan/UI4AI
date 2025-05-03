"""
Simple example of UI4AI usage.

This example shows the minimal setup required to use UI4AI.
No external API integration is needed for this demo.
"""
from UI4AI import run_chat

def generate_response(messages):
    """Simple echo bot for demonstration."""
    user_message = messages[-1]["content"]
    
    # Simple response generation
    if "hello" in user_message.lower():
        return "Hello there! How can I help you today?"
    elif "help" in user_message.lower():
        return "I'm a simple demo bot. I can respond to basic messages like 'hello' and 'help'."
    elif "?" in user_message:
        return "That's an interesting question. In a real implementation, I would connect to an LLM API to generate a thoughtful response."
    else:
        return f"I received your message: '{user_message}'. This is a simple demo without a real LLM backend."

# Run the chat app with minimal configuration
run_chat(
    generate_response=generate_response,
    page_title="Simple Demo",
    header_title="UI4AI Demo",
    byline_text="Simple Example"
)
