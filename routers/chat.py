from fastapi import APIRouter, Depends, HTTPException
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
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pymongo import MongoClient
from utils.chat_log import chat_log
from utils.get_context import find_answer_in_knowledge_base
from utils.databse_schema import update_index

from constants import *

# Router instance
router = APIRouter()

# Chat contexts
chat_contexts = {}

# define chat instance based on available API KEY and MODEL
try:
    chat_instance = ChatGroq(
        groq_api_key=GROQ_API_KEY, model_name=MODEL, temperature=MODEL_TEMPERATURE
    )
except Exception as e:
    print(f"GROQ Instance Error: {e}")
try:
    chat_instance = ChatOpenAI(
        model=MODEL, temperature=MODEL_TEMPERATURE, max_retries=2
    )
except Exception as e:
    print(f"OpenAI Instance Error: {e}")
try:
    chat_instance = ChatGoogleGenerativeAI(model=MODEL, temperature=MODEL_TEMPERATURE)
except Exception as e:
    print(f"Google Generative AI Instance Error: {e}")


system_prompt = "You are a friendly conversational chatbot who responds in the language of the user."


@router.post(
    "/chat",
    summary="Chat with the AI assistant",
    description=(
        "This endpoint allows users to chat with the AI assistant. It supports conversation context, maintains "
        "a memory buffer of recent interactions, and logs responses to the MongoDB database. If the question matches "
        "a predefined answer in the knowledge base, that response is returned immediately. Otherwise, the system generates "
        "a new response using the LLM. If the `id` parameter is provided and valid, the previous conversation context "
        "associated with that `id` will be used to generate the response. If the `id` is not provided or invalid, a new "
        "`id` will be generated, and the response will be based on the new context. Unanswered questions are stored "
        "in the unanswered questions collection if not already present."
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
                        "reference_question_id": "677ec97711172d691541fa4c",
                    }
                }
            },
        },
        404: {
            "description": "Question not found in knowledge base",
            "content": {
                "application/json": {
                    "example": {"detail": "Question not found in knowledge base"}
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
    reference_question_id, predefined_answer = find_answer_in_knowledge_base(
        db_client, request.question
    )
    if predefined_answer:
        response = predefined_answer
        # Ensure chat_id is set if predefined answer is found
        chat_id = request.id if request.id else str(uuid.uuid4())
    else:
        # update index of unanswered questions
        db = db_client[DB_NAME]
        unanswered_questions = db[UNANSWERED_QUESTIONS_COLLECTION]
        update_index(unanswered_questions, UNANSWERED_QUESTIONS_INDEX)
        raise HTTPException(
            status_code=404, detail=f"Question not found in knowledge base"
        )

    # create system prompt
    system_prompt = f"""You are a friendly conversational chatbot who responds in the language of the user.
Use the following information to answer the user's question:
{response}

And keep your answer to the point unless the user asks for more details."""

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
        llm=chat_instance,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )

    response = conversation.predict(human_input=request.question)

    # Maintain only defined maximum contexts
    if len(chat_contexts) > MAX_CONTEXTS:
        oldest_context_id = list(chat_contexts.keys())[0]
        del chat_contexts[oldest_context_id]

    # Log the response in the database
    log_id = chat_log(
        db_client, request.question, response, chat_id, reference_question_id
    )

    return ChatResponse(
        id=chat_id,
        response=response.strip(),
        reference_question_id=reference_question_id,
        log_id=log_id,
    )
