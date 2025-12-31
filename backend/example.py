"""
Example script demonstrating how to use the URL Ingestion Pipeline
"""
import os
from main import URLIngestionPipeline

def example_usage():
    """
    Example of how to use the URL ingestion pipeline programmatically
    """
    # Get API keys from environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not all([cohere_api_key, qdrant_url, qdrant_api_key]):
        print("Please set the required environment variables:")
        print("- COHERE_API_KEY")
        print("- QDRANT_URL")
        print("- QDRANT_API_KEY")
        return

    # Create pipeline instance
    pipeline = URLIngestionPipeline(
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key
    )

    # Run the pipeline on a specific URL
    base_url = "https://example.com"
    pipeline.run_pipeline(base_url, max_depth=1, max_urls=3)

if __name__ == "__main__":
    example_usage()