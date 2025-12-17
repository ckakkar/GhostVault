"""
Tests for ingestion system
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ingest import SUPPORTED_EXTENSIONS


class TestIngestionConfiguration:
    """Test ingestion configuration and constants"""

    def test_supported_extensions(self):
        """Test that supported extensions are correctly defined"""
        assert isinstance(SUPPORTED_EXTENSIONS, set)
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".markdown" in SUPPORTED_EXTENSIONS

    def test_extension_case_insensitive(self):
        """Test that extensions are stored in lowercase"""
        for ext in SUPPORTED_EXTENSIONS:
            assert ext.lower() == ext


class TestFileFiltering:
    """Test file filtering logic"""

    def test_valid_extensions(self):
        """Test that valid extensions are recognized"""
        valid_files = [Path("test.pdf"), Path("document.txt"), Path("readme.md"), Path("file.markdown")]

        for file_path in valid_files:
            assert file_path.suffix.lower() in SUPPORTED_EXTENSIONS

    def test_invalid_extensions(self):
        """Test that invalid extensions are rejected"""
        invalid_files = [Path("test.docx"), Path("document.xlsx"), Path("image.png"), Path("archive.zip")]

        for file_path in invalid_files:
            assert file_path.suffix.lower() not in SUPPORTED_EXTENSIONS
