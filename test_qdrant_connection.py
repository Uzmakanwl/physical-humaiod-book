#!/usr/bin/env python3
"""
Test script to connect to Qdrant cluster and verify data storage.
"""

import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

def test_qdrant_connection():
    """
    Test connection to Qdrant cluster and verify data storage.
    """
    print("Testing Qdrant Connection...")
    print("=" * 50)

    # Get configuration from environment variables
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("COLLECTION_NAME", "test_embeddings")

    print(f"QDRANT_HOST: {qdrant_host}")
    print(f"QDRANT_PORT: {qdrant_port}")
    print(f"QDRANT_API_KEY: {'Set' if qdrant_api_key else 'NOT SET'}")
    print(f"COLLECTION_NAME: {collection_name}")
    print()

    # Check if required environment variables are set
    if not qdrant_api_key:
        print("ERROR: QDRANT_API_KEY environment variable is not set!")
        print("Please set your Qdrant API key before running this script.")
        print("\nFor Qdrant Cloud, set:")
        print("set QDRANT_HOST=your-cluster-id.qdrant.tech")
        print("set QDRANT_PORT=6333")
        print("set QDRANT_API_KEY=your-api-key")
        print("set COLLECTION_NAME=your-collection-name")
        return False

    try:
        # Initialize Qdrant client
        print("Initializing Qdrant client...")

        # Determine if we're connecting to a cloud instance or local
        if "qdrant.tech" in qdrant_host or qdrant_host.startswith("https://"):
            # Cloud instance - use HTTPS
            if qdrant_host.startswith("https://"):
                # Extract host from full URL
                import re
                match = re.search(r"https://([^:/]+)", qdrant_host)
                if match:
                    qdrant_host = match.group(1)

            client = QdrantClient(
                host=qdrant_host,
                port=443,  # Use 443 for HTTPS
                https=True,
                api_key=qdrant_api_key,
                timeout=30
            )
            print(f"Connecting to cloud instance: https://{qdrant_host}:443")
        else:
            # Local instance
            client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                api_key=qdrant_api_key,
                timeout=30
            )
            print(f"Connecting to local instance: {qdrant_host}:{qdrant_port}")

        print("[SUCCESS] Qdrant client initialized successfully")

        # Test connection by getting cluster info
        try:
            cluster_info = client.get_collections()
            print(f"[SUCCESS] Connected to Qdrant cluster")
            print(f"[INFO] Available collections: {[col.name for col in cluster_info.collections]}")
        except Exception as e:
            print(f"[ERROR] Error connecting to Qdrant: {e}")
            return False

        # Create or check collection
        print(f"\nChecking/creating collection: {collection_name}")
        try:
            # Try to get collection info
            collection_info = client.get_collection(collection_name)
            print(f"[SUCCESS] Collection '{collection_name}' exists")
            print(f"[INFO] Current point count: {collection_info.points_count}")
        except Exception:
            # Collection doesn't exist, create it
            print(f"Collection '{collection_name}' doesn't exist, creating it...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=1024,  # Default size for Cohere embeddings
                    distance=models.Distance.COSINE
                )
            )
            print(f"[SUCCESS] Created collection '{collection_name}'")

        # Test storing a sample embedding
        print(f"\nTesting data storage...")
        test_embedding = [0.1] * 1024  # Sample embedding vector
        test_payload = {
            "test": "data",
            "source": "test_script",
            "timestamp": "2025-01-01T00:00:00Z",
            "description": "Test embedding to verify connection"
        }

        # Generate a unique ID for the test point
        test_id = str(uuid.uuid4())

        # Store the test point
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=test_id,
                    vector=test_embedding,
                    payload=test_payload
                )
            ]
        )
        print(f"[SUCCESS] Successfully stored test embedding with ID: {test_id}")

        # Verify the point was stored by retrieving it
        retrieved_points = client.retrieve(
            collection_name=collection_name,
            ids=[test_id]
        )

        if retrieved_points:
            print(f"[SUCCESS] Successfully retrieved test embedding")
            print(f"[INFO] Retrieved point ID: {retrieved_points[0].id}")
            print(f"[INFO] Retrieved payload: {retrieved_points[0].payload}")
        else:
            print(f"[ERROR] Failed to retrieve the stored embedding")
            return False

        # Check collection info after storing
        collection_info = client.get_collection(collection_name)
        print(f"[INFO] Updated point count: {collection_info.points_count}")

        # Test search functionality
        print(f"\nTesting search functionality...")
        search_results = client.search(
            collection_name=collection_name,
            query_vector=test_embedding,
            limit=5
        )
        print(f"[SUCCESS] Search successful, found {len(search_results)} results")

        print("\n" + "=" * 50)
        print("[SUCCESS] QDRANT CONNECTION TEST PASSED!")
        print("[SUCCESS] Data can be stored and retrieved from Qdrant cluster")
        print(f"[SUCCESS] Your collection '{collection_name}' is ready for use")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n[ERROR] Error during Qdrant connection test: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_environment_variables():
    """
    Check if required environment variables are set.
    """
    print("Checking environment variables...")

    required_vars = [
        ("QDRANT_HOST", "Qdrant host (e.g., your-cluster.qdrant.tech)"),
        ("QDRANT_API_KEY", "Qdrant API key"),
        ("QDRANT_PORT", "Qdrant port (default: 6333)"),
        ("COLLECTION_NAME", "Collection name (default: embeddings)")
    ]

    all_set = True
    for var, description in required_vars:
        value = os.getenv(var)
        status = "[SET] " if value else "[NOT SET] "
        print(f"  {var}: {status} ({description})")
        if not value and var != "QDRANT_PORT" and var != "COLLECTION_NAME":
            all_set = False

    if not all_set:
        print("\nTo set environment variables, use:")
        print("set QDRANT_HOST=your-cluster.qdrant.tech")
        print("set QDRANT_API_KEY=your-api-key")
        print("set QDRANT_PORT=6333")
        print("set COLLECTION_NAME=embeddings")
        print()

    return all_set

if __name__ == "__main__":
    print("Qdrant Connection Test Script")
    print("=" * 50)

    # Check environment variables first
    env_ok = check_environment_variables()

    if not env_ok:
        print("Please set the required environment variables and try again.")
        sys.exit(1)

    # Run the connection test
    success = test_qdrant_connection()

    if success:
        print("\n[SUCCESS]: Your Qdrant connection is working properly!")
        print("You can now run your embedding pipeline with confidence.")
    else:
        print("\n[FAILURE]: There are issues with your Qdrant connection.")
        print("Please check the error messages above and fix the configuration.")
        sys.exit(1)