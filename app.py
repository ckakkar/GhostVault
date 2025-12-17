#!/usr/bin/env python3
"""
GhostVault - Intelligence System
A professional RAG application with personality-based chat profiles.
"""

import asyncio
from pathlib import Path

import chainlit as cl
import chromadb
from llama_index.core import Settings, StorageContext, VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

from config import (
    CHROMA_COLLECTION_NAME,
    DB_DIR,
    OLLAMA_EMBEDDING_MODEL,
    OLLAMA_MODEL,
    OLLAMA_REQUEST_TIMEOUT,
    SIMILARITY_CUTOFF,
    SIMILARITY_TOP_K,
    STREAMING_DELAY,
)
from document_manager import (
    clear_all_documents,
    delete_document,
    get_document_count,
    get_document_info,
    list_documents,
)
from utils import deduplicate_sources, extract_source_info, get_db_stats, get_detailed_stats, logger

# Initialize LLM and Embeddings (optimized for M2)
Settings.llm = Ollama(model=OLLAMA_MODEL, request_timeout=OLLAMA_REQUEST_TIMEOUT)
Settings.embed_model = OllamaEmbedding(model_name=OLLAMA_EMBEDDING_MODEL)

# Chat Profile System Prompts
PROFILE_PROMPTS = {
    "the-architect": """You are "The Architect" - a highly technical, detail-oriented AI assistant. 
Your responses should:
- Focus on code structure, technical specifications, and implementation details
- Provide deep technical analysis with code examples when relevant
- Break down complex systems into their component parts
- Use precise technical terminology
- Explain the "how" and "why" behind technical decisions
Always base your answers on the provided documents and cite specific technical details.""",
    "the-executive": """You are "The Executive" - a concise, high-level strategic advisor.
Your responses should:
- Be brief and action-oriented
- Use bullet points and structured summaries
- Focus on high-level concepts, key takeaways, and ROI implications
- Avoid technical jargon unless necessary
- Provide strategic insights and recommendations
- Prioritize clarity and brevity
Always base your answers on the provided documents and highlight key business insights.""",
    "the-skeptic": """You are "The Skeptic" - a critical analyst who challenges assumptions.
Your responses should:
- Question assumptions and demand evidence
- Point out potential weaknesses or gaps in reasoning
- Ask probing questions about the provided information
- Highlight contradictions or inconsistencies in the documents
- Require strict proof and logical reasoning
- Challenge claims that lack sufficient support
Always base your critique on the provided documents and demand rigorous evidence for all claims.""",
}


@cl.set_chat_profiles
async def chat_profile():
    """Define the three chat profiles for GhostVault."""
    return [
        cl.ChatProfile(
            name="the-architect",
            markdown_description="**The Architect**: Highly technical, focuses on code structure, specs, and implementation details.",
            icon="🏗️",
        ),
        cl.ChatProfile(
            name="the-executive",
            markdown_description="**The Executive**: Brief, bullet-point summaries, focuses on high-level concepts and ROI.",
            icon="👔",
        ),
        cl.ChatProfile(
            name="the-skeptic",
            markdown_description="**The Skeptic**: Critical analysis, challenges assumptions, demands strict proof from documents.",
            icon="🔍",
        ),
    ]


