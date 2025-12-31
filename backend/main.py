import asyncio
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
import os
from typing import List, Dict, Optional
import time


class URLIngestionPipeline:
    def __init__(self, cohere_api_key: str, qdrant_url: str, qdrant_api_key: str):
        """
        Initialize the URL ingestion pipeline with required API keys and configuration.

        Args:
            cohere_api_key: API key for Cohere embedding service
            qdrant_url: URL for Qdrant cloud instance
            qdrant_api_key: API key for Qdrant cloud instance
        """
        self.cohere_client = cohere.Client(cohere_api_key)
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )
        self.collection_name = "url_embeddings"

    def discover_urls(self, base_url: str, max_depth: int = 1, max_urls: int = 10) -> List[str]:
        """
        Discover URLs from a base URL up to a specified depth.

        Args:
            base_url: Starting URL to discover from
            max_depth: Maximum depth to crawl (currently only supports depth 1)
            max_urls: Maximum number of URLs to discover

        Returns:
            List of discovered URLs
        """
        discovered_urls = set()
        discovered_urls.add(base_url)

        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)

                # Validate URL format
                parsed = urlparse(full_url)
                if parsed.scheme in ['http', 'https'] and full_url not in discovered_urls:
                    discovered_urls.add(full_url)

                if len(discovered_urls) >= max_urls:
                    break
        except Exception as e:
            print(f"Error discovering URLs from {base_url}: {str(e)}")

        return list(discovered_urls)[:max_urls]

    def extract_text_from_url(self, url: str) -> Optional[str]:
        """
        Extract text content from a given URL.

        Args:
            url: URL to extract text from

        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            print(f"Error extracting text from {url}: {str(e)}")
            return None

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks of specified size.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk (in characters)
            overlap: Overlap between chunks (in characters)

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            start = end - overlap

            # Ensure we don't go beyond the text length
            if start >= len(text):
                break

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            response = self.cohere_client.embed(
                texts=texts,
                model="embed-english-v3.0",  # Using Cohere's English embedding model
                input_type="search_document"  # Specify the input type for better embeddings
            )
            return [embedding for embedding in response.embeddings]
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            return []

    def setup_qdrant_collection(self, vector_size: int = 1024):
        """
        Set up the Qdrant collection for storing embeddings.

        Args:
            vector_size: Size of the embedding vectors
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Create collection with specified vector size
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
            else:
                print(f"Qdrant collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error setting up Qdrant collection: {str(e)}")

    def store_embeddings(self, texts: List[str], embeddings: List[List[float]], urls: List[str]):
        """
        Store embeddings and associated text in Qdrant.

        Args:
            texts: Original text chunks
            embeddings: Corresponding embeddings
            urls: URLs associated with the text chunks
        """
        try:
            # Prepare points for Qdrant
            points = []
            for i, (text, embedding, url) in enumerate(zip(texts, embeddings, urls)):
                point = models.PointStruct(
                    id=i,
                    vector=embedding,
                    payload={
                        "text": text,
                        "url": url,
                        "timestamp": time.time()
                    }
                )
                points.append(point)

            # Upload points to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Successfully stored {len(points)} embeddings in Qdrant")
        except Exception as e:
            print(f"Error storing embeddings in Qdrant: {str(e)}")

    def process_url(self, url: str) -> bool:
        """
        Process a single URL through the full pipeline.

        Args:
            url: URL to process

        Returns:
            True if successful, False otherwise
        """
        print(f"Processing URL: {url}")

        # Extract text from URL
        text = self.extract_text_from_url(url)
        if not text:
            print(f"Failed to extract text from {url}")
            return False

        print(f"Extracted {len(text)} characters from {url}")

        # Chunk the text
        chunks = self.chunk_text(text)
        print(f"Created {len(chunks)} chunks from the text")

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        if not embeddings:
            print("Failed to generate embeddings")
            return False

        print(f"Generated {len(embeddings)} embeddings")

        # Create URL list for each chunk
        chunk_urls = [url] * len(chunks)

        # Store in Qdrant
        self.store_embeddings(chunks, embeddings, chunk_urls)

        return True

    def run_pipeline(self, base_url: str, max_depth: int = 1, max_urls: int = 10):
        """
        Run the complete ingestion pipeline from URL discovery to storage.

        Args:
            base_url: Starting URL for discovery
            max_depth: Maximum depth for URL discovery
            max_urls: Maximum number of URLs to process
        """
        print("Starting URL ingestion pipeline...")

        # Discover URLs
        print("Discovering URLs...")
        urls = self.discover_urls(base_url, max_depth, max_urls)
        print(f"Discovered {len(urls)} URLs")

        # Set up Qdrant collection (assuming Cohere's embedding size - typically 1024 for embed-english-v3.0)
        self.setup_qdrant_collection(vector_size=1024)

        # Process each URL
        successful = 0
        for i, url in enumerate(urls):
            print(f"Processing {i+1}/{len(urls)}: {url}")
            if self.process_url(url):
                successful += 1

        print(f"Pipeline completed. Successfully processed {successful}/{len(urls)} URLs")


def main():
    """
    Main function to orchestrate the full ingestion pipeline end to end.
    """
    # Get API keys from environment variables
    cohere_api_key = os.getenv("COHERE_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not all([cohere_api_key, qdrant_url, qdrant_api_key]):
        print("Missing required environment variables:")
        print("- COHERE_API_KEY")
        print("- QDRANT_URL")
        print("- QDRANT_API_KEY")
        print("\nPlease set these environment variables before running the pipeline.")
        return

    # Base URL to start ingestion from (you can change this)
    base_url = os.getenv("BASE_URL", "\http://localhost:4000/frontend-book/")

    # Create pipeline instance
    pipeline = URLIngestionPipeline(
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key
    )

    # Run the pipeline
    pipeline.run_pipeline(base_url, max_depth=1, max_urls=5)


if __name__ == "__main__":
    main()
