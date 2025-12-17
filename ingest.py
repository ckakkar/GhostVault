#!/usr/bin/env python3
"""
GhostVault Ingestion System
Monitors the data/ directory for new PDF files and automatically indexes them.
"""

import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Configuration
DATA_DIR = Path("./data")
DB_DIR = Path("./db")
SUPPORTED_EXTENSIONS = {".pdf"}

# Initialize embeddings
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
chroma_collection = chroma_client.get_or_create_collection(name="ghostvault")
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
            # Try to get the collection count to see if index exists
            collection_count = chroma_collection.count()
            if collection_count > 0:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context
                )
                print("✅ GhostVault System Online. Intelligence core active.")
                print(f"📚 Loaded existing knowledge base ({collection_count} documents).")
            else:
                # Empty collection, create new index structure
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context
                )
                print("✅ GhostVault System Online. Intelligence core active.")
                print("📁 Knowledge base initialized. Ready for documents.")
        except Exception as e:
            # If anything fails, create a fresh index
            print(f"⚠️  Initializing new knowledge base. ({e})")
            self.index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context
            )
    
    def _index_file(self, file_path: Path):
        """Index a single PDF file into ChromaDB."""
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        
        if str(file_path) in self.processed_files:
            return
        
        try:
            print(f"🔍 Intercepting encrypted transmission: {file_path.name}")
            
            # Read and index the document
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
            
            if self.index is None:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context
                )
            
            # Add documents to the index
            for doc in documents:
                self.index.insert(doc)
            
            self.processed_files.add(str(file_path))
            print(f"✅ Successfully indexed: {file_path.name}")
            
        except Exception as e:
            print(f"❌ Error indexing {file_path.name}: {e}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            # Wait a bit for file to be fully written
            time.sleep(1)
            self._index_file(file_path)
    
    def on_moved(self, event):
        """Handle file move events (e.g., drag-and-drop)."""
        if event.is_directory:
            return
        
        file_path = Path(event.dest_path)
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            time.sleep(1)
            self._index_file(file_path)


def index_existing_files():
    """Index all existing PDF files in the data directory."""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created data directory: {DATA_DIR}")
        return
    
    handler = PDFHandler()
    pdf_files = list(DATA_DIR.glob("*.pdf"))
    
    if pdf_files:
        print(f"📚 Found {len(pdf_files)} existing PDF(s). Indexing...")
        for pdf_file in pdf_files:
            handler._index_file(pdf_file)
    else:
        print("📁 Data directory is empty. Waiting for files...")


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
    
    print("👁️  Watchdog activated. Monitoring data/ directory...")
    print("💡 Place PDF files in the 'data/' directory to automatically index them.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Shutting down GhostVault ingestion system...")
    
    observer.join()


if __name__ == "__main__":
    start_watcher()

