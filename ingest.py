#!/usr/bin/env python3
"""
GhostVault Ingestion System
Monitors the data/ directory for new documents and automatically indexes them.
Supports PDF, TXT, MD, and Markdown files.
"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from config import (
    DATA_DIR, DB_DIR, SUPPORTED_EXTENSIONS,
    OLLAMA_EMBEDDING_MODEL, CHROMA_COLLECTION_NAME,
    FILE_WRITE_DELAY, WATCHDOG_POLL_INTERVAL
)
from utils import logger, retry_on_failure, get_db_stats

# Initialize embeddings
Settings.embed_model = OllamaEmbedding(model_name=OLLAMA_EMBEDDING_MODEL)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
chroma_collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


class PDFHandler(FileSystemEventHandler):
    """Handles file system events for PDF ingestion."""
    
    def __init__(self):
        self.index = None
        self.processed_files = set()
        self._load_existing_index()
    
    def _load_existing_index(self):
        """Load existing index if available."""
        try:
            stats = get_db_stats(DB_DIR, CHROMA_COLLECTION_NAME)
            collection_count = stats.get("document_count", 0)
            
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
            
            if collection_count > 0:
                logger.info(f"Loaded existing knowledge base with {collection_count} documents")
                print("✅ GhostVault System Online. Intelligence core active.")
                print(f"📚 Loaded existing knowledge base ({collection_count} documents).")
            else:
                logger.info("Initialized new knowledge base")
                print("✅ GhostVault System Online. Intelligence core active.")
                print("📁 Knowledge base initialized. Ready for documents.")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            print(f"⚠️  Initializing new knowledge base. ({e})")
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
    
    @retry_on_failure(max_retries=3, delay=2.0)
    def _index_file(self, file_path: Path):
        """Index a single document file into ChromaDB."""
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        
        if str(file_path) in self.processed_files:
            logger.debug(f"Skipping already processed file: {file_path.name}")
            return
        
        try:
            logger.info(f"Indexing file: {file_path.name}")
            print(f"🔍 Intercepting encrypted transmission: {file_path.name}")
            
            # Read and index the document
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
            
            if not documents:
                logger.warning(f"No content extracted from {file_path.name}")
                print(f"⚠️  No content extracted from {file_path.name}")
                return
            
            if self.index is None:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context
                )
            
            # Add documents to the index
            for doc in documents:
                self.index.insert(doc)
            
            self.processed_files.add(str(file_path))
            logger.info(f"Successfully indexed {file_path.name} ({len(documents)} chunks)")
            print(f"✅ Successfully indexed: {file_path.name} ({len(documents)} chunks)")
            
        except Exception as e:
            logger.error(f"Error indexing {file_path.name}: {e}", exc_info=True)
            print(f"❌ Error indexing {file_path.name}: {e}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            # Wait a bit for file to be fully written
            time.sleep(FILE_WRITE_DELAY)
            self._index_file(file_path)
    
    def on_moved(self, event):
        """Handle file move events (e.g., drag-and-drop)."""
        if event.is_directory:
            return
        
        file_path = Path(event.dest_path)
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            time.sleep(FILE_WRITE_DELAY)
            self._index_file(file_path)


def index_existing_files():
    """Index all existing supported files in the data directory."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created data directory: {DATA_DIR}")
        print(f"📁 Created data directory: {DATA_DIR}")
        return
    
    handler = PDFHandler()
    
    # Find all supported files
    all_files = []
    for ext in SUPPORTED_EXTENSIONS:
        all_files.extend(DATA_DIR.glob(f"*{ext}"))
    
    if all_files:
        logger.info(f"Found {len(all_files)} existing file(s) to index")
        print(f"📚 Found {len(all_files)} existing file(s). Indexing...")
        for file_path in all_files:
            handler._index_file(file_path)
    else:
        logger.info("Data directory is empty")
        print("📁 Data directory is empty. Waiting for files...")
        print(f"💡 Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")


def start_watcher():
    """Start the file system watcher."""
    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Index existing files first
    index_existing_files()
    
    # Set up watchdog
    event_handler = PDFHandler()
    observer = Observer()
    observer.schedule(event_handler, str(DATA_DIR), recursive=False)
    observer.start()
    
    logger.info("Watchdog service started")
    print("👁️  Watchdog activated. Monitoring data/ directory...")
    print(f"💡 Place documents ({', '.join(SUPPORTED_EXTENSIONS)}) in the 'data/' directory to automatically index them.")
    
    try:
        while True:
            time.sleep(WATCHDOG_POLL_INTERVAL)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("Shutting down ingestion system")
        print("\n🛑 Shutting down GhostVault ingestion system...")
    
    observer.join()


if __name__ == "__main__":
    start_watcher()

