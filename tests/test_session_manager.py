"""Unit tests for UI4AI.session_manager."""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from UI4AI.session_manager import init_session_state, get_current_conversation


class TestInitSessionState:
    @patch("UI4AI.session_manager.load_conversations")
    @patch("UI4AI.session_manager.st")
    def test_sets_defaults_when_empty(self, mock_st, mock_load):
        mock_load.return_value = {}
        mock_st.session_state = {}
        init_session_state(None)
        assert mock_st.session_state.get("conversations") == {}
        assert mock_st.session_state.get("current_convo_id") is None
        assert mock_st.session_state.get("messages") == []
        assert mock_st.session_state.get("storage_path") is None
        assert mock_st.session_state.get("pending_suggestion") is None

    @patch("UI4AI.session_manager.load_conversations")
    @patch("UI4AI.session_manager.st")
    def test_does_not_overwrite_existing(self, mock_st, mock_load):
        mock_load.return_value = {}
        mock_st.session_state = {"messages": [{"role": "user", "content": "hi"}]}
        init_session_state(None)
        assert mock_st.session_state["messages"] == [{"role": "user", "content": "hi"}]

    @patch("UI4AI.session_manager.load_conversations")
    @patch("UI4AI.session_manager.st")
    def test_storage_path_passed(self, mock_st, mock_load):
        mock_load.return_value = {}
        mock_st.session_state = {}
        init_session_state("/tmp/convos.json")
        assert mock_st.session_state["storage_path"] == "/tmp/convos.json"
        mock_load.assert_called_once_with("/tmp/convos.json")


class TestGetCurrentConversation:
    @patch("UI4AI.session_manager.st")
    def test_none_when_no_current(self, mock_st):
        mock_st.session_state = SimpleNamespace(current_convo_id=None, conversations={})
        assert get_current_conversation() is None

    @patch("UI4AI.session_manager.st")
    def test_returns_conversation_when_set(self, mock_st):
        convo = {"id": "c1", "title": "Test", "messages": []}
        mock_st.session_state = SimpleNamespace(current_convo_id="c1", conversations={"c1": convo})
        assert get_current_conversation() == convo

    @patch("UI4AI.session_manager.st")
    def test_returns_none_when_id_missing(self, mock_st):
        mock_st.session_state = SimpleNamespace(current_convo_id="missing", conversations={})
        assert get_current_conversation() is None
