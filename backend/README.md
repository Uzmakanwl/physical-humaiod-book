# URL Ingestion & Embedding Pipeline

This project implements a complete pipeline for ingesting URLs, extracting text content, generating embeddings using Cohere, and storing them in Qdrant cloud.

## Features

- URL discovery and crawling
- Text extraction from web pages
- Text chunking with overlap
- Embedding generation using Cohere models
- Vector storage in Qdrant cloud
- End-to-end orchestration

## Prerequisites

Before running this pipeline, you'll need:

1. **Cohere API Key**: Get one from [Cohere](https://cohere.com/)
2. **Qdrant Cloud Account**: Get credentials from [Qdrant Cloud](https://qdrant.tech/)
3. **Python 3.13+**
4. **uv** package manager

## Setup

1. Install dependencies:
   ```bash
   cd backend
   uv sync
   ```

2. Set environment variables:
   ```bash
   export COHERE_API_KEY="your-cohere-api-key"
   export QDRANT_URL="your-qdrant-cloud-url"
   export QDRANT_API_KEY="your-qdrant-api-key"
   export BASE_URL="https://example.com"  # Optional, defaults to https://example.com
   ```

## Usage

Run the complete pipeline:
```bash
uv run main.py
```

## Configuration

You can customize the pipeline behavior by adjusting these parameters in the `run_pipeline` method:
- `max_depth`: Maximum depth for URL crawling (currently supports depth 1)
- `max_urls`: Maximum number of URLs to process
- `chunk_size`: Size of text chunks (default: 512 characters)
- `overlap`: Overlap between chunks (default: 50 characters)

## Architecture

The pipeline consists of these main components:

1. **URL Discovery**: Discovers URLs from a base URL
2. **Text Extraction**: Extracts clean text from web pages using BeautifulSoup
3. **Text Chunking**: Splits long text into overlapping chunks
4. **Embedding Generation**: Creates vector embeddings using Cohere's models
5. **Vector Storage**: Stores embeddings in Qdrant cloud with metadata

## Environment Variables

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: URL of your Qdrant cloud instance
- `QDRANT_API_KEY`: API key for your Qdrant cloud instance
- `BASE_URL`: Starting URL for ingestion (optional, defaults to "https://example.com")

## How It Works

1. The pipeline starts by discovering URLs from a base URL
2. For each URL, it extracts the text content and removes HTML tags
3. The text is then chunked into smaller pieces with overlap
4. Each chunk is sent to Cohere for embedding generation
5. The embeddings are stored in Qdrant cloud with the original text and URL metadata