@cl.on_chat_start
async def start():
    """Initialize the chat session with the selected profile."""
    # Get the selected chat profile
    profile = cl.user_session.get("chat_profile")

    if not profile:
        profile_name = "the-architect"  # Default
    else:
        profile_name = profile

    # Load the system prompt for the selected profile
    system_prompt = PROFILE_PROMPTS.get(profile_name, PROFILE_PROMPTS["the-architect"])

    # Initialize ChromaDB connection
    try:
        chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
        chroma_collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Load the index
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context)

        # Create query engine with retriever
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=SIMILARITY_TOP_K,
        )

        # Configure query engine
        query_engine = RetrieverQueryEngine.from_args(
            retriever=retriever,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=SIMILARITY_CUTOFF)],
        )

        # Get database stats
        stats = get_db_stats(DB_DIR, CHROMA_COLLECTION_NAME)
        doc_count = stats.get("document_count", 0)

        # Store in session
        cl.user_session.set("query_engine", query_engine)
        cl.user_session.set("system_prompt", system_prompt)
        cl.user_session.set("profile_name", profile_name)

        # Send welcome message
        profile_display = {
            "the-architect": "🏗️ The Architect",
            "the-executive": "👔 The Executive",
            "the-skeptic": "🔍 The Skeptic",
        }

        profile_icon = {"the-architect": "🏗️", "the-executive": "👔", "the-skeptic": "🔍"}.get(profile_name, "🏗️")
        profile_label = profile_display.get(profile_name, "The Architect")

        welcome_msg = f"**GhostVault System Online**\n\n"
        welcome_msg += f"{profile_icon} **{profile_label}**\n\n"
        if doc_count > 0:
            welcome_msg += f"📚 {doc_count} document{'s' if doc_count != 1 else ''} indexed\n\n"
        welcome_msg += "How can I assist you today?"

        # Add action buttons with clean descriptions
        actions = [
            cl.Action(name="list_documents", value="list", description="📋 Documents"),
            cl.Action(name="show_stats", value="stats", description="📊 Statistics"),
            cl.Action(name="clear_index", value="clear", description="🗑️ Clear Index"),
        ]

        await cl.Message(content=welcome_msg, actions=actions).send()
        logger.info(f"Chat session started with profile: {profile_name}, {doc_count} documents available")

    except chromadb.errors.CollectionNotFoundError:
        error_msg = f"⚠️ **System Error**: Knowledge base collection not found.\n\n"
        error_msg += "Please run the ingestion system first:\n"
        error_msg += "```bash\npython ingest.py\n```\n\n"
        error_msg += "Then place documents in the `data/` directory."
        await cl.Message(content=error_msg).send()
        logger.error("ChromaDB collection not found")
    except Exception as e:
        logger.error(f"Error initializing chat session: {e}", exc_info=True)
        await cl.Message(
            content=f"⚠️ **System Error**: Unable to connect to knowledge base.\n\nError: {str(e)}\n\nPlease ensure:\n1. The ingestion system has been run (`python ingest.py`)\n2. Documents have been indexed in the `data/` directory\n3. ChromaDB is accessible at `./db`"
        ).send()


def format_documents_list(documents: list) -> str:
    """Format documents list with clean, minimal styling."""
    if not documents:
        return "📋 **No documents indexed**\n\nAdd documents to the `data/` directory to get started."

    msg = "📋 **Indexed Documents**\n\n"
    for doc in documents:
        msg += f"**{doc['file_name']}**\n"
        msg += f"• {doc['chunk_count']} chunks • {doc['page_count']} pages\n\n"

    return msg.strip()


def format_statistics(stats: dict) -> str:
    """Format statistics with clean, organized display."""
    msg = "📊 **Knowledge Base Statistics**\n\n"
    msg += f"**Overview**\n"
    msg += f"• Documents: `{stats['document_count']}`\n"
    msg += f"• Total Chunks: `{stats['total_chunks']}`\n"
    msg += f"• Total Pages: `{stats['total_pages']}`\n\n"

    if stats.get("file_types"):
        msg += "**By File Type**\n"
        for ext, count in sorted(stats["file_types"].items()):
            ext_display = ext if ext else "No extension"
            msg += f"• `{ext_display}`: {count}\n"
        msg += "\n"

    msg += f"Status: `{stats.get('status', 'unknown').upper()}`"
    return msg


