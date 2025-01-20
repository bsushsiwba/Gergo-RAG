from fastapi import HTTPException
import logging

from pymongo import MongoClient, errors

from constants import *

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string from environment variables
CONNECTION_STRING = os.getenv("MONGODB_CONN_STR")

# Initialize MongoDB client
client = None


def get_mongo_client():
    """Get the MongoDB client, reconnecting if necessary."""
    global client
    if client is None or not client.admin.command("ping"):
        try:
            logging.info("Connecting to MongoDB cluster...")
            client = MongoClient(CONNECTION_STRING)
            logging.info("Successfully connected to MongoDB cluster.")
        except errors.PyMongoError as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise HTTPException(status_code=500, detail="Database connection failed")
    return client
