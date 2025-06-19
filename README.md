
# Doc AI Search - Semantic Product Document Indexing

Doc AI Search is an AI-powered pipeline for intelligent document indexing and semantic search. It enables storing and querying product documents (PDF/DOCX) using Google's Gemini embedding model and PostgreSQL with pgvector for high-quality semantic retrieval.

---

## Table of Contents

- [Directory Structure](#directory-structure)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Configure your environment variables](#2-configure-your-environment-variables)
  - [3. Run the setup script](#3-run-the-setup-script)
- [Running the Indexer](#running-the-indexer)
- [Running the Searcher](#running-the-searcher)
- [Security Warning](#security-warning)
- [License](#license)

---

## Directory Structure

```plaintext
DocAISearch/
├── indexer/                            # Document processing & indexing logic
│   ├── index_documents.py              # Parse documents, chunk, embed, store in DB
│   └── run_ksp_indexer.sh              # Shell script to run the indexer
│
├── searcher/                           # Semantic search interface
│   ├── search_documents.py             # Accepts query and retrieves most relevant chunks
│   └── run_ksp_searcher.sh             # Shell script to run the searcher
│
├── data/                               # Input document samples
│   └── ksp_example_catalog.pdf         # Example PDF catalog with 1000+ Hebrew words
│
├── requirements.txt                    # All required Python dependencies for both scripts
├── .env                                # Environment secrets (API key, DB creds)
├── setup.sh                            # Environment creation and dependency installer
├── README.md                           # Project documentation (this file)
```

---

## Features

- Smart text chunking (fixed/sentence/paragraph)
- Google Gemini embeddings (embedding-001)
- PostgreSQL + pgvector integration
- Cosine similarity search for top-5 relevant results
- CLI-based search and indexing utilities

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-user/DocAISearch.git
cd DocAISearch
```

### 2. Configure your environment variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydb
DB_USER=ksp
DB_PASSWORD=ksp_example
```

### 3. Run the setup script

```bash
chmod +x setup.sh
./setup.sh
```

The `setup.sh` script will:

- Create a virtual environment (`venv`)
- Activate it
- Install all dependencies from `requirements.txt`
- Prepare the environment for indexing and searching

> ⚠️ This script simplifies and standardizes environment setup so you don’t need to install packages globally.

---

## Running the Indexer

```bash
./indexer/run_ksp_indexer.sh
```

This will:

- Extract and parse text from the sample document
- Create text chunks using fixed-length strategy
- Generate embeddings with Gemini
- Store everything in PostgreSQL

---

## Running the Searcher

```bash
./searcher/run_ksp_searcher.sh
```

This will:

- Ask the user for a search query
- Convert it to an embedding
- Perform semantic similarity search against the DB
- Return the top 5 most relevant document chunks

---

## Security Warning

Never upload `.env` files to public repositories. They contain sensitive credentials.

---

## License

MIT License. Feel free to use and modify for research or commercial use.

Contributions, improvements, or extensions (e.g., support for web UI or other languages) are welcome!
