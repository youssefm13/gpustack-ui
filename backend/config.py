import os

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GPUSTACK_API_URL = os.getenv("GPUSTACK_API_URL", "http://192.168.1.231:80/v1/chat/completions")
GPUSTACK_API_KEY = os.getenv("GPUSTACK_API_KEY")
