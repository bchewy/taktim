#!/usr/bin/env python3
"""
Test environment variable loading
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).parent.parent
print(f"Project root: {project_root}")
print(f".env file exists: {(project_root / '.env').exists()}")

load_dotenv(project_root / ".env")

# Test environment variables
print(f"\nEnvironment variables:")
print(f"CONGRESS_API_KEY: {os.getenv('CONGRESS_API_KEY', 'NOT FOUND')[:20]}...")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT FOUND')[:20]}...")
print(f"PINECONE_API_KEY: {os.getenv('PINECONE_API_KEY', 'NOT FOUND')[:20]}...")