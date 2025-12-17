# GhostVault

[![CI](https://github.com/YOUR_USERNAME/GhostVault/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/GhostVault/actions/workflows/ci.yml)

A local RAG (Retrieval-Augmented Generation) system that actually feels like you're working with an intelligence system, not just another chatbot. Built for macOS with a focus on privacy, performance, and that satisfying "hacking into the mainframe" aesthetic.

## Why I Built This

I was frustrated with existing RAG solutions that either required cloud APIs (privacy concerns) or looked like they were designed in 2010. GhostVault is my attempt at building something that feels professional, runs entirely locally, and doesn't compromise on user experience.

The name comes from the fact that everything runs in the background like a ghost, and your documents are stored securely in a vault (ChromaDB). Plus, it sounds cool.

## What Makes This Different

**Three AI Personalities** - Not just one chatbot, but three distinct modes:
- **The Architect** - Dives deep into technical details, loves code examples, explains the "why" behind everything
- **The Executive** - Concise, strategic, all about ROI and high-level insights
- **The Skeptic** - Questions everything, demands proof, finds the holes in arguments

**Automatic Ingestion** - Drop a PDF in the `data/` folder and it's indexed automatically. No manual steps, no hassle.

**Source Attribution** - Every response ends with a "Decrypted Sources" section showing exactly where the information came from. No hallucinations, full transparency.

**Runs Entirely Locally** - Your documents never leave your machine. Perfect for sensitive work or when you just want to keep things private.

**Document Management** - Built-in commands and actions to list documents, view statistics, delete documents, and manage your knowledge base.

## Tech Stack

- **Python 3.11** - Modern Python with all the good stuff
- **LlamaIndex** - Handles the RAG pipeline (v0.10+)
- **Chainlit** - Modern chat UI that doesn't make me cringe
- **Ollama** - Local LLM inference (Llama3 + nomic-embed-text for M2 optimization)
- **ChromaDB** - Persistent vector storage
- **Watchdog** - File system monitoring for automatic ingestion

## Setup

### Prerequisites

You'll need Python 3.11+ and Ollama installed. If you don't have Ollama:

```bash
brew install ollama
ollama serve
```

Then pull the models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### Installation

1. Clone this repo (or just download it, I'm not your boss)

2. Create a virtual environment:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. (Optional) Copy `.env.example` to `.env` and tweak settings if you want. Defaults work fine for most cases.

### Running It

You'll need two terminals:

**Terminal 1 - Ingestion Service:**
```bash
python ingest.py
```

This watches the `data/` directory and automatically indexes any PDFs, markdown files, or text files you drop in.

**Terminal 2 - The App:**
```bash
chainlit run app.py
```

Then open your browser to `http://localhost:8000` and you're good to go.

## Usage

1. **Add Documents** - Drop PDF, TXT, or MD files into the `data/` directory. The ingestion service will automatically index them (you'll see "Intercepting encrypted transmission" messages).

2. **Choose a Profile** - When you start a new chat, pick one of the three profiles. Each has a completely different personality and response style.

3. **Ask Questions** - Just chat naturally. The system will retrieve relevant chunks from your documents and generate responses in the style of your chosen profile.

4. **Check Sources** - Every response ends with source citations showing the exact file and page number. Click through if you want to verify.

5. **Manage Documents** - Use the action buttons or commands:
   - **Action Buttons**: Click the buttons in the welcome message to list documents, view stats, or clear the index
   - **Commands**: Type `/list`, `/stats`, or `/delete <filename>` to manage your knowledge base

## Project Structure

```
GhostVault/
├── app.py              # Main Chainlit application
├── ingest.py           # Watchdog service for automatic indexing
├── config.py           # Centralized configuration
├── utils.py            # Helper functions and utilities
├── style.css           # Dark cyberpunk theme
├── chainlit.md         # Welcome screen
├── data/               # Drop your documents here
├── db/                 # ChromaDB storage (auto-created)
└── logs/               # Application logs (auto-created)
```

## Configuration

Most settings can be tweaked via environment variables or in `config.py`. Key ones:

- `OLLAMA_MODEL` - Which LLM to use (default: llama3)
- `OLLAMA_EMBEDDING_MODEL` - Embedding model (default: nomic-embed-text, optimized for M2)
- `SIMILARITY_TOP_K` - How many chunks to retrieve (default: 5)
- `SIMILARITY_CUTOFF` - Minimum similarity score (default: 0.7)

Check `config.py` for the full list.

## Design Decisions

**Why Chainlit?** - I tried building a custom UI with Flask/FastAPI, but Chainlit just works. It handles streaming, sessions, and all the annoying parts so I can focus on the RAG logic.

**Why ChromaDB?** - Persistent storage out of the box, easy to query, works great for local development. Plus it's Python-native.

**Why three profiles?** - Because different questions need different answers. Sometimes you want the technical deep-dive, sometimes you just want the executive summary. The Skeptic is there because I'm naturally suspicious and wanted an AI that shares that trait.

**Why Watchdog?** - Manually triggering indexing is annoying. File system events mean it "just works" - drop a file, it's indexed. No buttons to click.

## Performance

On an M2 Mac, responses are snappy (usually 2-5 seconds depending on query complexity). The nomic-embed-text model is specifically optimized for Apple Silicon, so embeddings are fast.

Indexing speed depends on document size, but a typical 50-page PDF takes about 10-20 seconds to process.

## Known Limitations

- Currently supports PDF, TXT, and Markdown files. More formats can be added easily.
- The UI is dark theme only (by design, it's supposed to look like a terminal)
- All processing happens on your machine, so if you have a weak CPU it might be slow
- No web interface for managing documents (yet) - you just use the file system

## Future Ideas

Things I might add if I get bored:

- [ ] Web interface for document management
- [ ] Support for more file types (Word docs, images with OCR)
- [ ] Custom profile creation
- [ ] Export chat history
- [ ] Batch import from folders
- [ ] Better error recovery (retry logic is there, but could be smarter)

## Contributing

This is a personal project, but if you find bugs or have ideas, feel free to open an issue. Just don't expect me to respond immediately - I have a day job.

## Testing

The project includes a comprehensive test suite using pytest. To run tests locally:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

Or use the Makefile:

```bash
make install-dev  # Install dependencies
make test         # Run tests
make test-cov     # Run tests with coverage
make lint         # Check code quality
make format       # Auto-format code
```

### CI/CD

GitHub Actions runs tests automatically on every push and pull request. The CI pipeline includes:

- Unit tests across Python 3.11 and 3.12
- Code linting with flake8
- Code formatting checks with black
- Import sorting verification with isort

Check the `.github/workflows/ci.yml` file for the full CI configuration. The badge at the top shows the current CI status (update the GitHub username/org in the badge URL).

## License

MIT License - do whatever you want with it. If you use this in production, maybe throw me a mention. Or don't. I'm not tracking you.

## Credits

Built with love (and caffeine) using:
- [LlamaIndex](https://www.llamaindex.ai/) - Makes RAG actually manageable
- [Chainlit](https://chainlit.io/) - Because building UIs is hard
- [Ollama](https://ollama.ai/) - Local LLMs that actually work
- [ChromaDB](https://www.trychroma.com/) - Vector databases made simple

---

**GhostVault System Online. Intelligence core active.**

