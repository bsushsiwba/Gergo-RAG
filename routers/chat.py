from fastapi import APIRouter, Depends
from pymongo import MongoClient
import uuid

from utils.mongo_client import get_mongo_client
from utils.base_models import ChatRequest, ChatResponse
from utils import chat_log

from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from pymongo import MongoClient
from utils.chat_log import chat_log
from utils.get_context import find_answer_in_knowledge_base

from constants import GROQ_API_KEY, MODEL, MAX_CONTEXTS

# Router instance
router = APIRouter()

# Chat contexts
chat_contexts = {}

# define GROQ chat instance
groq_chat = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL)

system_prompt = "You are a friendly conversational chatbot who responds in the language of the user."


@router.post(
    "/chat",
    summary="Chat with the AI assistant",
    description=(
        "This endpoint allows users to chat with the AI assistant. It supports conversation context, maintains "
        "a memory buffer of recent interactions, and logs responses to the MongoDB database. If the question matches "
        "a predefined answer in the knowledge base, that response is returned immediately. Otherwise, the system generates "
        "a new response using the LLM."
    ),
    response_model=ChatResponse,
    responses={
        200: {
            "description": (
                "The chatbot's response to the user's query, along with the conversation context and a unique chat ID."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "id": "b37e6182-8b0b-4a82-9d10-d7f6ddc52fd3",
                        "response": "The significance of roles is that they align with later developed regulations...",
                        "question_id": "677ec97711172d691541fa4c",
                    }
                }
            },
        },
        422: {
            "description": "Validation error for question parameter",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "missing",
                                "loc": ["body", "question"],
                                "msg": "Field required",
                                "input": {},
                                "url": "https://errors.pydantic.dev/2.9/v/missing",
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error if the LLM or database interaction fails.",
            "content": {
                "application/json": {
                    "example": {"detail": "Database connection failed"}
                }
            },
        },
    },
    tags=["Chat"],
)
def chat_endpoint(
    request: ChatRequest, db_client: MongoClient = Depends(get_mongo_client)
):
    global chat_contexts

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
