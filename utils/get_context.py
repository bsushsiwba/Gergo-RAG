import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# MongoDB database and collection
DATABASE_NAME = "RAG-index"
COLLECTION_NAME = "Multilingual-Questions"

# MongoDB Atlas Search parameters
SEARCH_INDEX = "default"
SEARCH_PATH = "*"
SCORE_THRESHOLD = 2
SORT_ORDER = -1
LIMIT = 1

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string from environment variables
CONNECTION_STRING = os.getenv("MONGODB_CONN_STR")

# Error codes
ERROR_CODE_NO_RESULTS = "ERR_NO_RESULTS"
ERROR_CODE_CONNECTION_FAILED = "ERR_CONNECTION_FAILED"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def fetch_top_result(question):
    """
    Fetches the top result for a question using MongoDB aggregation pipeline.

    Args:
        question (str): The question to search.

    Returns:
        tuple: (result, error_code)
            - result: [id, answer] if found, else None.
            - error_code: None if successful, or error code string.
    """
    try:
        # Log MongoDB connection attempt
        logging.info("Connecting to MongoDB cluster...")
        client = MongoClient(CONNECTION_STRING)
        logging.info("Successfully connected to MongoDB cluster.")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        return None, ERROR_CODE_CONNECTION_FAILED

    try:
        # Access the database and collection
        logging.info(
            f"Accessing database: {DATABASE_NAME}, collection: {COLLECTION_NAME}."
        )
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Define the aggregation pipeline
        pipeline = [
            {
                "$search": {
                    "index": SEARCH_INDEX,
                    "text": {"query": question, "path": {"wildcard": SEARCH_PATH}},
                }
            },
            {"$addFields": {"score": {"$meta": "searchScore"}}},
            {"$match": {"score": {"$gt": SCORE_THRESHOLD}}},
            {"$sort": {"score": SORT_ORDER}},
            {"$limit": LIMIT},
        ]

        # Log the query execution
        logging.info(f"Executing aggregation pipeline for question: '{question}'")
        results = list(collection.aggregate(pipeline))

        # Handle results
        if results:
            top_result = results[0]
            logging.info(f"Top result found with score: {top_result.get('score')}")
            return [str(top_result["_id"]), top_result.get("answer", None)], None
        else:
            logging.warning("No results found with a score above the threshold.")
            return None, ERROR_CODE_NO_RESULTS

    except Exception as e:
        logging.error(f"An error occurred during query execution: {e}")
        return None, str(e)
