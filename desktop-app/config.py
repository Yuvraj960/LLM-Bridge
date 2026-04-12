"""
Configuration settings for LLM Bridge Desktop Application
"""
import os
from pathlib import Path

# Application paths
APP_NAME = "LLM Bridge"
APP_VERSION = "1.0.0"

# Directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "llm-bridge.db"

# API Server settings
API_SERVER_HOST = "localhost"
API_SERVER_PORT = 11434
API_SERVER_URL = f"http://{API_SERVER_HOST}:{API_SERVER_PORT}"

# Encryption
ENCRYPTION_KEY_FILE = DATA_DIR / ".encryption_key"

# Quota warnings (percentage)
QUOTA_WARNING_THRESHOLD = 80

# ChatGPT limits (free tier)
CHATGPT_MESSAGES_PER_HOUR = 40
CHATGPT_WARNING_THRESHOLD = 32

# Claude limits (free tier)
CLAUDE_MESSAGES_PER_HOUR = 50
CLAUDE_WARNING_THRESHOLD = 40
