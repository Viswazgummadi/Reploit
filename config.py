# File: config.py
import os
from dotenv import load_dotenv

# Load all environment variables from .env
load_dotenv()

# --- Load Credentials ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
# --- Application Constants ---
PINECONE_INDEX_NAME = "code-assistant"
DAILY_GUEST_LIMIT = 450 # Our safe limit below the 500 requests/day