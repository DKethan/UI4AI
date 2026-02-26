import os

from UI4AI import run_chat
from Wrapper4AI.wrap import connect

# Use environment variable for API key (e.g. export OPENAI_API_KEY=sk-...)
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("Set OPENAI_API_KEY environment variable to run this integration test")

client = connect(
    provider="openai",
    model="gpt-4o",
    api_key=API_KEY,
)

run_chat(
    generate_response=client.chat_with_history,
    generate_title=client.generate_title,
    max_history_tokens=3000,
)
