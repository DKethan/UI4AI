from UI4AI import run_chat
from Wrapper4AI.wrap import connect

# Securely connect to the OpenAI client
API_KEY = "your api key here"  # Replace with your actual API key

client = connect(
    provider="openai",
    model="gpt-4o",
    api_key=API_KEY
)

# Run the chat interface
run_chat(
    generate_response=client.chat_with_history,
    generate_title=client.generate_title,
    max_history_tokens=3000
)