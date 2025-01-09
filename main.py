import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
import logging
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langdetect import detect
from pymongo import MongoClient, errors
from utils.get_context import fetch_top_result
from utils.chat_log import chat_log

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string from environment variables
CONNECTION_STRING = os.getenv("MONGODB_CONN_STR")

# Error codes
ERROR_CODE_CONNECTION_FAILED = "ERR_CONNECTION_FAILED"

# Initialize FastAPI app
app = FastAPI()

# Chat contexts
chat_contexts = {}
MAX_CONTEXTS = 5

# MongoDB client
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


def detect_language(text):
    """Detect the language of the input text."""
    try:
        return detect(text)
    except Exception:
        return "en"  # Default to English if detection fails


def find_answer_in_knowledge_base(client, question):
    """Search for an exact match in the knowledge base."""
    result, error_code = fetch_top_result(client, question)
    if error_code:
        return ["", None]
    else:
        return result


class ChatRequest(BaseModel):
    question: str
    id: str = None


class ChatResponse(BaseModel):
    id: str
    response: str
    question_id: str = None


# Get Groq API key and model
groq_api_key = "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"
model = "llama3-8b-8192"
groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

system_prompt = "You are a friendly conversational chatbot who responds in the language of the user."


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


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest, db_client: MongoClient = Depends(get_mongo_client)
):
    global chat_contexts

    # Detect language
    language = detect_language(request.question)

    # Check knowledge base for predefined answer
    question_id, predefined_answer = find_answer_in_knowledge_base(
        db_client, request.question
    )
    if predefined_answer:
        response = predefined_answer
        # Ensure chat_id is set if predefined answer is found
        chat_id = request.id if request.id else str(uuid.uuid4())
    else:
        # Retrieve or create chat context
        chat_id = request.id
        if not chat_id or chat_id not in chat_contexts:
            chat_id = str(uuid.uuid4())
            memory = ConversationBufferWindowMemory(
                k=5, memory_key="chat_history", return_messages=True
            )
            chat_contexts[chat_id] = memory
        else:
            memory = chat_contexts[chat_id]

        # Construct prompt and conversation chain
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{human_input}"),
            ]
        )

        conversation = LLMChain(
            llm=groq_chat,
            prompt=prompt,
            verbose=False,
            memory=memory,
        )

        response = conversation.predict(human_input=request.question)

    # Maintain only the 5 most recent contexts
    if len(chat_contexts) > MAX_CONTEXTS:
        oldest_context_id = list(chat_contexts.keys())[0]
        del chat_contexts[oldest_context_id]

    # Log the response in the database
    chat_log(db_client, request.question, response, chat_id, question_id)

    return ChatResponse(id=chat_id, response=response, question_id=question_id)
