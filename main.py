from fastapi import FastAPI
from constants import CONNECTION_STRING
from pymongo import MongoClient, errors
import logging

from routers import chat
from routers import get_chat_logs

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


@app.get("/")
async def welcome():
    return "The site is running correctly, use chat endpoint."


# Include the chat router
app.include_router(chat.router)


# Include the get_chat_logs router
app.include_router(get_chat_logs.router)