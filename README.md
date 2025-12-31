# Embedding Pipeline for RAG System

This project implements an embedding pipeline for a Retrieval-Augmented Generation (RAG) system that extracts content from Docusaurus documentation sites, generates semantic embeddings, and stores them in a vector database.

## Features

- **Content Extraction**: Extracts text content from Docusaurus URLs while preserving document structure and hierarchy
- **Content Validation**: Validates content quality before processing
- **Embedding Generation**: Generates semantic embeddings using Cohere's embedding API
- **Vector Storage**: Stores embeddings in Qdrant vector database with metadata linking
- **Pipeline Orchestration**: Complete workflow management with monitoring and error handling

## Architecture

The pipeline consists of the following components:

- `ContentExtractor`: Extracts content from Docusaurus URLs
- `ContentValidator`: Validates content quality
- `EmbeddingGenerator`: Generates semantic embeddings using Cohere
- `VectorStorage`: Stores embeddings in Qdrant vector database
- `PipelineManager`: Orchestrates the complete workflow

## Requirements

- Python 3.13+
- Cohere API key
- Qdrant vector database (local or cloud)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 cohere qdrant-client urllib3
   ```

## Configuration

Set the required environment variables:

```bash
export COHERE_API_KEY="your-cohere-api-key"
export QDRANT_HOST="localhost"  # Optional, defaults to localhost
export QDRANT_PORT="6333"      # Optional, defaults to 6333
export QDRANT_API_KEY="your-qdrant-api-key"  # Optional, for cloud instances
export QDRANT_URL="your-qdrant-cloud-url"    # Optional, for cloud instances
```

## Usage

### Command Line Interface

```bash
python -m src.cli.cli <URL1> <URL2> ...
```

### Python API

```python
from src.pipeline import PipelineManager
from src.extractor import ContentExtractor
from src.validator import ContentValidator
from src.embedder import EmbeddingGenerator
from src.storage import VectorStorage

# Create components
extractor = ContentExtractor()
validator = ContentValidator()
embedder = EmbeddingGenerator()
storage = VectorStorage()

# Create pipeline manager
pipeline_manager = PipelineManager()
pipeline_manager.set_components(extractor, validator, embedder, storage)

# Process URLs
urls = ["https://example.com/docs"]
results = pipeline_manager.run_pipeline(urls)
```

### Example

Run the example script to see the pipeline in action:

```bash
python example.py
```

## Environment Variables

- `COHERE_API_KEY`: Your Cohere API key (required)
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `QDRANT_API_KEY`: Qdrant API key (optional)
- `QDRANT_URL`: Qdrant cloud URL (optional, alternative to host/port)
- `COLLECTION_NAME`: Qdrant collection name (default: embeddings)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Log file path (default: pipeline.log)
- `BATCH_SIZE`: Processing batch size (default: 10)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `TIMEOUT`: Request timeout in seconds (default: 30)

## Project Structure

```
src/
├── cli/              # Command line interface
├── lib/              # Utility functions and configuration
├── models/           # Data models
├── extractor.py      # Content extraction module
├── validator.py      # Content validation module
├── embedder.py       # Embedding generation module
├── storage.py        # Vector storage module
└── pipeline.py       # Pipeline orchestration module
```

## Development

To run tests:

```bash
# Coming soon
```

## License

MIT