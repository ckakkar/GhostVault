"""
Tests for configuration management
"""

import pytest
from pathlib import Path
from config import (
    BASE_DIR, DATA_DIR, DB_DIR, LOGS_DIR,
    OLLAMA_MODEL, OLLAMA_EMBEDDING_MODEL,
    SUPPORTED_EXTENSIONS, SIMILARITY_TOP_K,
    SIMILARITY_CUTOFF
)


class TestConfig:
    """Test configuration values"""
    
    def test_base_directories_exist(self):
        """Test that base directories are Path objects"""
        assert isinstance(BASE_DIR, Path)
        assert isinstance(DATA_DIR, Path)
        assert isinstance(DB_DIR, Path)
        assert isinstance(LOGS_DIR, Path)
    
    def test_data_dir_path(self):
        """Test DATA_DIR is correctly set"""
        assert DATA_DIR == BASE_DIR / "data"
    
    def test_db_dir_path(self):
        """Test DB_DIR is correctly set"""
        assert DB_DIR == BASE_DIR / "db"
    
    def test_ollama_model_set(self):
        """Test Ollama model configuration"""
        assert isinstance(OLLAMA_MODEL, str)
        assert len(OLLAMA_MODEL) > 0
    
    def test_embedding_model_set(self):
        """Test embedding model configuration"""
        assert isinstance(OLLAMA_EMBEDDING_MODEL, str)
        assert len(OLLAMA_EMBEDDING_MODEL) > 0
    
    def test_supported_extensions(self):
        """Test supported file extensions"""
        assert isinstance(SUPPORTED_EXTENSIONS, set)
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
    
    def test_similarity_config(self):
        """Test similarity configuration values"""
        assert isinstance(SIMILARITY_TOP_K, int)
        assert SIMILARITY_TOP_K > 0
        assert isinstance(SIMILARITY_CUTOFF, float)
        assert 0.0 <= SIMILARITY_CUTOFF <= 1.0

