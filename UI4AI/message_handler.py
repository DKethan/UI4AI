import uuid
from datetime import datetime
from typing import Callable, Dict, List, Optional

import streamlit as st


def handle_user_input(
        generate_response: Optional[Callable],
        generate_title: Optional[Callable],
        count_tokens: Optional[Callable],
        chat_placeholder: str,
        spinner_text: str,
        max_history_tokens: Optional[int],
        save_conversations_func: Callable
):
    """
    Process user input, generate responses, and update conversation.
    
    Args:
        generate_response: Function to generate responses to user messages
        generate_title: Function to generate conversation titles
        count_tokens: Function to count tokens in conversations
        chat_placeholder: Placeholder text for the chat input
        spinner_text: Text to display while generating a response
        max_history_tokens: Maximum number of tokens to keep in history
        save_conversations_func: Function to save conversations
    """
    if prompt := st.chat_input(chat_placeholder):
        # Add user message to chat
        st.chat_message("user").markdown(prompt)

        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Create a conversation if needed
        create_conversation_if_needed(generate_title, prompt, save_conversations_func)

        # Flag to track if title was updated
        title_updated = False

        # Update title if this is the first message and title is still default
        convo_id = st.session_state.current_convo_id
        if (len(st.session_state.messages) == 1 and
                st.session_state.conversations[convo_id]["title"] == "New Conversation" and
                generate_title):
            st.session_state.conversations[convo_id]["title"] = generate_title(prompt)
            title_updated = True

        # Generate AI response
        if generate_response:
            with st.chat_message("assistant"):
                with st.spinner(spinner_text):
                    # Truncate messages if needed
                    if max_history_tokens and count_tokens:
                        st.session_state.messages = truncate_messages(
                            st.session_state.messages,
                            max_history_tokens,
                            count_tokens
                        )

                    # Generate response
                    response = generate_response(st.session_state.messages)
                    st.markdown(response)

            # Add response to state and save
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Update conversation in storage
            st.session_state.conversations[convo_id]["messages"] = st.session_state.messages

            # Update token count if provided
            if count_tokens:
                token_count = count_tokens(st.session_state.messages)
                st.session_state.conversations[convo_id]["token_count"] = token_count

            save_conversations_func()

            # Rerun to refresh UI if title was updated
            if title_updated:
                st.rerun()


def create_conversation_if_needed(
        generate_title: Optional[Callable], 
        first_prompt: str,
        save_conversations_func: Callable
):
    """
    Create a new conversation if one doesn't exist.
    
    Args:
        generate_title: Function to generate conversation titles
        first_prompt: The first user message
        save_conversations_func: Function to save conversations
    """
    if st.session_state.current_convo_id is None:
        convo_id = str(uuid.uuid4())
        st.session_state.current_convo_id = convo_id

        # Set default title, which may be updated later
        title = "New Conversation"
        if generate_title:
            title = generate_title(first_prompt)

        st.session_state.conversations[convo_id] = {
            "id": convo_id,
            "title": title,
            "messages": st.session_state.messages,
            "created_at": datetime.now().isoformat(),
            "token_count": 0
        }
        save_conversations_func()


def truncate_messages(messages: List[Dict], max_tokens: int, count_tokens: Callable) -> List[Dict]:
    """
    Truncate message history to fit within token limit.
    
    Args:
        messages: List of message dictionaries
        max_tokens: Maximum number of tokens to keep
        count_tokens: Function to count tokens
        
    Returns:
        Truncated list of messages
    """
    if not messages:
        return messages

    # Always keep the system message if present
    system_message = None
    other_messages = messages.copy()

    if messages[0]["role"] == "system":
        system_message = messages[0]
        other_messages = messages[1:]

    # Check if we need to truncate
    if count_tokens(messages) <= max_tokens:
        return messages

    # Truncate older messages first
    truncated_messages = []
    if system_message:
        truncated_messages.append(system_message)

    # Add messages from newest to oldest until we hit the token limit
    for message in reversed(other_messages):
        test_messages = truncated_messages + [message]
        if count_tokens(test_messages) <= max_tokens:
            truncated_messages = [message] + truncated_messages
        else:
            break

    return truncated_messages


def create_system_message(system_prompt: str):
    """
    Create a system message and add it to the current conversation.
    
    Args:
        system_prompt: Content for the system message
    """
    if not system_prompt:
        return
    
    # Check if there's already a system message
    if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
        # Update existing system message
        st.session_state.messages[0]["content"] = system_prompt
    else:
        # Add system message at the beginning
        st.session_state.messages.insert(0, {
            "role": "system",
            "content": system_prompt
        })
    
    # Update the conversation in storage if a conversation exists
    if st.session_state.current_convo_id:
        convo_id = st.session_state.current_convo_id
        st.session_state.conversations[convo_id]["messages"] = st.session_state.messages


def format_markdown_message(message_obj: Dict) -> str:
    """
    Format a message object as markdown.
    
    Args:
        message_obj: Message dictionary with role and content
        
    Returns:
        Formatted markdown string
    """
    role = message_obj.get("role", "unknown").upper()
    content = message_obj.get("content", "")
    
    return f"**{role}**:\n\n{content}\n\n"


def extract_code_blocks(message: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from a message.
    
    Args:
        message: Message content potentially containing code blocks
        
    Returns:
        List of dictionaries with code and language
    """
    import re
    
    # Match code blocks with language specification
    # Format: ```language\ncode\n```
    pattern = r"```([a-zA-Z0-9_]*)\n([\s\S]*?)\n```"
    
    matches = re.findall(pattern, message)
    
    code_blocks = []
    for lang, code in matches:
        code_blocks.append({
            "language": lang.strip() if lang.strip() else "text",
            "code": code.strip()
        })
    
    return code_blocks
