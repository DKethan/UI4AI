"""Unit tests for UI4AI.message_handler."""
import pytest

from UI4AI.message_handler import (
    truncate_messages,
    extract_code_blocks,
    format_markdown_message,
)


class TestTruncateMessages:
    def test_empty_returns_empty(self):
        assert truncate_messages([], 100, lambda m: 0) == []

    def test_under_limit_returns_unchanged(self):
        messages = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
        count = lambda m: len(str(m))  # simple token count
        assert truncate_messages(messages, 500, count) == messages

    def test_system_message_kept_first(self):
        system = {"role": "system", "content": "You are helpful."}
        user = {"role": "user", "content": "hi"}
        assistant = {"role": "assistant", "content": "hello"}
        messages = [system, user, assistant]
        # Allow only 2 "tokens" (messages) in addition to system
        def count_tokens(msgs):
            return len(msgs)
        result = truncate_messages(messages, 3, count_tokens)
        assert result[0]["role"] == "system"
        assert result[0]["content"] == "You are helpful."
        assert len(result) == 3

    def test_truncates_older_messages(self):
        messages = [
            {"role": "user", "content": "1"},
            {"role": "assistant", "content": "2"},
            {"role": "user", "content": "3"},
            {"role": "assistant", "content": "4"},
        ]
        # Keep total tokens (here: len) <= 3
        result = truncate_messages(messages, 3, len)
        assert len(result) <= 3
        # Newest messages kept
        assert result[-1]["content"] == "4"
        assert result[-2]["content"] == "3"


class TestExtractCodeBlocks:
    def test_empty_string(self):
        assert extract_code_blocks("") == []

    def test_single_block(self):
        text = "```python\nprint('hi')\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0]["language"] == "python"
        assert "print" in blocks[0]["code"]

    def test_multiple_blocks(self):
        text = "```py\nx=1\n```\n\n```\nplain\n```"
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0]["language"] == "py"
        assert blocks[1]["language"] == "text" or blocks[1]["language"] == ""


class TestFormatMarkdownMessage:
    def test_formats_role_and_content(self):
        msg = {"role": "user", "content": "Hello"}
        out = format_markdown_message(msg)
        assert "USER" in out
        assert "Hello" in out

    def test_unknown_role(self):
        msg = {"role": "custom", "content": "x"}
        out = format_markdown_message(msg)
        assert "CUSTOM" in out
        assert "x" in out
