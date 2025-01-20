# required imports
import os
from dotenv import load_dotenv

# Get environment variables
# Load environment variables from .env file
load_dotenv()

# MongoDB connection string from environment variables
CONNECTION_STRING = os.getenv("MONGODB_CONN_STR")

# Groq API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# CODE CONSTANTS

# Error codes
ERROR_CODE_CONNECTION_FAILED = "ERR_CONNECTION_FAILED"

# GROQ Model
MODEL = "llama3-8b-8192"

# Maximum number of chats to store for different users
MAX_CONTEXTS = 5
