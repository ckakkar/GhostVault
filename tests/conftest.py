"""
Pytest configuration and fixtures
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock chainlit BEFORE any imports happen
# This prevents chainlit from trying to load its config during tests
# We need to do this very early, before app.py imports chainlit
mock_chainlit = MagicMock()
mock_chainlit.set_chat_profiles = MagicMock()
mock_chainlit.on_chat_start = MagicMock()
mock_chainlit.on_message = MagicMock()
mock_chainlit.Message = MagicMock()
mock_chainlit.user_session = MagicMock()
mock_chainlit.ChatProfile = MagicMock()
sys.modules["chainlit"] = mock_chainlit


def pytest_configure(config):
    """Called after command line options have been parsed and all plugins initialized"""
    # Ensure chainlit is mocked before any test imports happen
    if "chainlit" not in sys.modules or not isinstance(sys.modules["chainlit"], MagicMock):
        mock_chainlit = MagicMock()
        mock_chainlit.set_chat_profiles = MagicMock()
        mock_chainlit.on_chat_start = MagicMock()
        mock_chainlit.on_message = MagicMock()
        mock_chainlit.Message = MagicMock()
        mock_chainlit.user_session = MagicMock()
        mock_chainlit.ChatProfile = MagicMock()
        sys.modules["chainlit"] = mock_chainlit


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB for testing"""
    with patch("chromadb.PersistentClient") as mock_client:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.return_value.get_collection.return_value = mock_collection
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        yield mock_collection


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    with patch("llama_index.vector_stores.chroma.ChromaVectorStore") as mock:
        yield mock


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing"""
    return {"file_path": "/path/to/test.pdf", "file_name": "test.pdf", "page_label": "1", "page_number": 1}
