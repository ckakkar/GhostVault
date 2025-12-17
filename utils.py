"""
GhostVault Utilities
Helper functions and utilities for the application.
"""

import logging
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb

from config import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT, handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """Decorator for retrying functions on failure."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {retries}/{max_retries}): {e}. Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper

    return decorator


def get_db_stats(db_path: Path, collection_name: str) -> Dict[str, Any]:
    """Get statistics about the ChromaDB collection."""
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        collection = client.get_collection(name=collection_name)
        count = collection.count()

        return {"document_count": count, "status": "active" if count > 0 else "empty"}
    except Exception as e:
        logger.error(f"Error getting DB stats: {e}")
        return {"document_count": 0, "status": "error", "error": str(e)}


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def extract_source_info(node) -> Optional[Dict[str, str]]:
    """Extract source information from a retrieval node."""
    try:
        if not hasattr(node, "node") or not hasattr(node.node, "metadata"):
            return None

        metadata = node.node.metadata
        file_path = metadata.get("file_path", metadata.get("file_name", "Unknown"))
        page_label = metadata.get("page_label", metadata.get("page_number", metadata.get("page", "N/A")))

        file_name = Path(file_path).name if file_path != "Unknown" else "Unknown"

        return {"file_name": file_name, "page": str(page_label), "full_path": str(file_path)}
    except Exception as e:
        logger.warning(f"Error extracting source info: {e}")
        return None


def deduplicate_sources(sources: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Remove duplicate sources based on file name and page."""
    seen = set()
    unique_sources = []

    for source in sources:
        if source is None:
            continue

        key = (source.get("file_name"), source.get("page"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(source)

    return unique_sources


def get_indexed_documents(db_path: Path, collection_name: str) -> List[Dict[str, Any]]:
    """Get list of all indexed documents with metadata."""
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        collection = client.get_collection(name=collection_name)

        # Get all documents
        results = collection.get(include=["metadatas", "documents"])

        documents_map = {}
        if results and results.get("metadatas"):
            for metadata in results["metadatas"]:
                file_path = metadata.get("file_path") or metadata.get("file_name", "Unknown")
                file_name = Path(file_path).name if file_path != "Unknown" else "Unknown"

                if file_name not in documents_map:
                    documents_map[file_name] = {
                        "file_name": file_name,
                        "file_path": file_path,
                        "chunk_count": 0,
                        "pages": set(),
                        "last_modified": metadata.get("last_modified"),
                    }

                documents_map[file_name]["chunk_count"] += 1
                page = metadata.get("page_label") or metadata.get("page_number") or metadata.get("page")
                if page:
                    documents_map[file_name]["pages"].add(str(page))

        # Convert to list and format
        documents = []
        for doc in documents_map.values():
            doc["pages"] = sorted(list(doc["pages"]), key=lambda x: int(x) if x.isdigit() else 0)
            doc["page_count"] = len(doc["pages"])
            documents.append(doc)

        return sorted(documents, key=lambda x: x["file_name"])
    except Exception as e:
        logger.error(f"Error getting indexed documents: {e}")
        return []


def get_detailed_stats(db_path: Path, collection_name: str) -> Dict[str, Any]:
    """Get detailed statistics about the knowledge base."""
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        collection = client.get_collection(name=collection_name)

        stats = get_db_stats(db_path, collection_name)
        documents = get_indexed_documents(db_path, collection_name)

        total_chunks = sum(doc["chunk_count"] for doc in documents)
        total_pages = sum(doc["page_count"] for doc in documents)

        # Count by file type
        file_types = {}
        for doc in documents:
            ext = Path(doc["file_name"]).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1

        return {
            "document_count": stats.get("document_count", 0),
            "total_chunks": total_chunks,
            "total_pages": total_pages,
            "documents": documents,
            "file_types": file_types,
            "status": stats.get("status", "unknown"),
        }
    except Exception as e:
        logger.error(f"Error getting detailed stats: {e}")
        return {
            "document_count": 0,
            "total_chunks": 0,
            "total_pages": 0,
            "documents": [],
            "file_types": {},
            "status": "error",
        }
