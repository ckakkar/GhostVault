"""
Document Management Utilities
Functions for managing indexed documents in ChromaDB
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import chromadb

from config import CHROMA_COLLECTION_NAME, DB_DIR
from utils import logger


def list_documents() -> List[Dict]:
    """List all indexed documents."""
    try:
        client = chromadb.PersistentClient(path=str(DB_DIR))
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)

        results = collection.get(include=["metadatas"])

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
                    }

                documents_map[file_name]["chunk_count"] += 1
                page = metadata.get("page_label") or metadata.get("page_number") or metadata.get("page")
                if page:
                    documents_map[file_name]["pages"].add(str(page))

        documents = []
        for doc in documents_map.values():
            doc["pages"] = sorted(list(doc["pages"]), key=lambda x: int(x) if x.isdigit() else 0)
            doc["page_count"] = len(doc["pages"])
            documents.append(doc)

        return sorted(documents, key=lambda x: x["file_name"])
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return []


def delete_document(file_name: str) -> bool:
    """Delete a document from the index by file name."""
    try:
        client = chromadb.PersistentClient(path=str(DB_DIR))
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)

        # Get all IDs with matching file_name in metadata
        results = collection.get(include=["metadatas", "ids"])
        ids_to_delete = []

        if results and results.get("metadatas") and results.get("ids"):
            for metadata, doc_id in zip(results["metadatas"], results["ids"]):
                meta_file_path = metadata.get("file_path") or metadata.get("file_name", "")
                meta_file_name = Path(meta_file_path).name if meta_file_path else ""

                if meta_file_name == file_name:
                    ids_to_delete.append(doc_id)

        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            logger.info(f"Deleted {len(ids_to_delete)} chunks for document: {file_name}")
            return True
        else:
            logger.warning(f"No chunks found for document: {file_name}")
            return False

    except Exception as e:
        logger.error(f"Error deleting document {file_name}: {e}")
        return False


def get_document_info(file_name: str) -> Optional[Dict]:
    """Get detailed information about a specific document."""
    documents = list_documents()
    for doc in documents:
        if doc["file_name"] == file_name:
            return doc
    return None


def get_document_count() -> int:
    """Get the total number of unique documents indexed."""
    documents = list_documents()
    return len(documents)


def clear_all_documents() -> int:
    """Clear all documents from the index. Returns number of documents cleared."""
    try:
        client = chromadb.PersistentClient(path=str(DB_DIR))
        collection = client.get_collection(name=CHROMA_COLLECTION_NAME)

        count_before = collection.count()

        # Get all IDs and delete them
        results = collection.get(include=["ids"])
        if results and results.get("ids"):
            collection.delete(ids=results["ids"])

        logger.info(f"Cleared {count_before} chunks from index")
        return count_before
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        return 0
