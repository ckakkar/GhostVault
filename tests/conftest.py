"""
Pytest configuration and fixtures
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_chromadb():
    """Mock ChromaDB for testing"""
    with patch('chromadb.PersistentClient') as mock_client:
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.return_value.get_collection.return_value = mock_collection
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        yield mock_collection


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    with patch('llama_index.vector_stores.chroma.ChromaVectorStore') as mock:
        yield mock


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing"""
    return {
        'file_path': '/path/to/test.pdf',
        'file_name': 'test.pdf',
        'page_label': '1',
        'page_number': 1
    }

