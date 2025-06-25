import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in parent directory (project root)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    # If python-dotenv is not installed, just use system environment variables
    pass

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GPUSTACK_API_URL = os.getenv("GPUSTACK_API_URL", "http://192.168.1.231:80/v1/chat/completions")
GPUSTACK_API_KEY = os.getenv("GPUSTACK_API_KEY")
