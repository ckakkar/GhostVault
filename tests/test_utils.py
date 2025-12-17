"""
Tests for utility functions
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from utils import deduplicate_sources, extract_source_info, format_file_size


class TestFormatFileSize:
    """Test file size formatting"""

    def test_bytes(self):
        """Test byte formatting"""
        assert format_file_size(512) == "512.00 B"

    def test_kilobytes(self):
        """Test kilobyte formatting"""
        assert format_file_size(2048) == "2.00 KB"

    def test_megabytes(self):
        """Test megabyte formatting"""
        assert format_file_size(2097152) == "2.00 MB"

    def test_gigabytes(self):
        """Test gigabyte formatting"""
        assert format_file_size(2147483648) == "2.00 GB"


class TestExtractSourceInfo:
    """Test source information extraction"""

    def test_extract_valid_source(self):
        """Test extracting source info from valid node"""
        mock_node = MagicMock()
        mock_node.node.metadata = {"file_path": "/path/to/document.pdf", "page_label": "5"}

        result = extract_source_info(mock_node)
        assert result is not None
        assert result["file_name"] == "document.pdf"
        assert result["page"] == "5"

    def test_extract_with_page_number(self):
        """Test extracting with page_number instead of page_label"""
        mock_node = MagicMock()
        mock_node.node.metadata = {"file_name": "doc.pdf", "page_number": 10}

        result = extract_source_info(mock_node)
        assert result is not None
        assert result["file_name"] == "doc.pdf"
        assert result["page"] == "10"

    def test_extract_invalid_node(self):
        """Test extracting from invalid node"""
        mock_node = MagicMock()
        del mock_node.node

        result = extract_source_info(mock_node)
        assert result is None

    def test_extract_unknown_file(self):
        """Test extracting with unknown file path"""
        mock_node = MagicMock()
        mock_node.node.metadata = {"file_path": "Unknown", "page_label": "N/A"}

        result = extract_source_info(mock_node)
        assert result is not None
        assert result["file_name"] == "Unknown"


class TestDeduplicateSources:
    """Test source deduplication"""

    def test_deduplicate_empty_list(self):
        """Test deduplicating empty list"""
        result = deduplicate_sources([])
        assert result == []

    def test_deduplicate_no_duplicates(self):
        """Test deduplicating list with no duplicates"""
        sources = [{"file_name": "doc1.pdf", "page": "1"}, {"file_name": "doc2.pdf", "page": "2"}]
        result = deduplicate_sources(sources)
        assert len(result) == 2

    def test_deduplicate_with_duplicates(self):
        """Test deduplicating list with duplicates"""
        sources = [
            {"file_name": "doc1.pdf", "page": "1"},
            {"file_name": "doc1.pdf", "page": "1"},
            {"file_name": "doc2.pdf", "page": "2"},
        ]
        result = deduplicate_sources(sources)
        assert len(result) == 2

    def test_deduplicate_filters_none(self):
        """Test that None values are filtered out"""
        sources = [{"file_name": "doc1.pdf", "page": "1"}, None, {"file_name": "doc2.pdf", "page": "2"}]
        result = deduplicate_sources(sources)
        assert len(result) == 2
        assert None not in result
