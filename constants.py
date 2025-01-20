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

# DB Constants
DB_NAME = "RAG-index"
CHAT_LOGS_COLLECTION = "Chat-Logs"
MULTILINGUAL_QUESTIONS_COLLECTION = "Multilingual-Questions"
UNANSWERED_QUESTIONS_COLLECTION = "Unanswered-Questions"
REVIEW_QUESTIONS_COLLECTION = "Review-Questions"

# DB Indexes
MULTILINGUAL_QUESTIONS_INDEX = "multilingual_questions_index"
UNANSWERED_QUESTIONS_INDEX = "unanswered_questions_index"
