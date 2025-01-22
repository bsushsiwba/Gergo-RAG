from fastapi import FastAPI
from constants import CONNECTION_STRING
from pymongo import MongoClient, errors
import logging
from utils.databse_schema import check_and_create_db_schema

from routers import home, chat, get_chat_logs, review_chat, delete_docs, add_context

# Initialize FastAPI app
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Establish database connection on app startup."""
    global client
    try:
        logging.info("Connecting to MongoDB cluster for logging chat")
        client = MongoClient(CONNECTION_STRING)
        logging.info("Successfully connected to MongoDB cluster.")

        # check for database Schema and create if not exists
        check_and_create_db_schema(client)
    except errors.PyMongoError as e:
        logging.error(f"Failed to connect to MongoDB during startup: {e}")
        client = None


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on app shutdown."""
    global client
    if client:
        client.close()
        logging.info("MongoDB connection closed.")
        client = None


# include home router
app.include_router(home.router)

# include add_context router
app.include_router(add_context.router)

# Include the chat router
app.include_router(chat.router)

# Include the get_chat_logs router
app.include_router(get_chat_logs.router)

# include the review_chat router
app.include_router(review_chat.router)

# include the delete_docs router
app.include_router(delete_docs.router)