@cl.on_action
async def on_action(action: cl.Action):
    """Handle action button clicks with clean responses."""
    if action.name == "list_documents":
        documents = list_documents()
        msg = format_documents_list(documents)
        await cl.Message(content=msg).send()

    elif action.name == "show_stats":
        stats = get_detailed_stats(DB_DIR, CHROMA_COLLECTION_NAME)
        msg = format_statistics(stats)
        await cl.Message(content=msg).send()

    elif action.name == "clear_index":
        count = clear_all_documents()
        msg = f"🗑️ **Index Cleared**\n\nRemoved `{count}` chunks from the knowledge base.\n\nPlace documents in `data/` to re-index."
        await cl.Message(content=msg).send()

    elif action.name == "delete_document":
        file_name = action.value
        success = delete_document(file_name)
        if success:
            msg = f"✅ Removed `{file_name}` from the knowledge base."
        else:
            msg = f"❌ Could not delete `{file_name}`. Document may not exist."
        await cl.Message(content=msg).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages with the selected profile's personality."""
    # Get query engine and system prompt from session
    query_engine = cl.user_session.get("query_engine")
    system_prompt = cl.user_session.get("system_prompt")
    profile_name = cl.user_session.get("profile_name", "the-architect")

    if not query_engine:
        await cl.Message(content="❌ **Error**: Query engine not initialized. Please refresh the page.").send()
        return

    # Check for special commands
    query_text = message.content.strip().lower()

    # Handle special commands with clean formatting
    if query_text.startswith("/list") or query_text == "/docs":
        documents = list_documents()
        msg = format_documents_list(documents)
        await cl.Message(content=msg).send()
        return

    elif query_text.startswith("/stats") or query_text == "/stat":
        stats = get_detailed_stats(DB_DIR, CHROMA_COLLECTION_NAME)
        msg = format_statistics(stats)
        await cl.Message(content=msg).send()
        return

    elif query_text.startswith("/delete "):
        file_name = message.content.replace("/delete", "").strip()
        success = delete_document(file_name)
        msg = f"✅ Removed `{file_name}`" if success else f"❌ Could not delete `{file_name}`"
        await cl.Message(content=msg).send()
        return

    # Create the query with system prompt
    full_query = f"{system_prompt}\n\nUser Question: {message.content}"

    # Create a streaming response
    response = cl.Message(content="")
    await response.send()

    # Stream the response
    response_text = ""
    sources_list = []

    try:
        logger.info(f"Processing query with profile: {profile_name}")

        # Query the engine
        query_response = query_engine.query(full_query)

        # Extract the response text
        if hasattr(query_response, "response"):
            response_text = str(query_response.response)
        else:
            response_text = str(query_response)

        # Extract sources from the response
        if hasattr(query_response, "source_nodes") and query_response.source_nodes:
            raw_sources = [extract_source_info(node) for node in query_response.source_nodes]
            unique_sources = deduplicate_sources([s for s in raw_sources if s])

            for source in unique_sources:
                sources_list.append(f"{source['file_name']} (Page {source['page']})")

            logger.info(f"Retrieved {len(sources_list)} unique sources for query")

        # Stream the response character by character for typing effect
        accumulated = ""
        for char in response_text:
            accumulated += char
            response.content = accumulated
            await response.update()
            # Small delay for typing effect
            await asyncio.sleep(STREAMING_DELAY)

        # Add sources section with clean formatting
        if sources_list:
            sources_section = "\n\n---\n\n**Sources**\n\n"
            for source in sources_list:
                sources_section += f"• `{source}`\n"
            response.content = response_text + sources_section
            await response.update()
        else:
            sources_section = "\n\n---\n\n**Sources**\n\nNo sources retrieved."
            response.content = response_text + sources_section
            await response.update()

    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        error_msg = f"❌ **Query Error**: {str(e)}\n\nPlease check:\n1. Ollama is running (`ollama serve`)\n2. {OLLAMA_MODEL} model is available (`ollama pull {OLLAMA_MODEL}`)\n3. {OLLAMA_EMBEDDING_MODEL} model is available (`ollama pull {OLLAMA_EMBEDDING_MODEL}`)"
        response.content = error_msg
        await response.update()


if __name__ == "__main__":
    # This is handled by Chainlit's CLI
    pass
