"""
GhostVault Configuration
Centralized configuration management for the application.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "db"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_REQUEST_TIMEOUT = float(os.getenv("OLLAMA_REQUEST_TIMEOUT", "300.0"))

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ghostvault")
CHROMA_PERSIST_DIR = str(DB_DIR)

# Supported file types
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}

# Retrieval Configuration
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))
SIMILARITY_CUTOFF = float(os.getenv("SIMILARITY_CUTOFF", "0.7"))

# Watchdog Configuration
WATCHDOG_POLL_INTERVAL = float(os.getenv("WATCHDOG_POLL_INTERVAL", "1.0"))
FILE_WRITE_DELAY = float(os.getenv("FILE_WRITE_DELAY", "1.0"))

# UI Configuration
STREAMING_DELAY = float(os.getenv("STREAMING_DELAY", "0.01"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2.0"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "ghostvault.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
